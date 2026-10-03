import GlassCard from "@/components/ui/GlassCard";
import SectionLabel from "@/components/ui/SectionLabel";
import { PHASE_LABEL } from "@/lib/utils";
import type { CurrentRepState } from "@/types/analysis";
import { Activity } from "lucide-react";

interface CurrentRepCardProps {
  rep: CurrentRepState;
}

export default function CurrentRepCard({ rep }: CurrentRepCardProps) {
  return (
    <GlassCard>
      <div className="flex items-center justify-between">
        <SectionLabel icon={<Activity className="size-3.5" />}>Current Rep</SectionLabel>
        <span className="text-sm font-semibold text-text-primary">Rep #{rep.repNumber}</span>
      </div>

      <div className="mt-4 grid grid-cols-2 gap-3">
        <Metric label="Phase" value={PHASE_LABEL[rep.phase]} />
        <Metric label="Elbow Angle" value={format(rep.elbowAngle, "°")} />
        <Metric label="ROM" value={format(rep.rangeOfMotion, "°")} />
        <Metric label="Tempo" value={format(rep.tempo, "s")} />
      </div>
    </GlassCard>
  );
}

/** Render a measurement, or an em dash when the backend reported none. */
function format(value: number | null, suffix: string): string {
  return value === null ? "—" : `${value}${suffix}`;
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-xl border border-hairline bg-glass px-3 py-2.5">
      <p className="text-[11px] font-medium uppercase tracking-wide text-text-muted">{label}</p>
      <p className="mt-0.5 text-lg font-semibold text-text-primary">{value}</p>
    </div>
  );
}
