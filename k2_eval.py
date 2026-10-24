"""
k2_eval.py — Phân tích K2 theo tiền đăng ký (prereg/prereg_k2.yaml).

    python k2_eval.py results/k2_v2        # lần chạy sau sửa đổi 24/10 (chính)
    python k2_eval.py results/k2           # lần chạy theo bản chốt 23/10 (giữ để đối chiếu, deviations.md mục 9)

Mỗi (nguồn, mức lược đồ, phương pháp, k, lần chia): lấy trung bình trên M lần rút trước khi kiểm định (R = 30 hiệu bắt cặp).
  (1) GO   : mỗi phương pháp chuyển giao − baseline chỉ dùng đích MẠNH NHẤT (chọn sau khi xem; kể cả XGB_SMALLK và TabPFN v2
             nếu đã có) ở k ≤ 50: Δ ≥ 0,02 và p sau Holm < 0,05, họ Holm = mọi phương pháp chuyển giao × k ≤ 50 của một
             (nguồn, mức) (sửa đổi V2, review 24/10); cộng điều kiện Δ trung bình ≥ −0,01 ở k = 100. Chưa có TabPFN v2 → “sơ bộ”.
  (2) báo cáo: mỗi phương pháp chuyển giao − baseline đích CHỌN TRƯỚC (PRESEL, M1).
  (3) RQ6  : TB-HTL v0 − baseline chuyển giao tốt nhất (không tính các biến thể TB-HTL); TB-HTL − từng ablation; − bản xáo trộn.
  (4) H5   : lợi ích = PR-AUC(phương pháp) − PR-AUC(PRESEL) cùng mức; hiệu L0 − L2 (chính), L0 − L1_core, L1_core − L2
             (xu hướng) cho TBHTL và RANKAVG_RF ở k ∈ {10, 20, 50}; Holm riêng cho từng loại (V3, review 24/10).
  (5) Tỷ lệ hoà khi chọn w (RANKAVG, RANKAVG_RF) và λ_s (TBHTL), phân bố w, λ_s theo k (V1); F1, G-Mean mô tả (V7).
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


LEVELS = ["L0", "L1", "L1_noAge", "L1_core", "L2"]


def combo_table(r, src, lv):
    """Bảng PR-AUC theo lần chia (trung bình M lần rút) cho một tổ hợp (nguồn, mức)."""
    grp = {"L0": f"L0_{src}", "L1_core": "L1"}.get(lv, lv)            # L1_core dùng phần chỉ dùng đích của L1
    to = r[(r.group == grp) & r.method.isin(TO + ["PRESEL"])]
    tr = r[(r.source == src) & (r.level == lv) & ~r.method.isin(TO + ["PRESEL"])]
    x = pd.concat([to, tr])
    return x.groupby(["method", "k", "rep"])[["pr_auc", "auc_roc", "brier", "ece", "f1", "gmean"]].mean()


def main(folder):
    r = load(folder)
    for c in ["brier", "ece", "f1", "gmean"]:          # lần chạy 23/10 chưa có F1, G-Mean
        if c not in r:
            r[c] = np.nan
    R = r.rep.nunique(); M = r.draw.nunique()
    combos = sorted({(s, l) for s, l in r[r.method == "ZS"][["source", "level"]].itertuples(index=False)},
                    key=lambda t: (t[0], LEVELS.index(t[1])))
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
                    kk = (m, "zero" if m == "ZS" else k)
                    curve_rows.append(dict(source=src, level=lv, k=int(k), method=m, pr_auc=x.mean(),
                                           **{c: T[c].unstack("rep").loc[kk].mean() for c in ["auc_roc", "brier", "ece", "f1", "gmean"]}))
    D = pd.DataFrame(out)
    D["p_holm"] = np.nan
    for _, idx in D.groupby(["source", "level", "ho"]).groups.items():
        D.loc[idx, "p_holm"] = holm(D.loc[idx, "p_corrected"].to_numpy())
    # GO: Δ ≥ 0,02 và p sau Holm < 0,05; họ Holm = mọi phương pháp chuyển giao × k ≤ 50 của một (nguồn, mức)
    go = D.ho.str.startswith("GO") & (D.k <= 50)
    D["p_holm_GO"] = np.nan
    for _, idx in D[go].groupby(["source", "level"]).groups.items():
        D.loc[idx, "p_holm_GO"] = holm(D.loc[idx, "p_corrected"].to_numpy())
    D["dat_GO_k"] = go & (D.delta >= 0.02) & (D.p_holm_GO < 0.05)
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
                          trang_thai="chính thức" if (r.method == "TabPFN").any() else "sơ bộ – chưa có TabPFN v2",
                          delta_tot_nhat_k50=f"{best.method}@k={best.k}: {best.delta:+.3f} [{best.ci_lo:+.3f}; {best.ci_hi:+.3f}]",
                          MDE80_trung_vi=g[g.k <= 50].MDE80.median()))
    K = pd.DataFrame(concl); K.to_csv(f"{folder}/k2_ket_luan.csv", index=False)

    # H5 (chốt trước khi chạy): Δ_mức = PR-AUC(phương pháp) − PR-AUC(PRESEL) cùng mức, bắt cặp theo lần chia;
    # so L0 với L2 (chính) và L0 – L1_core – L2 (xu hướng, giữ nguyên tập khái niệm chung); Holm theo từng loại so sánh
    h5 = []
    have = {c for c in combos}
    for src in sorted({c[0] for c in combos}):
        for meth in ["TBHTL", "RANKAVG_RF"]:
            for k in ["10", "20", "50"]:
                for a_, b_ in [("L0", "L2"), ("L0", "L1_core"), ("L1_core", "L2")]:
                    if (src, a_) not in have or (src, b_) not in have:
                        continue
                    da = combo_table(r, src, a_).pr_auc.unstack("rep")
                    db = combo_table(r, src, b_).pr_auc.unstack("rep")
                    d = ((da.loc[(meth, k)] - da.loc[("PRESEL", k)]) - (db.loc[(meth, k)] - db.loc[("PRESEL", k)])).dropna()
                    mean, lo, hi, p, mde = corrected(d)
                    h5.append(dict(source=src, method=meth, k=int(k), so_sanh=f"{a_} − {b_}", delta_loi_ich=mean,
                                   ci_lo=lo, ci_hi=hi, p_corrected=p, MDE80=mde, n=len(d)))
    if h5:
        H = pd.DataFrame(h5)                                   # Holm riêng cho từng loại so sánh; L0 − L2 là phép chính
        H["p_holm"] = H.groupby("so_sanh").p_corrected.transform(lambda p: holm(p.to_numpy()))
        H["ung_ho_H5"] = (H.so_sanh == "L0 − L2") & (H.delta_loi_ich > 0) & (H.p_holm < 0.05)
        H.to_csv(f"{folder}/k2_h5.csv", index=False)
        print("\nH5 – chênh lệch lợi ích giữa các mức lược đồ:"); print(H.round(3).to_string(index=False))

    # λ* của TB-HTL theo k (C4) và lựa chọn của PRESEL
    lam = r[r.method == "TBHTL"].groupby(["source", "level", "k"]).lam.median().unstack("k")[KS]
    lam.to_csv(f"{folder}/k2_tbhtl_lambda.csv")
    pres = r[r.method == "PRESEL"].groupby(["group", "k"]).chosen.agg(lambda s: s.value_counts().head(3).to_dict())
    pres.to_csv(f"{folder}/k2_presel_chon.csv")

    # (5) Quy tắc hoà (V1): tỷ lệ hoà và phân bố giá trị được chọn theo k
    hoa = None
    if "n_hoa" in r:
        x = r[r.method.isin(["RANKAVG", "RANKAVG_RF", "TBHTL"]) & (r.k != "zero")].copy()
        x["tham_so"] = np.where(x.method == "TBHTL", x.lam, x.w)
        x["hoa"] = x.n_hoa > 1
        hoa = x.groupby(["source", "level", "method", "k"]).agg(n=("rep", "size"), ty_le_hoa=("hoa", "mean"),
                                                                 trung_vi=("tham_so", "median")).reset_index()
        dist = x.groupby(["source", "level", "method", "k"]).tham_so.value_counts(normalize=True).unstack(fill_value=0)
        dist.columns = [f"ty_le_{c:g}" for c in dist.columns]
        hoa = hoa.merge(dist.reset_index(), on=["source", "level", "method", "k"])
        hoa["k"] = hoa.k.astype(int); hoa = hoa.sort_values(["source", "level", "method", "k"])
        hoa.to_csv(f"{folder}/k2_hoa.csv", index=False)

    pd.set_option("display.width", 250); pd.set_option("display.max_rows", 500)
    print(f"R = {R} lần chia, M = {M} lần rút; tổ hợp: {combos}\n")
    print(K.to_string(index=False))
    print("\nPR-AUC trung bình:")
    show = C.pivot_table(index=["source", "level", "method"], columns="k", values="pr_auc", sort=False)
    print(show.round(3).to_string())
    print("\nλ* trung vị của TB-HTL:"); print(lam.to_string())
    print("\nPRESEL chọn:"); print(pres.to_string())
    if hoa is not None:
        print("\nTỷ lệ hoà khi chọn w, λ_s:"); print(hoa.pivot_table(index=["source", "level", "method"], columns="k", values="ty_le_hoa", sort=False).round(2).to_string())

    # Hình: đường cong PR-AUC theo k, mỗi ô một (nguồn, mức)
    lvs = [l for l in LEVELS if any(c[1] == l for c in combos)]
    fig, axs = plt.subplots(len({c[0] for c in combos}), len(lvs), figsize=(4.4 * len(lvs), 7.5), sharey=False, constrained_layout=True, squeeze=False)
    for i, src in enumerate(sorted({c[0] for c in combos})):
        for j, lv in enumerate(lvs):
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
    print("\nĐã lưu:", ", ".join(sorted(os.path.basename(f) for f in glob.glob(f"{folder}/k2_*"))))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "results/k2_v2")
