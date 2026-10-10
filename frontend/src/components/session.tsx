"use client";

import { createContext, Fragment, useCallback, useContext, useEffect, useState, type ReactNode } from "react";
import { ApiError, api } from "@/lib/api";
import { displayName } from "@/lib/format";
import { errorText } from "@/lib/hooks";
import { activeProfileId, savedProfileId, setActiveProfile } from "@/lib/profile";
import type { Me } from "@/lib/types";
import { Logo } from "./icons";
import { useToast } from "./toast";
import { Button, Spinner } from "./ui";

type Session = {
  me: Me;
  isHod: boolean;
  profiles: Me[];
  /** Profile id being switched to, while the switch is in flight. */
  switchingTo: string | null;
  switchProfile: (id: string) => Promise<void>;
};
type State =
  | { status: "loading" }
  | { status: "ready"; me: Me; profiles: Me[] }
  | { status: "failed"; message: string; hint?: string };

const SessionContext = createContext<Session | null>(null);

const DATABASE_DOWN: State = {
  status: "failed",
  message: "Can't reach the database",
  hint: "This network blocks the database port (5432). Switch to a phone hotspot, then try again.",
};

async function loadSession(): Promise<State> {
  let profiles: Me[];
  try {
    profiles = await api<Me[]>("/profiles", { anonymous: true });
  } catch (error) {
    if (error instanceof ApiError && error.status === 404) {
      return {
        status: "failed",
        message: "Profile switching is off",
        hint: "Set DEMO_PROFILE_SWITCH=true in backend/.env, then restart the backend",
      };
    }
    if (error instanceof ApiError && error.status === 503) return DATABASE_DOWN;
    if (error instanceof ApiError && error.status === 0) {
      return { status: "failed", message: errorText(error), hint: "Start KawTeam with npm run dev in the project folder" };
    }
    return { status: "failed", message: errorText(error) };
  }
  if (profiles.length === 0) {
    return { status: "failed", message: "No people yet", hint: "Run python -m scripts.seed in backend" };
  }
  // Keep this tab's profile on retry; otherwise the last one used in this browser; else the first (HOD).
  const wanted = activeProfileId() ?? savedProfileId();
  const id = profiles.some((p) => p.id === wanted) ? wanted! : profiles[0].id;
  try {
    const me = await api<Me>("/me", { as: id });
    setActiveProfile(id);
    return { status: "ready", me, profiles };
  } catch (error) {
    if (error instanceof ApiError && error.status === 503) return DATABASE_DOWN;
    return { status: "failed", message: errorText(error) };
  }
}

/** Acts as one seeded person at a time. No sign-in: the profile menu switches between people. */
export function SessionProvider({ children }: { children: ReactNode }) {
  const toast = useToast();
  const [state, setState] = useState<State>({ status: "loading" });
  const [attempt, setAttempt] = useState(0);
  const [switchingTo, setSwitchingTo] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    loadSession().then((next) => {
      if (!cancelled) setState(next);
    });
    return () => {
      cancelled = true;
    };
  }, [attempt]);

  const retry = useCallback(() => {
    setState({ status: "loading" });
    setAttempt((n) => n + 1);
  }, []);

  const switchProfile = useCallback(
    async (id: string) => {
      if (state.status !== "ready" || id === state.me.id || switchingTo) return;
      setSwitchingTo(id);
      try {
        const me = await api<Me>("/me", { as: id });
        setActiveProfile(id);
        setState({ status: "ready", me, profiles: state.profiles });
        toast(`Switched to ${displayName(me)}`);
      } catch (error) {
        toast(errorText(error), "error");
      } finally {
        setSwitchingTo(null);
      }
    },
    [state, switchingTo, toast],
  );

  if (state.status === "loading") {
    return (
      <div className="flex min-h-[70vh] flex-col items-center justify-center gap-3 text-[var(--text-3)]">
        <Spinner size={22} />
        {/* Only shows when loading is slow (the database can take ~15 s to answer or time out) */}
        <p className="appear-late text-sm">Connecting…</p>
      </div>
    );
  }
  if (state.status === "failed") {
    return (
      <div className="flex min-h-[80vh] items-center justify-center px-4">
        <div className="card fade-in flex w-full max-w-sm flex-col items-center gap-4 p-8 text-center">
          <Logo size={44} />
          <div className="flex flex-col gap-1.5">
            <p className="title-md">{state.message}</p>
            {state.hint ? <p className="text-sm text-[var(--text-2)]">{state.hint}</p> : null}
          </div>
          <Button variant="secondary" onClick={retry}>
            Try again
          </Button>
        </div>
      </div>
    );
  }
  return (
    <SessionContext.Provider
      value={{
        me: state.me,
        isHod: state.me.roles.includes("hod"),
        profiles: state.profiles,
        switchingTo,
        switchProfile,
      }}
    >
      {/* A new profile remounts the app, so every page reloads its data as that person */}
      <Fragment key={state.me.id}>{children}</Fragment>
    </SessionContext.Provider>
  );
}

export function useSession(): Session {
  const session = useContext(SessionContext);
  if (!session) throw new Error("useSession must be used inside SessionProvider");
  return session;
}
