"""Đánh giá ảnh hưởng của quy tắc hoà khi chọn w (RANKAVG_RF, chiều B→A, Cổng 0).
python w_ties2_eval.py <w_ties_log2.json>
"""
import sys, json
import numpy as np, pandas as pd
from scipy import stats

L = pd.DataFrame(json.load(open(sys.argv[1])))
L["rep"] = L.groupby("k").cumcount()
L["n_tied"] = L.score.apply(lambda s: sum(v == max(s) for v in s))


def corrected(d, ratio=0.25):
    d = np.asarray(d, float); J = len(d); se = np.sqrt(1 / J + ratio) * d.std(ddof=1)
    t = stats.t.ppf(.975, J - 1)
    p = 2 * stats.t.sf(abs(d.mean() / se), J - 1)
    return d.mean(), d.mean() - t * se, d.mean() + t * se, p


rows = []
for k, g in L[L.k.isin([10, 20, 50, 100])].groupby("k"):
    for name, col in [("hoà → w = 0 (mã hiện tại)", "ap_spec"), ("hoà → w gần 0,5", "ap_mid"), ("w = 0,5 cố định", "ap_half")]:
        m, lo, hi, p = corrected(g[col] - g["ap_rf"])
        rows.append(dict(k=k, quy_tac=name, pr_rankavg_rf=g[col].mean(), pr_rf=g.ap_rf.mean(), delta=m, ci_lo=lo, ci_hi=hi, p=p,
                         ty_le_w0=(g.w == 0).mean() if col == "ap_spec" else ((g.w_mid == 0).mean() if col == "ap_mid" else 0.0)))
D = pd.DataFrame(rows)
pd.set_option("display.width", 200)
print(D.round(3).to_string(index=False))
