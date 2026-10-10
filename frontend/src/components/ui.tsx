import type { ButtonHTMLAttributes, ReactNode } from "react";

type Variant = "primary" | "secondary" | "ghost" | "danger" | "success";

const VARIANTS: Record<Variant, string> = {
  primary: "bg-[var(--accent)] text-white hover:brightness-110",
  secondary: "bg-[var(--surface-2)] text-[var(--text)] border border-[var(--line-strong)] hover:bg-[var(--surface)]",
  ghost: "text-[var(--text-2)] hover:text-[var(--text)] hover:bg-[var(--line)]",
  danger: "bg-[var(--red-soft)] text-[var(--red)] hover:brightness-95",
  success: "bg-[var(--green)] text-white hover:brightness-110",
};

export function Button({
  variant = "primary",
  size = "md",
  className = "",
  busy = false,
  children,
  ...props
}: ButtonHTMLAttributes<HTMLButtonElement> & { variant?: Variant; size?: "sm" | "md"; busy?: boolean }) {
  const sizing = size === "sm" ? "h-8 px-3 text-[0.8125rem] rounded-full" : "h-10 px-4 text-[0.9375rem] rounded-full";
  return (
    <button
      className={`press inline-flex items-center justify-center gap-1.5 font-medium whitespace-nowrap disabled:opacity-40 disabled:cursor-not-allowed ${sizing} ${VARIANTS[variant]} ${className}`}
      disabled={busy || props.disabled}
      {...props}
    >
      {busy ? <Spinner size={15} /> : null}
      {children}
    </button>
  );
}

export function Spinner({ size = 18 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" className="spin" aria-label="Loading">
      <circle cx="12" cy="12" r="9" fill="none" stroke="currentColor" strokeOpacity="0.2" strokeWidth="2.5" />
      <path d="M21 12a9 9 0 0 0-9-9" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" />
    </svg>
  );
}

type Tone = "blue" | "green" | "orange" | "red" | "purple" | "gray";

const TONES: Record<Tone, string> = {
  blue: "bg-[var(--accent-soft)] text-[var(--accent)]",
  green: "bg-[var(--green-soft)] text-[var(--green)]",
  orange: "bg-[var(--orange-soft)] text-[var(--orange)]",
  red: "bg-[var(--red-soft)] text-[var(--red)]",
  purple: "bg-[var(--purple-soft)] text-[var(--purple)]",
  gray: "bg-[var(--line)] text-[var(--text-2)]",
};

export function Pill({ tone = "gray", children, title }: { tone?: Tone; children: ReactNode; title?: string }) {
  return (
    <span
      title={title}
      className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-[0.72rem] font-semibold tracking-[0.01em] whitespace-nowrap ${TONES[tone]}`}
    >
      {children}
    </span>
  );
}

const TIER_TONE: Record<number, Tone> = { 0: "gray", 1: "blue", 2: "orange", 3: "red" };

export function TierBadge({ tier }: { tier: number }) {
  const who = tier >= 2 ? "HOD only" : "Committee or HOD";
  return (
    <Pill tone={TIER_TONE[tier] ?? "red"} title={`Tier ${tier}: ${who}`}>
      T{tier}
    </Pill>
  );
}

const STATUS_TONE: Record<string, Tone> = {
  pending: "orange",
  approved: "blue",
  executed: "green",
  sent: "green",
  rejected: "gray",
  refused: "red",
  expired: "gray",
  failed: "red",
  active: "green",
  awaiting_hod_confirmation: "orange",
  draft: "gray",
  completed: "blue",
  cancelled: "gray",
  pending_approval: "orange",
  ok: "green",
  approval_required: "orange",
  error: "red",
};

const STATUS_TEXT: Record<string, string> = {
  awaiting_hod_confirmation: "Awaiting HOD",
  pending_approval: "Awaiting approval",
  approval_required: "Needs approval",
  executed: "Done",
};

export function StatusPill({ status }: { status: string }) {
  const text = STATUS_TEXT[status] ?? status.charAt(0).toUpperCase() + status.slice(1).replace(/_/g, " ");
  return <Pill tone={STATUS_TONE[status] ?? "gray"}>{text}</Pill>;
}

export function Simulated() {
  return (
    <Pill tone="purple" title="No real message was sent">
      SIMULATED
    </Pill>
  );
}

export function Empty({ icon, text }: { icon: ReactNode; text: string }) {
  return (
    <div className="flex flex-col items-center justify-center gap-2 py-14 text-[var(--text-3)]">
      <div className="opacity-70">{icon}</div>
      <p className="text-sm">{text}</p>
    </div>
  );
}

export function PageHeader({ title, action, children }: { title: ReactNode; action?: ReactNode; children?: ReactNode }) {
  return (
    <div className="mb-6 flex flex-wrap items-end justify-between gap-3">
      <div className="min-w-0">
        <h1 className="title-xl">{title}</h1>
        {children}
      </div>
      {action}
    </div>
  );
}

export function Section({ title, aside, children }: { title: string; aside?: ReactNode; children: ReactNode }) {
  return (
    <section className="fade-in">
      <div className="mb-2.5 flex items-center justify-between gap-3">
        <h2 className="title-md">{title}</h2>
        {aside}
      </div>
      {children}
    </section>
  );
}

export function ErrorNote({ text }: { text: string }) {
  return <p className="rounded-xl bg-[var(--red-soft)] px-3 py-2 text-sm text-[var(--red)]">{text}</p>;
}

export function TableWrap({ children }: { children: ReactNode }) {
  return <div className="overflow-x-auto">{children}</div>;
}
