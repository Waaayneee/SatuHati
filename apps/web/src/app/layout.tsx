import type { Metadata } from "next";
import "./globals.css";
import { DemoProvider } from "@/components/kawteam";

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
    <html lang="en">
      <body><DemoProvider>{children}</DemoProvider></body>
    </html>
  );
}
