"""
kb1_v2_summary.py — Tổng hợp KB1 v2: trung bình ± ĐLC, CI 95% có hiệu chỉnh cho các lần chia chồng lấn,
corrected resampled t-test (Nadeau & Bengio, 2003) cho chênh lệch trong-miền -> xuyên-miền, hiệu chỉnh Holm.

    python kb1_v2_summary.py results/kb1_v2/results_kb1v2_<cfg>.csv
"""
import sys
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

RATIO = 0.25  # n_test / n_train với chia 80/20
MODELS = ["LR", "RF", "RF_leaf50", "XGB"]
NAMES = {"LR": "Logistic Regression (L2)", "RF": "Random Forest (mặc định)", "RF_leaf50": "Random Forest (min_samples_leaf = 50)",
         "XGB": "XGBoost (300 cây, độ sâu 4)", "rule_neg_experience": "Quy tắc “− kinh nghiệm” (không học)"}


def corrected_ci(x, ratio=RATIO):
    x = np.asarray(x, float); J = len(x)
    se = np.sqrt((1 / J + ratio) * np.var(x, ddof=1))
    h = stats.t.ppf(0.975, J - 1) * se
    return x.mean() - h, x.mean() + h


def corrected_t(diff, ratio=RATIO):
    diff = np.asarray(diff, float); J = len(diff)
    t = diff.mean() / np.sqrt((1 / J + ratio) * np.var(diff, ddof=1))
    return t, 2 * stats.t.sf(abs(t), J - 1)


def holm(p):
    p = np.asarray(p); o = np.argsort(p); m = len(p); adj = np.empty(m); run = 0
    for i, k in enumerate(o):
        run = max(run, (m - i) * p[k]); adj[k] = min(1, run)
    return adj


