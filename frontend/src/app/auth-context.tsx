import { createContext } from "react";
import type { LoginPayload, RegisterPayload, User } from "../types/auth";

export type AuthStatus = "loading" | "authenticated" | "anonymous";

export interface AuthState {
  token: string | null;
  user: User | null;
  status: AuthStatus;
  loginWithPassword: (payload: LoginPayload) => Promise<void>;
  registerWithPassword: (payload: RegisterPayload) => Promise<void>;
  logout: () => void;
  refreshUser: () => Promise<void>;
}

export const AuthContext = createContext<AuthState | undefined>(undefined);
