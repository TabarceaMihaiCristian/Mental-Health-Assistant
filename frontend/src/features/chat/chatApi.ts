import { apiRequest } from "../../lib/api";
import type { ChatInteractionResponse, ChatSession, ChatSessionDetail } from "../../types/chat";

export function listChatSessions(token: string) {
  return apiRequest<ChatSession[]>("/chat/sessions", { method: "GET", token });
}

export function getOpenChatSession(token: string) {
  return apiRequest<ChatSession | null>("/chat/sessions/open", { method: "GET", token });
}

export function createChatSession(token: string, summary?: string | null) {
  return apiRequest<ChatSession>("/chat/sessions", {
    method: "POST",
    token,
    body: JSON.stringify({ summary: summary ?? null }),
  });
}

export function getChatSession(token: string, sessionId: string) {
  return apiRequest<ChatSessionDetail>(`/chat/sessions/${sessionId}`, { method: "GET", token });
}

export function closeChatSession(token: string, sessionId: string) {
  return apiRequest<{ session: ChatSession }>(`/chat/sessions/${sessionId}/close`, {
    method: "PATCH",
    token,
  });
}

export function archiveChatSession(token: string, sessionId: string) {
  return apiRequest<{ session: ChatSession }>(`/chat/sessions/${sessionId}/archive`, {
    method: "PATCH",
    token,
  });
}

export function createChatInteraction(token: string, sessionId: string, content: string) {
  return apiRequest<ChatInteractionResponse>(`/chat/sessions/${sessionId}/interactions`, {
    method: "POST",
    token,
    body: JSON.stringify({ content }),
  });
}
