"""
splits.py — File chia dữ liệu dùng chung cho mọi phương pháp (Phụ lục B1 của đánh giá 07/10/2026).

Mỗi lần lặp r: train/test 80/20 phân tầng (random_state = r); k mẫu rút phân tầng từ phần train,
lồng nhau (10 ⊂ 20 ⊂ 50 ...), có ít nhất một mẫu dương, thay đổi theo r.

    python splits.py --domain A --data data/WA_Fn-UseC_-HR-Employee-Attrition.csv --out splits/ibm_splits.json
"""
import argparse
import json

import numpy as np
from sklearn.model_selection import train_test_split


def make_splits(y, ks=(10, 20, 50, 100, 200, 500), R=30, test_size=0.2):
    y = np.asarray(y)
    out = []
    for r in range(R):
        tr, te = train_test_split(np.arange(len(y)), test_size=test_size, stratify=y, random_state=r)
        rng = np.random.RandomState(10_000 + r)
        pos, neg = rng.permutation(tr[y[tr] == 1]), rng.permutation(tr[y[tr] == 0])
        prev, draws = y[tr].mean(), {}
        for k in ks:
            if k >= len(tr):
                continue
            n_pos = max(1, int(round(k * prev)))
            draws[str(k)] = sorted(np.r_[pos[:n_pos], neg[:k - n_pos]].tolist())
        out.append({"rep": r, "train": sorted(tr.tolist()), "test": sorted(te.tolist()), "k": draws})
    return out


def test_splits(splits, y):
    y = np.asarray(y)
    for s in splits:
        tr, te = set(s["train"]), set(s["test"])
        assert not tr & te, "train/test phải rời nhau"
        ks = sorted(s["k"], key=int)
        for k in ks:
            idx = s["k"][k]
            assert len(idx) == int(k) and set(idx) <= tr
            assert 0 < y[idx].sum() < len(idx), "k mẫu phải có cả hai lớp"
        for k1, k2 in zip(ks, ks[1:]):
            assert set(s["k"][k1]) <= set(s["k"][k2]), "k mẫu phải lồng nhau"
    return True


if __name__ == "__main__":
    from hr_data import load_ibm, load_jobchange
    ap = argparse.ArgumentParser()
    ap.add_argument("--domain", choices=["A", "B"], required=True)
    ap.add_argument("--data", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--R", type=int, default=30)
    a = ap.parse_args()
    _, y, info = (load_ibm if a.domain == "A" else load_jobchange)(a.data)
    sp = make_splits(y, R=a.R)
    test_splits(sp, y)
    json.dump({"domain": a.domain, "info": info, "splits": sp}, open(a.out, "w"))
    print(f"Đã lưu {a.out}: {len(sp)} lần lặp, {info}")
