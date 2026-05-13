export type NotificationType =
  | "appointment_requested"
  | "appointment_confirmed"
  | "appointment_rejected"
  | "appointment_rescheduled"
  | "appointment_cancelled"
  | "appointment_reminder";

export interface Notification {
  id: string;
  user_id: string;
  appointment_id: string | null;
  type: NotificationType;
  title: string;
  message: string;
  is_read: boolean;
  read_at: string | null;
  created_at: string;
}

export interface NotificationPageResponse {
  items: Notification[];
  page: number;
  page_size: number;
  total: number;
  total_pages: number;
}
