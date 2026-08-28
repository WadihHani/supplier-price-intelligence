import { createContext, useContext, useEffect, useState } from "react";
import { api, clearToken, getToken, setToken } from "../api/client";
import type { LoginResponse } from "../types/api";

interface AuthContextValue { authenticated: boolean; login: (email: string, password: string) => Promise<void>; logout: () => void; }
const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [authenticated, setAuthenticated] = useState(Boolean(getToken()));
  const logout = () => { clearToken(); setAuthenticated(false); };
  const login = async (email: string, password: string) => {
    const result = await api<LoginResponse>("/api/v1/auth/login", { method: "POST", body: JSON.stringify({ email, password }) });
    setToken(result.access_token); setAuthenticated(true);
  };
  useEffect(() => { window.addEventListener("session-expired", logout); return () => window.removeEventListener("session-expired", logout); }, []);
  return <AuthContext.Provider value={{ authenticated, login, logout }}>{children}</AuthContext.Provider>;
}
export function useAuth() { const value = useContext(AuthContext); if (!value) throw new Error("useAuth must be used within AuthProvider"); return value; }
