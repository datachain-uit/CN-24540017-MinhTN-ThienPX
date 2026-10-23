"""
tbhtl_thamdo_eval.py — (THĂM DÒ 23/10, xem deviations.md mục 3) So sánh bản TB-HTL dạng mạng nơ-ron với baseline của Cổng 0 trên cùng 30 lần chia (không đổi kết luận Cổng 0).

    python tbhtl_thamdo_eval.py results/g0_23 A          # chiều B→A

So sánh bắt cặp theo lần chia, CI 95% hiệu chỉnh Nadeau–Bengio (tỷ lệ test/train 0,25), Holm trong mỗi họ so sánh:
  (1) mỗi biến thể TB-HTL − baseline CHỈ DÙNG ĐÍCH mạnh nhất tại cùng k (kể cả TabPFN v2) — cùng tiêu chí với GO
  (2) TB-HTL − baseline chuyển giao đơn giản tốt nhất tại cùng k
  (3) ablation: TB-HTL − TBHTL_NOANCHOR (H3d), TB-HTL − TBHTL_SHARED (H3b), TB-HTL − TBHTL_SCRATCH (lợi ích từ nguồn),
      TB-HTL − TBHTL_SHUF (đối chứng nhãn nguồn xáo trộn)
"""
import glob, sys
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from g0_decision import corrected, holm, TO, TR, NAME, COL, MK

KS = ["10", "20", "50", "100"]
TB = ["TBHTL", "TBHTL_NOANCHOR", "TBHTL_SHARED", "TBHTL_SCRATCH", "TBHTL_SHUF"]
TBN = {"TBHTL": "TB-HTL thăm dò (MLP)", "TBHTL_NOANCHOR": "TB-HTL không neo (λ = 0)", "TBHTL_SHARED": "TB-HTL chỉ nhánh chung",
       "TBHTL_SCRATCH": "TB-HTL không tiền huấn luyện", "TBHTL_SHUF": "TB-HTL, nhãn nguồn xáo trộn"}


