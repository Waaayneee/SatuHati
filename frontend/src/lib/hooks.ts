"use client";

import { useCallback, useEffect, useState, useSyncExternalStore } from "react";
import { ApiError, api } from "./api";

// One shared 1-second clock for every countdown on the page.
let current = 0;
let timer: ReturnType<typeof setInterval> | null = null;
const listeners = new Set<() => void>();

function subscribe(listener: () => void) {
  listeners.add(listener);
  if (timer === null) {
    current = Date.now();
    timer = setInterval(() => {
      current = Date.now();
      listeners.forEach((l) => l());
    }, 1000);
  }
  return () => {
    listeners.delete(listener);
    if (listeners.size === 0 && timer !== null) {
      clearInterval(timer);
      timer = null;
    }
  };
}

/** Current time in ms, or null during server render (no time-dependent prerender). */
export function useNow(): number | null {
  return useSyncExternalStore(
    subscribe,
    () => current || (current = Date.now()),
    () => null,
  );
}

export function errorText(error: unknown): string {
  if (error instanceof ApiError) return error.message;
  return "Something went wrong";
}

/** Loads a backend path. `reload()` fetches again. */
export function useLoad<T>(path: string | null) {
  const [state, setState] = useState<{ data: T | null; error: string | null; path: string | null }>({
    data: null,
    error: null,
    path: null,
  });
  const [version, setVersion] = useState(0);

  useEffect(() => {
    if (!path) return;
    let cancelled = false;
    api<T>(path)
      .then((data) => {
        if (!cancelled) setState({ data, error: null, path });
      })
      .catch((error) => {
        if (!cancelled) setState((s) => ({ data: s.path === path ? s.data : null, error: errorText(error), path }));
      });
    return () => {
      cancelled = true;
    };
  }, [path, version]);

  const reload = useCallback(() => setVersion((v) => v + 1), []);
  const fresh = state.path === path;
  return {
    data: fresh ? state.data : null,
    error: fresh ? state.error : null,
    loading: !fresh || (state.data === null && state.error === null),
    reload,
  };
}

/** Lets one part of the page tell another that approvals changed (e.g. nav badge). */
export function announceApprovalsChanged() {
  window.dispatchEvent(new Event("kawteam:approvals-changed"));
}
