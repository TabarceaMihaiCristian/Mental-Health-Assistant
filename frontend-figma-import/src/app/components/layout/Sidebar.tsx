import { ReactNode, HTMLAttributes } from "react";
import { cn } from "../../lib/utils";
import { Home, MessageSquare, Users, Calendar, FileText, Bell, Settings, LayoutDashboard, UserCircle, Clock, Shield } from "lucide-react";

interface SidebarProps extends HTMLAttributes<HTMLElement> {
  role?: "user" | "specialist" | "admin";
}

export function Sidebar({ role = "user", className, ...props }: SidebarProps) {
  const userNavItems = [
    { icon: Home, label: "Dashboard", href: "#dashboard" },
    { icon: MessageSquare, label: "AI Chat", href: "#chat" },
    { icon: Users, label: "Find Specialists", href: "#specialists" },
    { icon: Calendar, label: "Appointments", href: "#appointments" },
    { icon: FileText, label: "Reports", href: "#reports" },
    { icon: Bell, label: "Notifications", href: "#notifications" },
    { icon: Settings, label: "Settings", href: "#settings" },
  ];

  const specialistNavItems = [
    { icon: LayoutDashboard, label: "Dashboard", href: "#specialist-dashboard" },
    { icon: Calendar, label: "Appointments", href: "#specialist-appointments" },
    { icon: Clock, label: "Schedule", href: "#specialist-schedule" },
    { icon: Bell, label: "Notifications", href: "#notifications" },
    { icon: UserCircle, label: "Profile", href: "#profile" },
  ];

  const adminNavItems = [
    { icon: LayoutDashboard, label: "Dashboard", href: "#admin-dashboard" },
    { icon: Users, label: "Specialists", href: "#admin-specialists" },
    { icon: Calendar, label: "Appointments", href: "#admin-appointments" },
    { icon: Shield, label: "System", href: "#admin-system" },
  ];

  const navItems = role === "specialist" ? specialistNavItems : role === "admin" ? adminNavItems : userNavItems;

  return (
    <aside
      className={cn(
        "w-64 h-screen bg-[--sidebar] border-r border-[--sidebar-border] flex flex-col",
        className
      )}
      {...props}
    >
      <div className="p-6">
        <h2 className="text-xl font-[--font-weight-semibold] text-[--sidebar-foreground]">
          Mental Health Assistant
        </h2>
      </div>

      <nav className="flex-1 px-3 py-2 space-y-1">
        {navItems.map((item) => (
          <a
            key={item.href}
            href={item.href}
            className={cn(
              "flex items-center gap-3 px-3 py-2.5 rounded-[--radius-lg] transition-colors",
              "text-[--sidebar-foreground] hover:bg-[--sidebar-accent]"
            )}
          >
            <item.icon className="size-5" />
            <span>{item.label}</span>
          </a>
        ))}
      </nav>
    </aside>
  );
}
