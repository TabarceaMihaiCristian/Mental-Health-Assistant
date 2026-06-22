import { AuthProvider } from "./auth-provider";
import { AppRouter } from "../routes/AppRouter";

function ensureLandingPageOnInitialOpen() {
  if (typeof window === "undefined") {
    return;
  }

  const { pathname, search, hash } = window.location;
  if (pathname === "/" && search.length === 0 && hash.length === 0) {
    return;
  }

  window.history.replaceState(window.history.state, "", "/");
}

export function App() {
  ensureLandingPageOnInitialOpen();

  return (
    <AuthProvider>
      <AppRouter />
    </AuthProvider>
  );
}
