"""
pairs_synthesis.py — Tổng hợp nhiều cặp miền (RQ4, R3; O3: Friedman – Nemenyi và biểu đồ critical difference).

    python pairs_synthesis.py --out results/tong_hop_cap

Đọc:
  KB1 2×2 : results/kb1_v2 (AB, CPU), results/kb1_AB (AB, TabPFN nếu có), results/kb1_AC, results/kb1_AD
  Cổng 0  : results/g0_23 (AB), results/g0_AC, results/g0_AD  (+ results/g0_AC_consistent: phân tích phụ)
"""
import argparse, glob, os
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from pairs import PAIRS, SHORT

RATIO = 0.25
TO = ["LR", "RF", "XGB", "CAT", "STACK", "TabPFN"]
TR = ["ZS", "STK_LR", "STK_XGB", "OFF_XGB", "DAUME_LR", "RANKAVG", "ANCHOR_LR", "RANKAVG_RF"]
NAME = {"LR": "LR", "RF": "RF", "XGB": "XGBoost", "CAT": "CatBoost", "STACK": "Stacking", "TabPFN": "TabPFN v2",
        "ZS": "Zero-shot", "STK_LR": "Stacking+LR (nguồn)", "STK_XGB": "Stacking+XGB (nguồn)", "OFF_XGB": "XGB khởi tạo nguồn",
        "DAUME_LR": "Daumé+LR", "RANKAVG": "Trung bình hạng (LR)", "ANCHOR_LR": "LR neo nguồn", "RANKAVG_RF": "Trung bình hạng (RF)"}
KB1 = {"AB": ["results/kb1_v2/results_kb1v2_99d14779.csv", "results/kb1_AB/results_kb1_AB_*.csv"],
       "AC": ["results/kb1_AC/results_kb1_AC_*.csv"], "AD": ["results/kb1_AD/results_kb1_AD_*.csv"]}
G0 = {"AB": "results/g0_23", "AC": "results/g0_AC", "AD": "results/g0_AD"}


def corrected(d):
    d = np.asarray(d, float); J = len(d); se = np.sqrt((1 / J + RATIO) * np.var(d, ddof=1)); h = stats.t.ppf(.975, J - 1) * se
    return d.mean(), d.mean() - h, d.mean() + h


def load_kb1(pair):
    fs = [f for p in KB1[pair] for f in glob.glob(p)]
    if not fs:
        return None
    r = pd.concat([pd.read_csv(f) for f in fs], ignore_index=True)
    r["model"] = r["model"].replace({"rule_neg_experience": "rule"})
    return r.drop_duplicates(subset=["target", "setting", "features", "encoding", "model", "rep"], keep="last")


