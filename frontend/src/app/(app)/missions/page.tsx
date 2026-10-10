"use client";

import { useRouter } from "next/navigation";
import { useCallback, useState, type FormEvent, type ReactNode } from "react";
import { PlusIcon, TargetIcon } from "@/components/icons";
import { useSession } from "@/components/session";
import { Sheet } from "@/components/sheet";
import { useToast } from "@/components/toast";
import { Button, Empty, ErrorNote, PageHeader, Spinner, StatusPill, TableWrap } from "@/components/ui";
import { api } from "@/lib/api";
import { day, money } from "@/lib/format";
import { errorText, useLoad } from "@/lib/hooks";
import type { Mission } from "@/lib/types";

export default function MissionsPage() {
  const router = useRouter();
  const { data, error, loading, reload } = useLoad<Mission[]>("/missions");
  const [open, setOpen] = useState(false);
  const close = useCallback(() => setOpen(false), []);

  return (
    <>
      <PageHeader
        title="Missions"
        action={
          <Button onClick={() => setOpen(true)}>
            <PlusIcon size={16} /> New
          </Button>
        }
      />

      {error ? <ErrorNote text={error} /> : null}
      {loading ? (
        <div className="flex justify-center py-16 text-[var(--text-3)]">
          <Spinner />
        </div>
      ) : data && data.length === 0 ? (
        <div className="card">
          <Empty icon={<TargetIcon size={30} />} text="No missions yet" />
        </div>
      ) : data ? (
        <TableWrap>
          <table className="grid-table fade-in">
            <thead>
              <tr>
                <th>Mission</th>
                <th>Product</th>
                <th>Qty</th>
                <th>Target</th>
                <th>Budget</th>
                <th>Deadline</th>
                <th>Status</th>
                <th>Owner</th>
              </tr>
            </thead>
            <tbody>
              {data.map((m) => (
                <tr key={m.id} className="clickable" onClick={() => router.push(`/missions/${m.id}`)}>
                  <td className="font-semibold whitespace-nowrap">{m.code}</td>
                  <td>{m.product ?? "—"}</td>
                  <td className="tabular-nums">{m.quantity ?? "—"}</td>
                  <td className="tabular-nums">{money(m.target_total_myr)}</td>
                  <td className="tabular-nums">{money(m.hard_budget_myr)}</td>
                  <td className="whitespace-nowrap">{day(m.delivery_deadline)}</td>
                  <td>
                    <StatusPill status={m.status} />
                  </td>
                  <td className="text-[var(--text-2)]">{m.owner_email?.split("@")[0] ?? "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </TableWrap>
      ) : null}

      <Sheet open={open} onClose={close} title="New mission">
        <NewMissionForm
          onCreated={(mission) => {
            close();
            reload();
            router.push(`/missions/${mission.id}`);
          }}
        />
      </Sheet>
    </>
  );
}

const EMPTY = {
  goal_text: "",
  product: "",
  quantity: "",
  target_total_myr: "",
  hard_budget_myr: "",
  minimum_quality: "4.0",
  delivery_deadline: "",
  max_rounds: "3",
};

function NewMissionForm({ onCreated }: { onCreated: (mission: Mission) => void }) {
  const { isHod } = useSession();
  const toast = useToast();
  const [form, setForm] = useState(EMPTY);
  const [confirmNow, setConfirmNow] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const set = (key: keyof typeof EMPTY) => (e: { target: { value: string } }) =>
    setForm((f) => ({ ...f, [key]: e.target.value }));
  const overBudget =
    form.target_total_myr !== "" && form.hard_budget_myr !== "" && Number(form.target_total_myr) > Number(form.hard_budget_myr);

  async function submit(event: FormEvent) {
    event.preventDefault();
    setBusy(true);
    setError(null);
    try {
      const mission = await api<Mission>("/missions", {
        method: "POST",
        body: {
          goal_text: form.goal_text.trim(),
          product: form.product.trim(),
          quantity: Number(form.quantity),
          target_total_myr: Number(form.target_total_myr),
          hard_budget_myr: Number(form.hard_budget_myr),
          minimum_quality: Number(form.minimum_quality),
          delivery_deadline: form.delivery_deadline,
          max_rounds: Number(form.max_rounds),
          confirm_limits: isHod && confirmNow,
        },
      });
      toast(`${mission.code} created`);
      setForm(EMPTY);
      setConfirmNow(false);
      onCreated(mission);
    } catch (e) {
      setError(errorText(e));
    } finally {
      setBusy(false);
    }
  }

  return (
    <form onSubmit={submit} className="flex flex-col gap-3.5">
      <Field label="Goal">
        <textarea
          className="field min-h-[76px] resize-y"
          placeholder="300 custom tote bags for our tech event"
          value={form.goal_text}
          onChange={set("goal_text")}
          required
          maxLength={2000}
        />
      </Field>
      <div className="grid grid-cols-2 gap-3">
        <Field label="Product">
          <input className="field" placeholder="Custom tote bags" value={form.product} onChange={set("product")} required />
        </Field>
        <Field label="Quantity">
          <input className="field" type="number" min={1} placeholder="300" value={form.quantity} onChange={set("quantity")} required />
        </Field>
        <Field label="Target (RM)">
          <input
            className="field"
            type="number"
            min={0}
            step="0.01"
            placeholder="1350"
            value={form.target_total_myr}
            onChange={set("target_total_myr")}
            required
          />
        </Field>
        <Field label="Hard budget (RM)">
          <input
            className="field"
            type="number"
            min={0.01}
            step="0.01"
            placeholder="1500"
            value={form.hard_budget_myr}
            onChange={set("hard_budget_myr")}
            required
          />
        </Field>
        <Field label="Min. quality (0–5)">
          <input
            className="field"
            type="number"
            min={0}
            max={5}
            step="0.1"
            value={form.minimum_quality}
            onChange={set("minimum_quality")}
            required
          />
        </Field>
        <Field label="Max rounds">
          <input className="field" type="number" min={1} max={10} value={form.max_rounds} onChange={set("max_rounds")} required />
        </Field>
        <Field label="Deadline" wide>
          <input className="field" type="date" value={form.delivery_deadline} onChange={set("delivery_deadline")} required />
        </Field>
      </div>
      {overBudget ? <p className="text-sm text-[var(--red)]">Target is above the hard budget</p> : null}
      {isHod ? (
        <label className="flex cursor-pointer items-center justify-between rounded-xl bg-[var(--surface-2)] px-3.5 py-2.5 text-sm">
          <span>Confirm limits now</span>
          <input type="checkbox" className="h-4 w-4 accent-[var(--accent)]" checked={confirmNow} onChange={(e) => setConfirmNow(e.target.checked)} />
        </label>
      ) : null}
      {error ? <ErrorNote text={error} /> : null}
      <Button type="submit" busy={busy} disabled={overBudget} className="mt-1 w-full">
        Create
      </Button>
    </form>
  );
}

function Field({ label, wide, children }: { label: string; wide?: boolean; children: ReactNode }) {
  return (
    <label className={`flex flex-col gap-1 ${wide ? "col-span-2" : ""}`}>
      <span className="label">{label}</span>
      {children}
    </label>
  );
}
