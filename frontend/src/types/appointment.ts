export type AppointmentMode = "online" | "onsite";
export type AppointmentStatus = "requested" | "confirmed" | "rejected" | "cancelled" | "completed";
export type AppointmentActorRole = "user" | "specialist" | "admin";

export interface AppointmentUserSummary {
  id: string;
  full_name: string;
  email: string;
}

export interface AppointmentSpecialistSummary {
  id: string;
  full_name: string;
  specialty: string;
  city: string | null;
}

export interface Appointment {
  id: string;
  user_id: string;
  specialist_id: string;
  user: AppointmentUserSummary | null;
  specialist: AppointmentSpecialistSummary | null;
  mode: AppointmentMode;
  status: AppointmentStatus;
  preferred_datetime: string;
  end_datetime: string;
  notes: string | null;
  cancellation_reason: string | null;
  rejection_reason: string | null;
  reschedule_note: string | null;
  confirmed_at: string | null;
  rejected_at: string | null;
  cancelled_at: string | null;
  completed_at: string | null;
  last_rescheduled_at: string | null;
  reminder_sent_at: string | null;
  last_rescheduled_by_role: AppointmentActorRole | null;
  status_updated_by_user_id: string | null;
  created_at: string;
  updated_at: string;
}

export interface AppointmentCreatePayload {
  specialist_id: string;
  mode: AppointmentMode;
  preferred_datetime: string;
  notes?: string | null;
}

export interface AppointmentReschedulePayload {
  preferred_datetime: string;
  note?: string | null;
}

export interface AppointmentCancellationPayload {
  reason?: string | null;
}

export interface AppointmentRejectionPayload {
  reason?: string | null;
}

export interface SpecialistAppointmentCreatePayload {
  user_id: string;
  mode: AppointmentMode;
  preferred_datetime: string;
  notes?: string | null;
}

export interface AppointmentSuggestionItem {
  specialist_id: string;
  specialist_name: string;
  specialty: string;
  city: string | null;
  consultation_modes: string[];
  average_rating: number | null;
  review_count: number;
  start_datetime: string;
  end_datetime: string;
}

export interface CriticalAppointmentSuggestions {
  generated_at: string;
  lookahead_days: number;
  total_suggestions: number;
  suggestions: AppointmentSuggestionItem[];
}
