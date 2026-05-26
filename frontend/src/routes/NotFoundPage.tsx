import { ButtonLink } from "../components/ui/Button";

export function NotFoundPage() {
  return (
    <div className="flex min-h-screen items-center justify-center px-6">
      <div className="max-w-xl rounded-[32px] border border-[--border] bg-white p-10 text-center shadow-[var(--shadow-xl)]">
        <p className="text-sm uppercase tracking-[0.18em] text-[--muted-foreground]">404</p>
        <h1 className="mt-4 text-4xl font-semibold tracking-[-0.04em]">Page not found</h1>
        <p className="mt-4 text-[--muted-foreground]">The page you are looking for is not available or may have moved.</p>
        <div className="mt-8 flex items-center justify-center gap-3">
          <ButtonLink to="/" variant="secondary">Public home</ButtonLink>
          <ButtonLink to="/app">Workspace</ButtonLink>
        </div>
      </div>
    </div>
  );
}
