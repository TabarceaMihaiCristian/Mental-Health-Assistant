import { createBrowserRouter, RouterProvider } from "react-router-dom";
import { AdminRoute } from "./AdminRoute";
import { GuestRoute } from "./GuestRoute";
import { NotFoundPage } from "./NotFoundPage";
import { ProtectedRoute } from "./ProtectedRoute";
import { ForgotPasswordPage } from "../features/auth/pages/ForgotPasswordPage";
import { LoginPage } from "../features/auth/pages/LoginPage";
import { RegisterPage } from "../features/auth/pages/RegisterPage";
import { ResetPasswordPage } from "../features/auth/pages/ResetPasswordPage";
import { AdminAppointmentsPage } from "../features/admin/pages/AppointmentsPage";
import { AdminDashboardPage } from "../features/admin/pages/DashboardPage";
import { AdminSpecialistsPage } from "../features/admin/pages/SpecialistsPage";
import { LandingPage } from "../features/public/pages/LandingPage";
import { SpecialistAppointmentsPage } from "../features/specialist/pages/AppointmentsPage";
import { SpecialistDashboardPage } from "../features/specialist/pages/DashboardPage";
import { SpecialistSchedulePage } from "../features/specialist/pages/SchedulePage";
import { SpecialistsListPage } from "../features/specialists/pages/SpecialistsListPage";
import { SpecialistDetailPage } from "../features/specialists/pages/SpecialistDetailPage";
import { AppointmentsPage } from "../features/user/pages/AppointmentsPage";
import { AIChatPage } from "../features/user/pages/AIChatPage";
import { DashboardPage } from "../features/user/pages/DashboardPage";
import { NotificationsPage } from "../features/user/pages/NotificationsPage";
import { ReportsPage } from "../features/user/pages/ReportsPage";
import { SettingsPage } from "../features/user/pages/SettingsPage";

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
      {
        element: <AdminRoute />,
        children: [
          { path: "/admin/dashboard", element: <AdminDashboardPage /> },
          { path: "/admin/specialists", element: <AdminSpecialistsPage /> },
          { path: "/admin/appointments", element: <AdminAppointmentsPage /> },
        ],
      },
    ],
  },
  { path: "*", element: <NotFoundPage /> },
]);

export function AppRouter() {
  return <RouterProvider router={router} />;
}
