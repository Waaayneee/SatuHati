"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { Fragment, useState } from "react";
import { ApprovalCard } from "@/components/approval-card";
import { ArrowLeftIcon, LockIcon, SendIcon, ShieldIcon, SparkIcon } from "@/components/icons";
import { useSession } from "@/components/session";
import { useToast } from "@/components/toast";
import { ActivityTable } from "@/components/activity-table";
import { Button, Empty, ErrorNote, Pill, Section, Simulated, Spinner, StatusPill, TableWrap } from "@/components/ui";
import { ApiError, api } from "@/lib/api";
import { day, humanize, money, stamp } from "@/lib/format";
import { announceApprovalsChanged, errorText, useLoad } from "@/lib/hooks";
import type { AgentRun, AuditRow, Mission, MissionDetail } from "@/lib/types";

export function MissionView() {
  const { id } = useParams<{ id: string }>();
  const { isHod } = useSession();
  const toast = useToast();
  const detail = useLoad<MissionDetail>(`/missions/${id}`);
  const activity = useLoad<AuditRow[]>(`/audit?mission_id=${id}&limit=100`);
  const [confirming, setConfirming] = useState(false);

  const refresh = () => {
    detail.reload();
    activity.reload();
  };

  async function confirmLimits() {
    setConfirming(true);
    try {
      await api<Mission>(`/missions/${id}/confirm-limits`, { method: "POST" });
      toast("Limits confirmed · mission active");
      refresh();
    } catch (e) {
      toast(errorText(e), "error");
    } finally {
      setConfirming(false);
    }
  }

  if (detail.error && !detail.data) return <ErrorNote text={detail.error} />;
  if (!detail.data) {
    return (
      <div className="flex justify-center py-16 text-[var(--text-3)]">
        <Spinner />
      </div>
    );
  }

  const { mission, approvals, messages, quotations } = detail.data;
  const awaiting = mission.status === "awaiting_hod_confirmation" || mission.status === "draft";

  return (
    <div className="flex flex-col gap-8">
      <div>
        <Link href="/missions" className="press mb-3 inline-flex items-center gap-0.5 text-[0.8125rem] text-[var(--accent)]">
          <ArrowLeftIcon size={15} /> Missions
        </Link>
        <div className="flex flex-wrap items-center gap-3">
          <h1 className="title-xl">{mission.code}</h1>
          <StatusPill status={mission.status} />
        </div>
        <p className="mt-1.5 max-w-3xl text-[var(--text-2)]">{mission.goal_text}</p>
      </div>

      <Facts mission={mission} />

      {awaiting ? (
        <div className="card fade-in flex flex-wrap items-center gap-3 p-4">
          <span className="flex h-9 w-9 items-center justify-center rounded-full bg-[var(--orange-soft)] text-[var(--orange)]">
            {isHod ? <ShieldIcon size={18} /> : <LockIcon size={18} />}
          </span>
          <span className="flex-1 font-medium">{isHod ? "Confirm these limits to activate" : "Waiting for HOD to confirm limits"}</span>
          {isHod ? (
            <Button onClick={confirmLimits} busy={confirming}>
              Confirm limits
            </Button>
          ) : null}
        </div>
      ) : null}

      <AgentPanel missionId={mission.id} onDone={refresh} />

      <Section title="Approvals" aside={approvals.length ? <span className="label">{approvals.length}</span> : null}>
        {approvals.length === 0 ? (
          <div className="card">
            <Empty icon={<ShieldIcon size={26} />} text="None yet" />
          </div>
        ) : (
          <div className="flex flex-col gap-3">
            {approvals.map((a) => (
              <ApprovalCard key={a.id} approval={a} showMission={false} onDecided={refresh} />
            ))}
          </div>
        )}
      </Section>

      <Section title="Messages">
        {messages.length === 0 ? (
          <div className="card">
            <Empty icon={<SendIcon size={26} />} text="No messages" />
          </div>
        ) : (
          <MessagesTable messages={messages} />
        )}
      </Section>

      {quotations.length ? (
        <Section title="Quotes">
          <TableWrap>
            <table className="grid-table">
              <thead>
                <tr>
                  <th>Supplier</th>
                  <th>Total</th>
                  <th>Unit</th>
                  <th>State</th>
                  <th>Source</th>
                </tr>
              </thead>
              <tbody>
                {quotations.map((q) => (
                  <tr key={q.id}>
                    <td className="font-medium">{q.supplier}</td>
                    <td className="tabular-nums">{money(q.total_price)}</td>
                    <td className="tabular-nums">{money(q.unit_price)}</td>
                    <td>{humanize(q.verification_state)}</td>
                    <td>{q.is_simulated ? <Pill tone="purple">DEMO DATA</Pill> : "Verified source"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </TableWrap>
        </Section>
      ) : null}

      <Section title="Activity">
        {activity.data && activity.data.length ? (
          <ActivityTable rows={activity.data} showMission={false} />
        ) : (
          <div className="card">
            <Empty icon={<SparkIcon size={26} />} text={activity.loading ? "Loading…" : "No visible activity"} />
          </div>
        )}
      </Section>
    </div>
  );
}

function Facts({ mission }: { mission: Mission }) {
  const facts: [string, string][] = [
    ["Product", mission.product ?? "—"],
    ["Quantity", mission.quantity?.toLocaleString("en-MY") ?? "—"],
    ["Target", money(mission.target_total_myr)],
    ["Hard budget", money(mission.hard_budget_myr)],
    ["Min. quality", mission.minimum_quality !== null ? `${mission.minimum_quality.toFixed(1)} / 5` : "—"],
    ["Deadline", day(mission.delivery_deadline)],
    ["Max rounds", String(mission.max_rounds)],
  ];
  return (
    <div className="grid grid-cols-2 gap-2.5 sm:grid-cols-4 lg:grid-cols-7">
      {facts.map(([label, value]) => (
        <div key={label} className="card fade-in px-3.5 py-3">
          <div className="label">{label}</div>
          <div className="mt-0.5 truncate font-semibold tabular-nums" title={value}>
            {value}
          </div>
        </div>
      ))}
    </div>
  );
}

const RUN_TONE: Record<AgentRun["status"], "green" | "orange" | "red" | "gray"> = {
  completed: "green",
  approval_required: "orange",
  max_iterations: "gray",
  refused: "red",
  incomplete: "red",
  error: "red",
};

function AgentPanel({ missionId, onDone }: { missionId: string; onDone: () => void }) {
  const toast = useToast();
  const [prompt, setPrompt] = useState("");
  const [busy, setBusy] = useState(false);
  const [run, setRun] = useState<AgentRun | null>(null);

  async function submit(event: { preventDefault(): void }) {
    event.preventDefault();
    if (!prompt.trim() || busy) return;
    setBusy(true);
    try {
      const result = await api<AgentRun>(`/missions/${missionId}/agent/run`, {
        method: "POST",
        body: { prompt: prompt.trim() },
      });
      setRun(result);
      if (result.approvals.length) announceApprovalsChanged();
      onDone();
    } catch (e) {
      toast(e instanceof ApiError && e.status === 503 ? e.message : errorText(e), "error");
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="card fade-in overflow-hidden">
      <form onSubmit={submit} className="flex flex-col gap-3 p-4 sm:p-5">
        <div className="flex items-center gap-2">
          <span className="flex h-7 w-7 items-center justify-center rounded-full bg-[var(--accent-soft)] text-[var(--accent)]">
            <SparkIcon size={16} />
          </span>
          <h2 className="title-md">Agent</h2>
        </div>
        <textarea
          className="field min-h-[70px] resize-y"
          placeholder="Find suppliers and send an enquiry to the cheapest within budget"
          aria-label="Instruction for the agent"
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          maxLength={4000}
          onKeyDown={(e) => {
            if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) submit(e);
          }}
        />
        <div className="flex items-center justify-between gap-3">
          <span className="label">{busy ? "Working…" : "Every external step waits for approval"}</span>
          <Button type="submit" busy={busy} disabled={!prompt.trim()}>
            Run agent
          </Button>
        </div>
      </form>

      {run ? (
        <div className="fade-in flex flex-col gap-3 border-t border-[var(--line)] bg-[var(--surface-2)] p-4 sm:p-5">
          <div className="flex flex-wrap items-center gap-2">
            <Pill tone={RUN_TONE[run.status]}>{humanize(run.status)}</Pill>
            {run.tool_calls.map((call, i) => (
              <Pill key={i} tone={call.status === "ok" ? "gray" : call.status === "approval_required" ? "orange" : "red"} title={call.reason ?? undefined}>
                {call.name}
                {call.tier !== null ? ` · T${call.tier}` : ""}
              </Pill>
            ))}
          </div>
          {run.final_text ? <p className="text-[0.875rem] whitespace-pre-wrap">{run.final_text}</p> : null}
        </div>
      ) : null}
    </section>
  );
}

function MessagesTable({ messages }: { messages: MissionDetail["messages"] }) {
  const [openId, setOpenId] = useState<string | null>(null);
  return (
    <TableWrap>
      <table className="grid-table">
        <thead>
          <tr>
            <th>Supplier</th>
            <th>Kind</th>
            <th>Total</th>
            <th>Status</th>
            <th>Mode</th>
            <th>Time</th>
          </tr>
        </thead>
        <tbody>
          {messages.map((m) => (
            <Fragment key={m.id}>
              <tr className="clickable" onClick={() => setOpenId(openId === m.id ? null : m.id)}>
                <td className="font-medium">{m.supplier ?? "—"}</td>
                <td>{humanize(m.kind)}</td>
                <td className="tabular-nums">{money(m.proposed_total_myr)}</td>
                <td>
                  <StatusPill status={m.status} />
                </td>
                <td>{m.is_simulated ? <Simulated /> : "Live"}</td>
                <td className="whitespace-nowrap text-[var(--text-2)]">{stamp(m.sent_at ?? m.created_at)}</td>
              </tr>
              {openId === m.id ? (
                <tr>
                  <td colSpan={6} className="bg-[var(--surface-2)]">
                    <div className="label mb-1">{m.recipient}</div>
                    <p className="whitespace-pre-wrap">{m.body}</p>
                  </td>
                </tr>
              ) : null}
            </Fragment>
          ))}
        </tbody>
      </table>
    </TableWrap>
  );
}
