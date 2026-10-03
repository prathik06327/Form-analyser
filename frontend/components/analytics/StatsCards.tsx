import GlassCard from "@/components/ui/GlassCard";
import { CheckCircle2, Gauge, Repeat, Trophy } from "lucide-react";
import type { LucideIcon } from "lucide-react";

interface StatCardDatum {
  id: string;
  label: string;
  value: number;
}

interface StatsCardsProps {
  stats: StatCardDatum[];
}

const ICON_BY_ID: Record<string, LucideIcon> = {
  "total-reps": Repeat,
  "correct-reps": CheckCircle2,
  "average-score": Gauge,
  "best-set": Trophy,
};

export default function StatsCards({ stats }: StatsCardsProps) {
  return (
    <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
      {stats.map((stat) => {
        const Icon = ICON_BY_ID[stat.id] ?? Gauge;
        return (
          <GlassCard key={stat.id} padding="sm" className="flex items-center gap-3">
            <span className="flex size-9 shrink-0 items-center justify-center rounded-lg bg-accent-soft text-accent-strong">
              <Icon className="size-4.5" strokeWidth={2} />
            </span>
            <div className="min-w-0">
              <p className="text-xl font-bold tabular-nums text-text-primary">{stat.value}</p>
              <p className="truncate text-[11px] font-medium text-text-muted">{stat.label}</p>
            </div>
          </GlassCard>
        );
      })}
    </div>
  );
}
