# Innate — Backend API

Behavioral risk scoring API (Member 2). FastAPI + SQLAlchemy, SQLite when running locally, Postgres (Neon) when deployed.

## Running instance

| | |
|---|---|
| URL | https://nhip-api-taupe.vercel.app |
| Swagger | https://nhip-api-taupe.vercel.app/docs → **Authorize** → enter an API key |
| API key | 3 keys by role (SDK / ops / ML), stored in `backend/.env.deploy-key` on Member 2's machine (not committed). Ask Member 2 when needed |
| Infrastructure | Vercel project `nhip-api`, Singapore region (`sin1`); Neon DB `nhip-db` (free tier, Singapore), attached via the Vercel Marketplace |
| Latency measured 23/11 | Server-side processing 16–21 ms per scoring call; round trip from Vietnam ~125–150 ms |

Redeploy: `cd backend; vercel deploy --prod`. Check status: `/vercel:status` in Claude Code, or `vercel ls nhip-api`.

## Run

```powershell
cd backend
uv sync
uv run uvicorn app.main:app --reload --port 8000
```

- Swagger: http://localhost:8000/docs (`/` also redirects here) → click **Authorize**, enter `demo-key` (the SDK key). To try the dashboard/export locally, also set `NHIP_OPS_KEYS` / `NHIP_ML_KEYS`.
- Tests: `uv run pytest -q` (7 tests, ~2 seconds). SQLite in tests has foreign-key checks turned on to match Postgres.

### Environment variables

| Variable | Default | Notes |
|---|---|---|
| `DATABASE_URL` | `sqlite:///./nhip.db` | Set automatically by Neon on Vercel; `postgres://` is automatically switched to the psycopg driver |
| `NHIP_API_KEYS` | `demo-key` *(only when the DB is local SQLite; with a real DB and no value set, access is closed)* | **SDK** keys (embedded in the web app): submit sessions, rhythm enrollment, scoring. Multiple keys separated by commas |
| `NHIP_OPS_KEYS` | *(empty = closed)* | **Dashboard** keys: view the session list, set labels |
| `NHIP_ML_KEYS` | *(empty = closed)* | **Member 1** keys: `/v1/export` |
| `NHIP_CORS_ORIGINS` | `*` | The deployed instance uses `*`. **Set the exact domains of the demo wallet + dashboard when Member 3 deploys the frontend** |
| `NHIP_THRESHOLD_A` | `0.25` | risk < A → `allow` |
| `NHIP_THRESHOLD_B` | `0.55` | risk > B → `hold`; between A and B → `step_up` |

Every response has an `X-Process-Time-Ms` header (processing latency, used for slide figures). Measured locally: ~6 ms per scoring call.

## Endpoints

All `/v1/*` endpoints need an `X-API-Key` header with the role listed in the *Access* column. Wrong key → 401; valid key with the wrong role → 403. The SDK key is embedded in the web app, so it **cannot** open the dashboard or export.

| Method | Path | Access | Purpose |
|---|---|---|---|
| GET | `/health` | deploy | Liveness check |
| POST | `/v1/sessions` | App | Submit an interaction session → `{session_id, n_features}` |
| POST | `/v1/users/{user_id}/enroll` | SDK | Body `{session_id}`. Marks an enrollment entry; after 3 entries the template exists and **enrollment is locked** (extra entries → 409) |
| GET | `/v1/users/{user_id}` | App | Number of enrolled entries, whether the template is ready, number of updates |
| POST | `/v1/sessions/{id}/score` | App | Body `{recipient_is_new, amount}` → score + action + reasons |
| GET | `/v1/export?participant_id=&limit=500&offset=0` | ML | Exports sessions that have `meta` (raw data + features + data-collection labels), oldest first, **paginated**: each page has at most `limit` (≤ 2000) sessions and ~3 MB; if more data remains, the `X-Next-Offset` header gives the offset of the next page |
| GET | `/v1/sessions?flagged=true&limit=50` | ops | Latest `step_up`/`hold` sessions (omit `flagged` = all scored sessions) |
| POST | `/v1/sessions/{id}/label` | ops | Body `{label: "fraud" \| "legit"}` |

