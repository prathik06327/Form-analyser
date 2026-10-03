import logging
import threading
import uuid
from pathlib import Path
from typing import Any

import cv2
import numpy as np
from fastapi import BackgroundTasks, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.analysis.live_session import create_session, get_session
from app.analysis.video_adapter import run_video_analysis

logger = logging.getLogger("api")
logging.basicConfig(level=logging.INFO)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Uploaded videos are staged here and deleted once analysis finishes.
UPLOAD_DIR = Path(__file__).resolve().parents[1] / "tmp_uploads"

ALLOWED_SUFFIXES = {".mp4", ".mov", ".avi", ".webm"}
UPLOAD_CHUNK_BYTES = 1024 * 1024

# KNOWN LIMITATION: job state lives in this process's memory only. Restarting
# the server loses every in-flight and completed job, and it does not work
# across multiple worker processes. Fine for local development; a real
# deployment needs a shared store (Redis/DB) instead.
_jobs: dict[str, dict[str, Any]] = {}
_jobs_lock = threading.Lock()


def _set_job(job_id: str, **fields: Any) -> None:
    """Atomically update a job record."""

    with _jobs_lock:
        job = _jobs.setdefault(job_id, {})
        job.update(fields)


def _get_job(job_id: str) -> dict[str, Any] | None:
    """Return a copy of a job record, if it exists."""

    with _jobs_lock:
        job = _jobs.get(job_id)
        return dict(job) if job is not None else None


def _process_video_job(job_id: str, video_path: Path) -> None:
    """Run analysis for one job, then always clean up the staged upload."""

    _set_job(job_id, status="processing")
    try:
        result = run_video_analysis(str(video_path))
        _set_job(job_id, status="done", result=result.model_dump(), error=None)
    except Exception as exc:  # surfaced to the client as an error job
        _set_job(job_id, status="error", result=None, error=str(exc))
    finally:
        video_path.unlink(missing_ok=True)


@app.get("/")
def home():
    return {
        "message": "Form Analyser Backend Running!"
    }


@app.get("/health")
def health():
    """Liveness check the frontend polls — no YOLO/pose work happens here."""
    return {
        "status": "ok"
    }


@app.post("/analyze/video", status_code=202)
async def analyze_video(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    """Accept a workout video and start analysis in the background.

    Returns immediately with a job id; poll `/analyze/status/{job_id}` for the
    result. Analysis of a 30-60s clip takes roughly 40-80s, which is far too
    long to hold an HTTP request open.
    """

    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in ALLOWED_SUFFIXES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{suffix or 'unknown'}'. Expected one of: MP4, MOV, AVI, WEBM.",
        )

    job_id = str(uuid.uuid4())
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    # Name the staged file after the job id — never the client-supplied
    # filename, which must not influence the path we write to.
    video_path = UPLOAD_DIR / f"{job_id}{suffix}"

    try:
        with video_path.open("wb") as buffer:
            while chunk := await file.read(UPLOAD_CHUNK_BYTES):
                buffer.write(chunk)
    except Exception as exc:
        video_path.unlink(missing_ok=True)
        raise HTTPException(status_code=500, detail=f"Failed to store upload: {exc}") from exc
    finally:
        await file.close()

    _set_job(job_id, status="pending", result=None, error=None)
    background_tasks.add_task(_process_video_job, job_id, video_path)

    return {"job_id": job_id, "status": "pending"}


@app.post("/analyze/frame")
async def analyze_frame(file: UploadFile = File(...), session_id: str | None = Form(default=None)):
    """Analyze one live-camera frame, continuing an existing session if given.

    Reuses the exact same pipeline as `/analyze/video`
    (pose -> biomechanics -> repetition -> assessment -> scoring) via
    `process_pipeline_frame`; only the state persistence differs — one video
    loop vs. one session dict entry per HTTP request.
    """

    if session_id is None:
        session = create_session()
    else:
        session = get_session(session_id)
        if session is None:
            raise HTTPException(status_code=404, detail=f"Unknown session id: {session_id}")

    raw = await file.read()
    buffer = np.frombuffer(raw, dtype=np.uint8)
    frame = cv2.imdecode(buffer, cv2.IMREAD_COLOR)
    if frame is None:
        raise HTTPException(status_code=400, detail="Could not decode image frame.")

    logger.info("session=%s frame received bytes=%s", session.session_id, len(raw))

    try:
        result = session.process_frame(frame)
    except Exception as exc:  # a bad frame must not kill the session
        logger.exception("session=%s frame processing failed", session.session_id)
        return {
            "sessionId": session.session_id,
            "analysisAvailable": False,
            "totalReps": session.total_reps,
            "currentRep": None,
            "movementState": "IDLE",
            "mistakes": [],
            "error": str(exc),
        }

    return result.model_dump()


@app.get("/analyze/status/{job_id}")
def analyze_status(job_id: str):
    """Report the status, and when finished the result, of an analysis job."""

    job = _get_job(job_id)
    if job is None:
        return JSONResponse(
            status_code=404,
            content={"status": "error", "result": None, "error": "Unknown job id."},
        )

    return {
        "status": job.get("status", "pending"),
        "result": job.get("result"),
        "error": job.get("error"),
    }
