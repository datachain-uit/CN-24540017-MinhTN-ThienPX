"""Hình và bảng mô tả cho tiểu mục "Phần bổ sung Cổng 0" của mục 4 bản đủ.
Chỉ đọc kết quả đã commit (1b26af6), không chạy mô hình, không dùng nhãn mới.
    python docs/ban_du/ve_hinh_g0_bo_sung.py
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

KS = ["10", "20", "50", "100", "200", "500"]
TO = ["LR", "RF", "XGB", "CAT", "STACK", "TabPFN"]
MOI = ["LightGBM", "AdaBoost", "XGB_SMALLK", "PRESEL"]
CAP = {"A": "AB", "B": "AB", "C": "AC", "D": "AD"}
TEN = {"A": "IBM", "B": "Job Change", "C": "HR 14.999", "D": "Babushkin"}

s = pd.read_csv("results/g0_bo_sung/chi_so_tu_du_doan_tho.csv", dtype={"k": str})
fig, ax = plt.subplots(1, 4, figsize=(13, 3.2), sharex=True)
for a, t in zip(ax, "ABCD"):
    o = s[(s.pair == CAP[t]) & (s.target == t) & s.method.isin(TO)].groupby(["method", "k"]).pr_auc.mean().unstack("k")[KS]
    a.plot(KS, o.max(), "k-o", ms=3, label="Mạnh nhất (chọn sau)")
    m = pd.read_csv(f"results/g0_bo_sung/results_moi_{t}.csv", dtype={"k": str})
    for me in MOI:
        g = m[m.method == me].groupby("k").pr_auc.mean().reindex(KS)
        tt = m[m.method == me].groupby("k").auc_roc.apply(lambda x: (x == 0.5).all()).reindex(KS).fillna(False).astype(bool)
        l, = a.plot(KS, g.where(~tt), "-o", ms=3, label=me)
        a.plot(KS, g.where(tt), "x", ms=7, color=l.get_color())
    a.axhline(s[(s.pair == CAP[t]) & (s.target == t) & (s.method == "LR") & (s.k == "10")].pr_auc.size and pd.read_csv(f"results/g0_bo_sung/results_moi_{t}.csv").pos_rate_test.mean(), color="grey", ls=":", lw=1)
    a.set_title(f"Đích {t} ({TEN[t]})", fontsize=10); a.set_xlabel("k"); a.tick_params(labelsize=8)
ax[0].set_ylabel("PR-AUC"); ax[0].legend(fontsize=7)
fig.tight_layout()
fig.savefig("docs/ban_du/hinh_g0_bo_sung.png", dpi=160)
