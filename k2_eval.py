"""
k2_eval.py — Phân tích K2 theo tiền đăng ký (prereg/prereg_k2.yaml).

    python k2_eval.py results/k2

Mỗi (nguồn, mức lược đồ, phương pháp, k, lần chia): lấy trung bình trên M lần rút trước khi kiểm định (R = 30 hiệu bắt cặp).
  (1) GO   : mỗi phương pháp chuyển giao − baseline chỉ dùng đích MẠNH NHẤT (chọn sau khi xem; kể cả XGB_SMALLK và TabPFN v2
             nếu đã có) ở k ≤ 50: Δ ≥ 0,02 và CI hiệu chỉnh không chứa 0; cộng điều kiện Δ trung bình ≥ −0,01 ở k = 100.
  (2) báo cáo: mỗi phương pháp chuyển giao − baseline đích CHỌN TRƯỚC (PRESEL, M1).
  (3) RQ6  : TB-HTL v0 − baseline chuyển giao tốt nhất (không tính các biến thể TB-HTL); TB-HTL − từng ablation; − bản xáo trộn.
  (4) H5   : lợi ích lớn nhất theo mức lược đồ L0 → L1 (→ L2 = Cổng 0, chỉ để đối chiếu).
CI 95% hiệu chỉnh Nadeau–Bengio (0,25); Holm trong mỗi họ (nguồn × mức × họ so sánh); MDE (power 80%).
"""
import glob, os, sys
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

RATIO = 0.25
KS = ["10", "20", "50", "100"]
TO = ["LR", "RF", "XGB", "XGB_SMALLK", "CAT", "STACK", "LightGBM", "AdaBoost", "TabPFN"]
TR = ["ZS", "STK_LR", "STK_XGB", "OFF_XGB", "DAUME_LR", "RANKAVG", "ANCHOR_LR", "RANKAVG_RF", "TBHTL"]
TB_ABL = ["TBHTL_mC1", "TBHTL_mC2", "TBHTL_mC4", "TBHTL_SHUF"]
SRC_NAME = {"B": "Job Change → IBM", "C": "HR 14.999 → IBM"}


def corrected(d):
    d = np.asarray(d, float); J = len(d); se = np.sqrt(1 / J + RATIO) * d.std(ddof=1)
    t975, t80 = stats.t.ppf(.975, J - 1), stats.t.ppf(.80, J - 1)
    p = 2 * stats.t.sf(abs(d.mean() / se), J - 1) if se > 0 else np.nan
    return d.mean(), d.mean() - t975 * se, d.mean() + t975 * se, p, (t975 + t80) * se


def holm(p):
    p = np.asarray(p, float); o = np.argsort(p); m = len(p); adj = np.empty(m); run = 0
    for i, k in enumerate(o):
        run = max(run, (m - i) * p[k]); adj[k] = min(1, run)
    return adj


def load(folder):
    fs = sorted(glob.glob(f"{folder}/results_k2_*.csv"))
    fs = [f for f in fs if "xao_tron" not in f]
    r = pd.concat([pd.read_csv(f, dtype={"k": str}) for f in fs], ignore_index=True)
    r = r.drop_duplicates(subset=["source", "level", "group", "method", "k", "rep", "draw"], keep="last")
    return r


def combo_table(r, src, lv):
    """Bảng PR-AUC theo lần chia (trung bình M lần rút) cho một tổ hợp (nguồn, mức)."""
    grp = f"L0_{src}" if lv == "L0" else lv
    to = r[(r.group == grp) & r.method.isin(TO + ["PRESEL"])]
    tr = r[(r.source == src) & (r.level == lv) & ~r.method.isin(TO + ["PRESEL"])]
    x = pd.concat([to, tr])
    return x.groupby(["method", "k", "rep"])[["pr_auc", "auc_roc", "brier", "ece"]].mean()


