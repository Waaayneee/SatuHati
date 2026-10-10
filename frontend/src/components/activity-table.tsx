import { humanize, roleLabel, stamp } from "@/lib/format";
import type { AuditRow } from "@/lib/types";
import { StatusPill, TableWrap } from "./ui";

export function ActivityTable({ rows, showMission = true }: { rows: AuditRow[]; showMission?: boolean }) {
  return (
    <TableWrap>
      <table className="grid-table">
        <thead>
          <tr>
            <th>Time</th>
            <th>Actor</th>
            <th>Role</th>
            <th>Event</th>
            <th>Tool</th>
            {showMission ? <th>Mission</th> : null}
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((r) => (
            <tr key={r.id}>
              <td className="whitespace-nowrap text-[var(--text-2)] tabular-nums">{stamp(r.at)}</td>
              <td className="max-w-[16rem] truncate" title={r.actor}>
                {r.actor_label}
              </td>
              <td>{roleLabel(r.actor_role)}</td>
              <td title={r.error ?? undefined}>{humanize(r.event_type)}</td>
              <td className="text-[var(--text-2)]">{r.tool_name ?? "—"}</td>
              {showMission ? <td className="whitespace-nowrap">{r.mission_code ?? "—"}</td> : null}
              <td>
                <StatusPill status={r.status} />
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </TableWrap>
  );
}
