import { AuthProvider } from "./auth-provider";
import { AppRouter } from "../routes/AppRouter";

export function App() {
  return (
    <AuthProvider>
      <AppRouter />
    </AuthProvider>
  );
}
