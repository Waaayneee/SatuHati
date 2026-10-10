import { activeProfileId } from "./profile";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
  ) {
    super(message);
  }
}

function detailMessage(body: unknown, fallback: string): string {
  const detail = (body as { detail?: unknown } | null)?.detail;
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail) && detail.length > 0) {
    const first = detail[0] as { msg?: string; loc?: unknown[] };
    const field = Array.isArray(first.loc) ? first.loc[first.loc.length - 1] : undefined;
    return [field, first.msg?.replace(/^Value error, /, "")].filter(Boolean).join(": ");
  }
  return fallback;
}

/**
 * Calls the backend as the chosen profile. The backend decides everything.
 * `as` overrides the active profile (used while switching); `anonymous` sends no profile.
 */
export async function api<T>(
  path: string,
  options: { method?: string; body?: unknown; as?: string; anonymous?: boolean } = {},
): Promise<T> {
  const headers: Record<string, string> = {};
  if (!options.anonymous) {
    const profileId = options.as ?? activeProfileId();
    if (!profileId) throw new ApiError(401, "No profile selected");
    headers["X-Profile-Id"] = profileId;
  }
  if (options.body !== undefined) headers["Content-Type"] = "application/json";

  let response: Response;
  try {
    response = await fetch(`${API_BASE}${path}`, {
      method: options.method ?? "GET",
      headers,
      body: options.body !== undefined ? JSON.stringify(options.body) : undefined,
    });
  } catch {
    throw new ApiError(0, "Can't reach the KawTeam server");
  }
  const body = await response.json().catch(() => null);
  if (!response.ok) throw new ApiError(response.status, detailMessage(body, response.statusText));
  return body as T;
}
