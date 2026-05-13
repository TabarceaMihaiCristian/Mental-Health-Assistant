import { Navigate, Outlet, useLocation } from "react-router-dom";
import { useAuth } from "../app/use-auth";

export function ProtectedRoute() {
  const { status } = useAuth();
  const location = useLocation();

  if (status === "loading") {
    return <div className="flex min-h-screen items-center justify-center px-6 text-sm text-[--muted-foreground]">Checking session...</div>;
  }

  if (status !== "authenticated") {
    return <Navigate to="/login" replace state={{ from: location }} />;
  }

  return <Outlet />;
}
