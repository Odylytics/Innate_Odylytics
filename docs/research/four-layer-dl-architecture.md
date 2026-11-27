# 4-Layer Neural Architecture for Innate (`Innate4LayerNet`) — Literature Synthesis & Draft Design

> Research & architecture draft (27/11/2026). **Design only — no code written yet.**
> Synthesizes all **52 PDF files (43 unique papers)** saved under `papers/` across `bot-detection/`, `evaluation-datasets/`, `owner-verification/`, and `risk-fusion-explainability/`.
> Plugs into Layer 2 of the end-to-end training & phone integration plan in [`../plan/dl-training-pipeline.md`](../plan/dl-training-pipeline.md).

---

## 1. Corpus Audit & What Each Paper Group Contributes

All 52 PDFs in `papers/` resolve to **43 unique papers** (9 files are duplicates across topic folders). Every major design choice of the 4-layer neural model traces directly to these papers:

| Paper(s) in `papers/` | Verified Technical Finding | Concrete Design Rule Adopted in `Innate4LayerNet` |
|---|---|---|
| **Buschek 2015** (`Buschek2015_...`), **Zheng 2014** (`Zheng2014_...`) | Spatial touch offsets `(dx, dy)` + jumps cut EER by **26.4–36.8%** over timing alone and outperform pressure; repeated digits (`1-1-1-1`) degrade accuracy; posture changes raise EER up to **86.3%** unless modeled. | Concatenate normalized offsets `(dx/key_w, dy/key_h)` and key-center jumps `(Δcx, Δcy)` directly with timing features at **Layer 1**; avoid `pressure`. |
| **TypeNet** (`Acien2021_TypeNet...`), **TypeFormer** (`Stragapede2022_...`), **KVC** (`Stragapede2023_KVC...`) | `Conv1D` before RNN reduces error ~35% (Lu et al. cited in TypeNet); TypeFormer uses **Gaussian Range Encoding (`G=20`)** + **Multi-Scale Keystroke CNN (`kernels 1,3,5`)** + Temporal/Channel self-attention; KVC `10F` (`HT, IPT, IRT, IKT` + lag-2/3) achieves **9.45% vs 10.17%** EER on mobile *without* ASCII key codes; Triplet loss beats Softmax & Contrastive; mobile EER drops steeply as enrollment count rises (`E=1→5→10`: `6.99%→3.84%→3.15%`). | **Layer 1** combines Gaussian Range Encoding + Multi-Scale `Conv1D(k=1,3,5)` over content-agnostic time-domain `10F` + spatial offsets; **Layer 2** compresses into a `64-d` L2-normalized embedding trained with Triplet / SupCon (same-PIN hard negatives). |
| **BioTouchPass2** (`Tolosana2020_...`), **BeCAPTCHA-Mouse** (`Acien2022_...`), **BehavePassDB** (`Stragapede2023_BehavePassDB.pdf`) | Bidirectional RNN captures past+future context on short 4-digit PINs (**2.38% EER** on MobileTouchDB); lightweight `GRU/LSTM` + neuromotor stats reaches **93%** on single-trajectory bot detection; BehavePassDB exposes **device bias** (`AUC 87.2%` random vs `68.7%` same-device skilled impostor) and uses `U[0.98, 1.02]` noise augmentation (Neverova et al.) to decorrelate device artifacts. | **Layer 2** uses a compact `BiGRU + Self-Attention + Attentive Stats Pooling` (~120K–180K params, exportable to NumPy/ONNX) instead of a 9-layer heavy Transformer, trained with slight multiplicative timing jitter and **without** contact size (`w, h`). |
| **FETA** (`Georgiev2022_...`), **BB-MAS** (`Belman2019_...`), **HMOG** (`Sitova2016_...`), **Touchalytics** (`Frank2013_...`), **Palin 2019**, **Teh 2016**, **UMDAA-02** | FETA quantifies 5 pitfalls (`13.8%` realistic vs `4.9%` unrealistic EER; phone-mixing `+3.2–5.8%`, non-contiguous split `+3.8%`, attacker-in-train `+2.55%`); Touchalytics (`0%` intra-session → `2–3%` inter-session → `<4%` 1 week) and Teh (`64%` single-session studies) prove accuracy decays with **inter-session time gap** $\Delta t$. | Split strictly person-disjoint & time-ordered; explicitly feed **inter-session $\Delta t$** into **Layer 3** attention decay and **Layer 4** threshold calibration; never mix contact size or multi-device leaks. |
| **Giot 2012** (`Giot2012_Hybrid...`), **Lovisotto 2020** (`Lovisotto2020_BiometricBackdoors...`), **Biggio 2012** (`Biggio2012_Poisoning...`) | Giot's **Hybrid template** (parallel initial anchor + recent sliding sub-references) beats single static or sliding templates; Biggio & Lovisotto prove thresholded self-update is vulnerable to gradual poisoning (`>70%` white-box success in `<10` injections), mitigated by **sigmoid recency weights**, **failed-attempt tracking**, and **angular drift direction** (`>99%` caught after 2 injections). | **Layer 3** maintains **both** an immutable initial enrollment anchor $\mu_0$ and a **time-decayed prototype** $\mu_{\text{decay}}$ via recency-weighted attention, plus an explicit **angular drift feature** $\cos(e_q - \mu_0, \mu_{\text{decay}} - \mu_0)$. |
| **ActReal** (`Wang2026_actreal...`), **BeCAPTCHA-Touch** (`Acien2021_becaptcha...`), **BeCAPTCHA-Type** (`DeAlcala2023_...`), **Iliou 2021a/b**, **Khan 2018**, **Fratantonio 2017**, **Diao 2019**, **Naseri 2019** | Accessibility abuse (`Cloak & Dagger`, `AccessiLeaks`, `Diao 2019`) motivates touch-level verification; `BeCAPTCHA-Type` proves pure LSTM collapses in few-shot (`20` subjects: `~50%`) while handcrafted features + trees stay `87–95%`; `Iliou 2021a` fuses **session-log temporal stats** with **trajectory dynamics**; `ActReal` defeats single detectors (`77.5%` ASR) and introduces **3 complementary critics**: `D_feat` (stats MLP), `D_wave` (masked Conv1D), and **Set comparison** $q_R(x) = [\mu_R, z, |\mu_R - z|, \mu_R \odot z, \sigma_R, c]$, while warning fixed time windows break variable-density sessions. | **Layer 3** adopts ActReal's **Set-to-Query algebraic comparison** $[\mu, e_q, |\mu - e_q|, (e_q - \mu)^2, \mu \odot e_q, \sigma_{\text{enroll}}]$; **Layer 4** fuses sequence neural descriptors with handcrafted `bot_features` + inter-session log velocity (`n_attempts_10m`, `dt_cv_recent`, `client_retries`) so few-shot bot detection stays robust. |
| **Freeman 2016**, **Wiefling 2019/2020/2021/2022**, **Singh 2019**, **PaySim** (`LopezRojas2016`) | `Freeman 2016` shows weighted likelihood fusion (`AUC 0.913→0.955`) with time decay; `Wiefling 2022` (3.3M users, 31.3M logins) proves genuine risk scores decay with **login history size** ($k$) and differ sharply by **login frequency** (`daily` vs `weekly` vs `>30d`), proposing **ML-learned Dynamic Access Thresholds** conditioned on history size; `Singh 2019` surveys **quality-gated fusion (`QAN`)** and contextual ancillary signals. | **Layer 4** implements **Quality- & History-Conditioned Calibration** (`τ(k, Δt)`, `T(k)`) and **Quality-Gated Risk Fusion** combining biometric scores with attempt counts, intervals, and transaction context. |
| **Ahmed 2026**, **Eberz 2017**, **Sugrim 2019**, **Lundberg 2017/2020**, **Psychoula 2021**, **Ke 2017**, **Breiman 2001** | Report error at the **operating point (`FAR@FRR=5%`)**, `DET` curves, confidence intervals, and per-user Gini skew; `SHAP` / `TreeSHAP` requires a **fixed, documented background set** (user's enrollment sessions) for fast, consistent real-time fraud explanations. | **Layer 4** calibrates thresholds specifically to `FRR = 5%` per $k$-bucket and outputs additive branch/feature attributions relative to the user's enrollment gallery for Vietnamese `explain.py`. |

---

## 2. Formal 4-Layer Neural Architecture (`Innate4LayerNet`)

Unlike the 4 *system stages* of the training pipeline (Data → Model Zoo → Eval → Export), **`Innate4LayerNet`** is a concrete **4-layer deep neural network** inside Layer 2 of the pipeline. It is explicitly conditioned on **attempt counts ("số lượt nhập")** and **inter-attempt intervals ("khoảng cách giữa các lần")**, while remaining compact enough (`~120K–180K` parameters) to export to pure NumPy / ONNX for serverless inference.

```
Inputs:
  x_seq      ∈ R^(L × 10)   : current session tap sequence (L=12 for PIN, L=50 for phrase)
  S_enroll   = {(x_k, Δt_k)} : k enrolled sessions (k = 2..10) + age Δt_k since enrollment
  h_ctx      ∈ R^14         : inter-session attempt counts, Δt intervals, retries, device flags
  f_tab      ∈ R^26         : handcrafted bot_features (excl. contact w/h) + context
       │
       ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ LAYER 1 — Spatio-Temporal Tokenization & Gaussian Range Encoding        │
│   • Gaussian Range Encoding (G=20) on continuous timing/offset scales   │
│   • Multi-Scale Masked Conv1D (kernels 1, 3, 5; d=64; GELU + LayerNorm) │
│   • Training noise jitter U[0.98, 1.02] to suppress device artifacts    │
│   Output: H^(1) ∈ R^(L × 64)                                            │
└─────────────────────────────────────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ LAYER 2 — Sequential Motor & Naturalness Encoder                        │
│   • BiGRU(hidden=32 per dir → 64) + 2-Head Masked Self-Attention + Norm │
│   • Attentive Statistics Pooling (weighted mean + std over valid mask)  │
│   • Two projection heads:                                               │
│       - e_q ∈ R^64 (L2-normalized identity embedding)                   │
│       - u_q ∈ R^32 (session-internal naturalness descriptor)            │
└─────────────────────────────────────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ LAYER 3 — Time- & Attempt-Aware Set Matching + Drift Guard              │
│   • Encode support set -> {e_1..e_k}; pair each with age ϕ(Δt_i) & k    │
│   • Hybrid References (Giot 2012 + Lovisotto 2020):                     │
│       - μ_0     = mean(e_1..e_k)               [static anchor]          │
│       - α_i     = softmax(W_a [e_i || ϕ(Δt_i) || log(1+k)])             │
│       - μ_decay = Σ α_i e_i                    [time-decayed proto]     │
│       - σ_enr   = smoothed intra-enroll spread (prior shrinkage)        │
│   • Set-to-Query Vector (ActReal Eq. 5 + Lovisotto drift):              │
│       v_match = [|μ_decay - e_q|, (e_q - μ_decay)^2, e_q ⊙ μ_decay,     │
│                  cos(e_q, μ_decay), cos(e_q, μ_0), σ_enr,               │
│                  cos(e_q - μ_0, μ_decay - μ_0), ϕ(h_ctx)]               │
└─────────────────────────────────────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ LAYER 4 — Dual-Stream Operating-Point Calibration & Context Head        │
│   • Stream A (Human vs Bot):                                            │
│       s_human = σ(MLP_bot([u_q || f_tab || h_burst]))                   │
│       (fuses sequence naturalness + handcrafted stats + retry/Δt bursts)│
│   • Stream B (Owner Verification w/ Dynamic History Threshold):         │
│       logit_raw = MLP_owner(v_match)                                    │
│       s_owner = σ((logit_raw - τ(k, Δt_last)) / T(k))                   │
│       (Wiefling 2022 dynamic k/Δt threshold calibrated @ FRR=5%)        │
│   • Outputs: (s_human, s_owner, drift_flag, additive_contributions)     │
└─────────────────────────────────────────────────────────────────────────┘
```

### Detailed Specification of Inputs & Each Layer

#### 0. Input Feature Contract
- **Per-tap sequence tensor $x_{\text{seq}} \in \mathbb{R}^{L \times 10}$** (padded to $L = 12$ for PINs, $L = 50$ for challenge phrases; contact area `w, h` and `pressure` excluded):
  1. `hold_s`: `(t_up - t_down) / 1000` (Zheng 2014, TypeNet)
  2. `pp_s`: press-to-press interval `Δt_down / 1000` (TypeNet)
  3. `rr_s`: release-to-release interval `Δt_up / 1000` (TypeNet)
  4. `rp_s`: flight time `(t_down[i] - t_up[i-1]) / 1000` (TypeNet)
  5–6. `pp2_s`, `rp2_s`: lag-2 digraph spans (`t[i] - t[i-2]`, inspired by KVC `10F` time-domain expansion without leaking key text)
  7–8. `dx_norm`, `dy_norm`: `(x - key_cx) / key_w`, `(y - key_cy) / key_h` (Buschek 2015 spatial offsets)
  9. `jump_dist`: Euclidean distance between consecutive key centers in normalized keypad units (Buschek 2015 touch jumps, zero-content spatial cue; `0` on free-text when keypad coords unavailable)
  10. `mask`: `1.0` for real taps, `0.0` for padding (TypeNet / ActReal validity mask)

- **Inter-session & attempt history vector $h_{\text{ctx}} \in \mathbb{R}^{14}$** (split into owner-drift context vs. bot-burst context):
  - **Attempt counts ("số lượt nhập"):**
    1. `log1p(n_enroll)` ($k$, enrolled attempts completed)
    2. `log1p(n_sessions_total)` (total user sessions to date)
    3. `attempt_index_in_sitting` (order within continuous session cluster `< 300s`)
    4. `n_attempts_10m` (burst count in last 10 minutes)
    5. `n_attempts_1h` (session count in last 1 hour)
    6. `n_attempts_24h` (session count in last 24 hours)
    7. `n_recent_flagged` (count of recent `step_up`/`hold` decisions)
    8. `client_retries` (mismatched/aborted PIN attempts on phone before submission)
  - **Inter-attempt intervals ("khoảng cách giữa các lần"):**
    9. `log1p(dt_prev_session_sec)` + `has_prev` flag (time since previous session)
    10. `log1p(dt_last_enroll_sec)` (time elapsed since last enrollment — Touchalytics/Buschek drift scale)
    11. `log1p(dt_mean_recent_sec)` (mean gap over last 10 sessions — Wiefling 2022 frequency bucket)
    12. `dt_cv_recent` (`std / mean` of recent inter-session gaps — Iliou/scripted regularity cue)
    13. `log1p(client_dt_prev_ms)` (high-res client gap between consecutive phone entries)
  - **Continuity:**
    14. `same_device_as_enroll` (fraction of enrolled sessions on the current `device_id`)

---

#### Layer 1 — Spatio-Temporal Tokenization & Gaussian Range Encoding
- **Motivation:** Standard Transformers fail on short continuous behavioral signals without smooth continuous encoding (**TypeFormer**), while 1D convolutions capture local n-graph keystroke dependencies before recurrent modeling (**TypeNet** §2, **ActReal** `D_wave`).
- **Operations:**
  1. Continuous features $x_{\text{seq}}$ pass through **Gaussian Range Encoding (GRE)** with $G = 20$ learnable Gaussian centers/widths on the timing and offset channels, producing normalized PDF embeddings concatenated with linearly projected features: $z_0 = W_{\text{in}} [x_{\text{seq}} \,\|\, \text{GRE}(x_{\text{seq}})]$.
  2. Three parallel masked **1D Convolutions** (`kernel_size ∈ {1, 3, 5}`, `channels = 64/branch` → concatenated + `1×1` projection to `d = 64`) capture single-tap dwell, digraph transitions, and trigraph cadence.
  3. Residual skip + `LayerNorm` + `Dropout(0.1)` (with training-time multiplicative jitter `~ U[0.98, 1.02]` per **BehavePassDB** to reduce device-timer overfitting).
- **Output:** $H^{(1)} \in \mathbb{R}^{L \times 64}$ (masked to zero on padding positions).

---

#### Layer 2 — Sequential Motor & Naturalness Encoder
- **Motivation:** Short 4–12 digit PINs need full bidirectional context (**BioTouchPass2** `BLSTM`), global self-attention captures non-adjacent key dependencies (e.g., 1st digit vs. 6th digit return to thumb anchor, **TypeFormer**), and `GRU` converges with fewer parameters and faster CPU execution than stacked LSTMs (**BeCAPTCHA-Mouse**).
- **Operations:**
  1. **1-layer Bidirectional GRU** (`hidden = 32` per direction → `64` concatenated) with recurrent dropout (`0.2`, **TypeNet**).
  2. **1-layer Masked Multi-Head Self-Attention** (`2` heads, `d_model = 64`, `Add & Norm` + 2-layer FFN `64 → 128 → 64`).
  3. **Attentive Statistics Pooling** over valid taps (`mask == 1`): computes attention-weighted mean $\bar{h}$ and standard deviation $\tilde{h}$ (capturing both average motor rhythm and within-PIN variability), projected into:
     - **Identity embedding:** $e_q = \text{L2Norm}(W_{\text{id}} [\bar{h} \,\|\, \tilde{h}]) \in \mathbb{R}^{64}$
     - **Naturalness descriptor:** $u_q = \text{GELU}(W_{\text{nat}} [\bar{h} \,\|\, \tilde{h}]) \in \mathbb{R}^{32}$
- **Training supervision (Encoder pre-training / joint loss):** `TripletLoss(margin=1.0)` / `SupCon` with **same-PIN hard negatives** (impostor typing the exact same 6 digits, matching `research/finetune/finetune.py` and **KVC** open-set protocol).

---

#### Layer 3 — Time- & Attempt-Aware Set Matching + Drift Guard
- **Motivation:** Treating $k$ enrollment attempts as an unweighted average ignores cross-session drift (**Buschek 2015**, **Touchalytics**) and enrollment-size uncertainty (**TypeNet**, **TypeFormer**, **Zheng 2014**). Combining an immutable enrollment anchor with a recency-weighted reference prevents gradual template poisoning (**Giot 2012**, **Lovisotto 2020**).
- **Operations:**
  Given the user's $k$ enrollment embeddings $\{e_1, \dots, e_k\}$ (pre-computed and stored in `User.template` at enrollment time!) and their ages $\Delta t_i = t_{\text{now}} - t_i$:
  1. **Dual Prototype Construction (Giot 2012 + Lovisotto 2020):**
     - Static anchor: $\mu_0 = \text{L2Norm}\big(\frac{1}{k}\sum_{i=1}^k e_i\big)$
     - Time- & consistency-weighted attention over enrollment rounds:
       $$\alpha_i = \text{softmax}_i\Big( w_a^\top \big[ e_i \,\|\, \cos(e_i, \mu_0) \,\|\, \log(1 + \Delta t_i) \,\|\, \log(1 + k) \big] \Big), \qquad \mu_{\text{decay}} = \text{L2Norm}\Big(\sum_{i=1}^k \alpha_i e_i\Big)$$
     - Empirical enrollment spread with population shrinkage floor $\sigma_{\text{enr}}$ (preserving the E1/E10 finding from `owner.py`).
  2. **Differentiable Set-to-Query Comparison (ActReal Eq. 5):**
     $$v_{\text{match}} = \Big[\, |\mu_{\text{decay}} - e_q|,\; (e_q - \mu_{\text{decay}})^2,\; e_q \odot \mu_{\text{decay}},\; \cos(e_q, \mu_{\text{decay}}),\; \cos(e_q, \mu_0),\; \sigma_{\text{enr}},\; \text{drift}_{\text{cos}},\; \phi(h_{\text{ctx}}) \,\Big]$$
     where $\text{drift}_{\text{cos}} = \cos(e_q - \mu_0,\, \mu_{\text{decay}} - \mu_0)$ measures **directional update alignment** (**Lovisotto 2020** §7.3 countermeasure against biometric backdoors).

---

#### Layer 4 — Dual-Stream Operating-Point Calibration & Context Fusion Head
- **Motivation:**
  - `BeCAPTCHA-Type` (DeAlcala 2023) proves neural sequence models underperform tree/tabular baselines when labeled bot data is small; fusing `u_q` with handcrafted `bot_features` + inter-attempt burst stats solves few-shot brittleness.
  - `Wiefling 2022` proves genuine risk distributions shift with **history size ($k$)** and **session frequency ($\Delta t$)**, motivating a learned dynamic threshold $\tau(k, \Delta t)$.
  - `Ahmed 2026` & `Eberz 2017` mandate calibrating directly at the **operating point (`FAR@FRR=5%`)** and checking per-user Gini equity.
  - `Singh 2019` & `Lundberg 2017/2020` highlight quality-gated fusion and additive attribution relative to a fixed enrollment background (`Psychoula 2021`).
- **Operations:**
  1. **Human / Bot Head (`s_human ∈ [0, 1]`):**
     - Fuses sequence naturalness $u_q$, handcrafted `bot_features` (`f_tab`, excluding `CONTACT_FEATURES`), and burst/interval history (`n_attempts_10m`, `client_retries`, `dt_cv_recent`, `client_dt_prev_ms`):
     - $s_{\text{human}} = \sigma\big(\text{MLP}_{\text{bot}}([u_q \,\|\, f_{\text{tab}} \,\|\, h_{\text{burst}}])\big)$, calibrated so validation humans at `FRR = 5%` map to `0.5` (compatible with `human_model.py` & `explain.py`).
  2. **Owner Head with Dynamic History Threshold (`s_owner ∈ [0, 1]`):**
     - Raw similarity logit: $z_{\text{own}} = \text{MLP}_{\text{owner}}(v_{\text{match}})$.
     - Learned dynamic threshold & temperature (**Wiefling 2022**):
       $$\tau(k, \Delta t_{\text{last}}) = \tau_0 + w_k \log(1+k) + w_{\Delta t} \log(1 + \Delta t_{\text{last\_enroll}}), \qquad T(k) = \text{softplus}(a_0 + a_k \log(1+k))$$
     - Calibrated score: $s_{\text{owner}} = \sigma\big((z_{\text{own}} - \tau(k, \Delta t_{\text{last}})) / T(k)\big)$, post-fitted on validation people per `k`-bucket (`k=2, 3, 4, 5+`) so `s_owner = 0.5` sits exactly at `FRR = 5%`.
  3. **Quality-Gated Output & Explainability Bridge:**
     - Exports `(s_human, s_owner, drift_cos, branch_attributions)` into `fusion.py` (`allow | step_up | hold`) and `explain.py` without changing the downstream rule: **no LLM on the decision path, and `owner_match` never locks an account on its own.**

---

## 3. Practical Constraints & Mapping to Existing Innate Pipeline

| Constraint in `Innate_Odylytics` | How `Innate4LayerNet` Respects It |
|---|---|
| **Vercel serverless has no `torch` / `libgomp`** (`backend/pyproject.toml`) | Compact footprint (~150K params): Layers 1–4 use only Conv1D, GRU, Attention, LayerNorm, GELU, and Linear ops — directly exportable to `.npz` (pure-NumPy runner) or `.onnx` with `< 10 ms` CPU latency. |
| **Enrollment is 3–10 entries on `#/collect`** (`web/src/Collect.tsx`) | Pretraining on Aalto / StrokePIN + Layer 3's **Time- & $k$-Aware Prototype** + **Dynamic Threshold $\tau(k, \Delta t)$** natively supports $k = 2 \dots 10$ without retraining per user, and directly measures the $k \ge 5$ curve that `enrollCurve.ts` currently extrapolates. |
| **Zero device leakage & privacy compliance** (PDPL 2025, E12b, FETA) | Contact size (`w, h`), raw `pressure`, and raw PIN digits are excluded from production identity vectors; `HistoryContext` uses only counts and $\Delta t$ intervals. |
| **Safe production rollout** (`backend/app/scoring/`) | Rolls out in **shadow mode** first (`TouchSession.result["shadow"]`), falling back cleanly to `human_lgbm.txt`, `owner_lgbm.txt`, and `owner.py` / `human.py` whenever disabled or unavailable. |
