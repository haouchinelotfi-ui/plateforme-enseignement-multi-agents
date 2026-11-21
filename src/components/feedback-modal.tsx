"use client";

import { useState } from "react";
import { api } from "@/lib/api";

interface Props {
  usageLogId: string;
  onClose: () => void;
}

export function FeedbackModal({ usageLogId, onClose }: Props) {
  const [rating, setRating] = useState(0);
  const [hover, setHover] = useState(0);
  const [comment, setComment] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [done, setDone] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function submit() {
    if (rating === 0) return;
    setSubmitting(true);
    setError(null);
    try {
      await api.submitFeedback(usageLogId, rating, comment || undefined);
      setDone(true);
      setTimeout(onClose, 1500);
    } catch (err: any) {
      setError(err.detail || "Erreur lors de l'envoi.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm animate-fade-in" onClick={onClose}>
      <div className="card p-6 w-full max-w-md mx-4 animate-scale-in" onClick={(e) => e.stopPropagation()}>
        {done ? (
          <div className="text-center py-6">
            <div className="text-4xl mb-3">✅</div>
            <p className="font-semibold">Merci pour votre retour !</p>
          </div>
        ) : (
          <>
            <h3 className="font-semibold text-lg">Noter cette réponse</h3>
            <p className="text-sm text-ink-500 mt-1">Votre avis aide à améliorer le tuteur.</p>

            <div className="mt-4 flex justify-center gap-2">
              {[1, 2, 3, 4, 5].map((n) => (
                <button
                  key={n}
                  onMouseEnter={() => setHover(n)}
                  onMouseLeave={() => setHover(0)}
                  onClick={() => setRating(n)}
                  className={`text-3xl transition-transform hover:scale-125 ${
                    (hover || rating) >= n ? "text-amber-400" : "text-ink-300 dark:text-ink-600"
                  }`}
                  aria-label={`${n} étoile${n > 1 ? "s" : ""}`}
                >
                  ★
                </button>
              ))}
            </div>

            <textarea
              value={comment}
              onChange={(e) => setComment(e.target.value)}
              placeholder="Commentaire (optionnel)…"
              className="input mt-4 min-h-[80px] resize-none"
            />

            {error && <p className="mt-2 text-sm text-red-600">{error}</p>}

            <div className="mt-4 flex gap-2 justify-end">
              <button onClick={onClose} className="btn-ghost">Annuler</button>
              <button onClick={submit} disabled={rating === 0 || submitting} className="btn-primary">
                {submitting ? "Envoi…" : "Envoyer"}
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
