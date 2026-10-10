"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import type { ApprovalSummary } from "@/lib/types";
import { GearIcon, InboxIcon, ListIcon, Logo, TargetIcon } from "./icons";
import { ProfileMenu } from "./profile-menu";
import { useSession } from "./session";

export function Nav() {
  const pathname = usePathname();
  const { isHod } = useSession();
  const [pending, setPending] = useState(0);

  useEffect(() => {
    let cancelled = false;
    const load = () =>
      api<ApprovalSummary[]>("/approvals?status=pending")
        .then((items) => !cancelled && setPending(items.length))
        .catch(() => {});
    load();
    const timer = setInterval(load, 30000);
    window.addEventListener("kawteam:approvals-changed", load);
    return () => {
      cancelled = true;
      clearInterval(timer);
      window.removeEventListener("kawteam:approvals-changed", load);
    };
  }, []);

  const items = [
    { href: "/missions", label: "Missions", icon: <TargetIcon size={16} /> },
    { href: "/approvals", label: "Approvals", icon: <InboxIcon size={16} />, badge: pending },
    { href: "/audit", label: "Audit", icon: <ListIcon size={16} /> },
    ...(isHod ? [{ href: "/settings", label: "Settings", icon: <GearIcon size={16} /> }] : []),
  ];

  return (
    <header className="chrome sticky top-0 z-30">
      <div className="mx-auto flex h-14 max-w-6xl items-center gap-3 px-4 sm:px-6">
        <Link href="/missions" className="flex shrink-0 items-center gap-2" aria-label="KawTeam home">
          <Logo size={26} />
          <span className="hidden text-[1.05rem] font-semibold tracking-[-0.02em] sm:inline">KawTeam</span>
        </Link>

        <nav className="flex min-w-0 flex-1 justify-center overflow-x-auto">
          <div className="flex gap-0.5 rounded-full bg-[var(--line)] p-0.5">
            {items.map((item) => {
              const active = pathname === item.href || pathname.startsWith(`${item.href}/`);
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  aria-label={item.badge ? `${item.label}, ${item.badge} pending` : item.label}
                  className={`press flex items-center gap-1.5 rounded-full px-3 py-1.5 text-[0.8125rem] font-medium whitespace-nowrap ${
                    active ? "bg-[var(--accent)] text-[var(--on-accent)] shadow-[var(--shadow-sm)]" : "text-[var(--text-2)] hover:text-[var(--text)]"
                  }`}
                >
                  {item.icon}
                  <span className="hidden md:inline">{item.label}</span>
                  {item.badge ? (
                    <span className="min-w-[1.15rem] rounded-full bg-[var(--red)] px-1 text-center text-[0.68rem] leading-[1.15rem] font-semibold text-[var(--surface)]">
                      {item.badge}
                    </span>
                  ) : null}
                </Link>
              );
            })}
          </div>
        </nav>

        <div className="flex shrink-0 items-center">
          <ProfileMenu />
        </div>
      </div>
    </header>
  );
}

export function NavPlaceholder() {
  return <header className="chrome sticky top-0 z-30 h-14" />;
}
