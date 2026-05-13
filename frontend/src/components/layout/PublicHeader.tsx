import { HeartHandshake } from "lucide-react";
import { ButtonLink } from "../ui/Button";

export function PublicHeader() {
  return (
    <header className="sticky top-0 z-20 border-b border-[--border] bg-[color:rgba(255,255,255,0.84)] backdrop-blur-md">
      <div className="mx-auto flex h-18 max-w-7xl items-center justify-between px-6">
        <div className="flex items-center gap-3">
          <div className="flex size-11 items-center justify-center rounded-2xl bg-[--primary-light] text-[--primary]">
            <HeartHandshake className="size-6" />
          </div>
          <div>
            <p className="text-sm uppercase tracking-[0.18em] text-[--muted-foreground]">Mental Health</p>
            <p className="text-lg font-semibold tracking-[-0.02em]">Assistant</p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <ButtonLink to="/login" variant="ghost" size="sm">Sign In</ButtonLink>
          <ButtonLink to="/register" size="sm">Get Started</ButtonLink>
        </div>
      </div>
    </header>
  );
}
