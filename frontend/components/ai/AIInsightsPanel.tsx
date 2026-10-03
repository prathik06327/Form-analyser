import GlassCard from "@/components/ui/GlassCard";
import SectionLabel from "@/components/ui/SectionLabel";
import type { AIInsight } from "@/types/analysis";
import { Lightbulb } from "lucide-react";

interface AIInsightsPanelProps {
  insights: AIInsight[];
}

export default function AIInsightsPanel({ insights }: AIInsightsPanelProps) {
  return (
    <GlassCard>
      <SectionLabel icon={<Lightbulb className="size-3.5" />}>AI Insights</SectionLabel>
      {insights.length === 0 ? (
        <p className="mt-4 text-sm text-text-muted">Insights will appear after your first session.</p>
      ) : (
        <ul className="mt-4 flex flex-col gap-3">
          {insights.map((insight) => (
            <li key={insight.id} className="flex items-start gap-2.5 text-sm text-text-secondary">
              <span className="mt-2 size-1.5 shrink-0 rounded-full bg-accent-cyan" />
              <span className="leading-relaxed text-text-primary/90">{insight.message}</span>
            </li>
          ))}
        </ul>
      )}
    </GlassCard>
  );
}
