import GlassCard from "@/components/ui/GlassCard";
import SectionLabel from "@/components/ui/SectionLabel";
import StatusBadge from "@/components/ui/StatusBadge";
import { TEMPO_STATE_LABEL, TEMPO_STATE_TONE } from "@/lib/utils";
import type { TempoState } from "@/types/analysis";
import { Timer } from "lucide-react";

interface TempoIndicatorProps {
  seconds: number;
  state: TempoState;
  hasData?: boolean;
}

export default function TempoIndicator({ seconds, state, hasData = true }: TempoIndicatorProps) {
  return (
    <GlassCard>
      <SectionLabel icon={<Timer className="size-3.5" />}>Tempo</SectionLabel>
      <div className="mt-3 flex items-end justify-between">
        <div>
          <span className="text-2xl font-bold text-text-primary">{hasData ? `${seconds}s` : "—"}</span>
          <span className="ml-1 text-xs text-text-muted">/ rep</span>
        </div>
        {hasData ? (
          <StatusBadge tone={TEMPO_STATE_TONE[state]}>{TEMPO_STATE_LABEL[state]}</StatusBadge>
        ) : (
          <StatusBadge tone="neutral">No Data</StatusBadge>
        )}
      </div>
    </GlassCard>
  );
}
