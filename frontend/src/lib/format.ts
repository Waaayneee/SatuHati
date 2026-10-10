const myr = new Intl.NumberFormat("en-MY", { maximumFractionDigits: 2 });

export function money(value: number | null | undefined): string {
  if (value === null || value === undefined) return "—";
  return `RM${myr.format(value)}`;
}

export function day(value: string | null | undefined): string {
  if (!value) return "—";
  const date = new Date(value.length === 10 ? `${value}T00:00:00` : value);
  return date.toLocaleDateString("en-GB", { day: "numeric", month: "short", year: "numeric" });
}

export function stamp(value: string | null | undefined): string {
  if (!value) return "—";
  return new Date(value).toLocaleString("en-GB", {
    day: "numeric",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  });
}

export function countdown(expiresAt: string, now: number | null): string {
  if (now === null) return "";
  let seconds = Math.floor((new Date(expiresAt).getTime() - now) / 1000);
  if (seconds <= 0) return "Expired";
  const d = Math.floor(seconds / 86400);
  seconds -= d * 86400;
  const h = Math.floor(seconds / 3600);
  seconds -= h * 3600;
  const m = Math.floor(seconds / 60);
  const s = seconds - m * 60;
  if (d > 0) return `${d}d ${h}h`;
  if (h > 0) return `${h}h ${m}m`;
  return `${m}m ${String(s).padStart(2, "0")}s`;
}

const ACTIONS: Record<string, string> = {
  send_enquiry: "Enquiry",
  send_clarification: "Clarification",
  send_follow_up: "Follow-up",
  send_counteroffer: "Counteroffer",
  send_terms_message: "Terms message",
  change_mission_limits: "Limit change",
  confirm_mission_limits: "Confirm limits",
  confirm_commitment: "Commitment",
};

export function humanize(value: string): string {
  const text = value.replace(/[._]/g, " ").trim();
  return text.charAt(0).toUpperCase() + text.slice(1);
}

export function actionLabel(actionType: string): string {
  return ACTIONS[actionType] ?? humanize(actionType);
}

export const MISSION_STATUS: Record<string, string> = {
  draft: "Draft",
  awaiting_hod_confirmation: "Awaiting HOD",
  active: "Active",
  completed: "Done",
  cancelled: "Cancelled",
};

export function roleLabel(role: string | null | undefined): string {
  if (role === "hod") return "HOD";
  if (role === "committee_member") return "Committee";
  if (role === "agent") return "Agent";
  return "—";
}

/** "chrispr" or "Chris Tan" from the profile name, else the email's local part. */
export function displayName(person: { name: string | null; email: string }): string {
  const raw = (person.name ?? "").trim() || person.email.split("@")[0];
  return raw.charAt(0).toUpperCase() + raw.slice(1);
}

/** One letter for a one-word name, two for "First Last". */
export function initials(person: { name: string | null; email: string }): string {
  const words = displayName(person).split(/\s+/).filter(Boolean);
  const letters = words.length > 1 ? words[0][0] + words[words.length - 1][0] : words[0][0];
  return letters.toUpperCase();
}
