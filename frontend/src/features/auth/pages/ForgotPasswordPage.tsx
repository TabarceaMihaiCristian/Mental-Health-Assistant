import { useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { AuthShell } from "../../../components/layout/AuthShell";
import { Button } from "../../../components/ui/Button";
import { TextField } from "../../../components/ui/Fields";
import { ApiError } from "../../../lib/api";
import { requestPasswordReset } from "../authApi";

export function ForgotPasswordPage() {
  const [email, setEmail] = useState("");
  const [submittedMessage, setSubmittedMessage] = useState<string | null>(null);
  const [resetToken, setResetToken] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const resetUrl = useMemo(() => {
    if (!resetToken) {
      return null;
    }

    return `${window.location.origin}/reset-password?token=${encodeURIComponent(resetToken)}`;
  }, [resetToken]);

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsSubmitting(true);
    setError(null);
    setSubmittedMessage(null);
    setResetToken(null);

    try {
      const response = await requestPasswordReset({ email: email.trim() });
      setSubmittedMessage(response.message);
      setResetToken(response.reset_token ?? null);
    } catch (caughtError) {
      setError(caughtError instanceof ApiError ? caughtError.detail : "Unable to request a password reset right now.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <AuthShell title="Reset access" subtitle="Request a password reset token for your account. In development, the reset link is shown directly because email delivery is not wired yet.">
      <form className="grid gap-5" onSubmit={handleSubmit}>
        <TextField
          label="Email"
          type="email"
          placeholder="email@example.com"
          value={email}
          onChange={(event) => setEmail(event.target.value)}
          disabled={isSubmitting}
          required
        />
        {error ? <div className="rounded-[24px] border border-[--destructive] bg-[color:rgba(220,38,38,0.08)] px-4 py-4 text-sm text-[--foreground]">{error}</div> : null}
        {submittedMessage ? (
          <div className="rounded-[24px] border border-[--teal-200] bg-[--teal-50] px-4 py-4 text-sm text-[--foreground]">
            <p>{submittedMessage}</p>
            {resetUrl ? (
              <div className="mt-3 grid gap-2">
                <p className="text-xs uppercase tracking-[0.24em] text-[--muted-foreground]">Development reset link</p>
                <a href={resetUrl} className="break-all font-medium text-[--primary] hover:underline">
                  {resetUrl}
                </a>
              </div>
            ) : null}
          </div>
        ) : null}
        <Button type="submit" size="lg" disabled={isSubmitting || !email.trim()}>
          {isSubmitting ? "Requesting..." : "Request reset link"}
        </Button>
      </form>
      <p className="mt-6 text-center text-sm text-[--muted-foreground]">
        Remembered your password? <Link to="/login" className="font-medium text-[--primary] hover:underline">Back to sign in</Link>
      </p>
    </AuthShell>
  );
}
