"use client";

import { Camera, Upload } from "lucide-react";
import type { LucideIcon } from "lucide-react";
import { cn } from "@/lib/utils";
import type { InputMode } from "@/types/analysis";

interface ExerciseInputProps {
  mode: InputMode;
  onChange: (mode: InputMode) => void;
  className?: string;
}

const OPTIONS: Array<{ id: InputMode; label: string; icon: LucideIcon }> = [
  { id: "live-camera", label: "Live Camera", icon: Camera },
  { id: "upload-video", label: "Upload Video", icon: Upload },
];

export default function ExerciseInput({ mode, onChange, className }: ExerciseInputProps) {
  return (
    <div
      role="tablist"
      aria-label="Exercise input mode"
      className={cn("glass inline-flex items-center gap-1 self-center rounded-full p-1", className)}
    >
      {OPTIONS.map((option) => {
        const Icon = option.icon;
        const active = option.id === mode;
        return (
          <button
            key={option.id}
            type="button"
            role="tab"
            aria-selected={active}
            onClick={() => onChange(option.id)}
            className={cn(
              "flex items-center gap-2 rounded-full px-4 py-2 text-sm font-semibold transition-all duration-150",
              active
                ? "bg-accent text-white shadow-[0_0_0_1px_rgba(124,92,255,0.5),0_6px_18px_-6px_rgba(124,92,255,0.65)]"
                : "text-text-secondary hover:text-text-primary"
            )}
          >
            <Icon className="size-4" strokeWidth={2} />
            {option.label}
          </button>
        );
      })}
    </div>
  );
}
