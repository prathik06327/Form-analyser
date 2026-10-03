"use client";

import { useEffect, useState } from "react";
import StatusBadge from "@/components/ui/StatusBadge";
import { checkBackendHealth } from "@/lib/api";
import { BACKEND_STATUS_LABEL, BACKEND_STATUS_TONE, cn } from "@/lib/utils";
import type { BackendConnectionStatus } from "@/types/analysis";

const POLL_INTERVAL_MS = 5000;

interface BackendStatusProps {
  className?: string;
}

export default function BackendStatus({ className }: BackendStatusProps) {
  const [status, setStatus] = useState<BackendConnectionStatus>("connecting");

  useEffect(() => {
    let cancelled = false;
    let timeoutId: ReturnType<typeof setTimeout>;

    async function poll() {
      try {
        const health = await checkBackendHealth();
        if (!cancelled) setStatus(health.status === "ok" ? "connected" : "disconnected");
      } catch {
        if (!cancelled) setStatus("disconnected");
      } finally {
        // Self-scheduling instead of setInterval so a slow/hanging request
        // never overlaps with the next poll — only one check is ever in flight.
        if (!cancelled) timeoutId = setTimeout(poll, POLL_INTERVAL_MS);
      }
    }

    poll();

    return () => {
      cancelled = true;
      clearTimeout(timeoutId);
    };
  }, []);

  return (
    <div className={cn("flex items-center gap-1.5", className)}>
      <span className="text-xs font-medium text-text-muted">Backend</span>
      <StatusBadge tone={BACKEND_STATUS_TONE[status]} pulse={status === "connecting"}>
        {BACKEND_STATUS_LABEL[status]}
      </StatusBadge>
    </div>
  );
}
