import { createFileRoute } from "@tanstack/react-router";
import { AppShell } from "@/components/app-shell";
import { QualityDesk } from "@/components/quality-desk";

export const Route = createFileRoute("/quality")({ component: QualityPage });

function QualityPage() {
  return (
    <AppShell>
      <QualityDesk />
    </AppShell>
  );
}
