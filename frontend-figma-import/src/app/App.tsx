import { useState } from "react";
import { Toaster } from "./components/ui/Toast";

// Design System
import DesignSystem from "./screens/DesignSystem";

// Landing & Auth
import LandingPage from "./screens/LandingPage";
import Login from "./screens/auth/Login";
import Register from "./screens/auth/Register";
import ForgotPassword from "./screens/auth/ForgotPassword";
import ResetPassword from "./screens/auth/ResetPassword";

// User Screens
import UserDashboard from "./screens/user/Dashboard";
import SpecialistDirectory from "./screens/user/SpecialistDirectory";
import AIChat from "./screens/user/AIChat";
import Appointments from "./screens/user/Appointments";

// Specialist Screens
import SpecialistDashboard from "./screens/specialist/Dashboard";

export default function App() {
  const [currentScreen, setCurrentScreen] = useState("sitemap");

  const screens = {
    // Core
    sitemap: <Sitemap onNavigate={setCurrentScreen} />,
    designSystem: <DesignSystem />,

    // Landing & Auth
    landing: <LandingPage />,
    login: <Login />,
    register: <Register />,
    forgotPassword: <ForgotPassword />,
    resetPassword: <ResetPassword />,

    // User
    userDashboard: <UserDashboard />,
    specialists: <SpecialistDirectory />,
    chat: <AIChat />,
    appointments: <Appointments />,

    // Specialist
    specialistDashboard: <SpecialistDashboard />,
  };

  return (
    <>
      {screens[currentScreen as keyof typeof screens]}
      <Toaster />
    </>
  );
}

function Sitemap({ onNavigate }: { onNavigate: (screen: string) => void }) {
  const sections = [
    {
      title: "Design System",
      items: [
        { name: "Design System", id: "designSystem" },
      ],
    },
    {
      title: "Public & Authentication",
      items: [
        { name: "Landing Page", id: "landing" },
        { name: "Login", id: "login" },
        { name: "Register", id: "register" },
        { name: "Forgot Password", id: "forgotPassword" },
        { name: "Reset Password", id: "resetPassword" },
      ],
    },
    {
      title: "User Role",
      items: [
        { name: "User Dashboard", id: "userDashboard" },
        { name: "Specialist Directory", id: "specialists" },
        { name: "AI Chat", id: "chat" },
        { name: "User Appointments", id: "appointments" },
      ],
    },
    {
      title: "Specialist Role",
      items: [
        { name: "Specialist Dashboard", id: "specialistDashboard" },
      ],
    },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-[--sand-50] to-[--teal-50] p-8">
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-12">
          <h1 className="text-5xl font-[--font-weight-semibold] text-[--foreground] mb-4">
            Mental Health Assistant
          </h1>
          <p className="text-xl text-[--muted-foreground] mb-2">
            Complete UI/UX Design System & Application
          </p>
          <p className="text-[--muted-foreground]">
            A serious, premium, calm healthcare-tech product
          </p>
        </div>

        <div className="grid md:grid-cols-2 gap-8">
          {sections.map((section) => (
            <div
              key={section.title}
              className="bg-[--card] rounded-[--radius-xl] shadow-[--shadow-lg] border border-[--border] p-6"
            >
              <h2 className="text-2xl font-[--font-weight-semibold] text-[--foreground] mb-4 pb-4 border-b border-[--border]">
                {section.title}
              </h2>
              <div className="space-y-2">
                {section.items.map((item) => (
                  <button
                    key={item.id}
                    onClick={() => onNavigate(item.id)}
                    className="w-full text-left px-4 py-3 rounded-[--radius-lg] hover:bg-[--accent] transition-colors text-[--foreground] font-[--font-weight-medium]"
                  >
                    {item.name}
                  </button>
                ))}
              </div>
            </div>
          ))}
        </div>

        <div className="mt-12 p-8 bg-[--card] rounded-[--radius-xl] shadow-[--shadow-lg] border border-[--border]">
          <h2 className="text-2xl font-[--font-weight-semibold] text-[--foreground] mb-4">
            Design Principles
          </h2>
          <div className="grid md:grid-cols-3 gap-6">
            <div>
              <h3 className="font-[--font-weight-semibold] text-[--foreground] mb-2">
                Color System
              </h3>
              <ul className="text-sm text-[--muted-foreground] space-y-1">
                <li>• Deep Teal - Primary</li>
                <li>• Muted Slate - Neutral/Text</li>
                <li>• Warm Sand - Backgrounds</li>
                <li>• Soft Sage - Success/Calm</li>
                <li>• Alert Red - Danger/Urgent</li>
                <li>• Warning Amber - Warnings</li>
              </ul>
            </div>
            <div>
              <h3 className="font-[--font-weight-semibold] text-[--foreground] mb-2">
                Design Language
              </h3>
              <ul className="text-sm text-[--muted-foreground] space-y-1">
                <li>• Soft gradients & subtle shadows</li>
                <li>• Strong visual hierarchy</li>
                <li>• Generous spacing</li>
                <li>• Rounded corners (not playful)</li>
                <li>• Crisp, clinical charts</li>
                <li>• Intentional typography</li>
              </ul>
            </div>
            <div>
              <h3 className="font-[--font-weight-semibold] text-[--foreground] mb-2">
                UX Goals
              </h3>
              <ul className="text-sm text-[--muted-foreground] space-y-1">
                <li>• Emotionally safe & easy to use</li>
                <li>• Reduce friction in booking care</li>
                <li>• Supportive AI chat experience</li>
                <li>• Professional specialist tools</li>
                <li>• Clear operational admin tools</li>
              </ul>
            </div>
          </div>
        </div>

        <div className="mt-8 p-6 bg-[--teal-700] text-white rounded-[--radius-xl] shadow-[--shadow-lg]">
          <h3 className="font-[--font-weight-semibold] mb-2">Complete Feature Set</h3>
          <div className="grid md:grid-cols-2 gap-4 text-sm">
            <ul className="space-y-1">
              <li>✓ Design system with all components</li>
              <li>✓ Landing page with full marketing content</li>
              <li>✓ Authentication flows (login, register, password reset)</li>
              <li>✓ User dashboard with risk state & mood tracking</li>
              <li>✓ Specialist directory with search & filters</li>
              <li>✓ AI chat with risk escalation</li>
            </ul>
            <ul className="space-y-1">
              <li>✓ Appointment management (book, reschedule, cancel)</li>
              <li>✓ Specialist dashboard with today's schedule</li>
              <li>✓ Status badges (appointment, risk levels)</li>
              <li>✓ Empty, loading, success, error states</li>
              <li>✓ Responsive layouts for desktop, tablet, mobile</li>
              <li>✓ Professional, trustworthy healthcare aesthetic</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
