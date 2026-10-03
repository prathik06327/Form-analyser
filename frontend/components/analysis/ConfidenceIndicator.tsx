import GlassCard from "@/components/ui/GlassCard";
import SectionLabel from "@/components/ui/SectionLabel";
import ProgressRing from "@/components/ui/ProgressRing";
import { Sparkles } from "lucide-react";

interface ConfidenceIndicatorProps {
  confidence: number | null;
}

export default function ConfidenceIndicator({ confidence }: ConfidenceIndicatorProps) {
  const hasData = confidence !== null;
  return (
    <GlassCard className="flex items-center gap-4">
      <ProgressRing
        value={confidence ?? 0}
        size={64}
        strokeWidth={6}
        color={hasData ? "var(--accent)" : "var(--text-muted)"}
      >
        <span className="text-sm font-bold text-text-primary">{hasData ? `${confidence}%` : "—"}</span>
      </ProgressRing>
      <div>
        <SectionLabel icon={<Sparkles className="size-3.5" />}>AI Confidence</SectionLabel>
        <p className="mt-1 text-xs text-text-muted">Certainty of the current analysis</p>
      </div>
    </GlassCard>
  );
}
