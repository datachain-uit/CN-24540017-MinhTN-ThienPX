"""
mde_cong0.py — Bảng MDE của Cổng 0 (review 22/10, N1 và mục 6.2), tính lại từ kết quả thô.

    python mde_cong0.py --out results/tong_hop_cap

Với mỗi chiều (đích, nguồn) và k ∈ {10, 20, 50}: baseline chỉ dùng đích mạnh nhất (như tiêu chí GO), mỗi phương pháp
chuyển giao m → hiệu bắt cặp d_r = PR-AUC(m) − PR-AUC(baseline) trên R = 30 lần chia.
  SE hiệu chỉnh (Nadeau–Bengio)  = sqrt(1/R + n_test/n_train) · sd(d)
  Nửa độ rộng CI 95%            = t(0,975; R−1) · SE                         (đối chiếu Phụ lục A4 của review 22/10)
  MDE (α = 0,05 hai phía, power 80%) = [t(0,975; R−1) + t(0,80; R−1)] · SE
  Δ nhỏ nhất đạt GO với power 80% = max(0,02; MDE)     (GO cần Δ ≥ 0,02 và CI không chứa 0)
Báo cáo cho phép so sánh “chuyển giao tốt nhất − đích mạnh nhất” (giống A4) và trung vị trên 8 phương pháp chuyển giao.
"""
import argparse, glob, os
import numpy as np
import pandas as pd
from scipy import stats

RATIO = 0.25
TO = ["LR", "RF", "XGB", "CAT", "STACK", "TabPFN"]
TR = ["ZS", "STK_LR", "STK_XGB", "OFF_XGB", "DAUME_LR", "RANKAVG", "ANCHOR_LR", "RANKAVG_RF"]
DIRS = [("results/g0_23", "A", "B→A", "AB"), ("results/g0_23", "B", "A→B", "AB"), ("results/g0_AC", "A", "C→A", "AC"),
        ("results/g0_AC", "C", "A→C", "AC"), ("results/g0_AD", "A", "D→A", "AD (thăm dò)"), ("results/g0_AD", "D", "A→D", "AD (thăm dò)")]


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--out", default="results/tong_hop_cap"); a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    rows = []
    for folder, tgt, chieu, cap in DIRS:
        r = pd.concat([pd.read_csv(f, dtype={"k": str}) for f in glob.glob(f"{folder}/results_g0_*.csv")], ignore_index=True)
        r = r[(r.target == tgt) & ~r.method.str.startswith("TBHTL")]
        R = r.rep.nunique()
        t975, t80 = stats.t.ppf(.975, R - 1), stats.t.ppf(.80, R - 1)
        for k in ["10", "20", "50"]:
            g = r[r.k.isin([k, "zero"])]
            curve = g.groupby(["method", "k"]).pr_auc.mean()
            base_m = max([m for m in TO if (m, k) in curve.index], key=lambda m: curve[(m, k)])
            base = g[(g.method == base_m) & (g.k == k)].set_index("rep").pr_auc
            per = []
            for m in TR:
                kk = "zero" if m == "ZS" else k
                x = g[(g.method == m) & (g.k == kk)].set_index("rep").pr_auc
                if not len(x):
                    continue
                d = (x - base).dropna()
                se = np.sqrt(1 / len(d) + RATIO) * d.std(ddof=1)
                per.append(dict(method=m, delta=d.mean(), se=se, half=t975 * se, mde=(t975 + t80) * se))
            P = pd.DataFrame(per)
            best = P.loc[P.delta.idxmax()]
            rows.append(dict(cap=cap, chieu=chieu, k=int(k), baseline_dich=base_m, pr_baseline=base.mean(),
                             chuyen_giao_tot_nhat=best.method, delta_tot_nhat=best.delta,
                             nua_do_rong_CI=best.half, MDE80=best.mde, MDE80_trung_vi_8_pp=P.mde.median(),
                             delta_GO_can_80=max(0.02, best.mde), R=R))
    T = pd.DataFrame(rows)
    T.to_csv(f"{a.out}/mde_cong0.csv", index=False)
    pd.set_option("display.width", 220)
    print(T.round(3).to_string(index=False))
    print(f"\nNửa độ rộng CI (chuyển giao tốt nhất): trung vị {T.nua_do_rong_CI.median():.3f}; "
          f"min {T.nua_do_rong_CI.min():.3f}; max {T.nua_do_rong_CI.max():.3f}; số ô < 0,02: {(T.nua_do_rong_CI < .02).sum()}/{len(T)}")
    print(f"MDE80 (chuyển giao tốt nhất): trung vị {T.MDE80.median():.3f}; chỉ AB + AC: {T[~T.cap.str.startswith('AD')].MDE80.median():.3f}")
    # bảng gọn: chiều × k
    W = T.pivot_table(index=["cap", "chieu"], columns="k", values="MDE80", sort=False)
    W.to_csv(f"{a.out}/mde_cong0_bang.csv")
    print("\nMDE80 theo chiều × k:"); print(W.round(3).to_string())


if __name__ == "__main__":
    main()
