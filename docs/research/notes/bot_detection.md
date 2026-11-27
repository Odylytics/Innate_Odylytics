# Bot detection — foundation papers for "Người hay máy?" ("Human or machine?") (plan §2 Scenario A ("Kịch bản A"), §5.1 Model 1)

PDF folder: `C:/TuanNghia/Project/Momo_Odylytics/papers/bot-detection/` (all files verified to start with `%PDF`).

## Q1. Accessibility-Service abuse / remote-control banking malware (threat model, §2 Scenario A)

### Takeaway
Peer-reviewed work shows the Android Accessibility API gives an app full UI read + inject control, and that the design flaws behind this were deliberately left unfixed by Google. Vendor reports confirm that malware families targeting Vietnam (RedHook, Gigabud) use exactly this to tap and type on the victim's behalf. So PIN, OTP and device all look "correct", which is the plan's premise.

### Cited Findings
- **Fratantonio, Y., Qian, C., Chung, S. P., Lee, W. (2017). "Cloak and Dagger: From Two Permissions to Complete Control of the UI Feedback Loop." IEEE S&P 2017, pp. 1041–1057. DOI 10.1109/SP.2017.39.** SYSTEM_ALERT_WINDOW + BIND_ACCESSIBILITY_SERVICE give complete control of the UI feedback loop. Google's a11y team marked the reported issues "won't fix" (19 May 2017), i.e. they are design-level and persist. Backs: §2 "Vì sao lọt" ("why it gets through") (the malware drives the real app). Local: `papers/bot-detection/Fratantonio2017_cloak-and-dagger.pdf` (Black Hat USA 2017 white-paper version of the same work; the IEEE version is closed access per dblp) — [cloak-and-dagger.org](https://cloak-and-dagger.org/), [BH PDF](https://blackhat.com/docs/us-17/thursday/us-17-Fratantonio-Cloak-And-Dagger-From-Two-Permissions-To-Complete-Control-Of-The-UI-Feedback-Loop-wp.pdf)
- **Diao, W., Zhang, Y., Zhang, L., Li, Z., Xu, F., Pan, X., Liu, X., Weng, J., Zhang, K., Wang, X. (2019). "Kindness is a Risky Business: On the Usage of the Accessibility APIs in Android." RAID 2019, USENIX, pp. 261–275.** A large-scale app scan finds the accessibility APIs "misused widely", including to bypass permission restrictions. Design flaws: no restriction on why the API is used, and no strong integrity guarantee for accessibility events. Backs: §2 (systemic, not a one-off bug). Local: `papers/bot-detection/Diao2019_kindness-risky-business-accessibility.pdf` — [USENIX](https://www.usenix.org/system/files/raid2019-diao.pdf)
- **Naseri, M., Borges Jr., N. P., Zeller, A., Rouvoy, R. (2019). "AccessiLeaks: Investigating Privacy Leaks Exposed by the Android Accessibility Service." PoPETs 2019(2): 291–305. DOI 10.2478/popets-2019-0031.** Just enabling an accessibility service leaves **72% of top finance apps** and 80% of top social apps open to eavesdropping, leaking logins and passwords. Backs: §2 "Mã độc xem màn hình… đọc OTP" (malware watches the screen and reads the OTP) and why PIN secrecy alone fails. Local: `papers/bot-detection/Naseri2019_accessileaks.pdf` — [PETS](https://petsymposium.org/2019/files/papers/issue2/popets-2019-0031.pdf)
- **Grey literature — Cyble CRIL (Jul 2025), "RedHook: A New Android Banking Trojan Targeting Users In Vietnam."** Delivered via a phishing site spoofing the State Bank of Vietnam (sbvhn[.]com, SBV.apk). Abuses accessibility services + MediaProjection for keylogging, screen capture and remote access over WebSocket. Active since ≥ Nov 2024, >500 infections. — [Cyble](https://cyble.com/blog/redhook-new-android-banking-targeting-in-vietnam/)
- **Grey literature — Group-IB, "Breaking down Gigabud banking malware with Fraud Matrix."** Gigabud's "TouchAction" feature abuses accessibility to perform taps, and newer versions add an accessibility keylogger. Targets include institutions in Vietnam, Thailand, Indonesia, the Philippines and Peru (Gigabud.Loan: >99 financial institutions). — [Group-IB](https://www.group-ib.com/blog/gigabud-banking-malware/)

### Inferences
- The automated input from these families comes through `AccessibilityService.dispatchGesture` or similar injected events, not through a finger. That is why §5.1 targets timing and geometry, and does not rely on credential checks.

### Gaps
- **Kraunelis et al., "On Malware Leveraging the Android Accessibility Framework" (MobiQuitous 2013)**: not fetched; paywalled (Springer LNICST). Venue and DOI not verified in this session, so check before citing.
- Leguesse et al., "Reducing the Forensic Footprint with Android Accessibility Attacks" (STM 2020) was seen only on ResearchGate ([link](https://www.researchgate.net/publication/344405451_Reducing_the_Forensic_Footprint_with_Android_Accessibility_Attacks)). Not downloaded; details unverified.
- Vendor reports on Octo/Octo2, Brata, SpyNote, Hirudo (ThreatFabric, Kaspersky, Trend Micro) were **not retrieved**: the search tool refused that query. No academic paper found that measures the timing or geometry of accessibility-injected taps in the wild, so the "nhịp quá đều, chạm đúng tâm" (rhythm too even, taps exactly on center) signature of real malware is an inference, not a cited measurement.

## Q2. Human vs. bot from touch/mouse dynamics (§2 "Tín hiệu" (signals), §5.1 "đặc trưng độ tự nhiên" (naturalness features))

### Takeaway
Bot detection from a single touch or mouse trajectory works very well against simple bots (near-perfect). Accuracy drops sharply against GAN-generated, human-like trajectories, and recovers when the model trains on those synthetic bots or adds a second signal (accelerometer). This directly backs §5.1's design: train on graded synthetic attacker data and report per-tactic results.

### Cited Findings
- **Acien, A., Morales, A., Fierrez, J., Vera-Rodriguez, R., Delgado-Mohatar, O. (2021). "BeCAPTCHA: Behavioral Bot Detection using Touchscreen and Mobile Sensors benchmarked on HuMIdb." Engineering Applications of AI 98:104058. arXiv:2005.13655.**
  - Task: one drag-and-drop on a phone; bots are handcrafted or GAN-synthesized trajectories; dataset HuMIdb has 600 users and 14 sensors.
  - With touch only and human-only training, accuracy is about **60%**. Adding the accelerometer raises it to **80–90%**. Training on both bot generators gives **>90%** against very realistic synthetic attacks.
  - GAN trajectories were "almost impossible" to separate using touch alone.
  - Backs: §5.1 (graded synthetic attackers, the hardest tactic is hard) and the swipe features in §5.0.
  - Local: `papers/bot-detection/Acien2021_becaptcha-touch.pdf` — [arXiv](https://arxiv.org/abs/2005.13655)
- **Acien, A., Morales, A., Fierrez, J., Vera-Rodriguez, R. (2022). "BeCAPTCHA-Mouse: Synthetic Mouse Trajectories and Improved Bot Detection." Pattern Recognition 127:108643. arXiv:2005.00890.**
  - Neuromotor (sigma-lognormal) features; two synthesis methods: heuristic functions and GAN.
  - Benchmark: 15,000 trajectories, 58 real users.
  - **93% average accuracy from a single trajectory** against high-realism bots. Fusing with standard mouse-dynamics features gives a >36% relative gain.
  - Backs: the "độ thẳng / độ cong / vận tốc" (straightness / curvature / velocity) naturalness features, and the claim that one gesture is enough.
  - Local: `papers/bot-detection/Acien2022_becaptcha-mouse.pdf` — [arXiv](https://arxiv.org/abs/2005.00890)
- **DeAlcala, D., Morales, A., Tolosana, R., Acien, A., Fierrez, J., et al. (2023). "BeCAPTCHA-Type: Biometric Keystroke Data Generation for Improved Bot Detection." CVPR Workshops 2023. arXiv:2207.13394.**
  - Synthesizes keystroke timing three ways: a Universal statistical model, a User-dependent statistical model, and a data-driven model. Data: 136M keystrokes from 168k subjects.
  - Detectors tested: SVM, **Random Forest**, Naive Bayes, LSTM.
  - Synthetic keystrokes are detected with high accuracy when labeled data is large, but few-shot settings are "an important challenge".
  - Backs: the PIN-timing bot detector, tactic 4 ("lấy mẫu từ phân bố người thật", sampling from the real-human distribution, = the Universal/statistical synthesis), and the use of RF.
  - Local: `papers/bot-detection/DeAlcala2023_becaptcha-type.pdf` — [arXiv](https://arxiv.org/abs/2207.13394)
  - Workshop venue is from memory; confirm it on arXiv.
- **Iliou, C., Kostoulas, T., Tsikrika, T., Katos, V., Vrochidis, S., Kompatsiaris, I. (2021). "Detection of Advanced Web Bots by Combining Web Logs with Mouse Behavioural Biometrics." Digital Threats: Research and Practice 2(3). DOI 10.1145/3447815.**
  - "Advanced" bots that mimic human browsing are harder to detect than moderate ones. The mouse-movement module beats the web-log module, reaching **100% accuracy from the first requests** on dataset D1.
  - The scripted bots move in fixed steps (e.g. 8 px increments), the "quá đều" (too even) signature.
  - Backs: §2 signal claim and §5.1 graded difficulty.
  - Local: `papers/bot-detection/Iliou2021_advanced-web-bots-mouse.pdf` — [Bournemouth eprint](https://eprints.bournemouth.ac.uk/36055/1/3447815.pdf)
- **Wang, M., Guo, H., Li, H., Fu, Y., Xu, J., Xu, C. (2026). "ActReal: System-Level Mobile Agents Challenge Mobile Automation Detection." arXiv:2608.30038 (preprint, not peer-reviewed).**
  - Existing mobile defenses detect automation via touch trajectory, action timing and touch–IMU coupling.
  - A privileged system-level agent that forges both touch and 6-axis IMU signals (from adapted genuine trajectories plus physics-guided IMU) evades them: **77.5% mean event-level attack success**, and **71.1% even with joint touch+IMU detectors**.
  - Backs: the honest "chiến thuật 4/phát lại khó" (tactic 4 / replay is hard) limitation and the case for adding IMU features in the future.
  - Local: `papers/bot-detection/Wang2026_actreal-mobile-agents.pdf` — [arXiv](https://arxiv.org/abs/2608.30038)

### Inferences
- BeCAPTCHA's ~60% (touch only, realistic GAN bots) versus near-100% against simple bots is the literature's version of the plan's "tactic 1 easy → tactic 4 hard" curve. Use it to frame the expected per-tactic results.
- Accelerometer/IMU fusion is the most-cited way to recover accuracy. An accessibility-malware tap on an idle phone produces no hand-motion IMU signal. That is an inference, because ActReal shows only that a *system-level* agent can forge IMU, which ordinary accessibility malware cannot do.

### Gaps
- No paper found that evaluates bot detection on PIN-pad taps specifically (tap-to-center offset as a feature). The "chạm đúng tâm nút" (tap exactly on button center) signal is supported only indirectly.
- Classic game-bot work (Gianvecchio et al., "Battle of Botcraft", CCS 2009) and blog-bot work (Chu et al., 2013) were not retrieved.

## Q3. Adversarial / synthetic human-like input (the 4 attacker tactics in §5.1)

### Takeaway
There is strong precedent that attackers can beat behavioral biometrics in three ways: (a) a robot driven by population statistics, matching tactic 4; (b) GAN or replay-based trajectory synthesis, matching tactics 3–4; (c) trained imitation. The plan should therefore keep admitting that tactic 4 is hard, and frame the per-tactic report as standard practice in this literature.

### Cited Findings
- **Serwadda, A., Phoha, V. V. (2013). "When kids' toys breach mobile phone security." ACM CCS 2013, pp. 599–610. DOI 10.1145/2508859.2516659.**
  - A Lego robot driven by **general-population swipe statistics** achieves "alarmingly high" penetration of touch-based authentication.
  - Calls zero-effort impostor testing into question.
  - Journal extension: Serwadda, Phoha, Wang, Kumar, Shukla, "Toward Robotic Robbery on the Touch Screen," ACM TISSEC 18(4), 2016, DOI 10.1145/2898353.
  - Backs: **tactic 4** (sampling from the human distribution) and the need to test against non-zero-effort attackers.
  - Local: **paywalled** (ACM; not downloaded) — [Semantic Scholar](https://www.semanticscholar.org/paper/When-kids'-toys-breach-mobile-phone-security-Serwadda-Phoha/5c3556d4bf94ba51cea58c5d624aed19e6223e59)
- **Khan, H., Hengartner, U., Vogel, D. (2018). "Augmented Reality-based Mimicry Attacks on Behaviour-Based Smartphone Authentication." MobiSys 2018. DOI 10.1145/3210240.3210317.**
  - 31 participants, >400 attacks.
  - Keystroke dynamics bypassed in **87%** of attacks after about **4 min** of mimicry training.
  - The same technique also beat a swipe-based continuous authentication system.
  - Related: Khan et al., MobiSys 2016 (DOI 10.1145/2906388.2906404), where shoulder-surfing mimicry bypassed touch implicit authentication at 84%.
  - Backs: Scenario B ("Kịch bản B"), and the replay/mimicry framing behind tactic 3.
  - Local: `papers/bot-detection/Khan2018_ar-mimicry-attacks.pdf` — [PDF](https://cs.uwaterloo.ca/~uhengart/publications/mobisys18.pdf)
- **Tey, C. M., Gupta, P., Gao, D. (2013). "I Can Be You: Questioning the Use of Keystroke Dynamics as Biometrics." NDSS 2013.**
  - 84 attacker participants.
  - False accept rate rose from 0.24 to **0.63** (easy password) and from 0.20 to **0.42** (hard password) after training with the Mimesis tool, given partial knowledge of the victim's timing.
  - Backs: tactic 4 for PIN timing.
  - Local: **not downloaded**. CORE and SMU links returned HTML instead of a PDF (OA landing page: [SMU INK](https://ink.library.smu.edu.sg/sis_research/1699/)).
- **Iliou, C., Kostoulas, T., Tsikrika, T., Katos, V., Vrochidis, S., Kompatsiaris, I. (2021). "Web Bot Detection Evasion Using Generative Adversarial Networks." IEEE CSR 2021, pp. 115–120.**
  - GAN-generated mouse and **touchscreen** trajectories let bots evade behavior-based detection, "even if the web server is aware of the attack method".
  - Backs: tactics 3–4 and the "thừa nhận chiến thuật 4 khó" (admit tactic 4 is hard) statement.
  - Local: `papers/bot-detection/Iliou2021_gan-web-bot-evasion.pdf` — [eprint](https://eprints.bournemouth.ac.uk/36301/1/Web_bot_detection_evasion_using_Generative_Adversarial_Networks_R1_v1.pdf)
- Also in this group: BeCAPTCHA (handcrafted + GAN bots), BeCAPTCHA-Type (Universal-distribution sampling) and ActReal (replay of adapted genuine trajectories), all covered in Q2.

### Inferences
- How the plan's 4 tactics map to the literature:
  - Tactic 1 (constant timing, exact center) corresponds to the "moderate" bots in Iliou 2021 and the simple handcrafted bots in BeCAPTCHA.
  - Tactic 2 (random noise) corresponds to the handcrafted bots with noise in BeCAPTCHA and BeCAPTCHA-Mouse.
  - Tactic 3 (replay of real sessions + noise) corresponds to ActReal's adapted genuine trajectories.
  - Tactic 4 (sampling from the human distribution) corresponds to Serwadda & Phoha 2013, the Universal model in BeCAPTCHA-Type, and the GAN bots.

### Gaps
- Stefan, Shu, Yao, "Robustness of keystroke-dynamics based biometrics against synthetic forgeries" (Computers & Security 2012) was not retrieved.

## Q4. Tree models (LightGBM / Random Forest) for this classification

### Takeaway
RF is a standard baseline in the bot-detection papers above (BeCAPTCHA-Type uses it explicitly). The two canonical method papers are open access.

### Cited Findings
- **Ke, G., Meng, Q., Finley, T., Wang, T., Chen, W., Ma, W., Ye, Q., Liu, T.-Y. (2017). "LightGBM: A Highly Efficient Gradient Boosting Decision Tree." NeurIPS 30.** Introduces GOSS and EFB for fast GBDT training on tabular features. Local: `papers/bot-detection/Ke2017_lightgbm.pdf` — [NeurIPS](https://papers.nips.cc/paper_files/paper/2017/file/6449f44a102fde848669bdd9eb6b76fa-Paper.pdf)
- **Breiman, L. (2001). "Random Forests." Machine Learning 45(1): 5–32. DOI 10.1023/A:1010933404324.** Local: `papers/bot-detection/Breiman2001_random-forests.pdf` (author copy) — [Berkeley](https://www.stat.berkeley.edu/~breiman/randomforest2001.pdf)
- RF used as a keystroke bot detector — DeAlcala et al. 2023 (above).

### Inferences
- With about 40 hand-built session features and small data, GBDT/RF is a defensible choice. BeCAPTCHA-Mouse's gain from fusing handcrafted features supports the "đặc trưng độ tự nhiên" (naturalness features) approach.

### Gaps
- No paper found comparing LightGBM specifically to deep models for touch-based bot detection.
