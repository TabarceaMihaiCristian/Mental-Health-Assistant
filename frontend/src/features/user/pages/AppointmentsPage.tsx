
import { useEffect, useMemo, useState } from "react";
import { Lightbulb, RefreshCcw } from "lucide-react";
import { AppShell } from "../../../components/layout/AppShell";
import { Badge } from "../../../components/ui/Badge";
import { Button } from "../../../components/ui/Button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../../../components/ui/Card";
import { Modal } from "../../../components/ui/Modal";
import { TextField, TextareaField } from "../../../components/ui/Fields";
import { useAuth } from "../../../app/use-auth";
import { cancelAppointment, listAppointments, listCriticalAppointmentSuggestions, rescheduleAppointment } from "../../appointments/appointmentsApi";
import type { Appointment, CriticalAppointmentSuggestions } from "../../../types/appointment";
import { formatDateTime, toTitleCase } from "../../../lib/format";
import { ApiError } from "../../../lib/api";

export function AppointmentsPage() {
  const { token } = useAuth();
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [activeAppointment, setActiveAppointment] = useState<Appointment | null>(null);
  const [mode, setMode] = useState<"cancel" | "reschedule" | null>(null);
  const [reason, setReason] = useState("");
  const [nextDateTime, setNextDateTime] = useState("");
  const [suggestions, setSuggestions] = useState<CriticalAppointmentSuggestions | null>(null);
  const [suggestionsError, setSuggestionsError] = useState<string | null>(null);

  async function reloadAppointments() {
    if (!token) {
      return;
    }
    setLoading(true);
    setError(null);
    try {
      setAppointments(await listAppointments(token));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to load appointments.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    if (!token) {
      return;
    }

    let cancelled = false;

    void (async () => {
      setLoading(true);
      setError(null);
      try {
        const items = await listAppointments(token);
        if (!cancelled) {
          setAppointments(items);
        }
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : "Unable to load appointments.");
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    })();

    return () => {
      cancelled = true;
    };
  }, [token]);

  const grouped = useMemo(() => {
    const mutable = appointments.filter((appointment) => ["requested", "confirmed"].includes(appointment.status));
    const history = appointments.filter((appointment) => !["requested", "confirmed"].includes(appointment.status));
    return { mutable, history };
  }, [appointments]);

  async function submitMutation() {
    if (!token || !activeAppointment || !mode) {
      return;
    }
    try {
      if (mode === "cancel") {
        await cancelAppointment(token, activeAppointment.id, { reason: reason || null });
        setSuccess("Appointment cancelled.");
      } else {
        await rescheduleAppointment(token, activeAppointment.id, {
          preferred_datetime: new Date(nextDateTime).toISOString(),
          note: reason || null,
        });
        setSuccess("Appointment rescheduled.");
      }
      setActiveAppointment(null);
      setMode(null);
      setReason("");
      setNextDateTime("");
      await reloadAppointments();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to update the appointment.");
    }
  }

  async function loadSuggestions() {
    if (!token) {
      return;
    }
    setSuggestionsError(null);
    try {
      setSuggestions(await listCriticalAppointmentSuggestions(token));
    } catch (err) {
      setSuggestions(null);
      setSuggestionsError(err instanceof ApiError ? err.detail : "Unable to load suggestions.");
    }
  }

  return (
    <AppShell
      title="Appointments"
      subtitle="Manage upcoming care, adjust plans when needed, and review past appointments."
      actions={
        <Button variant="secondary" onClick={() => void loadSuggestions()}>
          <Lightbulb className="size-4" />
          Care suggestions
        </Button>
      }
    >
      {error ? <div className="rounded-[28px] border border-[--destructive] bg-[--red-100] px-5 py-4 text-sm">{error}</div> : null}
      {success ? <div className="rounded-[28px] border border-[--teal-200] bg-[--teal-50] px-5 py-4 text-sm">{success}</div> : null}

      <div className="grid gap-6 lg:grid-cols-[1.45fr_1fr]">
        <Card>
          <CardHeader>
            <CardTitle>Upcoming and pending</CardTitle>
            <CardDescription>Requested and confirmed sessions that can still change.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {loading ? <p className="text-sm text-[--muted-foreground]">Loading appointments...</p> : null}
            {!loading && grouped.mutable.length === 0 ? <p className="text-sm text-[--muted-foreground]">No upcoming or pending appointments yet.</p> : null}
            {grouped.mutable.map((appointment) => (
              <div key={appointment.id} className="rounded-[24px] border border-[--border] bg-[--sand-50] p-5">
                <div className="flex flex-wrap items-start justify-between gap-4">
                  <div>
                    <p className="text-lg font-semibold tracking-[-0.02em]">{appointment.specialist?.full_name ?? "Unknown specialist"}</p>
                    <p className="mt-2 text-sm text-[--muted-foreground]">{formatDateTime(appointment.preferred_datetime)}</p>
                    <p className="mt-1 text-sm text-[--muted-foreground]">{toTitleCase(appointment.mode)} · {appointment.specialist?.specialty ?? "Specialist"}</p>
                  </div>
                  <Badge variant={appointment.status === "confirmed" ? "success" : "warning"}>{toTitleCase(appointment.status)}</Badge>
                </div>
                <div className="mt-4 flex flex-wrap gap-3">
                  <Button variant="secondary" size="sm" onClick={() => { setActiveAppointment(appointment); setMode("reschedule"); }}>
                    <RefreshCcw className="size-4" />
                    Reschedule
                  </Button>
                  <Button variant="danger" size="sm" onClick={() => { setActiveAppointment(appointment); setMode("cancel"); }}>
                    Cancel
                  </Button>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>

        <div className="grid gap-6">
          <Card>
            <CardHeader>
              <CardTitle>Completed and closed</CardTitle>
              <CardDescription>Past appointments and closed requests stay here for reference.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {grouped.history.length === 0 ? <p className="text-sm text-[--muted-foreground]">No past appointments yet.</p> : null}
              {grouped.history.map((appointment) => (
                <div key={appointment.id} className="rounded-[20px] border border-[--border] p-4">
                  <p className="font-semibold">{appointment.specialist?.full_name ?? "Unknown specialist"}</p>
                  <p className="mt-1 text-sm text-[--muted-foreground]">{formatDateTime(appointment.preferred_datetime)}</p>
                  <Badge variant="muted" className="mt-3">{toTitleCase(appointment.status)}</Badge>
                </div>
              ))}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Care suggestions</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {suggestions ? (
                <>
                <p className="text-sm text-[--muted-foreground]">Found {suggestions.total_suggestions} time slot suggestion(s) for higher-priority care.</p>
                  {suggestions.suggestions.slice(0, 3).map((item) => (
                    <div key={`${item.specialist_id}-${item.start_datetime}`} className="rounded-[20px] border border-[--border] p-4">
                      <p className="font-semibold">{item.specialist_name}</p>
                      <p className="mt-1 text-sm text-[--muted-foreground]">{item.specialty} · {item.city ?? "City not set"}</p>
                      <p className="mt-1 text-sm text-[--muted-foreground]">{formatDateTime(item.start_datetime)}</p>
                    </div>
                  ))}
                </>
              ) : suggestionsError ? (
                <p className="text-sm text-[--muted-foreground]">{suggestionsError}</p>
              ) : (
                <p className="text-sm text-[--muted-foreground]">Load care suggestions when you need faster support options.</p>
              )}
            </CardContent>
          </Card>
        </div>
      </div>

      <Modal isOpen={Boolean(activeAppointment && mode)} title={mode === "cancel" ? "Cancel appointment" : "Reschedule appointment"} onClose={() => { setActiveAppointment(null); setMode(null); }}>
        <div className="space-y-5">
          {activeAppointment ? (
            <div className="rounded-[20px] bg-[--sand-100] px-4 py-3 text-sm">
              Current appointment: {formatDateTime(activeAppointment.preferred_datetime)}
            </div>
          ) : null}
          {mode === "reschedule" ? (
            <TextField label="New appointment date and time" type="datetime-local" value={nextDateTime} onChange={(event) => setNextDateTime(event.target.value)} required />
          ) : null}
          <TextareaField label={mode === "cancel" ? "Cancellation reason" : "Reschedule note"} value={reason} onChange={(event) => setReason(event.target.value)} />
          <Button onClick={() => void submitMutation()} disabled={mode === "reschedule" && !nextDateTime}>{mode === "cancel" ? "Confirm cancellation" : "Confirm reschedule"}</Button>
        </div>
      </Modal>
    </AppShell>
  );
}
