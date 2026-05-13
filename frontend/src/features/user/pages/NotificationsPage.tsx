import { useEffect, useState } from "react";
import { AppShell } from "../../../components/layout/AppShell";
import { Badge } from "../../../components/ui/Badge";
import { Button } from "../../../components/ui/Button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../../../components/ui/Card";
import { useAuth } from "../../../app/use-auth";
import { deleteNotification, listNotifications, markAllNotificationsAsRead, markNotificationAsRead, markNotificationAsUnread } from "../../notifications/notificationsApi";
import type { Notification } from "../../../types/notification";
import { formatDateTime, toTitleCase } from "../../../lib/format";

export function NotificationsPage() {
  const { token } = useAuth();
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [error, setError] = useState<string | null>(null);

  async function loadNotifications() {
    if (!token) return;
    try {
      const page = await listNotifications(token);
      setNotifications(page.items);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to load notifications.");
    }
  }

  useEffect(() => {
    if (!token) {
      return;
    }

    let cancelled = false;

    void (async () => {
      try {
        const page = await listNotifications(token);
        if (!cancelled) {
          setNotifications(page.items);
        }
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : "Unable to load notifications.");
        }
      }
    })();

    return () => {
      cancelled = true;
    };
  }, [token]);

  return (
    <AppShell title="Notifications" subtitle="This inbox is now backed by the real notification API.">
      {error ? <div className="rounded-[28px] border border-[--destructive] bg-[--red-100] px-5 py-4 text-sm">{error}</div> : null}
      <div className="flex items-center gap-3">
        <Button variant="secondary" onClick={() => token && markAllNotificationsAsRead(token).then(() => loadNotifications())}>Mark all as read</Button>
      </div>
      <Card>
        <CardHeader>
          <CardTitle>Inbox</CardTitle>
          <CardDescription>Appointment and reminder notifications delivered by the backend.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {notifications.length === 0 ? <p className="text-sm text-[--muted-foreground]">No notifications yet.</p> : null}
          {notifications.map((notification) => (
            <div key={notification.id} className="rounded-[24px] border border-[--border] p-5">
              <div className="flex flex-wrap items-start justify-between gap-4">
                <div>
                  <p className="text-lg font-semibold tracking-[-0.02em]">{notification.title}</p>
                  <p className="mt-2 text-sm text-[--muted-foreground]">{notification.message}</p>
                  <p className="mt-2 text-xs uppercase tracking-[0.16em] text-[--muted-foreground]">{formatDateTime(notification.created_at)}</p>
                </div>
                <Badge variant={notification.is_read ? "muted" : "warning"}>{notification.is_read ? "Read" : "Unread"}</Badge>
              </div>
              <div className="mt-4 flex flex-wrap gap-3">
                <Button
                  variant="secondary"
                  size="sm"
                  onClick={() =>
                    token &&
                    (notification.is_read ? markNotificationAsUnread(token, notification.id) : markNotificationAsRead(token, notification.id)).then(() => loadNotifications())
                  }
                >
                  {notification.is_read ? "Mark unread" : "Mark read"}
                </Button>
                <Button variant="ghost" size="sm" onClick={() => token && deleteNotification(token, notification.id).then(() => loadNotifications())}>Delete</Button>
                <Badge variant="muted">{toTitleCase(notification.type)}</Badge>
              </div>
            </div>
          ))}
        </CardContent>
      </Card>
    </AppShell>
  );
}
