import { useState } from "react";
import { Sidebar } from "../../components/layout/Sidebar";
import { Header } from "../../components/layout/Header";
import { Card, CardContent } from "../../components/ui/Card";
import { Button } from "../../components/ui/Button";
import { Textarea } from "../../components/ui/Textarea";
import { Badge } from "../../components/ui/Badge";
import { MessageSquare, Send, AlertTriangle, Calendar } from "lucide-react";
import { Modal } from "../../components/ui/Modal";

export default function AIChat() {
  const [message, setMessage] = useState("");
  const [showEscalation, setShowEscalation] = useState(false);

  const sessions = [
    { id: 1, title: "Work stress discussion", date: "Today", preview: "Let's talk about coping strategies..." },
    { id: 2, title: "Sleep patterns", date: "Yesterday", preview: "I've been having trouble sleeping..." },
    { id: 3, title: "Anxiety management", date: "May 10", preview: "What techniques can help with..." },
  ];

  const messages = [
    { id: 1, type: "assistant", content: "Hello Sarah, I'm here to support you. How are you feeling today?" },
    { id: 2, type: "user", content: "Hi, I've been feeling really overwhelmed with work lately. It's hard to manage everything." },
    { id: 3, type: "assistant", content: "I understand that feeling overwhelmed at work can be really challenging. Let's explore this together. Can you tell me more about what specifically is making you feel overwhelmed?" },
    { id: 4, type: "user", content: "There's just so much on my plate. Deadlines are piling up and I feel like I can't catch a break." },
    { id: 5, type: "assistant", content: "It sounds like you're dealing with a lot right now. Here are a few coping strategies that might help:\n\n1. **Prioritize tasks** - Break down your work into smaller, manageable chunks\n2. **Set boundaries** - It's okay to say no or ask for help\n3. **Take regular breaks** - Even 5 minutes can help reset your mind\n4. **Practice breathing exercises** - Deep breathing can reduce stress in the moment\n\nWould you like to explore any of these strategies in more detail?" },
  ];

  return (
    <div className="flex min-h-screen bg-[--background]">
      <Sidebar role="user" />

      <div className="flex-1 flex flex-col">
        <Header userName="Sarah Johnson" showSearch={false} />

        <main className="flex-1 flex overflow-hidden">
          {/* Sessions Sidebar */}
          <div className="w-80 border-r border-[--border] bg-[--card] flex flex-col">
            <div className="p-4 border-b border-[--border]">
              <Button variant="primary" className="w-full">
                <MessageSquare className="size-4 mr-2" />
                New Chat Session
              </Button>
            </div>

            <div className="flex-1 overflow-y-auto p-4 space-y-2">
              {sessions.map((session) => (
                <div
                  key={session.id}
                  className={`p-4 rounded-[--radius-lg] cursor-pointer transition-colors ${
                    session.id === 1
                      ? "bg-[--primary-light] border border-[--primary]"
                      : "hover:bg-[--accent]"
                  }`}
                >
                  <div className="flex items-start justify-between mb-1">
                    <h4 className="font-[--font-weight-medium] text-[--foreground] text-sm">
                      {session.title}
                    </h4>
                    <span className="text-xs text-[--muted-foreground]">{session.date}</span>
                  </div>
                  <p className="text-xs text-[--muted-foreground] line-clamp-2">{session.preview}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Chat Area */}
          <div className="flex-1 flex flex-col">
            {/* Chat Header */}
            <div className="p-4 border-b border-[--border] bg-[--card]">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="font-[--font-weight-semibold] text-[--foreground]">AI Support Chat</h2>
                  <p className="text-sm text-[--muted-foreground]">Available 24/7 for emotional support</p>
                </div>
                <Badge variant="risk-low">Low Risk</Badge>
              </div>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-6 space-y-4">
              {messages.map((msg) => (
                <div
                  key={msg.id}
                  className={`flex ${msg.type === "user" ? "justify-end" : "justify-start"}`}
                >
                  <div
                    className={`max-w-[70%] rounded-[--radius-lg] p-4 ${
                      msg.type === "user"
                        ? "bg-[--primary] text-white"
                        : "bg-[--card] border border-[--border] text-[--foreground]"
                    }`}
                  >
                    <p className="text-sm whitespace-pre-line">{msg.content}</p>
                  </div>
                </div>
              ))}

              {/* Typing Indicator */}
              <div className="flex justify-start">
                <div className="bg-[--card] border border-[--border] rounded-[--radius-lg] p-4">
                  <div className="flex gap-1">
                    <div className="size-2 rounded-full bg-[--muted-foreground] animate-bounce" style={{ animationDelay: "0ms" }} />
                    <div className="size-2 rounded-full bg-[--muted-foreground] animate-bounce" style={{ animationDelay: "150ms" }} />
                    <div className="size-2 rounded-full bg-[--muted-foreground] animate-bounce" style={{ animationDelay: "300ms" }} />
                  </div>
                </div>
              </div>
            </div>

            {/* Input Area */}
            <div className="p-4 border-t border-[--border] bg-[--card]">
              <div className="flex items-end gap-3">
                <div className="flex-1">
                  <Textarea
                    value={message}
                    onChange={(e) => setMessage(e.target.value)}
                    placeholder="Type your message..."
                    className="min-h-[60px] resize-none"
                  />
                </div>
                <Button variant="primary" size="lg">
                  <Send className="size-4 mr-2" />
                  Send
                </Button>
              </div>
              <p className="text-xs text-[--muted-foreground] mt-2">
                This AI is here to support you, but it's not a replacement for professional care. If you're in crisis, please call 988.
              </p>
            </div>
          </div>
        </main>
      </div>

      {/* Risk Escalation Modal */}
      <Modal
        isOpen={showEscalation}
        onClose={() => setShowEscalation(false)}
        title="We're Here to Support You"
        size="lg"
      >
        <div className="space-y-6">
          <div className="flex items-start gap-4 p-4 rounded-[--radius-lg] bg-[--amber-100] border border-[--amber-600]">
            <AlertTriangle className="size-6 text-[--amber-600] flex-shrink-0 mt-0.5" />
            <div>
              <p className="text-[--foreground]">
                Based on our conversation, I think it might be helpful for you to speak with a licensed mental health professional. They can provide specialized support tailored to your needs.
              </p>
            </div>
          </div>

          <div>
            <h3 className="font-[--font-weight-semibold] text-[--foreground] mb-3">
              Recommended Next Steps
            </h3>
            <div className="space-y-3">
              <div className="p-4 rounded-[--radius-lg] border border-[--border] bg-[--card]">
                <h4 className="font-[--font-weight-medium] text-[--foreground] mb-2">
                  Book an Appointment
                </h4>
                <p className="text-sm text-[--muted-foreground] mb-4">
                  Connect with a licensed specialist who can provide professional guidance and support.
                </p>
                <Button variant="primary" className="w-full">
                  <Calendar className="size-4 mr-2" />
                  Find a Specialist
                </Button>
              </div>

              <div className="p-4 rounded-[--radius-lg] border border-[--border] bg-[--card]">
                <h4 className="font-[--font-weight-medium] text-[--foreground] mb-2">
                  Crisis Resources
                </h4>
                <p className="text-sm text-[--muted-foreground] mb-2">
                  If you're experiencing a crisis, please reach out immediately:
                </p>
                <ul className="text-sm text-[--foreground] space-y-1">
                  <li>• <strong>988 Suicide & Crisis Lifeline:</strong> Call or text 988</li>
                  <li>• <strong>Crisis Text Line:</strong> Text "HELLO" to 741741</li>
                  <li>• <strong>Emergency:</strong> Call 911 or go to your nearest ER</li>
                </ul>
              </div>
            </div>
          </div>

          <div className="flex gap-3">
            <Button variant="secondary" className="flex-1" onClick={() => setShowEscalation(false)}>
              Continue Chat
            </Button>
            <Button variant="primary" className="flex-1">
              Book Appointment
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
}
