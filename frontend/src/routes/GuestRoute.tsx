import { Navigate, Outlet } from "react-router-dom";
import { useAuth } from "../app/use-auth";
import { getHomePathForRole } from "../lib/role-home";

export function GuestRoute() {
  const { status, user } = useAuth();

  if (status === "loading") {
    return <div className="flex min-h-screen items-center justify-center px-6 text-sm text-[--muted-foreground]">Checking session...</div>;
  }

  if (status === "authenticated") {
    return <Navigate to={getHomePathForRole(user?.role)} replace />;
  }

  return <Outlet />;
}
