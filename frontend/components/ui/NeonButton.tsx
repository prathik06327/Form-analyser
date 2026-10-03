import type { ButtonHTMLAttributes, ReactNode } from "react";
import { Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";

type Variant = "primary" | "secondary" | "danger" | "ghost";

interface NeonButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  children: ReactNode;
  variant?: Variant;
  icon?: ReactNode;
  loading?: boolean;
}

const VARIANT_CLASSES: Record<Variant, string> = {
  primary:
    "bg-accent text-white shadow-[0_0_0_1px_rgba(124,92,255,0.5),0_8px_24px_-8px_rgba(124,92,255,0.65)] hover:bg-accent-strong hover:shadow-[0_0_0_1px_rgba(154,123,255,0.6),0_10px_28px_-6px_rgba(124,92,255,0.75)]",
  secondary:
    "bg-glass-strong text-text-primary border border-hairline-strong hover:bg-[rgba(255,255,255,0.1)]",
  danger:
    "bg-[rgba(208,59,59,0.12)] text-status-critical-fg border border-[rgba(208,59,59,0.35)] hover:bg-[rgba(208,59,59,0.2)]",
  ghost: "bg-transparent text-text-secondary hover:text-text-primary hover:bg-glass",
};

export default function NeonButton({
  children,
  variant = "primary",
  icon,
  loading = false,
  disabled,
  className,
  ...rest
}: NeonButtonProps) {
  return (
    <button
      disabled={disabled || loading}
      className={cn(
        "inline-flex items-center justify-center gap-2 rounded-xl px-4 py-2.5 text-sm font-semibold",
        "transition-all duration-150 active:scale-[0.98]",
        "disabled:opacity-45 disabled:cursor-not-allowed disabled:active:scale-100",
        "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-strong focus-visible:ring-offset-2 focus-visible:ring-offset-page",
        VARIANT_CLASSES[variant],
        className
      )}
      {...rest}
    >
      {loading ? <Loader2 className="size-4 animate-spin" aria-hidden /> : icon}
      {children}
    </button>
  );
}
