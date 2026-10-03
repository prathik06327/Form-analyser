import GlassCard from "@/components/ui/GlassCard";
import SectionLabel from "@/components/ui/SectionLabel";
import StatusBadge from "@/components/ui/StatusBadge";
import { FORM_TIER_LABEL } from "@/lib/utils";
import type { SessionSummary } from "@/types/analysis";
import { ClipboardList } from "lucide-react";

interface WorkoutSummaryProps {
  summary: SessionSummary;
}

const QUALITY_TONE = {
  excellent: "good",
  good: "accent",
  "needs-improvement": "warning",
  poor: "critical",
} as const;

export default function WorkoutSummary({ summary }: WorkoutSummaryProps) {
  const hasData = summary.totalReps > 0;

  return (
    <GlassCard>
      <div className="flex items-center justify-between">
        <SectionLabel icon={<ClipboardList className="size-3.5" />}>Workout Summary</SectionLabel>
        {hasData ? (
          <StatusBadge tone={QUALITY_TONE[summary.sessionQuality]}>
            {FORM_TIER_LABEL[summary.sessionQuality]}
          </StatusBadge>
        ) : (
          <StatusBadge tone="neutral">No Data</StatusBadge>
        )}
      </div>

      <div className="mt-4 grid grid-cols-2 gap-4 sm:grid-cols-4">
        <Stat label="Total Reps" value={summary.totalReps} />
        <Stat label="Correct Reps" value={summary.correctReps} />
        <Stat label="Average Score" value={summary.averageFormScore} />
        <Stat label="Best Rep" value={summary.bestScore} />
      </div>

      <div className="mt-4 rounded-xl border border-hairline bg-glass px-3.5 py-3">
        <p className="text-[11px] font-semibold uppercase tracking-wide text-text-muted">Most Common Issue</p>
        <p className="mt-1 text-sm font-medium text-text-primary">{summary.mostCommonIssue}</p>
      </div>
    </GlassCard>
  );
}

function Stat({ label, value }: { label: string; value: number }) {
  return (
    <div>
      <p className="text-2xl font-bold tabular-nums text-text-primary">{value}</p>
      <p className="text-[11px] font-medium uppercase tracking-wide text-text-muted">{label}</p>
    </div>
  );
}
