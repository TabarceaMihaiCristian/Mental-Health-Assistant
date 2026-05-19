import { useEffect, useMemo, useState } from "react";
import { Calendar, Shield, UserCog, Users } from "lucide-react";
import { useAuth } from "../../../app/use-auth";
import { AppShell } from "../../../components/layout/AppShell";
import { Badge } from "../../../components/ui/Badge";
import { ButtonLink } from "../../../components/ui/Button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle, StatCard } from "../../../components/ui/Card";
import { formatDateTime, toTitleCase } from "../../../lib/format";
import type { Appointment } from "../../../types/appointment";
import type { AdminSpecialist } from "../../../types/admin";
import { listAdminAppointments, listAdminSpecialists } from "../adminApi";

function badgeVariant(status: string) {
  if (status === "active" || status === "confirmed" || status === "completed") return "success";
  if (status === "inactive" || status === "cancelled" || status === "rejected") return "danger";
  return "warning";
}

export function AdminDashboardPage() {
  const { token } = useAuth();
  const [specialists, setSpecialists] = useState<AdminSpecialist[]>([]);
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!token) {
      return;
    }

    void Promise.all([
      listAdminSpecialists(token).then((payload) => setSpecialists(payload.items)),
      listAdminAppointments(token).then((payload) => setAppointments(payload.items)),
    ]).catch((err: Error) => setError(err.message));
  }, [token]);

  const activeSpecialists = specialists.filter((item) => item.status === "active");
  const inactiveSpecialists = specialists.filter((item) => item.status === "inactive");
  const pendingAppointments = appointments.filter((item) => item.status === "requested");
  const recentSpecialists = [...specialists].slice(0, 4);
  const recentAppointments = useMemo(
    () =>
      [...appointments]
        .sort((left, right) => right.preferred_datetime.localeCompare(left.preferred_datetime))
        .slice(0, 4),
    [appointments],
  );

  return (
    <AppShell
      role="admin"
      title="Admin dashboard"
      subtitle="Operational oversight for specialists and appointment activity across the platform."
      actions={<ButtonLink to="/admin/specialists" variant="secondary">Manage specialists</ButtonLink>}
    >
      {error ? <div className="rounded-[28px] border border-[--destructive] bg-[--red-100] px-5 py-4 text-sm">{error}</div> : null}
      <div className="grid gap-6 md:grid-cols-2 xl:grid-cols-4">
        <StatCard title="Specialists" value={String(specialists.length)} meta="All specialist records" icon={<Users className="size-6" />} />
        <StatCard title="Active specialists" value={String(activeSpecialists.length)} meta="Visible in the public directory" icon={<Shield className="size-6" />} />
        <StatCard title="Inactive specialists" value={String(inactiveSpecialists.length)} meta="Hidden from public booking" icon={<UserCog className="size-6" />} />
        <StatCard title="Pending appointments" value={String(pendingAppointments.length)} meta="Requests waiting on action" icon={<Calendar className="size-6" />} />
      </div>

      <div className="grid gap-6 xl:grid-cols-[1.1fr_1.1fr]">
        <Card>
          <CardHeader>
            <CardTitle>Recent specialist records</CardTitle>
            <CardDescription>Quick visibility into current specialist directory entries.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {recentSpecialists.length === 0 ? <p className="text-sm text-[--muted-foreground]">No specialists available.</p> : null}
            {recentSpecialists.map((specialist) => (
              <div key={specialist.id} className="flex flex-wrap items-start justify-between gap-4 rounded-[22px] border border-[--border] bg-[--sand-50] p-4">
                <div>
                  <p className="font-semibold tracking-[-0.02em]">{specialist.full_name}</p>
                  <p className="mt-1 text-sm text-[--muted-foreground]">{specialist.specialty}</p>
                  <p className="mt-1 text-sm text-[--muted-foreground]">{specialist.city ?? "City not set"} · {specialist.email ?? "No email"}</p>
                </div>
                <Badge variant={badgeVariant(specialist.status)}>{toTitleCase(specialist.status)}</Badge>
              </div>
            ))}
            <ButtonLink to="/admin/specialists" variant="ghost">Open specialist management</ButtonLink>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Recent appointments</CardTitle>
            <CardDescription>Latest appointment records visible to admins.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {recentAppointments.length === 0 ? <p className="text-sm text-[--muted-foreground]">No appointments available.</p> : null}
            {recentAppointments.map((appointment) => (
              <div key={appointment.id} className="flex flex-wrap items-start justify-between gap-4 rounded-[22px] border border-[--border] p-4">
                <div>
                  <p className="font-semibold tracking-[-0.02em]">{appointment.user?.full_name ?? "Unknown user"}</p>
                  <p className="mt-1 text-sm text-[--muted-foreground]">{appointment.specialist?.full_name ?? "Unknown specialist"}</p>
                  <p className="mt-1 text-sm text-[--muted-foreground]">{formatDateTime(appointment.preferred_datetime)}</p>
                </div>
                <Badge variant={badgeVariant(appointment.status)}>{toTitleCase(appointment.status)}</Badge>
              </div>
            ))}
            <ButtonLink to="/admin/appointments" variant="ghost">Open appointment oversight</ButtonLink>
          </CardContent>
        </Card>
      </div>
    </AppShell>
  );
}
