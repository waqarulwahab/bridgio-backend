import asyncio
import base64
import json
import io
import urllib.request
import urllib.error

from fastapi import APIRouter, HTTPException, Query, UploadFile, File
from fastapi.responses import StreamingResponse

from .state import GITHUB_TOKEN
from .utils import _auth

router = APIRouter()

REPO = "waqarulwahab/bridgio-agent"
API = "https://api.github.com"


def _gh(method: str, path: str, body=None):
    url = f"{API}{path}"
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", f"token {GITHUB_TOKEN}")
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("X-GitHub-Api-Version", "2022-11-28")
    if data:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            if r.status == 204:
                return {}
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        err_body = e.read().decode()
        raise HTTPException(e.code, f"GitHub API error: {err_body}")


@router.post("/api/build")
async def trigger_build(t: str = Query(...), pdf: UploadFile = File(...)):
    _auth(t)
    if not GITHUB_TOKEN:
        raise HTTPException(500, "GITHUB_TOKEN not configured on server")

    pdf_bytes = await pdf.read()
    if not pdf_bytes:
        raise HTTPException(400, "Empty PDF file")
    pdf_b64 = base64.b64encode(pdf_bytes).decode()

    # Get existing file SHA if any (needed for update)
    sha = None
    try:
        existing = _gh("GET", f"/repos/{REPO}/contents/decoy/decoy.pdf")
        sha = existing.get("sha")
    except HTTPException as e:
        if e.status_code != 404:
            raise

    # Commit PDF to repo
    commit_body: dict = {
        "message": "chore: update decoy PDF via dashboard",
        "content": pdf_b64,
        "branch": "main",
    }
    if sha:
        commit_body["sha"] = sha
    _gh("PUT", f"/repos/{REPO}/contents/decoy/decoy.pdf", commit_body)

    # Note current run count before triggering
    before = _gh("GET", f"/repos/{REPO}/actions/workflows/build.yml/runs?per_page=1")
    before_count = before.get("total_count", 0)

    # Trigger workflow_dispatch
    _gh("POST", f"/repos/{REPO}/actions/workflows/build.yml/dispatches", {
        "ref": "main",
        "inputs": {"trigger": "dashboard"},
    })

    # Poll up to 20s for new run to appear
    run_id = None
    for _ in range(10):
        await asyncio.sleep(2)
        runs = _gh("GET", f"/repos/{REPO}/actions/workflows/build.yml/runs?per_page=1")
        if runs.get("total_count", 0) > before_count:
            items = runs.get("workflow_runs", [])
            if items:
                run_id = items[0]["id"]
                break

    return {"run_id": run_id, "repo": REPO}


@router.get("/api/build/status")
async def build_status(run_id: int, t: str = Query(...)):
    _auth(t)
    if not GITHUB_TOKEN:
        raise HTTPException(500, "GITHUB_TOKEN not configured on server")
    run = _gh("GET", f"/repos/{REPO}/actions/runs/{run_id}")
    return {
        "status": run.get("status"),
        "conclusion": run.get("conclusion"),
        "html_url": run.get("html_url"),
    }


@router.get("/api/build/download")
async def build_download(run_id: int, t: str = Query(...)):
    _auth(t)
    if not GITHUB_TOKEN:
        raise HTTPException(500, "GITHUB_TOKEN not configured on server")

    artifacts = _gh("GET", f"/repos/{REPO}/actions/runs/{run_id}/artifacts")
    items = artifacts.get("artifacts", [])
    if not items:
        raise HTTPException(404, "No artifacts yet — build may still be running")

    artifact_id = items[0]["id"]
    url = f"{API}/repos/{REPO}/actions/artifacts/{artifact_id}/zip"

    req = urllib.request.Request(url)
    req.add_header("Authorization", f"token {GITHUB_TOKEN}")
    req.add_header("Accept", "application/vnd.github+json")

    # urllib follows redirects by default
    with urllib.request.urlopen(req, timeout=120) as r:
        data = r.read()

    return StreamingResponse(
        io.BytesIO(data),
        media_type="application/zip",
        headers={"Content-Disposition": "attachment; filename=BridgioAgent.zip"},
    )
