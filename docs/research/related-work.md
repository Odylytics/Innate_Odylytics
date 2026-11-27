# Related work and lessons applied (updated 25/11/2026)

Supplements [`paper-report.md`](paper-report.md) (52 PDFs in `papers/`). This section records **what has been done in fields close to the Vietnamese Innate Challenge, what the team learned, and what it tried or applied**. Searches were run on 25/11/2026; search results are only summaries, **not read in full** unless stated otherwise.

## 1. Gap: no work found on Vietnamese typing rhythm (Telex/VNI) or Pinyin IME

Two searches ("keystroke dynamics Vietnamese Telex VNI", "keystroke dynamics Chinese Pinyin IME") **returned no paper** on biometrics from typing through an input method editor (IME). There are only general surveys ([Keystroke Dynamics: Concepts, Techniques, and Applications](https://arxiv.org/pdf/2303.04605), [A Review of Several Keystroke Dynamics Methods](https://arxiv.org/pdf/2502.16177)) and one language-independent free-text patent ([US 10970573](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/10970573)). **Safe wording:** "we did not find any published work on Telex/VNI typing style as a biometric signal"; do not say "nobody has done it". The team's direction (transform keys, tone mark position) is therefore a **new hypothesis with no precedent to compare against**, and has to be measured by the team itself (see `innate-challenge-vi.md`).

## 2. Owner recognition from free typing on phones

| Work | What it did | Lesson for Innate |
|---|---|---|
| Stragapede et al., [TypeFormer](https://arxiv.org/abs/2212.13075) (Neural Comput. Appl. 2024) | Transformer for free typing on Aalto, EER 3.25% with 5 enrollment sessions × 50 keys | This number needs a model trained on tens of thousands of people and 50 keys; **the team's E13: EER 0.245 at 30 keys, 3 enrollment sentences, only 6 features**. Large gap: both the number of keys and the model matter. The team does not have the data to train a deep network. |
| Acien et al., TypeNet (T-BIOM 2021) | Mobile EER 10.7% (G=1) down to 6.3% (G=10) by number of enrollment sessions | Confirms the direction "more enrollment sessions is better" (E9, E13). |
| Gunetti & Picardi, [Keystroke Analysis of Free Text](https://dblp.uni-trier.de/rec/journals/tissec/GunettiP05.html) (TISSEC 2005) | Compares two free-typing samples using the speed ranking of shared key pairs (R) and absolute speed (A) | The team tried two ideas from the same family in E21 and E21b (see section 5). |
| Killourhy & Maxion (DSN 2009) | Scaled Manhattan is the best detector of 14 | Already used in `owner.py`. |

## 3. Attacks on behavioral biometrics (limits of Innate)

| Work | Content | Effect on Innate |
|---|---|---|
| Serwadda & Phoha, [Examining a Large Keystroke Biometrics Dataset for Statistical-Attack Openings](https://api.crossref.org/works/10.1145%2F2516951.2516960) (TISSEC 2013) | A statistical attack using population data raised the error of 3 verifiers by 28.6–84.4%, stronger on short strings | Matches the team's tactic 4 (sampling from the population); confirms short strings (PIN) are weaker than long strings (sentences). |
| Serwadda & Phoha, "Robotic Robbery on the Touch Screen" (TISSEC 2016) | A Lego robot swiping from population statistics got past touch authentication | Same direction: the "rhythm" component is not an absolute barrier. |
| [Conditional GAN for keystroke-performance attacks](https://arxiv.org/pdf/2212.08445) | A GAN generates free-typing rhythm to fool an authenticator | A bot that learns from human data (tactic 4) is a real threat; an unseen, unfamiliar bot is a weak point of Innate (E4b, E11). |
| Wang et al., [ActReal](https://arxiv.org/pdf/2608.30038) (preprint 2026) | A system-level agent faking interaction, 77.5% success against 6 detectors (HMOG, TToS, BehaveFormer, AuthConFormer) | Already in `paper-report.md`; keep the limit "rhythm alone is not enough". |
| Bimodal user verification vs synthetic data, [SECRYPT 2025](https://www.scitepress.org/PublishedPapers/2025/134501) | GAN data threatens face more than the phone pick-up gesture | Suggests that combining several channels is harder to beat than one channel. |
| Schneier blog 2005 + [patent US 11222101](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/11222101) | Requires typing a new sentence/string each time to block replay | Same idea as the Innate Challenge; counterargument: an attacker can still replay the victim's **timing** onto the new sentence. **We did not find a serious evaluation** of this design; the team has not yet blocked timing replay on a new sentence (section 5, next work). |

## 4. What Innate does differently

1. **A "typing style" channel independent of rhythm** (tone mark position, error correction, whether an IME is used): replaying timing onto a new sentence **cannot** reproduce this channel unless the bot simulates the IME. This is the main reason to do Vietnamese (not yet measured).
2. **Simulated sessions under privacy constraints:** only time, event type, length, character class; the sentence content is known to the server (signed token).
3. **Honest reporting following FETA:** time-based split, one device, FAR@FRR 5%.

## 5. What was tried from this work (measured results)

- **E19 (Touchalytics, 41 people):** fixed the swipe rule (see `ai-research.md`).
- **E21 (Aalto, 1,000 people evaluated):** normalized rhythm by **key pair** (how TypeNet/TypeFormer learn content, and the R/A of Gunetti–Picardi). **The result barely changed**: at 30 keys EER 0.249 (raw) → 0.245 (normalized) → 0.238 (raw + normalized); FAR@FRR 5% 0.498 → 0.467. The confidence intervals overlap, so this is **a small improvement, not certain**.
- **E21b:** comparing the profile of each common key pair between the enrollment sentence and the trial sentence **made things worse** (EER 0.326 alone; combining it still did not do better), because two random sentences share on average only 6.5 common pairs at 30 keys.
- **Conclusion:** with a random sentence each time, **the jump does not come from content normalization**. Two directions remain: (a) features independent of the sentence, such as Vietnamese typing style (E20, simulation); (b) use a small fixed set of sentences so that enrollment and trial sentences overlap (not yet measured; trade-off: easier to replay).

## 6. Further reading (not done)

Read in full Gunetti & Picardi 2005 (the R formula), Serwadda & Phoha 2013, and TypeFormer (figures by string length) before quoting numbers in slides. Also look for: IME/Pinyin biometrics in Chinese, HuMIdb, typing rhythm on word-suggestion keyboards.
