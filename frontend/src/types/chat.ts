import type { CriticalAppointmentSuggestions } from "./appointment";

export type SenderType = "user" | "assistant" | "system";
export type ChatSessionStatus = "open" | "closed" | "archived";

export interface ChatMessage {
  id: string;
  session_id: string;
  sender: SenderType;
  content: string;
  created_at: string;
}

export interface ChatSession {
  id: string;
  user_id: string;
  status: ChatSessionStatus;
  started_at: string;
  last_message_at: string;
  ended_at: string | null;
  summary: string | null;
  created_at: string;
  updated_at: string;
}

export interface ChatSessionDetail extends ChatSession {
  messages: ChatMessage[];
}

export interface ChatInteractionResponse {
  user_message: ChatMessage;
  assistant_message: ChatMessage;
  session: ChatSession;
  appointment_suggestions: CriticalAppointmentSuggestions | null;
}
