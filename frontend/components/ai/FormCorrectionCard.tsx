import GlassCard from "@/components/ui/GlassCard";
import SectionLabel from "@/components/ui/SectionLabel";
import StatusBadge from "@/components/ui/StatusBadge";
import { SEVERITY_LABEL } from "@/lib/utils";
import type { FormCorrection } from "@/types/analysis";
import { Wrench } from "lucide-react";

const SEVERITY_TONE = {
  low: "good",
  medium: "warning",
  high: "critical",
} as const;

interface FormCorrectionCardProps {
  correction: FormCorrection | null;
}

export default function FormCorrectionCard({ correction }: FormCorrectionCardProps) {
  return (
    <GlassCard>
      <div className="flex items-center justify-between">
        <SectionLabel icon={<Wrench className="size-3.5" />}>Form Correction</SectionLabel>
        {correction && (
          <StatusBadge tone={SEVERITY_TONE[correction.severity]}>{SEVERITY_LABEL[correction.severity]}</StatusBadge>
        )}
      </div>

      {correction ? (
        <>
          <p className="mt-3 text-base font-semibold text-text-primary">{correction.title}</p>
          <p className="mt-1 text-sm text-text-secondary">{correction.issue}</p>

          <div className="mt-3 rounded-xl border border-hairline bg-glass px-3.5 py-3">
            <p className="text-[11px] font-semibold uppercase tracking-wide text-text-muted">Correction</p>
            <p className="mt-1 text-sm text-text-primary">{correction.correction}</p>
          </div>
        </>
      ) : (
        <p className="mt-3 text-sm text-text-muted">No corrections yet — complete a rep to get feedback.</p>
      )}
    </GlassCard>
  );
}
