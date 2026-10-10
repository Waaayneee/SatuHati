import type { Metadata } from "next";
import localFont from "next/font/local";
import "./globals.css";
import { DemoProvider } from "@/components/kawteam";
import { Aurora } from "@/components/aurora";

// TeX Gyre Heros, a free Helvetica clone (GUST Font License, see ./fonts/GUST-FONT-LICENSE.txt).
const heros = localFont({
  src: [
    { path: "./fonts/texgyreheros-regular.otf", weight: "400", style: "normal" },
    { path: "./fonts/texgyreheros-italic.otf", weight: "400", style: "italic" },
    { path: "./fonts/texgyreheros-bold.otf", weight: "700", style: "normal" },
    { path: "./fonts/texgyreheros-bolditalic.otf", weight: "700", style: "italic" },
  ],
  variable: "--font-heros",
  display: "swap",
});

export const metadata: Metadata = {
  title: "KawTeam — Your project workspace",
  description: "Projects, conversations and vendor relationships. Keep the work moving, with your team making the final call.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={heros.variable}>
      <body>
        <Aurora />
        <DemoProvider>{children}</DemoProvider>
      </body>
    </html>
  );
}
