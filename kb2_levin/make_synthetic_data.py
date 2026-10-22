"""
make_synthetic_data.py
Sinh file CSV GIẢ LẬP có cùng cấu trúc MetaMIMIC (subject_id, 171 cột số, gender, 12 cột *_diagnosed,
có giá trị thiếu) để kiểm tra pipeline chạy được khi chưa có quyền truy cập MIMIC-IV.
KHÔNG dùng để báo cáo kết quả.

  python make_synthetic_data.py --n 3000 --out data/synthetic_metamimic.csv
"""
import argparse
import os

import numpy as np
import pandas as pd

from config import MIMIC_TARGETS


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=3000)
    ap.add_argument("--out", default="data/synthetic_metamimic.csv")
    a = ap.parse_args()
    rng = np.random.default_rng(0)
    n, d = a.n, 171
    Z = rng.normal(size=(n, 8))                                # yếu tố ẩn chung -> các nhãn có tương quan
    X = Z @ rng.normal(size=(8, d)) + rng.normal(scale=1.0, size=(n, d))
    X = np.exp(X / 4) * 50                                     # phân phối lệch giống xét nghiệm
    X[rng.random(X.shape) < 0.05] = np.nan
    df = pd.DataFrame(X, columns=[f"lab_{i}" for i in range(d)])
    df.insert(0, "subject_id", np.arange(n))
    df["gender"] = rng.integers(0, 2, n).astype(float)
    W = rng.normal(size=(8, 12))
    prev = np.array([.25, .6, .33, .19, .1, .36, .2, .15, .4, .1, .12, .08])
    logits = Z @ W + rng.normal(size=(n, 12))
    for j, c in enumerate(MIMIC_TARGETS):
        df[c] = (logits[:, j] > np.quantile(logits[:, j], 1 - prev[j])).astype(int)
    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
    df.to_csv(a.out, index=False)
    print(f"Saved {a.out}: {df.shape}")


if __name__ == "__main__":
    main()
