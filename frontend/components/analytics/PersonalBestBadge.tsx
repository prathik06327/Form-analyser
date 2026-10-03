import { Trophy } from "lucide-react";
import { cn } from "@/lib/utils";

interface PersonalBestBadgeProps {
  score: number;
  className?: string;
}

export default function PersonalBestBadge({ score, className }: PersonalBestBadgeProps) {
  return (
    <div
      className={cn(
        "flex items-center gap-3 rounded-xl border border-[rgba(250,178,25,0.35)] bg-[rgba(250,178,25,0.08)] px-4 py-3",
        className
      )}
    >
      <span className="flex size-9 shrink-0 items-center justify-center rounded-full bg-[rgba(250,178,25,0.15)] text-status-warning">
        <Trophy className="size-4.5" strokeWidth={2} />
      </span>
      <div>
        <p className="text-[11px] font-semibold uppercase tracking-wide text-status-warning">Personal Best</p>
        <p className="text-lg font-bold text-text-primary">
          {score} <span className="text-xs font-medium text-text-muted">Best Form Score</span>
        </p>
      </div>
    </div>
  );
}
