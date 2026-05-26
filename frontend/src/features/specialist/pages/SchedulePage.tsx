import { useEffect, useMemo, useState } from "react";
import { CalendarDays } from "lucide-react";
import { AppShell } from "../../../components/layout/AppShell";
import { Button } from "../../../components/ui/Button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../../../components/ui/Card";
import { SelectField, TextField } from "../../../components/ui/Fields";
import { useAuth } from "../../../app/use-auth";
import { createBreak, createTimeOff, deleteBreak, deleteTimeOff, getSpecialistCalendar, listAvailabilityRules, listBreaks, listTimeOff, replaceAvailabilityRules } from "../specialistApi";
import type { AvailabilityRule, SpecialistBreak, SpecialistTimeOff } from "../../../types/specialist";
import { formatDateTime, formatTimeOnly, nextDateString } from "../../../lib/format";

const weekdays = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];

export function SpecialistSchedulePage() {
  const { token } = useAuth();
  const [rules, setRules] = useState<AvailabilityRule[]>([]);
  const [breaks, setBreaks] = useState<SpecialistBreak[]>([]);
  const [timeOff, setTimeOff] = useState<SpecialistTimeOff[]>([]);
  const [calendarDateFrom, setCalendarDateFrom] = useState(nextDateString(0));
  const [calendarDateTo, setCalendarDateTo] = useState(nextDateString(7));
  const [calendarSummary, setCalendarSummary] = useState<{ appointments: number; slots: number } | null>(null);
  const [error, setError] = useState<string | null>(null);

  const [newRuleWeekday, setNewRuleWeekday] = useState("0");
  const [newRuleStart, setNewRuleStart] = useState("09:00");
  const [newRuleEnd, setNewRuleEnd] = useState("17:00");

  const [newBreakWeekday, setNewBreakWeekday] = useState("0");
  const [newBreakStart, setNewBreakStart] = useState("12:00");
  const [newBreakEnd, setNewBreakEnd] = useState("13:00");
  const [newBreakLabel, setNewBreakLabel] = useState("Lunch");

  const [newTimeOffStart, setNewTimeOffStart] = useState("");
  const [newTimeOffEnd, setNewTimeOffEnd] = useState("");
  const [newTimeOffReason, setNewTimeOffReason] = useState("");

  async function loadSchedule() {
    if (!token) return;
    try {
      const [availabilityRules, currentBreaks, currentTimeOff, calendar] = await Promise.all([
        listAvailabilityRules(token),
        listBreaks(token),
        listTimeOff(token),
        getSpecialistCalendar(token, calendarDateFrom, calendarDateTo),
      ]);
      setRules(availabilityRules);
      setBreaks(currentBreaks);
      setTimeOff(currentTimeOff);
      setCalendarSummary({ appointments: calendar.appointments.length, slots: calendar.available_slots.length });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to load schedule data.");
    }
  }

  useEffect(() => {
    if (!token) {
      return;
    }

    let cancelled = false;

    void (async () => {
      try {
        const [availabilityRules, currentBreaks, currentTimeOff, calendar] = await Promise.all([
          listAvailabilityRules(token),
          listBreaks(token),
          listTimeOff(token),
          getSpecialistCalendar(token, calendarDateFrom, calendarDateTo),
        ]);

        if (cancelled) {
          return;
        }

        setRules(availabilityRules);
        setBreaks(currentBreaks);
        setTimeOff(currentTimeOff);
        setCalendarSummary({ appointments: calendar.appointments.length, slots: calendar.available_slots.length });
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : "Unable to load schedule data.");
        }
      }
    })();

    return () => {
      cancelled = true;
    };
  }, [calendarDateFrom, calendarDateTo, token]);

  const groupedRules = useMemo(() => [...rules].sort((a, b) => a.weekday - b.weekday), [rules]);

  async function addAvailabilityRule() {
    if (!token) return;
    const payload = [...rules, { weekday: Number(newRuleWeekday), start_time: newRuleStart, end_time: newRuleEnd, is_enabled: true }].map(({ weekday, start_time, end_time, is_enabled }) => ({
      weekday, start_time, end_time, is_enabled,
    }));
    await replaceAvailabilityRules(token, payload);
    await loadSchedule();
  }

  return (
    <AppShell role="specialist" title="Specialist schedule" subtitle="Shape your weekly availability, protect personal time, and review open capacity.">
      {error ? <div className="rounded-[28px] border border-[--destructive] bg-[--red-100] px-5 py-4 text-sm">{error}</div> : null}
      <div className="grid gap-6 xl:grid-cols-[1.2fr_1fr_1fr]">
        <Card>
          <CardHeader>
            <CardTitle>Availability rules</CardTitle>
            <CardDescription>Replaceable weekly recurring availability.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {groupedRules.map((rule) => (
              <div key={rule.id} className="rounded-[20px] border border-[--border] p-4">
                <p className="font-semibold">{weekdays[rule.weekday]}</p>
                <p className="mt-1 text-sm text-[--muted-foreground]">{formatTimeOnly(rule.start_time)} - {formatTimeOnly(rule.end_time)}</p>
              </div>
            ))}
            <div className="grid gap-3 rounded-[24px] bg-[--sand-50] p-4">
              <SelectField label="Weekday" value={newRuleWeekday} onChange={(event) => setNewRuleWeekday(event.target.value)}>
                {weekdays.map((day, index) => <option key={day} value={String(index)}>{day}</option>)}
              </SelectField>
              <TextField label="Start" type="time" value={newRuleStart} onChange={(event) => setNewRuleStart(event.target.value)} />
              <TextField label="End" type="time" value={newRuleEnd} onChange={(event) => setNewRuleEnd(event.target.value)} />
              <Button onClick={() => void addAvailabilityRule()}>Add availability rule</Button>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Breaks and time off</CardTitle>
          <CardDescription>Block short breaks and longer time away from the calendar.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="rounded-[24px] bg-[--sand-50] p-4">
              <SelectField label="Break weekday" value={newBreakWeekday} onChange={(event) => setNewBreakWeekday(event.target.value)}>
                {weekdays.map((day, index) => <option key={day} value={String(index)}>{day}</option>)}
              </SelectField>
              <TextField label="Break start" type="time" value={newBreakStart} onChange={(event) => setNewBreakStart(event.target.value)} />
              <TextField label="Break end" type="time" value={newBreakEnd} onChange={(event) => setNewBreakEnd(event.target.value)} />
              <TextField label="Label" type="text" value={newBreakLabel} onChange={(event) => setNewBreakLabel(event.target.value)} />
              <Button className="mt-3" onClick={() => token && createBreak(token, { weekday: Number(newBreakWeekday), start_time: newBreakStart, end_time: newBreakEnd, label: newBreakLabel }).then(() => loadSchedule())}>Create break</Button>
            </div>
            {breaks.map((item) => (
              <div key={item.id} className="rounded-[20px] border border-[--border] p-4">
                <p className="font-semibold">{weekdays[item.weekday]} · {item.label ?? "Break"}</p>
                <p className="mt-1 text-sm text-[--muted-foreground]">{formatTimeOnly(item.start_time)} - {formatTimeOnly(item.end_time)}</p>
                <Button variant="ghost" size="sm" className="mt-3" onClick={() => token && deleteBreak(token, item.id).then(() => loadSchedule())}>Delete</Button>
              </div>
            ))}
            <div className="rounded-[24px] bg-[--sand-50] p-4">
              <TextField label="Time-off start" type="datetime-local" value={newTimeOffStart} onChange={(event) => setNewTimeOffStart(event.target.value)} />
              <TextField label="Time-off end" type="datetime-local" value={newTimeOffEnd} onChange={(event) => setNewTimeOffEnd(event.target.value)} />
              <TextField label="Reason" type="text" value={newTimeOffReason} onChange={(event) => setNewTimeOffReason(event.target.value)} />
              <Button className="mt-3" onClick={() => token && createTimeOff(token, { start_datetime: new Date(newTimeOffStart).toISOString(), end_datetime: new Date(newTimeOffEnd).toISOString(), reason: newTimeOffReason || null }).then(() => loadSchedule())}>Create time off</Button>
            </div>
            {timeOff.map((item) => (
              <div key={item.id} className="rounded-[20px] border border-[--border] p-4">
                <p className="font-semibold">{item.reason ?? "Time off"}</p>
                <p className="mt-1 text-sm text-[--muted-foreground]">{formatDateTime(item.start_datetime)} - {formatDateTime(item.end_datetime)}</p>
                <Button variant="ghost" size="sm" className="mt-3" onClick={() => token && deleteTimeOff(token, item.id).then(() => loadSchedule())}>Delete</Button>
              </div>
            ))}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Calendar summary</CardTitle>
          <CardDescription>Quick view of appointments and open slots in the selected window.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <TextField label="From" type="date" value={calendarDateFrom} onChange={(event) => setCalendarDateFrom(event.target.value)} />
            <TextField label="To" type="date" value={calendarDateTo} onChange={(event) => setCalendarDateTo(event.target.value)} />
            <div className="rounded-[24px] bg-[--teal-50] p-4 text-sm text-[--foreground]">
              <div className="flex items-center gap-2"><CalendarDays className="size-4 text-[--primary]" /> Appointments: {calendarSummary?.appointments ?? 0}</div>
              <p className="mt-2">Available slots: {calendarSummary?.slots ?? 0}</p>
            </div>
          </CardContent>
        </Card>
      </div>
    </AppShell>
  );
}
