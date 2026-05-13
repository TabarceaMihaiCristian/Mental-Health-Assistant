import { useEffect, useMemo, useState } from "react";
import { Calendar, Clock, TrendingUp, Users } from "lucide-react";
import { AppShell } from "../../../components/layout/AppShell";
import { Badge } from "../../../components/ui/Badge";
import { ButtonLink } from "../../../components/ui/Button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle, StatCard } from "../../../components/ui/Card";
import { useAuth } from "../../../app/use-auth";
import { listSpecialistAppointments } from "../specialistApi";
import type { Appointment } from "../../../types/appointment";
import { formatDateTime, toTitleCase } from "../../../lib/format";

export function SpecialistDashboardPage() {
  const { token } = useAuth();
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!token) return;
    listSpecialistAppointments(token)
      .then(setAppointments)
      .catch((err: Error) => setError(err.message));
  }, [token]);

  const todayAppointments = useMemo(
    () =>
      appointments
        .filter((appointment) => {
          const day = new Date(appointment.preferred_datetime).toDateString();
          return day === new Date().toDateString();
        })
        .sort((left, right) => left.preferred_datetime.localeCompare(right.preferred_datetime)),
    [appointments],
  );
  const pendingRequests = appointments.filter((appointment) => appointment.status === "requested");
  const confirmedAppointments = appointments.filter((appointment) => appointment.status === "confirmed");

  return (
    <AppShell role="specialist" title="Specialist dashboard" subtitle="This workspace is now connected to the specialist appointment API.">
      {error ? <div className="rounded-[28px] border border-[--destructive] bg-[--red-100] px-5 py-4 text-sm">{error}</div> : null}
      <div className="grid gap-6 md:grid-cols-2 xl:grid-cols-4">
        <StatCard title="Today’s appointments" value={String(todayAppointments.length)} meta="Live backend count" icon={<Calendar className="size-6" />} />
        <StatCard title="Pending requests" value={String(pendingRequests.length)} meta="Requires specialist action" icon={<Clock className="size-6" />} />
        <StatCard title="Confirmed appointments" value={String(confirmedAppointments.length)} meta="Upcoming care sessions" icon={<Users className="size-6" />} />
        <StatCard title="Total records" value={String(appointments.length)} meta="Current specialist workload" icon={<TrendingUp className="size-6" />} />
      </div>

      <div className="grid gap-6 xl:grid-cols-[1.4fr_1fr]">
        <Card>
          <CardHeader>
            <CardTitle>Today’s schedule</CardTitle>
            <CardDescription>Appointments assigned to the current specialist.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {todayAppointments.length === 0 ? <p className="text-sm text-[--muted-foreground]">No appointments scheduled for today.</p> : null}
            {todayAppointments.map((appointment) => (
              <div key={appointment.id} className="flex flex-wrap items-center justify-between gap-4 rounded-[24px] border border-[--border] bg-[--sand-50] p-5">
                <div>
                  <p className="text-lg font-semibold tracking-[-0.02em]">{appointment.user?.full_name ?? "Unknown patient"}</p>
                  <p className="mt-2 text-sm text-[--muted-foreground]">{formatDateTime(appointment.preferred_datetime)}</p>
                  <p className="mt-1 text-sm text-[--muted-foreground]">{toTitleCase(appointment.mode)} session</p>
                </div>
                <Badge variant={appointment.status === "confirmed" ? "success" : "warning"}>{toTitleCase(appointment.status)}</Badge>
              </div>
            ))}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Pending requests</CardTitle>
            <CardDescription>Jump to the management route to confirm, reject, or reschedule.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {pendingRequests.slice(0, 4).map((request) => (
              <div key={request.id} className="rounded-[20px] border border-[--border] p-4">
                <p className="font-semibold">{request.user?.full_name ?? "Unknown patient"}</p>
                <p className="mt-1 text-sm text-[--muted-foreground]">{formatDateTime(request.preferred_datetime)}</p>
              </div>
            ))}
            <ButtonLink to="/specialist/appointments" variant="secondary">Manage specialist appointments</ButtonLink>
          </CardContent>
        </Card>
      </div>
    </AppShell>
  );
}
