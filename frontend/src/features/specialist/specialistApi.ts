import { apiRequest } from "../../lib/api";
import type {
  Appointment,
  AppointmentRejectionPayload,
  AppointmentReschedulePayload,
  SpecialistAppointmentCreatePayload,
} from "../../types/appointment";
import type {
  AvailabilityRule,
  AvailabilityRulePayload,
  SpecialistBreak,
  SpecialistBreakPayload,
  SpecialistCalendar,
  SpecialistTimeOff,
  SpecialistTimeOffPayload,
} from "../../types/specialist";

export function listSpecialistAppointments(token: string) {
  return apiRequest<Appointment[]>("/specialist/appointments", { method: "GET", token });
}

export function confirmSpecialistAppointment(token: string, appointmentId: string) {
  return apiRequest<Appointment>(`/specialist/appointments/${appointmentId}/confirm`, { method: "PATCH", token });
}

export function rejectSpecialistAppointment(token: string, appointmentId: string, payload: AppointmentRejectionPayload) {
  return apiRequest<Appointment>(`/specialist/appointments/${appointmentId}/reject`, {
    method: "PATCH",
    token,
    body: JSON.stringify(payload),
  });
}

export function rescheduleSpecialistAppointment(token: string, appointmentId: string, payload: AppointmentReschedulePayload) {
  return apiRequest<Appointment>(`/specialist/appointments/${appointmentId}/reschedule`, {
    method: "PATCH",
    token,
    body: JSON.stringify(payload),
  });
}

export function completeSpecialistAppointment(token: string, appointmentId: string) {
  return apiRequest<Appointment>(`/specialist/appointments/${appointmentId}/complete`, { method: "PATCH", token });
}

export function createSpecialistAppointment(token: string, payload: SpecialistAppointmentCreatePayload) {
  return apiRequest<Appointment>("/specialist/appointments", {
    method: "POST",
    token,
    body: JSON.stringify(payload),
  });
}

export function listAvailabilityRules(token: string) {
  return apiRequest<AvailabilityRule[]>("/specialists/me/availability", { method: "GET", token });
}

export function replaceAvailabilityRules(token: string, payload: AvailabilityRulePayload[]) {
  return apiRequest<AvailabilityRule[]>("/specialists/me/availability", {
    method: "PUT",
    token,
    body: JSON.stringify(payload),
  });
}

export function getSpecialistCalendar(token: string, dateFrom: string, dateTo: string) {
  return apiRequest<SpecialistCalendar>(`/specialists/me/calendar?date_from=${dateFrom}&date_to=${dateTo}`, {
    method: "GET",
    token,
  });
}

export function listBreaks(token: string) {
  return apiRequest<SpecialistBreak[]>("/specialists/me/breaks", { method: "GET", token });
}

export function createBreak(token: string, payload: SpecialistBreakPayload) {
  return apiRequest<SpecialistBreak>("/specialists/me/breaks", {
    method: "POST",
    token,
    body: JSON.stringify(payload),
  });
}

export function deleteBreak(token: string, breakId: string) {
  return apiRequest<void>(`/specialists/me/breaks/${breakId}`, { method: "DELETE", token });
}

export function listTimeOff(token: string) {
  return apiRequest<SpecialistTimeOff[]>("/specialists/me/time-off", { method: "GET", token });
}

export function createTimeOff(token: string, payload: SpecialistTimeOffPayload) {
  return apiRequest<SpecialistTimeOff>("/specialists/me/time-off", {
    method: "POST",
    token,
    body: JSON.stringify(payload),
  });
}

export function deleteTimeOff(token: string, timeOffId: string) {
  return apiRequest<void>(`/specialists/me/time-off/${timeOffId}`, { method: "DELETE", token });
}
