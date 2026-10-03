import type { HTMLAttributes, ReactNode } from "react";
import { cn } from "@/lib/utils";

interface GlassCardProps extends HTMLAttributes<HTMLDivElement> {
  children: ReactNode;
  padding?: "none" | "sm" | "md" | "lg";
}

const PADDING: Record<NonNullable<GlassCardProps["padding"]>, string> = {
  none: "",
  sm: "p-4",
  md: "p-5 sm:p-6",
  lg: "p-6 sm:p-8",
};

export default function GlassCard({
  children,
  padding = "md",
  className,
  ...rest
}: GlassCardProps) {
  return (
    <div
      className={cn(
        "glass rounded-2xl shadow-[0_1px_0_0_rgba(255,255,255,0.04)_inset]",
        PADDING[padding],
        className
      )}
      {...rest}
    >
      {children}
    </div>
  );
}
