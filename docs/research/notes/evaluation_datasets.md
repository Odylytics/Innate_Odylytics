# Evaluation methodology & datasets — academic backing for Innate (plan §5.5, §8, §10)

Scope: papers that back the plan's evaluation choices (temporal split, single phone, no impostor data in training, report EER + FAR@FRR=5% + per-tactic bot catch rate + accuracy vs. #enrolments 1/3/5), plus public datasets usable for benchmarking. Local PDFs live in `C:/TuanNghia/Project/Momo_Odylytics/papers/evaluation-datasets/` (all verified `%PDF` header, all < 11 MB). Numbers below were read from the PDF text unless stated otherwise.

## Q1. Common pitfalls in evaluating touch/behavioral biometrics (random vs temporal split, multiple devices, impostor data in training, EER-only)

### Takeaway
FETA (Georgiev et al.) quantifies exactly the pitfalls the plan avoids: random (non-contiguous) splits, mixing phone models and putting attacker data in training each make the EER look better, and together they turn a realistic 13.8% EER into an "unrealistic" 4.9%. All 30 touch papers they reviewed fall into at least one pitfall. Eberz et al. 2017 and Sugrim et al. 2019 add that one mean EER hides systematic errors and threshold-dependent behaviour.

### Cited Findings
- FETA names six pitfalls: small sample size, phone model mixing, non-contiguous training data, attacker samples in training, swipe aggregation, and code/dataset availability. "All published studies overlook at least one of the pitfalls" (30 touch-dynamics papers reviewed). — [Georgiev et al., FETA, arXiv:2201.10606v2](https://arxiv.org/abs/2201.10606)
- FETA dataset: 515 users over 31 days, 1,194,451 strokes. Mean EER effects: attacker data in training 2.55 percentage points (pp); non-contiguous training data 3.8 pp; phone-model mixing 3.2–5.8 pp; combined effect 8.9 pp. — [FETA abstract](https://arxiv.org/abs/2201.10606)
- FETA Fig. 7 (ROC, SVM): "Realistic" evaluation gives 13.8% EER, while all pitfalls together ("Unrealistic") give 4.9%. Random vs contiguous training selection: 6.4% vs 8.6% EER. — [FETA PDF, Fig. 6–7](https://arxiv.org/pdf/2201.10606v2)
- FETA: "an unrealistic training data selection can lead to an increase in performance of 3.8% EER when using a RANDOM approach compared to the DEDICATEDSESSIONS approach". The DEDICATEDSESSIONS approach trains on the first sessions and tests on later sessions, which is the plan's "đăng ký bằng phiên trước, kiểm thử bằng phiên sau" (enroll on earlier sessions, test on later ones). — [FETA PDF §6](https://arxiv.org/pdf/2201.10606v2)
- FETA: 80% of reviewed studies "use an unrealistic attacker modeling approach and include attacker data into the training set". A further 18% use randomized data selection. 17% report only aggregated (multi-swipe) results. — [FETA PDF §3](https://arxiv.org/pdf/2201.10606v2)
- FETA Table 4: mixing phone models (COMBINED) "results in overestimation of performance even when subsampling to the number of users present in each specific phone model". A classifier can also identify the iPhone model from a single swipe, which shows that device artefacts leak into features. — [FETA PDF §7, Table 4](https://arxiv.org/pdf/2201.10606v2)
- FETA notes that most Android devices approximate touch pressure from touch size. This supports the plan's choice to drop `pressure`. — [FETA PDF §4](https://arxiv.org/pdf/2201.10606v2)
- A conference version exists: "Common evaluation pitfalls in touch-based authentication systems", AsiaCCS 2022 (same authors). I could not confirm a journal DOI for the FETA v2 manuscript, so cite it as arXiv:2201.10606v2 (2023), DOI 10.48550/arXiv.2201.10606. — [search result / Google Scholar listing](https://arxiv.org/abs/2201.10606)
- Eberz et al. 2017 surveyed 25 papers (5 biometrics) and 16 datasets. "Most papers only report the mean of these measures [FAR/FRR] with little attention paid to their distribution". Systematic errors let attackers "perpetually escape detection". "Blind optimization of the mean EER … can sometimes lead to lower security". They propose the Gini Coefficient. Touchscreen input shows more even error distributions than eye movements. — [Eberz et al., AsiaCCS 2017, ORA/Oxford PDF](https://www.cs.ox.ac.uk/files/14899/asiaccs17.pdf)
- Eberz 2017: for false rejects, even a low, non-zero FRR for every user "might still lead to frequent false alarms due to the base rate fallacy" when the system runs often. This argues for fixing FRR at a usable level. — [Eberz 2017](https://www.cs.ox.ac.uk/files/14899/asiaccs17.pdf)
- Sugrim et al. (NDSS 2019) surveyed 35 publications and found "no uniform approach for reporting metrics". They argue that TPR, FPR, EER, AUROC, ACC and GC are "inherently flawed" as single numbers, and recommend full ROC curves plus the frequency count of scores (FCS). — [Sugrim et al., NDSS 2019 PDF](http://jannelindqvist.com/publications/NDSS19-robustmetrics.pdf)
- Touchalytics itself warns that a mouse-dynamics result (FAR 0.36%, FRR 0%) was "suspected that this result was influenced by recording the data on a different computer for each user". This is the device-confound reason for using one phone for everyone. — [Frank et al. 2013, arXiv:1207.6231](https://arxiv.org/pdf/1207.6231)
- BehavePassDB's authors also criticise protocols where each user uses their own device, because extracted "features of user might in reality be related" to the device. — [Stragapede et al., BehavePassDB, arXiv:2206.02502](https://arxiv.org/abs/2206.02502)

### Inferences
- The plan's §5.5 choices (temporal split, one phone, no random split) are each a named FETA pitfall avoided. The slide can cite FETA's 4.9% → 13.8% gap as the reason Innate's numbers may look "worse" than the literature but are honest.
- Pairwise verifier (Model 2, Version 2 / "Bản 2"): train it on pairs from a disjoint set of people, never on the test people's impostor data. This keeps the open-set protocol used by FETA (EXCLUDEATK) and KVC.
- Reporting per-user EER spread (or the Gini coefficient) would answer the Eberz critique cheaply.

### Gaps
- FETA does not give a numeric effect for the "EER-only" reporting choice. It argues it qualitatively and shows full ROC curves.
- No paper found evaluates a PIN-pad-only (4-digit) task with the FETA protocol. FETA is about swipes/scrolls.

## Q2. Temporal drift / template aging in touch biometrics

### Takeaway
Error grows with the time gap between enrolment and test. Touchalytics goes from 0% median EER intra-session to 2–3% inter-session and up to 4% one week later, and from about 13% with a single stroke. Surveys say touch dynamics are "not stable over time" and recommend template adaptation. This backs both the temporal split and the plan's "only update template after high-confidence accepts".

### Cited Findings
- Touchalytics (41 users, scrolling/swiping): median EER is 0% intra-session, 2–3% inter-session and "below 4%" one week after enrolment. "The authentication difficulty seems to increase with increasing temporal distance to the training phase". The authors say this "disqualif[ies] this method as a standalone authentication mechanism for long-term authentication". — [Frank et al., IEEE TIFS 8(1):136–148, 2013, DOI 10.1109/TIFS.2012.2225048](https://arxiv.org/abs/1207.6231)
- Touchalytics: intra-session tests used "randomly subsampled strokes from the entire corpus". This is the optimistic random-split setting. — [Frank 2013 Fig. 6 caption](https://arxiv.org/pdf/1207.6231)
- Touchalytics: a single-stroke decision gives about 13% EER, and 11–12 strokes converge to 2–3% (inter-session). This supports the plan's choice to report both single-session and aggregated levels. — [Frank 2013 §Results](https://arxiv.org/pdf/1207.6231)
- HMOG (100 users, 8 sessions) trains on the first two sessions and tests on the remaining two. It uses one-class verifiers such as scaled Manhattan (template = feature mean, scaled by per-user std), the same idea as Innate's Bản 1. It deliberately avoids 2-class verifiers because they need other users' biometric data. Best EER is 7.16% walking and 10.05% sitting with HMOG+tap+keystroke. — [Sitová et al., IEEE TIFS 2016, arXiv:1501.01199](https://arxiv.org/abs/1501.01199)
- Teh et al. survey: 64% of reviewed touch-dynamics experiments collected each subject's data in a single session. "Touch dynamics biometrics, like other behavioral biometrics … is not stable over time". The survey describes data adaptation (updating the template after each successful authentication) to track gradual change. — [Teh et al., Computers & Security 59:210–235, 2016, DOI 10.1016/j.cose.2016.03.003; Manchester preprint](https://pure.manchester.ac.uk/ws/files/33082822/COSE_Preprint_escholar.pdf)
- FETA (31-day dataset): non-contiguous training selection inflates performance by 3.8 pp EER. In effect, random splits hide drift. — [FETA](https://arxiv.org/abs/2201.10606)

### Inferences
- With only 3–5 enrolment sessions over about 3 days (plan §7), Innate can only measure short-term inter-session drift, not week-scale aging. Say so on the slide.
- The plan's guarded template update (only after high-match accepts) matches Teh's adaptation idea. The poisoning risk is covered by other notes, not here.

### Gaps
- I did not retrieve a dedicated "Roy et al." template-aging paper for touch. FETA cites Watanabe & Kun 2017 ("Long-term influence of user identification based on touch operation", Procedia CS 112) as a long-term study, but I did not read it.
- No quantitative week-over-week PIN-tap drift figure was found.

## Q3. Metrics: EER, FAR@FRR, ROC/DET, ISO/IEC 19795

### Takeaway
ISO/IEC 19795-1 asks for error rates at stated operating points, DET curves and uncertainty intervals, not just a threshold-free summary. Recent work (Ahmed & Imtiaz 2026) and Sugrim 2019 argue that the error rate at a fixed operating point is the primary number. KVC already reports FNMR@1%/10% FMR. This directly backs "FAR khi FRR = 5%" alongside EER.

### Cited Findings
- ISO/IEC 19795-1:2021, "Biometric performance testing and reporting — Part 1: Principles and framework" (2nd ed., May 2021, JTC 1/SC 37). It specifies performance metrics (FMR/FNMR, FAR/FRR), requirements on test protocols and on reporting. The standard is paywalled. — [ISO page](https://www.iso.org/standard/73515.html)
- Ahmed & Imtiaz (arXiv 2026): "ISO/IEC 19795-1 asks for error rates at stated operating points, for the detection error tradeoff (DET) curve … and for an interval of uncertainty on every value". A single ROC-AUC or EER "is a threshold-independent summary that the standard does not endorse". On face data, the system with the higher AUC was significantly worse at FMR = 10⁻³. They recommend "the DET curve and the FNMR at a fixed FMR … as the primary report, with ROC-AUC and EER retained as supplementary context". — [Ahmed & Imtiaz, arXiv:2606.20680](https://arxiv.org/abs/2606.20680) (recent preprint, not peer-reviewed as far as I could tell; modalities are face/voice/iris/fingerprint, not touch)
- KVC benchmark metrics include EER plus "FNMR @ X% FMR" with X = 1% and 10%, described as a point on the DET curve. — [Stragapede et al., KVC, arXiv:2311.06000](https://arxiv.org/abs/2311.06000)
- Sugrim 2019: metrics derived from a confusion matrix "depend on the threshold". When only such numbers are reported, "the system cannot be implemented". They recommend full ROC plus score distributions. — [Sugrim NDSS 2019](http://jannelindqvist.com/publications/NDSS19-robustmetrics.pdf)
- Touchalytics justifies reporting EER because "the preferences for one or the other [FRR vs FAR] clearly depends on the individual application scenario". In other words, the paper does not pick an operating point, which a deployed product must do. — [Frank 2013](https://arxiv.org/pdf/1207.6231)
- Eberz 2017: the base-rate fallacy makes non-zero FRR costly for frequently used systems. This is the usability argument for fixing FRR at a low value (plan: FRR ≈ 5%). — [Eberz 2017](https://www.cs.ox.ac.uk/files/14899/asiaccs17.pdf)

### Inferences
- In 19795 terms, Innate's "FAR @ FRR = 5%" is the mirror of "FNMR @ fixed FMR". Both are operating-point metrics. Because the product's cost is user friction (step_up), fixing FRR is the defensible choice. Plot a DET curve too.
- With ~25 people the number of impostor comparisons is small. Bootstrap confidence intervals (as Ahmed & Imtiaz do) would satisfy the "interval of uncertainty" requirement.

### Gaps
- I could not read ISO/IEC 19795-1 itself (paywalled). Statements about its content come from the ISO abstract and secondary papers.

## Q4. Public datasets for training/benchmarking

### Takeaway
Several free datasets match parts of Innate's signal set. HuMIdb is the closest fit for human-vs-bot (600 users, 14 sensors, with a BeCAPTCHA bot benchmark). Aalto/KVC is the best fit for mobile keystroke timing at scale. HMOG and BehavePassDB fit multi-session touch plus sensors on fixed devices. BB-MAS fits cross-device behaviour. MobileTouchDB is touch-drawn PINs on 94 phone models.

### Cited Findings
- **HMOG**: 100 users (53 male, 47 female), 8 free-text typing sessions (4 sitting, 4 walking), touch, keystroke and accelerometer/gyroscope/magnetometer sensors at 100 Hz, custom virtual keyboard. — [Sitová et al. 2016, arXiv:1501.01199](https://arxiv.org/abs/1501.01199). Dataset access/licence: not verified in this pass.
- **Touchalytics/Frank**: 41 users; scrolling and swiping; inter-session plus a one-week follow-up. — [Frank 2013](https://arxiv.org/abs/1207.6231). Dataset licence: not verified.
- **FETA dataset**: 515 users over 31 days, 1,194,451 strokes on constrained iPhone models; "dataset and our code are available online". — [FETA](https://arxiv.org/abs/2201.10606)
- **BB-MAS**: 117 participants; typing, gait and swipes on desktop, phone and tablet by the same users. Hosted on IEEE DataPort, DOI 10.21227/rpaz-0h66, described as "open-access". Finding: key-hold times are shorter and inter-key latencies longer on handheld devices than on desktop. — [Belman et al., arXiv:1912.02736](https://arxiv.org/abs/1912.02736)
- **Aalto mobile typing (typing37k)**: 37,370 volunteers on their own phones in a web transcription task; 36.2 WPM, 2.3% uncorrected errors; 74% type with two thumbs. Raw, processed and CSV data plus source code are downloadable from the project page. MobileHCI 2019, DOI 10.1145/3338286.3340120. — [Palin et al. 2019](https://userinterfaces.aalto.fi/typing37k/). Licence terms: not verified. Caveat: many device models (the FETA phone-mixing pitfall).
- **KVC (Keystroke Verification Challenge)**: benchmark built on the Aalto desktop and mobile keystroke databases, "over 185,000 subjects"; open-set protocol (development and evaluation subjects disjoint); hosted on CodaLab (competition 14063); introduces the Skewed Impostor Ratio fairness metric; time-domain features without key content for privacy. Example TypeFormer mobile EER ≈ 9.4–10.2% (mean over 10 subsets). — [Stragapede et al., arXiv:2311.06000](https://arxiv.org/abs/2311.06000)
- **TypeNet**: on the Aalto mobile set, EER 9.2% (touchscreen) vs 2.2% (physical keyboard). Mobile EER with triplet loss and M = 100 keys falls from 10.7% (1 enrolment sequence) to 8.9% (2), 7.3% (5), 6.6% (7) and 6.3% (10). This backs reporting accuracy against the number of enrolments (1/3/5). — [Acien et al., IEEE T-BIOM 2021, arXiv:2101.05570](https://arxiv.org/abs/2101.05570)
- **BehavePassDB**: 81 users, 4 acquisition sessions × 8 tasks, 15 modalities (touch plus background sensors). Provides random-impostor (different user, different device) and skilled-impostor scenarios; distributed via GitHub BiDAlab/MobileB2C_BehavePassDB. Basis of the IJCB 2022 MobileB2C competition (arXiv:2210.03072). — [Stragapede et al., arXiv:2206.02502](https://arxiv.org/abs/2206.02502)
- **HuMIdb / BeCAPTCHA-Mobile**: 600 users, 14 sensors, "freely available to the research community" (github.com/BiDAlab/HuMIdb). BeCAPTCHA tests bot detection against fake drag-and-drop samples synthesised with GANs and handcrafted methods. This is the closest precedent for the plan's per-tactic bot simulator (Model 1). — [Acien et al., arXiv:2005.13655](https://arxiv.org/abs/2005.13655)
- **MobileTouchDB**: 217 users, 94 smartphone models, characters drawn on the touchscreen. BioTouchPass2 (TA-RNN) reaches 2.38% EER with a 4-digit password and one training sample per character. IEEE TIFS 2020, DOI 10.1109/TIFS.2020.2973832; data on github.com/BiDAlab/MobileTouchDB. — [Tolosana et al., arXiv:2001.10223](https://arxiv.org/abs/2001.10223)
- **UMDAA-02**: multi-modal (front camera, touch, location and more) smartphone dataset from the University of Maryland (BTAS 2016). Benchmarks "indicate that more robust methods fine-tuned to the mobile platform are needed". — [Mahbub et al., arXiv:1610.07930](https://arxiv.org/abs/1610.07930)

### Inferences
- For a 10-day contest, the most useful external benchmark is (a) HuMIdb for the human-vs-bot model and (b) KVC/Aalto mobile for a sanity check of PIN-timing features. Both are free, but their licences must be checked before use and listed in the README.
- None of these datasets uses a self-drawn PIN pad captured through web Pointer Events. External numbers are context only, not directly comparable.

### Gaps
- I did not verify exact licence texts (CC-BY, research-only, EULA) for HMOG, Aalto, HuMIdb, BehavePassDB, MobileTouchDB or FETA. Check each homepage or GitHub README before use.
- I did not find an exact PIN-tapping dataset with impostors who know the PIN beyond the per-paper data in §10 of the plan.

## Q5. Surveys of touch-based continuous authentication

### Takeaway
Three surveys frame the field: Teh et al. 2016 (touch dynamics, open preprint), Patel et al. 2016 (IEEE SPM, paywalled) and Stylios et al. 2021 (Information Fusion, paywalled). They agree that fusing modalities helps and that stability over time and evaluation consistency are open problems.

### Cited Findings
- Teh, Zhang, Teoh & Chen (2016), Computers & Security 59:210–235: reviews touch-dynamics work and data-acquisition practice. 64% of studies used single-session collection; the survey discusses template data adaptation. — [Manchester preprint](https://pure.manchester.ac.uk/ws/files/33082822/COSE_Preprint_escholar.pdf)
- Patel, Chellappa, Chandra & Barbello (2016), "Continuous user authentication on mobile devices: Recent progress and remaining challenges", IEEE Signal Processing Magazine 33(4):49–61, DOI 10.1109/MSP.2016.2555335: overview of methods, merits and drawbacks, and open challenges. — [Semantic Scholar](https://www.semanticscholar.org/paper/b77c9f03d6300d5d1d193e92c0ac422bf3b586c6). Paywalled; no arXiv version found.
- Stylios, Kokolakis, Thanou & Chatzis (2021), "Behavioral biometrics & continuous user authentication on mobile devices: A survey", Information Fusion 66:76–99, DOI 10.1016/j.inffus.2020.08.021: sorts the field into 7 categories (gait, touch gestures, keystroke, behavioural profiling, hand waving, power consumption, fusion); highlights that fusion improves results. — [ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S1566253520303493). Paywalled.

### Inferences
- Cite Teh 2016 (open) for "touch is not stable over time / single-session studies are optimistic". Cite Stylios 2021 for "fusion of signals helps", which supports Model 3's fusion of risk signals.

### Gaps
- I did not read the full text of Patel 2016 or Stylios 2021 (paywalled). The descriptions above come from abstracts and index pages.

## Q6. Per-paper catalogue (citation · link · plan claim backed · key number · local PDF)

### Takeaway
15 open-access PDFs downloaded and verified. 3 key works are paywalled (Patel 2016, Stylios 2021, ISO/IEC 19795-1).

### Cited Findings
1. Georgiev, M., Eberz, S., Turner, H., Lovisotto, G., Martinovic, I. "FETA: Fair Evaluation of Touch-based Authentication." arXiv:2201.10606v2, 2023 (conference version: AsiaCCS 2022, "Common evaluation pitfalls in touch-based authentication systems"). Backs: temporal split, one phone, no impostor data in training. Key number: realistic 13.8% vs unrealistic 4.9% EER; random split inflates by 3.8 pp. Local: `papers/evaluation-datasets/Georgiev2022_FETA-fair-evaluation-touch-auth.pdf` — [arXiv](https://arxiv.org/abs/2201.10606)
2. Frank, M., Biedert, R., Ma, E., Martinovic, I., Song, D. "Touchalytics…" IEEE TIFS 8(1):136–148, 2013. DOI 10.1109/TIFS.2012.2225048. Backs: drift over time; single- vs aggregated-session reporting. Key number: EER 0% intra-session / 2–3% inter-session / ≤4% after one week; about 13% for a single stroke. Local: `Frank2013_Touchalytics.pdf` — [arXiv](https://arxiv.org/abs/1207.6231)
3. Sitová, Z., Šeděnka, J., Yang, Q., Peng, G., Zhou, G., Gasti, P., Balagani, K. "HMOG…" IEEE TIFS 11(5), 2016. Backs: train on early sessions and test on later ones; scaled-Manhattan template (Bản 1); one-class verifiers. Key number: 100 users; EER 7.16% walking / 10.05% sitting. Local: `Sitova2016_HMOG.pdf` — [arXiv](https://arxiv.org/abs/1501.01199)
4. Eberz, S., Rasmussen, K.B., Lenders, V., Martinovic, I. "Evaluating Behavioral Biometrics for Continuous Authentication: Challenges and Metrics." AsiaCCS 2017, pp. 386–399. DOI 10.1145/3052973.3053032. Backs: do not report the mean EER alone; base-rate argument for low FRR. Key number: 25 papers and 16 datasets analysed; Gini coefficient proposed. Local: `Eberz2017_evaluating-behavioral-biometrics-metrics.pdf` — [Oxford PDF](https://www.cs.ox.ac.uk/files/14899/asiaccs17.pdf)
5. Sugrim, S., Liu, C., McLean, M., Lindqvist, J. "Robust Performance Metrics for Authentication Systems." NDSS 2019. DOI 10.14722/ndss.2019.23351. Backs: ROC and operating points over single numbers. Key number: 35 publications, no uniform metric reporting. Local: `Sugrim2019_robust-performance-metrics.pdf` — [PDF](http://jannelindqvist.com/publications/NDSS19-robustmetrics.pdf)
6. Ahmed, A., Imtiaz, M.H. "Beyond ROC-AUC: Operating-Point Performance Reporting for Biometric Verification." arXiv:2606.20680, 2026 (preprint). Backs: FAR@fixed FRR as the primary metric; ISO 19795-1 alignment; confidence intervals. Local: `Ahmed2026_beyond-ROC-AUC-operating-point.pdf` — [arXiv](https://arxiv.org/abs/2606.20680)
7. ISO/IEC 19795-1:2021, Biometric performance testing and reporting — Part 1: Principles and framework. Backs: standard terminology (FAR/FRR/FMR/FNMR, DET). Paywalled — [ISO](https://www.iso.org/standard/73515.html)
8. Stragapede, G., Vera-Rodriguez, R., Tolosana, R., Morales, A., Damer, N., Fierrez, J., Ortega-Garcia, J. "Keystroke Verification Challenge (KVC): Biometric and Fairness Benchmark Evaluation." arXiv:2311.06000v3, 2023 (IEEE Access, 2024 per later citations; not verified here). Backs: open-set protocol; FNMR@FMR metrics; Aalto data. Key number: >185k subjects; mobile EER about 9.4–10.2%. Local: `Stragapede2023_KVC-keystroke-verification-challenge.pdf` — [arXiv](https://arxiv.org/abs/2311.06000)
9. Acien, A., Morales, A., Monaco, J.V., Vera-Rodriguez, R., Fierrez, J. "TypeNet: Deep Learning Keystroke Biometrics." IEEE T-BIOM, 2021. Backs: accuracy vs number of enrolments; Siamese/triplet idea related to the pairwise verifier. Key number: mobile EER 10.7% (G=1) → 7.3% (G=5) → 6.3% (G=10). Local: `Acien2021_TypeNet-deep-keystroke.pdf` — [arXiv](https://arxiv.org/abs/2101.05570)
10. Palin, K., Feit, A.M., Kim, S., Kristensson, P.O., Oulasvirta, A. "How do people type on mobile devices? Observations from a study with 37,000 volunteers." MobileHCI 2019. DOI 10.1145/3338286.3340120. Backs: Aalto mobile dataset source. Key number: 37,370 users; 36.2 WPM. Local: `Palin2019_how-people-type-mobile-37k.pdf` — [project page](https://userinterfaces.aalto.fi/typing37k/)
11. Stragapede, G., Vera-Rodriguez, R., Tolosana, R., Morales, A. "BehavePassDB: Public Database for Mobile Behavioral Biometrics and Benchmark Evaluation." arXiv:2206.02502 (Pattern Recognition, 2023 per later citations; not verified here). Backs: multi-session dataset; device-confound caution. Key number: 81 users × 4 sessions. Local: `Stragapede2023_BehavePassDB.pdf` — [arXiv](https://arxiv.org/abs/2206.02502)
12. Acien, A., Morales, A., Fierrez, J., Vera-Rodriguez, R., Delgado-Mohatar, O. "BeCAPTCHA: Behavioral Bot Detection using Touchscreen and Mobile Sensors benchmarked on HuMIdb." arXiv:2005.13655, 2020. Backs: Model 1 human-vs-bot with synthetic (GAN/handcrafted) bots, reported per bot type. Key number: HuMIdb has 600 users and 14 sensors. Local: `Acien2020_BeCAPTCHA-Mobile-HuMIdb.pdf` — [arXiv](https://arxiv.org/abs/2005.13655)
13. Belman, A.K., Wang, L., Iyengar, S.S., Sniatala, P., Wright, R., et al. "Insights from BB-MAS — A Large Dataset for Typing, Gait and Swipes of the Same Person on Desktop, Tablet and Phone." arXiv:1912.02736, 2019. Backs: device changes alter timing features (the "user changes phone" judge question). Key number: 117 users. Local: `Belman2019_BB-MAS-dataset.pdf` — [arXiv](https://arxiv.org/abs/1912.02736)
14. Tolosana, R., Vera-Rodriguez, R., Fierrez, J., Ortega-Garcia, J. "BioTouchPass2: Touchscreen Password Biometrics Using Time-Aligned Recurrent Neural Networks." IEEE TIFS, 2020. DOI 10.1109/TIFS.2020.2973832. Backs: 4-digit PIN plus behaviour as a second factor. Key number: 2.38% EER; MobileTouchDB has 217 users and 94 phone models. Local: `Tolosana2020_BioTouchPass2-MobileTouchDB.pdf` — [arXiv](https://arxiv.org/abs/2001.10223)
15. Mahbub, U., Sarkar, S., Patel, V.M., Chellappa, R. "Active User Authentication for Smartphones: A Challenge Data Set and Benchmark Results." BTAS 2016. Backs: UMDAA-02 dataset (optional). Local: `Mahbub2016_UMDAA02-active-auth-challenge.pdf` — [arXiv](https://arxiv.org/abs/1610.07930)
16. Teh, P.S., Zhang, N., Teoh, A.B.J., Chen, K. "A survey on touch dynamics authentication in mobile devices." Computers & Security 59:210–235, 2016. DOI 10.1016/j.cose.2016.03.003. Backs: touch is not stable over time; 64% of studies are single-session. Local: `Teh2016_survey-touch-dynamics-auth.pdf` (author preprint) — [preprint](https://pure.manchester.ac.uk/ws/files/33082822/COSE_Preprint_escholar.pdf)
17. Patel, V.M., Chellappa, R., Chandra, D., Barbello, B. "Continuous user authentication on mobile devices: Recent progress and remaining challenges." IEEE SPM 33(4):49–61, 2016. DOI 10.1109/MSP.2016.2555335. Paywalled.
18. Stylios, I., Kokolakis, S., Thanou, O., Chatzis, S. "Behavioral biometrics & continuous user authentication on mobile devices: A survey." Information Fusion 66:76–99, 2021. DOI 10.1016/j.inffus.2020.08.021. Paywalled.

### Inferences
- Minimum citation set for the AI slide: FETA (protocol), Touchalytics (drift), Eberz 2017 or Ahmed 2026 plus ISO 19795-1 (metrics), TypeNet (enrolment curve), BeCAPTCHA/HuMIdb (bot detection precedent).

### Gaps
- Journal venues for KVC (IEEE Access) and BehavePassDB (Pattern Recognition) come from memory and secondary citations, not verified in this pass.
- The HMOG author list beyond the first five arXiv-listed names (Gasti, Balagani) is from memory; check against the IEEE record.
