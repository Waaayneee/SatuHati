"use client";

import { createContext, useCallback, useContext, useState, type ReactNode } from "react";
import { CheckIcon, XIcon } from "./icons";

type Toast = { id: number; text: string; tone: "ok" | "error" };
type Push = (text: string, tone?: Toast["tone"]) => void;

const ToastContext = createContext<Push>(() => {});

export function ToastProvider({ children }: { children: ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const push = useCallback<Push>((text, tone = "ok") => {
    const id = Date.now() + Math.random();
    setToasts((list) => [...list, { id, text, tone }]);
    setTimeout(() => setToasts((list) => list.filter((t) => t.id !== id)), 4200);
  }, []);

  return (
    <ToastContext.Provider value={push}>
      {children}
      <div
        className="pointer-events-none fixed inset-x-0 top-16 z-50 flex flex-col items-center gap-2 px-4"
        role="status"
        aria-live="polite"
      >
        {toasts.map((t) => (
          <div
            key={t.id}
            className={`toast-in pointer-events-auto flex max-w-md items-center gap-2 rounded-full px-4 py-2.5 text-sm font-medium shadow-[var(--shadow-lg)] ${
              t.tone === "ok" ? "bg-[var(--accent)] text-[var(--on-accent)]" : "bg-[var(--red)] text-[var(--surface)]"
            }`}
          >
            {t.tone === "ok" ? <CheckIcon size={16} /> : <XIcon size={16} />}
            <span>{t.text}</span>
          </div>
        ))}
      </div>
      <style>{`
        .toast-in { animation: toast-in 320ms cubic-bezier(0.2, 0.9, 0.25, 1) both; }
        @keyframes toast-in { from { opacity: 0; transform: translateY(-12px) scale(0.98); } to { opacity: 1; transform: none; } }
        @media (prefers-reduced-motion: reduce) { .toast-in { animation: fade-only 200ms ease both; } }
      `}</style>
    </ToastContext.Provider>
  );
}

export function useToast(): Push {
  return useContext(ToastContext);
}
