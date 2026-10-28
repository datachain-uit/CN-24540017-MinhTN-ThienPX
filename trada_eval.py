"""
trada_eval.py — Phân tích họ so sánh TrAdaBoost theo prereg/prereg_trada.yaml.

    python trada_eval.py                    # results/trada + Cổng 0 (g0_23, g0_AC) + K2 sau sửa đổi (k2_v2)
    python trada_eval.py --muc-san          # chỉ đọc file xáo trộn nhãn của TRADA (kiểm tra mức sàn)

Phép chính – họ Holm riêng gồm 18 phép: Δ = PR-AUC(TRADA) − PR-AUC(baseline chỉ dùng đích mạnh nhất cùng k),
k ∈ {10, 20, 50}, cho 4 chiều Cổng 0 (A→B, B→A, A→C, C→A) và 2 tổ hợp K2-L0 (đích A, nguồn B, C).
“Mạnh nhất” = PR-AUC trung bình cao nhất ở k đó trong các baseline chỉ dùng đích có trong file kết quả
(kể cả TabPFN v2). TRADA đạt khi Δ ≥ 0,02 và p sau Holm < 0,05. Họ Holm đã chốt của Cổng 0 và K2 giữ nguyên.
Phụ (Holm riêng trong nhóm phụ): TRADA − RF, TRADA − LR, TRADA − ZS theo PR-AUC, k ∈ {10, 20, 50, 100}.
Mô tả: TRADA − RF theo F1 (ngưỡng theo tỷ lệ dương của k mẫu) khi baseline có cột f1; TRADA_BAL (độ nhạy).
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


def read(fs):
    return pd.concat([pd.read_csv(f, dtype={"k": str}) for f in fs], ignore_index=True)


def baselines():
    """Bảng dài: setting, target, source, method, k, rep, pr_auc, (f1) – trung bình theo lần rút ở K2."""
    out = []
    for pair, d in G0_DIR.items():
        fs = [f for f in glob.glob(f"{d}/results_g0_*.csv") if "_tie_" not in f and "tbhtl" not in f]
        r = read(fs)
        r = r[~r.method.astype(str).str.startswith("TBHTL")]
        dom = sorted(set(pair))
        r["source"] = r.target.map({dom[0]: dom[1], dom[1]: dom[0]})
        r["setting"] = "g0"
        out.append(r)
    fs = [f for f in glob.glob("results/k2_v2/results_k2_*.csv") if "xao_tron" not in f]
    if fs:
        r = read(fs)
        r = r[(r.level == "L0") & r.source.isin(["B", "C"])]
        r["setting"] = "k2l0"
        out.append(r)
    else:
        print("CHÚ Ý: chưa có results/k2_v2 – bỏ qua K2-L0")
    b = pd.concat(out, ignore_index=True)
    cols = ["setting", "target", "source", "method", "k", "rep"]
    val = [c for c in ("pr_auc", "f1") if c in b.columns]
    return b.groupby(cols)[val].mean().reset_index()


def main(muc_san=False):
    fs = sorted(glob.glob("results/trada/results_trada_*.csv"))
    fs = [f for f in fs if ("xao_tron" in f) == muc_san and "kiem_tra_zs" not in f]
    t = read(fs)
    print("Tệp TRADA:", [f.split("/")[-1] for f in fs])
    if muc_san:
        g = t.groupby(["setting", "target", "source", "method"]).agg(pr_auc=("pr_auc", "mean"), ty_le_duong=("pos_rate_test", "mean"))
        print(g.round(3).to_string())
        return
    t = t.groupby(["setting", "target", "source", "method", "k", "rep"])[["pr_auc", "f1"]].mean().reset_index()
    b = baselines()
    allr = pd.concat([b, t], ignore_index=True)
    rows = []
    for (st, tg, sr), g in allr.groupby(["setting", "target", "source"]):
        T = g.set_index(["method", "k", "rep"]).sort_index()
        has_tabpfn = (g.method == "TabPFN").any()
        for k in ["10", "20", "50", "100"]:
            if ("TRADA", k) not in T.index.droplevel("rep"):
                continue
            pr = T.pr_auc.unstack("rep")
            cand = {m: pr.loc[(m, k)].mean() for m in TO if (m, k) in pr.index}
            best = max(cand, key=cand.get)
            zs = pr.loc[("ZS", "zero")] if ("ZS", "zero") in pr.index else None
            tests = [("chinh", "TRADA − đích mạnh nhất", pr.loc[("TRADA", k)], pr.loc[(best, k)], best),
                     ("do_nhay", "TRADA_BAL − đích mạnh nhất", pr.loc[("TRADA_BAL", k)], pr.loc[(best, k)], best)]
            for m in ("RF", "LR"):
                if (m, k) in pr.index:
                    tests.append(("phu", f"TRADA − {m}", pr.loc[("TRADA", k)], pr.loc[(m, k)], m))
            if zs is not None:
                tests.append(("phu", "TRADA − ZS", pr.loc[("TRADA", k)], zs, "ZS"))
            if "f1" in T.columns and ("RF", k) in T.index.droplevel("rep"):
                f1 = T.f1.unstack("rep")
                if f1.loc[("RF", k)].notna().all():
                    tests.append(("mo_ta_F1", "F1: TRADA − RF", f1.loc[("TRADA", k)], f1.loc[("RF", k)], "RF"))
            for ho, name, xa, xb, vs in tests:
                d = (xa - xb).dropna()                     # bắt cặp theo lần chia có đủ hai phương pháp
                mean, lo, hi, p = corrected(d)
                rows.append(dict(setting=st, target=tg, source=sr, k=int(k), ho=ho, so_sanh=name, so_voi=vs,
                                 a=xa[d.index].mean(), b=xb[d.index].mean(), delta=mean, ci_lo=lo, ci_hi=hi, p=p, n=len(d),
                                 co_TabPFN=has_tabpfn))
    D = pd.DataFrame(rows)
    prim = (D.ho == "chinh") & (D.k <= 50)
    D.loc[prim, "p_holm"] = holm(D.loc[prim, "p"].to_numpy())
    D["dat"] = prim & (D.delta >= 0.02) & (D.p_holm < 0.05)
    sec = D.ho == "phu"
    D.loc[sec, "p_holm_phu"] = holm(D.loc[sec, "p"].to_numpy())
    pd.set_option("display.width", 230); pd.set_option("display.max_rows", 300)
    print(f"PHÉP CHÍNH: {int(prim.sum())} phép (dự kiến 18); số phép đạt: {int(D.dat.sum())}")
    if not D.loc[prim, "co_TabPFN"].all():
        print("CHÚ Ý: có tổ hợp chưa có TabPFN v2 trong baseline – kết luận là SƠ BỘ")
    show = ["setting", "target", "source", "k", "so_sanh", "so_voi", "a", "b", "delta", "ci_lo", "ci_hi", "p", "p_holm", "dat"]
    print(D.loc[prim, show].round(4).to_string(index=False))
    D.to_csv("results/trada/trada_kiem_dinh.csv", index=False)
    print("Đã lưu results/trada/trada_kiem_dinh.csv")


if __name__ == "__main__":
    main("--muc-san" in sys.argv)