def main(folder, tgt):
    files = sorted(glob.glob(f"{folder}/results_g0_*.csv"))
    r = pd.concat([pd.read_csv(f, dtype={"k": str}) for f in files], ignore_index=True)
    r = r[(r.target == tgt)]
    g = r[r.k.isin(KS + ["zero"])]
    curve = g.groupby(["method", "k"]).pr_auc.mean()
    get = lambda m, k: g[(g.method == m) & (g.k == ("zero" if m == "ZS" else k))].set_index("rep").pr_auc.sort_index()

    out = []
    for k in KS:
        to = {m: curve.get((m, k)) for m in TO if (m, k) in curve.index}
        bt = max(to, key=to.get)
        trs = {m: curve.get((m, "zero" if m == "ZS" else k)) for m in TR if (m, "zero" if m == "ZS" else k) in curve.index}
        btr = max(trs, key=trs.get)
        comps = [(m, bt, "so với đích mạnh nhất") for m in TB] + [("TBHTL", btr, "so với chuyển giao đơn giản tốt nhất")] + \
                [("TBHTL", m, "ablation") for m in TB[1:]]
        for a, b, fam in comps:
            x, y = get(a, k), get(b, k)
            if not len(x) or not len(y):
                continue
            d = (x - y).dropna()
            mean, lo, hi, p = corrected(d)
            out.append(dict(target=tgt, k=int(k), ho=fam, method=a, so_voi=b, pr_method=x.mean(), pr_so_voi=y.mean(),
                            delta=mean, ci_lo=lo, ci_hi=hi, p_corrected=p, n=len(d)))
    T = pd.DataFrame(out)
    T["p_holm"] = np.nan
    for fam, idx in T.groupby("ho").groups.items():
        T.loc[idx, "p_holm"] = holm(T.loc[idx, "p_corrected"].to_numpy())
    T["dat_tieu_chi_GO"] = (T.ho == "so với đích mạnh nhất") & (T.k <= 50) & (T.delta >= 0.02) & (T.ci_lo > 0)
    T.to_csv(f"{folder}/tbhtl_kiem_dinh_{tgt}.csv", index=False)

    # λ* theo k (kết quả về cơ chế, C4)
    lam = g[g.method == "TBHTL"].groupby("k").lam.agg(["median", "mean", lambda s: (s >= 10).mean()])
    lam.columns = ["lam_trung_vi", "lam_tb", "ty_le_lam_ge10"]
    lam = lam.reindex(KS)
    lam.to_csv(f"{folder}/tbhtl_lambda_{tgt}.csv")

    pd.set_option("display.width", 220)
    print("PR-AUC trung bình (30 lần chia):")
    show = TB + ["ZS", "LR", "RF", "CAT", "STACK", "TabPFN", "RANKAVG_RF", "DAUME_LR", "ANCHOR_LR"]
    print(curve.unstack().reindex(index=[m for m in show if m in curve.index.get_level_values(0)], columns=["zero"] + KS).round(3).to_string())
    print("\nKiểm định:")
    print(T[["k", "ho", "method", "so_voi", "pr_method", "pr_so_voi", "delta", "ci_lo", "ci_hi", "p_holm", "dat_tieu_chi_GO"]].round(3).to_string(index=False))
    print("\nλ* theo k:"); print(lam.round(3).to_string())

    # Hình: đường cong PR-AUC theo k
    fig, ax = plt.subplots(figsize=(7.2, 4.2), constrained_layout=True)
    xs = np.arange(len(KS))
    for m in ["LR", "RF", "CAT", "TabPFN"]:
        if m in curve.index.get_level_values(0):
            ax.plot(xs, [curve.get((m, k), np.nan) for k in KS], color=COL[m], marker=MK[m], lw=1.2, ls="--", alpha=.8, label=f"{NAME[m]} (chỉ đích)")
    if ("RANKAVG_RF", "10") in curve.index:
        ax.plot(xs, [curve.get(("RANKAVG_RF", k)) for k in KS], color=COL["RANKAVG_RF"], marker="h", lw=1.2, ls=":", label=NAME["RANKAVG_RF"])
    sty = {"TBHTL": ("#111111", "o", 2.4), "TBHTL_NOANCHOR": ("#8c8c8c", "s", 1.4), "TBHTL_SHARED": ("#c97b00", "^", 1.4),
           "TBHTL_SCRATCH": ("#5b8def", "D", 1.4), "TBHTL_SHUF": ("#d6336c", "x", 1.4)}
    for m, (c, mk, lw) in sty.items():
        if m in curve.index.get_level_values(0):
            ax.plot(xs, [curve.get((m, k), np.nan) for k in KS], color=c, marker=mk, lw=lw, label=TBN[m])
    if ("ZS", "zero") in curve.index:
        ax.axhline(curve[("ZS", "zero")], color=COL["ZS"], ls=":", lw=1, label="Zero-shot từ nguồn")
    ax.axhline(g.pos_rate_test.mean(), color="#999", lw=.8, label="Đoán ngẫu nhiên")
    ax.set_xticks(xs); ax.set_xticklabels(KS); ax.set_xlabel("Số mẫu có nhãn của miền đích (k)"); ax.set_ylabel("PR-AUC trung bình (30 lần chia)")
    ax.grid(axis="y", color="#e5e5e5"); ax.spines[["top", "right"]].set_visible(False)
    ax.set_title(f"TB-HTL thăm dò (MLP, 23/10) so với baseline Cổng 0 – đích {tgt}", loc="left", fontsize=10, fontweight="bold")
    ax.legend(fontsize=7, frameon=False, loc="upper left", ncol=2)
    fig.savefig(f"{folder}/tbhtl_hinh_{tgt}.png", dpi=200, bbox_inches="tight", facecolor="white")
    print(f"\nĐã lưu: tbhtl_kiem_dinh_{tgt}.csv, tbhtl_lambda_{tgt}.csv, tbhtl_hinh_{tgt}.png")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "results/g0_23", sys.argv[2] if len(sys.argv) > 2 else "A")