def load_g0(folder):
    fs = sorted(glob.glob(f"{folder}/results_g0_*.csv"))
    if not fs:
        return None
    r = pd.concat([pd.read_csv(f, dtype={"k": str}) for f in fs], ignore_index=True)
    return r


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--out", default="results/tong_hop_cap"); a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    rows, blocks = [], []
    for pair in ["AB", "AC", "AD"]:
        P = PAIRS[pair]; d1, d2 = P["domains"]; ms = P["main"]
        k1, g0 = load_kb1(pair), load_g0(G0[pair])
        if k1 is None or g0 is None:
            continue
        for tgt, src in [(d1, d2), (d2, d1)]:
            sel = lambda st, ft, en, m: k1[(k1.target == tgt) & (k1.setting == st) & (k1.features == ft) & (k1.encoding == en) & (k1.model == m)].sort_values("rep")
            full = sel("in", "full", "-", "LR").auc_roc; ins = sel("in", ms, "std", "LR").auc_roc
            x_std = sel(f"{src}->{tgt}", ms, "std", "LR").auc_roc; x_c1 = sel(f"{src}->{tgt}", ms, "rank", "LR").auc_roc
            best_cross = max(x_std.mean(), x_c1.mean())
            g = g0[g0.target == tgt]
            if len(g) == 0 or g.rep.nunique() < 30:
                print(f"Bỏ qua {pair} đích {tgt}: Cổng 0 chưa đủ 30 lần chia"); continue
            curve = g.groupby(["method", "k"]).pr_auc.mean()
            # Δ của chuyển giao tốt nhất so với baseline đích mạnh nhất, k ≤ 50
            best_d, best_txt = -9, ""
            for k in ["10", "20", "50"]:
                to = {m: curve.get((m, k)) for m in TO if (m, k) in curve.index}
                bm = max(to, key=to.get)
                base = g[(g.method == bm) & (g.k == k)].set_index("rep").pr_auc
                for m in TR:
                    kk = "zero" if m == "ZS" else k
                    c = g[(g.method == m) & (g.k == kk)].set_index("rep").pr_auc
                    if len(c):
                        mean, lo, hi = corrected((c - base).dropna())
                        if mean > best_d:
                            best_d, best_txt = mean, f"{NAME[m]} @k={k}: {mean:+.3f} [{lo:+.3f}; {hi:+.3f}]"
                            best_go = (mean >= .02) and (lo > 0)
            zs = g[g.method == "ZS"]
            rows.append(dict(cap=pair, chieu=f"{src}→{tgt}", nhan=P["label_semantics"], so_KN=len(k1[(k1.features == ms)].pipe(lambda x: x)) and None,
                             in_full_LR=full.mean(), in_KN_LR=ins.mean(), cross_std_LR=x_std.mean(), cross_C1_LR=x_c1.mean(),
                             mat_dac_trung=full.mean() - ins.mean(), lech_mien=ins.mean() - best_cross,
                             ZS_auc=zs.auc_roc.mean(), ZS_pr=zs.pr_auc.mean(), ty_le_duong=g.pos_rate_test.mean(),
                             chuyen_giao_tot_nhat=best_txt, GO=best_go))
            # khối cho Friedman: (cặp, chiều, k)
            for k in ["10", "20", "50", "100", "200", "500", "full"]:
                vals = {}
                for m in TO + TR:
                    kk = "zero" if m == "ZS" else k
                    if (m, kk) in curve.index:
                        vals[m] = curve[(m, kk)]
                blocks.append(dict(cap=pair, target=tgt, k=k, **vals))
    S = pd.DataFrame(rows).drop(columns=["so_KN"])
    S.to_csv(f"{a.out}/tong_hop_theo_cap.csv", index=False)
    pd.set_option("display.width", 250); pd.set_option("display.max_columns", 30)
    print(S.round(3).to_string(index=False))

    B = pd.DataFrame(blocks)
    cols = [m for m in TO + TR if m in B.columns]

    def friedman(Bx, methods):
        M = Bx[methods].to_numpy()
        R = np.array([stats.rankdata(-row) for row in M])            # hạng 1 = PR-AUC cao nhất
        avg = R.mean(0); N, kk = R.shape
        chi2, p = stats.friedmanchisquare(*M.T)
        FF = (N - 1) * chi2 / (N * (kk - 1) - chi2)
        q = stats.studentized_range.ppf(0.95, kk, np.inf) / np.sqrt(2)
        CD = q * np.sqrt(kk * (kk + 1) / (6 * N))
        tab = pd.DataFrame({"phuong_phap": [NAME[m] for m in methods], "nhom": ["chỉ đích" if m in TO else "chuyển giao" for m in methods],
                            "hang_TB": avg}).sort_values("hang_TB")
        return tab, N, kk, chi2, p, FF, CD

    # Phân tích chính: đủ mọi phương pháp (kể cả TabPFN) — bỏ các khối thiếu một phương pháp
    # (TabPFN không chạy ở mức "full" khi tập huấn luyện > 10.000 dòng, tức đích B của cặp AB).
    full_blocks = B[cols].notna().all(axis=1)
    miss = B.loc[~full_blocks, ["cap", "target", "k"]].astype(str).agg("/".join, axis=1).tolist()
    rank_tab, N, kk, chi2, p, FF, CD = friedman(B[full_blocks], cols)
    rank_tab.to_csv(f"{a.out}/friedman_hang.csv", index=False)
    txt = (f"Friedman: N = {N} khối (cặp × chiều × k), k = {kk} phương pháp; chi2 = {chi2:.2f}, p = {p:.2e}; "
           f"Iman–Davenport F = {FF:.2f}; Nemenyi CD (α = 0,05) = {CD:.2f}. Khối bị bỏ vì thiếu phương pháp: {miss}")
    # Phân tích phụ: mọi khối, bỏ phương pháp thiếu ở một số khối
    m2 = [m for m in cols if B[m].notna().all()]
    t2, N2, k2, c2, p2, F2, CD2 = friedman(B, m2)
    t2.to_csv(f"{a.out}/friedman_hang_phu.csv", index=False)
    txt2 = (f"Phụ: N = {N2} khối, k = {k2} phương pháp (bỏ {[m for m in cols if m not in m2]}); chi2 = {c2:.2f}, p = {p2:.2e}; "
            f"F = {F2:.2f}; CD = {CD2:.2f}")
    open(f"{a.out}/friedman.txt", "w").write(txt + "\n" + txt2 + "\n" + rank_tab.round(3).to_string(index=False) + "\n\n" + t2.round(3).to_string(index=False))
    print("\n" + txt); print(rank_tab.round(2).to_string(index=False)); print(txt2); print(t2.round(2).to_string(index=False))

    # Biểu đồ hạng trung bình ± CD/2 (hai phương pháp khác nhau có ý nghĩa khi hai đoạn không chồng nhau)
    order = rank_tab.reset_index(drop=True)
    fig, ax = plt.subplots(figsize=(7.5, 0.32 * len(order) + 1.2), constrained_layout=True)
    yy = np.arange(len(order))[::-1]
    for y, (_, rr) in zip(yy, order.iterrows()):
        col = "#7f7f7f" if rr.nhom == "chỉ đích" else "#2a78d6"
        ax.errorbar(rr.hang_TB, y, xerr=CD / 2, fmt="o" if rr.nhom == "chỉ đích" else "D", color=col, capsize=3, ms=6)
    ax.set_yticks(yy); ax.set_yticklabels([f"{r.phuong_phap}" for r in order.itertuples()], fontsize=9)
    ax.invert_xaxis(); ax.set_xlabel(f"Hạng trung bình theo PR-AUC (1 = tốt nhất), đoạn = ± CD/2, CD = {CD:.2f}")
    ax.grid(axis="x", color="#e5e5e5"); ax.spines[["top", "right"]].set_visible(False)
    ax.set_title(f"Friedman – Nemenyi trên {N} khối (cặp × chiều × k)", loc="left", fontsize=10, fontweight="bold")
    from matplotlib.lines import Line2D
    ax.legend([Line2D([], [], marker="o", color="#7f7f7f", ls=""), Line2D([], [], marker="D", color="#2a78d6", ls="")],
              ["Chỉ dùng dữ liệu đích", "Chuyển giao"], loc="upper left", fontsize=8, frameon=False)
    fig.savefig(f"{a.out}/cd_diagram.png", dpi=200, bbox_inches="tight", facecolor="white")


if __name__ == "__main__":
    main()
