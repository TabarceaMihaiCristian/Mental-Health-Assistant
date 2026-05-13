import { useCallback, useEffect, useMemo, useState, type ReactNode } from "react";
import { getMe, login, register } from "../features/auth/authApi";
import { persistAuth, readStoredAuth } from "../lib/auth-storage";
import type { AuthResponse, LoginPayload, RegisterPayload, User } from "../types/auth";
import { AuthContext, type AuthState, type AuthStatus } from "./auth-context";

function readInitialAuthState(): {
  token: string | null;
  user: User | null;
  status: AuthStatus;
} {
  const stored = readStoredAuth();

  if (!stored) {
    return {
      token: null,
      user: null,
      status: "anonymous",
    };
  }

  return {
    token: stored.access_token,
    user: stored.user,
    status: "authenticated",
  };
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [initialState] = useState(readInitialAuthState);
  const [token, setToken] = useState<string | null>(initialState.token);
  const [user, setUser] = useState<User | null>(initialState.user);
  const [status, setStatus] = useState<AuthStatus>(initialState.status);

  const clearAuth = useCallback(() => {
    persistAuth(null);
    setToken(null);
    setUser(null);
    setStatus("anonymous");
  }, []);

  const applyAuth = useCallback((result: AuthResponse) => {
    persistAuth(result);
    setToken(result.access_token);
    setUser(result.user);
    setStatus("authenticated");
  }, []);

  const refreshUser = useCallback(async () => {
    const stored = readStoredAuth();
    const nextToken = token ?? stored?.access_token ?? null;

    if (!nextToken) {
      clearAuth();
      return;
    }

    const nextUser = await getMe(nextToken);
    setToken(nextToken);
    setUser(nextUser);
    setStatus("authenticated");

    if (stored) {
      persistAuth({ ...stored, access_token: nextToken, user: nextUser });
    }
  }, [clearAuth, token]);

  useEffect(() => {
    if (!token) {
      return;
    }

    void getMe(token)
      .then((nextUser) => {
        setUser(nextUser);
        const stored = readStoredAuth();
        if (stored) {
          persistAuth({ ...stored, access_token: token, user: nextUser });
        }
      })
      .catch(() => {
        clearAuth();
      });
  }, [clearAuth, token]);

  const loginWithPassword = useCallback(
    async (payload: LoginPayload) => {
      const result = await login(payload);
      applyAuth(result);
    },
    [applyAuth],
  );

  const registerWithPassword = useCallback(
    async (payload: RegisterPayload) => {
      const result = await register(payload);
      applyAuth(result);
    },
    [applyAuth],
  );

  const value = useMemo<AuthState>(
    () => ({ token, user, status, loginWithPassword, registerWithPassword, logout: clearAuth, refreshUser }),
    [token, user, status, loginWithPassword, registerWithPassword, clearAuth, refreshUser],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
