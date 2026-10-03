import GlassCard from "@/components/ui/GlassCard";
import SectionLabel from "@/components/ui/SectionLabel";
import { formTierFromScore, FORM_TIER_COLOR } from "@/lib/utils";
import type { SessionHistoryEntry } from "@/types/analysis";
import { CalendarClock } from "lucide-react";

interface SessionHistoryProps {
  sessions: SessionHistoryEntry[];
}

export default function SessionHistory({ sessions }: SessionHistoryProps) {
  return (
    <GlassCard>
      <SectionLabel icon={<CalendarClock className="size-3.5" />}>Session History</SectionLabel>
      {sessions.length === 0 ? (
        <p className="mt-4 text-sm text-text-muted">No previous sessions yet — complete a session to see it here.</p>
      ) : (
        <ul className="mt-4 flex flex-col divide-y divide-hairline">
          {sessions.map((session) => {
            const color = FORM_TIER_COLOR[formTierFromScore(session.score)];
            return (
              <li key={session.id} className="flex items-center justify-between py-3 first:pt-0 last:pb-0">
                <div>
                  <p className="text-sm font-medium text-text-primary">{session.label}</p>
                  <p className="text-xs text-text-muted">{session.reps} reps</p>
                </div>
                <span className="text-lg font-bold tabular-nums" style={{ color }}>
                  {session.score}
                </span>
              </li>
            );
          })}
        </ul>
      )}
    </GlassCard>
  );
}
