"""Kiểm bản đang online TRƯỚC khi quay video và trước hạn nộp: /health phải báo cả hai mô hình học đã nạp.

Dùng: python backend/scripts/check_online.py https://nhip-api-taupe.vercel.app
Thoát mã 1 nếu API không trả lời, hoặc mô hình học không nạp (khi đó bản online đang chạy luật thuần).
"""
import json
import subprocess
import sys
import time

url = (sys.argv[1] if len(sys.argv) > 1 else "https://nhip-api-taupe.vercel.app").rstrip("/") + "/health"
try:  # dùng curl: kho chứng chỉ của Python cài từ python.org trên macOS hay thiếu, không nên tắt kiểm tra chứng chỉ
    t = time.perf_counter()
    body = json.loads(subprocess.run(["curl", "-sS", "-m", "20", url], check=True, capture_output=True, text=True).stdout)
    ms = (time.perf_counter() - t) * 1000
except Exception as e:  # noqa: BLE001
    sys.exit(f"KHÔNG GỌI ĐƯỢC {url}: {e}")
m = body.get("models") or {}
print(f"{url}: {body} ({ms:.0f} ms)")
if not (m.get("human") and m.get("owner")):
    sys.exit("MÔ HÌNH HỌC KHÔNG NẠP: bản online đang chạy luật thuần. Xem backend/app/scoring/lgbm_text.py và log deploy.")
print("OK: cả hai mô hình học đã nạp.")
