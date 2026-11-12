from fastapi import APIRouter, Query

from .utils import _auth, _relay

router = APIRouter()


@router.post("/api/run-command")
async def api_run_cmd(body: dict, t: str = Query(...), d: str = Query(...)):
    _auth(t)
    return await _relay(d, {"type": "run_command", "cmd": body.get("cmd", "")}, 35.0)


@router.get("/api/list-processes")
async def api_procs(t: str = Query(...), d: str = Query(...)):
    _auth(t)
    return await _relay(d, {"type": "list_processes"}, 15.0)


@router.post("/api/kill-process")
async def api_kill(body: dict, t: str = Query(...), d: str = Query(...)):
    _auth(t)
    return await _relay(d, {"type": "kill_process", "pid": body.get("pid", 0)})


@router.post("/api/delete-path")
async def api_del(t: str = Query(...), d: str = Query(...), path: str = Query(...)):
    _auth(t)
    return await _relay(d, {"type": "delete_path", "path": path})


@router.post("/api/rename-path")
async def api_rename(body: dict, t: str = Query(...), d: str = Query(...)):
    _auth(t)
    return await _relay(d, {"type": "rename_path", "path": body.get("path", ""), "new_name": body.get("new_name", "")})


@router.post("/api/create-folder")
async def api_mkdir(t: str = Query(...), d: str = Query(...), path: str = Query(...)):
    _auth(t)
    return await _relay(d, {"type": "create_folder", "path": path})
