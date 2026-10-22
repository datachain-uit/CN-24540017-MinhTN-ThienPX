"""
g0_decision.py — Tổng hợp G0-2/G0-3 và áp tiêu chí GO/PIVOT của Cổng 0.

Tiêu chí (báo cáo B2.2, đã chốt trước khi chạy):
  GO    nếu có ít nhất một baseline chuyển giao đơn giản vượt baseline CHỈ-DÙNG-ĐÍCH MẠNH NHẤT tại cùng k (kể cả TabPFN v2)
        ở một mức k ≤ 50, chênh PR-AUC ≥ 0,02 và CI 95% (có hiệu chỉnh Nadeau–Bengio) không chứa 0;
  PIVOT nếu không.
Baseline đích mạnh nhất được chọn theo PR-AUC trung bình tại từng k (lựa chọn có lợi cho baseline, nên thận trọng với GO).
Kiểm định bắt cặp theo lần chia; ngoài CI hiệu chỉnh còn báo p Holm trên mọi cặp (phương pháp chuyển giao × k ≤ 50) của một chiều.

    python g0_decision.py results/g0_23            # đọc mọi results_g0_23_*.csv trong thư mục (CPU + TabPFN nếu có)
"""
import glob, sys
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

RATIO = 0.25
KS_DECIDE = ["10", "20", "50"]
K_ORDER = ["10", "20", "50", "100", "200", "500", "full"]
TO = ["LR", "RF", "XGB", "CAT", "STACK", "TabPFN"]
TR = ["ZS", "STK_LR", "STK_XGB", "OFF_XGB", "DAUME_LR", "RANKAVG", "ANCHOR_LR", "RANKAVG_RF"]
CTRL = ["ZS", "STK_LR", "RANKAVG", "ANCHOR_LR", "RANKAVG_RF"]
NAME = {"LR": "LR", "RF": "Random Forest", "XGB": "XGBoost", "TabPFN": "TabPFN v2", "ZS": "Zero-shot từ nguồn",
        "STK_LR": "Stacking + LR", "STK_XGB": "Stacking + XGBoost", "OFF_XGB": "XGBoost khởi tạo từ nguồn",
        "DAUME_LR": "Tăng cường Daumé + LR", "CAT": "CatBoost", "STACK": "Stacking LR+RF+XGB",
        "RANKAVG": "Trung bình hạng w(k)", "ANCHOR_LR": "LR neo hệ số nguồn", "RANKAVG_RF": "Trung bình hạng RF + nguồn"}
COL = {"STK_LR": "#2a78d6", "STK_XGB": "#eb6834", "OFF_XGB": "#1baf7a", "DAUME_LR": "#eda100", "ZS": "#e87ba4",
       "RANKAVG": "#008300", "ANCHOR_LR": "#6250d6", "RANKAVG_RF": "#e34948",
       "LR": "#2a78d6", "XGB": "#eb6834", "RF": "#1baf7a", "CAT": "#eda100", "STACK": "#008300", "TabPFN": "#6250d6"}
MK = {"STK_LR": "o", "STK_XGB": "s", "OFF_XGB": "D", "DAUME_LR": "^", "ZS": "v", "RANKAVG": "X", "ANCHOR_LR": "P", "RANKAVG_RF": "h",
      "LR": "o", "XGB": "s", "RF": "D", "CAT": "^", "STACK": "X", "TabPFN": "P"}
DIR = {"A": "B→A (đích IBM, nhãn nghỉ việc)", "B": "A→B (đích Job Change, nhãn ý định)"}


def corrected(d, ratio=RATIO):
    d = np.asarray(d, float); J = len(d); sd = np.std(d, ddof=1)
    se = np.sqrt((1 / J + ratio)) * sd
    t = d.mean() / se if se > 0 else np.inf
    h = stats.t.ppf(0.975, J - 1) * se
    return d.mean(), d.mean() - h, d.mean() + h, 2 * stats.t.sf(abs(t), J - 1)


