import { useState, type FormEvent } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../../../app/use-auth";
import { AuthShell } from "../../../components/layout/AuthShell";
import { Button } from "../../../components/ui/Button";
import { SelectField, TextField } from "../../../components/ui/Fields";
import { ApiError } from "../../../lib/api";
import { readStoredAuth } from "../../../lib/auth-storage";
import { getHomePathForRole } from "../../../lib/role-home";

export function RegisterPage() {
  const { registerWithPassword } = useAuth();
  const navigate = useNavigate();
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [role, setRole] = useState("user");
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (password !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    if (role !== "user") {
      setError("Public registration is currently connected for user accounts only.");
      return;
    }

    setError(null);
    setIsSubmitting(true);
    try {
      await registerWithPassword({ full_name: fullName.trim(), email, password });
      const nextRole = readStoredAuth()?.user?.role;
      navigate(getHomePathForRole(nextRole), { replace: true });
    } catch (err) {
      setError(err instanceof ApiError ? err.detail : "Unable to create the account right now.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <AuthShell title="Create your account" subtitle="Begin with a clean, secure workspace for support and specialist coordination." footnote="Create your account to book care, track progress, and stay in control of your plan.">
      {error ? <div className="mb-6 rounded-[24px] border border-[--destructive] bg-[--red-100] px-4 py-4 text-sm text-[--foreground]">{error}</div> : null}
      <form className="grid gap-5" onSubmit={handleSubmit}>
        <TextField label="Full name" type="text" autoComplete="name" placeholder="Jane Doe" value={fullName} onChange={(event) => setFullName(event.target.value)} required />
        <TextField label="Email" type="email" autoComplete="email" placeholder="email@example.com" value={email} onChange={(event) => setEmail(event.target.value)} required />
        <div className="grid gap-5 md:grid-cols-2">
          <TextField label="Password" type="password" autoComplete="new-password" placeholder="password" value={password} onChange={(event) => setPassword(event.target.value)} required />
          <TextField label="Confirm password" type="password" autoComplete="new-password" placeholder="password" value={confirmPassword} onChange={(event) => setConfirmPassword(event.target.value)} required />
        </div>
        <SelectField label="I am a..." value={role} onChange={(event) => setRole(event.target.value)}>
          <option value="user">Individual seeking support</option>
          <option value="specialist">Mental health specialist</option>
        </SelectField>
        <label className="flex items-start gap-3 text-sm text-[--muted-foreground]">
          <input type="checkbox" required className="mt-1 size-4 rounded accent-[--primary]" />
          <span>I agree to the terms of service and privacy policy.</span>
        </label>
        <Button type="submit" size="lg" disabled={isSubmitting}>{isSubmitting ? "Creating account..." : "Create account"}</Button>
      </form>
      <p className="mt-6 text-center text-sm text-[--muted-foreground]">
        Already have an account? <Link to="/login" className="font-medium text-[--primary] hover:underline">Sign in</Link>
      </p>
    </AuthShell>
  );
}