def main(folder):
    r = load(folder)
    R = r.rep.nunique(); M = r.draw.nunique()
    combos = sorted({(s, l) for s, l in r[r.method == "ZS"][["source", "level"]].itertuples(index=False)},
                    key=lambda t: (t[0], ["L0", "L1", "L1_noAge"].index(t[1])))
    out, curve_rows = [], []
    for src, lv in combos:
        T = combo_table(r, src, lv)
        pr = T.pr_auc.unstack("rep")
        get = lambda m, k: pr.loc[(m, "zero" if m == "ZS" else k)] if (m, "zero" if m == "ZS" else k) in pr.index else None
        for k in KS:
            cand = {m: get(m, k).mean() for m in TO if get(m, k) is not None}
            best_to = max(cand, key=cand.get)
            trs = {m: get(m, k).mean() for m in TR if get(m, k) is not None and m != "TBHTL"}
            best_tr = max(trs, key=trs.get)
            fams = [("GO: chuyển giao − đích mạnh nhất", m, best_to) for m in TR] + \
                   [("Báo cáo: chuyển giao − đích chọn trước", m, "PRESEL") for m in TR] + \
                   [("RQ6: TB-HTL − chuyển giao tốt nhất", "TBHTL", best_tr)] + \
                   [("RQ6: ablation TB-HTL", "TBHTL", m) for m in TB_ABL + ["ANCHOR_LR"]]
            for fam, a_, b_ in fams:
                xa, xb = get(a_, k), get(b_, k)
                if xa is None or xb is None:
                    continue
                d = (xa - xb).dropna()
                mean, lo, hi, p, mde = corrected(d)
                out.append(dict(source=src, level=lv, k=int(k), ho=fam, method=a_, so_voi=b_, pr_method=xa.mean(), pr_so_voi=xb.mean(),
                                delta=mean, ci_lo=lo, ci_hi=hi, p_corrected=p, MDE80=mde, nua_do_rong=(hi - lo) / 2, n=len(d)))
            for m in TO + ["PRESEL"] + TR + TB_ABL:
                x = get(m, k)
                if x is not None:
                    curve_rows.append(dict(source=src, level=lv, k=int(k), method=m, pr_auc=x.mean(),
                                           auc_roc=T.auc_roc.unstack("rep").loc[(m, "zero" if m == "ZS" else k)].mean(),
                                           brier=T.brier.unstack("rep").loc[(m, "zero" if m == "ZS" else k)].mean(),
                                           ece=T.ece.unstack("rep").loc[(m, "zero" if m == "ZS" else k)].mean()))
    D = pd.DataFrame(out)
    D["p_holm"] = np.nan
    for _, idx in D.groupby(["source", "level", "ho"]).groups.items():
        D.loc[idx, "p_holm"] = holm(D.loc[idx, "p_corrected"].to_numpy())
    D["dat_GO_k"] = D.ho.str.startswith("GO") & (D.k <= 50) & (D.delta >= 0.02) & (D.ci_lo > 0)
    C = pd.DataFrame(curve_rows)
    D.to_csv(f"{folder}/k2_kiem_dinh.csv", index=False); C.to_csv(f"{folder}/k2_duong_cong.csv", index=False)

    # Kết luận GO theo (nguồn, mức), kể cả điều kiện chuyển giao âm ở k = 100
    concl = []
    for (src, lv), g in D[D.ho.str.startswith("GO")].groupby(["source", "level"], sort=False):
        ok = []
        for m in TR:
            gm = g[g.method == m]
            hit = gm[(gm.k <= 50) & gm.dat_GO_k]
            neg100 = gm[gm.k == 100].delta
            if len(hit) and (len(neg100) == 0 or neg100.iloc[0] >= -0.01):
                ok.append(f"{m}@k={','.join(map(str, hit.k))}")
        best = g[g.k <= 50].loc[g[g.k <= 50].delta.idxmax()]
        concl.append(dict(source=src, level=lv, ket_luan="GO" if ok else "PIVOT", phuong_phap_GO="; ".join(ok),
                          delta_tot_nhat_k50=f"{best.method}@k={best.k}: {best.delta:+.3f} [{best.ci_lo:+.3f}; {best.ci_hi:+.3f}]",
                          MDE80_trung_vi=g[g.k <= 50].MDE80.median()))
    K = pd.DataFrame(concl); K.to_csv(f"{folder}/k2_ket_luan.csv", index=False)

    # λ* của TB-HTL theo k (C4) và lựa chọn của PRESEL
    lam = r[r.method == "TBHTL"].groupby(["source", "level", "k"]).lam.median().unstack("k")[KS]
    lam.to_csv(f"{folder}/k2_tbhtl_lambda.csv")
    pres = r[r.method == "PRESEL"].groupby(["group", "k"]).chosen.agg(lambda s: s.value_counts().head(3).to_dict())
    pres.to_csv(f"{folder}/k2_presel_chon.csv")

    pd.set_option("display.width", 250); pd.set_option("display.max_rows", 500)
    print(f"R = {R} lần chia, M = {M} lần rút; tổ hợp: {combos}\n")
    print(K.to_string(index=False))
    print("\nPR-AUC trung bình:")
    show = C.pivot_table(index=["source", "level", "method"], columns="k", values="pr_auc", sort=False)
    print(show.round(3).to_string())
    print("\nλ* trung vị của TB-HTL:"); print(lam.to_string())
    print("\nPRESEL chọn:"); print(pres.to_string())

    # Hình: đường cong PR-AUC theo k, mỗi ô một (nguồn, mức)
    fig, axs = plt.subplots(len({c[0] for c in combos}), 3, figsize=(13, 7.5), sharey=False, constrained_layout=True, squeeze=False)
    for i, src in enumerate(sorted({c[0] for c in combos})):
        for j, lv in enumerate(["L0", "L1", "L1_noAge"]):
            ax = axs[i, j]; g = C[(C.source == src) & (C.level == lv)]
            if not len(g):
                ax.axis("off"); continue
            xs = np.arange(len(KS)); val = lambda m: [g[(g.method == m) & (g.k == int(k))].pr_auc.mean() for k in KS]
            to_best = [g[(g.k == int(k)) & g.method.isin(TO)].pr_auc.max() for k in KS]
            tr_best = [g[(g.k == int(k)) & g.method.isin(TR[1:-1])].pr_auc.max() for k in KS]
            ax.plot(xs, to_best, "k--", marker="o", label="Đích mạnh nhất (sau khi xem)")
            ax.plot(xs, val("PRESEL"), color="#7f7f7f", marker="s", label="Đích chọn trước (PRESEL)")
            ax.plot(xs, tr_best, color="#2a78d6", marker="D", label="Chuyển giao đơn giản tốt nhất")
            ax.plot(xs, val("TBHTL"), color="#e34948", marker="^", lw=2, label="TB-HTL v0")
            zs = g[g.method == "ZS"].pr_auc.mean()
            ax.axhline(zs, color="#e87ba4", ls=":", label="Zero-shot")
            ax.set_xticks(xs); ax.set_xticklabels(KS); ax.grid(axis="y", color="#e5e5e5"); ax.spines[["top", "right"]].set_visible(False)
            ax.set_title(f"{SRC_NAME[src]} – {lv}", loc="left", fontsize=10, fontweight="bold")
            if j == 0:
                ax.set_ylabel("PR-AUC (30 lần chia × 5 lần rút)")
            if i == len(axs) - 1:
                ax.set_xlabel("k")
    h, l = axs[0, 0].get_legend_handles_labels()
    fig.legend(h, l, loc="upper center", ncol=5, frameon=False, bbox_to_anchor=(.5, 1.06), fontsize=8.5)
    fig.savefig(f"{folder}/k2_hinh_duong_cong.png", dpi=200, bbox_inches="tight", facecolor="white")
    print(f"\nĐã lưu: k2_kiem_dinh.csv, k2_duong_cong.csv, k2_ket_luan.csv, k2_tbhtl_lambda.csv, k2_presel_chon.csv, k2_hinh_duong_cong.png")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "results/k2")
