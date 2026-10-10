import { Suspense } from "react";
import { Spinner } from "@/components/ui";
import { MissionView } from "./mission-view";

export default function MissionPage() {
  // MissionView reads the dynamic [id] param, which needs a Suspense boundary.
  return (
    <Suspense
      fallback={
        <div className="flex justify-center py-16 text-[var(--text-3)]">
          <Spinner />
        </div>
      }
    >
      <MissionView />
    </Suspense>
  );
}
