import { useEffect, useMemo, useState } from "react";
import { Bell, Calendar, MessageSquare, ShieldAlert, Users } from "lucide-react";
import { useAuth } from "../../../app/use-auth";
import { AppShell } from "../../../components/layout/AppShell";
import { ButtonLink } from "../../../components/ui/Button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle, StatCard } from "../../../components/ui/Card";
import { listAppointments } from "../../appointments/appointmentsApi";
import { getUnreadNotificationCount } from "../../notifications/notificationsApi";
import { listDailyMoodSummaries } from "../../reports/reportsApi";
import type { Appointment } from "../../../types/appointment";
import type { DailyMoodSummary } from "../../../types/report";
import { formatDateTime } from "../../../lib/format";

export function DashboardPage() {
  const { user, token } = useAuth();
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [dailySummaries, setDailySummaries] = useState<DailyMoodSummary[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);

  useEffect(() => {
    if (!token) {
      return;
    }

    void Promise.allSettled([
      listAppointments(token).then(setAppointments),
      listDailyMoodSummaries(token).then(setDailySummaries),
      getUnreadNotificationCount(token).then((payload) => setUnreadCount(payload.unread_count)),
    ]);
  }, [token]);

  const nextAppointment = useMemo(
    () =>
      [...appointments]
        .filter((appointment) => ["requested", "confirmed"].includes(appointment.status))
        .sort((left, right) => left.preferred_datetime.localeCompare(right.preferred_datetime))[0] ?? null,
    [appointments],
  );

  const latestSummary = dailySummaries[0] ?? null;

  return (
    <AppShell
      title={user?.full_name ?? "Dashboard"}
      subtitle="Keep track of upcoming care, recent updates, and your latest mood summary."
      actions={<ButtonLink to="/specialists" variant="secondary">Browse specialists</ButtonLink>}
    >
      <div className="grid gap-6 md:grid-cols-2 xl:grid-cols-4">
        <StatCard
          title="Next appointment"
          value={nextAppointment ? formatDateTime(nextAppointment.preferred_datetime) : "Not scheduled"}
          meta={nextAppointment?.specialist?.full_name ?? "Reserve a specialist slot to populate this card."}
          icon={<Calendar className="size-6" />}
        />
        <StatCard title="Unread notifications" value={String(unreadCount)} meta="Waiting in your inbox" icon={<Bell className="size-6" />} />
        <StatCard
          title="Latest mood summary"
          value={latestSummary?.dominant_mood ?? "Not available"}
          meta={latestSummary ? `Intensity ${latestSummary.average_intensity.toFixed(1)}` : "Chat check-ins and reports will populate this view."}
          icon={<MessageSquare className="size-6" />}
        />
        <StatCard
          title="Current risk state"
          value={latestSummary?.risk ?? "Unknown"}
          meta={latestSummary?.summary_text ?? "Risk guidance appears once mood summaries are available."}
          icon={<ShieldAlert className="size-6" />}
        />
      </div>

      <div className="grid gap-6 xl:grid-cols-[1.5fr_1fr]">
        <Card>
          <CardHeader>
            <CardTitle>What to do next</CardTitle>
            <CardDescription>Pick up where you left off and move to the area you need most.</CardDescription>
          </CardHeader>
          <CardContent className="grid gap-4 pt-4 md:grid-cols-2">
            <ButtonLink to="/chat" className="justify-start rounded-[24px] px-5" size="lg"><MessageSquare className="size-5" /> Open support chat</ButtonLink>
            <ButtonLink to="/specialists" variant="secondary" className="justify-start rounded-[24px] px-5" size="lg"><Users className="size-5" /> Find specialists</ButtonLink>
            <ButtonLink to="/appointments" variant="secondary" className="justify-start rounded-[24px] px-5" size="lg"><Calendar className="size-5" /> Review appointments</ButtonLink>
            <ButtonLink to="/reports" variant="ghost" className="justify-start rounded-[24px] px-5" size="lg"><ShieldAlert className="size-5" /> Review reports</ButtonLink>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Account overview</CardTitle>
            <CardDescription>Your account snapshot for this workspace.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4 text-sm text-[--muted-foreground]">
            <div>
              <p className="text-xs uppercase tracking-[0.16em]">Email</p>
              <p className="mt-1 text-base font-medium text-[--foreground]">{user?.email}</p>
            </div>
            <div>
              <p className="text-xs uppercase tracking-[0.16em]">Role</p>
              <p className="mt-1 text-base font-medium capitalize text-[--foreground]">{user?.role}</p>
            </div>
            <div>
              <p className="text-xs uppercase tracking-[0.16em]">Appointments on record</p>
              <p className="mt-1 text-base font-medium text-[--foreground]">{appointments.length}</p>
            </div>
          </CardContent>
        </Card>
      </div>
    </AppShell>
  );
}
