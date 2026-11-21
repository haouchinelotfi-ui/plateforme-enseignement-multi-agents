"use client";

import { useState, FormEvent } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth-context";
import { Navbar } from "@/components/navbar";

export default function LoginPage() {
  const { login } = useAuth();
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await login(email, password);
      router.push("/dashboard");
    } catch (err: any) {
      setError(err.detail || "Email ou mot de passe incorrect.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <>
      <Navbar />
      <main className="min-h-screen flex items-center justify-center pt-24 pb-12 px-4">
        <div className="w-full max-w-md">
          <div className="text-center mb-8 animate-fade-up">
            <h1 className="text-3xl font-bold">Bon retour 👋</h1>
            <p className="mt-2 text-ink-600 dark:text-ink-400">
              Connectez-vous pour reprendre votre apprentissage
            </p>
          </div>

          <form onSubmit={handleSubmit} className="card p-8 animate-fade-up animate-delay-100">
            {error && (
              <div className="mb-4 rounded-xl bg-red-50 border border-red-200 px-4 py-3 text-sm text-red-700 dark:bg-red-900/30 dark:border-red-800 dark:text-red-300 animate-slide-down">
                {error}
              </div>
            )}

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-1.5">Email</label>
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="input"
                  placeholder="eleve@exemple.com"
                  autoComplete="email"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-1.5">Mot de passe</label>
                <input
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="input"
                  placeholder="••••••••"
                  autoComplete="current-password"
                />
              </div>
            </div>

            <button type="submit" disabled={loading} className="btn-primary w-full mt-6">
              {loading ? "Connexion…" : "Se connecter →"}
            </button>

            <p className="mt-4 text-center text-sm text-ink-500">
              Pas encore de compte ?{" "}
              <Link href="/register" className="text-brand-600 font-medium hover:underline">
                Essai gratuit 7 jours
              </Link>
            </p>
          </form>
        </div>
      </main>
    </>
  );
}
