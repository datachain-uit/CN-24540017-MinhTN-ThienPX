"""
g0_tie_neutral_eval.py — Phân tích độ nhạy của Cổng 0 với quy tắc hoà trung tính (deviations.md mục 10; QĐ5 review 25/10).

    python g0_tie_neutral_eval.py                       # đọc results/g0_23, g0_AC, g0_AD và results/g0_tie_neutral/<cặp>
    python g0_tie_neutral_eval.py --check               # kiểm tra: với kết quả gốc phải sinh lại đúng g0_kiem_dinh_GO.csv đã công bố

Với RANKAVG và RANKAVG-RF (hai phương pháp phụ thuộc quy tắc hoà khi chọn w), so sánh hai quy tắc:
  "first"   – như Cổng 0 đã báo cáo (hoà → w = 0, tức bỏ nguồn)
  "neutral" – hoà → w gần 0,5 nhất (g0_pair.py --tie neutral)
trên cùng 30 lần chia, cùng baseline chỉ dùng đích mạnh nhất (gồm TabPFN v2) và cùng tiêu chí GO của Cổng 0
(Δ ≥ 0,02 và CI hiệu chỉnh không chứa 0, k ∈ {10, 20, 50}), kèm p sau Holm trong họ 8 phương pháp chuyển giao × 3 k
của mỗi chiều. Mọi phương pháp khác không đổi giữa hai quy tắc. Không đổi kết luận đã chốt: đây là phân tích độ nhạy.
Ghi results/g0_tie_neutral/g0_tie_neutral_so_sanh.csv và g0_tie_neutral_ket_luan.csv.
Mã do Claude (Anthropic) sinh, khai báo ở docs/khai_bao_cong_cu.md.
"""
import glob
import pandas as pd
from g0_decision import corrected, holm, KS_DECIDE, TR

FOLDERS = {"AB": "results/g0_23", "AC": "results/g0_AC", "AD": "results/g0_AD"}
TIE_DEP = ["RANKAVG", "RANKAVG_RF"]


def load(folder):
    fs = sorted(glob.glob(f"{folder}/results_g0_23_*.csv") + glob.glob(f"{folder}/results_g0_[A-D][A-D]_*.csv"))
    r = pd.concat([pd.read_csv(f) for f in fs], ignore_index=True)
    r = r[~r.method.astype(str).str.startswith("TBHTL")]
    r["k"] = r["k"].astype(str)
    return r


def go_table(r, pair, rule):
    rows = []
    for tgt, rt in r.groupby("target"):
        zs = rt[rt.method == "ZS"].set_index("rep").pr_auc
        for k in KS_DECIDE:
            rk = rt[rt.k == k]
            means = rk[rk.family == "target_only"].groupby("method").pr_auc.mean()
            best = means.idxmax(); base = rk[rk.method == best].set_index("rep").pr_auc
            for m in TR:
                cand = zs if m == "ZS" else rk[rk.method == m].set_index("rep").pr_auc
                if not len(cand):
                    continue
                d = (cand - base).dropna()
                mean, lo, hi, p = corrected(d.to_numpy())
                rows.append(dict(cap=pair, dich=tgt, quy_tac_hoa=rule, k=int(k), method=m, best_target_only=best,
                                 method_pr=cand.mean(), delta=mean, ci_lo=lo, ci_hi=hi, p_corr=p, n_rep=len(d)))
    T = pd.DataFrame(rows)
    T["p_holm"] = T.groupby("dich").p_corr.transform(lambda p: holm(p.to_numpy()))
    T["dat_GO"] = (T.delta >= 0.02) & (T.ci_lo > 0)
    return T


def check():
    """Review 27/10 (V1): với kết quả gốc (quy tắc first), bảng phải trùng g0_kiem_dinh_GO.csv đã công bố của từng cặp."""
    cols = ["delta", "ci_lo", "ci_hi", "p_corr", "p_holm"]
    ok = True
    for pair, folder in FOLDERS.items():
        T = go_table(load(folder), pair, "first").rename(columns={"dich": "target"})
        P = pd.read_csv(f"{folder}/g0_kiem_dinh_GO.csv")
        m = T.merge(P, on=["target", "k", "method"], suffixes=("", "_cb"))
        dmax = max((m[c] - m[c + "_cb"]).abs().max() for c in cols)
        same_go = bool((m.dat_GO == m.dat_GO_cb).all()) if "dat_GO_cb" in m else True
        same_best = bool((m.best_target_only == m.best_target_only_cb).all())
        good = len(m) == len(P) == len(T) and dmax < 1e-9 and same_go and same_best
        ok &= good
        print(f"{pair}: {len(m)}/{len(P)} dòng khớp, lệch tối đa {dmax:.1e}, dat_GO trùng: {same_go}, baseline trùng: {same_best} -> {'ĐẠT' if good else 'LỖI'}")
    print("KẾT QUẢ:", "ĐẠT" if ok else "LỖI")
    return ok


def main():
    out = []
    for pair, folder in FOLDERS.items():
        r = load(folder)
        tn = pd.concat([pd.read_csv(f) for f in glob.glob(f"results/g0_tie_neutral/{pair}/results_g0_*_tie_neutral.csv")])
        tn["k"] = tn["k"].astype(str)
        r_neu = pd.concat([r[~r.method.isin(TIE_DEP)], tn], ignore_index=True)
        out += [go_table(r, pair, "first"), go_table(r_neu, pair, "neutral")]
    T = pd.concat(out, ignore_index=True)
    S = T[T.method.isin(TIE_DEP)].pivot_table(index=["cap", "dich", "method", "k"], columns="quy_tac_hoa",
                                              values=["method_pr", "delta", "ci_lo", "ci_hi", "p_holm"]).round(4)
    S.columns = [f"{a}_{b}" for a, b in S.columns]
    S.to_csv("results/g0_tie_neutral/g0_tie_neutral_so_sanh.csv")
    K = T.groupby(["cap", "dich", "quy_tac_hoa"]).dat_GO.any().unstack("quy_tac_hoa").replace({True: "GO", False: "PIVOT"})
    K.to_csv("results/g0_tie_neutral/g0_tie_neutral_ket_luan.csv")
    pd.set_option("display.width", 220)
    print("Kết luận Cổng 0 theo hai quy tắc hoà (tiêu chí GO của Cổng 0):"); print(K.to_string())
    print("\nRANKAVG, RANKAVG-RF: Δ so với baseline đích mạnh nhất [CI 95%]:")
    print(S[["delta_first", "delta_neutral", "ci_lo_neutral", "ci_hi_neutral", "p_holm_neutral"]].to_string())


if __name__ == "__main__":
    import sys
    check() if "--check" in sys.argv else main()
