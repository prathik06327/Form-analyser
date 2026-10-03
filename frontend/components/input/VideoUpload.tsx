"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { AlertTriangle, CheckCircle2, FileVideo, Loader2, UploadCloud, X } from "lucide-react";
import GlassCard from "@/components/ui/GlassCard";
import NeonButton from "@/components/ui/NeonButton";
import StatusBadge from "@/components/ui/StatusBadge";
import { analyzeVideo, type AnalysisPhase } from "@/lib/api";
import { cn, formatFileSize } from "@/lib/utils";
import type { AnalysisStatus, VideoAnalysisResult, VideoUploadStage } from "@/types/analysis";

const ACCEPTED_EXTENSIONS = [".mp4", ".mov", ".avi", ".webm"];
const ACCEPTED_MIME_TYPES = ["video/mp4", "video/quicktime", "video/x-msvideo", "video/webm"];
const ACCEPT_ATTR = [...ACCEPTED_MIME_TYPES, ...ACCEPTED_EXTENSIONS].join(",");

const PHASE_LABEL: Record<AnalysisPhase, string> = {
  uploading: "Uploading...",
  processing: "Processing...",
};

interface VideoUploadProps {
  onAnalysisStatusChange?: (status: AnalysisStatus) => void;
  onAnalysisComplete?: (result: VideoAnalysisResult) => void;
  onViewResults?: () => void;
}

function isSupportedVideoFile(file: File): boolean {
  const name = file.name.toLowerCase();
  const hasSupportedExtension = ACCEPTED_EXTENSIONS.some((ext) => name.endsWith(ext));
  const hasSupportedMime = ACCEPTED_MIME_TYPES.includes(file.type);
  return hasSupportedExtension || hasSupportedMime;
}

