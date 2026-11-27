"""Check the online build BEFORE recording the video and before the submission deadline: /health must report that both learned models are loaded.

Usage: python backend/scripts/check_online.py https://nhip-api-taupe.vercel.app
Exits with code 1 if the API does not respond, or the learned models are not loaded (the online build is then running pure rules).
"""
import json
import subprocess
import sys
import time

url = (sys.argv[1] if len(sys.argv) > 1 else "https://nhip-api-taupe.vercel.app").rstrip("/") + "/health"
try:  # use curl: the certificate store of a python.org Python install on macOS is often missing, and certificate checking should not be disabled
    t = time.perf_counter()
    body = json.loads(subprocess.run(["curl", "-sS", "-m", "20", url], check=True, capture_output=True, text=True).stdout)
    ms = (time.perf_counter() - t) * 1000
except Exception as e:  # noqa: BLE001
    sys.exit(f"CANNOT REACH {url}: {e}")
m = body.get("models") or {}
print(f"{url}: {body} ({ms:.0f} ms)")
if not (m.get("human") and m.get("owner")):
    sys.exit("LEARNED MODELS NOT LOADED: the online build is running pure rules. See backend/app/scoring/lgbm_text.py and the deploy log.")
print("OK: both learned models are loaded.")
