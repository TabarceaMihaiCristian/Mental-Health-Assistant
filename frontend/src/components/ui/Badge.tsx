import type { HTMLAttributes } from "react";
import { cn } from "../../lib/cn";

const variants = {
  default: "bg-[--primary] text-white",
  muted: "bg-[--secondary] text-[--foreground]",
  success: "bg-[--success-light] text-[--success]",
  warning: "bg-[--warning-light] text-[--warning]",
  danger: "bg-[--red-100] text-[--destructive]",
};

export function Badge({ className, children, variant = "default", ...props }: HTMLAttributes<HTMLSpanElement> & { variant?: keyof typeof variants }) {
  return (
    <span className={cn("inline-flex items-center rounded-full px-3 py-1 text-xs font-semibold", variants[variant], className)} {...props}>
      {children}
    </span>
  );
}
