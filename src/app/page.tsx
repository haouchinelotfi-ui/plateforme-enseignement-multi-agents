import Link from "next/link";
import { Navbar } from "@/components/navbar";
import { Footer } from "@/components/footer";
import { Reveal } from "@/components/reveal";
import { Blob, GridBackground } from "@/components/decorations";
import { PRICING_PLANS, formatPrice } from "@/lib/pricing";

export default function HomePage() {
  return (
    <>
      <Navbar />
      <main>
        {/* ============ HERO ============ */}
        <section className="relative overflow-hidden pt-32 pb-20 sm:pt-40 sm:pb-28">
          <GridBackground />
          <Blob className="top-10 -left-20 h-72 w-72" />
          <Blob className="bottom-0 -right-20 h-96 w-96" />

          <div className="container-page relative">
            <div className="mx-auto max-w-4xl text-center">
              <div className="animate-fade-in inline-flex items-center gap-2 rounded-full border border-brand-200 bg-brand-50 px-4 py-1.5 text-sm font-medium text-brand-700 dark:border-brand-800 dark:bg-brand-900/30 dark:text-brand-300">
                <span className="relative flex h-2 w-2">
                  <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-brand-500 opacity-75" />
                  <span className="relative inline-flex h-2 w-2 rounded-full bg-brand-600" />
                </span>
                121 tuteurs IA spécialisés · Essai gratuit 7 jours
              </div>

              <h1 className="mt-6 text-4xl font-bold tracking-tight text-balance sm:text-6xl animate-fade-up">
                Un tuteur personnel pour <span className="gradient-text">chaque matière</span>,
                <br className="hidden sm:block" /> du CEM au Lycée.
              </h1>

              <p className="mt-6 text-lg text-ink-600 dark:text-ink-300 text-pretty max-w-2xl mx-auto animate-fade-up animate-delay-100">
                Oupsii déploie 121 agents IA spécialisés par niveau et matière, alignés sur le
                programme officiel algérien. Diagnostic de niveau, accompagnement personnalisé,
                suivi de progression — sans carte bancaire.
              </p>

              <div className="mt-10 flex flex-col sm:flex-row items-center justify-center gap-4 animate-fade-up animate-delay-200">
                <Link href="/register" className="btn-primary text-base px-8 py-4">
                  Commencer l'essai gratuit
                  <span className="animate-bounce-subtle">→</span>
                </Link>
                <Link href="/#features" className="btn-secondary text-base px-8 py-4">
                  Découvrir comment
                </Link>
              </div>

              <p className="mt-6 text-sm text-ink-500 animate-fade-up animate-delay-300">
                ⚡ Setup en 2 minutes · 🎓 Tous niveaux (1AM → 3AS) · 🔒 Sans engagement
              </p>
            </div>

            {/* Stats band */}
            <Reveal className="mt-20" delay={400}>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {[
                  { v: "121", l: "Agents spécialisés" },
                  { v: "11", l: "Niveaux couverts" },
                  { v: "11", l: "Matières" },
                  { v: "7j", l: "Essai gratuit" },
                ].map((s) => (
                  <div key={s.l} className="card p-6 text-center">
                    <div className="text-3xl font-bold gradient-text">{s.v}</div>
                    <div className="mt-1 text-sm text-ink-600 dark:text-ink-400">{s.l}</div>
                  </div>
                ))}
              </div>
            </Reveal>
          </div>
        </section>

        {/* ============ FEATURES ============ */}
        <section id="features" className="py-20 sm:py-28">
          <div className="container-page">
            <Reveal className="mx-auto max-w-2xl text-center mb-16">
              <h2 className="text-3xl font-bold sm:text-4xl text-balance">
                Une plateforme pensée pour la <span className="gradient-text">réussite</span>
              </h2>
              <p className="mt-4 text-ink-600 dark:text-ink-300">
                Chaque fonctionnalité est conçue pour réduire l'écart entre l'élève et l'excellence.
              </p>
            </Reveal>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {FEATURES.map((f, i) => (
                <Reveal key={f.title} delay={i * 100}>
                  <div className="card p-6 h-full hover:shadow-md transition-shadow group">
                    <div className="inline-flex h-12 w-12 items-center justify-center rounded-xl bg-brand-50 text-2xl dark:bg-brand-900/30 group-hover:scale-110 transition-transform">
                      {f.icon}
                    </div>
                    <h3 className="mt-4 font-semibold text-lg">{f.title}</h3>
                    <p className="mt-2 text-sm text-ink-600 dark:text-ink-400">{f.desc}</p>
                  </div>
                </Reveal>
              ))}
            </div>
          </div>
        </section>

        {/* ============ HOW IT WORKS ============ */}
        <section className="py-20 sm:py-28 bg-ink-50/50 dark:bg-ink-900/50">
          <div className="container-page">
            <Reveal className="mx-auto max-w-2xl text-center mb-16">
              <h2 className="text-3xl font-bold sm:text-4xl">
                Comment ça <span className="gradient-text">marche</span>
              </h2>
            </Reveal>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              {STEPS.map((s, i) => (
                <Reveal key={s.title} delay={i * 150}>
                  <div className="relative">
                    <div className="absolute -top-4 -left-2 text-6xl font-bold text-brand-100 dark:text-brand-900/40">
                      {i + 1}
                    </div>
                    <div className="card p-6 pt-8 relative z-10">
                      <div className="text-3xl mb-3">{s.icon}</div>
                      <h3 className="font-semibold text-lg">{s.title}</h3>
                      <p className="mt-2 text-sm text-ink-600 dark:text-ink-400">{s.desc}</p>
                    </div>
                  </div>
                </Reveal>
              ))}
            </div>
          </div>
        </section>

        {/* ============ PRICING TEASER ============ */}
        <section className="py-20 sm:py-28">
          <div className="container-page">
            <Reveal className="mx-auto max-w-2xl text-center mb-16">
              <h2 className="text-3xl font-bold sm:text-4xl">
                Des tarifs <span className="gradient-text">accessibles</span>
              </h2>
              <p className="mt-4 text-ink-600 dark:text-ink-300">
                Commence gratuitement pendant 7 jours. Sans carte bancaire.
              </p>
            </Reveal>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-5xl mx-auto">
              {PRICING_PLANS.map((plan, i) => (
                <Reveal key={plan.id} delay={i * 100}>
                  <div className={`card p-8 h-full flex flex-col ${plan.highlighted ? "ring-2 ring-brand-500 shadow-lg" : ""}`}>
                    {plan.highlighted && (
                      <div className="absolute -top-3 left-1/2 -translate-x-1/2">
                        <span className="badge-brand bg-brand-600 text-white">★ Populaire</span>
                      </div>
                    )}
                    <h3 className="font-semibold text-lg">{plan.name}</h3>
                    <div className="mt-4">
                      <span className="text-4xl font-bold">{plan.price === 0 ? "Gratuit" : formatPrice(plan.price)}</span>
                      {plan.price > 0 && (
                        <span className="text-ink-500 text-sm">/{plan.interval === "month" ? "mois" : "an"}</span>
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
                    <Link
                      href={plan.price === 0 ? "/register" : "/register"}
                      className={`mt-8 ${plan.highlighted ? "btn-primary" : "btn-secondary"}`}
                    >
                      {plan.price === 0 ? "Commencer" : "Choisir"}
                    </Link>
                  </div>
                </Reveal>
              ))}
            </div>
          </div>
        </section>

        {/* ============ CTA ============ */}
        <section className="py-20 sm:py-28">
          <div className="container-page">
            <Reveal>
              <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-brand-600 to-brand-800 px-8 py-16 text-center shadow-xl">
                <Blob className="top-0 right-0 h-48 w-48 opacity-30" />
                <Blob className="bottom-0 left-0 h-64 w-64 opacity-20" />
                <div className="relative">
                  <h2 className="text-3xl font-bold text-white sm:text-4xl text-balance">
                    Prêt à transformer votre apprentissage ?
                  </h2>
                  <p className="mt-4 text-brand-100 max-w-xl mx-auto">
                    Rejoignez les élèves qui progressent avec un tuteur IA dédié à chaque matière.
                  </p>
                  <Link
                    href="/register"
                    className="mt-8 inline-flex items-center justify-center gap-2 rounded-xl bg-white px-8 py-4 text-base font-semibold text-brand-700 shadow-lg hover:shadow-xl transition-all hover:scale-105"
                  >
                    Démarrer l'essai gratuit de 7 jours →
                  </Link>
                </div>
              </div>
            </Reveal>
          </div>
        </section>
      </main>
      <Footer />
    </>
  );
}

const FEATURES = [
  { icon: "🤖", title: "121 agents spécialisés", desc: "Un tuteur IA expert par combinaison niveau × matière, du 1AM au 3AS, aligné sur le programme algérien." },
  { icon: "🎯", title: "Diagnostic de niveau", desc: "Un quiz multi-matières détecte automatiquement le niveau de l'élève et oriente vers le bon agent." },
  { icon: "💬", title: "Chat conversationnel", desc: "Interface de discussion naturelle avec l'agent, exercices progressifs et vérification de compréhension." },
  { icon: "📊", title: "Suivi de progression", desc: "Télémétrie d'usage, tokens consommés, latence et feedback élève pour un pilotage qualité." },
  { icon: "🔒", title: "Essai sans carte", desc: "7 jours d'accès complet sans carte bancaire. Abonnement mensuel ou annuel ensuite, annulable à tout moment." },
  { icon: "⚡", title: "Cache-Aside Redis", desc: "Routeur centralisé avec cache Redis pour des réponses rapides et une scalabilité à 10 000+ élèves." },
];

const STEPS = [
  { icon: "📝", title: "Inscription & diagnostic", desc: "Créez un compte en 2 minutes, puis passez le quiz de niveau qui détecte automatiquement votre classe." },
  { icon: "🎯", title: "Agent personnalisé", desc: "Oupsii sélectionne le tuteur IA adapté à votre niveau et à la matière que vous voulez travailler." },
  { icon: "🚀", title: "Progressez", desc: "Discutez, posez des questions, faites des exercices. L'agent s'adapte et vous accompagne jusqu'à l'excellence." },
];
