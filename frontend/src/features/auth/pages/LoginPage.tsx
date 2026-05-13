import { useState, type FormEvent } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { AlertCircle } from "lucide-react";
import { useAuth } from "../../../app/use-auth";
import { AuthShell } from "../../../components/layout/AuthShell";
import { Button } from "../../../components/ui/Button";
import { TextField } from "../../../components/ui/Fields";
import { ApiError } from "../../../lib/api";

export function LoginPage() {
  const { loginWithPassword } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const redirectTo = (location.state as { from?: { pathname?: string } } | undefined)?.from?.pathname ?? "/app";
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [rememberMe, setRememberMe] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setIsSubmitting(true);

    try {
      await loginWithPassword({ email, password });
      navigate(redirectTo, { replace: true });
    } catch (err) {
      setError(err instanceof ApiError ? err.detail : "Unable to sign in right now.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <AuthShell title="Welcome back" subtitle="Sign in to continue your care journey." footnote="Protected by your backend authentication flow and session bootstrap endpoint.">
      {error ? (
        <div className="mb-6 flex items-start gap-3 rounded-[24px] border border-[--destructive] bg-[--red-100] px-4 py-4 text-sm text-[--foreground]">
          <AlertCircle className="mt-0.5 size-5 shrink-0 text-[--destructive]" />
          <p>{error}</p>
        </div>
      ) : null}

      <form className="grid gap-5" onSubmit={handleSubmit}>
        <TextField label="Email" type="email" autoComplete="email" placeholder="email@example.com" value={email} onChange={(event) => setEmail(event.target.value)} required />
        <TextField label="Password" type="password" autoComplete="current-password" placeholder="••••••••" value={password} onChange={(event) => setPassword(event.target.value)} required />

        <div className="flex items-center justify-between gap-4 text-sm text-[--muted-foreground]">
          <label className="flex items-center gap-2">
            <input type="checkbox" checked={rememberMe} onChange={(event) => setRememberMe(event.target.checked)} className="size-4 rounded accent-[--primary]" />
            <span>Remember me</span>
          </label>
          <Link to="/forgot-password" className="font-medium text-[--primary] hover:underline">Forgot password?</Link>
        </div>

        <Button type="submit" size="lg" disabled={isSubmitting}>
          {isSubmitting ? "Signing in..." : "Sign in"}
        </Button>
      </form>

      <p className="mt-6 text-center text-sm text-[--muted-foreground]">
        Don&apos;t have an account? <Link to="/register" className="font-medium text-[--primary] hover:underline">Create one</Link>
      </p>
    </AuthShell>
  );
}


