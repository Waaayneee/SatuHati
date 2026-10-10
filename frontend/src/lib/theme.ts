/** Light by default. The choice is kept per browser and applied before first paint (see app/layout.tsx). */

export type Theme = "light" | "dark";

export const THEME_KEY = "kawteam:theme";

/** Runs in <head> before paint. Only "dark" changes anything. */
export const THEME_SCRIPT = `(function(){try{if(localStorage.getItem("${THEME_KEY}")==="dark")document.documentElement.setAttribute("data-theme","dark")}catch(e){}})()`;

export function storedTheme(): Theme {
  try {
    return window.localStorage.getItem(THEME_KEY) === "dark" ? "dark" : "light";
  } catch {
    return "light";
  }
}

export function applyTheme(theme: Theme) {
  document.documentElement.setAttribute("data-theme", theme);
  try {
    window.localStorage.setItem(THEME_KEY, theme);
  } catch {
    // Storage blocked: the theme still applies until the page reloads.
  }
}
