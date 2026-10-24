"""Ghi lại điểm kiểm định chéo của RANKAVG_RF (g0_pair.rankavg_rf) để đếm số lần w = 0 được chọn do HOÀ.
Chạy từ thư mục gốc của kho Git: python chan_doan/w_ties2.py --pair AB --data A=... B=... --targets A --only RANKAVG_RF --out <thư mục tạm>
"""
import sys, json
import numpy as np
sys.path.insert(0, ".")
import g0_pair as G
from sklearn.model_selection import StratifiedKFold
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import average_precision_score
LOG = []

def rankavg_rf_logged(Ftr, ytr, Fte, scores, tr, te, seed):
    n_pos, n_neg = int(ytr.sum()), int(len(ytr) - ytr.sum())
    cv = min(3 if len(ytr) > 1000 else 5, n_pos, n_neg)
    grid = G.CFG["RANKAVG"]["grid"]
    rf = lambda: RandomForestClassifier(**G.CFG["RF"], n_jobs=-1, random_state=seed)
    out = {}
    if cv >= 2:
        oof = np.zeros(len(ytr)); fold_id = np.zeros(len(ytr), int)
        for f, (a_, b_) in enumerate(StratifiedKFold(cv, shuffle=True, random_state=seed).split(Ftr, ytr)):
            oof[b_] = rf().fit(Ftr[a_], ytr[a_]).predict_proba(Ftr[b_])[:, 1]; fold_id[b_] = f
    final = rf().fit(Ftr, ytr).predict_proba(Fte)[:, 1]
    for sfx, sc in scores.items():
        s_tr, s_te = sc[tr], sc[te]
        if cv >= 2:
            score = []
            for w in grid:
                aps = [average_precision_score(ytr[fold_id == f], w * G._rank(s_tr[fold_id == f]) + (1 - w) * G._rank(oof[fold_id == f]))
                       for f in range(cv) if 0 < ytr[fold_id == f].sum() < (fold_id == f).sum()]
                score.append(np.mean(aps) if aps else -1)
            w = grid[int(np.argmax(score))]
            best = max(score); tied = [g for g, v in zip(grid, score) if v == best]
            w_mid = min(tied, key=lambda g: (abs(g - 0.5), g))          # hoà -> w gần 0,5 nhất
            pv = lambda ww: ww * G._rank(s_te) + (1 - ww) * G._rank(final)
            LOG.append(dict(k=len(ytr), sfx=sfx, seed=seed, score=[float(v) for v in score], w=w, w_mid=w_mid,
                            ap_spec=float(average_precision_score(G_Y[te], pv(w))), ap_mid=float(average_precision_score(G_Y[te], pv(w_mid))),
                            ap_rf=float(average_precision_score(G_Y[te], final)), ap_half=float(average_precision_score(G_Y[te], pv(0.5)))))
        else:
            w = 0.5
        out[sfx] = (w * G._rank(s_te) + (1 - w) * G._rank(final), w)
    return out

from pairs import LOADERS, parse_data_args
_args = dict(a.split("=", 1) for a in sys.argv[sys.argv.index("--data") + 1:] if "=" in a and not a.startswith("--"))
G_Y = LOADERS["A"](_args["A"])[1]
G.rankavg_rf = rankavg_rf_logged
G.main()
json.dump(LOG, open("w_ties_log2.json", "w"))
