import { describe, expect, it } from 'vitest'
import { AttemptTracker } from './attempt'

describe('AttemptTracker', () => {
  it('first entry has no gap, later ones do, retries reset after each entry', () => {
    let t = 1000
    const a = new AttemptTracker(() => t)
    a.bump(); a.bump()
    expect(a.take('signup_enroll')).toEqual({ flow_stage: 'signup_enroll', retries: 2 })
    t = 5200
    a.bump()
    expect(a.take('signup_enroll')).toEqual({ flow_stage: 'signup_enroll', retries: 1, client_dt_prev_ms: 4200 })
    t = 6000
    expect(a.take('transfer').retries).toBe(0)
  })
  it('caps retries at the backend limit', () => {
    const a = new AttemptTracker(() => 0)
    for (let i = 0; i < 80; i++) a.bump()
    expect(a.take('transfer').retries).toBe(50)
  })
})
