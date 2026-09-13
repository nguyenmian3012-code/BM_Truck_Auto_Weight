import type { ScaleDriver, ScaleEvent } from "@/lib/hw/events";
import { SCALE_STABLE_BAND_KG, SCALE_STABLE_SEC } from "@/lib/hw/events";

/** Mock cân nhỏ: cùng ScaleEvent với đầu cân thật. Không bấm nút chụp. */
export function createMockScaleDriver(opts?: {
  tickMs?: number;
  targetKg?: number;
}): ScaleDriver {
  const tickMs = opts?.tickMs ?? 200;
  const targetKg = opts?.targetKg ?? 16880;
  return {
    id: "mock",
    listen(onEvent) {
      let elapsed = 0;
      let lastStable = false;
      const window: number[] = [];
      const id = setInterval(() => {
        elapsed += tickMs;
        const climbing = Math.min(1, elapsed / 1500);
        const noise = (1 - climbing) * 80 * Math.sin(elapsed / 90);
        const kg = Math.round(targetKg * climbing + noise);
        window.push(kg);
        const keep = Math.ceil((SCALE_STABLE_SEC * 1000) / tickMs);
        if (window.length > keep) window.shift();
        const spread = Math.max(...window) - Math.min(...window);
        const stable = climbing >= 1 && spread < SCALE_STABLE_BAND_KG;
        const raw = `ST,${kg},kg${stable ? ",S" : ""}`;
        const event: ScaleEvent = {
          kg,
          stable,
          ts: new Date().toISOString(),
          raw,
        };
        if (stable && !lastStable) onEvent(event);
        else if (!stable) onEvent({ ...event, stable: false });
        lastStable = stable;
      }, tickMs);
      return () => clearInterval(id);
    },
  };
}
