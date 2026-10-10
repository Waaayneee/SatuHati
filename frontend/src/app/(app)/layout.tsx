import { Suspense } from "react";
import { Nav, NavPlaceholder } from "@/components/nav";
import { SessionProvider } from "@/components/session";
import { ToastProvider } from "@/components/toast";

export default function AppLayout({ children }: { children: React.ReactNode }) {
  return (
    <SessionProvider>
      <ToastProvider>
        {/* Nav reads the URL, so it gets its own Suspense boundary for prerendering */}
        <Suspense fallback={<NavPlaceholder />}>
          <Nav />
        </Suspense>
        <main className="mx-auto max-w-6xl px-4 pt-8 pb-20 sm:px-6">{children}</main>
      </ToastProvider>
    </SessionProvider>
  );
}
