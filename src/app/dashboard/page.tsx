"use client";

import { useState, useRef, useEffect, FormEvent } from "react";
import { useAuth } from "@/lib/auth-context";
import { api } from "@/lib/api";
import { Navbar } from "@/components/navbar";
import type { ChatResponse } from "@/lib/types";
import { FeedbackModal } from "@/components/feedback-modal";

interface Msg {
  id: string;
  role: "user" | "assistant";
  content: string;
  usage_log_id?: string;
  agent_name?: string;
}

const SUBJECTS = [
  { slug: "mathematiques", name: "Mathématiques", icon: "📐" },
  { slug: "physique", name: "Physique", icon: "⚛️" },
  { slug: "chimie", name: "Chimie", icon: "🧪" },
  { slug: "svt", name: "SVT", icon: "🧬" },
  { slug: "arabe", name: "Arabe", icon: "📖" },
  { slug: "francais", name: "Français", icon: "🇫🇷" },
  { slug: "anglais", name: "Anglais", icon: "🇬🇧" },
  { slug: "histoire_geo", name: "Histoire-Géo", icon: "🗺️" },
  { slug: "philo", name: "Philosophie", icon: "💭" },
  { slug: "islamiques", name: "Sciences Islamiques", icon: "🕌" },
  { slug: "informatique", name: "Informatique", icon: "💻" },
];

