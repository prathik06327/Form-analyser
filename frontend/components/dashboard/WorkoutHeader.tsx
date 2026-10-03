import { Activity, Clock } from "lucide-react";
import ExerciseSelector from "./ExerciseSelector";
import StatusBadge from "@/components/ui/StatusBadge";
import BackendStatus from "@/components/connection/BackendStatus";
import { ANALYSIS_STATUS_LABEL, ANALYSIS_STATUS_TONE, formatSeconds } from "@/lib/utils";
import type { AnalysisStatus, Exercise, ExerciseId } from "@/types/analysis";

interface WorkoutHeaderProps {
  exercises: Exercise[];
  selectedExercise: ExerciseId;
  onSelectExercise: (id: ExerciseId) => void;
  analysisStatus: AnalysisStatus;
  elapsedSeconds: number;
}

export default function WorkoutHeader({
  exercises,
  selectedExercise,
  onSelectExercise,
  analysisStatus,
  elapsedSeconds,
}: WorkoutHeaderProps) {
  return (
    <header className="flex flex-col gap-4">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex items-center gap-3">
          <span className="flex size-10 shrink-0 items-center justify-center rounded-xl bg-accent-soft text-accent-strong">
            <Activity className="size-5" strokeWidth={2.25} />
          </span>
          <div>
            <h1 className="text-lg font-bold tracking-tight text-text-primary sm:text-xl">FormSense AI</h1>
            <p className="text-xs text-text-muted">Bicep Curl Form Analyzer</p>
          </div>
        </div>
        <BackendStatus />
      </div>

      <div className="flex flex-wrap items-center gap-2.5 sm:gap-3">
        <div className="flex items-center gap-1.5 rounded-xl border border-hairline-strong bg-glass-strong px-3 py-2 text-sm font-medium tabular-nums text-text-secondary">
          <Clock className="size-4 text-text-muted" />
          {formatSeconds(elapsedSeconds)}
        </div>
        <div className="flex items-center gap-1.5">
          <span className="text-xs font-medium text-text-muted">Analysis</span>
          <StatusBadge tone={ANALYSIS_STATUS_TONE[analysisStatus]} pulse={analysisStatus === "analyzing"}>
            {ANALYSIS_STATUS_LABEL[analysisStatus]}
          </StatusBadge>
        </div>
        <ExerciseSelector exercises={exercises} selected={selectedExercise} onSelect={onSelectExercise} />
      </div>
    </header>
  );
}
