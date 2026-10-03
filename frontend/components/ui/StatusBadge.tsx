import type { ReactNode } from "react";
import { cn } from "@/lib/utils";

export type BadgeTone = "good" | "warning" | "critical" | "neutral" | "accent";

interface StatusBadgeProps {
  children: ReactNode;
  tone?: BadgeTone;
  pulse?: boolean;
  icon?: ReactNode;
  className?: string;
}

const TONE_CLASSES: Record<BadgeTone, string> = {
  good: "bg-[rgba(12,163,12,0.14)] text-status-good-fg border-[rgba(12,163,12,0.35)]",
  warning: "bg-[rgba(250,178,25,0.14)] text-status-warning border-[rgba(250,178,25,0.35)]",
  critical: "bg-[rgba(208,59,59,0.14)] text-status-critical-fg border-[rgba(208,59,59,0.35)]",
  neutral: "bg-glass-strong text-text-secondary border-hairline-strong",
  accent: "bg-accent-soft text-accent-strong border-[rgba(124,92,255,0.4)]",
};

const DOT_CLASSES: Record<BadgeTone, string> = {
  good: "bg-status-good-fg",
  warning: "bg-status-warning",
  critical: "bg-status-critical-fg",
  neutral: "bg-text-muted",
  accent: "bg-accent-strong",
};

export default function StatusBadge({
  children,
  tone = "neutral",
  pulse = false,
  icon,
  className,
}: StatusBadgeProps) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-[11px] font-semibold uppercase tracking-wide",
        TONE_CLASSES[tone],
        className
      )}
    >
      {icon ?? (
        <span className={cn("size-1.5 rounded-full", DOT_CLASSES[tone], pulse && "animate-pulse-dot")} />
      )}
      {children}
    </span>
  );
}