export default function DashboardPage() {
  const { user, isTrialActive, isSubscribed, refreshUser } = useAuth();
  const [selectedSubject, setSelectedSubject] = useState<string | null>(null);
  const [messages, setMessages] = useState<Msg[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [feedbackTarget, setFeedbackTarget] = useState<{ usageLogId: string; msgId: string } | null>(null);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages]);

  // Trial expired banner
  const trialDaysLeft = user ? Math.max(0, Math.ceil((new Date(user.trial_ends_at).getTime() - Date.now()) / 86400000)) : 0;
  const accessBlocked = !isSubscribed && !isTrialActive;

  async function sendMessage(e: FormEvent) {
    e.preventDefault();
    if (!input.trim() || loading || !selectedSubject) return;
    const content = input.trim();
    setInput("");

    const userMsg: Msg = { id: crypto.randomUUID(), role: "user", content };
    setMessages((m) => [...m, userMsg]);
    setLoading(true);

    try {
      const res: ChatResponse = await api.chat(content, {
        session_id: sessionId || undefined,
        subject_slug: selectedSubject,
      });
      setSessionId(res.session_id);
      setMessages((m) => [
        ...m,
        {
          id: crypto.randomUUID(),
          role: "assistant",
          content: res.message,
          usage_log_id: res.usage_log_id,
          agent_name: res.agent_name,
        },
      ]);
      refreshUser(); // update last_active
    } catch (err: any) {
      setMessages((m) => [
        ...m,
        { id: crypto.randomUUID(), role: "assistant", content: `⚠️ Erreur : ${err.detail || "Le tuteur est temporairement indisponible."}` },
      ]);
    } finally {
      setLoading(false);
    }
  }

  const currentSubject = SUBJECTS.find((s) => s.slug === selectedSubject);

  return (
    <>
      <Navbar />
      <main className="min-h-screen pt-20 flex">
        {/* Sidebar sujets */}
        <aside className="hidden lg:flex flex-col w-64 border-r border-ink-100 dark:border-ink-800 bg-ink-50/50 dark:bg-ink-900/50 p-4 fixed inset-y-0 top-20 pt-20 overflow-y-auto">
          <h2 className="text-xs font-semibold uppercase text-ink-500 mb-3">Matières</h2>
          <div className="space-y-1">
            {SUBJECTS.map((s) => (
              <button
                key={s.slug}
                onClick={() => { setSelectedSubject(s.slug); setMessages([]); setSessionId(null); }}
                className={`w-full flex items-center gap-3 rounded-xl px-3 py-2 text-sm font-medium transition ${
                  selectedSubject === s.slug
                    ? "bg-brand-50 text-brand-700 dark:bg-brand-900/30 dark:text-brand-300"
                    : "text-ink-600 hover:bg-ink-100 dark:text-ink-300 dark:hover:bg-ink-800"
                }`}
              >
                <span className="text-lg">{s.icon}</span>
                {s.name}
              </button>
            ))}
          </div>
        </aside>

        {/* Main chat */}
        <div className="flex-1 lg:ml-64 flex flex-col">
          {/* Trial banner */}
          {user && !isSubscribed && (
            <div className={`px-6 py-2.5 text-sm text-center ${
              accessBlocked
                ? "bg-red-50 text-red-700 dark:bg-red-900/30 dark:text-red-300"
                : "bg-amber-50 text-amber-700 dark:bg-amber-900/30 dark:text-amber-300"
            }`}>
              {accessBlocked
                ? "⏰ Votre essai est terminé. Abonnez-vous pour continuer."
                : `⏰ Essai gratuit : ${trialDaysLeft} jour${trialDaysLeft > 1 ? "s" : ""} restant${trialDaysLeft > 1 ? "s" : ""}. `}
              {!accessBlocked && <a href="/pricing" className="underline font-semibold">S'abonner →</a>}
            </div>
          )}

          {!selectedSubject ? (
            <WelcomeScreen user={user} onSelect={setSelectedSubject} />
          ) : (
            <>
              {/* Header */}
              <div className="border-b border-ink-100 dark:border-ink-800 px-6 py-3 flex items-center gap-3">
                <span className="text-2xl">{currentSubject?.icon}</span>
                <div>
                  <h1 className="font-semibold">{currentSubject?.name}</h1>
                  <p className="text-xs text-ink-500">Tuteur IA spécialisé · {user?.detected_level?.code || "Niveau non détecté"}</p>
                </div>
              </div>

              {/* Messages */}
              <div ref={scrollRef} className="flex-1 overflow-y-auto px-6 py-6 space-y-4">
                {messages.length === 0 && (
                  <div className="text-center py-12">
                    <div className="text-4xl mb-3">{currentSubject?.icon}</div>
                    <p className="text-ink-500">Posez votre première question en {currentSubject?.name.toLowerCase()}…</p>
                  </div>
                )}

                {messages.map((m) => (
                  <div key={m.id} className={`flex ${m.role === "user" ? "justify-end" : "justify-start"} animate-fade-up`}>
                    <div className={`max-w-[80%] rounded-2xl px-4 py-3 ${
                      m.role === "user"
                        ? "bg-brand-600 text-white"
                        : "bg-ink-100 dark:bg-ink-800"
                    }`}>
                      {m.agent_name && <div className="text-xs text-ink-500 mb-1">{m.agent_name}</div>}
                      <p className="text-sm whitespace-pre-wrap">{m.content}</p>
                      {m.usage_log_id && (
                        <button
                          onClick={() => setFeedbackTarget({ usageLogId: m.usage_log_id!, msgId: m.id })}
                          className="mt-2 text-xs underline opacity-70 hover:opacity-100"
                        >
                          ⭐ Noter cette réponse
                        </button>
                      )}
                    </div>
                  </div>
                ))}

                {loading && (
                  <div className="flex justify-start">
                    <div className="bg-ink-100 dark:bg-ink-800 rounded-2xl px-4 py-3">
                      <div className="flex gap-1">
                        <span className="h-2 w-2 rounded-full bg-ink-400 animate-pulse" />
                        <span className="h-2 w-2 rounded-full bg-ink-400 animate-pulse animate-delay-100" />
                        <span className="h-2 w-2 rounded-full bg-ink-400 animate-pulse animate-delay-200" />
                      </div>
                    </div>
                  </div>
                )}
              </div>

              {/* Input */}
              <form onSubmit={sendMessage} className="border-t border-ink-100 dark:border-ink-800 p-4">
                <div className="flex gap-2">
                  <input
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    placeholder={`Écrivez votre message en ${currentSubject?.name.toLowerCase()}…`}
                    disabled={loading}
                    className="input flex-1"
                  />
                  <button type="submit" disabled={loading || !input.trim()} className="btn-primary px-6">
                    {loading ? "…" : "Envoyer →"}
                  </button>
                </div>
              </form>
            </>
          )}
        </div>
      </main>

      {feedbackTarget && (
        <FeedbackModal
          usageLogId={feedbackTarget.usageLogId}
          onClose={() => setFeedbackTarget(null)}
        />
      )}
    </>
  );
}

function WelcomeScreen({ user, onSelect }: { user: any; onSelect: (slug: string) => void }) {
  return (
    <div className="flex-1 flex items-center justify-center p-6">
      <div className="max-w-2xl w-full text-center">
        <div className="text-5xl mb-4">🎓</div>
        <h1 className="text-2xl font-bold">Bonjour {user?.email?.split("@")[0] || ""} 👋</h1>
        <p className="mt-2 text-ink-600 dark:text-ink-400">
          Sélectionnez une matière pour commencer à discuter avec votre tuteur IA.
        </p>

        <div className="mt-8 grid grid-cols-2 sm:grid-cols-3 gap-3">
          {SUBJECTS.map((s) => (
            <button
              key={s.slug}
              onClick={() => onSelect(s.slug)}
              className="card p-4 hover:shadow-md hover:border-brand-300 transition-all hover:scale-105"
            >
              <div className="text-3xl">{s.icon}</div>
              <div className="mt-2 text-sm font-medium">{s.name}</div>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
