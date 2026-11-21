"use client";

import { useState, useEffect } from "react";
import { useAuth } from "@/lib/auth-context";
import { api } from "@/lib/api";
import { Navbar } from "@/components/navbar";
import { useRouter } from "next/navigation";

export default function AccountPage() {
  const { user, isSubscribed, isTrialActive, logout, loading: authLoading } = useAuth();
  const router = useRouter();
  const [portalLoading, setPortalLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!authLoading && !user) router.push("/login");
  }, [authLoading, user, router]);

  if (!user) {
    return (
      <>
        <Navbar />
        <main className="min-h-screen flex items-center justify-center pt-24">
          <div className="inline-block h-10 w-10 animate-spin rounded-full border-4 border-brand-200 border-t-brand-600" />
        </main>
      </>
    );
  }

  const trialEnd = new Date(user.trial_ends_at);
  const trialDaysLeft = Math.max(0, Math.ceil((trialEnd.getTime() - Date.now()) / 86400000));
  const memberSince = new Date(user.created_at).toLocaleDateString("fr-FR");

  async function openPortal() {
    setPortalLoading(true);
    setError(null);
    try {
      const { url } = await api.createPortalSession();
      window.location.href = url;
    } catch (err: any) {
      setError(err.detail || "Impossible d'ouvrir le portail de gestion.");
    } finally {
      setPortalLoading(false);
    }
  }

  const statusBadge = {
    trialing: { label: "Essai gratuit", cls: "bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-300" },
    active: { label: "Abonné", cls: "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-300" },
    past_due: { label: "Paiement en retard", cls: "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-300" },
    canceled: { label: "Annulé", cls: "bg-ink-100 text-ink-600 dark:bg-ink-800 dark:text-ink-300" },
    incomplete: { label: "Incomplet", cls: "bg-ink-100 text-ink-600 dark:bg-ink-800 dark:text-ink-300" },
    trialing_expired: { label: "Essai expiré", cls: "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-300" },
  };
  const badge = statusBadge[user.subscription_status] || statusBadge.incomplete;

  return (
    <>
      <Navbar />
      <main className="min-h-screen pt-24 pb-12 px-4">
        <div className="container-page max-w-3xl">
          <h1 className="text-3xl font-bold mb-2">Mon compte</h1>
          <p className="text-ink-500 mb-8">Gérez votre profil et votre abonnement.</p>

          {error && (
            <div className="mb-6 rounded-xl bg-red-50 border border-red-200 px-4 py-3 text-sm text-red-700 dark:bg-red-900/30 dark:border-red-800 dark:text-red-300">
              {error}
            </div>
          )}

          {/* Profile card */}
          <div className="card p-6 mb-6">
            <h2 className="font-semibold text-lg mb-4">Profil</h2>
            <div className="space-y-3">
              <div className="flex justify-between items-center py-2 border-b border-ink-100 dark:border-ink-700">
                <span className="text-sm text-ink-500">Email</span>
                <span className="text-sm font-medium">{user.email}</span>
              </div>
              <div className="flex justify-between items-center py-2 border-b border-ink-100 dark:border-ink-700">
                <span className="text-sm text-ink-500">Niveau détecté</span>
                <span className="text-sm font-medium">{user.detected_level?.name || "Non détecté"}</span>
              </div>
              <div className="flex justify-between items-center py-2 border-b border-ink-100 dark:border-ink-700">
                <span className="text-sm text-ink-500">Membre depuis</span>
                <span className="text-sm font-medium">{memberSince}</span>
              </div>
              <div className="flex justify-between items-center py-2">
                <span className="text-sm text-ink-500">Dernière activité</span>
                <span className="text-sm font-medium">{new Date(user.last_active_at).toLocaleDateString("fr-FR")}</span>
              </div>
            </div>
          </div>

          {/* Subscription card */}
          <div className="card p-6 mb-6">
            <h2 className="font-semibold text-lg mb-4">Abonnement</h2>
            <div className="flex items-center gap-3 mb-4">
              <span className={`badge ${badge.cls}`}>{badge.label}</span>
              {isSubscribed && <span className="text-sm text-green-600">✓ Accès complet</span>}
            </div>

            {!isSubscribed && isTrialActive && (
              <div className="rounded-xl bg-amber-50 dark:bg-amber-900/20 p-4 mb-4">
                <p className="text-sm text-amber-700 dark:text-amber-300">
                  ⏰ Il vous reste <strong>{trialDaysLeft} jour{trialDaysLeft > 1 ? "s" : ""}</strong> d'essai gratuit.
                </p>
                <p className="text-xs text-amber-600 dark:text-amber-400 mt-1">
                  Fin de l'essai : {trialEnd.toLocaleDateString("fr-FR")}
                </p>
              </div>
            )}

            {!isSubscribed && !isTrialActive && (
              <div className="rounded-xl bg-red-50 dark:bg-red-900/20 p-4 mb-4">
                <p className="text-sm text-red-700 dark:text-red-300">
                  ⏰ Votre essai est terminé. Abonnez-vous pour continuer à accéder aux 121 tuteurs.
                </p>
              </div>
            )}

            <div className="flex flex-wrap gap-3">
              {!isSubscribed && (
                <a href="/pricing" className="btn-primary">Voir les offres →</a>
              )}
              {isSubscribed && user.stripe_subscription_id && (
                <button onClick={openPortal} disabled={portalLoading} className="btn-secondary">
                  {portalLoading ? "Ouverture…" : "Gérer l'abonnement (Stripe)"}
                </button>
              )}
              <button onClick={() => { logout(); }} className="btn-ghost">Se déconnecter</button>
            </div>
          </div>

          {/* Danger zone */}
          <div className="card p-6 border-red-200 dark:border-red-900/50">
            <h2 className="font-semibold text-lg mb-2 text-red-600">Zone sensible</h2>
            <p className="text-sm text-ink-500 mb-4">
              La suppression de compte est irréversible. Contactez le support pour toute demande.
            </p>
            <a href="mailto:contact@oupsii.app" className="btn-ghost text-red-600">Contacter le support</a>
          </div>
        </div>
      </main>
    </>
  );
}
