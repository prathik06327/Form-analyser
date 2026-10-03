import GlassCard from "@/components/ui/GlassCard";
import SectionLabel from "@/components/ui/SectionLabel";
import type { MuscleActivation } from "@/types/analysis";
import { Dumbbell } from "lucide-react";
import { cn } from "@/lib/utils";

interface MuscleActivationCardProps {
  muscles: MuscleActivation[];
}

const ROLE_STYLES: Record<MuscleActivation["role"], string> = {
  Primary: "border-[rgba(124,92,255,0.4)] bg-accent-soft text-accent-strong",
  Secondary: "border-hairline-strong bg-glass-strong text-text-secondary",
  Stabilizer: "border-hairline bg-glass text-text-muted",
};

export default function MuscleActivationCard({ muscles }: MuscleActivationCardProps) {
  return (
    <GlassCard>
      <SectionLabel icon={<Dumbbell className="size-3.5" />}>Target Muscles</SectionLabel>
      <p className="mt-1 text-xs text-text-muted">Muscles emphasized by this exercise — not a live activation reading.</p>
      <div className="mt-4 flex flex-col gap-2.5">
        {muscles.map((muscle) => (
          <div key={muscle.name} className="flex items-center justify-between rounded-xl border border-hairline bg-glass px-3.5 py-2.5">
            <span className="text-sm font-medium text-text-primary">{muscle.name}</span>
            <span className={cn("rounded-full border px-2.5 py-0.5 text-[11px] font-semibold", ROLE_STYLES[muscle.role])}>
              {muscle.role}
            </span>
          </div>
        ))}
      </div>
    </GlassCard>
  );
}
