"use client";

import { createContext, useContext, useEffect, useState, ReactNode } from "react";

type Theme = "light" | "dark";

interface ThemeContextValue {
  theme: Theme;
  toggle: () => void;
  setTheme: (t: Theme) => void;
}

const ThemeContext = createContext<ThemeContextValue | undefined>(undefined);

export function ThemeProvider({ children }: { children: ReactNode }) {
  const [theme, setThemeState] = useState<Theme>("light");

  useEffect(() => {
    const stored = localStorage.getItem("oupsii_theme") as Theme | null;
    const prefers = window.matchMedia("(prefers-color-scheme: dark)").matches;
    const t = stored || (prefers ? "dark" : "light");
    setThemeState(t);
    document.documentElement.classList.toggle("dark", t === "dark");
  }, []);

  const setTheme = (t: Theme) => {
    setThemeState(t);
    localStorage.setItem("oupsii_theme", t);
    document.documentElement.classList.toggle("dark", t === "dark");
  };

  const toggle = () => setTheme(theme === "light" ? "dark" : "light");

  return <ThemeContext.Provider value={{ theme, toggle, setTheme }}>{children}</ThemeContext.Provider>;
}

export function useTheme() {
  const ctx = useContext(ThemeContext);
  if (!ctx) throw new Error("useTheme must be used within ThemeProvider");
  return ctx;
}
