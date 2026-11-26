"""Đọc mô hình LightGBM từ file văn bản (.txt) và dự đoán bằng Python thuần, KHÔNG cần lightgbm/numpy/libgomp.

Lý do: trên Vercel (Lambda) lightgbm không nạp được (thiếu libgomp), nên bản online rơi về luật (/health models false).
Hỗ trợ đúng những gì mô hình của repo dùng: nhị phân (sigmoid), chia số (không phân loại), thiếu giá trị theo decision_type.
Kiểm tương đương với lightgbm: tests/test_lgbm_text.py.
"""

import math
from pathlib import Path

_ZERO = 1e-35  # kZeroThreshold của LightGBM


class TextBooster:
    def __init__(self, text: str):
        self.trees: list[dict] = []
        for block in text.split("\nTree=")[1:]:
            f = {}
            for line in block.split("\n"):
                if line.startswith("end of trees"):
                    break
                k, _, v = line.partition("=")
                f[k] = v
            n = int(f["num_leaves"])
            if int(f.get("num_cat", 0)) or n < 2:
                if n < 2:  # cây một lá
                    self.trees.append({"leaf": float(f["leaf_value"].split()[0]), "n": 1})
                    continue
                raise ValueError("chỉ hỗ trợ chia số")
            self.trees.append({
                "n": n, "feat": [int(x) for x in f["split_feature"].split()], "thr": [float(x) for x in f["threshold"].split()],
                "dt": [int(x) for x in f["decision_type"].split()], "l": [int(x) for x in f["left_child"].split()],
                "r": [int(x) for x in f["right_child"].split()], "leaf": [float(x) for x in f["leaf_value"].split()]})
        if "objective=binary" not in text.split("\n\n")[0]:
            raise ValueError("chỉ hỗ trợ objective nhị phân")

    @classmethod
    def from_file(cls, path) -> "TextBooster":
        return cls(Path(path).read_text(encoding="utf-8"))

    def _tree(self, t: dict, x: list[float]) -> float:
        if t["n"] == 1:
            return t["leaf"]
        i = 0
        while True:
            v = x[t["feat"][i]]
            dt = t["dt"][i]
            miss = (dt >> 2) & 3  # 0 không, 1 số 0, 2 NaN
            if math.isnan(v) and miss != 2:
                v = 0.0
            if (miss == 1 and -_ZERO <= v <= _ZERO) or (miss == 2 and math.isnan(v)):
                nxt = t["l"][i] if dt & 2 else t["r"][i]
            else:
                nxt = t["l"][i] if v <= t["thr"][i] else t["r"][i]
            if nxt < 0:
                return t["leaf"][~nxt]
            i = nxt

    def predict(self, rows) -> list[float]:
        """Xác suất lớp 1, cùng giao diện `Booster.predict` của lightgbm cho một danh sách hàng."""
        out = []
        for x in rows:
            s = sum(self._tree(t, x) for t in self.trees)
            out.append(1 / (1 + math.exp(-s)) if s > -700 else 0.0)
        return out
