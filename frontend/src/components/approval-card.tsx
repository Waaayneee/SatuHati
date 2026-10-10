"use client";

import Link from "next/link";
import { useState } from "react";
import { ApiError, api } from "@/lib/api";
import { actionLabel, countdown, money, stamp } from "@/lib/format";
import { announceApprovalsChanged, errorText, useNow } from "@/lib/hooks";
import type { ApprovalDetail, ApprovalSummary } from "@/lib/types";
import { CheckIcon, ChevronIcon, ClockIcon, LockIcon, XIcon } from "./icons";
import { useToast } from "./toast";
import { Button, Spinner, StatusPill, TierBadge } from "./ui";

function BudgetBar({ proposed, target, limit }: { proposed: number; target: number | null; limit: number | null }) {
  if (limit === null || limit <= 0) return <span className="font-semibold tabular-nums">{money(proposed)}</span>;
  const over = proposed > limit;
  const fill = Math.min(proposed / limit, 1) * 100;
  const targetAt = target !== null ? Math.min(target / limit, 1) * 100 : null;
  return (
    <div className="flex flex-col gap-1.5">
      <div className="flex flex-wrap items-baseline gap-x-3 gap-y-0.5 text-[0.8125rem]">
        <span className={`font-semibold tabular-nums ${over ? "text-[var(--red)]" : ""}`}>{money(proposed)}</span>
        {target !== null ? <span className="text-[var(--text-2)] tabular-nums">target {money(target)}</span> : null}
        <span className="text-[var(--text-2)] tabular-nums">limit {money(limit)}</span>
      </div>
      <div className="relative h-1.5 w-full max-w-xs overflow-hidden rounded-full bg-[var(--line)]">
        <div
          className="absolute inset-y-0 left-0 rounded-full"
          style={{ width: `${fill}%`, background: over ? "var(--red)" : "var(--green)" }}
        />
        {targetAt !== null ? (
          <div className="absolute inset-y-0 w-0.5 bg-[var(--text)] opacity-50" style={{ left: `calc(${targetAt}% - 1px)` }} />
        ) : null}
      </div>
    </div>
  );
}

