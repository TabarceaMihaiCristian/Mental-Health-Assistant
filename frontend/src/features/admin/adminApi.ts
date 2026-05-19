import { apiRequest } from "../../lib/api";
import type { AppointmentStatus } from "../../types/appointment";
import type {
  AdminSpecialist,
  AdminSpecialistCreatePayload,
  AdminSpecialistPage,
  AdminSpecialistStatusPayload,
  AdminSpecialistUpdatePayload,
  AppointmentPage,
} from "../../types/admin";

export function listAdminSpecialists(token: string, page = 1, pageSize = 100) {
  return apiRequest<AdminSpecialistPage>(`/admin/specialists?page=${page}&page_size=${pageSize}`, {
    method: "GET",
    token,
  });
}

export function createAdminSpecialist(token: string, payload: AdminSpecialistCreatePayload) {
  return apiRequest<AdminSpecialist>("/admin/specialists", {
    method: "POST",
    token,
    body: JSON.stringify(payload),
  });
}

export function updateAdminSpecialist(
  token: string,
  specialistId: string,
  payload: AdminSpecialistUpdatePayload,
) {
  return apiRequest<AdminSpecialist>(`/admin/specialists/${specialistId}`, {
    method: "PATCH",
    token,
    body: JSON.stringify(payload),
  });
}

export function updateAdminSpecialistStatus(
  token: string,
  specialistId: string,
  payload: AdminSpecialistStatusPayload,
) {
  return apiRequest<AdminSpecialist>(`/admin/specialists/${specialistId}/status`, {
    method: "PATCH",
    token,
    body: JSON.stringify(payload),
  });
}

export function listAdminAppointments(
  token: string,
  filters: {
    status?: AppointmentStatus | "";
    specialist_id?: string;
    user_id?: string;
    date_from?: string;
    date_to?: string;
    page?: number;
    page_size?: number;
  } = {},
) {
  const params = new URLSearchParams();

  if (filters.status) params.set("status", filters.status);
  if (filters.specialist_id) params.set("specialist_id", filters.specialist_id);
  if (filters.user_id) params.set("user_id", filters.user_id);
  if (filters.date_from) params.set("date_from", filters.date_from);
  if (filters.date_to) params.set("date_to", filters.date_to);
  params.set("page", String(filters.page ?? 1));
  params.set("page_size", String(filters.page_size ?? 100));

  return apiRequest<AppointmentPage>(`/admin/appointments?${params.toString()}`, {
    method: "GET",
    token,
  });
}
