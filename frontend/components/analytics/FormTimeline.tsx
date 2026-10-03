import GlassCard from "@/components/ui/GlassCard";
import SectionLabel from "@/components/ui/SectionLabel";
import { formatSeconds } from "@/lib/utils";
import type { TimelineEvent } from "@/types/analysis";
import { CheckCircle2, AlertTriangle, History } from "lucide-react";

interface FormTimelineProps {
  events: TimelineEvent[];
}

export default function FormTimeline({ events }: FormTimelineProps) {
  return (
    <GlassCard>
      <SectionLabel icon={<History className="size-3.5" />}>Form Timeline</SectionLabel>
      {events.length === 0 && (
        <p className="mt-4 text-sm text-text-muted">No events recorded yet — start analysis to begin.</p>
      )}
      <ol className="mt-4 flex flex-col gap-3 scrollbar-thin max-h-64 overflow-y-auto pr-1">
        {events.map((event, i) => (
          <li key={`${event.timestampSec}-${i}`} className="flex items-center gap-3 text-sm">
            <span className="w-11 shrink-0 font-mono text-xs tabular-nums text-text-muted">
              {formatSeconds(event.timestampSec)}
            </span>
            {event.kind === "good" ? (
              <CheckCircle2 className="size-4 shrink-0 text-status-good-fg" />
            ) : (
              <AlertTriangle className="size-4 shrink-0 text-status-warning" />
            )}
            <span className="text-text-primary">{event.label}</span>
          </li>
        ))}
      </ol>
    </GlassCard>
  );
}
