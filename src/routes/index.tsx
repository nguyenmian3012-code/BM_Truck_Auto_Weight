import { createFileRoute } from "@tanstack/react-router";
import { AppShell } from "@/components/app-shell";
import { WeighStation } from "@/components/weigh-station";

export const Route = createFileRoute("/")({ component: Home });

function Home() {
  return (
    <AppShell>
      <WeighStation />
    </AppShell>
  );
}