### App flow (Member 3)

```
Rhythm enrollment (3–5 times):  POST /v1/sessions  →  POST /v1/users/{uid}/enroll
Money transfer:                 POST /v1/sessions  →  POST /v1/sessions/{sid}/score  →  show action + explanation_vi
```

### Session the SDK sends (data contract)

Only timing (ms, counted from entering the screen) and coordinates (px), **no PIN content** other than the key label, which is needed to know the key center. A full example is available in Swagger.

```json
{
  "user_id": "demo_user",            // letters, digits, _ . -  (≤ 64 characters)
  "device_id": "demo_phone",
  "pin_taps": [                       // ≤ 12; taken from Pointer Events on the custom-drawn PIN keypad
    {"key": "1", "t_down": 0, "t_up": 95, "x": 66, "y": 395, "w": 40, "h": 40,
     "key_cx": 60, "key_cy": 400, "key_w": 100, "key_h": 70}
  ],
  "swipes": [ {"points": [{"t": 0, "x": 200, "y": 600}, {"t": 40, "x": 230, "y": 470}]} ],
  "screens": [ {"name": "transfer", "t_enter": 0, "t_first_touch": 1200} ]
}
```

- `w`, `h` = `PointerEvent.width/height`; `key_cx/cy/w/h` = key center and size (`getBoundingClientRect`).
- Do not send `pressure`. Do not rely on `isTrusted`.
- Limits: ≤ 30 swipes per session, ≤ 200 points per swipe (~3 seconds at 60 Hz); longer ones are truncated by the SDK.
- **During data collection** add `"meta": {"participant_id": "p07", "sitting": 1, "role": "genuine", "note": "..."}`. `sitting` = which collection round it is (1 enrollment, 2+ testing); `role` = `genuine`, `impostor` (knows the PIN, tries to tap like the owner) or `bot` (with `tactic` 1–4, sent by the [simulator](../attacker/README.md)). Impersonation entries: `user_id` is the owner's account, `participant_id` is the person tapping.
- The server rejects (422): `t_up < t_down`, NaN/negative numbers, `user_id` with unusual characters, too many events.

**Input fields other than the PIN (`fields`, optional):** amount, recipient, note. Only **timing, event type and character count** are sent, not the content.

```json
"fields": [
  {"name": "amount",    "events": [{"t": 4100, "kind": "key", "n": 1, "cls": "digit"}, {"t": 4290, "kind": "key", "n": 1, "cls": "digit"}]},
  {"name": "recipient", "events": [{"t": 2200, "kind": "paste", "n": 10}]},
  {"name": "note",      "events": [{"t": 6100, "kind": "key", "n": 1, "cls": "letter"}, {"t": 6350, "kind": "delete", "n": 1}]}
]
```

- `name`: `amount | recipient | note | name`. `kind`: `key` (typed character), `paste`, `delete`, `set_text` (text changed **without key events**, e.g. Accessibility `ACTION_SET_TEXT`; only a native SDK can detect it).
- The old web SDK (`wallet.html`, removed) only emitted `key`, `paste`, `delete` from the `input` event; it did not emit `set_text`.
- Baseline rule: `set_text` in the **amount** field is treated as a machine (`text_set_without_keys`, order held); in other fields it only lowers the score slightly, because autofill/contacts can also set text without keys. Thresholds are **not yet verified on real devices** (R9).
- Typing rhythm inside a field (≥ 4 keys) becomes the owner-recognition features `fld_<field>_gap_mean/std`; for them to be in the template, the enrollment entries must also type in those fields.

### Scoring response

```json
{
  "session_id": "s_8f21a0c3d4e5",
  "human_score": 0.97,
  "owner_match": 0.12,
  "risk": "medium",
  "risk_score": 0.47,
  "action": "step_up",
  "reasons": ["pin_rhythm_slower_40pct", "tap_offset_left", "new_recipient"],
  "explanation_vi": "Thao tác giống người thật nhưng không khớp thói quen của chủ tài khoản (nhịp PIN chậm hơn 40%, chạm lệch trái). Giao dịch: người nhận mới. Đề nghị xác thực khuôn mặt trước khi chuyển."
}
```

