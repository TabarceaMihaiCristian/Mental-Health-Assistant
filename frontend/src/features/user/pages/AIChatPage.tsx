import type { KeyboardEvent } from "react";
import { useEffect, useMemo, useState } from "react";
import { Archive, Calendar, MessageSquare, Send, Square } from "lucide-react";
import { AppShell } from "../../../components/layout/AppShell";
import { Badge } from "../../../components/ui/Badge";
import { Button, ButtonLink } from "../../../components/ui/Button";
import { Card } from "../../../components/ui/Card";
import { Modal } from "../../../components/ui/Modal";
import { TextareaField } from "../../../components/ui/Fields";
import { useAuth } from "../../../app/use-auth";
import { archiveChatSession, closeChatSession, createChatInteraction, createChatSession, getChatSession, getOpenChatSession, listChatSessions } from "../../chat/chatApi";
import type { ChatMessage, ChatSession, ChatSessionDetail } from "../../../types/chat";
import type { CriticalAppointmentSuggestions } from "../../../types/appointment";
import { formatDateTime } from "../../../lib/format";

function normalizeSender(sender: string) {
  return sender.toLowerCase();
}

function mergeMessages(existing: ChatMessage[], incoming: ChatMessage[]) {
  const byId = new Map<string, ChatMessage>();

  for (const message of [...existing, ...incoming]) {
    byId.set(message.id, message);
  }

  return [...byId.values()].sort(
    (left, right) => new Date(left.created_at).getTime() - new Date(right.created_at).getTime(),
  );
}

function toSessionDetail(session: ChatSession): ChatSessionDetail {
  return {
    ...session,
    messages: [],
  };
}

function createOptimisticMessage(sender: ChatMessage["sender"], content: string): ChatMessage {
  return {
    id: `temp-${sender}-${crypto.randomUUID()}`,
    session_id: "pending",
    sender,
    content,
    created_at: new Date().toISOString(),
  };
}

const ASSISTANT_TYPING_TEXT = "Thinking...";

