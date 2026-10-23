"""
splits_k2.py — File chia cho K2: cùng 30 lần chia train/test với Cổng 0, thêm M lần rút k mẫu trong mỗi lần chia
(review 18/10, mục 6.6 và Phụ lục B2; review 22/10, N1).

    python splits_k2.py --ibm data/WA_Fn-UseC_-HR-Employee-Attrition.csv --out prereg/splits_A_R30_M5.json

Quy ước (chốt trước khi chạy):
  - Lần chia r (0–29): train/test 80/20 phân tầng, random_state = r  → trùng Cổng 0.
  - Lần rút m (0–4) trong lần chia r: RandomState(10000 + r) nếu m = 0 (trùng đúng k mẫu của Cổng 0),
    RandomState(10000 + 1000·m + r) nếu m ≥ 1. Mỗi lần rút: phân tầng, lồng nhau 10 ⊂ 20 ⊂ 50 ⊂ 100, ≥ 1 mẫu dương.
  - Phân tích: lấy trung bình chỉ số trên M lần rút trong mỗi lần chia rồi mới kiểm định (R = 30 hiệu bắt cặp).
"""
import argparse, hashlib, json, os
import numpy as np
from sklearn.model_selection import train_test_split

from splits import make_splits, test_splits


def make_splits_M(y, ks=(10, 20, 50, 100), R=30, M=5, test_size=0.2):
    y = np.asarray(y)
    out = []
    for r in range(R):
        tr, te = train_test_split(np.arange(len(y)), test_size=test_size, stratify=y, random_state=r)
        prev, draws = y[tr].mean(), []
        for m in range(M):
            rng = np.random.RandomState(10_000 + r if m == 0 else 10_000 + 1000 * m + r)
            pos, neg = rng.permutation(tr[y[tr] == 1]), rng.permutation(tr[y[tr] == 0])
            d = {}
            for k in ks:
                n_pos = max(1, int(round(k * prev)))
                d[str(k)] = sorted(np.r_[pos[:n_pos], neg[:k - n_pos]].tolist())
            draws.append(d)
        out.append({"rep": r, "train": sorted(tr.tolist()), "test": sorted(te.tolist()), "draws": draws})
    return out


def check(sp, y, R):
    for m in range(len(sp[0]["draws"])):                      # mỗi lần rút thoả điều kiện như file chia Cổng 0
        test_splits([{"train": s["train"], "test": s["test"], "k": s["draws"][m]} for s in sp], y)
    g0 = make_splits(y, ks=(10, 20, 50, 100, 200, 500), R=R)  # lần rút 0 trùng Cổng 0
    for a, b in zip(sp, g0):
        assert a["train"] == b["train"] and a["test"] == b["test"]
        assert all(a["draws"][0][k] == b["k"][k] for k in a["draws"][0])
    return True


if __name__ == "__main__":
    from pairs import load_ibm
    ap = argparse.ArgumentParser()
    ap.add_argument("--ibm", required=True)
    ap.add_argument("--out", default="prereg/splits_A_R30_M5.json")
    ap.add_argument("--R", type=int, default=30); ap.add_argument("--M", type=int, default=5)
    a = ap.parse_args()
    y = load_ibm(a.ibm)[1]
    sp = make_splits_M(y, R=a.R, M=a.M)
    check(sp, y, a.R)
    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
    s = json.dumps(sp)
    open(a.out, "w").write(s)
    print(f"Đã lưu {a.out}: R = {a.R}, M = {a.M}; lần rút 0 trùng Cổng 0; sha256 = {hashlib.sha256(s.encode()).hexdigest()}")
