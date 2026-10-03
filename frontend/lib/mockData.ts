import type { Exercise, MuscleActivation } from "@/types/analysis";

/**
 * Static application configuration.
 *
 * NOTE: this file previously held fabricated analysis results (rep counts, form
 * scores, ROM/tempo readings, session history). Those were removed when
 * `POST /analyze/video` was wired up — all analysis data now comes from the
 * backend via `lib/api.ts`, and anything the backend cannot measure renders as
 * an empty state instead.
 *
 * Only genuinely static, non-user-specific configuration belongs here. Do not
 * add placeholder scores or session data.
 */

/** Exercises offered in the selector. Only bicep curl is analyzable today. */
export const EXERCISES: Exercise[] = [
  { id: "bicep-curl", label: "Bicep Curl", enabled: true },
  { id: "squat", label: "Squat", enabled: false },
  { id: "push-up", label: "Push-up", enabled: false },
  { id: "lunge", label: "Lunge", enabled: false },
];

/**
 * Reference information about which muscles the exercise targets. Intentionally
 * static: this describes the movement itself, not a measurement of the user.
 */
export const MUSCLE_ACTIVATION: MuscleActivation[] = [
  { name: "Biceps", role: "Primary" },
  { name: "Forearms", role: "Secondary" },
  { name: "Shoulders", role: "Stabilizer" },
];