The `explanation_vi` string is product text shown to wallet users (in English: "The interaction looks like a real person but does not match the account owner's habits (PIN rhythm 40% slower, taps offset to the left). Transaction: new recipient. Face verification recommended before transferring.").

`owner_match = null` when the user has not enrolled the 3 entries yet (reason `not_enrolled`). If enrolled but the session lacks PIN rhythm (no PIN tapped, or the PIN is shorter than at enrollment) → `owner_match = 0`, reason `missing_pin_evidence`, never `allow`.

## Scoring layer (`app/scoring/`) — Member 1 replaces file by file, keeping function signatures

| File | Function | Current baseline |
|---|---|---|
| `features.py` | `extract(raw) -> dict` | Key hold, key-to-key interval, total time, center offset (dx, dy relative to key size), contact size; swipes: duration, length, straightness, mean/peak velocity; time to first touch |
| `owner.py` | `build_template`, `score`, `update` | Scaled Manhattan (Killourhy & Maxion 2009) with a standard-deviation floor. Distance → [0,1] mapping **not calibrated** (d = 2 → 0.5) |
| `human.py` | `score(features) -> (human_score, reasons)` | Rules: rhythm too even (CV < 0.08), taps exactly at the center (< 0.06 of key width), perfectly straight swipe (weak signal, deduction at most 0.5) |
| `fusion.py` | `fuse`, `amount_anomaly` | `0.40·(1−human) + 0.35·(1−owner) + 0.15·new_recipient + 0.10·amount_anomaly`; `human < 0.3` → always `hold` |
| `explain.py` | `explain(...)` | Feature groups deviating ≥ 1.5 sd → at most 3 reasons + Vietnamese sentence from a template. No LLM |

**Template update** (section 5.2 of the plan): only after the first scored session is `allow`, is not an enrollment entry, `owner_match ≥ 0.8` and `human_score ≥ 0.8`. Moving average α = 0.1, and the template must not drift more than 1 sd from enrollment. Not done: drift direction check.

## Tests run

`tests/test_api.py` (fake data from `tests/synth.py`):

- Missing/wrong API key → 401 (including non-ASCII headers); wrong-role key → 403; invalid data → 422; enrolling someone else's session → 400; enrolling more once a template exists → 409.
- Session with only swipes, or a PIN with missing keys, for an enrolled account → not `allow`, reason `missing_pin_evidence`.
- Full flow: not enrolled → `not_enrolled`; enroll 3 entries → template exists; real owner → `allow`; someone else who knows the PIN → `step_up` with rhythm/position reasons; tactic 1 bot → `hold` with `tap_exact_center`; amount 50 times larger → `amount_unusual`; template updated; dashboard sees the flagged session; labeling works.
- Drift cap: 200 rounds of "gradual teaching" with far-off sessions, the template stays within ±1 sd.

Running 200 seeds on fake data: the real owner is let through 95%, someone else is flagged 100%, tactic 1 bot is held 100%. **This is self-generated data, not figures for slides**; real numbers must be measured on data collected from people per section 5.5.

## Known limits

- Thresholds and weights are starting values, not fitted on real data.
- The human/bot rules catch tactics 1–2; tactic 3 (replaying a real person's session) and tactic 4 will get through, which needs Member 1's model.
- The SDK key is in the web app, so anyone can see it: app users can still submit sessions and score for **any** `user_id`, and can enroll the rhythm in advance for an account that has **not** enrolled yet. A real product must tie `user_id` to the wallet's login session (the partner's backend calls the API with a secret key).
- There is no flow to reset the template (re-enrollment); for now `users.template` must be deleted in the DB.
- The template is shared across all devices of one user (the plan uses one demo phone).
- Not yet available: hacker simulator, LLM summary for the dashboard, DB migrations (tables are created automatically at startup).

## Member 2's next tasks

1. ~~Hacker simulator~~ — done 23/11, see [attacker/README.md](../attacker/README.md).
2. ~~Deploy~~ — done 23/11. Remaining: set `NHIP_CORS_ORIGINS` once the frontend domain exists.
3. Demo account for the judges.
