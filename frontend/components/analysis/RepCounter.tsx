"use client";

import { useEffect, useRef, useState } from "react";
import { cn } from "@/lib/utils";

interface RepCounterProps {
  reps: number;
  className?: string;
}

export default function RepCounter({ reps, className }: RepCounterProps) {
  const [pop, setPop] = useState(false);
  const prevReps = useRef(reps);

  useEffect(() => {
    if (prevReps.current !== reps) {
      prevReps.current = reps;
      setPop(true);
      const id = setTimeout(() => setPop(false), 320);
      return () => clearTimeout(id);
    }
  }, [reps]);

  return (
    <div className={cn("flex flex-col items-center", className)}>
      <span
        className={cn(
          "text-6xl font-bold tabular-nums tracking-tight text-text-primary sm:text-7xl",
          pop && "animate-count-pop"
        )}
      >
        {reps}
      </span>
      <span className="mt-1 text-xs font-semibold uppercase tracking-[0.2em] text-text-muted">Reps</span>
    </div>
  );
}
