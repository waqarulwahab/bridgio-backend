import base64

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse

from .utils import _auth, _relay

router = APIRouter()


@router.get("/api/browse")
async def api_browse(t: str = Query(...), d: str = Query(...), path: str = Query("")):
    _auth(t)
    return await _relay(d, {"type": "browse", "path": path})


@router.get("/api/drives")
async def api_drives(t: str = Query(...), d: str = Query(...)):
    _auth(t)
    return await _relay(d, {"type": "drives"})


@router.get("/api/stats")
async def api_stats(t: str = Query(...), d: str = Query(...)):
    _auth(t)
    return await _relay(d, {"type": "stats"})


@router.get("/api/quick-access")
async def api_qa(t: str = Query(...), d: str = Query(...)):
    _auth(t)
    return await _relay(d, {"type": "quick_access"})


@router.get("/api/thumbnail")
async def api_thumb(t: str = Query(...), d: str = Query(...), path: str = Query(...), size: int = Query(160)):
    _auth(t)
    r = await _relay(d, {"type": "thumbnail", "path": path, "size": size}, 15.0)
    if "error" in r:
        raise HTTPException(400, r["error"])
    data = base64.b64decode(r["data"])
    return StreamingResponse(iter([data]), media_type="image/jpeg",
                             headers={"Cache-Control": "max-age=300"})


@router.get("/api/text-preview")
async def api_text(t: str = Query(...), d: str = Query(...), path: str = Query(...)):
    _auth(t)
    return await _relay(d, {"type": "text_preview", "path": path})


@router.post("/api/open-on-pc")
async def api_open(t: str = Query(...), d: str = Query(...), path: str = Query(...)):
    _auth(t)
    return await _relay(d, {"type": "open_on_pc", "path": path})


@router.get("/api/download")
async def api_download(t: str = Query(...), d: str = Query(...), path: str = Query(...)):
    _auth(t)
    name = path.replace("\\", "/").split("/")[-1]

    async def stream():
        offset, chunk_size = 0, 256 * 1024
        while True:
            try:
                r = await _relay(d, {"type": "chunk", "path": path,
                                     "offset": offset, "size": chunk_size}, 30.0)
            except Exception:
                break
            if "error" in r:
                break
            chunk = base64.b64decode(r.get("data", ""))
            if chunk:
                yield chunk
            if r.get("done"):
                break
            offset += len(chunk)

    return StreamingResponse(
        stream(),
        media_type="application/octet-stream",
        headers={"Content-Disposition": f'attachment; filename="{name}"'},
    )
