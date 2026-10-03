/**
 * Shared analysis types.
 *
 * These mirror the shape the FastAPI + YOLO backend is expected to return.
 * The UI is built entirely against these types with mock data (lib/mockData.ts)
 * standing in for real backend responses — swapping the data source later
 * should not require touching any component.
 */

export type ExerciseId = "bicep-curl" | "squat" | "push-up" | "lunge";

export interface Exercise {
  id: ExerciseId;
  label: string;
  enabled: boolean;
}

export type SessionStatus = "ready" | "analyzing" | "paused" | "ended";

export type RepPhase = "idle" | "concentric" | "top" | "eccentric" | "bottom";

export type CurlStatus =
  | "READY"
  | "CURLING"
  | "TOP POSITION"
  | "LOWERING"
  | "FORM ISSUE";

export type FormTier = "excellent" | "good" | "needs-improvement" | "poor";

export type TempoState = "too-fast" | "controlled" | "too-slow";

export type ElbowDriftState = "stable" | "slight-drift" | "excessive-drift";

export type Severity = "low" | "medium" | "high";

/** A single joint/keypoint as detected by the pose model, normalized 0-1 within the frame. */
export interface PoseKeypoint {
  name: "shoulder" | "elbow" | "wrist" | "hip";
  x: number;
  y: number;
  confidence: number;
}

/**
 * Metrics are nullable because the backend reports null rather than a
 * fabricated number whenever a measurement is genuinely unavailable for a rep.
 */
export interface RepAnalysis {
  repNumber: number;
  formScore: number;
  elbowAngle: number | null;
  rangeOfMotion: number | null;
  tempo: number | null;
  elbowStability: number | null;
  poseConfidence: number | null;
  phase: RepPhase;
  mistakes: string[];
  timestampSec: number;
}

/**
 * Session-average movement scores (0-100).
 *
 * `shoulderStability` and `wristAlignment` are always null today: the
 * biomechanics engine computes no equivalent metric, so the UI shows an empty
 * row for them instead of inventing a value.
 */
export interface MovementBreakdown {
  shoulderStability: number | null;
  elbowStability: number | null;
  rangeOfMotion: number | null;
  wristAlignment: number | null;
  tempo: number | null;
}

export interface FormCorrection {
  title: string;
  issue: string;
  correction: string;
  severity: Severity;
}

export interface AIAnalysisSnapshot {
  overallForm: number;
  movementQuality: FormTier;
  mainIssue: string;
  confidence: number;
}

export interface TimelineEvent {
  timestampSec: number;
  label: string;
  kind: "good" | "warning";
}

export interface AIInsight {
  id: string;
  message: string;
}

export interface MuscleActivation {
  name: string;
  role: "Primary" | "Secondary" | "Stabilizer";
}

export interface SessionSummary {
  totalReps: number;
  correctReps: number;
  averageFormScore: number;
  bestScore: number;
  mostCommonIssue: string;
  sessionQuality: FormTier;
}

export interface SessionHistoryEntry {
  id: string;
  label: string;
  reps: number;
  score: number;
}

export interface SessionAnalysis {
  totalReps: number;
  correctReps: number;
  averageFormScore: number;
  bestScore: number;
  reps: RepAnalysis[];
}

/**
 * Exactly what `POST /analyze/video` produces: a `SessionAnalysis` plus the
 * additional data the pipeline genuinely computes, so the dashboard does not
 * have to fall back to mock values.
 */
export interface VideoAnalysisResult extends SessionAnalysis {
  movementBreakdown: MovementBreakdown;
  timeline: TimelineEvent[];
  mostCommonIssue: string | null;
}

export interface CurrentRepState {
  repNumber: number;
  phase: RepPhase;
  elbowAngle: number | null;
  rangeOfMotion: number | null;
  tempo: number | null;
}

export interface LiveMetrics {
  formScore: number;
  poseAccuracy: number;
  confidence: number;
  tempoState: TempoState;
  elbowDrift: ElbowDriftState;
  curlStatus: CurlStatus;
}

/** Which exercise input source is currently feeding the analysis pipeline. */
export type InputMode = "live-camera" | "upload-video";

/**
 * Unified analysis status shown in the dashboard header, independent of the
 * FastAPI connection itself. Live Camera mode derives this from SessionStatus;
 * Upload Video mode derives it from VideoUpload's own local upload/analyze stage.
 */
export type AnalysisStatus = "ready" | "analyzing" | "paused" | "completed" | "error";

/** Connectivity state of the FastAPI backend, polled via GET /health. */
export type BackendConnectionStatus = "connecting" | "connected" | "disconnected";

/**
 * Local state machine for the video upload flow. FILE_SELECTED and
 * READY_TO_ANALYZE from the product spec collapse into a single "selected"
 * stage here — there is no async validation step between them yet, so the UI
 * for both is identical.
 */
export type VideoUploadStage = "empty" | "selected" | "analyzing" | "completed" | "failed";
