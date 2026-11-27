# Datasets for experiments

> Links checked on 24/11/2026 (real HTTP requests from the work machine). **Licenses must be re-read on the original page before use in the submission**, and every dataset used must be listed in the submission README (source + license + citation).
> Downloaded data goes in `research/data/` (gitignored, not committed).

## Usable now, no permission needed

| Dataset | Content | Size | Direct download link | License |
|---|---|---|---|---|
| **StrokePIN** (Nankai, 2026) ⭐ | **6-digit PINs on a phone**: 97 people, 18,935 entries, 20 PINs shared by everyone, sitting/walking; touch X/Y coordinates, size, pressure, motion sensors | repo ~68 MB | `git clone https://github.com/Litraveler/StrokePIN.git` · page: https://ieee-dataport.org/documents/strokepin-0 (DOI 10.21227/thft-4721) | **CC BY-NC-SA 4.0** per the repo README and the page description (non-commercial, attribution, **derivatives shared under the same license**). The IEEE DataPort page lists the title as "Creative Commons Attribution", a slight contradiction: use the stricter terms |
| **CMU DSL-StrongPassword** | 51 people × 400 typings of one password, 31 timing features (computer) | 4.6 MB | https://www.cs.cmu.edu/~keystroke/DSL-StrongPasswordData.csv | Checked 25/11: the page states no license; asks for a citation of Killourhy & Maxion 2009 |
| **Touchalytics** (Frank 2013) | 41 people, swipe/scroll: coordinates, pressure, contact area | **raw data 5.2 MB** · features 1.6 MB | http://www.mariofrank.net/touchalytics/data.zip · http://www.mariofrank.net/touchalytics/features.zip · [readme](http://www.mariofrank.net/touchalytics/readme_data.txt) | **Checked 25/11: neither the page nor the readme states a license**; cite the TIFS 2013 paper. Already used in E19 |
| **MOBIKEY** (Sapientia) | 54 people, 3 text passwords on a Nexus 7 tablet, with pressure and finger area | small | https://www.ms.sapientia.ro/~manyi/mobikey/data/rawdata.zip · page: https://www.ms.sapientia.ro/~manyi/mobikey.html | Not checked |

## Large, direct download links

| Dataset | Content | Size | Direct download link (checked: HTTP 200) |
|---|---|---|---|
| **Aalto typing37k, processed version** | 37,370 people typing on a phone (SQL format) | **0.84 GB** | https://userinterfaces.aalto.fi/typing37k/data/processed_typing_data.zip |
| **Aalto typing37k, raw + processed CSV** | Same as above, in CSV (easy to use with Python) | **5.63 GB** | https://userinterfaces.aalto.fi/typing37k/data/csv_raw_and_processed.zip |
| **Aalto typing37k, raw SQL** | Original data | **4.89 GB** (43.4 GB unzipped) | https://userinterfaces.aalto.fi/typing37k/data/raw_typing_data.zip |
| Aalto data-collection code | Web keystroke collection tool | small | https://userinterfaces.aalto.fi/typing37k/resources/source_code.zip |

Original page: https://userinterfaces.aalto.fi/typing37k/. **Checked 25/11:** the page and the paper say "openly available" but state no data license (only the collection software is MIT); cite MobileHCI 2019, and ask the authors if redistributing derived data. The work machine currently has ~70 GB free. **The 0.84 GB processed CSV version is a reasonable starting point** before taking the 5.6 GB version.

## Need a license agreement (email the authors)

| Dataset | Content | Process |
|---|---|---|
| **HuMIdb** | 600 people, 14 sensors, BeCAPTCHA bot benchmark (for the human/machine task) | https://github.com/BiDAlab/HuMIdb: sign the agreement, email `atvs@uam.es`, receive a download account |
| **MobileTouchDB** | 217 people, 94 phone models, digits/PINs drawn by hand | https://github.com/BiDAlab/MobileTouchDB: same process, same email |
| **TypeNet benchmark** | Keystroke embeddings | https://github.com/BiDAlab/TypeNet: same process |
| **BB-MAS** | 117 people, multiple devices | DOI https://doi.org/10.21227/rpaz-0h66 (IEEE DataPort, free account needed; curl gets 403) |

## No confirmed link found

HMOG, BehavePassDB, KVC, FETA: the addresses I tried were all 404 or unreachable, so they are not listed. Look on the original paper pages in `papers/`.

## Note on bot data

No public dataset contains **real touch-controlling malware** on a PIN. Bots have to be generated with real tools (`adb input`, a `dispatchGesture` app); see R1 in [`research-plan.md`](research-plan.md).
