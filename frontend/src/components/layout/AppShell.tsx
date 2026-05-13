import type { ComponentType, ReactNode } from "react";
import { Bell, Calendar, FileText, LayoutDashboard, LogOut, MessageSquare, Settings, Shield, Users } from "lucide-react";
import { NavLink } from "react-router-dom";
import { useAuth } from "../../app/use-auth";
import { cn } from "../../lib/cn";
import { Avatar } from "../ui/Avatar";
import { Button } from "../ui/Button";

interface NavItem {
  label: string;
  to: string;
  icon: ComponentType<{ className?: string }>;
}

const userItems: NavItem[] = [
  { label: "Dashboard", to: "/app", icon: LayoutDashboard },
  { label: "AI Chat", to: "/chat", icon: MessageSquare },
  { label: "Specialists", to: "/specialists", icon: Users },
  { label: "Appointments", to: "/appointments", icon: Calendar },
  { label: "Reports", to: "/reports", icon: FileText },
  { label: "Notifications", to: "/notifications", icon: Bell },
  { label: "Settings", to: "/settings", icon: Settings },
];

const specialistItems: NavItem[] = [
  { label: "Dashboard", to: "/specialist/dashboard", icon: LayoutDashboard },
  { label: "Appointments", to: "/specialist/appointments", icon: Calendar },
  { label: "Schedule", to: "/specialist/schedule", icon: MessageSquare },
  { label: "Notifications", to: "/notifications", icon: Bell },
  { label: "System", to: "/design-system", icon: Shield },
];

export function AppShell({ title, subtitle, children, role = "user", actions }: { title: string; subtitle?: string; children: ReactNode; role?: "user" | "specialist"; actions?: ReactNode }) {
  const { user, logout } = useAuth();
  const navItems = role === "specialist" ? specialistItems : userItems;
  const displayName = role === "specialist" ? "Specialist Workspace" : user?.full_name ?? "User";

  return (
    <div className="flex min-h-screen bg-transparent">
      <aside className="hidden w-72 shrink-0 border-r border-[--sidebar-border] bg-[color:rgba(248,249,250,0.88)] px-5 py-6 lg:flex lg:flex-col">
        <div className="mb-8 flex items-center gap-3 px-2">
          <div className="flex size-12 items-center justify-center rounded-2xl bg-[--primary-light] text-[--primary]">
            <Shield className="size-6" />
          </div>
          <div>
            <p className="text-sm uppercase tracking-[0.18em] text-[--muted-foreground]">Mental Health</p>
            <p className="text-lg font-semibold tracking-[-0.02em]">Assistant</p>
          </div>
        </div>
        <nav className="grid gap-1">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                cn(
                  "flex items-center gap-3 rounded-2xl px-4 py-3 text-sm font-medium transition-colors",
                  isActive ? "bg-white text-[--foreground] shadow-[var(--shadow-sm)]" : "text-[--muted-foreground] hover:bg-[--sidebar-accent] hover:text-[--foreground]",
                )
              }
            >
              <item.icon className="size-5" />
              <span>{item.label}</span>
            </NavLink>
          ))}
        </nav>
        <div className="mt-auto rounded-[28px] border border-[--border] bg-white p-4 shadow-[var(--shadow-sm)]">
          <div className="flex items-center gap-3">
            <Avatar name={displayName} />
            <div>
              <p className="font-semibold tracking-[-0.02em]">{displayName}</p>
              <p className="text-sm text-[--muted-foreground]">{role === "specialist" ? "Specialist view" : user?.email}</p>
            </div>
          </div>
          <Button variant="ghost" size="sm" className="mt-4 w-full justify-start rounded-2xl" onClick={logout}>
            <LogOut className="size-4" />
            Logout
          </Button>
        </div>
      </aside>

      <div className="flex min-h-screen flex-1 flex-col">
        <header className="border-b border-[--border] bg-[color:rgba(255,255,255,0.82)] px-6 py-5 backdrop-blur-md">
          <div className="mx-auto flex w-full max-w-7xl items-start justify-between gap-6">
            <div>
              <p className="text-sm uppercase tracking-[0.18em] text-[--muted-foreground]">{role === "specialist" ? "Practice workspace" : "Authenticated workspace"}</p>
              <h1 className="mt-2 text-4xl font-semibold tracking-[-0.04em] text-[--foreground]">{title}</h1>
              {subtitle ? <p className="mt-3 max-w-3xl text-[--muted-foreground]">{subtitle}</p> : null}
            </div>
            <div className="flex shrink-0 items-center gap-3">
              {actions}
            </div>
          </div>
        </header>
        <main className="mx-auto flex w-full max-w-7xl flex-1 flex-col gap-6 px-6 py-8">{children}</main>
      </div>
    </div>
  );
}


