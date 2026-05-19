import { useEffect, useMemo, useState } from "react";
import { Filter, RefreshCw } from "lucide-react";
import { useAuth } from "../../../app/use-auth";
import { AppShell } from "../../../components/layout/AppShell";
import { Badge } from "../../../components/ui/Badge";
import { Button } from "../../../components/ui/Button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle, StatCard } from "../../../components/ui/Card";
import { SelectField, TextField } from "../../../components/ui/Fields";
import { formatDateTime, toTitleCase } from "../../../lib/format";
import type { Appointment, AppointmentStatus } from "../../../types/appointment";
import { listAdminAppointments } from "../adminApi";

function badgeVariant(status: string) {
  if (status === "confirmed" || status === "completed") return "success";
  if (status === "rejected" || status === "cancelled") return "danger";
  return "warning";
}

export function AdminAppointmentsPage() {
  const { token } = useAuth();
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [status, setStatus] = useState<AppointmentStatus | "">("");
  const [dateFrom, setDateFrom] = useState("");
  const [dateTo, setDateTo] = useState("");
  const [appliedFilters, setAppliedFilters] = useState({ status: "" as AppointmentStatus | "", date_from: "", date_to: "" });

  async function loadAppointments() {
    if (!token) {
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const payload = await listAdminAppointments(token, {
        status: appliedFilters.status,
        date_from: appliedFilters.date_from,
        date_to: appliedFilters.date_to,
      });
      setAppointments(payload.items);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to load admin appointments.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    if (!token) {
      return;
    }

    void listAdminAppointments(token, {
      status: appliedFilters.status,
      date_from: appliedFilters.date_from,
      date_to: appliedFilters.date_to,
    })
      .then((payload) => setAppointments(payload.items))
      .catch((err: Error) => setError(err.message))
      .finally(() => setLoading(false));
  }, [token, appliedFilters]);

  const pendingCount = appointments.filter((item) => item.status === "requested").length;
  const confirmedCount = appointments.filter((item) => item.status === "confirmed").length;
  const completedCount = appointments.filter((item) => item.status === "completed").length;
  const orderedAppointments = useMemo(
    () => [...appointments].sort((left, right) => right.preferred_datetime.localeCompare(left.preferred_datetime)),
    [appointments],
  );

  return (
    <AppShell
      role="admin"
      title="Appointment oversight"
      subtitle="Cross-platform view of all appointment records with lightweight operational filtering."
      actions={<Button variant="ghost" onClick={() => void loadAppointments()}><RefreshCw className="size-4" /> Refresh</Button>}
    >
      {error ? <div className="rounded-[28px] border border-[--destructive] bg-[--red-100] px-5 py-4 text-sm">{error}</div> : null}
      <div className="grid gap-6 md:grid-cols-2 xl:grid-cols-4">
        <StatCard title="Total appointments" value={String(appointments.length)} meta="Current result set" icon={<Filter className="size-6" />} />
        <StatCard title="Requested" value={String(pendingCount)} meta="Waiting on specialist action" />
        <StatCard title="Confirmed" value={String(confirmedCount)} meta="Upcoming scheduled sessions" />
        <StatCard title="Completed" value={String(completedCount)} meta="Closed care sessions" />
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Filters</CardTitle>
          <CardDescription>Filter the admin appointment oversight list by state and date window.</CardDescription>
        </CardHeader>
        <CardContent className="grid gap-4 md:grid-cols-4">
          <SelectField label="Status" value={status} onChange={(event) => setStatus(event.target.value as AppointmentStatus | "") }>
            <option value="">All statuses</option>
            <option value="requested">Requested</option>
            <option value="confirmed">Confirmed</option>
            <option value="rejected">Rejected</option>
            <option value="cancelled">Cancelled</option>
            <option value="completed">Completed</option>
          </SelectField>
          <TextField label="Date from" type="date" value={dateFrom} onChange={(event) => setDateFrom(event.target.value)} />
          <TextField label="Date to" type="date" value={dateTo} onChange={(event) => setDateTo(event.target.value)} />
          <div className="flex items-end gap-3">
            <Button style={{ backgroundColor: "var(--primary)", color: "#ffffff" }} className="hover:brightness-95" onClick={() => { setLoading(true); setError(null); setAppliedFilters({ status, date_from: dateFrom, date_to: dateTo }); }}>Apply</Button>
            <Button
              variant="secondary"
              onClick={() => {
                setStatus("");
                setDateFrom("");
                setDateTo("");
                setLoading(true);
                setError(null);
                setAppliedFilters({ status: "", date_from: "", date_to: "" });
              }}
            >
              Reset
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Appointment records</CardTitle>
          <CardDescription>{loading ? "Loading appointment records..." : `${appointments.length} appointments in the current result set.`}</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {!loading && orderedAppointments.length === 0 ? <p className="text-sm text-[--muted-foreground]">No appointments matched the current filters.</p> : null}
          {orderedAppointments.map((appointment) => (
            <div key={appointment.id} className="rounded-[22px] border border-[--border] bg-[--sand-50] p-5">
              <div className="flex flex-wrap items-start justify-between gap-4">
                <div>
                  <p className="font-semibold tracking-[-0.02em]">{appointment.user?.full_name ?? "Unknown user"}</p>
                  <p className="mt-1 text-sm text-[--muted-foreground]">{appointment.user?.email ?? "No user email"}</p>
                  <p className="mt-2 text-sm text-[--muted-foreground]">Specialist: {appointment.specialist?.full_name ?? "Unknown specialist"}</p>
                  <p className="mt-1 text-sm text-[--muted-foreground]">{appointment.specialist?.specialty ?? "No specialty"} · {appointment.specialist?.city ?? "No city"}</p>
                </div>
                <div className="text-right">
                  <Badge variant={badgeVariant(appointment.status)}>{toTitleCase(appointment.status)}</Badge>
                  <p className="mt-2 text-sm text-[--muted-foreground]">{toTitleCase(appointment.mode)} session</p>
                  <p className="mt-1 text-sm text-[--muted-foreground]">{formatDateTime(appointment.preferred_datetime)}</p>
                </div>
              </div>
              {appointment.notes ? <p className="mt-4 text-sm text-[--foreground]">Notes: {appointment.notes}</p> : null}
              {appointment.rejection_reason ? <p className="mt-2 text-sm text-[--muted-foreground]">Rejection reason: {appointment.rejection_reason}</p> : null}
              {appointment.cancellation_reason ? <p className="mt-2 text-sm text-[--muted-foreground]">Cancellation reason: {appointment.cancellation_reason}</p> : null}
              {appointment.reschedule_note ? <p className="mt-2 text-sm text-[--muted-foreground]">Reschedule note: {appointment.reschedule_note}</p> : null}
            </div>
          ))}
        </CardContent>
      </Card>
    </AppShell>
  );
}
