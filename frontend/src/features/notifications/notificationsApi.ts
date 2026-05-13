import { apiRequest } from "../../lib/api";
import type { NotificationPageResponse } from "../../types/notification";

interface NotificationFilters {
  isRead?: boolean;
  type?: string;
}

function toQuery(filters: NotificationFilters = {}) {
  const params = new URLSearchParams();
  if (typeof filters.isRead === "boolean") {
    params.set("is_read", String(filters.isRead));
  }
  if (filters.type) {
    params.set("type", filters.type);
  }
  const query = params.toString();
  return query ? `?${query}` : "";
}

export function listNotifications(token: string, filters: NotificationFilters = {}) {
  return apiRequest<NotificationPageResponse>(`/notifications${toQuery(filters)}`, { method: "GET", token });
}

export function getUnreadNotificationCount(token: string) {
  return apiRequest<{ unread_count: number }>("/notifications/unread-count", { method: "GET", token });
}

export function markNotificationAsRead(token: string, notificationId: string) {
  return apiRequest(`/notifications/${notificationId}/read`, { method: "PATCH", token });
}

export function markNotificationAsUnread(token: string, notificationId: string) {
  return apiRequest(`/notifications/${notificationId}/unread`, { method: "PATCH", token });
}

export function markAllNotificationsAsRead(token: string) {
  return apiRequest("/notifications/read-all", { method: "PATCH", token });
}

export function deleteNotification(token: string, notificationId: string) {
  return apiRequest<void>(`/notifications/${notificationId}`, { method: "DELETE", token });
}

export function bulkDeleteNotifications(token: string, filters: NotificationFilters = {}) {
  return apiRequest<{ affected_count: number }>(`/notifications${toQuery(filters)}`, { method: "DELETE", token });
}
