import { Play, Pause, RotateCcw } from "lucide-react";
import NeonButton from "@/components/ui/NeonButton";
import type { SessionStatus } from "@/types/analysis";

interface WorkoutControlsProps {
  status: SessionStatus;
  onStart: () => void;
  onPause: () => void;
  onReset: () => void;
}

export default function WorkoutControls({ status, onStart, onPause, onReset }: WorkoutControlsProps) {
  const isAnalyzing = status === "analyzing";
  const isPaused = status === "paused";

  return (
    <div className="flex flex-wrap items-center gap-2.5">
      <NeonButton
        variant="primary"
        icon={<Play className="size-4" />}
        loading={isAnalyzing}
        disabled={isAnalyzing}
        onClick={onStart}
      >
        {isAnalyzing ? "Analyzing..." : isPaused ? "Resume Analysis" : "Start Analysis"}
      </NeonButton>

      <NeonButton
        variant="secondary"
        icon={<Pause className="size-4" />}
        disabled={!isAnalyzing}
        onClick={onPause}
      >
        Pause Analysis
      </NeonButton>

      <NeonButton variant="danger" icon={<RotateCcw className="size-4" />} onClick={onReset}>
        Reset Session
      </NeonButton>
    </div>
  );
}
