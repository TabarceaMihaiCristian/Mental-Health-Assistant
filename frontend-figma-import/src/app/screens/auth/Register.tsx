import { Button } from "../../components/ui/Button";
import { Input } from "../../components/ui/Input";
import { Select } from "../../components/ui/Select";

export default function Register() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-[--sand-50] to-[--teal-50] flex items-center justify-center p-6">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-[--font-weight-semibold] text-[--foreground] mb-2">
            Create Your Account
          </h1>
          <p className="text-[--muted-foreground]">
            Begin your journey to better mental health
          </p>
        </div>

        <div className="bg-[--card] rounded-[--radius-xl] shadow-[--shadow-xl] p-8 border border-[--border]">
          <form className="space-y-5">
            <div className="grid grid-cols-2 gap-4">
              <Input
                type="text"
                label="First Name"
                placeholder="John"
                autoComplete="given-name"
              />
              <Input
                type="text"
                label="Last Name"
                placeholder="Doe"
                autoComplete="family-name"
              />
            </div>

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
              autoComplete="new-password"
            />

            <Input
              type="password"
              label="Confirm Password"
              placeholder="••••••••"
              autoComplete="new-password"
            />

            <Select
              label="I am a..."
              options={[
                { value: "", label: "Select your role" },
                { value: "user", label: "Individual seeking support" },
                { value: "specialist", label: "Mental health specialist" },
              ]}
            />

            <label className="flex items-start gap-3 cursor-pointer">
              <input type="checkbox" className="size-4 mt-1 rounded accent-[--primary]" />
              <span className="text-sm text-[--foreground]">
                I agree to the{" "}
                <a href="#terms" className="text-[--primary] hover:underline">Terms of Service</a>
                {" "}and{" "}
                <a href="#privacy" className="text-[--primary] hover:underline">Privacy Policy</a>
              </span>
            </label>

            <Button variant="primary" className="w-full" size="lg">
              Create Account
            </Button>
          </form>

          <div className="mt-6 text-center text-sm">
            <span className="text-[--muted-foreground]">Already have an account? </span>
            <a href="#login" className="text-[--primary] font-[--font-weight-medium] hover:underline">
              Sign in
            </a>
          </div>
        </div>

        <p className="mt-6 text-center text-xs text-[--muted-foreground]">
          Your information is protected with end-to-end encryption
        </p>
      </div>
    </div>
  );
}
