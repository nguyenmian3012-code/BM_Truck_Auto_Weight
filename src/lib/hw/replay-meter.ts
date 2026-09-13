import type { MeterDriver, MeterReading } from "@/lib/hw/events";

/** Phát lại log RS232 máy bột (Task 3). Không bịa số. */
export function parseStarchLine(raw: string): number | null {
  const n = raw.replace(",", ".").match(/(\d+(?:\.\d+)?)/);
  if (!n) return null;
  const v = Number(n[1]);
  if (!Number.isFinite(v)) return null;
  if (v > 100 && v <= 1000) return v / 10;
  if (v > 0 && v <= 80) return v;
  return null;
}

export function createReplayMeterDriver(lines: string[], gapMs = 1500): MeterDriver {
  return {
    id: "replay",
    listen(onEvent) {
      let i = 0;
      const id = setInterval(() => {
        if (i >= lines.length) {
          clearInterval(id);
          return;
        }
        const raw = lines[i++];
        const starchPct = parseStarchLine(raw);
        if (starchPct == null) return;
        const event: MeterReading = {
          starchPct,
          ts: new Date().toISOString(),
          raw,
        };
        onEvent(event);
      }, gapMs);
      return () => clearInterval(id);
    },
  };
}
