import { Navigate, Outlet, useLocation } from "react-router-dom";
import { useAuth } from "../app/use-auth";
import { getHomePathForRole } from "../lib/role-home";

export function AdminRoute() {
  const { status, user } = useAuth();
  const location = useLocation();

  if (status === "loading") {
    return <div className="flex min-h-screen items-center justify-center px-6 text-sm text-[--muted-foreground]">Checking admin access...</div>;
  }

  if (status !== "authenticated") {
    return <Navigate to="/login" replace state={{ from: location }} />;
  }

  if (user?.role !== "admin") {
    return <Navigate to={getHomePathForRole(user?.role)} replace />;
  }

  return <Outlet />;
}
