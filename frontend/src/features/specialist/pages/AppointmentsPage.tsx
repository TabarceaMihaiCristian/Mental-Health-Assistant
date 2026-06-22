import { useEffect, useState } from "react";
import { AppShell } from "../../../components/layout/AppShell";
import { Badge } from "../../../components/ui/Badge";
import { Button } from "../../../components/ui/Button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../../../components/ui/Card";
import { Modal } from "../../../components/ui/Modal";
import { TextField, TextareaField } from "../../../components/ui/Fields";
import { useAuth } from "../../../app/use-auth";
import { completeSpecialistAppointment, confirmSpecialistAppointment, listSpecialistAppointments, rejectSpecialistAppointment, rescheduleSpecialistAppointment } from "../specialistApi";
import type { Appointment } from "../../../types/appointment";
import { formatDateTime, toTitleCase } from "../../../lib/format";

export function SpecialistAppointmentsPage() {
  const { token } = useAuth();
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [active, setActive] = useState<Appointment | null>(null);
  const [mode, setMode] = useState<"reject" | "reschedule" | null>(null);
  const [reason, setReason] = useState("");
  const [dateTime, setDateTime] = useState("");

  async function loadAppointments() {
    if (!token) return;
    try {
      setAppointments(await listSpecialistAppointments(token));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to load specialist appointments.");
    }
  }

  useEffect(() => {
    if (!token) {
      return;
    }

    let cancelled = false;

    void (async () => {
      try {
        const items = await listSpecialistAppointments(token);
        if (!cancelled) {
          setAppointments(items);
        }
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : "Unable to load specialist appointments.");
        }
      }
    })();

    return () => {
      cancelled = true;
    };
  }, [token]);

  async function mutate(action: "confirm" | "complete" | "reject" | "reschedule", appointment: Appointment) {
    if (!token) return;
    try {
      if (action === "confirm") await confirmSpecialistAppointment(token, appointment.id);
      if (action === "complete") await completeSpecialistAppointment(token, appointment.id);
      if (action === "reject") await rejectSpecialistAppointment(token, appointment.id, { reason: reason || null });
      if (action === "reschedule") await rescheduleSpecialistAppointment(token, appointment.id, { preferred_datetime: new Date(dateTime).toISOString(), note: reason || null });
      setActive(null);
      setMode(null);
      setReason("");
      setDateTime("");
      await loadAppointments();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to update the appointment.");
    }
  }

  return (
    <AppShell role="specialist" title="Specialist appointments" subtitle="Review requests, confirm care, and manage schedule changes from one place.">
      {error ? <div className="rounded-[28px] border border-[--destructive] bg-[--red-100] px-5 py-4 text-sm">{error}</div> : null}
      <Card>
        <CardHeader>
          <CardTitle>Assigned appointments</CardTitle>
          <CardDescription>Confirm, reject, reschedule, or complete appointments from this view.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {appointments.length === 0 ? <p className="text-sm text-[--muted-foreground]">No appointments assigned yet.</p> : null}
          {appointments.map((appointment) => (
            <div key={appointment.id} className="rounded-[24px] border border-[--border] p-5">
              <div className="flex flex-wrap items-start justify-between gap-4">
                <div>
                  <p className="text-lg font-semibold tracking-[-0.02em]">{appointment.user?.full_name ?? "Unknown patient"}</p>
                  <p className="mt-2 text-sm text-[--muted-foreground]">{formatDateTime(appointment.preferred_datetime)}</p>
                  <p className="mt-1 text-sm text-[--muted-foreground]">{toTitleCase(appointment.mode)} - {appointment.notes ?? "No notes"}</p>
                </div>
                <Badge variant={appointment.status === "confirmed" ? "success" : appointment.status === "requested" ? "warning" : "muted"}>{toTitleCase(appointment.status)}</Badge>
              </div>
              <div className="mt-4 flex flex-wrap gap-3">
                {appointment.status === "requested" ? <Button variant="secondary" size="sm" onClick={() => void mutate("confirm", appointment)}>Confirm</Button> : null}
                {appointment.status === "requested" ? <Button variant="ghost" size="sm" onClick={() => { setActive(appointment); setMode("reject"); }}>Reject</Button> : null}
                {["requested", "confirmed"].includes(appointment.status) ? <Button variant="secondary" size="sm" onClick={() => { setActive(appointment); setMode("reschedule"); }}>Reschedule</Button> : null}
                {appointment.status === "confirmed" ? <Button variant="success" size="sm" onClick={() => void mutate("complete", appointment)}>Complete</Button> : null}
              </div>
            </div>
          ))}
        </CardContent>
      </Card>

      <Modal isOpen={Boolean(active && mode)} title={mode === "reject" ? "Reject appointment" : "Reschedule appointment"} onClose={() => { setActive(null); setMode(null); }}>
        <div className="space-y-5">
          {mode === "reschedule" ? <TextField label="New date and time" type="datetime-local" value={dateTime} onChange={(event) => setDateTime(event.target.value)} required /> : null}
          <TextareaField label={mode === "reject" ? "Reason" : "Reschedule note"} value={reason} onChange={(event) => setReason(event.target.value)} />
          {active && mode ? <Button onClick={() => void mutate(mode, active)}>{mode === "reject" ? "Confirm rejection" : "Confirm reschedule"}</Button> : null}
        </div>
      </Modal>
    </AppShell>
  );
}
