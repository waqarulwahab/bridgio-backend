"""
PC Sync Relay Server
Deploy on Railway (free)

Environment variables:
  PCSYNC_USER    - login username  (default: samar)
  PCSYNC_PASS    - login password  (default: pcsync2024)
  PCSYNC_SECRET  - device secret   (default: device_secret_key)
  PORT           - server port     (set automatically by Render)
"""
import logging
import os

import uvicorn
from fastapi import FastAPI, Query
from fastapi.responses import FileResponse

from routes.utils import _load_state, _fetch_rc_exe, _auth
from routes import devices, files, system, downloads, websockets, dashboard, rc_dashboard, build
from routes.db import db_path

logging.basicConfig(level=logging.INFO)

app = FastAPI(docs_url=None, redoc_url=None)

# Load persisted state on startup
_load_state()
_fetch_rc_exe()

# Register all routers
app.include_router(devices.router)
app.include_router(files.router)
app.include_router(system.router)
app.include_router(downloads.router)
app.include_router(websockets.router)
app.include_router(dashboard.router)
app.include_router(rc_dashboard.router)
app.include_router(build.router)


@app.get("/api/backup")
async def backup_db(t: str = Query(...)):
    _auth(t)
    path = db_path()
    if not os.path.exists(path):
        from fastapi import HTTPException
        raise HTTPException(404, "Database not found")
    return FileResponse(path, filename="bridgio_backup.db", media_type="application/octet-stream")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
