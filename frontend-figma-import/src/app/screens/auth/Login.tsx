import { useState } from "react";
import { Button } from "../../components/ui/Button";
import { Input } from "../../components/ui/Input";
import { AlertCircle } from "lucide-react";

export default function Login() {
  const [error, setError] = useState("");

  return (
    <div className="min-h-screen bg-gradient-to-br from-[--sand-50] to-[--teal-50] flex items-center justify-center p-6">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-[--font-weight-semibold] text-[--foreground] mb-2">
            Welcome Back
          </h1>
          <p className="text-[--muted-foreground]">
            Sign in to continue your mental health journey
          </p>
        </div>

        <div className="bg-[--card] rounded-[--radius-xl] shadow-[--shadow-xl] p-8 border border-[--border]">
          {error && (
            <div className="mb-6 flex items-start gap-3 p-4 rounded-[--radius-lg] bg-[--red-100] border border-[--destructive]">
              <AlertCircle className="size-5 text-[--destructive] mt-0.5 flex-shrink-0" />
              <p className="text-sm text-[--foreground]">{error}</p>
            </div>
          )}

          <form className="space-y-5">
            <Input
              type="email"
              label="Email"
              placeholder="email@example.com"
              autoComplete="email"
            />

            <Input
              type="password"
              label="Password"
              placeholder="••••••••"
              autoComplete="current-password"
            />

            <div className="flex items-center justify-between text-sm">
              <label className="flex items-center gap-2 cursor-pointer">
                <input type="checkbox" className="size-4 rounded accent-[--primary]" />
                <span className="text-[--foreground]">Remember me</span>
              </label>
              <a href="#forgot-password" className="text-[--primary] hover:underline">
                Forgot password?
              </a>
            </div>

            <Button variant="primary" className="w-full" size="lg">
              Sign In
            </Button>
          </form>

          <div className="mt-6 text-center text-sm">
            <span className="text-[--muted-foreground]">Don't have an account? </span>
            <a href="#register" className="text-[--primary] font-[--font-weight-medium] hover:underline">
              Sign up
            </a>
          </div>
        </div>

        <p className="mt-6 text-center text-xs text-[--muted-foreground]">
          Protected by bank-level encryption and HIPAA compliant
        </p>
      </div>
    </div>
  );
}
