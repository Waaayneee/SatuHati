"use client";

import { ActivityTable } from "@/components/activity-table";
import { ListIcon } from "@/components/icons";
import { Button, Empty, ErrorNote, PageHeader, Spinner } from "@/components/ui";
import { useLoad } from "@/lib/hooks";
import type { AuditRow } from "@/lib/types";

export default function AuditPage() {
  const { data, error, loading, reload } = useLoad<AuditRow[]>("/audit?limit=300");

  return (
    <>
      <PageHeader
        title="Audit"
        action={
          <Button variant="secondary" size="sm" onClick={reload}>
            Refresh
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
          <Empty icon={<ListIcon size={30} />} text="No events yet" />
        </div>
      ) : data ? (
        <div className="fade-in">
          <ActivityTable rows={data} />
        </div>
      ) : null}
    </>
  );
}
