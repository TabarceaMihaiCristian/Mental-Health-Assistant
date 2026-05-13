import type { ReactNode } from "react";

export function AuthShell({ title, subtitle, children, footnote }: { title: string; subtitle: string; children: ReactNode; footnote?: string }) {
  return (
    <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-[--sand-50] via-white to-[--teal-50] px-6 py-12">
      <div className="w-full max-w-md">
        <div className="mb-8 text-center">
          <p className="text-sm uppercase tracking-[0.18em] text-[--muted-foreground]">Secure access</p>
          <h1 className="mt-3 text-4xl font-semibold tracking-[-0.04em] text-[--foreground]">{title}</h1>
          <p className="mt-3 text-[--muted-foreground]">{subtitle}</p>
        </div>
        <div className="rounded-[32px] border border-[--border] bg-white p-8 shadow-[var(--shadow-xl)]">{children}</div>
        {footnote ? <p className="mt-6 text-center text-xs text-[--muted-foreground]">{footnote}</p> : null}
      </div>
    </div>
  );
}
