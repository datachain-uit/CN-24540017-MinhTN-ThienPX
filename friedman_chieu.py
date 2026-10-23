"""
friedman_chieu.py — Friedman – Nemenyi ở mức CHIỀU (review 22/10, N3 và mục 6.5).

    python friedman_chieu.py --out results/tong_hop_cap

Mỗi khối là một chiều chuyển giao; giá trị là PR-AUC trung bình trên k ∈ {10, 20, 50} (mức k quyết định của Cổng 0).
Zero-shot không phụ thuộc k nên không đưa vào (giống Phụ lục B3 của review). Đối chứng xáo trộn bị loại.
  Chính    : 4 chiều AB + AC (A ↔ D là thăm dò, tách khỏi tổng hợp chính – quyết định 2)
  Đối chiếu: 6 chiều kể cả A ↔ D (đúng phép tính ở Phụ lục A3 của review: χ² = 36,2; CD = 7,45)
N ≤ 6 nên chỉ mang tính mô tả. Bản 41 khối (pairs_synthesis.py) là phân tích độ nhạy: các khối phụ thuộc nhau vì
các mức k lồng nhau dùng chung lần chia và ba chiều có đích IBM dùng chung file chia.
"""
import argparse, os
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

NAME = {"LR": "LR", "RF": "Random Forest", "XGB": "XGBoost", "CAT": "CatBoost", "STACK": "Stacking LR + RF + XGB", "TabPFN": "TabPFN v2",
        "STK_LR": "Stacking điểm nguồn + LR", "STK_XGB": "Stacking điểm nguồn + XGBoost", "OFF_XGB": "XGBoost khởi tạo từ nguồn",
        "DAUME_LR": "Daumé + LR", "RANKAVG": "Trung bình hạng LR w(k)", "ANCHOR_LR": "LR neo hệ số nguồn", "RANKAVG_RF": "RANKAVG-RF"}
TO = ["LR", "RF", "XGB", "CAT", "STACK", "TabPFN"]
SRC = [("g0_23", "AB"), ("g0_AC", "AC"), ("g0_AD", "AD")]


def friedman(blk):
    rank = blk.rank(axis=1, ascending=False)                       # 1 = tốt nhất
    chi2, p = stats.friedmanchisquare(*[blk[c] for c in blk.columns])
    N, k = blk.shape
    q = stats.studentized_range.ppf(0.95, k, np.inf) / np.sqrt(2)
    CD = q * np.sqrt(k * (k + 1) / (6 * N))
    return rank.mean().sort_values(), chi2, p, CD, N, k


def cd_plot(avg, CD, N, title, path):
    fig, ax = plt.subplots(figsize=(7.5, 0.32 * len(avg) + 1.2), constrained_layout=True)
    yy = np.arange(len(avg))[::-1]
    for y, (m, v) in zip(yy, avg.items()):
        to = m in TO
        ax.errorbar(v, y, xerr=CD / 2, fmt="o" if to else "D", color="#7f7f7f" if to else "#2a78d6", capsize=3, ms=6)
    ax.set_yticks(yy); ax.set_yticklabels([NAME.get(m, m) for m in avg.index], fontsize=9)
    ax.invert_xaxis(); ax.set_xlabel(f"Hạng trung bình theo PR-AUC (1 = tốt nhất), đoạn = ± CD/2, CD = {CD:.2f}")
    ax.grid(axis="x", color="#e5e5e5"); ax.spines[["top", "right"]].set_visible(False)
    ax.set_title(title, loc="left", fontsize=10, fontweight="bold")
    from matplotlib.lines import Line2D
    ax.legend([Line2D([], [], marker="o", color="#7f7f7f", ls=""), Line2D([], [], marker="D", color="#2a78d6", ls="")],
              ["Chỉ dùng dữ liệu đích", "Chuyển giao"], loc="upper left", fontsize=8, frameon=False)
    fig.savefig(path, dpi=200, bbox_inches="tight", facecolor="white")


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--out", default="results/tong_hop_cap"); a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    x = pd.concat([pd.read_csv(f"results/{d}/g0_bang_duong_cong.csv").assign(pair=p) for d, p in SRC])
    x = x[~x.method.str.contains("SHUF")]; x["k"] = x.k.astype(str)
    blk_all = x[x.k.isin(["10", "20", "50"])].groupby(["pair", "target", "method"]).pr_auc.mean().unstack().dropna(axis=1)
    out, txt = [], []
    for name, blk in [("chinh_4_chieu", blk_all.drop(index="AD", level="pair")), ("doi_chieu_6_chieu", blk_all)]:
        avg, chi2, p, CD, N, k = friedman(blk)
        line = f"{name}: N = {N} chiều, k = {k} phương pháp; chi2 = {chi2:.2f}, p = {p:.1e}; Nemenyi CD (α = 0,05) = {CD:.2f}"
        txt.append(line); print(line)
        for m, v in avg.items():
            out.append(dict(phan_tich=name, phuong_phap=NAME.get(m, m), ma=m, nhom="chỉ đích" if m in TO else "chuyển giao", hang_TB=v))
        cd_plot(avg, CD, N, f"Friedman – Nemenyi mức chiều ({N} chiều{', bỏ A ↔ D thăm dò' if N == 4 else ''}; chỉ mô tả)",
                f"{a.out}/cd_chieu_{N}.png")
        print(avg.round(2).to_string(), "\n")
    pd.DataFrame(out).to_csv(f"{a.out}/friedman_chieu_hang.csv", index=False)
    open(f"{a.out}/friedman_chieu.txt", "w").write("\n".join(txt) + "\n")
    blk_all.to_csv(f"{a.out}/friedman_chieu_khoi.csv")


if __name__ == "__main__":
    main()
