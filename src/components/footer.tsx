import Link from "next/link";

export function Footer() {
  return (
    <footer className="border-t border-ink-100 dark:border-ink-800 bg-ink-50/50 dark:bg-ink-900">
      <div className="container-page py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          <div className="md:col-span-2">
            <div className="flex items-center gap-2 font-bold text-lg mb-3">
              <span className="inline-flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-brand-500 to-brand-700 text-white">
                O
              </span>
              <span className="gradient-text">Oupsii</span>
            </div>
            <p className="text-sm text-ink-600 dark:text-ink-400 max-w-sm">
              La plateforme d'enseignement multi-agents qui accompagne chaque élève
              du CEM au Lycée avec 121 tuteurs IA spécialisés par niveau et matière.
            </p>
          </div>

          <div>
            <h4 className="font-semibold mb-3 text-sm">Produit</h4>
            <ul className="space-y-2 text-sm text-ink-600 dark:text-ink-400">
              <li><Link href="/#features" className="hover:text-brand-600">Fonctionnalités</Link></li>
              <li><Link href="/pricing" className="hover:text-brand-600">Tarifs</Link></li>
              <li><Link href="/register" className="hover:text-brand-600">Essai gratuit</Link></li>
              <li><Link href="/dashboard" className="hover:text-brand-600">Tableau de bord</Link></li>
            </ul>
          </div>

          <div>
            <h4 className="font-semibold mb-3 text-sm">Support</h4>
            <ul className="space-y-2 text-sm text-ink-600 dark:text-ink-400">
              <li><Link href="/account" className="hover:text-brand-600">Mon compte</Link></li>
              <li><a href="mailto:contact@oupsii.app" className="hover:text-brand-600">Contact</a></li>
              <li><Link href="/#faq" className="hover:text-brand-600">FAQ</Link></li>
            </ul>
          </div>
        </div>

        <div className="mt-10 pt-6 border-t border-ink-100 dark:border-ink-800 flex flex-col sm:flex-row justify-between gap-4 text-xs text-ink-500">
          <p>© {new Date().getFullYear()} Oupsii. Tous droits réservés.</p>
          <p>Fait avec ❤️ pour les élèves algériens</p>
        </div>
      </div>
    </footer>
  );
}
