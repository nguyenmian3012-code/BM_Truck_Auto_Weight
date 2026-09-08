import { SCALE_STABLE_BAND_KG, SCALE_STABLE_MS } from "./types";
import { settleWeightKg } from "./cargo";

export type ScaleTick = {
  kg: number;
  elapsedMs: number;
  stableForMs: number;
  done: boolean;
};

export function startScaleSettle(
  onTick: (tick: ScaleTick) => void,
  targetKg = settleWeightKg(),
): () => void {
  const t0 = performance.now();
  let stableFrom: number | null = null;

  const id = window.setInterval(() => {
    const elapsed = performance.now() - t0;
    const decay = Math.max(0, 1 - elapsed / 900);
    const noise = decay * (30 + Math.random() * 70);
    const kg = Math.max(0, targetKg + (Math.random() * 2 - 1) * noise);
    const inBand = Math.abs(kg - targetKg) <= SCALE_STABLE_BAND_KG;
    if (inBand) {
      if (stableFrom == null) stableFrom = performance.now();
    } else {
      stableFrom = null;
    }
    const stableForMs = stableFrom ? performance.now() - stableFrom : 0;
    const done = stableForMs >= SCALE_STABLE_MS;
    if (done) {
      window.clearInterval(id);
      onTick({
        kg: targetKg,
        elapsedMs: elapsed,
        stableForMs: SCALE_STABLE_MS,
        done: true,
      });
      return;
    }
    onTick({
      kg: Math.round(kg * 10) / 10,
      elapsedMs: elapsed,
      stableForMs,
      done: false,
    });
  }, 120);

  return () => window.clearInterval(id);
}