def main(path, out_prefix=None):
    r = pd.read_csv(path)
    out_prefix = out_prefix or path.replace(".csv", "")
    cell = lambda d: f"{d.auc_roc.mean():.3f} ± {d.auc_roc.std():.3f} ({d.pr_auc.mean():.3f})"

    # Bảng chính: 4 khái niệm chung, mã hoá std; dòng đủ đặc trưng
    rows = []
    for m in MODELS + ["rule_neg_experience"]:
        row = {"Mô hình": NAMES[m]}
        for tgt, src in [("A", "B"), ("B", "A")]:
            enc = "-" if m.startswith("rule") else "std"
            full = r[(r.target == tgt) & (r.setting == "in") & (r.features == "full") & (r.model == m)]
            ins = r[(r.target == tgt) & (r.setting == "in") & (r.features == "canon4") & (r.encoding == enc) & (r.model == m)]
            xs = r[(r.target == tgt) & (r.setting == f"{src}->{tgt}") & (r.features == "canon4") & (r.encoding == enc) & (r.model == m)]
            row[f"Đủ đặc trưng {tgt}"] = cell(full) if len(full) else "–"
            row[f"Trong-miền {tgt} (4 KN)"] = cell(ins)
            row[f"{src}→{tgt} (4 KN)"] = cell(xs) if len(xs) else "–"
        rows.append(row)
    main_tab = pd.DataFrame(rows)
    main_tab.to_csv(out_prefix + "_bang_chinh.csv", index=False)

    # Chênh lệch trong-miền -> xuyên-miền (bắt cặp theo lần chia), cả hai mã hoá
    tests = []
    for enc in ["std", "rank"]:
        for m in MODELS:
            for tgt, src in [("A", "B"), ("B", "A")]:
                ins = r[(r.target == tgt) & (r.setting == "in") & (r.features == "canon4") & (r.encoding == enc) & (r.model == m)].sort_values("rep")
                xs = r[(r.target == tgt) & (r.setting == f"{src}->{tgt}") & (r.features == "canon4") & (r.encoding == enc) & (r.model == m)].sort_values("rep")
                for met in ["auc_roc", "pr_auc"]:
                    d = xs[met].to_numpy() - ins[met].to_numpy()
                    t, p = corrected_t(d); lo, hi = corrected_ci(d)
                    tests.append(dict(encoding=enc, model=m, direction=f"{src}->{tgt}", metric=met,
                                      in_mean=ins[met].mean(), cross_mean=xs[met].mean(), delta=d.mean(),
                                      ci_lo=lo, ci_hi=hi, p_corrected=p, p_naive=stats.ttest_rel(xs[met], ins[met]).pvalue,
                                      ratio_cross_in=xs[met].mean() / ins[met].mean(),
                                      ratio_above_chance=(xs[met].mean() - 0.5) / (ins[met].mean() - 0.5) if met == "auc_roc" else np.nan))
    T = pd.DataFrame(tests)
    for (enc, met), g in T.groupby(["encoding", "metric"]):
        T.loc[g.index, "p_holm"] = holm(g.p_corrected.to_numpy())
    T.to_csv(out_prefix + "_kiem_dinh.csv", index=False)

    # Mã hoá và tập khái niệm (LR, XGB)
    sens = []
    for fs in ["canon4", "canon5"]:
        for enc in ["std", "rank"]:
            for m in ["LR", "XGB"]:
                row = {"Khái niệm": "4 KN" if fs == "canon4" else "5 KN (+ thâm niên)", "Mã hoá": enc, "Mô hình": m}
                for tgt, src in [("A", "B"), ("B", "A")]:
                    ins = r[(r.target == tgt) & (r.setting == "in") & (r.features == fs) & (r.encoding == enc) & (r.model == m)]
                    xs = r[(r.target == tgt) & (r.setting == f"{src}->{tgt}") & (r.features == fs) & (r.encoding == enc) & (r.model == m)]
                    row[f"Trong-miền {tgt}"] = f"{ins.auc_roc.mean():.3f}"
                    row[f"{src}→{tgt}"] = f"{xs.auc_roc.mean():.3f}"
                sens.append(row)
    pd.DataFrame(sens).to_csv(out_prefix + "_ma_hoa.csv", index=False)

    # Hình: AUC-ROC trong-miền vs xuyên-miền, CI 95% có hiệu chỉnh
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 3.9), sharey=True, constrained_layout=True)
    for ax, (tgt, src) in zip(axes, [("A", "B"), ("B", "A")]):
        x = np.arange(len(MODELS))
        series = [(-0.22, "in", "std", "Trong-miền", "#7f7f7f", "o"),
                  (0.0, f"{src}->{tgt}", "std", "Xuyên-miền, thang đo của nguồn", "#9ec5f0", "s"),
                  (0.22, f"{src}->{tgt}", "rank", "Xuyên-miền, căn chỉnh theo miền (C1)", "#2a78d6", "D")]
        for off, setting, enc, lab, col, mk in series:
            means, err = [], []
            for m in MODELS:
                v = r[(r.target == tgt) & (r.setting == setting) & (r.features == "canon4") & (r.encoding == enc) & (r.model == m)].auc_roc
                lo, hi = corrected_ci(v); means.append(v.mean()); err.append(hi - v.mean())
            ax.errorbar(x + off, means, yerr=err, fmt=mk, color=col, capsize=3, ms=6, label=lab)
        rule = r[(r.target == tgt) & (r.model == "rule_neg_experience") & (r.features == "canon4")].auc_roc.mean()
        ax.axhline(rule, color="#eb6834", ls="--", lw=1.2, label="Quy tắc “− kinh nghiệm”")
        ax.axhline(0.5, color="#bbbbbb", lw=1)
        ax.set_xticks(x); ax.set_xticklabels(["LR", "RF", "RF (leaf 50)", "XGBoost"])
        ax.set_title(f"Đích {tgt} ({'IBM' if tgt == 'A' else 'Job Change'}): trong-miền và {src}→{tgt}", loc="left", fontsize=10, fontweight="bold")
        ax.grid(axis="y", color="#e5e5e5"); ax.spines[["top", "right"]].set_visible(False)
    axes[0].set_ylabel("AUC-ROC (CI 95% có hiệu chỉnh)")
    h, l = axes[0].get_legend_handles_labels(); fig.legend(h, l, loc="upper center", ncol=4, frameon=False, fontsize=8, bbox_to_anchor=(.5, 1.1))
    fig.savefig(out_prefix + "_hinh.png", dpi=200, bbox_inches="tight", facecolor="white")

    pd.set_option("display.width", 250); pd.set_option("display.max_columns", 20)
    print(main_tab.to_string(index=False))
    print(T[T.metric == "auc_roc"][["encoding", "model", "direction", "in_mean", "cross_mean", "delta", "ci_lo", "ci_hi",
                                    "p_naive", "p_corrected", "p_holm", "ratio_cross_in", "ratio_above_chance"]].round(4).to_string(index=False))
    print(pd.DataFrame(sens).to_string(index=False))


if __name__ == "__main__":
    main(sys.argv[1])
