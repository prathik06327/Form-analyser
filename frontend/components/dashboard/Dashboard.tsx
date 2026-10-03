"use client";

import { useCallback, useEffect, useMemo, useState } from "react";

import WorkoutHeader from "./WorkoutHeader";

import ExerciseInput from "@/components/input/ExerciseInput";
import LiveCameraMode from "@/components/input/LiveCameraMode";
import VideoUpload from "@/components/input/VideoUpload";

import RepCounter from "@/components/analysis/RepCounter";
import CurrentRepCard from "@/components/analysis/CurrentRepCard";
import FormScore from "@/components/analysis/FormScore";
import RangeOfMotionGauge from "@/components/analysis/RangeOfMotionGauge";
import TempoIndicator from "@/components/analysis/TempoIndicator";
import ElbowPositionIndicator from "@/components/analysis/ElbowPositionIndicator";
import MovementBreakdown from "@/components/analysis/MovementBreakdown";
import ConfidenceIndicator from "@/components/analysis/ConfidenceIndicator";
import PoseAccuracyMeter from "@/components/analysis/PoseAccuracyMeter";

import AICoachMessage from "@/components/ai/AICoachMessage";
import FormCorrectionCard from "@/components/ai/FormCorrectionCard";
import AIAnalysisCard from "@/components/ai/AIAnalysisCard";
import AIInsightsPanel from "@/components/ai/AIInsightsPanel";

import StatsCards from "@/components/analytics/StatsCards";
import PerformanceChart from "@/components/analytics/PerformanceChart";
import RepConsistencyChart from "@/components/analytics/RepConsistencyChart";
import FormTimeline from "@/components/analytics/FormTimeline";
import WorkoutSummary from "@/components/analytics/WorkoutSummary";
import SessionHistory from "@/components/analytics/SessionHistory";
import MuscleActivationCard from "@/components/analytics/MuscleActivationCard";

import { EXERCISES, MUSCLE_ACTIVATION } from "@/lib/mockData";
import { formTierFromScore, sessionStatusToAnalysisStatus } from "@/lib/utils";
import type {
  AnalysisStatus,
  ElbowDriftState,
  ExerciseId,
  InputMode,
  SessionStatus,
  TempoState,
  VideoAnalysisResult,
} from "@/types/analysis";

const EMPTY_BREAKDOWN = {
  shoulderStability: null,
  elbowStability: null,
  rangeOfMotion: null,
  wristAlignment: null,
  tempo: null,
};

const EMPTY_REP = {
  repNumber: 0,
  phase: "idle" as const,
  elbowAngle: null,
  rangeOfMotion: null,
  tempo: null,
};

