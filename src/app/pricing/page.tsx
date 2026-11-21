"use client";

import { useState } from "react";
import { useAuth } from "@/lib/auth-context";
import { api } from "@/lib/api";
import { Navbar } from "@/components/navbar";
import { Footer } from "@/components/footer";
import { Reveal } from "@/components/reveal";
import { Blob } from "@/components/decorations";
import { PRICING_PLANS, formatPrice } from "@/lib/pricing";
import { useRouter } from "next/navigation";

export default function PricingPage() {
  const { isAuthenticated, isSubscribed } = useAuth();
  const router = useRouter();
  const [loadingPlan, setLoadingPlan] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function handleSubscribe(planId: string, priceId: string) {
    if (!isAuthenticated) {
      router.push("/register");
      return;
    }
    if (planId === "trial") {
      router.push("/dashboard");
      return;
    }
    setLoadingPlan(planId);
    setError(null);
    try {
      const { url } = await api.createCheckoutSession(priceId);
      window.location.href = url;
    } catch (err: any) {
      setError(err.detail || "Erreur lors de la redirection vers Stripe.");
    } finally {
      setLoadingPlan(null);
    }
  }

  return (
    <>
      <Navbar />
      <main className="relative pt-32 pb-20 overflow-hidden">
        <Blob className="top-20 -right-20 h-72 w-72" />
        <div className="container-page relative">
          <Reveal className="text-center max-w-2xl mx-auto mb-12">
            <h1 className="text-4xl font-bold sm:text-5xl text-balance">
              Des tarifs <span className="gradient-text">simples</span> et accessibles
            </h1>
            <p className="mt-4 text-ink-600 dark:text-ink-300">
              Commencez gratuitement pendant 7 jours. Sans carte bancaire.
              Choisissez ensuite l'abonnement qui vous convient.
            </p>
          </Reveal>

          {error && (
            <div className="max-w-md mx-auto mb-6 rounded-xl bg-red-50 border border-red-200 px-4 py-3 text-sm text-red-700 dark:bg-red-900/30 dark:border-red-800 dark:text-red-300 text-center">
              {error}
            </div>
          )}

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-5xl mx-auto">
            {PRICING_PLANS.map((plan, i) => (
              <Reveal key={plan.id} delay={i * 100}>
                <div className={`card p-8 h-full flex flex-col relative ${plan.highlighted ? "ring-2 ring-brand-500 shadow-lg" : ""}`}>
                  {plan.highlighted && (
                    <div className="absolute -top-3 left-1/2 -translate-x-1/2">
                      <span className="badge bg-brand-600 text-white">★ Populaire</span>
                    </div>
                  )}
                  <h3 className="font-semibold text-lg">{plan.name}</h3>
                  <div className="mt-4">
                    <span className="text-4xl font-bold">
                      {plan.price === 0 ? "Gratuit" : formatPrice(plan.price)}
                    </span>
                    {plan.price > 0 && (
                      <span className="text-ink-500 text-sm">
                        /{plan.interval === "month" ? "mois" : "an"}
                      </span>
                    )}
                  </div>
                  <ul className="mt-6 space-y-3 flex-1">
                    {plan.features.map((f) => (
                      <li key={f} className="flex items-start gap-2 text-sm text-ink-600 dark:text-ink-400">
                        <span className="text-brand-500 mt-0.5">✓</span>
                        {f}
                      </li>
                    ))}
                  </ul>

                  {isSubscribed && plan.id !== "trial" ? (
                    <button disabled className="btn-secondary mt-8 opacity-60 cursor-default">
                      Abonnement actif ✓
                    </button>
                  ) : (
                    <button
                      onClick={() => handleSubscribe(plan.id, plan.stripe_price_id)}
                      disabled={loadingPlan === plan.id}
                      className={`mt-8 ${plan.highlighted ? "btn-primary" : "btn-secondary"}`}
                    >
                      {loadingPlan === plan.id ? "Redirection…" : plan.price === 0 ? "Commencer gratuitement" : "Choisir ce plan"}
                    </button>
                  )}
                </div>
              </Reveal>
            ))}
          </div>

          {/* FAQ */}
          <Reveal className="mt-20 max-w-3xl mx-auto">
            <h2 className="text-2xl font-bold text-center mb-8">Questions fréquentes</h2>
            <div className="space-y-4">
              {FAQ.map((item) => (
                <details key={item.q} className="card p-5 group">
                  <summary className="font-medium cursor-pointer flex items-center justify-between">
                    {item.q}
                    <span className="text-ink-400 group-open:rotate-180 transition-transform">▼</span>
                  </summary>
                  <p className="mt-3 text-sm text-ink-600 dark:text-ink-400">{item.a}</p>
                </details>
              ))}
            </div>
          </Reveal>
        </div>
      </main>
      <Footer />
    </>
  );
}

const FAQ = [
  { q: "L'essai gratuit nécessite-t-il une carte bancaire ?", a: "Non. L'essai de 7 jours donne accès à toutes les fonctionnalités sans aucune carte. Vous ne serez débité qu'une fois abonné." },
  { q: "Puis-je annuler à tout moment ?", a: "Oui. L'abonnement est sans engagement. Vous pouvez l'annuler depuis votre espace compte ou via le portail Stripe à tout moment." },
  { q: "Tous les niveaux sont-ils couverts ?", a: "Oui, 11 niveaux du 1AM au 3AS (toutes séries) et 11 matières, soit 121 tuteurs IA spécialisés alignés sur le programme algérien." },
  { q: "Comment fonctionne le diagnostic de niveau ?", a: "Un quiz multi-matières analyse vos réponses et détecte automatiquement votre niveau, puis oriente vers le bon tuteur IA." },
];
