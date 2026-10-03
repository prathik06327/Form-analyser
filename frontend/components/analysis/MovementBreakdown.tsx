import GlassCard from "@/components/ui/GlassCard";
import SectionLabel from "@/components/ui/SectionLabel";
import type { MovementBreakdown as MovementBreakdownData } from "@/types/analysis";
import { ListChecks } from "lucide-react";

interface MovementBreakdownProps {
  data: MovementBreakdownData;
}

const ROWS: Array<{ key: keyof MovementBreakdownData; label: string }> = [
  { key: "shoulderStability", label: "Shoulder Stability" },
  { key: "elbowStability", label: "Elbow Stability" },
  { key: "rangeOfMotion", label: "Range of Motion" },
  { key: "wristAlignment", label: "Wrist Alignment" },
  { key: "tempo", label: "Tempo" },
];

export default function MovementBreakdown({ data }: MovementBreakdownProps) {
  return (
    <GlassCard>
      <SectionLabel icon={<ListChecks className="size-3.5" />}>Movement Breakdown</SectionLabel>
      <div className="mt-4 flex flex-col gap-3.5">
        {ROWS.map(({ key, label }) => {
          const value = data[key];
          // A null metric has no backend equivalent — show an empty track
          // rather than an implied 0%.
          return (
            <div key={key}>
              <div className="mb-1.5 flex items-center justify-between text-sm">
                <span className="text-text-secondary">{label}</span>
                <span className="font-semibold tabular-nums text-text-primary">
                  {value === null ? "—" : `${Math.round(value)}%`}
                </span>
              </div>
              <div className="h-1.5 w-full overflow-hidden rounded-full bg-hairline-strong">
                {value !== null && (
                  <div
                    className="h-full rounded-full bg-series-1 transition-[width] duration-500 ease-out"
                    style={{ width: `${Math.max(0, Math.min(100, value))}%` }}
                  />
                )}
              </div>
            </div>
          );
        })}
      </div>
    </GlassCard>
  );
}
