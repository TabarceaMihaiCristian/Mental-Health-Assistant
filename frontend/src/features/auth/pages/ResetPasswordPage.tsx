import { useMemo, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { AuthShell } from "../../../components/layout/AuthShell";
import { Button } from "../../../components/ui/Button";
import { TextField } from "../../../components/ui/Fields";
import { ApiError } from "../../../lib/api";
import { resetPassword } from "../authApi";

export function ResetPasswordPage() {
  const [searchParams] = useSearchParams();
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const token = searchParams.get("token")?.trim() ?? "";
  const validationError = useMemo(() => {
    if (!token) {
      return "This reset link is missing a token. Request a new reset link and try again.";
    }
    if (confirmPassword && password !== confirmPassword) {
      return "Passwords do not match.";
    }
    return null;
  }, [confirmPassword, password, token]);

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (validationError) {
      setError(validationError);
      return;
    }

    setIsSubmitting(true);
    setError(null);
    setMessage(null);

    try {
      const response = await resetPassword({ token, password });
      setMessage(response.message);
      setPassword("");
      setConfirmPassword("");
    } catch (caughtError) {
      setError(caughtError instanceof ApiError ? caughtError.detail : "Unable to reset the password right now.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <AuthShell title="Choose a new password" subtitle="Use the token from your reset link to set a new password for the account.">
      {message ? (
        <div className="rounded-[24px] border border-[--teal-200] bg-[--teal-50] px-4 py-4 text-sm text-[--foreground]">{message}</div>
      ) : (
        <form className="grid gap-5" onSubmit={handleSubmit}>
          <TextField
            label="New password"
            type="password"
            placeholder="Enter a new password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            disabled={isSubmitting || !token}
            required
          />
          <TextField
            label="Confirm password"
            type="password"
            placeholder="Repeat the new password"
            value={confirmPassword}
            onChange={(event) => setConfirmPassword(event.target.value)}
            error={error ?? validationError ?? undefined}
            disabled={isSubmitting || !token}
            required
          />
          <Button type="submit" size="lg" disabled={isSubmitting || Boolean(validationError) || password.length < 8}>
            {isSubmitting ? "Updating..." : "Update password"}
          </Button>
        </form>
      )}
      <p className="mt-6 text-center text-sm text-[--muted-foreground]">
        <Link to="/login" className="font-medium text-[--primary] hover:underline">Back to sign in</Link>
      </p>
    </AuthShell>
  );
}
