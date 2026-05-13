import { apiRequest } from "../../lib/api";
import type { User } from "../../types/auth";

export interface UserProfileUpdatePayload {
  full_name: string;
  age_range?: string | null;
  occupation?: string | null;
  goals?: string | null;
  preferred_activities?: string[];
  timezone: string;
}

export interface PasswordChangePayload {
  current_password: string;
  new_password: string;
}

export function getCurrentUserAccount(token: string) {
  return apiRequest<User>("/users/me", { method: "GET", token });
}

export function updateCurrentUserProfile(token: string, payload: UserProfileUpdatePayload) {
  return apiRequest<User>("/users/me", {
    method: "PUT",
    token,
    body: JSON.stringify(payload),
  });
}

export function changeCurrentUserPassword(token: string, payload: PasswordChangePayload) {
  return apiRequest<void>("/users/me/password", {
    method: "PATCH",
    token,
    body: JSON.stringify(payload),
  });
}
