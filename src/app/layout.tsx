import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { AuthProvider } from "@/lib/auth-context";
import { ThemeProvider } from "@/lib/theme-provider";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  display: "swap",
});

export const metadata: Metadata = {
  title: {
    default: "Oupsii — Plateforme d'enseignement multi-agents",
    template: "%s · Oupsii",
  },
  description:
    "121 tuteurs IA spécialisés par niveau et matière, du CEM au Lycée. Diagnostic de niveau, accompagnement personnalisé, essai gratuit 7 jours.",
  keywords: ["enseignement", "IA", "tuteur IA", "algérie", "CEM", "lycée", "BEM", "BAC", "cours en ligne"],
  authors: [{ name: "Oupsii" }],
  openGraph: {
    title: "Oupsii — Plateforme d'enseignement multi-agents",
    description: "121 tuteurs IA spécialisés par niveau et matière. Essai gratuit 7 jours.",
    type: "website",
    locale: "fr_FR",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="fr" suppressHydrationWarning>
      <body className={`${inter.variable} font-sans`}>
        <ThemeProvider>
          <AuthProvider>{children}</AuthProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}
