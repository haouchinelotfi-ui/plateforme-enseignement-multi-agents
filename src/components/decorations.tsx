"use client";

import { ReactNode } from "react";

/** Blob décoratif animé en arrière-plan */
export function Blob({ className = "" }: { className?: string }) {
  return (
    <div className={`pointer-events-none absolute ${className}`} aria-hidden>
      <div className="h-full w-full rounded-full bg-gradient-to-br from-brand-400/30 to-brand-600/20 blur-3xl animate-blob" />
    </div>
  );
}

/** Grille de fond décorative */
export function GridBackground({ className = "" }: { className?: string }) {
  return <div className={`pointer-events-none absolute inset-0 bg-grid ${className}`} aria-hidden />;
}

/** Orbe flottant décoratif */
export function FloatingOrb({ className = "", children }: { className?: string; children?: ReactNode }) {
  return (
    <div className={`pointer-events-none absolute animate-float ${className}`} aria-hidden>
      {children}
    </div>
  );
}
