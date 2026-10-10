"use client";

import { useRouter } from "next/navigation";
import { createContext, useCallback, useContext, useEffect, useState, type ReactNode } from "react";
import { ApiError, api } from "@/lib/api";
import { supabase } from "@/lib/supabase";
import type { Me } from "@/lib/types";
import { Logo, LogoutIcon } from "./icons";
import { Button, Spinner } from "./ui";

type Session = { me: Me; isHod: boolean; signOut: () => Promise<void> };
type State = { status: "loading" } | { status: "ready"; me: Me } | { status: "denied"; message: string };

const SessionContext = createContext<Session | null>(null);

/** Gate for signed-in pages: needs a Supabase session and a KawTeam role (from GET /me). */
export function SessionProvider({ children }: { children: ReactNode }) {
  const router = useRouter();
  const [state, setState] = useState<State>({ status: "loading" });

  const signOut = useCallback(async () => {
    await supabase().auth.signOut();
    router.replace("/login");
  }, [router]);

  useEffect(() => {
    let cancelled = false;
    const client = supabase();
    client.auth.getSession().then(async ({ data }) => {
      if (!data.session) {
        router.replace("/login");
        return;
      }
      try {
        const me = await api<Me>("/me");
        if (!cancelled) setState({ status: "ready", me });
      } catch (error) {
        if (error instanceof ApiError && error.status === 401) router.replace("/login");
        else if (!cancelled)
          setState({ status: "denied", message: error instanceof ApiError ? error.message : "Can't load your account" });
      }
    });
    const { data } = client.auth.onAuthStateChange((event) => {
      if (event === "SIGNED_OUT") router.replace("/login");
    });
    return () => {
      cancelled = true;
      data.subscription.unsubscribe();
    };
  }, [router]);

  if (state.status === "loading") {
    return (
      <div className="flex min-h-[70vh] items-center justify-center text-[var(--text-3)]">
        <Spinner size={22} />
      </div>
    );
  }
  if (state.status === "denied") {
    return (
      <div className="flex min-h-[80vh] items-center justify-center px-4">
        <div className="card fade-in flex w-full max-w-sm flex-col items-center gap-4 p-8 text-center">
          <Logo size={40} />
          <p className="text-[var(--text-2)]">{state.message}</p>
          <Button variant="secondary" onClick={signOut}>
            <LogoutIcon size={16} /> Sign out
          </Button>
        </div>
      </div>
    );
  }
  return (
    <SessionContext.Provider value={{ me: state.me, isHod: state.me.roles.includes("hod"), signOut }}>
      {children}
    </SessionContext.Provider>
  );
}

export function useSession(): Session {
  const session = useContext(SessionContext);
  if (!session) throw new Error("useSession must be used inside SessionProvider");
  return session;
}
