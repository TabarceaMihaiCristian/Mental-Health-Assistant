import { HTMLAttributes, ReactNode } from "react";
import { cn } from "../../lib/utils";

interface EmptyStateProps extends HTMLAttributes<HTMLDivElement> {
  icon?: ReactNode;
  title: string;
  description?: string;
  action?: ReactNode;
}

export function EmptyState({ icon, title, description, action, className, ...props }: EmptyStateProps) {
  return (
    <div
      className={cn(
        "flex flex-col items-center justify-center text-center py-12 px-6",
        className
      )}
      {...props}
    >
      {icon && <div className="mb-4 text-[--muted-foreground]">{icon}</div>}
      <h3 className="mb-2 font-[--font-weight-semibold] text-[--foreground]">{title}</h3>
      {description && <p className="mb-6 text-[--muted-foreground] max-w-sm">{description}</p>}
      {action && <div>{action}</div>}
    </div>
  );
}
