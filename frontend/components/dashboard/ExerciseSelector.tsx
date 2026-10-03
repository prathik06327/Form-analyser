"use client";

import { useState, useRef, useEffect } from "react";
import { ChevronDown, Dumbbell } from "lucide-react";
import { cn } from "@/lib/utils";
import type { Exercise, ExerciseId } from "@/types/analysis";

interface ExerciseSelectorProps {
  exercises: Exercise[];
  selected: ExerciseId;
  onSelect: (id: ExerciseId) => void;
}

export default function ExerciseSelector({ exercises, selected, onSelect }: ExerciseSelectorProps) {
  const [open, setOpen] = useState(false);
  const rootRef = useRef<HTMLDivElement>(null);
  const current = exercises.find((e) => e.id === selected);

  useEffect(() => {
    function onClickOutside(event: MouseEvent) {
      if (rootRef.current && !rootRef.current.contains(event.target as Node)) {
        setOpen(false);
      }
    }
    document.addEventListener("mousedown", onClickOutside);
    return () => document.removeEventListener("mousedown", onClickOutside);
  }, []);

  return (
    <div className="relative" ref={rootRef}>
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        aria-haspopup="listbox"
        aria-expanded={open}
        className="flex items-center gap-2 rounded-xl border border-hairline-strong bg-glass-strong px-3.5 py-2 text-sm font-medium text-text-primary transition-colors hover:bg-[rgba(255,255,255,0.1)]"
      >
        <Dumbbell className="size-4 text-accent-strong" />
        {current?.label ?? "Select Exercise"}
        <ChevronDown className={cn("size-4 text-text-muted transition-transform", open && "rotate-180")} />
      </button>

      {open && (
        <ul
          role="listbox"
          className="glass absolute right-0 z-20 mt-2 w-56 overflow-hidden rounded-xl p-1.5 shadow-2xl sm:right-auto sm:left-0"
        >
          {exercises.map((exercise) => (
            <li key={exercise.id}>
              <button
                type="button"
                role="option"
                aria-selected={exercise.id === selected}
                disabled={!exercise.enabled}
                onClick={() => {
                  onSelect(exercise.id);
                  setOpen(false);
                }}
                className={cn(
                  "flex w-full items-center justify-between rounded-lg px-3 py-2 text-left text-sm transition-colors",
                  exercise.id === selected ? "bg-accent-soft text-accent-strong" : "text-text-secondary hover:bg-glass-strong hover:text-text-primary",
                  !exercise.enabled && "cursor-not-allowed opacity-40 hover:bg-transparent hover:text-text-secondary"
                )}
              >
                {exercise.label}
                {!exercise.enabled && <span className="text-[10px] font-semibold uppercase tracking-wide">Soon</span>}
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
