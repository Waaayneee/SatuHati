"use client";

import { useCallback, useEffect, useRef, useState, type KeyboardEvent } from "react";
import { displayName, initials, roleLabel } from "@/lib/format";
import { applyTheme, storedTheme, type Theme } from "@/lib/theme";
import type { Me } from "@/lib/types";
import { CheckIcon, MoonIcon, SunIcon } from "./icons";
import { useSession } from "./session";
import { Spinner } from "./ui";

export function Avatar({ person, size = 32 }: { person: Me; size?: number }) {
  const hod = person.primary_role === "hod";
  return (
    <span
      aria-hidden="true"
      className={`avatar ${hod ? "avatar-hod" : "avatar-member"}`}
      style={{ width: size, height: size, fontSize: size * 0.42 }}
    >
      {initials(person)}
    </span>
  );
}

/** Top-right profile button. Its menu switches who you act as (no password) and the appearance. */
export function ProfileMenu() {
  const { me, profiles, switchingTo, switchProfile } = useSession();
  const [open, setOpen] = useState(false);
  const [theme, setTheme] = useState<Theme>(storedTheme);
  const root = useRef<HTMLDivElement>(null);
  const trigger = useRef<HTMLButtonElement>(null);
  const panel = useRef<HTMLDivElement>(null);

  const close = useCallback((refocus: boolean) => {
    setOpen(false);
    if (refocus) trigger.current?.focus();
  }, []);

  useEffect(() => {
    if (!open) return;
    const onPointerDown = (e: PointerEvent) => {
      if (!root.current?.contains(e.target as Node)) close(false);
    };
    const onKey = (e: globalThis.KeyboardEvent) => e.key === "Escape" && close(true);
    document.addEventListener("pointerdown", onPointerDown);
    document.addEventListener("keydown", onKey);
    panel.current?.querySelector<HTMLElement>('[aria-checked="true"]')?.focus();
    return () => {
      document.removeEventListener("pointerdown", onPointerDown);
      document.removeEventListener("keydown", onKey);
    };
  }, [open, close]);

  // Arrow keys move between the menu's items, like a native menu.
  function onMenuKey(e: KeyboardEvent<HTMLDivElement>) {
    if (!["ArrowDown", "ArrowUp", "Home", "End"].includes(e.key)) return;
    const items = Array.from(panel.current?.querySelectorAll<HTMLElement>('[role^="menuitem"]') ?? []);
    if (items.length === 0) return;
    e.preventDefault();
    const at = items.indexOf(document.activeElement as HTMLElement);
    const next =
      e.key === "Home" ? 0 : e.key === "End" ? items.length - 1 : (at + (e.key === "ArrowDown" ? 1 : -1) + items.length) % items.length;
    items[next].focus();
  }

  async function choose(person: Me) {
    if (person.id === me.id) {
      close(true);
      return;
    }
    await switchProfile(person.id);
    // The app remounts on success; on failure keep the menu so another person can be picked.
  }

  function pickTheme(next: Theme) {
    setTheme(next);
    applyTheme(next);
  }

  return (
    <div ref={root} className="relative">
      <button
        ref={trigger}
        onClick={() => (open ? close(false) : setOpen(true))}
        aria-haspopup="menu"
        aria-expanded={open}
        aria-label={`${displayName(me)}, ${roleLabel(me.primary_role)}. Switch profile`}
        className="press flex items-center gap-2 rounded-full py-1 pr-1 pl-1 hover:bg-[var(--line)] sm:pl-3"
      >
        <span className="hidden flex-col items-end leading-tight sm:flex">
          <span className="text-[0.8125rem] font-semibold tracking-[-0.01em]">{displayName(me)}</span>
          <span className="text-[0.68rem] font-medium text-[var(--text-2)]">{roleLabel(me.primary_role)}</span>
        </span>
        <Avatar person={me} size={32} />
      </button>

      <div
        ref={panel}
        role="menu"
        aria-label="Switch profile"
        inert={!open}
        onKeyDown={onMenuKey}
        className={`popover ${open ? "is-open" : ""}`}
      >
        <p className="label px-3 pt-1 pb-1.5 font-medium">Act as</p>
        <div className="flex flex-col gap-0.5">
          {profiles.map((person) => {
            const current = person.id === me.id;
            return (
              <button
                key={person.id}
                role="menuitemradio"
                aria-checked={current}
                onClick={() => choose(person)}
                disabled={switchingTo !== null && switchingTo !== person.id}
                className={`menu-row press ${current ? "is-current" : ""}`}
              >
                <Avatar person={person} size={34} />
                <span className="flex min-w-0 flex-1 flex-col text-left leading-tight">
                  <span className="truncate text-[0.875rem] font-semibold tracking-[-0.01em]">{displayName(person)}</span>
                  <span className="truncate text-[0.72rem] text-[var(--text-2)]">{roleLabel(person.primary_role)}</span>
                </span>
                <span className="flex w-5 justify-center text-[var(--accent)]">
                  {switchingTo === person.id ? <Spinner size={15} /> : current ? <CheckIcon size={17} /> : null}
                </span>
              </button>
            );
          })}
        </div>

        <div className="my-2 h-px bg-[var(--line)]" />

        <div className="flex items-center justify-between gap-3 px-3 py-1">
          <span className="text-[0.8125rem] font-medium">Appearance</span>
          <div className="flex gap-0.5 rounded-full bg-[var(--line)] p-0.5" role="group" aria-label="Appearance">
            {(["light", "dark"] as const).map((option) => (
              <button
                key={option}
                role="menuitemradio"
                aria-checked={theme === option}
                aria-label={option === "light" ? "Light" : "Dark"}
                onClick={() => pickTheme(option)}
                className={`press flex h-7 w-9 items-center justify-center rounded-full ${
                  theme === option ? "bg-[var(--surface)] text-[var(--text)] shadow-[var(--shadow-sm)]" : "text-[var(--text-2)] hover:text-[var(--text)]"
                }`}
              >
                {option === "light" ? <SunIcon size={15} /> : <MoonIcon size={15} />}
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
