"""
c1_do_nhay_eval.py — Phân tích độ nhạy C1 theo prereg/prereg_c1_do_nhay.yaml.

    python c1_do_nhay_eval.py               # đọc results/c1_do_nhay/*_cpu.csv, Cổng 0 (g0_23, g0_AC), K2 (k2_v2)
    python c1_do_nhay_eval.py --muc-san     # chỉ đọc file xáo trộn nhãn

Phép chính (họ Holm 4 phép): Δ = PR-AUC(ZS_MID) − PR-AUC(ZS_C1), bắt cặp theo lần chia, cho 4 chiều Cổng 0
(A→B, B→A, A→C, C→A); CI 95% hiệu chỉnh Nadeau–Bengio (0,25). Kết luận “C1 ảnh hưởng đáng kể” khi |Δ| ≥ 0,02
và p sau Holm < 0,05.
Phụ (mô tả, không đổi kết luận đã chốt): ZS_MID − baseline chỉ dùng đích mạnh nhất ở k ∈ {10, 20, 50}, cho
Cổng 0 (4 chiều) và K2-L0 (đích A, nguồn B và C); Holm trong từng thiết lập; kèm cùng phép với ZS_C1 để đối chiếu.
"""
import glob, sys
import numpy as np
import pandas as pd
from scipy import stats

RATIO = 0.25
TO = ["LR", "RF", "XGB", "XGB_SMALLK", "CAT", "STACK", "LightGBM", "AdaBoost", "TabPFN"]
G0_DIR = {"AB": "results/g0_23", "AC": "results/g0_AC"}


def corrected(d):
    d = np.asarray(d, float); J = len(d); se = np.sqrt(1 / J + RATIO) * d.std(ddof=1)
    p = 2 * stats.t.sf(abs(d.mean() / se), J - 1) if se > 0 else np.nan
    h = stats.t.ppf(.975, J - 1) * se
    return d.mean(), d.mean() - h, d.mean() + h, p


def holm(p):
    p = np.asarray(p, float); o = np.argsort(p); m = len(p); adj = np.empty(m); run = 0
    for i, k in enumerate(o):
        run = max(run, (m - i) * p[k]); adj[k] = min(1, run)
    return adj


def target_only():
    """PR-AUC theo (thiết lập, đích, nguồn, phương pháp, k, lần chia) của baseline chỉ dùng đích."""
    out = []
    for pair, d in G0_DIR.items():
        fs = [f for f in glob.glob(f"{d}/results_g0_*.csv") if "_tie_" not in f and "tbhtl" not in f]
        r = pd.concat([pd.read_csv(f, dtype={"k": str}) for f in fs])
        r = r[r.method.isin(TO)]
        dom = sorted(set(pair))
        r["source"] = r.target.map({dom[0]: dom[1], dom[1]: dom[0]}); r["setting"] = "Cổng 0"
        out.append(r[["setting", "target", "source", "method", "k", "rep", "pr_auc"]])
    fs = [f for f in glob.glob("results/k2_v2/results_k2_*.csv") if "xao_tron" not in f]
    if fs:
        r = pd.concat([pd.read_csv(f, dtype={"k": str}) for f in fs])
        r = r[(r.level == "L0") & r.source.isin(["B", "C"]) & r.method.isin(TO)]
        r = r.groupby(["target", "source", "method", "k", "rep"]).pr_auc.mean().reset_index()   # TB theo lần rút
        r["setting"] = "K2-L0"
        out.append(r)
    return pd.concat(out, ignore_index=True)


def main(muc_san=False):
    fs = sorted(glob.glob("results/c1_do_nhay/results_c1_*.csv"))
    fs = [f for f in fs if ("xao_tron" in f) == muc_san and "kiem_tra_zs" not in f]
    z = pd.concat([pd.read_csv(f) for f in fs], ignore_index=True)
    print("Tệp:", [f.split("/")[-1] for f in fs])
    if muc_san:
        print(z.groupby(["source", "target", "method"]).agg(pr_auc=("pr_auc", "mean"), ty_le_duong=("pos_rate_test", "mean")).round(3))
        return
    W = z.pivot_table(index=["source", "target", "rep"], columns="method", values="pr_auc")
    rows = []
    for (s, t), g in W.groupby(level=[0, 1]):
        mean, lo, hi, p = corrected(g["ZS_MID"] - g["ZS_C1"])
        rho = z[(z.source == s) & (z.target == t) & (z.method == "ZS_MID")].spearman_c1_mid.mean()
        rows.append(dict(chieu=f"{s}→{t}", zs_c1=g["ZS_C1"].mean(), zs_mid=g["ZS_MID"].mean(), delta=mean,
                         ci_lo=lo, ci_hi=hi, p=p, spearman_tb=rho))
    M = pd.DataFrame(rows); M["p_holm"] = holm(M.p.to_numpy())
    M["anh_huong_dang_ke"] = (M.delta.abs() >= 0.02) & (M.p_holm < 0.05)
    pd.set_option("display.width", 220)
    print("PHÉP CHÍNH – ZS_MID − ZS_C1:"); print(M.round(4).to_string(index=False))
    T = target_only(); sec = []
    for setting, tg, sr in [("Cổng 0", t, s) for s, t in W.index.droplevel(2).unique()] + [("K2-L0", "A", "B"), ("K2-L0", "A", "C")]:
        b = T[(T.setting == setting) & (T.target == tg) & (T.source == sr)]
        if b.empty:
            continue
        B_ = b.pivot_table(index=["method", "k"], columns="rep", values="pr_auc")
        has_tabpfn = (b.method == "TabPFN").any()
        part = []
        for k in ["10", "20", "50"]:
            cand = {m: B_.loc[(m, k)].mean() for m in TO if (m, k) in B_.index}
            best = max(cand, key=cand.get)
            for zm in ["ZS_MID", "ZS_C1"]:
                zz = W.loc[(sr, tg)][zm]
                dd = (zz - B_.loc[(best, k)]).dropna()
                mean, lo, hi, p = corrected(dd)
                part.append(dict(thiet_lap=setting, chieu=f"{sr}→{tg}", k=int(k), zs=zm, so_voi=best, delta=mean,
                                 ci_lo=lo, ci_hi=hi, p=p, co_TabPFN=has_tabpfn))
        P_ = pd.DataFrame(part)
        for zm in ["ZS_MID", "ZS_C1"]:
            idx = P_.zs == zm
            P_.loc[idx, "p_holm"] = holm(P_.loc[idx, "p"].to_numpy())
        sec.append(P_)
    S = pd.concat(sec, ignore_index=True)
    S["dat_nhu_GO"] = (S.delta >= 0.02) & (S.p_holm < 0.05)
    print("\nPHỤ (mô tả) – ZS − baseline chỉ dùng đích mạnh nhất:"); print(S.round(4).to_string(index=False))
    M.to_csv("results/c1_do_nhay/c1_phep_chinh.csv", index=False)
    S.to_csv("results/c1_do_nhay/c1_phep_phu.csv", index=False)


if __name__ == "__main__":
    main("--muc-san" in sys.argv)
