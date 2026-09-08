import { createFileRoute } from "@tanstack/react-router";
import { AppShell } from "@/components/app-shell";
import { MonitorDesk } from "@/components/monitor-desk";

export const Route = createFileRoute("/reports")({ component: ReportsPage });

function ReportsPage() {
  return (
    <AppShell>
      <MonitorDesk />
    </AppShell>
  );
}
