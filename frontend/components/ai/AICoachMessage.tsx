import { Sparkles } from "lucide-react";
import { cn } from "@/lib/utils";

interface AICoachMessageProps {
  message: string;
  className?: string;
}

export default function AICoachMessage({ message, className }: AICoachMessageProps) {
  return (
    <div
      className={cn(
        "relative overflow-hidden rounded-2xl border border-[rgba(124,92,255,0.3)] bg-accent-soft p-5 sm:p-6",
        className
      )}
    >
      <div
        className="pointer-events-none absolute -right-10 -top-10 size-40 rounded-full opacity-40 blur-3xl"
        style={{ background: "var(--accent)" }}
        aria-hidden
      />
      <div className="relative flex items-start gap-3">
        <span className="mt-0.5 flex size-8 shrink-0 items-center justify-center rounded-full bg-accent/20 text-accent-strong">
          <Sparkles className="size-4" strokeWidth={2} />
        </span>
        <div>
          <p className="text-xs font-semibold uppercase tracking-wider text-accent-strong">AI Coach</p>
          <p className="mt-1.5 text-sm leading-relaxed text-text-primary sm:text-[15px]">{message}</p>
        </div>
      </div>
    </div>
  );
}
