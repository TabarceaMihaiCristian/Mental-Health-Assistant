import { cn } from "../../lib/cn";

export function Avatar({ name, size = "md", src }: { name: string; size?: "sm" | "md" | "lg"; src?: string | null }) {
  const initials = name
    .split(" ")
    .map((part) => part[0])
    .join("")
    .slice(0, 2)
    .toUpperCase();

  const sizeClass = size === "sm" ? "size-9 text-xs" : size === "lg" ? "size-14 text-lg" : "size-11 text-sm";

  return src ? (
    <img src={src} alt={name} className={cn("rounded-full object-cover", sizeClass)} />
  ) : (
    <div className={cn("flex items-center justify-center rounded-full bg-[--primary-light] font-semibold text-[--primary]", sizeClass)}>
      {initials}
    </div>
  );
}
