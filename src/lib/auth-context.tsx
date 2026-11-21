"use client";

import { createContext, useContext, useState, useEffect, useCallback, useMemo, ReactNode } from "react";
import { useRouter } from "next/navigation";
import { api } from "./api";
import type { User } from "./types";

interface AuthContextValue {
  user: User | null;
  loading: boolean;
  isAuthenticated: boolean;
  isTrialActive: boolean;
  isSubscribed: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string) => Promise<void>;
  logout: () => void;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  const refreshUser = useCallback(async () => {
    try {
      const me = await api.me();
      setUser(me);
    } catch {
      setUser(null);
    }
  }, []);

  useEffect(() => {
    // Hydrate from localStorage token
    const token = typeof window !== "undefined" ? localStorage.getItem("oupsii_token") : null;
    if (!token) {
      setLoading(false);
      return;
    }
    refreshUser().finally(() => setLoading(false));
  }, [refreshUser]);

  const login = useCallback(async (email: string, password: string) => {
    const u = await api.login(email, password);
    setUser(u);
  }, []);

  const register = useCallback(async (email: string, password: string) => {
    const u = await api.register(email, password);
    setUser(u);
  }, []);

  const logout = useCallback(() => {
    api.logout();
    setUser(null);
    router.push("/");
  }, [router]);

  const isTrialActive = useMemo(() => {
    if (!user) return false;
    return new Date(user.trial_ends_at) > new Date();
  }, [user]);

  const isSubscribed = user?.subscription_status === "active" || user?.subscription_status === "trialing";

  return (
    <AuthContext.Provider
      value={{ user, loading, isAuthenticated: !!user, isTrialActive, isSubscribed, login, register, logout, refreshUser }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
