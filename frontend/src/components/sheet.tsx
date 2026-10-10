"use client";

import { useEffect, useRef, type ReactNode } from "react";
import { XIcon } from "./icons";

/**
 * Modal sheet. Rises from the bottom and leaves the same way, over a dimming scrim
 * (a modal task). Esc or the scrim closes it.
 */
export function Sheet({
  open,
  onClose,
  title,
  children,
}: {
  open: boolean;
  onClose: () => void;
  title: string;
  children: ReactNode;
}) {
  const panel = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => e.key === "Escape" && onClose();
    window.addEventListener("keydown", onKey);
    const previous = document.activeElement as HTMLElement | null;
    const first =
      panel.current?.querySelector<HTMLElement>("input, textarea, select") ??
      panel.current?.querySelector<HTMLElement>("button");
    first?.focus();
    document.body.style.overflow = "hidden";
    return () => {
      window.removeEventListener("keydown", onKey);
      document.body.style.overflow = "";
      previous?.focus();
    };
  }, [open, onClose]);

  return (
    <div className={`sheet-root ${open ? "is-open" : ""}`} inert={!open}>
      <div className="sheet-scrim" onClick={onClose} />
      <div ref={panel} className="sheet-panel" role="dialog" aria-modal="true" aria-label={title}>
        <div className="mx-auto mb-3 h-1.5 w-10 rounded-full bg-[var(--line-strong)] sm:hidden" />
        <div className="mb-4 flex items-center justify-between">
          <h2 className="title-md">{title}</h2>
          <button onClick={onClose} className="press rounded-full p-1.5 text-[var(--text-2)] hover:bg-[var(--line)]" aria-label="Close">
            <XIcon size={18} />
          </button>
        </div>
        {children}
      </div>
      <style>{`
        .sheet-root { position: fixed; inset: 0; z-index: 40; pointer-events: none; }
        .sheet-root.is-open { pointer-events: auto; }
        .sheet-scrim { position: absolute; inset: 0; background: var(--scrim); opacity: 0; transition: opacity 280ms ease; }
        .is-open .sheet-scrim { opacity: 1; }
        .sheet-panel {
          position: absolute; left: 50%; bottom: 0; width: min(560px, 100%); max-height: 92vh; overflow-y: auto;
          background: var(--surface); border-radius: 22px 22px 0 0; padding: 14px 22px 26px;
          box-shadow: var(--shadow-lg);
          transform: translate(-50%, 104%);
          transition: transform 420ms cubic-bezier(0.32, 0.72, 0, 1);
        }
        .is-open .sheet-panel { transform: translate(-50%, 0); }
        @media (min-width: 640px) {
          .sheet-panel { bottom: 50%; border-radius: 22px; padding: 22px 26px 26px; transform: translate(-50%, calc(50% + 100vh)); }
          .is-open .sheet-panel { transform: translate(-50%, 50%); }
        }
        @media (prefers-reduced-motion: reduce) {
          .sheet-panel, .is-open .sheet-panel { transition: opacity 200ms ease; }
          .sheet-root:not(.is-open) .sheet-panel { opacity: 0; }
        }
      `}</style>
    </div>
  );
}
