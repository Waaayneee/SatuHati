"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState, type FormEvent } from "react";
import { Logo } from "@/components/icons";
import { Button, ErrorNote } from "@/components/ui";
import { supabase } from "@/lib/supabase";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    supabase()
      .auth.getSession()
      .then(({ data }) => {
        if (data.session) router.replace("/missions");
      });
  }, [router]);

  async function submit(event: FormEvent) {
    event.preventDefault();
    setBusy(true);
    setError(null);
    const { error: signInError } = await supabase().auth.signInWithPassword({ email: email.trim(), password });
    if (signInError) {
      setError(signInError.message === "Invalid login credentials" ? "Wrong email or password" : signInError.message);
      setBusy(false);
      return;
    }
    router.replace("/missions");
  }

  return (
    <div className="relative flex min-h-screen items-center justify-center overflow-hidden px-4">
      <div
        aria-hidden="true"
        className="pointer-events-none absolute inset-0"
        style={{
          background:
            "radial-gradient(60% 50% at 20% 10%, rgba(10,132,255,0.16), transparent 70%), radial-gradient(50% 45% at 85% 90%, rgba(94,92,230,0.16), transparent 70%)",
        }}
      />
      <form onSubmit={submit} className="card fade-in relative flex w-full max-w-[380px] flex-col gap-5 p-8">
        <div className="flex flex-col items-center gap-3 pb-1 text-center">
          <Logo size={52} />
          <h1 className="text-[1.6rem] leading-tight font-bold tracking-[-0.025em]">KawTeam</h1>
        </div>
        <div className="flex flex-col gap-3">
          <input
            className="field"
            type="email"
            autoComplete="email"
            placeholder="Email"
            aria-label="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
          <input
            className="field"
            type="password"
            autoComplete="current-password"
            placeholder="Password"
            aria-label="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </div>
        {error ? <ErrorNote text={error} /> : null}
        <Button type="submit" busy={busy} className="w-full">
          Sign in
        </Button>
      </form>
    </div>
  );
}
