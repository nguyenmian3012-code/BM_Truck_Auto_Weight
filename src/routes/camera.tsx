import { createFileRoute } from "@tanstack/react-router";
import { AppShell } from "@/components/app-shell";
import { CameraDesk } from "@/components/camera-desk";

export const Route = createFileRoute("/camera")({ component: CameraPage });

function CameraPage() {
  return (
    <AppShell>
      <CameraDesk />
    </AppShell>
  );
}
