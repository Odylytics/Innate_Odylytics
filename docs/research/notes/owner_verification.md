# Foundation papers for Innate — Model 2 "Có phải chủ tài khoản?" ("Is this the account owner?") (plan §5.0, §5.2)

Local PDFs: `C:/TuanNghia/Project/Momo_Odylytics/papers/owner-verification/` (14 files, all checked for a `%PDF` header, all < 11 MB).
All numbers below were read from the downloaded PDF text unless marked otherwise. DOIs marked "(from memory, verify)" were not checked against the publisher page.

## Paper index

| # | Citation | Link / DOI | Plan claim backed | Local PDF |
|---|---|---|---|---|
| 1 | Zheng N., Bai K., Huang H., Wang H. "You Are How You Touch: User Verification on Smartphones via Tapping Behaviors." IEEE ICNP 2014. | https://www.eecis.udel.edu/~hnw/paper/tapping.pdf ; DOI 10.1109/ICNP.2014.43 (from memory, verify) | PIN rhythm + touch features; scaled-distance template; enrollment count | `Zheng2014_YouAreHowYouTouch-tapping.pdf` |
| 2 | Buschek D., De Luca A., Alt F. "Improving Accuracy, Applicability and Usability of Keystroke Biometrics on Mobile Touchscreen Devices." CHI 2015. | http://www.florian-alt.org/unibw/wp-content/publications/buschek2015chi.pdf ; DOI 10.1145/2702123.2702252 (from memory, verify) | Touch offset (dx, dy) vs key centre; multi-session evaluation | `Buschek2015_KeystrokeBiometricsTouchscreen-spatial.pdf` |
| 3 | Frank M., Biedert R., Ma E., Martinovic I., Song D. "Touchalytics: On the Applicability of Touchscreen Input as a Behavioral Biometric for Continuous Authentication." IEEE TIFS 8(1), 2013 (arXiv 1207.6231). | https://arxiv.org/abs/1207.6231 ; DOI 10.1109/TIFS.2012.2225048 (from memory, verify) | Swipe/scroll features (velocity, acceleration, deviation/curvature) | `Frank2012_Touchalytics.pdf` |
| 4 | Sitová Z., Šeděnka J., Yang Q., Peng G., Zhou G., Gasti P., Balagani K. "HMOG: New Behavioral Biometric Features for Continuous Authentication of Smartphone Users." IEEE TIFS 2016 (arXiv 1501.01199). | https://arxiv.org/abs/1501.01199 ; DOI 10.1109/TIFS.2015.2506542 (from memory, verify) | Swipes alone are weak; tap + motion fusion | `Sitova2015_HMOG.pdf` |
| 5 | Killourhy K.S., Maxion R.A. "Comparing Anomaly-Detection Algorithms for Keystroke Dynamics." IEEE/IFIP DSN 2009. | https://www.cs.cmu.edu/~keystroke/KillourhyMaxion09.pdf ; DOI 10.1109/DSN.2009.5270346 (from memory, verify) | Template + scaled Manhattan / Mahalanobis scoring | `Killourhy2009_ComparingAnomalyDetectorsKeystroke.pdf` |
| 6 | Acien A., Morales A., Monaco J.V., Vera-Rodriguez R., Fierrez J. "TypeNet: Deep Learning Keystroke Biometrics." IEEE T-BIOM 2021 (arXiv 2101.05570). | https://arxiv.org/abs/2101.05570 | Siamese / contrastive / triplet verifier; few enrollment samples | `Acien2021_TypeNet-LargeScale.pdf` |
| 7 | Stragapede G., Delgado-Santos P., Tolosana R., Vera-Rodriguez R., Guest R., Morales A. "Mobile Keystroke Biometrics Using Transformers." arXiv 2207.07596 (2022). | https://arxiv.org/abs/2207.07596 | Accuracy vs number of enrollment sessions (1/5/10) | `Stragapede2022_MobileKeystrokeTransformers.pdf` |
| 8 | Stragapede G., Vera-Rodriguez R., Tolosana R., Morales A., Damer N., Fierrez J., Ortega-Garcia J. "Keystroke Verification Challenge (KVC): Biometric and Fairness Benchmark Evaluation." arXiv 2311.06000v3. | https://arxiv.org/abs/2311.06000 | 5-enrollment protocol; benchmark for few-shot verifiers | `Stragapede2023_KVC-KeystrokeVerificationChallenge.pdf` |
| 9 | Georgiev M., Eberz S., Turner H., Lovisotto G., Martinovic I. "FETA: Fair Evaluation of Touch-based Authentication." arXiv 2201.10606v2 (2023). | https://arxiv.org/abs/2201.10606 | Evaluation hygiene (plan §5.5) | `Georgiev2022_FETA-touchAuthEval.pdf` |
| 10 | Khan H., Hengartner U., Vogel D. "Augmented Reality-based Mimicry Attacks on Behaviour-Based Smartphone Authentication." ACM MobiSys 2018. | https://cs.uwaterloo.ca/~uhengart/publications/mobisys18.pdf ; DOI 10.1145/3210240.3210317 (from memory, verify) | Limits: keystroke template can be mimicked | `Khan2018_ARMimicryAttacks.pdf` |
| 11 | Biggio B., Fumera G., Roli F., Didaci L. "Poisoning Adaptive Biometric Systems." SSPR&SPR 2012, LNCS 7626. | https://link.springer.com/content/pdf/10.1007/978-3-642-34166-3_46.pdf ; DOI 10.1007/978-3-642-34166-3_46 | Template poisoning via self-update | `Biggio2012_PoisoningAdaptiveBiometricSystems.pdf` |
| 12 | Lovisotto G., Eberz S., Martinovic I. "Biometric Backdoors: A Poisoning Attack Against Unsupervised Template Updating." IEEE EuroS&P 2020 (arXiv 1905.09162). | https://arxiv.org/abs/1905.09162 | Update threshold is not enough on its own; detecting drift | `Lovisotto2020_BiometricBackdoors-TemplatePoisoning.pdf` |
| 13 | Giot R., Rosenberger C., Dorizzi B. "Hybrid Template Update System for Unimodal Biometric Systems." BTAS 2012 (arXiv 1207.0783). | https://arxiv.org/abs/1207.0783 | Template update for keystroke dynamics (sliding vs growing window) | `Giot2012_HybridTemplateUpdate.pdf` |
| 14 | Biggio B., Didaci L., Fumera G., Roli F. "Poisoning attacks to compromise face templates." ICB 2013. | DOI 10.1109/ICB.2013.6613006 | Template poisoning (follow-up to #11) | paywalled (the author-site PDF URL tried returned HTML) |
| 15 | Pisani P.H., Giot R., de Carvalho A.C.P.L.F., Lorena A.C. "Enhanced template update: Application to keystroke dynamics." Computers & Security, 2016. | DOI 10.1016/j.cose.2016.04.004 | Keystroke template update | paywalled (not read) |
| 16 | Pisani P.H. et al. "Adaptive Biometric Systems: Review and Perspectives." ACM Computing Surveys 2019. | https://www.researchgate.net/publication/334289043 | Survey of self-update / co-update | paywalled (not read; DOI not checked) |

---

## Q1. Do PIN tapping rhythm and touch-position offset tell people apart on smartphones?

### Takeaway
Yes. On a soft PIN keypad, timing (hold time and inter-key latency) combined with touch features reaches an EER of about 3.65–7% with one person per template (Zheng 2014). Touch-to-key offset features cut keystroke EER by 26–37% compared with timing alone (Buschek 2015). This backs the "PIN rhythm" and "touch position" rows of §5.0. One caveat: Buschek found that pressure alone gave low single-feature EERs, but the plan correctly avoids depending on it.

### Cited Findings
- Zheng et al. collected 11,062 PIN entries from over 80 users. They used four feature sets: time, pressure, touched size and acceleration (a 4-digit PIN gives 7 time features; an 8-digit PIN gives 15). They report average EERs "down to 3.65%" — [Zheng 2014](https://www.eecis.udel.edu/~hnw/paper/tapping.pdf)
- Per-PIN EERs in Zheng Table 3 range from 3.65% to 7.37%. PINs with repeated digits (1-1-1-1, 5-5-5-5) are less accurate than 3-2-4-4 and the two 8-digit PINs. Combining all four feature sets always beat any single set — [Zheng 2014](https://www.eecis.udel.edu/~hnw/paper/tapping.pdf)
- Buschek et al. (28 users × 2 sessions × 3 postures × 6 passwords × 20 repetitions) added spatial features to the usual hold/flight times: touch down/up location, offset to the key centre, "jumps" between touches, and drag. Combined spatial and temporal sets gave 26.4–36.8% lower EER than the best temporal-only sets, and 8.5–26.3% lower than spatial-only sets — [Buschek 2015](http://www.florian-alt.org/unibw/wp-content/publications/buschek2015chi.pdf)
- Buschek: in the best wrapper-selected feature sets, offsets were the most important addition. Down-pressure had low single-feature EER but never appeared in the best sets — [Buschek 2015](http://www.florian-alt.org/unibw/wp-content/publications/buschek2015chi.pdf)
- Buschek: single-session evaluation gave EERs less than half of those across sessions (classifiers had 51–73% lower EER within a session), so they recommend collecting data in at least 2 sessions — [Buschek 2015](http://www.florian-alt.org/unibw/wp-content/publications/buschek2015chi.pdf)
- The Buschek related-work section cites prior PIN-unlock work with EERs of 3.65–7.34% using distance-based anomaly detection, which matches Zheng — [Buschek 2015](http://www.florian-alt.org/unibw/wp-content/publications/buschek2015chi.pdf)

### Inferences
- Feeding the custom PIN keypad's pointer-event coordinates into dx/dy offsets is supported by Buschek. The plan's claim that PIN rhythm is "strongest" is only partly supported: Buschek shows offsets plus timing beats timing alone. Phrase it as "timing + spatial together are strongest".
- Zheng's PIN EERs depend heavily on PIN content (repeated digits are worse). Each user has their own PIN, so expect per-user variance.

### Gaps
- Zheng's 3.65% uses 85 training actions per user and a fixed PIN shared across users, so it is not directly comparable to 3–5 enrollments.
- Zheng's acceleration features need motion sensors, which the plan's web Pointer Events setup does not collect. Expect higher EER without them; Zheng's Fig. 10 has per-feature-set EERs, which I did not transcribe.

## Q2. Are swipe/scroll features (velocity, acceleration, curvature) useful for continuous authentication?

### Takeaway
They are useful, but much weaker per gesture than PIN features. Touchalytics needs about 11–12 strokes to reach 2–3% EER. HMOG reports 25.7–34.2% EER for tap/hold/swipe features alone. This supports the plan's wording "Người vs máy; bổ sung nhận diện" (human vs machine; supplementary identification) (supporting signal, not the primary owner signal).

### Cited Findings
- Touchalytics proposes 30 behavioural stroke features. Median EER is 0% intra-session, 2–3% inter-session, and below 4% one week after enrollment — [Frank 2012/2013](https://arxiv.org/abs/1207.6231)
- Touchalytics ranks features by relative mutual information with user identity. Top features: 20th-percentile pairwise velocity (19.63%), average velocity (8.84%), 80th-percentile velocity (7.85%), median velocity at the last 3 points (7.24%), and largest deviation from the end-to-end line (6.08%, a curvature proxy) — [Frank 2012](https://arxiv.org/abs/1207.6231)
- Touchalytics: the EER converges to 2–3% at about 11–12 strokes per decision and stays there up to 20 strokes. They used 11 strokes, i.e. 11–43 s per decision — [Frank 2012](https://arxiv.org/abs/1207.6231)
- HMOG: tap, key-hold and swipe features alone had 25.7–34.2% EER. HMOG (motion) features gave 7.16% (walking) and 10.05% (sitting). Adding tap/keystroke features to HMOG lowered EER from 17.93% to 11.74% (walking) and from 19.11% to 15.25% (sitting) — [Sitová 2015](https://arxiv.org/abs/1501.01199)

### Inferences
- A wallet session usually has only a few swipes before payment, far fewer than Touchalytics' 11 strokes. Swipe features should be a low-weight signal in Model 2 and mainly a bot/human signal in Model 1.

### Gaps
- No paper here evaluates swipe features from web Pointer Events (all use native Android logs).

## Q3. Template scoring with per-feature normalized distance (scaled Manhattan, Mahalanobis)

### Takeaway
This is strongly supported. In the standard keystroke benchmark, scaled Manhattan (mean template, each feature divided by its spread) was the best of 14 detectors (EER 9.6%). Zheng's PIN system uses the same idea: an L1 distance where each feature is divided by its standard deviation. This is exactly the plan's "Bản 1" (Version 1).

### Cited Findings
- Killourhy & Maxion: 51 subjects typed the same password 400 times each, and 14 anomaly detectors were evaluated. EER ranking: Manhattan (scaled) 0.096; Nearest Neighbor (Mahalanobis) 0.100; Outlier Count (z-score) 0.102; SVM one-class 0.102; Mahalanobis 0.110; Manhattan (filtered) 0.136 — [Killourhy & Maxion 2009](https://www.cs.cmu.edu/~keystroke/KillourhyMaxion09.pdf)
- Killourhy & Maxion scaled Manhattan: the score is the Manhattan distance to the mean vector, with each feature dimension divided by its mean absolute deviation in training. The paper's data set (DSL-StrongPassword) is public — [Killourhy & Maxion 2009](https://www.cs.cmu.edu/~keystroke/KillourhyMaxion09.pdf)
- Caveat from the same table: at zero-miss (no impostor accepted), scaled Manhattan ranks only 5th (false-alarm 0.601), while NN-Mahalanobis is best (0.468). Detector ranking depends on the operating point — [Killourhy & Maxion 2009](https://www.cs.cmu.edu/~keystroke/KillourhyMaxion09.pdf)
- Zheng: dissimilarity d(XQ, Xi) = Σ_j |XQ,j − Xi,j| / σ_j, and the decision uses the nearest enrollment sample. The authors note that dividing by σ_j gives more weight to stable features (z-score idea) — [Zheng 2014](https://www.eecis.udel.edu/~hnw/paper/tapping.pdf)

### Inferences
- The explainability claim ("PIN chậm hơn 40%", PIN 40% slower) falls naturally out of per-feature z-score terms in scaled Manhattan; each term is one feature's contribution.
- With only 3–5 enrollments, σ_j estimates are very noisy. Use a floor on σ_j (or a population-level prior) to avoid division by near-zero. This is my inference; it is not tested in these papers.

### Gaps
- Killourhy uses desktop keyboard timing only (no touch). No paper found compares these detectors on mobile PIN data with 3–5 enrollments.

## Q4. Few-shot / pairwise / Siamese verifiers for behavioural biometrics

### Takeaway
This is supported. TypeNet trains one shared embedding with softmax, contrastive (Siamese) or triplet loss, and verifies new users never seen in training by distance to a few gallery samples. Triplet loss was best and contrastive second; it works one-shot (G=1) but improves strongly with G=5–10. This is the academic basis for "Bản 2" (Version 2).

### Cited Findings
- TypeNet (LSTM, trained on 100k+ subjects): EER 2.2% (physical keyboard) and 9.2% (touchscreen), on test users not seen in training — [Acien 2021](https://arxiv.org/abs/2101.05570)
- TypeNet scores by the average Euclidean distance between the query embedding and G gallery (enrollment) embeddings. Mobile results: the best was M=100 keystrokes and G=10 with triplet loss at 6.3% EER, then contrastive 10.0% and softmax 12.3%. One-shot (G=1) triplet loss degraded to 10.7% — [Acien 2021](https://arxiv.org/abs/2101.05570)
- TypeNet: in mobile, "there is a significant improvement when increasing the number of sequences per subject", while sequence length beyond 70 keys barely helps. Under a fixed G=5 protocol, TypeNet beat SVM/digraph baselines, which "require a large number of training sequences per subject (100)" — [Acien 2021](https://arxiv.org/abs/2101.05570)
- Stragapede 2022 (Transformer, Aalto mobile set): EER 3.84% with 5 enrollment sessions, vs 9.20% for TypeNet under the same protocol — [Stragapede 2022](https://arxiv.org/abs/2207.07596)
- KVC benchmark uses 5 enrollment sessions per subject and reports results for triplet-loss models (a value of 10.164% for mobile and 12.949% for desktop appears in the text; the metric symbol was lost in PDF extraction, so check it in the PDF before quoting) — [Stragapede 2023 KVC](https://arxiv.org/abs/2311.06000)

### Inferences
- The plan's "~25 people × 5 sessions → thousands of pairs" is tiny next to TypeNet (100k+ subjects). A pairwise model on 25 people risks overfitting to those people. Use leave-users-out validation (as FETA recommends) and present Bản 2 as an experiment, with Bản 1 as the baseline.
- Feature-difference input |x_a − x_b| into a GBM/logistic model is a lightweight form of Siamese verification. I found no paper testing exactly that on PIN data.

### Gaps
- I did not find a peer-reviewed Siamese verifier specifically for PIN tapping or swipe data in this pass. TypeNet and KVC are free-text keystroke.

## Q5. Template adaptation and the poisoning risk ("only update after high-confidence accepted sessions")

### Takeaway
Self-update with a confidence threshold is the standard technique, so the plan's rule matches the literature. The same literature also shows that a threshold alone does not stop a patient attacker: poisoning can walk the template toward the attacker in small accepted steps. Add rate limits and a drift check.

### Cited Findings
- Biggio et al. define template self-update as updating the template x_c with sample x only if s(x, x_c) ≥ an update threshold, usually stricter than the acceptance threshold. They show a crafted sequence of samples can "gradually poison" the template until the attacker is accepted (PCA face verification) — [Biggio 2012](https://link.springer.com/content/pdf/10.1007/978-3-642-34166-3_46.pdf)
- Lovisotto et al.: "biometric backdoors" craft intermediate samples that each pass the self-update threshold. White-box attacks succeed in over 70% of cases with fewer than ten injection attempts, and black-box in about 15%. Their countermeasure detects the consistent direction of template updates: 7–14% EER, with over 99% of attacks detected after two injections — [Lovisotto 2020](https://arxiv.org/abs/1905.09162)
- Lovisotto notes supervised updating (e.g. Windows Hello asks for PIN/password re-entry before an update) as the safer alternative to unsupervised updating — [Lovisotto 2020](https://arxiv.org/abs/1905.09162)
- Giot et al. evaluate keystroke template update on public sets (8 sessions on DSL2009, 5 on GREYC2009). They compare no update, sliding window and growing window, report impostor-update metrics (IUSR), and show a hybrid scheme beats classic self-update — [Giot 2012](https://arxiv.org/abs/1207.0783)
- Biggio et al. 2013 (ICB) extend poisoning to face templates (DOI 10.1109/ICB.2013.6613006). Paywalled, not read — [Semantic Scholar](https://www.semanticscholar.org/paper/0288c17e7f5a48c182124da31d2e7b31d8a131cf)

### Inferences
- Concrete design consequences: (a) the update threshold must be stricter than the accept threshold; (b) use a sliding window that caps how far the template can move per day; (c) update only on sessions that also passed a non-behavioural factor (PIN correct + known device), matching "supervised update"; (d) monitor drift direction across consecutive updates (Lovisotto countermeasure).

### Gaps
- No poisoning study found specifically on mobile touch/PIN behavioural templates; the evidence is from face (Biggio, Lovisotto) and keystroke update (Giot). Pisani 2016 (keystroke, paywalled) was not read.

## Q6. How many enrollment samples are needed (1/3/5)?

### Takeaway
More enrollment samples help a lot, and 1 is clearly worse. Deep shared models (TypeNet/Transformer) work with 5 and lose roughly half their accuracy at 1. Per-user template methods like Zheng's used far more (accuracy plateaus around 20 PIN entries; EER reported at 85). 3–5 enrollments are realistic only for a pretrained shared model, or with progressive enrollment via safe updates.

### Cited Findings
- Stragapede 2022, Aalto mobile EER by enrollment sessions E (TypeNet → Transformer): E=1: 12.60% → 6.99%; E=5: 9.20% → 3.84%; E=10: 8.00% → 3.15% — [Stragapede 2022](https://arxiv.org/abs/2207.07596)
- TypeNet mobile: triplet 6.3% at G=10 vs 10.7% at G=1 — [Acien 2021](https://arxiv.org/abs/2101.05570)
- Zheng: accuracy "remains on a similar level after 20 user actions", with diminishing gains from 20 to 40; Table 3 EERs use 85 training actions — [Zheng 2014](https://www.eecis.udel.edu/~hnw/paper/tapping.pdf)
- Touchalytics needs about 11–12 strokes per decision for its 2–3% EER — [Frank 2012](https://arxiv.org/abs/1207.6231)
- Buschek: training and testing in one session gives less than half the EER of cross-session testing, so enrollment should span at least 2 sessions/days — [Buschek 2015](http://www.florian-alt.org/unibw/wp-content/publications/buschek2015chi.pdf)

### Inferences
- With 3–5 PIN entries in one sitting, a Zheng-style template will be noisier than the published 3.65–7%. Present demo results honestly, and grow the template over the first weeks using Q5's guarded update.

### Gaps
- No paper found reports PIN-tap EER specifically at 3 enrollments.

## Evaluation caveats and attacks (supports plan §5.5 and §8)

### Cited Findings
- FETA: evaluation pitfalls change mean EER by several points. Including attacker data in training: 2.55 pp; non-contiguous training data: 3.8 pp; mixing phone models: 3.2–5.8 pp. Combined: 8.9 pp EER — [Georgiev 2022 FETA](https://arxiv.org/abs/2201.10606)
- Khan et al.: an AR app that guides an attacker let them bypass keystroke dynamics in 87% of attacks after about 4 minutes of mimicry training, and on the first try in 73%, vs a 6% baseline — [Khan 2018](https://cs.uwaterloo.ca/~uhengart/publications/mobisys18.pdf)
- Inference: present behavioural owner verification as a risk signal fused with others (plan §5.3), not a standalone gate.