def holm(p):
    p = np.asarray(p); o = np.argsort(p); m = len(p); adj = np.empty(m); run = 0
    for i, k in enumerate(o):
        run = max(run, (m - i) * p[k]); adj[k] = min(1, run)
    return adj


TGTS = ["A", "B"]


def set_pair(pair):
    """Đặt tên chiều chuyển giao cho cặp khác AB (đọc từ pairs.py)."""
    global TGTS, DIR
    if pair in (None, "AB"):
        return
    from pairs import PAIRS, SHORT
    d1, d2 = PAIRS[pair]["domains"]
    TGTS = [d1, d2]
    DIR = {d1: f"{d2}→{d1} (đích {SHORT[d1]})", d2: f"{d1}→{d2} (đích {SHORT[d2]})"}


def main(folder):
    files = sorted(glob.glob(f"{folder}/results_g0_23_*.csv") + glob.glob(f"{folder}/results_g0_[A-D][A-D]_*.csv"))
    r = pd.concat([pd.read_csv(f) for f in files], ignore_index=True)
    r["k"] = r["k"].astype(str)
    has_tabpfn = (r.method == "TabPFN").any()
    print("Đọc:", [f.split("/")[-1] for f in files], "| có TabPFN v2:", has_tabpfn)

    # Bảng đường cong: PR-AUC (AUC-ROC) trung bình
    curve = r.groupby(["target", "method", "k"])[["pr_auc", "auc_roc"]].mean().reset_index()
    curve.to_csv(f"{folder}/g0_bang_duong_cong.csv", index=False)

    rows = []
    for tgt in TGTS:
        rt = r[r.target == tgt]
        zs = rt[rt.method == "ZS"].set_index("rep").pr_auc
        for k in KS_DECIDE:
            rk = rt[rt.k == k]
            means = rk[rk.family == "target_only"].groupby("method").pr_auc.mean()
            best = means.idxmax()
            base = rk[rk.method == best].set_index("rep").pr_auc
            for m in TR:
                cand = zs if m == "ZS" else rk[rk.method == m].set_index("rep").pr_auc
                if not len(cand):
                    continue
                d = (cand - base).dropna()
                mean, lo, hi, p = corrected(d.to_numpy())
                rows.append(dict(target=tgt, k=int(k), method=m, best_target_only=best, base_pr=base.mean(), method_pr=cand.mean(),
                                 delta=mean, ci_lo=lo, ci_hi=hi, p_corr=p, n_rep=len(d), pos_rate=rk.pos_rate_test.mean()))
    T = pd.DataFrame(rows)
    for tgt, g in T.groupby("target"):
        T.loc[g.index, "p_holm"] = holm(g.p_corr.to_numpy())
    T["dat_GO"] = (T.delta >= 0.02) & (T.ci_lo > 0)
    T.to_csv(f"{folder}/g0_kiem_dinh_GO.csv", index=False)

    pd.set_option("display.width", 220)
    print("\nPR-AUC trung bình theo k (cột) – G0-2 và G0-3:")
    for tgt in TGTS:
        piv = curve[curve.target == tgt].pivot(index="method", columns="k", values="pr_auc")
        piv = piv[[c for c in ["zero"] + K_ORDER if c in piv.columns]].reindex([m for m in TO + TR if m in piv.index])
        print(f"\nĐích {tgt} — {DIR[tgt]}; tỷ lệ dương test = {r[r.target == tgt].pos_rate_test.mean():.3f}")
        print(piv.round(3).to_string())
    print("\nSo với baseline đích mạnh nhất tại cùng k (Δ PR-AUC, CI 95% hiệu chỉnh):")
    print(T[["target", "k", "method", "best_target_only", "base_pr", "method_pr", "delta", "ci_lo", "ci_hi", "p_corr", "p_holm", "dat_GO"]]
          .round(4).to_string(index=False))

    verdict = {}
    for tgt in TGTS:
        g = T[(T.target == tgt) & T.dat_GO]
        verdict[tgt] = "GO" if len(g) else "PIVOT"
        print(f"\nKẾT LUẬN chiều {DIR[tgt]}: {verdict[tgt]}" +
              (f" — đạt ở: {', '.join(f'{x.method}@k={x.k} (Δ={x.delta:+.3f})' for x in g.itertuples())}" if len(g) else ""))
    if not has_tabpfn:
        print("\nLƯU Ý: chưa có TabPFN v2 → kết luận TẠM THỜI. Nếu là PIVOT thì TabPFN không thể đổi thành GO "
              "(nó chỉ làm baseline mạnh hơn); nếu là GO thì phải chạy TabPFN để xác nhận.")
    open(f"{folder}/g0_ket_luan.txt", "w").write(
        "\n".join(f"{t}: {v}" for t, v in verdict.items()) + f"\nco_TabPFN: {has_tabpfn}\n")

    # ---------------- Phân tích phụ: chuyển giao có giúp CHÍNH mô hình đó không (cùng họ, mọi k)
    pairs = [("STK_LR", "LR"), ("DAUME_LR", "LR"), ("STK_XGB", "XGB"), ("OFF_XGB", "XGB")]
    rows2 = []
    for tgt in TGTS:
        for k in K_ORDER:
            rk = r[(r.target == tgt) & (r.k == k)]
            for m, b in pairs:
                a_, b_ = rk[rk.method == m].set_index("rep").pr_auc, rk[rk.method == b].set_index("rep").pr_auc
                if len(a_) and len(b_):
                    mean, lo, hi, p = corrected((a_ - b_).dropna().to_numpy())
                    rows2.append(dict(target=tgt, k=k, method=m, vs=b, delta=mean, ci_lo=lo, ci_hi=hi, p_corr=p))
    S2 = pd.DataFrame(rows2); S2.to_csv(f"{folder}/g0_cung_ho.csv", index=False)
    print("\nPhân tích phụ – chuyển giao so với CÙNG mô hình chỉ dùng đích (Δ PR-AUC):")
    print(S2.pivot_table(index=["target", "method", "vs"], columns="k", values="delta")[K_ORDER].round(3).to_string())

    # ---------------- G0-4: đối chứng xáo trộn nhãn nguồn
    if (r.family == "control").any():
        rows3 = []
        for tgt in TGTS:
            for m in CTRL:
                for k in (["zero"] if m == "ZS" else K_ORDER):
                    rk = r[(r.target == tgt) & (r.k == k)]
                    a_, b_ = rk[rk.method == m].set_index("rep").pr_auc, rk[rk.method == m + "_SHUF"].set_index("rep").pr_auc
                    if len(a_) and len(b_):
                        mean, lo, hi, p = corrected((a_ - b_).dropna().to_numpy())
                        rows3.append(dict(target=tgt, method=m, k=k, that=a_.mean(), xao_tron=b_.mean(), delta=mean, ci_lo=lo, ci_hi=hi, p_corr=p))
        S3 = pd.DataFrame(rows3); S3.to_csv(f"{folder}/g0_doi_chung_xao_tron.csv", index=False)
        print("\nG0-4 – nguồn thật trừ nguồn xáo trộn nhãn (Δ PR-AUC; > 0 nghĩa là nguồn mang thông tin):")
        print(S3.pivot_table(index=["target", "method"], columns="k", values="delta")[[c for c in ["zero"] + K_ORDER if c in set(S3.k)]].round(3).to_string())

    # ---------------- Hình 1: Δ PR-AUC so với baseline đích mạnh nhất (k ≤ 50)
    fig, axes = plt.subplots(1, 2, figsize=(11, 3.9), sharey=True, constrained_layout=True)
    for ax, tgt in zip(axes, TGTS):
        g = T[T.target == tgt]
        ms = [m for m in TR if m in set(g.method)]
        w = 0.11
        for i, m in enumerate(ms):
            gm = g[g.method == m].sort_values("k")
            x = np.arange(len(gm)) + (i - (len(ms) - 1) / 2) * w
            ax.errorbar(x, gm.delta, yerr=[gm.delta - gm.ci_lo, gm.ci_hi - gm.delta], fmt=MK[m], color=COL[m], ms=7,
                        mec="#fcfcfb", mew=1.2, capsize=2.5, lw=1.4, label=NAME[m])
        ax.axhline(0, color="#52514e", lw=1)
        ax.axhline(0.02, color="#52514e", lw=1, ls="--")
        ax.text(-0.48, 0.024, "ngưỡng GO +0,02", fontsize=8, color="#52514e", ha="left", va="bottom", zorder=5,
                bbox=dict(boxstyle="square,pad=0.15", fc="white", ec="none"))
        ax.set_xticks(range(len(KS_DECIDE))); ax.set_xticklabels([f"k = {k}" for k in KS_DECIDE])
        ax.set_title(f"{DIR[tgt]}", loc="left", fontsize=10, fontweight="bold")
        ax.grid(axis="y", color="#e4e3df"); ax.spines[["top", "right"]].set_visible(False)
    axes[0].set_ylabel("Δ PR-AUC so với baseline đích mạnh nhất\n(CI 95% có hiệu chỉnh)")
    h, l = axes[0].get_legend_handles_labels()
    fig.legend(h, l, loc="upper center", ncol=4, frameon=False, fontsize=8, bbox_to_anchor=(.5, 1.14))
    fig.savefig(f"{folder}/g0_hinh_delta.png", dpi=200, bbox_inches="tight", facecolor="white")

    # ---------------- Hình 2: đường cong PR-AUC theo k
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 3.9), constrained_layout=True)
    for ax, tgt in zip(axes, TGTS):
        ct = curve[curve.target == tgt]
        for m in [x for x in TO if x in set(ct.method)]:
            c = ct[ct.method == m].set_index("k").reindex(K_ORDER).dropna()
            x = [K_ORDER.index(k) for k in c.index]
            ax.plot(x, c.pr_auc, marker=MK[m], color=COL[m], lw=2, ms=7, mec="#fcfcfb", mew=1.2, label=f"{NAME[m]} (chỉ đích)")
        best_tr = ct[ct.method.isin([m for m in TR if m != "ZS"])].groupby("k").pr_auc.max().reindex(K_ORDER).dropna()
        ax.plot([K_ORDER.index(k) for k in best_tr.index], best_tr, color="#0b0b0b", lw=1.6, ls="--", marker=".",
                label="Chuyển giao tốt nhất tại mỗi k")
        zsv = ct[ct.method == "ZS"].pr_auc.mean()
        ax.axhline(zsv, color=COL["ZS"], lw=1.6, ls=":", label="Zero-shot từ nguồn")
        pr = r[r.target == tgt].pos_rate_test.mean()
        ax.axhline(pr, color="#9a9994", lw=1, label="Đoán ngẫu nhiên (tỷ lệ dương)")
        ax.set_xticks(range(len(K_ORDER))); ax.set_xticklabels(K_ORDER)
        ax.set_xlabel("Số mẫu có nhãn của miền đích (k)")
        ax.set_title(DIR[tgt], loc="left", fontsize=10, fontweight="bold")
        ax.grid(axis="y", color="#e4e3df"); ax.spines[["top", "right"]].set_visible(False)
    axes[0].set_ylabel("PR-AUC trung bình (30 lần chia)")
    h, l = axes[0].get_legend_handles_labels()
    fig.legend(h, l, loc="upper center", ncol=4, frameon=False, fontsize=8, bbox_to_anchor=(.5, 1.17))
    fig.savefig(f"{folder}/g0_hinh_duong_cong.png", dpi=200, bbox_inches="tight", facecolor="white")
    print("\nĐã lưu: g0_bang_duong_cong.csv, g0_kiem_dinh_GO.csv, g0_ket_luan.txt, g0_hinh_delta.png, g0_hinh_duong_cong.png")


if __name__ == "__main__":
    set_pair(sys.argv[2] if len(sys.argv) > 2 else None)
    main(sys.argv[1] if len(sys.argv) > 1 else "results/g0_23")
