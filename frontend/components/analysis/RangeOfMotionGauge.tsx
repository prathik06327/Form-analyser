import GlassCard from "@/components/ui/GlassCard";
import SectionLabel from "@/components/ui/SectionLabel";
import ProgressRing from "@/components/ui/ProgressRing";
import StatusBadge from "@/components/ui/StatusBadge";
import { Move3d } from "lucide-react";

interface RangeOfMotionGaugeProps {
  degrees: number;
  max?: number;
  hasData?: boolean;
}

function romTier(degrees: number): { label: string; tone: "good" | "warning" | "critical" } {
  if (degrees >= 120) return { label: "Good", tone: "good" };
  if (degrees >= 90) return { label: "Fair", tone: "warning" };
  return { label: "Limited", tone: "critical" };
}

export default function RangeOfMotionGauge({ degrees, max = 150, hasData = true }: RangeOfMotionGaugeProps) {
  const tier = romTier(degrees);

  return (
    <GlassCard>
      <SectionLabel icon={<Move3d className="size-3.5" />}>Range of Motion</SectionLabel>
      <div className="mt-3 flex items-center gap-4">
        <ProgressRing
          value={hasData ? degrees : 0}
          max={max}
          size={80}
          strokeWidth={7}
          color={hasData ? "var(--accent-cyan)" : "var(--text-muted)"}
        >
          <span className="text-lg font-bold text-text-primary">{hasData ? `${degrees}°` : "—"}</span>
        </ProgressRing>
        <div className="flex flex-col gap-1.5">
          <span className="text-2xl font-bold text-text-primary">{hasData ? `${degrees}°` : "—"}</span>
          {hasData ? (
            <StatusBadge tone={tier.tone}>{tier.label}</StatusBadge>
          ) : (
            <StatusBadge tone="neutral">No Data</StatusBadge>
          )}
        </div>
      </div>
    </GlassCard>
  );
}
