import type { Metadata, Viewport } from "next";
import { ThemeSync } from "@/components/theme-sync";
import { THEME_SCRIPT } from "@/lib/theme";
import "./globals.css";

export const metadata: Metadata = {
  title: "KawTeam",
  description: "Find, compare and negotiate with suppliers, with every external step approved.",
};

export const viewport: Viewport = {
  themeColor: "#f4f8ec",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    // Light by default. The inline script applies a saved dark choice before first paint.
    <html lang="en" className="h-full" suppressHydrationWarning>
      <head>
        <script dangerouslySetInnerHTML={{ __html: THEME_SCRIPT }} />
      </head>
      <body className="min-h-full">
        <ThemeSync />
        {children}
      </body>
    </html>
  );
}
