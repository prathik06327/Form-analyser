/**
 * Centralized FastAPI client.
 *
 * The backend base URL is controlled entirely through NEXT_PUBLIC_API_URL —
 * no component should ever hardcode a backend URL directly. Every request the
 * frontend makes to FastAPI should go through a function exported from this
 * file, even before the corresponding backend route exists.
 */

import type { VideoAnalysisResult } from "@/types/analysis";

export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";

export interface HealthResponse {
  status: string;
}

async function apiFetch(path: string, init: RequestInit = {}, timeoutMs = 4000): Promise<Response> {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), timeoutMs);
  try {
    return await fetch(`${API_BASE_URL}${path}`, {
      ...init,
      signal: controller.signal,
      cache: "no-store",
    });
  } finally {
    clearTimeout(timeout);
  }
}

/**
 * GET /health — verifies the FastAPI process is alive and reachable.
 * This must stay a plain liveness check; no YOLO/pose work happens here.
 */
export async function checkBackendHealth(): Promise<HealthResponse> {
  const res = await apiFetch("/health");
  if (!res.ok) {
    throw new Error(`Backend health check failed with status ${res.status}`);
  }
  return res.json();
}

export interface VideoAnalysisRequest {
  file: File;
  exerciseId: string;
}

export interface FrameAnalysisRequest {
  frame: Blob;
  exerciseId: string;
}

export type AnalysisJobStatus = "pending" | "processing" | "done" | "error";

interface AnalysisJobResponse {
  status: AnalysisJobStatus;
  result: VideoAnalysisResult | null;
  error: string | null;
}

/** Phase reported back to the UI while a video analysis is in flight. */
export type AnalysisPhase = "uploading" | "processing";

const POLL_INTERVAL_MS = 2000;
const ANALYSIS_TIMEOUT_MS = 3 * 60 * 1000;

function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

/**
 * POST /analyze/video, then poll GET /analyze/status/{job_id} until the job
 * finishes.
 *
 * Analysis of a 30-60s clip takes roughly 40-80s, so the backend runs it as a
 * background job rather than holding the request open. `onPhase` lets the
 * caller distinguish the upload from the (much longer) processing wait.
 */
export async function analyzeVideo(
  request: VideoAnalysisRequest,
  onPhase?: (phase: AnalysisPhase) => void
): Promise<VideoAnalysisResult> {
  onPhase?.("uploading");

  const body = new FormData();
  body.append("file", request.file);

  // No apiFetch here: its 4s timeout is sized for health checks, and uploading
  // a large video can legitimately take longer than that.
  const startRes = await fetch(`${API_BASE_URL}/analyze/video`, {
    method: "POST",
    body,
    cache: "no-store",
  });

  if (!startRes.ok) {
    throw new Error(await readErrorMessage(startRes, "Failed to start video analysis"));
  }

  const { job_id: jobId } = (await startRes.json()) as { job_id?: string };
  if (!jobId) {
    throw new Error("Backend did not return a job id for the analysis request.");
  }

  onPhase?.("processing");

  const deadline = Date.now() + ANALYSIS_TIMEOUT_MS;
  while (Date.now() < deadline) {
    await sleep(POLL_INTERVAL_MS);

    const statusRes = await fetch(`${API_BASE_URL}/analyze/status/${jobId}`, { cache: "no-store" });
    if (!statusRes.ok) {
      throw new Error(await readErrorMessage(statusRes, "Failed to read analysis status"));
    }

    const job = (await statusRes.json()) as AnalysisJobResponse;

    if (job.status === "error") {
      throw new Error(job.error ?? "Video analysis failed on the backend.");
    }
    if (job.status === "done") {
      if (!job.result) {
        throw new Error("Analysis finished but returned no result.");
      }
      return job.result;
    }
  }

  throw new Error("Analysis timed out after 3 minutes. The video may be too long to process.");
}

/** Pull a useful message out of an error response body. */
async function readErrorMessage(res: Response, fallback: string): Promise<string> {
  try {
    const data = await res.json();
    const detail = (data as { detail?: unknown; error?: unknown }).detail ?? (data as { error?: unknown }).error;
    if (typeof detail === "string" && detail) return detail;
  } catch {
    // Body wasn't JSON — fall through to the generic message.
  }
  return `${fallback} (HTTP ${res.status}).`;
}

// --- Not implemented on the backend yet ---
//
// Real-time frame analysis has no backend route. This stays an explicit stub
// rather than a faked connection, so the live camera path cannot appear to be
// producing real analysis when it is not.

export interface AnalysisSession {
  sessionId: string;
}

/** POST /analyze/frame — not implemented on the backend yet. */
export async function analyzeFrame(request: FrameAnalysisRequest): Promise<AnalysisSession> {
  void request;
  throw new Error("analyzeFrame() is not implemented yet: POST /analyze/frame does not exist on the backend.");
}

/** GET /session/:id — not implemented on the backend yet. */
export async function getSession(sessionId: string): Promise<AnalysisSession> {
  void sessionId;
  throw new Error("getSession() is not implemented yet: the session endpoint does not exist on the backend.");
}
