import type {
  AnalysisStatus,
  BackendConnectionStatus,
  CurlStatus,
  ElbowDriftState,
  FormTier,
  RepPhase,
  SessionStatus,
  Severity,
  TempoState,
} from "@/types/analysis";
import type { BadgeTone } from "@/components/ui/StatusBadge";

export function cn(...classes: Array<string | false | null | undefined>): string {
  return classes.filter(Boolean).join(" ");
}

export function formTierFromScore(score: number): FormTier {
  if (score >= 90) return "excellent";
  if (score >= 75) return "good";
  if (score >= 60) return "needs-improvement";
  return "poor";
}

export const FORM_TIER_LABEL: Record<FormTier, string> = {
  excellent: "Excellent",
  good: "Good Form",
  "needs-improvement": "Needs Improvement",
  poor: "Poor Form",
};

/** Maps a form tier to a CSS color token — status colors stay reserved and consistent app-wide. */
export const FORM_TIER_COLOR: Record<FormTier, string> = {
  excellent: "var(--status-good-fg)",
  good: "var(--series-1)",
  "needs-improvement": "var(--status-warning)",
  poor: "var(--status-critical-fg)",
};

export const TEMPO_STATE_LABEL: Record<TempoState, string> = {
  "too-fast": "Too Fast",
  controlled: "Controlled",
  "too-slow": "Too Slow",
};

export const ELBOW_DRIFT_LABEL: Record<ElbowDriftState, string> = {
  stable: "Stable",
  "slight-drift": "Slight Drift",
  "excessive-drift": "Excessive Drift",
};

export const SEVERITY_LABEL: Record<Severity, string> = {
  low: "Low",
  medium: "Medium",
  high: "High",
};

export const SEVERITY_COLOR: Record<Severity, string> = {
  low: "var(--status-good-fg)",
  medium: "var(--status-warning)",
  high: "var(--status-critical-fg)",
};

export const TEMPO_STATE_TONE: Record<TempoState, "good" | "warning" | "critical" | "neutral" | "accent"> = {
  "too-fast": "warning",
  controlled: "good",
  "too-slow": "warning",
};

export const ELBOW_DRIFT_TONE: Record<ElbowDriftState, "good" | "warning" | "critical" | "neutral" | "accent"> = {
  stable: "good",
  "slight-drift": "warning",
  "excessive-drift": "critical",
};

export const CURL_STATUS_TONE: Record<CurlStatus, "good" | "warning" | "critical" | "neutral" | "accent"> = {
  READY: "neutral",
  CURLING: "accent",
  "TOP POSITION": "good",
  LOWERING: "accent",
  "FORM ISSUE": "critical",
};

export const PHASE_LABEL: Record<RepPhase, string> = {
  idle: "Idle",
  concentric: "Concentric",
  top: "Top Position",
  eccentric: "Eccentric",
  bottom: "Bottom Position",
};

export const SESSION_STATUS_LABEL: Record<SessionStatus, string> = {
  ready: "Ready",
  analyzing: "Analyzing",
  paused: "Paused",
  ended: "Session Ended",
};

export const SESSION_STATUS_TONE: Record<SessionStatus, "good" | "warning" | "critical" | "neutral" | "accent"> = {
  ready: "neutral",
  analyzing: "good",
  paused: "warning",
  ended: "neutral",
};

export function formatSeconds(totalSeconds: number): string {
  const minutes = Math.floor(totalSeconds / 60);
  const seconds = Math.floor(totalSeconds % 60);
  return `${String(minutes).padStart(2, "0")}:${String(seconds).padStart(2, "0")}`;
}

/** The unified "Analysis" indicator — separate from backend connectivity. */
export const ANALYSIS_STATUS_LABEL: Record<AnalysisStatus, string> = {
  ready: "Ready",
  analyzing: "Analyzing",
  paused: "Paused",
  completed: "Completed",
  error: "Error",
};

export const ANALYSIS_STATUS_TONE: Record<AnalysisStatus, BadgeTone> = {
  ready: "neutral",
  analyzing: "good",
  paused: "warning",
  completed: "accent",
  error: "critical",
};

/** Maps the existing Live Camera SessionStatus onto the unified AnalysisStatus shown in the header. */
export function sessionStatusToAnalysisStatus(status: SessionStatus): AnalysisStatus {
  if (status === "ended") return "completed";
  return status;
}

export const BACKEND_STATUS_LABEL: Record<BackendConnectionStatus, string> = {
  connecting: "Connecting...",
  connected: "Connected",
  disconnected: "Disconnected",
};

export const BACKEND_STATUS_TONE: Record<BackendConnectionStatus, BadgeTone> = {
  connecting: "neutral",
  connected: "good",
  disconnected: "critical",
};

export function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  const kb = bytes / 1024;
  if (kb < 1024) return `${kb.toFixed(1)} KB`;
  const mb = kb / 1024;
  if (mb < 1024) return `${mb.toFixed(1)} MB`;
  return `${(mb / 1024).toFixed(1)} GB`;
}
