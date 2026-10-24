"""Đo tần suất hoà khi chọn lam_s của TB-HTL v0 (k2_run.choose_lam_s) trên chính file chia K2.
Chạy từ thư mục gốc của kho Git: python chan_doan/lam_ties.py <số lần chia> <số lần rút>
Chỉ dùng k mẫu có nhãn của mỗi lần rút (giống k2_run), không đụng tập test.
"""
import sys, json
import numpy as np
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import average_precision_score, log_loss

sys.path.insert(0, ".")
import k2_run as K
from kb1_pair import Enc
from pairs import LOADERS, PAIRS, concepts
from sklearn.linear_model import LogisticRegression
from g0_pair import CFG as G0, onehot_pre
from hr_data import full_features
from k2_khai_niem import A_KEY, raw_col

R = int(sys.argv[1]); M = int(sys.argv[2])
GRID = (0.1, 1, 10, 100, 1e4)
paths = {"A": "data/WA_Fn-UseC_-HR-Employee-Attrition.csv", "B": "data/aug_train.csv", "C": "data/HR_comma_sep.csv"}
XA, yA, _ = LOADERS["A"](paths["A"])
SP = json.load(open("prereg/splits_A_R30_M5.json"))[:R]
out = []
FA, catA = full_features(XA)
KN = json.load(open("prereg/k2_khai_niem.json"))
for s, lv in [("B", "L0"), ("C", "L0"), ("B", "L1"), ("C", "L1")]:
    P = PAIRS[K.PAIR_OF[s]]; Xs, ys = LOADERS[s](paths[s])[:2]
    cset = P["main"] if lv == "L0" else K.L1_SET[s]
    Cs, Ct = concepts(K.PAIR_OF[s], s, Xs, cset), concepts(K.PAIR_OF[s], "A", XA, cset)
    cols = KN["nguon"][s][lv]["cot_IBM_dich_thay"]
    covered = sorted({raw_col(A_KEY[c]) for c in Cs.columns}); priv = [c for c in cols if c not in covered]
    enc = Enc("rank", P["binary"]); Zr = enc.fit_source(Cs)
    lr = LogisticRegression(**G0["LR"]).fit(Zr, ys)
    for r in range(R):
        sp = SP[r]; tr_all = np.array(sp["train"])
        et = Enc("rank", P["binary"]); et.fit_source(Ct.iloc[tr_all]); Zt = et.src.transform(Ct)
        sc = lr.decision_function(Zt)
        for m in range(M):
            for k in ["10", "20", "50", "100"]:
                tr = np.array(sp["draws"][m][k]); y = yA[tr]
                if priv:
                    Xp = onehot_pre(FA[priv], [c for c in catA if c in priv]).fit(FA[priv].iloc[tr]).transform(FA[priv].iloc[tr])
                else:
                    Xp = np.zeros((len(tr), 0))
                n_pos = int(y.sum()); n_fold = min(3, n_pos, len(y) - n_pos)
                cv = StratifiedKFold(n_fold, shuffle=True, random_state=r)
                ap, ll = {}, {}
                for lam in GRID:
                    a_, l_ = [], []
                    for a, b in cv.split(Zt[tr], y):
                        w = K.tbhtl_fit(Zt[tr][a], Xp[a], y[a], sc[tr][a], lam)
                        z = K.tbhtl_logit(w, Zt[tr][b], Xp[b], sc[tr][b])
                        a_.append(average_precision_score(y[b], z))
                        l_.append(log_loss(y[b], K.SIGMOID(z), labels=[0, 1]))
                    ap[lam], ll[lam] = np.mean(a_), np.mean(l_)
                best = max(ap.values())
                tied = [lam for lam in GRID if ap[lam] == best]
                out.append(dict(source=s, level=lv, rep=r, draw=m, k=int(k), n_pos=n_pos, n_fold=n_fold,
                                lam_spec=tied[0], n_tied=len(tied), all_tied=len(tied) == len(GRID),
                                lam_logloss=min(ll, key=ll.get)))
import pandas as pd
D = pd.DataFrame(out)
D.to_csv("lam_ties.csv", index=False)
g = D.groupby(["source", "level", "k"])
print(g.agg(n=("rep", "size"), n_pos=("n_pos", "first"), n_fold=("n_fold", "first"),
            ty_le_hoa=("n_tied", lambda v: (v > 1).mean()), ty_le_hoa_ca_5=("all_tied", "mean"),
            ty_le_lam01=("lam_spec", lambda v: (v == 0.1).mean())).round(2).to_string())
print("\nPhân bố lam_s theo đặc tả (hoà -> nhỏ nhất):")
print(D.groupby(["source", "level", "k"]).lam_spec.value_counts(normalize=True).unstack(fill_value=0).round(2).to_string())
print("\nPhân bố lam_s nếu chọn theo log-loss:")
print(D.groupby(["source", "level", "k"]).lam_logloss.value_counts(normalize=True).unstack(fill_value=0).round(2).to_string())
