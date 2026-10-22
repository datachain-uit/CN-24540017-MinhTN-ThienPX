"""
kb1_pair_summary.py — Tổng hợp thí nghiệm 2×2 cho một cặp (bảng chính, kiểm định có hiệu chỉnh, độ nhạy, hình).

    python kb1_pair_summary.py --pair AD results/kb1_AD/results_kb1_AD_*.csv
    python kb1_pair_summary.py --pair AB results/kb1_v2/results_kb1v2_99d14779.csv results/kb1_AB/results_kb1_AB_*_TabPFN.csv --out results/kb1_AB/tong_hop

Gộp được kết quả CPU và TabPFN v2 (cùng lần chia). Kiểm định: corrected resampled t-test (Nadeau & Bengio, 2003),
tỷ lệ test/train 0,25; Holm trong mỗi (mã hoá × chỉ số).
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
ORDER = ["LR", "RF", "RF_leaf50", "XGB", "TabPFN"]
NAMES = {"LR": "Logistic Regression (L2)", "RF": "Random Forest (mặc định)", "RF_leaf50": "Random Forest (min_samples_leaf = 50)",
         "XGB": "XGBoost (300 cây, độ sâu 4)", "TabPFN": "TabPFN v2", "rule": "Quy tắc không cần học"}
TICK = {"LR": "LR", "RF": "RF", "RF_leaf50": "RF (leaf 50)", "XGB": "XGBoost", "TabPFN": "TabPFN v2"}


def corrected(d, ratio=RATIO):
    d = np.asarray(d, float); J = len(d); se = np.sqrt((1 / J + ratio) * np.var(d, ddof=1))
    t = d.mean() / se if se > 0 else np.inf; h = stats.t.ppf(0.975, J - 1) * se
    return d.mean(), d.mean() - h, d.mean() + h, 2 * stats.t.sf(abs(t), J - 1)


def holm(p):
    p = np.asarray(p); o = np.argsort(p); m = len(p); adj = np.empty(m); run = 0
    for i, k in enumerate(o):
        run = max(run, (m - i) * p[k]); adj[k] = min(1, run)
    return adj


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pair", required=True)
    ap.add_argument("files", nargs="+")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    P = PAIRS[a.pair]; d1, d2 = P["domains"]; main_set = P["main"]
    files = [f for pat in a.files for f in glob.glob(pat)]
    r = pd.concat([pd.read_csv(f) for f in files], ignore_index=True)
    r["model"] = r["model"].replace({"rule_neg_experience": "rule"})
    r = r.drop_duplicates(subset=["target", "setting", "features", "encoding", "model", "rep"], keep="last")
    models = [m for m in ORDER if m in set(r.model)]
    out = a.out or os.path.join(os.path.dirname(files[0]), f"tong_hop_kb1_{a.pair}")
    os.makedirs(os.path.dirname(out) if os.path.dirname(out) else ".", exist_ok=True)
    cell = lambda d: f"{d.auc_roc.mean():.3f} ± {d.auc_roc.std():.3f} ({d.pr_auc.mean():.3f})" if len(d) else "–"
    sel = lambda tgt, setting, feats, enc, m: r[(r.target == tgt) & (r.setting == setting) & (r.features == feats) &
                                               (r.encoding == enc) & (r.model == m)].sort_values("rep")

    rows = []
    for m in models + ["rule"]:
        row = {"Mô hình": NAMES[m]}
        for tgt, src in [(d1, d2), (d2, d1)]:
            enc = "-" if m == "rule" else "std"
            row[f"Đủ đặc trưng {tgt}"] = cell(sel(tgt, "in", "full", "-", m)) if m != "rule" else "–"
            row[f"Trong-miền {tgt} (KN chung)"] = cell(sel(tgt, "in", main_set, enc, m))
            row[f"{src}→{tgt} (KN chung, std)"] = cell(sel(tgt, f"{src}->{tgt}", main_set, "std", m)) if m != "rule" else "–"
            row[f"{src}→{tgt} (KN chung, C1)"] = cell(sel(tgt, f"{src}->{tgt}", main_set, "rank", m)) if m != "rule" else "–"
        rows.append(row)
    main_tab = pd.DataFrame(rows); main_tab.to_csv(out + "_bang_chinh.csv", index=False)

    tests = []
    for enc in ["std", "rank"]:
        for m in models:
            for tgt, src in [(d1, d2), (d2, d1)]:
                ins, xs = sel(tgt, "in", main_set, enc, m), sel(tgt, f"{src}->{tgt}", main_set, enc, m)
                if not len(ins) or not len(xs):
                    continue
                for met in ["auc_roc", "pr_auc"]:
                    d = xs[met].to_numpy() - ins[met].to_numpy()
                    mean, lo, hi, p = corrected(d)
                    tests.append(dict(encoding=enc, model=m, direction=f"{src}->{tgt}", metric=met, in_mean=ins[met].mean(),
                                      cross_mean=xs[met].mean(), delta=mean, ci_lo=lo, ci_hi=hi, p_corrected=p,
                                      ratio_cross_in=xs[met].mean() / ins[met].mean(),
                                      ratio_above_chance=(xs[met].mean() - .5) / (ins[met].mean() - .5) if met == "auc_roc" else np.nan))
    T = pd.DataFrame(tests)
    for _, g in T.groupby(["encoding", "metric"]):
        T.loc[g.index, "p_holm"] = holm(g.p_corrected.to_numpy())
    T.to_csv(out + "_kiem_dinh.csv", index=False)

    sens = []
    for cs in P["sets"]:
        for enc in ["std", "rank"]:
            for m in models:
                row = {"Tập khái niệm": cs, "Mã hoá": enc, "Mô hình": m}
                for tgt, src in [(d1, d2), (d2, d1)]:
                    ins, xs = sel(tgt, "in", cs, enc, m), sel(tgt, f"{src}->{tgt}", cs, enc, m)
                    row[f"Trong-miền {tgt}"] = round(ins.auc_roc.mean(), 3) if len(ins) else np.nan
                    row[f"{src}→{tgt}"] = round(xs.auc_roc.mean(), 3) if len(xs) else np.nan
                sens.append(row)
    S = pd.DataFrame(sens).dropna(how="all", subset=[c for c in pd.DataFrame(sens).columns if "→" in c or "Trong" in c])
    S.to_csv(out + "_ma_hoa.csv", index=False)

    fig, axes = plt.subplots(1, 2, figsize=(11, 3.9), sharey=False, constrained_layout=True)
    for ax, (tgt, src) in zip(axes, [(d1, d2), (d2, d1)]):
        x = np.arange(len(models))
        for off, setting, enc, lab, col, mk in [(-0.22, "in", "std", "Trong-miền", "#7f7f7f", "o"),
                                                (0.0, f"{src}->{tgt}", "std", "Xuyên-miền, thang đo của nguồn", "#9ec5f0", "s"),
                                                (0.22, f"{src}->{tgt}", "rank", "Xuyên-miền, căn chỉnh theo miền (C1)", "#2a78d6", "D")]:
            ms, er, xx = [], [], []
            for i, m in enumerate(models):
                v = sel(tgt, setting, main_set, enc, m).auc_roc
                if len(v) > 1:
                    mean = v.mean(); lo, hi = corrected_ci(v)
                    ms.append(mean); er.append(hi - mean); xx.append(i + off)
            ax.errorbar(xx, ms, yerr=er, fmt=mk, color=col, capsize=3, ms=6, label=lab)
        rule = sel(tgt, "in", main_set, "-", "rule").auc_roc.mean()
        ax.axhline(rule, color="#eb6834", ls="--", lw=1.2, label="Quy tắc không cần học")
        ax.axhline(0.5, color="#bbbbbb", lw=1)
        ax.set_xticks(x); ax.set_xticklabels([TICK[m] for m in models])
        ax.set_title(f"Đích {tgt} ({SHORT[tgt]}): trong-miền và {src}→{tgt}", loc="left", fontsize=10, fontweight="bold")
        ax.grid(axis="y", color="#e5e5e5"); ax.spines[["top", "right"]].set_visible(False)
    axes[0].set_ylabel("AUC-ROC (CI 95% có hiệu chỉnh)")
    h, l = axes[0].get_legend_handles_labels()
    fig.legend(h, l, loc="upper center", ncol=4, frameon=False, fontsize=8, bbox_to_anchor=(.5, 1.1))
    fig.savefig(out + "_hinh.png", dpi=200, bbox_inches="tight", facecolor="white")

    pd.set_option("display.width", 250); pd.set_option("display.max_columns", 30)
    print("Đọc:", [os.path.basename(f) for f in files], "| mô hình:", models)
    print(main_tab.to_string(index=False))
    print(T[T.metric == "auc_roc"][["encoding", "model", "direction", "in_mean", "cross_mean", "delta", "ci_lo", "ci_hi",
                                    "p_corrected", "p_holm", "ratio_cross_in", "ratio_above_chance"]].round(4).to_string(index=False))
    print(S.to_string(index=False))


def corrected_ci(v):
    _, lo, hi, _ = corrected(np.asarray(v, float))
    return lo, hi


if __name__ == "__main__":
    main()
