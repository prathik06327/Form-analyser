import { AlertTriangle } from "lucide-react";
import { SEVERITY_COLOR, SEVERITY_LABEL, cn } from "@/lib/utils";
import type { Severity } from "@/types/analysis";

interface FormErrorAlertProps {
  title: string;
  message: string;
  severity: Severity;
  className?: string;
}

const SEVERITY_BG: Record<Severity, string> = {
  low: "bg-[rgba(12,163,12,0.08)] border-[rgba(12,163,12,0.3)]",
  medium: "bg-[rgba(250,178,25,0.08)] border-[rgba(250,178,25,0.3)]",
  high: "bg-[rgba(208,59,59,0.1)] border-[rgba(208,59,59,0.35)]",
};

export default function FormErrorAlert({ title, message, severity, className }: FormErrorAlertProps) {
  const color = SEVERITY_COLOR[severity];

  return (
    <div
      role="alert"
      className={cn("flex items-start gap-3 rounded-xl border p-4", SEVERITY_BG[severity], className)}
    >
      <AlertTriangle className="mt-0.5 size-4 shrink-0" style={{ color }} strokeWidth={2} />
      <div className="min-w-0">
        <div className="flex items-center gap-2">
          <p className="text-xs font-semibold uppercase tracking-wide" style={{ color }}>
            Form Issue Detected
          </p>
          <span className="text-[10px] font-semibold uppercase tracking-wide text-text-muted">
            {SEVERITY_LABEL[severity]}
          </span>
        </div>
        <p className="mt-1 text-sm font-medium text-text-primary">{title}</p>
        <p className="mt-0.5 text-sm text-text-secondary">{message}</p>
      </div>
    </div>
  );
}