export function AIChatPage() {
  const { token } = useAuth();
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [activeSession, setActiveSession] = useState<ChatSessionDetail | null>(null);
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [suggestions, setSuggestions] = useState<CriticalAppointmentSuggestions | null>(null);

  async function reloadSessions(targetId?: string | null) {
    if (!token) {
      return;
    }
    const [items, openSession] = await Promise.all([listChatSessions(token), getOpenChatSession(token)]);
    setSessions(items);

    const resolvedId = targetId ?? openSession?.id ?? items[0]?.id ?? null;
    if (!resolvedId) {
      setActiveSession(null);
      return;
    }

    setActiveSession(await getChatSession(token, resolvedId));
  }

  useEffect(() => {
    if (!token) {
      return;
    }

    let cancelled = false;

    void (async () => {
      setLoading(true);
      setError(null);
      try {
        const [items, openSession] = await Promise.all([listChatSessions(token), getOpenChatSession(token)]);
        if (cancelled) {
          return;
        }

        setSessions(items);
        const targetSession = openSession ?? items[0] ?? null;
        if (!targetSession) {
          setActiveSession(null);
          return;
        }

        const detail = await getChatSession(token, targetSession.id);
        if (!cancelled) {
          setActiveSession(detail);
        }
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : "Unable to load chat sessions.");
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    })();

    return () => {
      cancelled = true;
    };
  }, [token]);

  async function ensureSession() {
    if (!token) {
      throw new Error("Authentication token missing.");
    }
    if (activeSession && activeSession.status === "open") {
      return activeSession;
    }

    const knownOpenSession = sessions.find((item) => item.status === "open");
    if (knownOpenSession) {
      const detail = await getChatSession(token, knownOpenSession.id);
      setActiveSession(detail);
      return detail;
    }

    const remoteOpenSession = await getOpenChatSession(token);
    if (remoteOpenSession) {
      const detail = await getChatSession(token, remoteOpenSession.id);
      setSessions((current) => {
        const next = current.filter((item) => item.id !== remoteOpenSession.id);
        return [remoteOpenSession, ...next];
      });
      setActiveSession(detail);
      return detail;
    }

    const created = await createChatSession(token);
    const detail = toSessionDetail(created);
    setSessions((current) => [created, ...current]);
    setActiveSession(detail);
    return detail;
  }

  async function handleStartNewSession() {
    if (!token) {
      return;
    }

    setError(null);
    const created = await createChatSession(token);
    const detail = toSessionDetail(created);
    setSessions((current) => [created, ...current.filter((item) => item.id !== created.id)]);
    setActiveSession(detail);
    setSuggestions(null);
    setMessage("");
  }

  async function handleCloseSession() {
    if (!token || !activeSession) return;
    const result = await closeChatSession(token, activeSession.id);
    await reloadSessions(result.session.id);
  }

  async function handleArchiveSession() {
    if (!token || !activeSession) return;
    const result = await archiveChatSession(token, activeSession.id);
    await reloadSessions(result.session.id);
  }

  async function handleSend() {
    if (!token || !message.trim()) {
      return;
    }

    const content = message.trim();
    const optimisticUserMessage = createOptimisticMessage("user", content);
    const typingMessage = createOptimisticMessage("assistant", ASSISTANT_TYPING_TEXT);

    setSending(true);
    setError(null);
    setMessage("");

    try {
      const currentSession = await ensureSession();

      const optimisticUserWithSession = {
        ...optimisticUserMessage,
        session_id: currentSession.id,
      };
      const typingWithSession = {
        ...typingMessage,
        session_id: currentSession.id,
      };

      setActiveSession((existing) => {
        const base = existing ?? currentSession;
        return {
          ...base,
          last_message_at: optimisticUserWithSession.created_at,
          messages: mergeMessages(base.messages, [optimisticUserWithSession, typingWithSession]),
        };
      });

      const response = await createChatInteraction(token, currentSession.id, content);

      setActiveSession((existing) => {
        const base = existing ?? currentSession;
        const withoutTemps = base.messages.filter(
          (item) => item.id !== optimisticUserWithSession.id && item.id !== typingWithSession.id,
        );

        return {
          ...base,
          ...response.session,
          messages: mergeMessages(withoutTemps, [response.user_message, response.assistant_message]),
        };
      });

      setSessions((current) => {
        const next = current.filter((item) => item.id !== response.session.id);
        return [response.session, ...next];
      });
      setSuggestions(response.appointment_suggestions);
    } catch (err) {
      setActiveSession((existing) => {
        if (!existing) {
          return existing;
        }

        return {
          ...existing,
          messages: existing.messages.filter(
            (item) => item.id !== optimisticUserMessage.id && item.id !== typingMessage.id,
          ),
        };
      });
      setMessage(content);
      setError(err instanceof Error ? err.message : "Unable to send message.");
    } finally {
      setSending(false);
    }
  }

  function handleComposerKeyDown(event: KeyboardEvent<HTMLTextAreaElement>) {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      void handleSend();
    }
  }

  const hasCriticalSuggestions = useMemo(() => Boolean(suggestions && suggestions.total_suggestions > 0), [suggestions]);

  return (
    <AppShell
      title="AI support chat"
      subtitle="Talk through what you are feeling and keep your conversations organized in one place."
      actions={
        activeSession ? (
          <div className="flex flex-wrap gap-3">
            {activeSession.status === "open" ? (
              <Button variant="secondary" onClick={() => void handleCloseSession()}>
                <Square className="size-4" />
                Close session
              </Button>
            ) : null}
            {activeSession.status !== "archived" ? (
              <Button variant="ghost" onClick={() => void handleArchiveSession()}>
                <Archive className="size-4" />
                Archive
              </Button>
            ) : null}
          </div>
        ) : undefined
      }
    >
      {error ? <div className="rounded-[28px] border border-[--destructive] bg-[--red-100] px-5 py-4 text-sm">{error}</div> : null}
      <div className="grid min-h-[70vh] gap-6 xl:grid-cols-[320px_1fr]">
        <Card className="overflow-hidden">
          <div className="border-b border-[--border] p-4">
            <Button
              className="w-full"
              onClick={() => void handleStartNewSession()}
              style={{
                backgroundColor: "var(--primary)",
                borderColor: "var(--teal-300)",
                color: "#ffffff",
              }}
            >
              <MessageSquare className="size-4" />
              New chat session
            </Button>
          </div>
          <div className="grid gap-2 p-4">
            {loading ? <p className="text-sm text-[--muted-foreground]">Loading sessions...</p> : null}
            {!loading && sessions.length === 0 ? <p className="text-sm text-[--muted-foreground]">No conversations yet. Start a message when you are ready.</p> : null}
            {sessions.map((session) => (
              <button
                key={session.id}
                className={`rounded-[24px] border p-4 text-left transition ${activeSession?.id === session.id ? "border-[--primary] bg-[--teal-50]" : "border-transparent bg-transparent hover:bg-[--sand-100]"}`}
                onClick={async () => {
                  if (!token) return;
                  setActiveSession(await getChatSession(token, session.id));
                }}
              >
                <div className="flex items-start justify-between gap-3">
                  <p className="font-semibold tracking-[-0.02em]">{session.summary ?? "Support conversation"}</p>
                  <span className="text-xs text-[--muted-foreground] capitalize">{session.status}</span>
                </div>
                <p className="mt-2 text-sm text-[--muted-foreground]">{formatDateTime(session.last_message_at)}</p>
              </button>
            ))}
          </div>
        </Card>

        <Card className="flex min-h-[70vh] flex-col overflow-hidden">
          <div className="flex items-center justify-between border-b border-[--border] px-6 py-5">
            <div>
              <h2 className="text-xl font-semibold tracking-[-0.02em]">Active conversation</h2>
              <p className="mt-1 text-sm text-[--muted-foreground]">
                {activeSession ? `Session started ${formatDateTime(activeSession.started_at)}` : "No active session yet."}
              </p>
            </div>
            <Badge variant={hasCriticalSuggestions ? "warning" : "success"}>{hasCriticalSuggestions ? "Escalation available" : activeSession?.status === "open" ? "Open" : activeSession?.status === "closed" ? "Closed" : "Archived"}</Badge>
          </div>
          <div className="flex-1 space-y-4 overflow-y-auto px-6 py-6">
            {!activeSession ? <p className="text-sm text-[--muted-foreground]">Start a new session or send a message to begin.</p> : null}
            {activeSession?.messages.map((item) => {
              const sender = normalizeSender(item.sender);
              const isUser = sender === "user";
              const isTypingPlaceholder = item.content === ASSISTANT_TYPING_TEXT && item.id.startsWith("temp-assistant-");

              return (
                <div key={item.id} className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
                  <div
                    className={`max-w-[70%] rounded-[24px] border px-5 py-4 text-sm leading-7 shadow-[var(--shadow-sm)] whitespace-pre-wrap ${
                      isUser ? "text-white" : "border-[--border] bg-[--sand-50] text-[--foreground]"
                    }`}
                    style={
                      isUser
                        ? {
                            backgroundColor: "var(--primary)",
                            borderColor: "var(--teal-300)",
                            color: "#ffffff",
                          }
                        : undefined
                    }
                  >
                    {isTypingPlaceholder ? <span className="animate-pulse text-[--muted-foreground]">{item.content}</span> : item.content}
                  </div>
                </div>
              );
            })}
          </div>
          <div className="border-t border-[--border] px-6 py-5">
            <div className="rounded-[28px] border border-[--border] bg-[--sand-50] p-4 shadow-[var(--shadow-sm)]">
              <TextareaField
                label="Message"
                value={message}
                onChange={(event) => setMessage(event.target.value)}
                onKeyDown={handleComposerKeyDown}
                placeholder={activeSession?.status === "open" || !activeSession ? "Type your message..." : "Closed sessions cannot receive new messages."}
                className="min-h-24"
                disabled={Boolean(activeSession && activeSession.status !== "open")}
              />
              <div className="mt-4 flex flex-wrap items-center justify-between gap-3">
                <p className="text-xs text-[--muted-foreground]">Press Enter to send. Use Shift+Enter for a new line.</p>
                <Button onClick={() => void handleSend()} disabled={sending || !message.trim() || Boolean(activeSession && activeSession.status !== "open")}>
                  <Send className="size-4" />
                  {sending ? "Sending..." : "Send message"}
                </Button>
              </div>
            </div>
            <p className="mt-3 text-xs text-[--muted-foreground]">This AI is supportive, but not a replacement for professional care. If you are in crisis, contact emergency resources immediately.</p>
          </div>
        </Card>
      </div>

      <Modal isOpen={hasCriticalSuggestions} title="Recommended care escalation" onClose={() => setSuggestions(null)}>
        <div className="space-y-5">
          <p className="text-sm text-[--muted-foreground]">Based on this conversation, these care options may be worth reviewing next.</p>
          {suggestions?.suggestions.map((item) => (
            <div key={`${item.specialist_id}-${item.start_datetime}`} className="rounded-[24px] border border-[--border] p-4">
              <p className="font-semibold">{item.specialist_name}</p>
              <p className="mt-1 text-sm text-[--muted-foreground]">{item.specialty} · {item.city ?? "City not set"}</p>
              <p className="mt-1 text-sm text-[--muted-foreground]">{formatDateTime(item.start_datetime)}</p>
            </div>
          ))}
          <ButtonLink to="/appointments"><Calendar className="size-4" /> Continue in appointments</ButtonLink>
        </div>
      </Modal>
    </AppShell>
  );
}
