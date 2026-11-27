# E22 — ways to reduce FAR at 30 keys (Aalto, real people; test sentence differs from enrollment sentence)

| Configuration | EER | FAR @ FRR 5% |
|---|---|---|
| raw (6, as in E13), K=1 enrollment sentences | 0.288 [0.279, 0.296] | 0.625 [0.603, 0.652] |
| raw (6, as in E13), K=3 enrollment sentences | 0.253 [0.245, 0.260] | 0.517 [0.498, 0.541] |
| raw (6, as in E13), K=5 enrollment sentences | 0.246 [0.237, 0.253] | 0.471 [0.440, 0.491] |
| raw (6, as in E13), K=8 enrollment sentences | 0.235 [0.227, 0.244] | 0.457 [0.435, 0.486] |
| raw + digraph-normalized (12), K=3 enrollment sentences | 0.248 [0.240, 0.255] | 0.502 [0.485, 0.524] |
| 12 + phone-holding angle (16), K=3 enrollment sentences | 0.144 [0.137, 0.151] | 0.277 [0.258, 0.315] |
| raw + digraph-normalized (12), K=3, learned model (LightGBM) | 0.227 [0.220, 0.233] | 0.429 [0.409, 0.446] |
