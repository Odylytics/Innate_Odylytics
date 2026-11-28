import type { AttemptMeta } from './api'

/** Counts the wrong or aborted tries of a PIN entry and the time since the previous entry (backend AttemptMeta). Content-free. */
export class AttemptTracker {
  private retries = 0
  private last: number | null = null
  constructor(private now: () => number = () => performance.now()) {}

  /** a wrong PIN, a deleted digit or a tap that failed */
  bump() { this.retries++ }

  /** Meta for the entry being sent now; then resets the retry count and stamps this entry as the previous one.
   *  client_dt_prev_ms = from the previous entry being sent to this one being sent (absent for the first). */
  take(stage: NonNullable<AttemptMeta['flow_stage']>): AttemptMeta {
    const t = this.now()
    const meta: AttemptMeta = { flow_stage: stage, retries: Math.min(this.retries, 50), ...(this.last != null ? { client_dt_prev_ms: Math.round(t - this.last) } : {}) }
    this.retries = 0
    this.last = t
    return meta
  }
}
