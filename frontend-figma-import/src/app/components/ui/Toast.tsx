import { Toaster as Sonner } from "sonner";

export function Toaster() {
  return (
    <Sonner
      position="top-right"
      toastOptions={{
        classNames: {
          toast:
            "bg-[--card] text-[--card-foreground] border border-[--border] shadow-[--shadow-lg] rounded-[--radius-lg]",
          description: "text-[--muted-foreground]",
          actionButton: "bg-[--primary] text-[--primary-foreground]",
          cancelButton: "bg-[--muted] text-[--muted-foreground]",
          error: "bg-[--destructive] text-[--destructive-foreground] border-[--destructive]",
          success: "bg-[--success] text-[--success-foreground] border-[--success]",
          warning: "bg-[--warning] text-[--warning-foreground] border-[--warning]",
          info: "bg-[--info] text-[--info-foreground] border-[--info]",
        },
      }}
    />
  );
}
