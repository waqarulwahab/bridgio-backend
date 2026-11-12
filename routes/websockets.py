import asyncio
import json
import logging
import time
import uuid

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from .state import (
    devices, pending, known_devices, SECRET,
    rc_devices, rc_latest_frame, known_rc_devices,
)
from .utils import _save_devices, _save_rc_state

logger = logging.getLogger("pcsync")
router = APIRouter()


@router.websocket("/ws/device")
async def ws_device(ws: WebSocket):
    await ws.accept()
    did = None
    try:
        logger.info("ws: waiting for init")
        raw = await asyncio.wait_for(ws.receive_text(), 15.0)
        logger.info("ws: got init: %s", raw[:120])
        init = json.loads(raw)
        if init.get("secret") != SECRET:
            logger.warning("ws: wrong secret '%s'", init.get("secret", ""))
            await ws.close(1008, "Unauthorized")
            return
        did = init["device_id"]
        devices[did] = {"ws": ws, "name": init.get("name", did)}
        existing = known_devices.get(did, {})
        known_devices[did] = {
            "name": init.get("name", did),
            "custom_name": existing.get("custom_name", ""),
            "online": True,
            "last_seen": time.time(),
            "connected_at": time.time(),
        }
        _save_devices()
        logger.info("ws: registered %s (total=%d)", did, len(devices))

        while True:
            raw = await ws.receive_text()
            msg = json.loads(raw)
            rid = msg.get("req_id")
            if rid in pending:
                fut = pending.pop(rid)
                if not fut.done():
                    fut.set_result(msg)
    except WebSocketDisconnect:
        logger.info("ws: client disconnected did=%s", did)
    except Exception as e:
        logger.error("ws: error did=%s: %s", did, e)
    finally:
        if did:
            devices.pop(did, None)
            if did in known_devices:
                known_devices[did]["online"] = False
                known_devices[did]["last_seen"] = time.time()
            _save_devices()
            logger.info("ws: deregistered %s", did)


@router.websocket("/ws/rc-device")
async def ws_rc_device(ws: WebSocket):
    await ws.accept()
    did = ws.query_params.get("device_id", str(uuid.uuid4()))
    rc_devices[did] = {"ws": ws, "viewers": set()}
    existing_rc = known_rc_devices.get(did, {})
    known_rc_devices[did] = {
        "name": did,
        "custom_name": existing_rc.get("custom_name", ""),
        "online": True,
        "last_seen": time.time(),
        "connected_at": time.time(),
    }
    _save_rc_state()
    logger.info("rc-device connected: %s", did)
    try:
        async for raw in ws.iter_text():
            try:
                msg = json.loads(raw)
                if msg.get("type") == "frame":
                    frame = msg.get("data", "")
                    rc_latest_frame[did] = frame
                    dead = set()
                    for viewer_ws in rc_devices[did]["viewers"]:
                        try:
                            await viewer_ws.send_text(json.dumps({"type": "frame", "data": frame}))
                        except Exception:
                            dead.add(viewer_ws)
                    rc_devices[did]["viewers"] -= dead
            except Exception as e:
                logger.error("rc-device msg error: %s", e)
    except WebSocketDisconnect:
        pass
    finally:
        rc_devices.pop(did, None)
        rc_latest_frame.pop(did, None)
        if did in known_rc_devices:
            known_rc_devices[did]["online"] = False
            known_rc_devices[did]["last_seen"] = time.time()
        _save_rc_state()
        logger.info("rc-device disconnected: %s", did)


@router.websocket("/ws/rc-viewer")
async def ws_rc_viewer(ws: WebSocket):
    await ws.accept()
    did = ws.query_params.get("device_id", "")
    if not did or did not in rc_devices:
        await ws.close(1008, "Device not found")
        return
    rc_devices[did]["viewers"].add(ws)
    viewer_count = len(rc_devices[did]["viewers"])
    try:
        await rc_devices[did]["ws"].send_text(json.dumps({"type": "viewer_count", "count": viewer_count}))
    except Exception:
        pass
    if did in rc_latest_frame:
        await ws.send_text(json.dumps({"type": "frame", "data": rc_latest_frame[did]}))
    logger.info("rc-viewer connected for device: %s (viewers=%d)", did, viewer_count)
    try:
        async for raw in ws.iter_text():
            try:
                msg = json.loads(raw)
                if msg.get("type") == "input" and did in rc_devices:
                    await rc_devices[did]["ws"].send_text(raw)
            except Exception as e:
                logger.error("rc-viewer msg error: %s", e)
    except WebSocketDisconnect:
        pass
    finally:
        if did in rc_devices:
            rc_devices[did]["viewers"].discard(ws)
            viewer_count = len(rc_devices[did]["viewers"])
            try:
                await rc_devices[did]["ws"].send_text(json.dumps({"type": "viewer_count", "count": viewer_count}))
            except Exception:
                pass
            logger.info("rc-viewer disconnected from device: %s (viewers=%d)", did, viewer_count)
