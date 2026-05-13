import type { HTMLAttributes, ReactNode } from "react";
import { cn } from "../../lib/cn";

export function Card({ className, ...props }: HTMLAttributes<HTMLDivElement>) {
  return <div className={cn("rounded-[28px] border border-[--border] bg-white shadow-[var(--shadow-lg)]", className)} {...props} />;
}

export function CardHeader({ className, ...props }: HTMLAttributes<HTMLDivElement>) {
  return <div className={cn("px-6 pt-6", className)} {...props} />;
}

export function CardTitle({ className, ...props }: HTMLAttributes<HTMLHeadingElement>) {
  return <h2 className={cn("text-xl font-semibold tracking-[-0.02em] text-[--foreground]", className)} {...props} />;
}

export function CardDescription({ className, ...props }: HTMLAttributes<HTMLParagraphElement>) {
  return <p className={cn("mt-2 text-sm text-[--muted-foreground]", className)} {...props} />;
}

export function CardContent({ className, ...props }: HTMLAttributes<HTMLDivElement>) {
  return <div className={cn("px-6 pb-6", className)} {...props} />;
}

export function StatCard({ title, value, meta, icon }: { title: string; value: string; meta?: string; icon?: ReactNode }) {
  return (
    <Card>
      <CardContent className="flex items-start justify-between gap-4 p-6">
        <div>
          <p className="text-sm text-[--muted-foreground]">{title}</p>
          <p className="mt-2 text-3xl font-semibold tracking-[-0.03em]">{value}</p>
          {meta ? <p className="mt-2 text-xs text-[--muted-foreground]">{meta}</p> : null}
        </div>
        {icon ? <div className="rounded-2xl bg-[--primary-light] p-3 text-[--primary]">{icon}</div> : null}
      </CardContent>
    </Card>
  );
}
