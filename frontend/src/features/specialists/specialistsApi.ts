import { apiRequest } from "../../lib/api";
import type { Specialist, SpecialistAvailability, SpecialistReview, SpecialistReviewPayload } from "../../types/specialist";

export function listSpecialists(token: string) {
  return apiRequest<Specialist[]>("/specialists", {
    method: "GET",
    token,
  });
}

export function getSpecialist(token: string, specialistId: string) {
  return apiRequest<Specialist>(`/specialists/${specialistId}`, {
    method: "GET",
    token,
  });
}

export function getSpecialistAvailability(token: string, specialistId: string, dateFrom: string, dateTo: string) {
  return apiRequest<SpecialistAvailability>(`/specialists/${specialistId}/availability?date_from=${dateFrom}&date_to=${dateTo}`, {
    method: "GET",
    token,
  });
}

export function createSpecialistReview(token: string, specialistId: string, payload: SpecialistReviewPayload) {
  return apiRequest<SpecialistReview>(`/specialists/${specialistId}/reviews`, {
    method: "POST",
    token,
    body: JSON.stringify(payload),
  });
}

export function updateMySpecialistReview(token: string, specialistId: string, payload: SpecialistReviewPayload) {
  return apiRequest<SpecialistReview>(`/specialists/${specialistId}/reviews/me`, {
    method: "PUT",
    token,
    body: JSON.stringify(payload),
  });
}
