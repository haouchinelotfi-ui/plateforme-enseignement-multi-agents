import type { PricingPlan } from "./types";

// Plans de pricing — les price_id Stripe sont renseignés via env vars côté backend
export const PRICING_PLANS: PricingPlan[] = [
  {
    id: "trial",
    name: "Essai gratuit",
    price: 0,
    interval: "month",
    stripe_price_id: "",
    features: [
      "7 jours d'accès complet",
      "121 tuteurs IA spécialisés",
      "Diagnostic de niveau personnalisé",
      "Chat illimité avec les agents",
      "Sans carte bancaire",
    ],
  },
  {
    id: "monthly",
    name: "Mensuel",
    price: 1200,
    interval: "month",
    stripe_price_id: "STRIPE_PRICE_ID_MONTHLY",
    highlighted: true,
    features: [
      "Accès complet aux 121 agents",
      "Chat illimité",
      "Suivi de progression",
      "Support prioritaire",
      "Annulation à tout moment",
    ],
  },
  {
    id: "yearly",
    name: "Annuel",
    price: 9900,
    interval: "year",
    stripe_price_id: "STRIPE_PRICE_ID_YEARLY",
    features: [
      "Tout le plan mensuel",
      "2 mois offerts (-18%)",
      "Rapport de progression trimestriel",
      "Accès anticipé aux nouveautés",
      "Support dédié",
    ],
  },
];

export function formatPrice(cents: number): string {
  return new Intl.NumberFormat("fr-DZ", { style: "currency", currency: "DZD", maximumFractionDigits: 0 }).format(cents);
}
