import type { InputHTMLAttributes, ReactNode, SelectHTMLAttributes, TextareaHTMLAttributes } from "react";
import { cn } from "../../lib/cn";

function FieldShell({ label, error, children, helpText }: { label: string; error?: string; helpText?: string; children: ReactNode }) {
  return (
    <label className="grid gap-2 text-sm font-medium text-[--foreground]">
      <span>{label}</span>
      {children}
      {error ? <span className="text-sm text-[--destructive]">{error}</span> : null}
      {!error && helpText ? <span className="text-xs text-[--muted-foreground]">{helpText}</span> : null}
    </label>
  );
}

const inputClassName = "h-12 w-full rounded-2xl border border-[--border] bg-[--input-background] px-4 text-[--foreground] outline-none transition focus:border-[--primary] focus:ring-4 focus:ring-[color:rgba(38,173,165,0.16)] disabled:cursor-not-allowed disabled:opacity-70";

export function TextField({ label, error, helpText, className, ...props }: InputHTMLAttributes<HTMLInputElement> & { label: string; error?: string; helpText?: string }) {
  return (
    <FieldShell label={label} error={error} helpText={helpText}>
      <input className={cn(inputClassName, className)} {...props} />
    </FieldShell>
  );
}

export function SelectField({ label, error, className, children, ...props }: SelectHTMLAttributes<HTMLSelectElement> & { label: string; error?: string; children: ReactNode }) {
  return (
    <FieldShell label={label} error={error}>
      <select className={cn(inputClassName, className)} {...props}>
        {children}
      </select>
    </FieldShell>
  );
}

export function TextareaField({ label, error, className, ...props }: TextareaHTMLAttributes<HTMLTextAreaElement> & { label: string; error?: string }) {
  return (
    <FieldShell label={label} error={error}>
      <textarea className={cn("min-h-28 w-full rounded-2xl border border-[--border] bg-[--input-background] px-4 py-3 text-[--foreground] outline-none transition focus:border-[--primary] focus:ring-4 focus:ring-[color:rgba(38,173,165,0.16)] disabled:cursor-not-allowed disabled:opacity-70", className)} {...props} />
    </FieldShell>
  );
}


