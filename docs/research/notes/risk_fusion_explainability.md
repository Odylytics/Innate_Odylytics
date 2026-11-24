# Risk fusion, step-up and explanation: supporting papers for Innate (plan sections 5.0 notes, 5.3, 5.4)

PDF folder: `C:/TuanNghia/Project/Momo_Odylytics/papers/risk-fusion-explainability/`. Every file listed below was checked for a `%PDF` header and is under 40 MB.

## Q1. Risk-based / adaptive authentication (allow / step_up / hold from behaviour plus context)

### Takeaway
Risk-based authentication (RBA) is an established pattern. Implicit signals are scored and an extra factor is requested only when risk is high. That is the same design as Innate's 3-zone `allow / step_up / hold`. The literature supports choosing the threshold for low friction on genuine users, then reporting the attack catch rate at that false-positive rate. This is exactly the "FRR ≈ 5%, report FAR" choice in 5.3.

### Cited Findings
- **Freeman, D.M., Jain, S., Dürmuth, M., Biggio, B., Giacinto, G. (2016). "Who Are You? A Statistical Approach to Measuring User Authenticity." NDSS 2016. DOI 10.14722/ndss.2016.23240.**
  - Local PDF: `Freeman2016_who-are-you.pdf`
  - Backs: the risk score, the step-up decision, weighted combination of signals, and choosing thresholds by false-positive budget.
  - What it does: classifies logins by IP, geolocation, browser and time of day, and requires extra verification (for example a phone step) for suspicious attempts. Validated on real LinkedIn login data plus simulated attacks, it shows that "a majority of attacks can be prevented by imposing additional verification steps on only a small fraction of users."
  - Weighted fusion beats each single feature. AUC: IP 0.872, UA 0.789, IP+UA 0.913, **weighted IP+UA 0.955** (interpolation smoothing, Fig. 3).
  - Results reported as TPR at 10% FPR: 95% of a botnet attack and 77% of compromised accounts. Attack-specific AUC: password-only attacker 0.999, simulated botnet 0.992.
  - Source: [NDSS PDF](https://www.ndss-symposium.org/wp-content/uploads/2017/09/who-are-you-statistical-approach-measuring-user-authenticity.pdf)
- **Wiefling, S., Lo Iacono, L., Dürmuth, M. (2019). "Is This Really You? An Empirical Study on Risk-Based Authentication Applied in the Wild." IFIP SEC 2019, Springer, pp. 134–148. DOI 10.1007/978-3-030-22312-0_10. arXiv:2003.07622.**
  - Local PDF: `Wiefling2019_is-this-really-you.pdf`
  - Backs: step-up as industry practice. RBA is recommended by the NIST digital identity guidelines and used by large services.
  - Findings: studied 8 popular online services, analysing which features and combinations/classifiers they use. All tested services offered verification codes as the extra factor.
  - Source: [arXiv](https://arxiv.org/abs/2003.07622)
- **Wiefling, S., Dürmuth, M., Lo Iacono, L. (2020). "More Than Just Good Passwords? A Study on Usability and Security Perceptions of Risk-based Authentication." ACSAC 2020. arXiv:2010.00339.**
  - Local PDF: `Wiefling2020_more-than-just-good-passwords.pdf`
  - Backs: "less friction for the genuine owner". Step-up only when risky is perceived as more usable than always-on 2FA.
  - Findings: lab study, n=65. RBA was rated significantly more usable than the 2FA variants, more secure than password-only, and about as secure as 2FA.
  - Source: [arXiv](https://arxiv.org/abs/2010.00339)
- **Wiefling, S., Dürmuth, M., Lo Iacono, L. (2021). "What's in Score for Website Users: A Data-driven Long-term Study on Risk-based Authentication Characteristics." FC 2021, Springer. arXiv:2101.10681.**
  - Local PDF: `Wiefling2021_whats-in-score.pdf`
  - Backs: thresholds and weights must be tuned per service. This justifies tunable A/B thresholds rather than fixed constants.
  - Findings: N=780 users, 247 features, more than 1.8 years of data. "Even small configuration adjustments can greatly impact RBA's security and usability properties."
  - Source: [arXiv](https://arxiv.org/abs/2101.10681)
- **Wiefling, S., Jørgensen, P.R., Thunem, S., Lo Iacono, L. (2022). "Pump Up Password Security! Evaluating and Enhancing Risk-Based Authentication on a Real-World Large-Scale Online Service." ACM TOPS 26(1). DOI 10.1145/3546069. arXiv:2206.15139.**
  - Local PDF: `Wiefling2022_pump-up-password-security.pdf`
  - Backs: large-scale evidence for step-up, and ML-based tuning of RBA parameters. This is the "replace weights with a supervised model later" roadmap.
  - Findings: 3.3M users and 31.3M logins over more than one year, at Telenor Digital. Provides an ML-based RBA parameter optimisation method and a synthesized open data set. Users "profit from RBA after just a few logins", which is relevant to Innate's few-shot enrolment.
  - Source: [arXiv](https://arxiv.org/abs/2206.15139)

### Inferences
- Freeman 2016 is the closest academic analogue to Innate's formula 5.3: a per-user likelihood of the current context, combined with learned weights, then thresholded into step-up. Innate adds behavioural scores to the contextual ones.
- In all these papers the RBA features are login context (IP, user agent), not transaction context (new payee, unusual amount). Using payee and amount is supported by the fraud literature (Q3), not by the RBA papers.

### Gaps
- I found no paper that evaluates RBA with a 3-zone allow/step-up/hold scheme specifically. Most RBA studies use 2 zones (allow or challenge), and some add a block. The "hold" zone is a design extension.
- I did not find a Google risk-based authentication analysis distinct from Wiefling 2019, which includes Google among its 8 services.

## Q2. Score-level fusion (weighted sum, normalisation)

### Takeaway
A weighted sum of normalised scores is the textbook score-level fusion method. Z-score, min-max and tanh normalisation followed by the sum rule performed best in Jain et al. 2005. User-specific weights help.

### Cited Findings
- **Jain, A.K., Nandakumar, K., Ross, A. (2005). "Score normalization in multimodal biometric systems." Pattern Recognition 38(12), 2270–2285. DOI 10.1016/j.patcog.2005.01.012.**
  - Local PDF: none. The author-hosted PDF ([MSU link](http://biometrics.cse.msu.edu/Publications/Multibiometrics/JainNandakumarRoss_ScoreNormalization_PR05.pdf)) timed out from here (HTTP 000) and other mirrors returned 404. Treat as **paywalled** at Elsevier, and try the MSU link manually.
  - Backs: the normalised-distance score in 5.2 and the weighted sum in 5.3.
  - Findings:
    - Face, fingerprint and hand geometry were fused. Min-max, z-score and tanh normalisation followed by the sum rule gave the best performance.
    - Min-max and z-score are sensitive to outliers; tanh is efficient and robust.
    - User-specific weights beat global weights.
  - Source: [Semantic Scholar](https://www.semanticscholar.org/paper/Score-normalization-in-multimodal-biometric-systems-Jain-Nandakumar/0a00f3ca6efe78953b40c68ad13fbd1b01a1d4e6)
- **Singh, M., Singh, R., Ross, A. (2019). "A Comprehensive Overview of Biometric Fusion." Information Fusion 52, 187–205. arXiv:1902.02919.**
  - Local PDF: `Singh2019_overview-biometric-fusion.pdf`
  - Backs: fusion design overall, including "utilizing contextual information to improve biometric recognition accuracy" and continuous authentication with ancillary information. This is the bridge between biometric scores and contextual signals in 5.3.
  - Source: [arXiv](https://arxiv.org/abs/1902.02919)
- Freeman 2016 (Q1): the weighted combination of IP and UA scores gives AUC 0.955 versus 0.913 unweighted. This is direct evidence that weights matter. [NDSS PDF](https://www.ndss-symposium.org/wp-content/uploads/2017/09/who-are-you-statistical-approach-measuring-user-authenticity.pdf)

### Inferences
- In 5.3, normalise each term (for example z-score against the user's own history for "unusual amount") before weighting. Otherwise the term with the largest range dominates.
- Consider tanh normalisation, because enrolment with 3–5 sessions gives noisy statistics and z-score is outlier-sensitive.

### Gaps
- I did not verify the exact tables in Jain 2005, because the full PDF could not be downloaded. The findings above come from the abstract and slide summary.

## Q3. Transaction fraud with behavioural plus transactional features in mobile money / e-wallets

### Takeaway
There is open, citable work on mobile-money fraud, but it is mostly synthetic (PaySim). I found no peer-reviewed paper on Vietnamese e-wallet fraud.

### Cited Findings
- **Lopez-Rojas, E.A., Elmir, A., Axelsson, S. (2016). "PaySim: A financial mobile money simulator for fraud detection." 28th European Modeling and Simulation Symposium (EMSS 2016), Larnaca, pp. 249–255.**
  - Local PDF: `LopezRojas2016_paysim.pdf`
  - Backs: the claim "no real fraud data, so use synthetic or simulated data". Even academia lacks real mobile-money fraud data.
  - Findings: the authors note "the lack of legitimate datasets on mobile money transactions" as a major research problem. PaySim simulates transactions from a real African mobile-money service; the public data set has about 6.6M records.
  - Source: [PDF](https://www.msc-les.org/proceedings/emss/2016/EMSS2016_249.pdf)
- **Vijayanand, D., Smrithy, G.S. (2025). "Explainable AI-enhanced ensemble learning for financial fraud detection in mobile money transactions." SAGE journal. DOI 10.1177/18724981241289751.**
  - Local PDF: **paywalled**.
  - Combines ensembles with XAI for mobile-money fraud.
  - Source: [SAGE](https://journals.sagepub.com/doi/10.1177/18724981241289751)
- **Zambia mobile-money study (Research Square preprint, 2025/26).**
  - Local PDF: not downloaded. It is a preprint, not peer-reviewed, and its snippets contradict each other on the top feature.
  - Findings: 10,000 real operator transactions, XGBoost, SHAP. SHAP ranks customer–agent interaction frequency and transaction velocity as dominant; another snippet lists amount_log as the strongest feature.
  - Source: [Research Square](https://www.researchsquare.com/article/rs-10789631/v1)

### Inferences
- The "new payee" and "unusual amount vs history" terms in 5.3 match recipient-history and amount features, which dominate PaySim-based models. This comes from a GitHub project, not a paper: [AKrutto26 repo](https://github.com/AKrutto26/transactional-level-mobile-money-fraud-detection-ml-ensemble). It is weak evidence.

### Gaps
- No Vietnam or Southeast Asia e-wallet fraud paper found. The searches returned only Vietnamese financial-statement fraud work ([ResearchGate](https://www.researchgate.net/publication/360912965)).
- No academic paper found that fuses touch biometrics with transaction features for payments.

## Q4. Explainability (SHAP, TreeSHAP) and the LightGBM model

### Takeaway
SHAP gives per-feature additive contributions that sum to the model output. TreeSHAP computes them exactly and quickly for tree models such as LightGBM. This supports "top 2–3 contributing features → Vietnamese template sentence". For the weighted-sum fusion, each term w_i·x_i already is its exact additive contribution, so no SHAP is needed there.

### Cited Findings
- **Lundberg, S.M., Lee, S.-I. (2017). "A Unified Approach to Interpreting Model Predictions." NeurIPS 2017. arXiv:1705.07874.**
  - Local PDF: `Lundberg2017_unified-approach-shap.pdf`
  - Defines SHAP values as the unique additive feature attribution satisfying local accuracy, missingness and consistency.
  - Source: [arXiv](https://arxiv.org/abs/1705.07874)
- **Lundberg, S.M., Erion, G., Chen, H., DeGrave, A., Prutkin, J.M., Nair, B., Katz, R., Himmelfarb, J., Bansal, N., Lee, S.-I. (2020). "From local explanations to global understanding with explainable AI for trees." Nature Machine Intelligence 2, 56–67. DOI 10.1038/s42256-019-0138-9. arXiv:1905.04610.**
  - Local PDF: `Lundberg2020_local-to-global-treeshap.pdf` (19 MB)
  - Findings: a "polynomial time algorithm to compute optimal explanations" (TreeSHAP) for random forests and gradient-boosted trees, plus interaction values. This makes per-request explanation feasible within API latency.
  - Source: [arXiv](https://arxiv.org/abs/1905.04610)
- **Ke, G., Meng, Q., Finley, T., Wang, T., Chen, W., Ma, W., Ye, Q., Liu, T.-Y. (2017). "LightGBM: A Highly Efficient Gradient Boosting Decision Tree." NeurIPS 2017.**
  - Local PDF: `Ke2017_lightgbm.pdf`
  - Findings: GOSS plus EFB "speeds up the training process of conventional GBDT by up to over 20 times while achieving almost the same accuracy."
  - Source: [NeurIPS PDF](https://papers.nips.cc/paper_files/paper/2017/file/6449f44a102fde848669bdd9eb6b76fa-Paper.pdf)
- **Psychoula, I., Gutmann, A., Mainali, P., Lee, S.H., Dunphy, P., Petitcolas, F.A.P. (2021). "Explainable Machine Learning for Fraud Detection." IEEE Computer 54(10), 49–59. DOI 10.1109/MC.2021.3081249. arXiv:2105.06314.**
  - Local PDF: `Psychoula2021_explainable-ml-fraud.pdf`
  - Backs: explanations in real-time fraud detection.
  - Findings: compares LIME and SHAP for real-time fraud detection on supervised and unsupervised models. Choice of background data set and runtime are the key trade-offs, alongside model complexity and explanation reliability.
  - Source: [arXiv](https://arxiv.org/abs/2105.06314)

### Inferences
- SHAP depends on the background data set (Psychoula). Innate should fix and document the background set (for example the user's enrolment sessions) so explanations are stable.
- A recent preprint warns that applying SMOTE before the train/test split distorts SHAP backgrounds ([arXiv 2604.14231](https://arxiv.org/pdf/2604.14231)). This is relevant if the team oversamples bot sessions. It is a preprint and I did not read it in full.

### Gaps
- No paper found that tests user comprehension of Vietnamese-language fraud explanations.

## Q5. Technical caveats: touch pressure/size and Pointer Events

### Takeaway
The W3C Pointer Events spec itself mandates placeholder values when hardware lacks support: pressure 0.5 while a button is pressed, and width/height 1. That directly justifies "do not rely on `pressure`" and treating contact size with caution. Synthetic events can be built from script, which is why `isTrusted` and similar checks are not a robust bot test.

### Cited Findings
- **W3C (2024+). Pointer Events Level 3 (W3C spec).** Not a paper; HTML only, not downloaded.
  - For hardware without pressure support, pressure "MUST be 0.5 when in the active buttons state", otherwise 0.
  - When contact geometry is not detected, width/height "MUST return a default value of 1."
  - The `PointerEventInit` constructor lets script "construct untrusted (synthetic) pointer events."
  - Source: [W3C Pointer Events 3](https://www.w3.org/TR/pointerevents3/)
- **Frank, M., Biedert, R., Ma, E., Martinovic, I., Song, D. (2013). "Touchalytics: On the Applicability of Touchscreen Input as a Behavioral Biometric for Continuous Authentication." IEEE TIFS 8(1), 136–148. DOI 10.1109/TIFS.2012.2225048. arXiv:1207.6231.**
  - Local PDF: `Frank2013_touchalytics.pdf`
  - Backs: swipe/scroll features (5.0) and the claim that touch alone is not enough, so fusion is needed.
  - Findings:
    - Median EER of 0% intra-session, 2–3% inter-session, and below 4% one week after enrolment.
    - The authors say this "disqualif[ies] this method as a standalone" authentication mechanism, and propose it as one part of a multi-modal system.
  - Note: Touchalytics did use pressure and area from Android. It is not evidence that pressure is unreliable; use the W3C spec for that.
  - Source: [arXiv](https://arxiv.org/abs/1207.6231)
- Android `MotionEvent.getPressure()` returns an abstract 0–1 unit. Its fidelity, range and resolution are device-dependent.
  - Source: Zheng et al., "You are How You Touch" (ICNP 2014), [PDF](https://www.eecis.udel.edu/~hnw/paper/icnp14.pdf). Not downloaded.
  - This came from search snippets and was not read in full.

### Inferences
- The custom in-app PIN pad plus Pointer Events design is consistent with the spec: timestamps and coordinates are always real, while pressure and size may be placeholders. Add a runtime check: if pressure is always 0.5 (or width is always 1) across a session, drop that feature for the device.

### Gaps
- I found no peer-reviewed measurement study listing which Android models report constant pressure. A blog claims constant 0 or 1 force values on non-pressure screens ([send.win blog](https://blog.send.win/touch-event-fingerprinting-mobile-complete-guide-2026/)), which is low-quality evidence.

## Q6. Social-engineering / coached-victim ("active coercion") detection via behavioural signals

### Takeaway
I found no peer-reviewed academic paper that detects coached or coerced victims from touch or typing behaviour during a payment. The evidence is vendor material. Cite it as industry practice, not as validated science.

### Cited Findings
- **BioCatch (c. 2021–22). "Authorized Push Payment Fraud: How Digital Behavior Can Uncover Social Engineering Scams."**
  - Developed with customers. Lists "segmented typing", which indicates dictation such as a scammer reading out an account number, and frequent device-orientation changes as duress signals.
  - Source: [BioCatch blog](https://www.biocatch.com/blog/authorized-push-payment-fraud-how-digital-behavior-can-uncover-social-engineering-scams)
- **ThreatFabric. "A Multi-layered Approach to Detecting Impersonation Scams."**
  - Behavioural biometrics (keystrokes, navigation, touch, rotation) are "paramount to detecting coercion or hesitancy". The signals are strongest when correlated with an active call or a remote-access tool.
  - Transaction signals: size, velocity, payee relation age.
  - This directly mirrors 5.3's "new payee" term plus 5.0's session-rhythm features.
  - Source: [ThreatFabric](https://www.threatfabric.com/blogs/a-multi-layered-approach-to-detecting-impersonation-scams)
- Other vendor sources also describe long hesitation, pauses and fragmented typing as coaching signals that should trigger step-up:
  - [Sardine](https://www.sardine.ai/learn/behavioral-biometrics)
  - [SEON](https://seon.io/resources/behavioral-biometrics-against-fraud/)
- Academic scam work on arXiv analyses conversations, not in-app behaviour. One example is scam-baiting call scripts: [arXiv 2307.01965](https://arxiv.org/abs/2307.01965).

### Inferences
- The "bị dẫn dắt / bị điều khiển" (coached / remotely controlled) claim in 5.0 should be presented as a hypothesis motivated by industry practice. Ideally the team runs a small role-play experiment: one participant dictates, another types.

### Gaps
- No academic validation or public numbers for coercion detection were found. All of the evidence above is vendor marketing or blogs.
