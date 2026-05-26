import { Award, Calendar, CheckCircle, FileText, Lock, MessageSquare, Shield, Users } from "lucide-react";
import { PublicHeader } from "../../../components/layout/PublicHeader";
import { ButtonLink } from "../../../components/ui/Button";
import { Card, CardHeader, CardTitle, CardContent } from "../../../components/ui/Card";

export function LandingPage() {
  return (
    <div className="min-h-screen">
      <PublicHeader />

      <section className="mx-auto max-w-7xl px-6 py-24 md:py-32">
        <div className="mx-auto max-w-4xl text-center">
          <p className="text-sm uppercase tracking-[0.22em] text-[--muted-foreground]">Calm care coordination</p>
          <h1 className="mt-4 text-5xl font-semibold tracking-[-0.06em] text-[--foreground] md:text-7xl">
            Your path to better mental wellness starts with one coherent workspace.
          </h1>
          <p className="mx-auto mt-6 max-w-3xl text-lg leading-8 text-[--muted-foreground] md:text-xl">
            Connect with licensed specialists, use AI-assisted support responsibly, manage appointments, and follow your mental health journey in one secure platform.
          </p>
          <div className="mt-10 flex flex-wrap items-center justify-center gap-4">
            <ButtonLink to="/register" size="lg">Start your journey</ButtonLink>
            <ButtonLink to="/login" variant="secondary" size="lg">Sign in</ButtonLink>
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-7xl px-6 py-12 md:py-20">
        <div className="mb-12 text-center">
          <h2 className="text-3xl font-semibold tracking-[-0.03em] md:text-4xl">How it works</h2>
          <p className="mx-auto mt-4 max-w-2xl text-[--muted-foreground]">A direct, private flow from immediate support to specialist care.</p>
        </div>
        <div className="grid gap-6 md:grid-cols-3">
          {[
            { icon: Users, title: "Create your profile", copy: "Set up your account and keep your private information in a secure healthcare-oriented environment." },
            { icon: MessageSquare, title: "Get support", copy: "Use the AI assistant for structured support, then escalate into professional care when needed." },
            { icon: Calendar, title: "Book and manage care", copy: "Find specialists, reserve time slots, and manage your appointments with minimal friction." },
          ].map((item) => (
            <Card key={item.title} className="h-full">
              <CardContent className="p-8 text-center">
                <div className="mx-auto mb-5 flex size-16 items-center justify-center rounded-full bg-[--primary-light] text-[--primary]">
                  <item.icon className="size-8" />
                </div>
                <h3 className="text-xl font-semibold tracking-[-0.02em]">{item.title}</h3>
                <p className="mt-4 text-[--muted-foreground]">{item.copy}</p>
              </CardContent>
            </Card>
          ))}
        </div>
      </section>

      <section className="bg-white/80 py-16 md:py-24">
        <div className="mx-auto max-w-7xl px-6">
          <div className="mb-12 text-center">
            <h2 className="text-3xl font-semibold tracking-[-0.03em] md:text-4xl">Comprehensive mental health support</h2>
            <p className="mx-auto mt-4 max-w-3xl text-[--muted-foreground]">Everything is organized around the core moments that matter most in care and follow-through.</p>
          </div>
          <div className="grid gap-6 md:grid-cols-2">
            {[
              { icon: MessageSquare, title: "AI chat support", copy: "A calm conversation space with clear next steps when deeper care may be helpful." },
              { icon: Users, title: "Specialist discovery", copy: "Browse licensed professionals by specialty, city, rating, and consultation mode." },
              { icon: Calendar, title: "Appointment coordination", copy: "Book, reschedule, confirm, and track care interactions from one place." },
              { icon: FileText, title: "Reports and summaries", copy: "Review mood summaries and support data with a clear, non-technical presentation." },
            ].map((item) => (
              <Card key={item.title}>
                <CardHeader>
                  <div className="flex items-start gap-4">
                    <div className="flex size-12 items-center justify-center rounded-2xl bg-[--primary-light] text-[--primary]">
                      <item.icon className="size-6" />
                    </div>
                    <div>
                      <CardTitle>{item.title}</CardTitle>
                      <p className="mt-2 text-sm text-[--muted-foreground]">{item.copy}</p>
                    </div>
                  </div>
                </CardHeader>
              </Card>
            ))}
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-7xl px-6 py-16 md:py-24">
        <div className="grid gap-6 md:grid-cols-3">
          {[
            { icon: Shield, title: "Privacy-first handling", copy: "A healthcare-oriented design that avoids noisy or playful treatment of sensitive information." },
            { icon: Lock, title: "Secure access patterns", copy: "Authenticated routes, role-aware workspaces, and a clear separation of public and private flows." },
            { icon: Award, title: "Operational clarity", copy: "A UI system that works for both end users and professionals without diverging into separate design languages." },
          ].map((item) => (
            <div key={item.title} className="flex gap-4 rounded-[28px] border border-[--border] bg-white p-6 shadow-[var(--shadow-sm)]">
              <item.icon className="mt-1 size-6 shrink-0 text-[--primary]" />
              <div>
                <h3 className="font-semibold tracking-[-0.02em]">{item.title}</h3>
                <p className="mt-2 text-sm text-[--muted-foreground]">{item.copy}</p>
              </div>
            </div>
          ))}
        </div>
      </section>

      <section className="mx-auto max-w-7xl rounded-[40px] bg-gradient-to-br from-[--teal-700] to-[--teal-900] px-6 py-16 text-center text-white md:px-10 md:py-20">
        <h2 className="text-3xl font-semibold tracking-[-0.03em] md:text-4xl">Built for users and specialists</h2>
        <p className="mx-auto mt-4 max-w-3xl text-[--teal-100]">
          Specialists also have a focused workspace for daily overview, appointment requests, scheduling, and practice management.
        </p>
        <div className="mt-8 flex flex-col items-center gap-3 text-[--teal-100]">
          <div className="flex items-center gap-3"><CheckCircle className="size-5" /> Flexible scheduling</div>
          <div className="flex items-center gap-3"><CheckCircle className="size-5" /> Secure communication</div>
          <div className="flex items-center gap-3"><CheckCircle className="size-5" /> Operational dashboard patterns</div>
        </div>
      </section>
    </div>
  );
}
