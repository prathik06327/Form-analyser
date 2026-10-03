"use client";

import { useEffect, useState } from "react";
import { CheckCircle2, AlertTriangle } from "lucide-react";
import { cn } from "@/lib/utils";

export interface FeedbackToastData {
  id: string;
  message: string;
  kind: "good" | "warning";
}

interface RealTimeFeedbackToastProps {
  toasts: FeedbackToastData[];
  onDismiss: (id: string) => void;
  durationMs?: number;
}

export default function RealTimeFeedbackToast({
  toasts,
  onDismiss,
  durationMs = 3200,
}: RealTimeFeedbackToastProps) {
  return (
    <div className="pointer-events-none absolute inset-x-0 bottom-4 flex flex-col items-center gap-2 sm:bottom-6">
      {toasts.map((toast) => (
        <ToastItem key={toast.id} toast={toast} durationMs={durationMs} onDismiss={onDismiss} />
      ))}
    </div>
  );
}

function ToastItem({
  toast,
  durationMs,
  onDismiss,
}: {
  toast: FeedbackToastData;
  durationMs: number;
  onDismiss: (id: string) => void;
}) {
  const [leaving, setLeaving] = useState(false);

  useEffect(() => {
    const leaveTimer = setTimeout(() => setLeaving(true), durationMs);
    return () => clearTimeout(leaveTimer);
  }, [durationMs]);

  useEffect(() => {
    if (!leaving) return;
    const removeTimer = setTimeout(() => onDismiss(toast.id), 180);
    return () => clearTimeout(removeTimer);
  }, [leaving, onDismiss, toast.id]);

  const isGood = toast.kind === "good";

  return (
    <div
      className={cn(
        "pointer-events-auto flex items-center gap-2 rounded-full border bg-black/60 px-4 py-2 text-sm font-medium shadow-lg backdrop-blur-md",
        isGood ? "border-[rgba(12,163,12,0.4)] text-status-good-fg" : "border-[rgba(250,178,25,0.4)] text-status-warning",
        leaving ? "animate-toast-out" : "animate-toast-in"
      )}
    >
      {isGood ? <CheckCircle2 className="size-4" /> : <AlertTriangle className="size-4" />}
      <span className="text-text-primary">{toast.message}</span>
    </div>
  );
}
