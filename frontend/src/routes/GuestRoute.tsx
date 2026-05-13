import { Navigate, Outlet } from "react-router-dom";
import { useAuth } from "../app/use-auth";

export function GuestRoute() {
  const { status } = useAuth();

  if (status === "loading") {
    return <div className="flex min-h-screen items-center justify-center px-6 text-sm text-[--muted-foreground]">Checking session...</div>;
  }

  if (status === "authenticated") {
    return <Navigate to="/app" replace />;
  }

  return <Outlet />;
}
