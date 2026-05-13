import { HTMLAttributes } from "react";
import { cn } from "../../lib/utils";
import { Bell, Search } from "lucide-react";
import { Avatar } from "../ui/Avatar";
import { Input } from "../ui/Input";

interface HeaderProps extends HTMLAttributes<HTMLElement> {
  userName?: string;
  userAvatar?: string;
  showSearch?: boolean;
}

export function Header({ userName = "User", userAvatar, showSearch, className, ...props }: HeaderProps) {
  return (
    <header
      className={cn(
        "h-16 border-b border-[--border] bg-[--card] flex items-center justify-between px-6",
        className
      )}
      {...props}
    >
      {showSearch && (
        <div className="flex-1 max-w-md">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 size-5 text-[--muted-foreground]" />
            <input
              type="search"
              placeholder="Search..."
              className="w-full h-10 pl-10 pr-4 rounded-[--radius-lg] border border-[--border] bg-[--input-background] text-[--foreground] placeholder:text-[--muted-foreground] focus:outline-none focus:ring-2 focus:ring-[--ring]"
            />
          </div>
        </div>
      )}

      {!showSearch && <div />}

      <div className="flex items-center gap-4">
        <button
          className="relative p-2 rounded-[--radius-lg] hover:bg-[--accent] transition-colors"
          aria-label="Notifications"
        >
          <Bell className="size-5 text-[--foreground]" />
          <span className="absolute top-1.5 right-1.5 size-2 bg-[--destructive] rounded-full" />
        </button>

        <div className="flex items-center gap-3">
          <Avatar src={userAvatar} fallback={userName[0]} size="md" />
          <span className="font-[--font-weight-medium] text-[--foreground]">{userName}</span>
        </div>
      </div>
    </header>
  );
}