export default function VideoUpload({
  onAnalysisStatusChange,
  onAnalysisComplete,
  onViewResults,
}: VideoUploadProps) {
  const [stage, setStage] = useState<VideoUploadStage>("empty");
  const [file, setFile] = useState<File | null>(null);
  const [phase, setPhase] = useState<AnalysisPhase>("uploading");
  const [error, setError] = useState<string | null>(null);
  const [dragActive, setDragActive] = useState(false);

  const inputRef = useRef<HTMLInputElement>(null);
  // Guards against a resolved request from a file the user already removed.
  const requestIdRef = useRef(0);

  useEffect(() => {
    const analysisStatus: AnalysisStatus =
      stage === "analyzing"
        ? "analyzing"
        : stage === "completed"
          ? "completed"
          : stage === "failed"
            ? "error"
            : "ready";
    onAnalysisStatusChange?.(analysisStatus);
  }, [stage, onAnalysisStatusChange]);

  const acceptFile = useCallback((candidate: File) => {
    if (!isSupportedVideoFile(candidate)) {
      setError("Unsupported file type. Please choose an MP4, MOV, AVI, or WEBM video.");
      return;
    }
    setError(null);
    setFile(candidate);
    setStage("selected");
  }, []);

  const handleInputChange = useCallback(
    (event: React.ChangeEvent<HTMLInputElement>) => {
      const candidate = event.target.files?.[0];
      event.target.value = "";
      if (candidate) acceptFile(candidate);
    },
    [acceptFile]
  );

  const handleDrop = useCallback(
    (event: React.DragEvent<HTMLDivElement>) => {
      event.preventDefault();
      setDragActive(false);
      const candidate = event.dataTransfer.files?.[0];
      if (candidate) acceptFile(candidate);
    },
    [acceptFile]
  );

  const handleRemove = useCallback(() => {
    requestIdRef.current += 1; // abandon any in-flight analysis
    setFile(null);
    setError(null);
    setStage("empty");
  }, []);

  const handleAnalyze = useCallback(async () => {
    if (!file) return;

    const requestId = ++requestIdRef.current;
    setError(null);
    setPhase("uploading");
    setStage("analyzing");

    try {
      const result = await analyzeVideo({ file, exerciseId: "bicep-curl" }, (next) => {
        if (requestId === requestIdRef.current) setPhase(next);
      });
      if (requestId !== requestIdRef.current) return;
      onAnalysisComplete?.(result);
      setStage("completed");
    } catch (caught) {
      if (requestId !== requestIdRef.current) return;
      setError(caught instanceof Error ? caught.message : "Video analysis failed.");
      setStage("failed");
    }
  }, [file, onAnalysisComplete]);

  return (
    <GlassCard className="flex min-h-[280px] flex-col items-center justify-center text-center">
      {stage === "empty" && (
        <div
          role="button"
          tabIndex={0}
          onClick={() => inputRef.current?.click()}
          onKeyDown={(e) => (e.key === "Enter" || e.key === " ") && inputRef.current?.click()}
          onDragOver={(e) => {
            e.preventDefault();
            setDragActive(true);
          }}
          onDragLeave={() => setDragActive(false)}
          onDrop={handleDrop}
          className={cn(
            "flex w-full flex-col items-center gap-3 rounded-xl border-2 border-dashed px-6 py-10 transition-colors cursor-pointer",
            dragActive ? "border-accent-strong bg-accent-soft" : "border-hairline-strong hover:border-hairline-strong"
          )}
        >
          <span className="flex size-14 items-center justify-center rounded-full border border-hairline-strong bg-glass-strong text-accent-strong">
            <UploadCloud className="size-6" strokeWidth={1.5} />
          </span>
          <div>
            <p className="text-sm font-semibold text-text-primary">Upload Workout Video</p>
            <p className="mt-1 text-xs text-text-muted">Drag &amp; drop your video here</p>
          </div>
          <p className="text-xs text-text-muted">or</p>
          <NeonButton
            type="button"
            variant="secondary"
            onClick={(e) => {
              e.stopPropagation();
              inputRef.current?.click();
            }}
          >
            Choose Video
          </NeonButton>
          <p className="text-[11px] font-medium uppercase tracking-wide text-text-muted">
            MP4 • MOV • AVI • WEBM
          </p>
          {error && <p className="text-xs font-medium text-status-critical-fg">{error}</p>}
          <input
            ref={inputRef}
            type="file"
            accept={ACCEPT_ATTR}
            onChange={handleInputChange}
            className="hidden"
            aria-label="Choose a workout video file"
          />
        </div>
      )}

      {stage === "selected" && file && (
        <div className="flex w-full flex-col items-center gap-4">
          <span className="flex size-14 items-center justify-center rounded-full border border-hairline-strong bg-glass-strong text-accent-strong">
            <FileVideo className="size-6" strokeWidth={1.5} />
          </span>
          <div>
            <p className="max-w-xs truncate text-sm font-semibold text-text-primary">{file.name}</p>
            <p className="mt-0.5 text-xs text-text-muted">{formatFileSize(file.size)}</p>
          </div>
          <StatusBadge tone="accent">Ready for analysis</StatusBadge>
          <div className="flex items-center gap-2.5">
            <NeonButton variant="secondary" icon={<X className="size-4" />} onClick={handleRemove}>
              Remove
            </NeonButton>
            <NeonButton variant="primary" icon={<UploadCloud className="size-4" />} onClick={handleAnalyze}>
              Analyze Video
            </NeonButton>
          </div>
        </div>
      )}

      {stage === "analyzing" && file && (
        <div className="flex w-full flex-col items-center gap-4">
          <Loader2 className="size-8 animate-spin text-accent-strong" strokeWidth={2} />
          <p className="text-sm font-semibold text-text-primary">Analyzing {file.name}</p>
          {/* The backend reports no granular progress, so this stays an
              indeterminate state label rather than a fabricated percentage. */}
          <p className="text-xs font-medium uppercase tracking-wide text-text-muted">{PHASE_LABEL[phase]}</p>
          <p className="max-w-xs text-[11px] text-text-muted">
            Pose analysis runs on every frame — a 30 second clip takes about a minute.
          </p>
        </div>
      )}

      {stage === "completed" && file && (
        <div className="flex w-full flex-col items-center gap-4">
          <span className="flex size-14 items-center justify-center rounded-full border border-[rgba(12,163,12,0.35)] bg-[rgba(12,163,12,0.14)] text-status-good-fg">
            <CheckCircle2 className="size-7" strokeWidth={1.75} />
          </span>
          <p className="text-sm font-semibold text-text-primary">Analysis Complete</p>
          <p className="max-w-xs truncate text-xs text-text-muted">{file.name}</p>
          <div className="flex items-center gap-2.5">
            <NeonButton variant="ghost" onClick={handleRemove}>
              Upload Another Video
            </NeonButton>
            <NeonButton variant="primary" onClick={onViewResults}>
              View Results
            </NeonButton>
          </div>
        </div>
      )}

      {stage === "failed" && (
        <div className="flex w-full flex-col items-center gap-4">
          <span className="flex size-14 items-center justify-center rounded-full border border-[rgba(208,59,59,0.35)] bg-[rgba(208,59,59,0.14)] text-status-critical-fg">
            <AlertTriangle className="size-7" strokeWidth={1.75} />
          </span>
          <p className="text-sm font-semibold text-text-primary">Analysis Failed</p>
          <p className="max-w-sm text-xs text-text-muted">{error}</p>
          <div className="flex items-center gap-2.5">
            <NeonButton variant="secondary" onClick={handleRemove}>
              Choose Another Video
            </NeonButton>
            {file && (
              <NeonButton variant="primary" onClick={handleAnalyze}>
                Try Again
              </NeonButton>
            )}
          </div>
        </div>
      )}
    </GlassCard>
  );
}
