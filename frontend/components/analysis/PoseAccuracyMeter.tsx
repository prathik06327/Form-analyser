import GlassCard from "@/components/ui/GlassCard";
import SectionLabel from "@/components/ui/SectionLabel";
import ProgressRing from "@/components/ui/ProgressRing";
import { ScanFace } from "lucide-react";

interface PoseAccuracyMeterProps {
  accuracy: number | null;
}

export default function PoseAccuracyMeter({ accuracy }: PoseAccuracyMeterProps) {
  const hasData = accuracy !== null;
  return (
    <GlassCard className="flex items-center gap-4">
      <ProgressRing
        value={accuracy ?? 0}
        size={64}
        strokeWidth={6}
        color={hasData ? "var(--series-1)" : "var(--text-muted)"}
      >
        <span className="text-sm font-bold text-text-primary">{hasData ? `${accuracy}%` : "—"}</span>
      </ProgressRing>
      <div>
        <SectionLabel icon={<ScanFace className="size-3.5" />}>Pose Accuracy</SectionLabel>
        <p className="mt-1 text-xs text-text-muted">Keypoint detection quality, not form score</p>
      </div>
    </GlassCard>
  );
}
