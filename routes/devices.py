from fastapi import APIRouter, HTTPException, Query, Request

from .state import devices, known_devices, known_rc_devices
from .utils import _auth, _make_token, _h, _save_devices
from . import db as _db

router = APIRouter()


@router.post("/api/login")
async def api_login(body: dict):
    from .state import USER, PASS
    from .utils import _h, _make_token
    if body.get("u") == USER and _h(body.get("p", "")) == _h(PASS):
        return {"token": _make_token()}
    raise HTTPException(401, "Wrong username or password")


@router.get("/api/devices")
async def api_devices(t: str = Query(...)):
    _auth(t)
    return [
        {
            "id": k,
            "name": v.get("custom_name") or v["name"],
            "raw_name": v["name"],
            "online": v["online"],
            "last_seen": v["last_seen"],
            "connected_at": v.get("connected_at", v["last_seen"]),
        }
        for k, v in known_devices.items()
    ]


@router.post("/api/rename-device")
async def rename_device(request: Request, t: str = Query(...)):
    _auth(t)
    body = await request.json()
    did = body.get("device_id")
    new_name = (body.get("name") or "").strip()
    if not did or not new_name:
        raise HTTPException(400, "device_id and name required")
    if did not in known_devices:
        raise HTTPException(404, "Device not found")
    known_devices[did]["custom_name"] = new_name
    _db.rename_device_db(did, new_name)
    return {"ok": True}


@router.delete("/api/delete-device")
async def delete_device(t: str = Query(...), device_id: str = Query(...)):
    _auth(t)
    if device_id not in known_devices:
        raise HTTPException(404, "Device not found")
    known_devices.pop(device_id, None)
    devices.pop(device_id, None)
    _db.delete_device_db(device_id)
    return {"ok": True}


@router.get("/debug")
async def debug():
    from .state import SECRET
    return {"devices": list(devices.keys()), "secret_ok": SECRET == "device_secret_key"}


@router.get("/api/rc-devices")
async def api_rc_devices(t: str = Query(...)):
    _auth(t)
    return [
        {
            "id": k,
            "name": v.get("custom_name") or v["name"],
            "online": v["online"],
            "last_seen": v["last_seen"],
            "connected_at": v.get("connected_at", v["last_seen"]),
        }
        for k, v in known_rc_devices.items()
    ]
