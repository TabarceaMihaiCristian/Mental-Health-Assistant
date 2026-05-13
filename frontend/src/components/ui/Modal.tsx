import { useEffect, type ReactNode } from "react";
import { createPortal } from "react-dom";
import { X } from "lucide-react";
import { cn } from "../../lib/cn";

export function Modal({ isOpen, title, children, onClose, size = "lg" }: { isOpen: boolean; title: string; children: ReactNode; onClose: () => void; size?: "md" | "lg" | "xl" }) {
  useEffect(() => {
    if (!isOpen) {
      return;
    }

    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        onClose();
      }
    };

    document.body.style.overflow = "hidden";
    document.addEventListener("keydown", onKeyDown);

    return () => {
      document.body.style.overflow = "";
      document.removeEventListener("keydown", onKeyDown);
    };
  }, [isOpen, onClose]);

  if (!isOpen) {
    return null;
  }

  const width = size === "md" ? "max-w-xl" : size === "xl" ? "max-w-5xl" : "max-w-3xl";

  return createPortal(
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <button className="absolute inset-0 bg-[color:rgba(8,35,33,0.35)] backdrop-blur-sm" aria-label="Close modal" onClick={onClose} />
      <div className={cn("relative z-10 w-full rounded-[32px] border border-[--border] bg-white shadow-[var(--shadow-xl)]", width)}>
        <div className="flex items-center justify-between border-b border-[--border] px-6 py-5">
          <h2 className="text-xl font-semibold tracking-[-0.02em]">{title}</h2>
          <button className="rounded-full p-2 text-[--muted-foreground] transition hover:bg-[--accent]" onClick={onClose}>
            <X className="size-5" />
          </button>
        </div>
        <div className="px-6 py-6">{children}</div>
      </div>
    </div>,
    document.body,
  );
}
