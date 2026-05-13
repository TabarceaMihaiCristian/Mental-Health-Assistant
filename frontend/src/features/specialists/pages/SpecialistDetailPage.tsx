
import { useEffect, useMemo, useState } from "react";
import { useParams } from "react-router-dom";
import { Calendar, MapPin, Star, Video } from "lucide-react";
import { useAuth } from "../../../app/use-auth";
import { AppShell } from "../../../components/layout/AppShell";
import { Badge } from "../../../components/ui/Badge";
import { Button, ButtonLink } from "../../../components/ui/Button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../../../components/ui/Card";
import { SelectField, TextareaField } from "../../../components/ui/Fields";
import { getSpecialist, getSpecialistAvailability, createSpecialistReview, updateMySpecialistReview } from "../specialistsApi";
import { createAppointment } from "../../appointments/appointmentsApi";
import type { Specialist, SpecialistAvailabilitySlot } from "../../../types/specialist";
import { formatDateTime, nextDateString, toTitleCase } from "../../../lib/format";
import { ApiError } from "../../../lib/api";

export function SpecialistDetailPage() {
  const { specialistId } = useParams();
  const { token } = useAuth();
  const [specialist, setSpecialist] = useState<Specialist | null>(null);
  const [slots, setSlots] = useState<SpecialistAvailabilitySlot[]>([]);
  const [dateFrom, setDateFrom] = useState(nextDateString(0));
  const [dateTo, setDateTo] = useState(nextDateString(7));
  const [selectedSlot, setSelectedSlot] = useState("");
  const [selectedMode, setSelectedMode] = useState<"online" | "onsite">("online");
  const [notes, setNotes] = useState("");
  const [rating, setRating] = useState("5");
  const [reviewComment, setReviewComment] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [submittingBooking, setSubmittingBooking] = useState(false);

  useEffect(() => {
    if (!token || !specialistId) {
      return;
    }

    let cancelled = false;

    void (async () => {
      setLoading(true);
      setError(null);
      try {
        const [profile, availability] = await Promise.all([
          getSpecialist(token, specialistId),
          getSpecialistAvailability(token, specialistId, dateFrom, dateTo),
        ]);

        if (cancelled) {
          return;
        }

        setSpecialist(profile);
        setSlots(availability.slots);
        const initialMode = (profile.consultation_modes[0] ?? "online").toLowerCase();
        setSelectedMode(initialMode === "onsite" ? "onsite" : "online");
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : "Unable to load specialist profile.");
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
  }, [dateFrom, dateTo, specialistId, token]);

  const slotOptions = useMemo(
    () => slots.map((slot) => ({ value: slot.start_datetime, label: formatDateTime(slot.start_datetime) })),
    [slots],
  );
  const selectedSlotLabel = slotOptions.find((slot) => slot.value === selectedSlot)?.label ?? null;

  async function handleBooking() {
    if (!token || !specialist || !selectedSlot) return;
    setSubmittingBooking(true);
    setError(null);
    setSuccess(null);
    try {
      await createAppointment(token, {
        specialist_id: specialist.id,
        mode: selectedMode,
        preferred_datetime: new Date(selectedSlot).toISOString(),
        notes: notes || null,
      });
      setSuccess("Appointment request submitted.");
      setNotes("");
      setSelectedSlot("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to create appointment.");
    } finally {
      setSubmittingBooking(false);
    }
  }

  async function handleReviewSubmit() {
    if (!token || !specialist) return;
    setError(null);
    setSuccess(null);
    try {
      try {
        await createSpecialistReview(token, specialist.id, { rating: Number(rating), comment: reviewComment || null });
      } catch (err) {
        if (err instanceof ApiError && err.detail.toLowerCase().includes("already reviewed")) {
          await updateMySpecialistReview(token, specialist.id, { rating: Number(rating), comment: reviewComment || null });
        } else {
          throw err;
        }
      }
      setSuccess("Review saved.");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to save review.");
    }
  }

  return (
    <AppShell title={specialist?.full_name ?? "Specialist profile"} subtitle="This specialist profile is now backed by live profile and availability endpoints." actions={<ButtonLink to="/specialists" variant="secondary">Back to directory</ButtonLink>}>
      {loading ? <div className="rounded-[28px] border border-[--border] bg-white px-5 py-8 text-sm text-[--muted-foreground] shadow-[var(--shadow-sm)]">Loading specialist profile...</div> : null}
      {error ? <div className="rounded-[28px] border border-[--destructive] bg-[--red-100] px-5 py-4 text-sm">{error}</div> : null}
      {success ? <div className="rounded-[28px] border border-[--teal-200] bg-[--teal-50] px-5 py-4 text-sm">{success}</div> : null}
      {specialist ? (
        <div className="grid gap-6 xl:grid-cols-[1.3fr_1fr]">
          <Card>
            <CardHeader>
              <div className="flex items-start justify-between gap-4">
                <div>
                  <CardTitle>{specialist.full_name}</CardTitle>
                  <CardDescription>{specialist.specialty}</CardDescription>
                </div>
                <Badge variant="success">{specialist.status}</Badge>
              </div>
            </CardHeader>
            <CardContent className="space-y-6">
              <p className="leading-7 text-[--muted-foreground]">{specialist.bio ?? "This specialist has not published a profile bio yet."}</p>
              <div className="grid gap-4 text-sm text-[--muted-foreground] md:grid-cols-2">
                <div className="rounded-[24px] bg-[--sand-100] px-4 py-4"><MapPin className="mb-3 size-5 text-[--primary]" /> {specialist.city ?? "City not set"}</div>
                <div className="rounded-[24px] bg-[--sand-100] px-4 py-4"><Video className="mb-3 size-5 text-[--primary]" /> {(specialist.consultation_modes ?? []).join(", ") || "Consultation modes not set"}</div>
                <div className="rounded-[24px] bg-[--sand-100] px-4 py-4 md:col-span-2"><Star className="mb-3 size-5 text-[--amber-700]" /> {specialist.average_rating?.toFixed(1) ?? "No rating yet"} average rating across {specialist.review_count} review(s).</div>
              </div>

              <div className="rounded-[28px] border border-[--border] p-5">
                <h3 className="text-lg font-semibold tracking-[-0.02em]">Leave or update your review</h3>
                <div className="mt-4 grid gap-4">
                  <SelectField label="Rating" value={rating} onChange={(event) => setRating(event.target.value)}>
                    {[5, 4, 3, 2, 1].map((item) => <option key={item} value={String(item)}>{item}</option>)}
                  </SelectField>
                  <TextareaField label="Comment" value={reviewComment} onChange={(event) => setReviewComment(event.target.value)} />
                  <Button variant="secondary" onClick={() => void handleReviewSubmit()}>Save review</Button>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Book an appointment</CardTitle>
              <CardDescription>Live slot availability within a selected date window.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid gap-4 md:grid-cols-2">
                <SelectField label="Available from" value={dateFrom} onChange={(event) => setDateFrom(event.target.value)}>
                  <option value={dateFrom}>{dateFrom}</option>
                </SelectField>
                <SelectField label="Available to" value={dateTo} onChange={(event) => setDateTo(event.target.value)}>
                  <option value={dateTo}>{dateTo}</option>
                </SelectField>
              </div>
              <SelectField label="Mode" value={selectedMode} onChange={(event) => setSelectedMode(event.target.value as "online" | "onsite")}>
                {(specialist.consultation_modes.length ? specialist.consultation_modes : ["online", "onsite"]).map((mode) => {
                  const normalized = mode.toLowerCase() === "onsite" ? "onsite" : "online";
                  return <option key={normalized} value={normalized}>{toTitleCase(normalized)}</option>;
                })}
              </SelectField>
              <SelectField label="Choose slot" value={selectedSlot} onChange={(event) => setSelectedSlot(event.target.value)}>
                <option value="">Select a slot</option>
                {slotOptions.map((slot) => <option key={slot.value} value={slot.value}>{slot.label}</option>)}
              </SelectField>
              {selectedSlotLabel ? <div className="rounded-[20px] border border-[--teal-200] bg-[--teal-50] px-4 py-3 text-sm">Selected slot: {selectedSlotLabel}</div> : null}
              <TextareaField label="Notes" value={notes} onChange={(event) => setNotes(event.target.value)} />
              <Button onClick={() => void handleBooking()} disabled={!selectedSlot || submittingBooking}><Calendar className="size-4" /> {submittingBooking ? "Requesting..." : "Request appointment"}</Button>
            </CardContent>
          </Card>
        </div>
      ) : null}
    </AppShell>
  );
}
