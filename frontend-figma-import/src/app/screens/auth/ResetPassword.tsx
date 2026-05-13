import { useState } from "react";
import { Button } from "../../components/ui/Button";
import { Input } from "../../components/ui/Input";
import { CheckCircle } from "lucide-react";

export default function ResetPassword() {
  const [submitted, setSubmitted] = useState(false);

  if (submitted) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-[--sand-50] to-[--teal-50] flex items-center justify-center p-6">
        <div className="w-full max-w-md">
          <div className="bg-[--card] rounded-[--radius-xl] shadow-[--shadow-xl] p-8 border border-[--border] text-center">
            <div className="size-16 mx-auto mb-4 rounded-full bg-[--success-light] flex items-center justify-center">
              <CheckCircle className="size-8 text-[--success]" />
            </div>
            <h2 className="text-2xl font-[--font-weight-semibold] text-[--foreground] mb-2">
              Password Reset Successful
            </h2>
            <p className="text-[--muted-foreground] mb-6">
              Your password has been successfully updated. You can now sign in with your new password.
            </p>
            <Button variant="primary" className="w-full">
              Sign In
            </Button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-[--sand-50] to-[--teal-50] flex items-center justify-center p-6">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-[--font-weight-semibold] text-[--foreground] mb-2">
            Set New Password
          </h1>
          <p className="text-[--muted-foreground]">
            Enter your new password below
          </p>
        </div>

        <div className="bg-[--card] rounded-[--radius-xl] shadow-[--shadow-xl] p-8 border border-[--border]">
          <form className="space-y-5" onSubmit={(e) => { e.preventDefault(); setSubmitted(true); }}>
            <Input
              type="password"
              label="New Password"
              placeholder="••••••••"
              autoComplete="new-password"
            />

            <Input
              type="password"
              label="Confirm New Password"
              placeholder="••••••••"
              autoComplete="new-password"
            />

            <div className="text-sm text-[--muted-foreground] space-y-1">
              <p className="font-[--font-weight-medium] text-[--foreground]">Password must contain:</p>
              <ul className="space-y-1 ml-4">
                <li>• At least 8 characters</li>
                <li>• One uppercase letter</li>
                <li>• One lowercase letter</li>
                <li>• One number</li>
              </ul>
            </div>

            <Button variant="primary" className="w-full" size="lg" type="submit">
              Reset Password
            </Button>
          </form>
        </div>
      </div>
    </div>
  );
}
