import type { Appointment } from "./appointment";

export interface Specialist {
  id: string;
  full_name: string;
  specialty: string;
  bio: string | null;
  consultation_modes: string[];
  city: string | null;
  status: string;
  average_rating: number | null;
  review_count: number;
}

export interface SpecialistAvailabilitySlot {
  start_datetime: string;
  end_datetime: string;
  is_available: boolean;
}

export interface SpecialistAvailability {
  specialist_id: string;
  slot_duration_minutes: number;
  date_from: string;
  date_to: string;
  slots: SpecialistAvailabilitySlot[];
}

export interface SpecialistReview {
  id: string;
  specialist_id: string;
  user_id: string;
  rating: number;
  comment: string | null;
  created_at: string;
  updated_at: string;
}

export interface SpecialistReviewPayload {
  rating: number;
  comment?: string | null;
}

export interface AvailabilityRule {
  id: string;
  specialist_id: string;
  weekday: number;
  start_time: string;
  end_time: string;
  is_enabled: boolean;
}

export interface AvailabilityRulePayload {
  weekday: number;
  start_time: string;
  end_time: string;
  is_enabled: boolean;
}

export interface SpecialistBreak {
  id: string;
  specialist_id: string;
  weekday: number;
  start_time: string;
  end_time: string;
  label: string | null;
}

export interface SpecialistBreakPayload {
  weekday: number;
  start_time: string;
  end_time: string;
  label?: string | null;
}

export interface SpecialistTimeOff {
  id: string;
  specialist_id: string;
  start_datetime: string;
  end_datetime: string;
  reason: string | null;
}

export interface SpecialistTimeOffPayload {
  start_datetime: string;
  end_datetime: string;
  reason?: string | null;
}

export interface SpecialistCalendar {
  specialist_id: string;
  date_from: string;
  date_to: string;
  appointments: Appointment[];
  available_slots: SpecialistAvailabilitySlot[];
  breaks: SpecialistBreak[];
  time_off_periods: SpecialistTimeOff[];
}
