"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth-context";
import { api } from "@/lib/api";
import type { QuizQuestion, QuizResult } from "@/lib/types";
import { Navbar } from "@/components/navbar";
import { Blob } from "@/components/decorations";

export default function QuizPage() {
  const { isAuthenticated, loading: authLoading } = useAuth();
  const router = useRouter();
  const [questions, setQuestions] = useState<QuizQuestion[]>([]);
  const [loading, setLoading] = useState(true);
  const [current, setCurrent] = useState(0);
  const [answers, setAnswers] = useState<Record<string, number>>({});
  const [result, setResult] = useState<QuizResult | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!authLoading && !isAuthenticated) router.push("/register");
  }, [authLoading, isAuthenticated, router]);

  useEffect(() => {
    api.getQuiz().then(setQuestions).catch(() => setError("Impossible de charger le quiz.")).finally(() => setLoading(false));
  }, []);

  function selectAnswer(qId: string, optIdx: number) {
    setAnswers((prev) => ({ ...prev, [qId]: optIdx }));
    setTimeout(() => {
      if (current < questions.length - 1) setCurrent((c) => c + 1);
    }, 300);
  }

  async function submit() {
    setSubmitting(true);
    setError(null);
    try {
      const r = await api.submitQuiz(answers);
      setResult(r);
    } catch (err: any) {
      setError(err.detail || "Erreur lors de la soumission.");
    } finally {
      setSubmitting(false);
    }
  }

  const progress = questions.length ? ((current + 1) / questions.length) * 100 : 0;
  const q = questions[current];

  if (authLoading || loading) {
    return (
      <>
        <Navbar />
        <main className="min-h-screen flex items-center justify-center pt-24">
          <div className="text-center">
            <div className="inline-block h-10 w-10 animate-spin rounded-full border-4 border-brand-200 border-t-brand-600" />
            <p className="mt-4 text-ink-500">Chargement du diagnostic…</p>
          </div>
        </main>
      </>
    );
  }

  if (result) {
    return (
      <>
        <Navbar />
        <main className="min-h-screen pt-24 pb-12 px-4">
          <div className="container-page max-w-3xl">
            <div className="card p-8 text-center animate-scale-in">
              <div className="text-5xl mb-4">🎯</div>
              <h1 className="text-2xl font-bold">Diagnostic terminé !</h1>
              <p className="mt-2 text-ink-600 dark:text-ink-400">Votre niveau a été détecté :</p>

              <div className="mt-6 inline-block rounded-2xl bg-brand-50 dark:bg-brand-900/30 px-8 py-4">
                <div className="text-3xl font-bold gradient-text">{result.detected_level_code}</div>
                <div className="text-sm text-ink-600 dark:text-ink-400 mt-1">{result.detected_level_name}</div>
              </div>

              {result.recommendation && (
                <p className="mt-6 text-sm text-ink-600 dark:text-ink-400 max-w-lg mx-auto">{result.recommendation}</p>
              )}

              {result.score_by_subject && Object.keys(result.score_by_subject).length > 0 && (
                <div className="mt-8 grid grid-cols-2 sm:grid-cols-3 gap-3 text-left">
                  {Object.entries(result.score_by_subject).map((entry) => {
                    const subj = entry[0];
                    const score = entry[1];
                    const pct = score.total ? Math.round((score.correct / score.total) * 100) : 0;
                    return (
                      <div key={subj} className="rounded-xl border border-ink-100 dark:border-ink-700 p-3">
                        <div className="text-xs text-ink-500 capitalize">{subj}</div>
                        <div className="text-sm font-semibold">{score.correct} / {score.total}</div>
                        <div className="mt-1 h-1.5 rounded-full bg-ink-100 dark:bg-ink-700">
                          <div className="h-full rounded-full bg-brand-500" style={{ width: pct + "%" }} />
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}

              <button onClick={() => router.push("/dashboard")} className="btn-primary mt-8">
                Accéder à mon tableau de bord →
              </button>
            </div>
          </div>
        </main>
      </>
    );
  }

  if (!q) {
    return (
      <>
        <Navbar />
        <main className="min-h-screen flex items-center justify-center pt-24">
          <div className="text-center">
            <p className="text-ink-500">{error || "Aucune question disponible."}</p>
          </div>
        </main>
      </>
    );
  }

  return (
    <>
      <Navbar />
      <main className="relative min-h-screen pt-24 pb-12 px-4 overflow-hidden">
        <Blob className="top-20 right-0 h-64 w-64" />
        <div className="container-page max-w-2xl relative">
          <div className="mb-8">
            <div className="flex justify-between text-sm text-ink-500 mb-2">
              <span>Question {current + 1} sur {questions.length}</span>
              <span>{Math.round(progress)}%</span>
            </div>
            <div className="h-2 rounded-full bg-ink-100 dark:bg-ink-700 overflow-hidden">
              <div className="h-full rounded-full bg-gradient-to-r from-brand-500 to-brand-600 transition-all duration-500" style={{ width: progress + "%" }} />
            </div>
          </div>

          {error && (
            <div className="mb-4 rounded-xl bg-red-50 border border-red-200 px-4 py-3 text-sm text-red-700 dark:bg-red-900/30 dark:border-red-800 dark:text-red-300">
              {error}
            </div>
          )}

          <div key={q.id} className="card p-8 animate-scale-in">
            <div className="badge-brand mb-4">{q.subject_slug}</div>
            <h2 className="text-xl font-semibold text-balance">{q.question}</h2>

            <div className="mt-6 space-y-3">
              {q.options.map((opt, idx) => {
                const selected = answers[q.id] === idx;
                const btnClass = selected
                  ? "w-full text-left rounded-xl border-2 px-5 py-4 text-sm font-medium transition-all border-brand-500 bg-brand-50 dark:bg-brand-900/30"
                  : "w-full text-left rounded-xl border-2 px-5 py-4 text-sm font-medium transition-all border-ink-100 dark:border-ink-700 hover:border-brand-400 hover:bg-brand-50/50 dark:hover:bg-brand-900/20";
                const dotClass = selected
                  ? "inline-flex h-6 w-6 items-center justify-center rounded-full border-2 mr-3 text-xs border-brand-500 bg-brand-500 text-white"
                  : "inline-flex h-6 w-6 items-center justify-center rounded-full border-2 mr-3 text-xs border-ink-300 dark:border-ink-600";
                return (
                  <button key={idx} onClick={() => selectAnswer(q.id, idx)} className={btnClass}>
                    <span className={dotClass}>{String.fromCharCode(65 + idx)}</span>
                    {opt}
                  </button>
                );
              })}
            </div>
          </div>

          <div className="mt-6 flex justify-between">
            <button onClick={() => setCurrent((c) => Math.max(0, c - 1))} disabled={current === 0} className="btn-ghost">
              ← Précédent
            </button>
            {current === questions.length - 1 ? (
              <button onClick={submit} disabled={submitting || Object.keys(answers).length < questions.length} className="btn-primary">
                {submitting ? "Analyse…" : "Voir mon résultat →"}
              </button>
            ) : (
              <button onClick={() => setCurrent((c) => c + 1)} disabled={answers[q.id] === undefined} className="btn-primary">
                Suivant →
              </button>
            )}
          </div>
        </div>
      </main>
    </>
  );
}
