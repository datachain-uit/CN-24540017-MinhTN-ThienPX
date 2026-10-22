"""
analyze_results.py
Tổng hợp kết quả giống Hình 2, 7, 9 của bài báo:
  - Thứ hạng có xét ý nghĩa thống kê: trên mỗi (nhiệm vụ, số mẫu), hạng của mô hình m
    = 1 + số mô hình tốt hơn m một cách có ý nghĩa (Wilcoxon rank-sum một phía, p < 0.05,
    trên ROC-AUC của các seed). Các mô hình top không khác biệt có ý nghĩa đều nhận hạng 1.
  - Trung bình hạng trên 12 nhiệm vụ -> heatmap; sai số chuẩn của hạng; AUC trung bình;
    mức cải thiện ROC-AUC so với CatBoost.

  python analyze_results.py --results outputs/results_metamimic.csv
"""
import argparse
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import ranksums

MODEL_ORDER = ["ft_transformer", "resnet", "mlp", "tab_transformer", "catboost", "xgboost"]
MODEL_LABEL = {"ft_transformer": "FT-Transformer", "resnet": "ResNet", "mlp": "MLP",
               "tab_transformer": "TabTransformer", "catboost": "CatBoost", "xgboost": "XGBoost"}
SETUP_ORDER = ["FS", "LH-E2E", "MLP-E2E", "LH", "MLP", "Stacking"]


def significance_ranks(df: pd.DataFrame, alpha=0.05) -> pd.DataFrame:
    out = []
    for (t, n), g in df.groupby(["target_idx", "n_samples"]):
        scores = {k: v["auc"].dropna().values for k, v in g.groupby(["model", "setup"])}
        for m, sm in scores.items():
            better = 0
            for o, so in scores.items():
                if o == m or len(so) < 2 or len(sm) < 2:
                    continue
                if ranksums(so, sm, alternative="greater").pvalue < alpha:
                    better += 1
            out.append(dict(target_idx=t, n_samples=n, model=m[0], setup=m[1], rank=1 + better,
                            mean_auc=float(np.mean(sm))))
    return pd.DataFrame(out)


def ordered_columns(cols):
    return sorted(cols, key=lambda c: (MODEL_ORDER.index(c[0]) if c[0] in MODEL_ORDER else 99,
                                       SETUP_ORDER.index(c[1]) if c[1] in SETUP_ORDER else 99))


def plot_panels(table: pd.DataFrame, path: str, title: str, cmap="RdYlBu", fmt=".1f", cbar_label="Rank"):
    table = table.dropna(axis=1, how="all")
    models = [m for m in MODEL_ORDER if m in table.columns.get_level_values(0)]
    if not models:
        print(f"  (bỏ qua {os.path.basename(path)}: chưa đủ dữ liệu, ví dụ cần >= 2 nhiệm vụ để tính SE)")
        return
    widths = [table[m].shape[1] for m in models]
    fig, axes = plt.subplots(1, len(models), figsize=(1.0 * sum(widths) + 2, 3.6),
                             gridspec_kw={"width_ratios": widths}, squeeze=False)
    vmin, vmax = np.nanmin(table.values), np.nanmax(table.values)
    im = None
    for ax, m in zip(axes[0], models):
        sub = table[m]
        im = ax.imshow(sub.values, cmap=cmap, vmin=vmin, vmax=vmax, aspect="auto")
        for i in range(sub.shape[0]):
            for j in range(sub.shape[1]):
                ax.text(j, i, format(sub.values[i, j], fmt), ha="center", va="center", fontsize=8)
        ax.set_xticks(range(sub.shape[1]))
        ax.set_xticklabels(sub.columns, rotation=45, ha="right", fontsize=8)
        ax.set_yticks(range(sub.shape[0]))
        ax.set_yticklabels(sub.index if ax is axes[0][0] else [], fontsize=8)
        ax.set_title(MODEL_LABEL.get(m, m), fontsize=9)
    axes[0][0].set_ylabel("Num samples")
    fig.colorbar(im, ax=axes[0].tolist(), label=cbar_label, shrink=0.8)
    fig.suptitle(title, fontsize=10)
    fig.savefig(path, dpi=200, bbox_inches="tight")
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", required=True)
    ap.add_argument("--out-dir", default=None)
    ap.add_argument("--alpha", type=float, default=0.05)
    ap.add_argument("--exclude", nargs="*", default=[], help="vd: tab_transformer (Hình 2 không có TabTransformer)")
    a = ap.parse_args()
    out = a.out_dir or os.path.join(os.path.dirname(a.results) or ".", "analysis")
    os.makedirs(out, exist_ok=True)

    df = pd.read_csv(a.results)
    df = df[~df.model.isin(a.exclude)]
    ranks = significance_ranks(df, a.alpha)
    ranks.to_csv(os.path.join(out, "ranks_per_task.csv"), index=False)

    def pivot(values, agg):
        t = ranks.pivot_table(index="n_samples", columns=["model", "setup"], values=values, aggfunc=agg)
        t = t[ordered_columns(list(t.columns))]
        return t.sort_index(ascending=False)

    avg_rank = pivot("rank", "mean")
    se = ranks.groupby(["n_samples", "model", "setup"])["rank"].agg(
        lambda x: np.std(x, ddof=1) / np.sqrt(len(x)) if len(x) > 1 else np.nan)
    se_rank = se.unstack(["model", "setup"]).reindex(columns=avg_rank.columns).sort_index(ascending=False)
    mean_auc = pivot("mean_auc", "mean")
    avg_rank.round(2).to_csv(os.path.join(out, "avg_rank.csv"))
    se_rank.round(2).to_csv(os.path.join(out, "rank_std_error.csv"))
    mean_auc.round(4).to_csv(os.path.join(out, "mean_auc.csv"))

    plot_panels(avg_rank, os.path.join(out, "fig2_avg_ranks.png"),
                "Average rank across downstream tasks (lower = better)")
    plot_panels(se_rank, os.path.join(out, "fig7_rank_std_error.png"), "Rank standard error",
                cmap="Blues_r", cbar_label="Rank SE")

    # Hình 9: cải thiện ROC-AUC so với CatBoost (FS), trung bình trên các nhiệm vụ
    if ("catboost", "FS") in set(zip(ranks.model, ranks.setup)):
        base = ranks[(ranks.model == "catboost") & (ranks.setup == "FS")][["target_idx", "n_samples", "mean_auc"]]
        imp = ranks.merge(base, on=["target_idx", "n_samples"], suffixes=("", "_cb"))
        imp["delta"] = imp["mean_auc"] - imp["mean_auc_cb"]
        imp_t = imp.pivot_table(index="n_samples", columns=["model", "setup"], values="delta", aggfunc="mean")
        imp_t = imp_t[ordered_columns(list(imp_t.columns))].sort_index(ascending=False)
        imp_t.round(3).to_csv(os.path.join(out, "auc_improvement_over_catboost.csv"))
        plot_panels(imp_t, os.path.join(out, "fig9_auc_improvement.png"),
                    "Average ROC-AUC improvement over CatBoost", cmap="RdYlBu_r", fmt=".2f",
                    cbar_label="ΔAUC")

    pd.set_option("display.width", 250)
    print("\nAverage rank (hàng = số mẫu downstream):\n", avg_rank.round(1))
    print(f"\nĐã lưu bảng & hình vào {out}/")


if __name__ == "__main__":
    main()
