import asyncio
import hashlib
import logging
import os
import time
import uuid

from fastapi import HTTPException

from .state import (
    USER, PASS, SECRET,
    devices, pending, known_devices, known_rc_devices,
    _RC_EXE_PATH, _RC_EXE_CACHE, _RC_GITHUB_RAW, GITHUB_TOKEN,
)
from . import db as _db

logger = logging.getLogger("pcsync")


def _h(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()


def _load_state():
    _db.init_db()
    _db.init_builds_table()
    known_devices.update(_db.load_devices())
    known_rc_devices.update(_db.load_rc_devices())
    logger.info("loaded %d devices, %d rc_devices from SQLite", len(known_devices), len(known_rc_devices))


def _save_devices():
    for did, data in known_devices.items():
        try:
            _db.upsert_device(did, data)
        except Exception as e:
            logger.warning("save_devices failed %s: %s", did, e)


def _save_rc_state():
    for did, data in known_rc_devices.items():
        try:
            _db.upsert_rc_device(did, data)
        except Exception as e:
            logger.warning("save_rc_state failed %s: %s", did, e)


def _make_token() -> str:
    return _h(USER + ":" + PASS + ":" + SECRET + ":pcsync-v2")


def _auth(t: str):
    if t != _make_token():
        raise HTTPException(401, "Invalid token — please login again")


async def _relay(did: str, msg: dict, timeout: float = 20.0) -> dict:
    if did not in devices:
        raise HTTPException(503, "PC is offline — make sure EXE is running")
    rid = str(uuid.uuid4())
    msg["req_id"] = rid
    loop = asyncio.get_event_loop()
    fut: asyncio.Future = loop.create_future()
    pending[rid] = fut
    try:
        await devices[did]["ws"].send_text(json.dumps(msg))
        return await asyncio.wait_for(asyncio.shield(fut), timeout)
    except asyncio.TimeoutError:
        pending.pop(rid, None)
        raise HTTPException(504, "PC did not respond in time")
    except Exception as exc:
        pending.pop(rid, None)
        raise HTTPException(503, str(exc))


def _fetch_rc_exe():
    for path in (_RC_EXE_PATH, _RC_EXE_CACHE):
        if os.path.exists(path):
            return path
    if not GITHUB_TOKEN:
        return None
    try:
        import urllib.request
        logger.info("Downloading SystemDriver.exe from private repo...")
        req = urllib.request.Request(_RC_GITHUB_RAW, headers={"Authorization": f"token {GITHUB_TOKEN}"})
        with urllib.request.urlopen(req, timeout=60) as r, open(_RC_EXE_CACHE, "wb") as f:
            f.write(r.read())
        logger.info("Downloaded SystemDriver.exe (%d bytes)", os.path.getsize(_RC_EXE_CACHE))
        return _RC_EXE_CACHE
    except Exception as e:
        logger.warning("RC EXE download failed: %s", e)
        return None
