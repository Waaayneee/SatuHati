"use client";

import { useState } from "react";
import { ApprovalCard } from "@/components/approval-card";
import { InboxIcon } from "@/components/icons";
import { Empty, ErrorNote, PageHeader, Spinner } from "@/components/ui";
import { useLoad } from "@/lib/hooks";
import type { ApprovalSummary } from "@/lib/types";

const FILTERS = [
  { key: "pending", label: "Pending" },
  { key: "all", label: "All" },
] as const;

export default function ApprovalsPage() {
  const [filter, setFilter] = useState<"pending" | "all">("pending");
  const { data, error, loading, reload } = useLoad<ApprovalSummary[]>(`/approvals?status=${filter}`);

  return (
    <>
      <PageHeader
        title="Approvals"
        action={
          <div className="flex rounded-full bg-[var(--line)] p-0.5" role="tablist">
            {FILTERS.map((f) => (
              <button
                key={f.key}
                role="tab"
                aria-selected={filter === f.key}
                onClick={() => setFilter(f.key)}
                className={`press rounded-full px-3.5 py-1.5 text-[0.8125rem] font-medium ${
                  filter === f.key ? "bg-[var(--surface)] shadow-[var(--shadow-sm)]" : "text-[var(--text-2)]"
                }`}
              >
                {f.label}
              </button>
            ))}
          </div>
        }
      />
      {error ? <ErrorNote text={error} /> : null}
      {loading ? (
        <div className="flex justify-center py-16 text-[var(--text-3)]">
          <Spinner />
        </div>
      ) : data && data.length === 0 ? (
        <div className="card">
          <Empty icon={<InboxIcon size={30} />} text={filter === "pending" ? "Nothing waiting" : "No approvals yet"} />
        </div>
      ) : (
        <div className="flex flex-col gap-3">
          {data?.map((a) => <ApprovalCard key={a.id} approval={a} onDecided={reload} />)}
        </div>
      )}
    </>
  );
}
