import { apiRequest } from "../../lib/api";
import type {
  Appointment,
  AppointmentCancellationPayload,
  AppointmentCreatePayload,
  AppointmentReschedulePayload,
  CriticalAppointmentSuggestions,
} from "../../types/appointment";

export function listAppointments(token: string) {
  return apiRequest<Appointment[]>("/appointments", { method: "GET", token });
}

export function createAppointment(token: string, payload: AppointmentCreatePayload) {
  return apiRequest<Appointment>("/appointments", {
    method: "POST",
    token,
    body: JSON.stringify(payload),
  });
}

export function cancelAppointment(token: string, appointmentId: string, payload: AppointmentCancellationPayload) {
  return apiRequest<Appointment>(`/appointments/${appointmentId}/cancel`, {
    method: "PATCH",
    token,
    body: JSON.stringify(payload),
  });
}

export function rescheduleAppointment(token: string, appointmentId: string, payload: AppointmentReschedulePayload) {
  return apiRequest<Appointment>(`/appointments/${appointmentId}/reschedule`, {
    method: "PATCH",
    token,
    body: JSON.stringify(payload),
  });
}

export function listCriticalAppointmentSuggestions(token: string) {
  return apiRequest<CriticalAppointmentSuggestions>("/appointments/suggestions/critical", {
    method: "GET",
    token,
  });
}
