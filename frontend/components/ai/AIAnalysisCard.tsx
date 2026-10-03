import GlassCard from "@/components/ui/GlassCard";
import SectionLabel from "@/components/ui/SectionLabel";
import { FORM_TIER_LABEL } from "@/lib/utils";
import type { AIAnalysisSnapshot } from "@/types/analysis";
import { BrainCircuit } from "lucide-react";

interface AIAnalysisCardProps {
  analysis: AIAnalysisSnapshot | null;
}

export default function AIAnalysisCard({ analysis }: AIAnalysisCardProps) {
  return (
    <GlassCard>
      <SectionLabel icon={<BrainCircuit className="size-3.5" />}>AI Analysis</SectionLabel>
      {analysis ? (
        <dl className="mt-4 grid grid-cols-2 gap-4">
          <Row label="Overall Form" value={`${analysis.overallForm}%`} />
          <Row label="Movement Quality" value={FORM_TIER_LABEL[analysis.movementQuality]} />
          <Row label="Main Issue" value={analysis.mainIssue} />
          <Row label="Confidence" value={`${analysis.confidence}%`} />
        </dl>
      ) : (
        <p className="mt-4 text-sm text-text-muted">No analysis yet — start analysis to begin.</p>
      )}
    </GlassCard>
  );
}

function Row({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <dt className="text-[11px] font-medium uppercase tracking-wide text-text-muted">{label}</dt>
      <dd className="mt-0.5 text-lg font-semibold text-text-primary">{value}</dd>
    </div>
  );
}
