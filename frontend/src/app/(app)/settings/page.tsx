"use client";

import { LockIcon } from "@/components/icons";
import { useSession } from "@/components/session";
import { Empty, ErrorNote, PageHeader, Pill, Section, Spinner, StatusPill, TableWrap } from "@/components/ui";
import { roleLabel } from "@/lib/format";
import { useLoad } from "@/lib/hooks";
import type { UserRow } from "@/lib/types";

export default function SettingsPage() {
  const { isHod } = useSession();
  if (!isHod) {
    return (
      <>
        <PageHeader title="Settings" />
        <div className="card">
          <Empty icon={<LockIcon size={28} />} text="HOD only" />
        </div>
      </>
    );
  }
  return <Users />;
}

function Users() {
  const { data, error, loading } = useLoad<UserRow[]>("/users");
  return (
    <>
      <PageHeader title="Settings" />
      <Section title="People" aside={<span className="label">Read only</span>}>
        {error ? <ErrorNote text={error} /> : null}
        {loading ? (
          <div className="flex justify-center py-10 text-[var(--text-3)]">
            <Spinner />
          </div>
        ) : (
          <TableWrap>
            <table className="grid-table">
              <thead>
                <tr>
                  <th>Email</th>
                  <th>Name</th>
                  <th>Role</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {data?.map((u) => (
                  <tr key={u.id}>
                    <td className="font-medium">{u.email}</td>
                    <td>{u.name ?? "—"}</td>
                    <td>
                      <span className="flex gap-1">
                        {u.roles.map((r) => (
                          <Pill key={r} tone={r === "hod" ? "blue" : "gray"}>
                            {roleLabel(r)}
                          </Pill>
                        ))}
                      </span>
                    </td>
                    <td>
                      <StatusPill status={u.status} />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </TableWrap>
        )}
      </Section>
    </>
  );
}
