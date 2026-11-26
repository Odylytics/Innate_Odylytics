# Chỉ mục thí nghiệm (E1–E27)

> Cập nhật 25/11/2026. Diễn giải, giả thuyết và giới hạn của từng thí nghiệm: [`../docs/research/ai-research.md`](../docs/research/ai-research.md) (mục 6b). Mã trong `experiments/`, bảng kết quả trong `results/`. Dữ liệu: [`../docs/research/datasets.md`](../docs/research/datasets.md). Giấy phép dữ liệu: [`../THIRD_PARTY_NOTICES.md`](../THIRD_PARTY_NOTICES.md).
> Cột "Dữ liệu": **thật** = người thật công khai; **giả** = tự sinh (không đưa lên slide). Bot luôn là bộ sinh của đội (chưa có bot thật).

| E | Câu hỏi | Dữ liệu | Mã `experiments/` | Kết quả `results/` | Kết luận ngắn |
|---|---|---|---|---|---|
| E1/E2 | Co rút phương sai về dân số có giúp few-shot? | thật (CMU, bàn phím máy tính) | `e1_fewshot_owner.py` | `e1_dsl.md` | Giảm FAR@FRR5% 7–11 điểm, EER không đổi |
| E3 | Hiệu chỉnh ánh xạ điểm chủ `d → score` | thật (StrokePIN) | `e3_calibrate_owner.py` | `e3_calibrate_owner.md` | Ánh xạ cũ cho 84% kẻ biết PIN qua 0,5; Platt cân bằng lớp còn 27% (chủ 90%); FAR@FRR5% vẫn 50%. Nối thử vào backend (`NHIP_OWNER_MAP=platt`, `e24_platt_map.md`): chỉ đổi đường dự phòng và làm hỏng luồng người nhận mới; để tắt mặc định |
| E4 | LightGBM người/máy, bỏ-một-chiến-thuật | giả | `e4_human_bot_lgbm.py` | `e4_human_bot_lgbm.md` | Số đẹp là học tắt; bot lạ sập |
| E4b | Người/máy với người thật | thật (StrokePIN) | `e4b_human_bot_real.py` | `e4b_human_bot_real.md` | CT1/2 100%; CT3 9–26%, CT4 20–73% |
| E5 | Phát hiện phát lại, nhiễu thích nghi | giả | `e5_replay.py` | `e5_replay.md` | Bắt tới ±10–15% |
| E5b | Hiệu chỉnh phát lại trên người thật | thật (StrokePIN) | `e5b_replay_real.py` | `e5b_replay_real.md` | Ngưỡng 0,07; 29% ở ±15% |
| E7 | Đầu độc mẫu chuẩn | giả | `e7_poisoning.py` | `e7_poisoning.md` | Nên "freeze + flag" (chưa áp dụng) |
| E9 | Nhận chủ trên PIN điện thoại thật | thật (StrokePIN) | `strokepin_loader.py`, `e9_strokepin_owner.py` | `e9_strokepin_owner.md` | EER ~0,16; đổi tư thế mất tín hiệu |
| E10/E10b | Co rút về dân số dùng được khi triển khai | thật | `make_population_prior.py`, `e10_deployable_prior.py`, `e10b_backend_path.py` | `e10_*.md`, `e10b_*.md` | Vào `owner.py`, sinh `population_prior.json` |
| E11 | Người/máy trên ô văn bản tự do | thật (Aalto) | `aalto_note_extract.py`, `e11_text_field_bots.py` | `e11_text_field_bots.md` | Bot ngây thơ ~100% khi đã thấy; bot lạ 0% |
| E12/E12b | Mô hình chủ học được | thật (StrokePIN) | `e12_learned_owner.py`, `train_owner_model.py` | `e12_learned_owner.md`, `e12b_*.md` | FAR@FRR5% 0,573 → 0,375 |
| E13 | Nhiều phím hơn có tốt hơn? (Innate Challenge) | thật (Aalto) | `e13_length_effect.py` | `e13_length_effect.md` | FAR 81% → 49% từ 6 → 30 phím |
| E14 | Chủ khi gõ chuỗi số mới (số tài khoản) | thật (StrokePIN) | `e14_unseen_digits.py` | `e14_unseen_digits.md` | EER 0,33 (6 số mới); xem `docs/research/transfer-flow.md` |
| E18 | Số cách gõ Telex/VNI của một câu | lý thuyết | `e18_vi_variation.py` | `e18_vi_variation.txt` | 3–6,6 bit biến thể (trần) |
| E19 | Luật vuốt và nhận chủ bằng vuốt | thật (Touchalytics) | `e19_touchalytics.py` | `e19_touchalytics.txt` | Luật cũ chặn nhầm 13,4%; luật vận tốc đều 0/20.896; vuốt không nhận chủ (AUC ~0,5) |
| E20 | Bao nhiêu âm tiết có chỗ chọn dấu thanh | mô phỏng | `e20_vi_style_sim.py` | `e20_vi_style_sim.txt` | AUC 0,66 (1) → 0,89 (8); chọn câu ≥ 4 |
| E21/E21b | Chuẩn hoá theo cặp phím | thật (Aalto) | `aalto_note_chars.py`, `e21_digraph_norm.py`, `e21b_digraph_profile.py` | `e21_digraph_norm.md`, `e21b_*.md` | Gần như không đổi; hồ sơ cặp phím tệ hơn |
| E22 | Cách giảm FAR của câu thử thách | thật (Aalto) | `aalto_note_orient.py`, `e22_improve_far.py` | `e22_improve_far.md` | Mô hình học −7 điểm; tư thế lạc quan, bỏ |
| E23 | Chuyển động điện thoại cho nhận chủ | thật (StrokePIN) | `e23_imu_fusion.py` | `e23_imu_fusion.md` | EER 0,04 nhưng là nhiễu thiết bị; đổi tư thế mất |
| E24 | Quyết định toàn hệ thống (allow/step_up/hold) | thật + bot | `e24_end_to_end.py` | `e24_end_to_end.md` | Bot ngây thơ và phát lại ≤ ±10% 100% hold |
| E25 | Quét ngưỡng A, B | thật + bot | `e24_end_to_end.py` | `e24_end_to_end.md` | Không có điểm tối ưu cho cả hai phía |
| E26 | Độ trễ API local | giả | `e26_latency.py` | `e26_latency.md` | `/score` p50 3,7 ms, max 36 ms sau khi nạp sẵn mô hình (trước: lần đầu ~1 s) |
| E28 | PIN 4 số (demo) hay 6 số: quyết định của hệ thống | thật (StrokePIN cắt 4 chạm, xấp xỉ) | `e28_pin_length.py` | `e28_pin_length.md` | PIN 4 số: mô hình chủ học không chạy; kẻ biết PIN được allow 68% (6 số: 28%) |
| E27/E27b | Bot thích nghi; ngưỡng phát lại | thật + bot | `e24_end_to_end.py` | `e24_end_to_end.md` | Phát lại ±15% trở lên và bot biết mẫu chuẩn qua mặt |

**Chưa chạy / chưa có số:** E3 trên dữ liệu đội (đã chạy trên StrokePIN), E6, E8 (kế hoạch trong `docs/research/research-plan.md`); gộp PIN + câu; kiểu gõ tiếng Việt trên người thật; bot thật; dữ liệu của đội. Đường ống cho dữ liệu đội: `team_analysis.py` (T1–T5), `team_data_dryrun.py` (thử ống bằng dữ liệu giả), `train_human_model.py --export ... --out ...`.

## Chạy lại
- Môi trường: `numpy pandas scikit-learn lightgbm` (+ `fastapi httpx` cho `e26`, `team_data_dryrun`). Dữ liệu tải riêng vào `research/data/` (git-ignored).
- Dùng `python -I` cho script đọc dữ liệu tải ngoài (`aalto_note_*.py`).
- Số hiệu E15–E17 không dùng (đã đổi thành E19–E21 để khỏi trùng E14).
