import type { Appointment } from "./appointment";

export type SpecialistStatus = "active" | "inactive";

export interface AdminSpecialist {
  id: string;
  user_id: string | null;
  full_name: string;
  specialty: string;
  bio: string | null;
  consultation_modes: string[];
  city: string | null;
  status: SpecialistStatus;
  email: string | null;
  user_is_active: boolean | null;
  average_rating: number | null;
  review_count: number;
}

export interface AdminSpecialistPage {
  items: AdminSpecialist[];
  page: number;
  page_size: number;
  total: number;
  total_pages: number;
}

export interface AdminSpecialistCreatePayload {
  email: string;
  full_name: string;
  password: string;
  specialty: string;
  bio?: string | null;
  consultation_modes: string[];
  city?: string | null;
}

export interface AdminSpecialistUpdatePayload {
  full_name?: string | null;
  specialty?: string | null;
  bio?: string | null;
  consultation_modes?: string[] | null;
  city?: string | null;
}

export interface AdminSpecialistStatusPayload {
  status: SpecialistStatus;
}

export interface AppointmentPage {
  items: Appointment[];
  page: number;
  page_size: number;
  total: number;
  total_pages: number;
}
