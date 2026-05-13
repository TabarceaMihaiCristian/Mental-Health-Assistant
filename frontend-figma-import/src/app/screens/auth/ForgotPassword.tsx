import { useState } from "react";
import { Button } from "../../components/ui/Button";
import { Input } from "../../components/ui/Input";
import { CheckCircle, ArrowLeft } from "lucide-react";

export default function ForgotPassword() {
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
              Check Your Email
            </h2>
            <p className="text-[--muted-foreground] mb-6">
              We've sent password reset instructions to your email address.
            </p>
            <Button variant="primary" className="w-full" onClick={() => setSubmitted(false)}>
              Back to Sign In
            </Button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-[--sand-50] to-[--teal-50] flex items-center justify-center p-6">
      <div className="w-full max-w-md">
        <a href="#login" className="inline-flex items-center gap-2 text-[--primary] hover:underline mb-6">
          <ArrowLeft className="size-4" />
          Back to Sign In
        </a>

        <div className="text-center mb-8">
          <h1 className="text-3xl font-[--font-weight-semibold] text-[--foreground] mb-2">
            Reset Your Password
          </h1>
          <p className="text-[--muted-foreground]">
            Enter your email and we'll send you instructions to reset your password
          </p>
        </div>

        <div className="bg-[--card] rounded-[--radius-xl] shadow-[--shadow-xl] p-8 border border-[--border]">
          <form className="space-y-5" onSubmit={(e) => { e.preventDefault(); setSubmitted(true); }}>
            <Input
              type="email"
              label="Email"
              placeholder="email@example.com"
              autoComplete="email"
            />

            <Button variant="primary" className="w-full" size="lg" type="submit">
              Send Reset Instructions
            </Button>
          </form>
        </div>
      </div>
    </div>
  );
}
