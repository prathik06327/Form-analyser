import GlassCard from "@/components/ui/GlassCard";
import SectionLabel from "@/components/ui/SectionLabel";
import StatusBadge from "@/components/ui/StatusBadge";
import { cn, ELBOW_DRIFT_LABEL, ELBOW_DRIFT_TONE } from "@/lib/utils";
import type { ElbowDriftState } from "@/types/analysis";
import { GitCommitHorizontal } from "lucide-react";

interface ElbowPositionIndicatorProps {
  state: ElbowDriftState;
  hasData?: boolean;
}

const STEPS: ElbowDriftState[] = ["stable", "slight-drift", "excessive-drift"];

const STEP_COLOR: Record<ElbowDriftState, string> = {
  stable: "bg-status-good-fg",
  "slight-drift": "bg-status-warning",
  "excessive-drift": "bg-status-critical-fg",
};

export default function ElbowPositionIndicator({ state, hasData = true }: ElbowPositionIndicatorProps) {
  const activeIndex = STEPS.indexOf(state);

  return (
    <GlassCard>
      <SectionLabel icon={<GitCommitHorizontal className="size-3.5" />}>Elbow Position</SectionLabel>
      <div className="mt-3 flex items-center justify-between">
        {hasData ? (
          <StatusBadge tone={ELBOW_DRIFT_TONE[state]}>{ELBOW_DRIFT_LABEL[state]}</StatusBadge>
        ) : (
          <StatusBadge tone="neutral">No Data</StatusBadge>
        )}
      </div>
      <div className="mt-3 flex gap-1.5">
        {STEPS.map((step, i) => (
          <span
            key={step}
            className={cn(
              "h-1.5 flex-1 rounded-full transition-colors",
              hasData && i <= activeIndex ? STEP_COLOR[state] : "bg-hairline-strong"
            )}
          />
        ))}
      </div>
    </GlassCard>
  );
}
