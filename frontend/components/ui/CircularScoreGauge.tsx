"use client";

import { cn, formTierFromScore, FORM_TIER_COLOR, FORM_TIER_LABEL } from "@/lib/utils";

interface CircularScoreGaugeProps {
  score: number;
  size?: number;
  strokeWidth?: number;
  label?: string;
  showTierLabel?: boolean;
  /** When false, renders a neutral "No Data" state instead of computing a (misleading) tier from a zero score. */
  hasData?: boolean;
  className?: string;
}

export default function CircularScoreGauge({
  score,
  size = 176,
  strokeWidth = 12,
  label = "/100",
  showTierLabel = true,
  hasData = true,
  className,
}: CircularScoreGaugeProps) {
  const clamped = Math.max(0, Math.min(100, score));
  const tier = formTierFromScore(clamped);
  const color = hasData ? FORM_TIER_COLOR[tier] : "var(--text-muted)";

  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const offset = hasData ? circumference * (1 - clamped / 100) : circumference;
  const center = size / 2;

  return (
    <div
      className={cn("relative inline-flex items-center justify-center", className)}
      style={{ width: size, height: size }}
      role="meter"
      aria-valuenow={hasData ? clamped : undefined}
      aria-valuemin={0}
      aria-valuemax={100}
      aria-label="Form score"
    >
      <svg width={size} height={size} className="-rotate-90">
        <circle
          cx={center}
          cy={center}
          r={radius}
          fill="none"
          stroke="var(--border-hairline)"
          strokeWidth={strokeWidth}
        />
        {hasData && (
          <circle
            cx={center}
            cy={center}
            r={radius}
            fill="none"
            stroke={color}
            strokeWidth={strokeWidth}
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            style={{
              transition: "stroke-dashoffset 0.6s cubic-bezier(0.4, 0, 0.2, 1), stroke 0.3s ease",
              filter: `drop-shadow(0 0 6px ${color}55)`,
            }}
          />
        )}
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <div className="flex items-baseline gap-1">
          <span className="text-4xl font-bold tracking-tight text-text-primary tabular-nums">
            {hasData ? Math.round(clamped) : "—"}
          </span>
          {hasData && <span className="text-sm font-medium text-text-muted">{label}</span>}
        </div>
        {showTierLabel && (
          <span className="mt-1 text-[11px] font-semibold uppercase tracking-wide" style={{ color }}>
            {hasData ? FORM_TIER_LABEL[tier] : "No Data"}
          </span>
        )}
      </div>
    </div>
  );
}