export function ApprovalCard({
  approval,
  onDecided,
  showMission = true,
}: {
  approval: ApprovalSummary;
  onDecided: () => void;
  showMission?: boolean;
}) {
  const toast = useToast();
  const now = useNow();
  const [open, setOpen] = useState(false);
  const [detail, setDetail] = useState<ApprovalDetail | null>(null);
  const [mode, setMode] = useState<"approved" | "rejected" | null>(null);
  const [reason, setReason] = useState("");
  const [busy, setBusy] = useState(false);
  const pending = approval.status === "pending";
  const isMessage = approval.action_type.startsWith("send_");

  async function toggle() {
    const next = !open;
    setOpen(next);
    if (next && !detail) {
      try {
        setDetail(await api<ApprovalDetail>(`/approvals/${approval.id}`));
      } catch (e) {
        toast(errorText(e), "error");
      }
    }
  }

  async function decide() {
    if (!mode || !reason.trim()) return;
    setBusy(true);
    try {
      const result = await api<ApprovalDetail>(`/approvals/${approval.id}/decision`, {
        method: "POST",
        body: { decision: mode, reason: reason.trim() },
      });
      if (result.status === "executed") toast(isMessage ? "Approved · sent (simulated)" : "Approved · done");
      else if (result.status === "rejected") toast("Rejected");
      else if (result.status === "failed")
        toast(`Refused at execution: ${String(result.execution_result?.error ?? "check failed")}`, "error");
      setMode(null);
      setReason("");
      setDetail(result);
      announceApprovalsChanged();
      onDecided();
    } catch (e) {
      toast(e instanceof ApiError && e.status === 403 ? `Not allowed: ${e.message}` : errorText(e), "error");
      if (e instanceof ApiError && e.status === 409) onDecided();
    } finally {
      setBusy(false);
    }
  }

  const left = countdown(approval.expires_at, now);

  return (
    <article className="card fade-in overflow-hidden">
      <div className="flex flex-col gap-3 p-4 sm:p-5">
        <div className="flex flex-wrap items-center gap-2">
          <TierBadge tier={approval.tier} />
          <span className="font-semibold">{actionLabel(approval.action_type)}</span>
          {approval.recipient_name ? (
            <span className="text-[var(--text-2)]">→ {approval.recipient_name}</span>
          ) : null}
          {showMission && approval.mission_code && approval.mission_id ? (
            <Link href={`/missions/${approval.mission_id}`} className="text-[0.8125rem] text-[var(--accent)] hover:underline">
              {approval.mission_code}
            </Link>
          ) : null}
          <span className="ml-auto flex items-center gap-2">
            {pending && left ? (
              <span
                className={`flex items-center gap-1 text-[0.8125rem] tabular-nums ${left === "Expired" ? "text-[var(--red)]" : "text-[var(--text-2)]"}`}
                title={`Expires ${stamp(approval.expires_at)}`}
              >
                <ClockIcon size={14} /> {left}
              </span>
            ) : null}
            {!pending ? <StatusPill status={approval.status} /> : null}
          </span>
        </div>

        <div className="label">
          {approval.requester_label}
          {approval.tier >= 2 ? (
            <span className="ml-2 inline-flex items-center gap-1 text-[var(--orange)]">
              <LockIcon size={12} /> HOD
            </span>
          ) : null}
        </div>

        {approval.preview ? (
          <blockquote className="rounded-xl border-l-[3px] border-[var(--line-strong)] bg-[var(--surface-2)] px-3.5 py-2.5 text-[0.875rem] whitespace-pre-wrap text-[var(--text)]">
            {approval.preview}
          </blockquote>
        ) : null}

        {approval.proposed_total_myr !== null ? (
          <BudgetBar
            proposed={approval.proposed_total_myr}
            target={approval.target_total_myr}
            limit={approval.hard_budget_myr}
          />
        ) : null}

        <div className="flex flex-wrap items-center gap-2 pt-1">
          {pending && mode === null ? (
            <>
              <Button size="sm" variant="success" onClick={() => setMode("approved")}>
                <CheckIcon size={15} /> Approve
              </Button>
              <Button size="sm" variant="secondary" onClick={() => setMode("rejected")}>
                <XIcon size={15} /> Reject
              </Button>
            </>
          ) : null}
          <button
            onClick={toggle}
            className="press ml-auto flex items-center gap-0.5 rounded-full px-2 py-1 text-[0.8125rem] text-[var(--text-2)] hover:bg-[var(--line)]"
            aria-expanded={open}
          >
            Details
            <ChevronIcon size={14} className={`transition-transform duration-200 ${open ? "rotate-90" : ""}`} />
          </button>
        </div>

        {mode !== null ? (
          <form
            className="fade-in flex flex-col gap-2 sm:flex-row"
            onSubmit={(e) => {
              e.preventDefault();
              decide();
            }}
          >
            <input
              className="field flex-1"
              autoFocus
              placeholder={mode === "approved" ? "Reason for approving" : "Reason for rejecting"}
              aria-label="Reason"
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              maxLength={1000}
            />
            <div className="flex gap-2">
              <Button type="submit" busy={busy} disabled={!reason.trim()} variant={mode === "approved" ? "success" : "danger"}>
                {mode === "approved" ? "Approve" : "Reject"}
              </Button>
              <Button type="button" variant="ghost" onClick={() => setMode(null)} aria-label="Cancel">
                <XIcon size={16} />
              </Button>
            </div>
          </form>
        ) : null}
      </div>

      {open ? (
        <div className="fade-in border-t border-[var(--line)] bg-[var(--surface-2)] px-4 py-4 text-[0.8125rem] sm:px-5">
          {detail ? <DetailBody detail={detail} /> : <Spinner size={16} />}
        </div>
      ) : null}
    </article>
  );
}

function DetailBody({ detail }: { detail: ApprovalDetail }) {
  const snapshot = detail.content_snapshot;
  const rows: [string, string][] = [];
  if (typeof snapshot.recipient === "string") rows.push(["To", snapshot.recipient]);
  if (typeof snapshot.kind === "string") rows.push(["Kind", snapshot.kind]);
  rows.push(["Requested", stamp(detail.created_at)]);
  rows.push(["Expires", stamp(detail.expires_at)]);
  rows.push(["Eligible", detail.eligible_roles.map((r) => (r === "hod" ? "HOD" : "Committee (not requester)")).join(", ")]);
  if (detail.approver_email) rows.push(["Decided by", `${detail.approver_email} (${detail.approver_role === "hod" ? "HOD" : "Committee"})`]);
  if (detail.decision_reason) rows.push(["Reason", detail.decision_reason]);
  if (detail.execution_result) {
    const error = detail.execution_result.error;
    rows.push(["Result", typeof error === "string" ? error : detail.execution_result.is_simulated ? "Sent (simulated)" : "Done"]);
  }
  rows.push(["Hash", `${detail.content_hash.slice(0, 16)}…`]);
  if (!detail.can_decide && detail.cannot_decide_reason && detail.status === "pending") {
    rows.push(["You", detail.cannot_decide_reason]);
  }

  return (
    <div className="flex flex-col gap-3">
      {typeof snapshot.body === "string" ? (
        <p className="rounded-xl bg-[var(--surface)] p-3 whitespace-pre-wrap">{snapshot.body}</p>
      ) : (
        <pre className="overflow-x-auto rounded-xl bg-[var(--surface)] p-3 text-[0.75rem]">{JSON.stringify(snapshot, null, 2)}</pre>
      )}
      <dl className="grid grid-cols-[auto_1fr] gap-x-4 gap-y-1">
        {rows.map(([k, v]) => (
          <div key={k} className="contents">
            <dt className="text-[var(--text-3)]">{k}</dt>
            <dd className="break-words">{v}</dd>
          </div>
        ))}
      </dl>
    </div>
  );
}
