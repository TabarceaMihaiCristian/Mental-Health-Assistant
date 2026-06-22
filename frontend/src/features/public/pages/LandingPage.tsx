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
          <p className="text-sm uppercase tracking-[0.22em] text-[--muted-foreground]">Mental health support</p>
          <h1 className="mt-4 text-5xl font-semibold tracking-[-0.06em] text-[--foreground] md:text-7xl">
            Mental health support, specialist care, and appointment management in one place.
          </h1>
          <p className="mx-auto mt-6 max-w-3xl text-lg leading-8 text-[--muted-foreground] md:text-xl">
            Talk to a licensed specialist, use guided AI support when needed, manage appointments, and follow your progress from a single platform.
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
          <p className="mx-auto mt-4 max-w-2xl text-[--muted-foreground]">A clear flow from first contact to ongoing specialist support.</p>
        </div>
        <div className="grid gap-6 md:grid-cols-3">
          {[
            { icon: Users, title: "Create your profile", copy: "Create an account and keep your personal information organized in a protected workspace." },
            { icon: MessageSquare, title: "Get support", copy: "Use the chat assistant for guided support and continue with specialist care when needed." },
            { icon: Calendar, title: "Book and manage care", copy: "Find specialists, request appointments, and manage your schedule from one place." },
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
            <p className="mx-auto mt-4 max-w-3xl text-[--muted-foreground]">The platform brings together the main tools needed for follow-up, communication, and appointment coordination.</p>
          </div>
          <div className="grid gap-6 md:grid-cols-2">
            {[
              { icon: MessageSquare, title: "AI chat support", copy: "A guided conversation space that can help you reflect on your state and next steps." },
              { icon: Users, title: "Specialist discovery", copy: "Browse licensed professionals by specialty, city, rating, and consultation mode." },
              { icon: Calendar, title: "Appointment coordination", copy: "Request, reschedule, confirm, and track appointments from a single workspace." },
              { icon: FileText, title: "Reports and summaries", copy: "Review mood summaries and reports in a format that is easy to follow." },
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
            { icon: Shield, title: "Privacy-first handling", copy: "Sensitive data is presented in a calm interface built for healthcare-related use cases." },
            { icon: Lock, title: "Secure access patterns", copy: "Public pages, authenticated routes, and role-based workspaces are clearly separated." },
            { icon: Award, title: "Operational clarity", copy: "Users, specialists, and administrators work in focused areas designed for their daily tasks." },
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
        <h2 className="text-3xl font-semibold tracking-[-0.03em] md:text-4xl">Built for users, specialists, and administrators</h2>
        <p className="mx-auto mt-4 max-w-3xl text-[--teal-100]">
          Each role has a dedicated workspace for the actions that matter most: support, scheduling, oversight, and account management.
        </p>
        <div className="mt-8 flex flex-col items-center gap-3 text-[--teal-100]">
          <div className="flex items-center gap-3"><CheckCircle className="size-5" /> Flexible scheduling</div>
          <div className="flex items-center gap-3"><CheckCircle className="size-5" /> Structured support flows</div>
          <div className="flex items-center gap-3"><CheckCircle className="size-5" /> Clear role-based workspaces</div>
        </div>
      </section>
    </div>
  );
}
