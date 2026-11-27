// "Accuracy check" while enrolling: share of PIN-knowing impostors stopped (1 - FAR at FRR 5%) after k enrollment entries.
// k = 2..4 measured on real phone PINs (E30, StrokePIN, sitting, backend distance: research/results/e30_enroll_curve.md).
// k >= 5 is extrapolated with a power law through k = 3 and 4 (StrokePIN has at most 5 sittings, so no test entry is left).
const MEASURED: Record<number, number> = { 2: 0.857, 3: 0.503, 4: 0.429 }
const B = Math.log(MEASURED[3] / MEASURED[4]) / Math.log(4 / 3)

export const MIN_JUDGE_ENROLL = 5
export const MAX_ENROLL = 10 // same as backend MAX_ENROLL

export function impostorStopped(k: number): { value: number; measured: boolean } {
  if (k < 2) return { value: 0, measured: true } // one entry has no spread: no template
  if (MEASURED[k] !== undefined) return { value: 1 - MEASURED[k], measured: true }
  return { value: 1 - MEASURED[4] * (4 / k) ** B, measured: false }
}
