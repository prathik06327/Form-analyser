import type { ReactNode } from "react";
import { cn } from "@/lib/utils";

interface SectionLabelProps {
  children: ReactNode;
  icon?: ReactNode;
  className?: string;
}

export default function SectionLabel({ children, icon, className }: SectionLabelProps) {
  return (
    <div className={cn("flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-text-muted", className)}>
      {icon}
      {children}
    </div>
  );
}
