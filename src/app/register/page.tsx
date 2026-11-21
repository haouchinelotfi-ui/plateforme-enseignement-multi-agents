"use client";

import { useState, FormEvent } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth-context";
import { Navbar } from "@/components/navbar";

export default function RegisterPage() {
  const { register } = useAuth();
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    if (password !== confirm) {
      setError("Les mots de passe ne correspondent pas.");
      return;
    }
    if (password.length < 6) {
      setError("Le mot de passe doit contenir au moins 6 caractères.");
      return;
    }
    setLoading(true);
    try {
      await register(email, password);
      // Redirect to quiz diagnostic after registration
      router.push("/quiz");
    } catch (err: any) {
      setError(err.detail || "Erreur lors de l'inscription.");
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
            <h1 className="text-3xl font-bold">Créer un compte</h1>
            <p className="mt-2 text-ink-600 dark:text-ink-400">
              Essai gratuit de 7 jours · sans carte bancaire
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
                  autoComplete="new-password"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-1.5">Confirmer le mot de passe</label>
                <input
                  type="password"
                  required
                  value={confirm}
                  onChange={(e) => setConfirm(e.target.value)}
                  className="input"
                  placeholder="••••••••"
                  autoComplete="new-password"
                />
              </div>
            </div>

            <button type="submit" disabled={loading} className="btn-primary w-full mt-6">
              {loading ? "Création…" : "Créer mon compte →"}
            </button>

            <p className="mt-4 text-center text-sm text-ink-500">
              Déjà un compte ?{" "}
              <Link href="/login" className="text-brand-600 font-medium hover:underline">
                Se connecter
              </Link>
            </p>
          </form>

          <p className="mt-6 text-center text-xs text-ink-500">
            En créant un compte, vous acceptez nos conditions d'utilisation.
            Votre essai de 7 jours commence immédiatement.
          </p>
        </div>
      </main>
    </>
  );
}
