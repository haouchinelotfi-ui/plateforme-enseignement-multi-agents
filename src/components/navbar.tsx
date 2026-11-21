"use client";

import Link from "next/link";
import { useState, useEffect } from "react";
import { useAuth } from "@/lib/auth-context";
import { useTheme } from "@/lib/theme-provider";

export function Navbar() {
  const { isAuthenticated, user, logout } = useAuth();
  const { theme, toggle } = useTheme();
  const [scrolled, setScrolled] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 20);
    window.addEventListener("scroll", onScroll);
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  return (
    <header
      className={`fixed top-0 inset-x-0 z-50 transition-all duration-300 ${
        scrolled ? "glass shadow-sm py-2" : "bg-transparent py-4"
      }`}
    >
      <nav className="container-page flex items-center justify-between">
        <Link href="/" className="flex items-center gap-2 font-bold text-lg">
          <span className="inline-flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-brand-500 to-brand-700 text-white shadow-md">
            O
          </span>
          <span className="gradient-text">Oupsii</span>
        </Link>

        {/* Desktop */}
        <div className="hidden md:flex items-center gap-6">
          <Link href="/#features" className="text-sm font-medium text-ink-600 hover:text-brand-600 transition dark:text-ink-300">
            Fonctionnalités
          </Link>
          <Link href="/pricing" className="text-sm font-medium text-ink-600 hover:text-brand-600 transition dark:text-ink-300">
            Tarifs
          </Link>
          {isAuthenticated ? (
            <>
              <Link href="/dashboard" className="text-sm font-medium text-ink-600 hover:text-brand-600 transition dark:text-ink-300">
                Tableau de bord
              </Link>
              <button onClick={toggle} className="btn-ghost px-2" aria-label="Thème">
                {theme === "light" ? "🌙" : "☀️"}
              </button>
              <button onClick={logout} className="btn-ghost">
                Déconnexion
              </button>
            </>
          ) : (
            <>
              <button onClick={toggle} className="btn-ghost px-2" aria-label="Thème">
                {theme === "light" ? "🌙" : "☀️"}
              </button>
              <Link href="/login" className="btn-ghost">
                Connexion
              </Link>
              <Link href="/register" className="btn-primary">
                Essai gratuit
              </Link>
            </>
          )}
        </div>

        {/* Mobile toggle */}
        <button
          className="md:hidden btn-ghost px-2"
          onClick={() => setMenuOpen(!menuOpen)}
          aria-label="Menu"
        >
          {menuOpen ? "✕" : "☰"}
        </button>
      </nav>

      {/* Mobile menu */}
      {menuOpen && (
        <div className="md:hidden container-page mt-2 animate-slide-down">
          <div className="card flex flex-col gap-2 p-4">
            <Link href="/#features" onClick={() => setMenuOpen(false)} className="btn-ghost justify-start">Fonctionnalités</Link>
            <Link href="/pricing" onClick={() => setMenuOpen(false)} className="btn-ghost justify-start">Tarifs</Link>
            {isAuthenticated ? (
              <>
                <Link href="/dashboard" onClick={() => setMenuOpen(false)} className="btn-ghost justify-start">Tableau de bord</Link>
                <button onClick={() => { logout(); setMenuOpen(false); }} className="btn-ghost justify-start">Déconnexion</button>
              </>
            ) : (
              <>
                <Link href="/login" onClick={() => setMenuOpen(false)} className="btn-ghost justify-start">Connexion</Link>
                <Link href="/register" onClick={() => setMenuOpen(false)} className="btn-primary">Essai gratuit</Link>
              </>
            )}
          </div>
        </div>
      )}
    </header>
  );
}
