/**
 * The person the UI acts as (demo profile switching, no password).
 * The active profile lives in this tab's memory, so switching in one tab never changes
 * who another open tab acts as. localStorage only remembers the last choice for next time.
 */

const KEY = "kawteam:profile";
let active: string | null = null;

export function activeProfileId(): string | null {
  return active;
}

export function savedProfileId(): string | null {
  try {
    return window.localStorage.getItem(KEY);
  } catch {
    return null;
  }
}

export function setActiveProfile(id: string) {
  active = id;
  try {
    window.localStorage.setItem(KEY, id);
  } catch {
    // Private mode or blocked storage: this tab still uses the profile.
  }
}
