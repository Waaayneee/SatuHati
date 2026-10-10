"use client";

import { useLayoutEffect } from "react";
import { applyTheme, storedTheme } from "@/lib/theme";

/** Re-applies the saved theme after React's dev-only remount clears <html data-theme>. No-op in production. */
export function ThemeSync() {
  useLayoutEffect(() => {
    if (storedTheme() === "dark") applyTheme("dark");
  }, []);
  return null;
}
