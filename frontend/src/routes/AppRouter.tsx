import { createBrowserRouter, RouterProvider } from "react-router-dom";
import { GuestRoute } from "./GuestRoute";
import { NotFoundPage } from "./NotFoundPage";
import { ProtectedRoute } from "./ProtectedRoute";
import { LandingPage } from "../features/public/pages/LandingPage";
import { DashboardPage } from "../features/user/pages/DashboardPage";
import { LoginPage } from "../features/auth/pages/LoginPage";
import { RegisterPage } from "../features/auth/pages/RegisterPage";
import { ForgotPasswordPage } from "../features/auth/pages/ForgotPasswordPage";
import { ResetPasswordPage } from "../features/auth/pages/ResetPasswordPage";
import { SpecialistsListPage } from "../features/specialists/pages/SpecialistsListPage";
import { SpecialistDetailPage } from "../features/specialists/pages/SpecialistDetailPage";
import { AppointmentsPage } from "../features/user/pages/AppointmentsPage";
import { AIChatPage } from "../features/user/pages/AIChatPage";
import { ReportsPage } from "../features/user/pages/ReportsPage";
import { NotificationsPage } from "../features/user/pages/NotificationsPage";
import { SettingsPage } from "../features/user/pages/SettingsPage";
import { SpecialistDashboardPage } from "../features/specialist/pages/DashboardPage";
import { SpecialistAppointmentsPage } from "../features/specialist/pages/AppointmentsPage";
import { SpecialistSchedulePage } from "../features/specialist/pages/SchedulePage";

const router = createBrowserRouter([
  { path: "/", element: <LandingPage /> },
  {
    element: <GuestRoute />,
    children: [
      { path: "/login", element: <LoginPage /> },
      { path: "/register", element: <RegisterPage /> },
      { path: "/forgot-password", element: <ForgotPasswordPage /> },
      { path: "/reset-password", element: <ResetPasswordPage /> },
    ],
  },
  {
    element: <ProtectedRoute />,
    children: [
      { path: "/app", element: <DashboardPage /> },
      { path: "/chat", element: <AIChatPage /> },
      { path: "/specialists", element: <SpecialistsListPage /> },
      { path: "/specialists/:specialistId", element: <SpecialistDetailPage /> },
      { path: "/appointments", element: <AppointmentsPage /> },
      { path: "/reports", element: <ReportsPage /> },
      { path: "/notifications", element: <NotificationsPage /> },
      { path: "/settings", element: <SettingsPage /> },
      { path: "/specialist/dashboard", element: <SpecialistDashboardPage /> },
      { path: "/specialist/appointments", element: <SpecialistAppointmentsPage /> },
      { path: "/specialist/schedule", element: <SpecialistSchedulePage /> },
    ],
  },
  { path: "*", element: <NotFoundPage /> },
]);

export function AppRouter() {
  return <RouterProvider router={router} />;
}