export default function Dashboard() {
  const [selectedExercise, setSelectedExercise] = useState<ExerciseId>("bicep-curl");
  const [inputMode, setInputMode] = useState<InputMode>("live-camera");
  const [status, setStatus] = useState<SessionStatus>("ready");
  const [elapsedSeconds, setElapsedSeconds] = useState(0);
  const [uploadAnalysisStatus, setUploadAnalysisStatus] = useState<AnalysisStatus>("ready");
  // The only source of analysis data in the dashboard. Null until a real
  // backend result arrives — there is no mock fallback.
  const [result, setResult] = useState<VideoAnalysisResult | null>(null);

  const isAnalyzing = status === "analyzing";

  // Real session clock. This is genuine elapsed time, not simulated data.
  useEffect(() => {
    if (!isAnalyzing) return;
    const id = setInterval(() => setElapsedSeconds((s) => s + 1), 1000);
    return () => clearInterval(id);
  }, [isAnalyzing]);

  const analysisStatus: AnalysisStatus =
    inputMode === "live-camera" ? sessionStatusToAnalysisStatus(status) : uploadAnalysisStatus;

  const handleViewResults = useCallback(() => {
    document.getElementById("detailed-analytics")?.scrollIntoView({ behavior: "smooth", block: "start" });
  }, []);

  const handleStart = useCallback(() => setStatus("analyzing"), []);
  const handlePause = useCallback(() => setStatus("paused"), []);
  const handleReset = useCallback(() => {
    setStatus("ready");
    setElapsedSeconds(0);
    setResult(null);
  }, []);

  const reps = useMemo(() => result?.reps ?? [], [result]);
  const latestRep = reps.length > 0 ? reps[reps.length - 1] : null;
  // A finished analysis that detected no repetitions has no form data. Scoring
  // it as 0 would read as "poor form" when the truth is "nothing measured".
  const hasReps = reps.length > 0;

  const currentRep = useMemo(() => {
    if (!latestRep) return EMPTY_REP;
    return {
      repNumber: latestRep.repNumber,
      phase: latestRep.phase,
      elbowAngle: latestRep.elbowAngle,
      rangeOfMotion: latestRep.rangeOfMotion,
      tempo: latestRep.tempo,
    };
  }, [latestRep]);

  // Categorical states come from the engine's own mistake detections rather
  // than thresholds invented here. Note the engine does not distinguish
  // "excessive" drift or "too slow" tempo, so those two states are unreachable
  // until per-mistake severity is carried in the response.
  const elbowDrift: ElbowDriftState | null = latestRep
    ? latestRep.mistakes.includes("Elbow Drift")
      ? "slight-drift"
      : "stable"
    : null;

  const tempoState: TempoState | null = latestRep
    ? latestRep.mistakes.includes("Fast Lowering")
      ? "too-fast"
      : "controlled"
    : null;

  const poseAccuracy = useMemo(() => {
    const values = reps.map((rep) => rep.poseConfidence).filter((v): v is number => v !== null);
    if (values.length === 0) return null;
    return Math.round(values.reduce((sum, v) => sum + v, 0) / values.length);
  }, [reps]);

  const stats = [
    { id: "total-reps", label: "Total Reps", value: result?.totalReps ?? 0 },
    { id: "correct-reps", label: "Correct Reps", value: result?.correctReps ?? 0 },
    { id: "average-score", label: "Average Score", value: Math.round(result?.averageFormScore ?? 0) },
    { id: "best-set", label: "Best Set", value: Math.round(result?.bestScore ?? 0) },
  ];

  const summary = {
    totalReps: result?.totalReps ?? 0,
    correctReps: result?.correctReps ?? 0,
    averageFormScore: Math.round(result?.averageFormScore ?? 0),
    bestScore: Math.round(result?.bestScore ?? 0),
    mostCommonIssue: result?.mostCommonIssue ?? "—",
    // Derived with the frontend's own tier thresholds so there is a single
    // definition of what a score means.
    sessionQuality: formTierFromScore(result?.averageFormScore ?? 0),
  };

  return (
    <div className="app-shell-bg min-h-screen">
      <div className="mx-auto flex max-w-[1400px] flex-col gap-6 px-4 py-6 sm:px-6 sm:py-8 lg:px-8">
        <WorkoutHeader
          exercises={EXERCISES}
          selectedExercise={selectedExercise}
          onSelectExercise={setSelectedExercise}
          analysisStatus={analysisStatus}
          elapsedSeconds={elapsedSeconds}
        />

        <ExerciseInput mode={inputMode} onChange={setInputMode} className="mx-auto" />

        {/* Exercise input (camera or upload) + current-rep rail */}
        <section className="grid grid-cols-1 gap-6 lg:grid-cols-[1.6fr_1fr]">
          {inputMode === "live-camera" ? (
            // No frame endpoint exists, so nothing here is analyzed: no
            // keypoints, no status, no toasts. Controls drive the session
            // clock only.
            <LiveCameraMode
              sessionStatus={status}
              curlStatus="READY"
              keypoints={[]}
              toasts={[]}
              onDismissToast={() => {}}
              onStart={handleStart}
              onPause={handlePause}
              onReset={handleReset}
            />
          ) : (
            <VideoUpload
              onAnalysisStatusChange={setUploadAnalysisStatus}
              onAnalysisComplete={setResult}
              onViewResults={handleViewResults}
            />
          )}

          <div className="flex flex-col gap-4">
            <div className="glass flex items-center justify-center rounded-2xl py-5">
              <RepCounter reps={result?.totalReps ?? 0} />
            </div>
            <CurrentRepCard rep={currentRep} />
            <FormScore score={result?.averageFormScore ?? 0} hasData={hasReps} />
            <RangeOfMotionGauge
              degrees={currentRep.rangeOfMotion ?? 0}
              hasData={currentRep.rangeOfMotion !== null}
            />
            <TempoIndicator
              seconds={currentRep.tempo ?? 0}
              state={tempoState ?? "controlled"}
              hasData={currentRep.tempo !== null && tempoState !== null}
            />
            <ElbowPositionIndicator state={elbowDrift ?? "stable"} hasData={elbowDrift !== null} />
          </div>
        </section>

        {/* AI feedback */}
        <section className="flex flex-col gap-4">
          {/* Placeholder text, unchanged: real coaching copy comes from the
              feedback engine, which is deliberately not wired up. */}
          <AICoachMessage message="Start analysis to receive live coaching feedback." />
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
            {/* Coaching text comes from the feedback engine, which is not wired
                up yet — this stays empty rather than showing invented advice. */}
            <FormCorrectionCard correction={null} />
            <AIAnalysisCard
              analysis={
                result && hasReps
                  ? {
                      overallForm: Math.round(result.averageFormScore),
                      movementQuality: formTierFromScore(result.averageFormScore),
                      mainIssue: result.mostCommonIssue ?? "—",
                      confidence: poseAccuracy ?? 0,
                    }
                  : null
              }
            />
          </div>
        </section>

        {/* Detailed analytics */}
        <section id="detailed-analytics" className="flex flex-col gap-4 scroll-mt-6">
          <SectionHeading label="Detailed Analytics" />
          <StatsCards stats={stats} />

          <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
            <PerformanceChart reps={reps} />
            <RepConsistencyChart reps={reps} />
          </div>

          <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
            <FormTimeline events={result?.timeline ?? []} />
            <MovementBreakdown data={result?.movementBreakdown ?? EMPTY_BREAKDOWN} />
          </div>

          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            {/* No separate model-confidence metric exists; only pose keypoint
                confidence, which PoseAccuracyMeter reports on its own. */}
            <ConfidenceIndicator confidence={null} />
            <PoseAccuracyMeter accuracy={poseAccuracy} />
          </div>

          <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
            {/* Longer-term insights need the feedback engine (not wired up). */}
            <AIInsightsPanel insights={[]} />
            {/* Intentionally static: reference information about which muscles
                the exercise targets, not a measurement of this user. */}
            <MuscleActivationCard muscles={MUSCLE_ACTIVATION} />
          </div>
        </section>

        {/* Summary + history */}
        <section className="flex flex-col gap-4">
          <WorkoutSummary summary={summary} />
          {/* No session persistence on the backend, so there is no history. */}
          <SessionHistory sessions={[]} />
        </section>
      </div>
    </div>
  );
}

function SectionHeading({ label }: { label: string }) {
  return <h2 className="sr-only">{label}</h2>;
}
