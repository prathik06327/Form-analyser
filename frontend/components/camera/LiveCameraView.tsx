import { Camera, Pause, Radio } from "lucide-react";
import PoseDetectionOverlay from "./PoseDetectionOverlay";
import CurlStatusBadge from "./CurlStatusBadge";
import type { CurlStatus, PoseKeypoint, SessionStatus } from "@/types/analysis";
import { cn } from "@/lib/utils";

interface LiveCameraViewProps {
  sessionStatus: SessionStatus;
  curlStatus: CurlStatus;
  keypoints: PoseKeypoint[];
}

export default function LiveCameraView({ sessionStatus, curlStatus, keypoints }: LiveCameraViewProps) {
  const isAnalyzing = sessionStatus === "analyzing";
  const isPaused = sessionStatus === "paused";

  return (
    <div className="relative aspect-video w-full overflow-hidden rounded-2xl border border-hairline bg-[radial-gradient(120%_120%_at_50%_0%,#1a1c22_0%,#0a0b0f_70%)]">
      {/* Corner AR brackets — reads as a real CV capture frame */}
      <div className="pointer-events-none absolute inset-4 sm:inset-6" aria-hidden>
        {[
          "top-0 left-0 border-t-2 border-l-2",
          "top-0 right-0 border-t-2 border-r-2",
          "bottom-0 left-0 border-b-2 border-l-2",
          "bottom-0 right-0 border-b-2 border-r-2",
        ].map((pos) => (
          <span
            key={pos}
            className={cn("absolute size-5 rounded-[2px] border-accent-cyan/40", pos)}
          />
        ))}
      </div>

      {sessionStatus === "ready" && (
        <div className="absolute inset-0 flex flex-col items-center justify-center gap-3 text-text-muted">
          <div className="flex size-14 items-center justify-center rounded-full border border-hairline-strong bg-glass-strong">
            <Camera className="size-6" strokeWidth={1.5} />
          </div>
          <p className="text-sm font-medium text-text-secondary">Camera Ready</p>
          <p className="text-xs text-text-muted">Start analysis to begin pose tracking</p>
        </div>
      )}

      {(isAnalyzing || isPaused) && (
        <>
          <PoseDetectionOverlay keypoints={keypoints} active={isAnalyzing} />
          {isPaused && (
            <div className="absolute inset-0 flex flex-col items-center justify-center gap-2 bg-black/50 backdrop-blur-[2px]">
              <div className="flex size-12 items-center justify-center rounded-full border border-hairline-strong bg-glass-strong">
                <Pause className="size-5" strokeWidth={1.5} />
              </div>
              <p className="text-sm font-medium text-text-secondary">Analysis Paused</p>
            </div>
          )}
        </>
      )}

      {/* Top overlay row */}
      <div className="absolute inset-x-4 top-4 flex items-center justify-between sm:inset-x-6 sm:top-6">
        {isAnalyzing ? (
          <span className="inline-flex items-center gap-1.5 rounded-full bg-black/45 px-2.5 py-1 text-[11px] font-semibold uppercase tracking-wide text-status-critical-fg">
            <Radio className="size-3 animate-pulse-dot" strokeWidth={2.5} />
            Live
          </span>
        ) : (
          <span />
        )}
        {(isAnalyzing || isPaused) && <CurlStatusBadge status={curlStatus} className="bg-black/45" />}
      </div>
    </div>
  );
}
