"""Sinh bảng cho bài TAIMMA 2027 từ kết quả đã commit (mục 7.5 review 01/11, Phụ lục B4).
    python paper/taimma2027/scripts/bang_bai_bao.py        # chạy ở thư mục gốc của kho
Ghi tables/T*.tex; dòng đầu mỗi file ghi file nguồn và mã commit. Không sửa số trên Overleaf.
T1, T5, phần C1 và PRESEL của T6: Thiên. T2, T3, T4 (kèm RQ6, H5), phần hoà và CORAL của T6: Minh (hàm t2, t3, t4, t4_rq6, t4_h5, t6_hoa, t6_coral). Bảng vừa khổ một cột LNCS, không dùng table* (QĐ1, mục 7.3 review 07/11).
"""
import json, os, subprocess
import pandas as pd
from scipy import stats

OUT = "paper/taimma2027/tables"
TO = ["LR", "RF", "XGB", "CAT", "STACK", "TabPFN"]
CAP = {"A": "AB", "B": "AB", "C": "AC", "D": "AD"}
TEN = {"A": "IBM", "B": "Job Change", "C": "HR 14,999", "D": "Babushkin"}
TINH_CHAT = {"A": "fictional", "B": "real, intent label", "C": "simulated", "D": "real, censored label"}


def commit_cua(path):
    return subprocess.run(["git", "log", "-1", "--format=%h", "--", path],
                          capture_output=True, text=True).stdout.strip()


def chieu(nguon, dich):
    return rf"{nguon}$\to${dich}"


def so(x, n=3):
    s = f"{abs(x):.{n}f}"
    return ("$-$" if x < 0 else "$+$") + s


def ghi(ten, nguon, cot, tieu_de, dong):
    tex = [f"% source: {p}, commit {commit_cua(p)}" for p in nguon]
    tex += [rf"\begin{{tabular}}{{{cot}}}", r"\hline", tieu_de + r" \\", r"\hline",
            *[d + r" \\" for d in dong], r"\hline", r"\end{tabular}"]
    os.makedirs(OUT, exist_ok=True)
    with open(f"{OUT}/{ten}.tex", "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(tex) + "\n")


def t1():
    src, kn = "eda/bang1_tong_quan_mien.csv", "prereg/k2_khai_niem.json"
    d = pd.read_csv(src, encoding="utf-8-sig").set_index("Miền")
    n = json.load(open(kn, encoding="utf-8"))["nguon"]
    dong = []
    for m in "ABCD":
        r = d.loc[m]
        muc = "--" if m not in n else ", ".join(f"{k.replace('_', chr(92) + '_')}: {len(v['khai_niem_chung'])}" for k, v in n[m].items() if "khai_niem_chung" in v)
        dong.append(f"{m} & {TEN[m]} & {int(r['Dòng còn lại']):,} & "
                    rf"{100 * r['Tỷ lệ dương']:.2f}\% & {TINH_CHAT[m]} & {muc}")
    ghi("T1_domains", [src, kn], "llrrll",
        r"Domain & Dataset & Rows & Positive rate & Nature & Shared concepts", dong)


def t5():
    src = "results/trada/trada_kiem_dinh.csv"
    d = pd.read_csv(src)
    d = d[d.p_holm.notna()].assign(kem=lambda x: (x.p_holm < 0.05) & (x.delta < 0))
    dong = []
    for (st, ng, dc), g in d.groupby(["setting", "source", "target"], sort=False):
        ten = "Gate 0" if st == "g0" else "K2-L0"
        dong.append(f"{ten} & {chieu(ng, dc)} & {len(g)} & {int(g.dat.sum())} & {int(g.kem.sum())} & "
                    f"{so(g.delta.min())} to {so(g.delta.max())}")
    dong.append(f"Total & & {len(d)} & {int(d.dat.sum())} & {int(d.kem.sum())} & ")
    ghi("T5_tradaboost", [src], "llrrrl",
        r"Setting & Direction & Tests & Passed & Sig. worse & $\Delta$ range", dong)


def t5_mde():
    """Ba phép không phân biệt được với baseline; MDE80 theo công thức của mde_cong0.py, từ khoảng tin cậy."""
    src = "results/trada/trada_kiem_dinh.csv"
    d = pd.read_csv(src)
    d = d[d.p_holm.notna() & (d.p_holm >= 0.05)]
    t975, t80 = stats.t.ppf(0.975, 29), stats.t.ppf(0.80, 29)
    dong = []
    for r in d.itertuples():
        ten = "Gate 0" if r.setting == "g0" else "K2-L0"
        mde = (r.ci_hi - r.ci_lo) / 2 * (t975 + t80) / t975
        dong.append(f"{ten} & {chieu(r.source, r.target)} & {r.k} & {so(r.delta)} & {r.p_holm:.3f} & {mde:.3f}")
    ghi("T5_mde", [src], "llrrrr", r"Setting & Direction & $k$ & $\Delta$ & Holm $p$ & MDE$_{80}$", dong)


def t6_c1():
    src = "results/c1_do_nhay/c1_phep_chinh.csv"
    d = pd.read_csv(src)
    dong = [f"{r.chieu.replace('→', '$' + chr(92) + 'to$')} & {r.zs_c1:.3f} & {r.zs_mid:.3f} & {so(r.delta)} & "
            f"[{so(r.ci_lo)}, {so(r.ci_hi)}] & {'$<$0.001' if r.p_holm < 0.001 else f'{r.p_holm:.3f}'}"
            for r in d.itertuples()]
    ghi("T6_c1", [src], "lrrrll", r"Direction & C1 & C1\_MID & $\Delta$ & 95\% CI & Holm $p$", dong)


def t6_presel():
    src = "results/g0_bo_sung/chi_so_tu_du_doan_tho.csv"
    moi = [f"results/g0_bo_sung/results_moi_{t}.csv" for t in "ABCD"]
    s = pd.read_csv(src, dtype={"k": str})
    dong = []
    for t, f in zip("ABCD", moi):
        o = s[(s.pair == CAP[t]) & (s.target == t) & s.method.isin(TO)].groupby(["method", "k"]).pr_auc.mean().unstack("k")
        p = pd.read_csv(f, dtype={"k": str})
        p = p[p.method == "PRESEL"].groupby("k").pr_auc.mean()
        cuoi = [f"{p[k] - o[k].max():.3f}".replace("-", "$-$") for k in ["10", "20", "50"]]
        dong.append(f"{t} ({TEN[t]}) & " + " & ".join(cuoi))
    ghi("T6_presel", [src, *moi], "lrrr", r"Target & $k=10$ & $k=20$ & $k=50$", dong)


# ---------------- Phần của Minh: T2, T3, T4, phần hoà và CORAL của T6 ----------------
G0 = {"AB": "results/g0_23", "AC": "results/g0_AC", "AD": "results/g0_AD"}
NGUON_G0 = {("AB", "A"): "B", ("AB", "B"): "A", ("AC", "A"): "C", ("AC", "C"): "A", ("AD", "A"): "D", ("AD", "D"): "A"}


def ten_pp(m):
    return m.replace("_", r"\_")


def p_txt(p):
    return "$<$0.001" if p < 0.001 else f"{p:.3f}"


def t2():
    """Danh sách phương pháp lấy từ tiền đăng ký K2 (không gõ tay)."""
    import yaml
    src = "prereg/prereg_k2.yaml"
    m = yaml.safe_load(open(src, encoding="utf-8"))["methods"]
    dong = [r"Target-only & " + ", ".join(ten_pp(x) for x in m["target_only"]) + r"; PRESEL (pre-selected by CV on the $k$ labels)",
            r"Transfer & " + ", ".join(ten_pp(x) for x in m["transfer"]),
            r"Transfer, L0 only & " + ", ".join(ten_pp(x) for x in m["transfer_L0_only"]),
            r"Theory-guided (RQ6) & TB-HTL v0 (docs/tbhtl\_v0\_spec.md)",
            r"Control (shuffled source labels) & " + ", ".join(ten_pp(x) for x in m["control"])]
    ghi("T2_methods", [src], "@{}lp{8.0cm}@{}", r"Group & Methods", dong)


def t3():
    """Cổng 0: Δ tốt nhất (chuyển giao − đích mạnh nhất) ở k ≤ 50, CI, Holm p, kết luận GO/PIVOT, MDE80 trung vị theo k."""
    mde_src = "results/tong_hop_cap/mde_cong0_bang.csv"
    mde = pd.read_csv(mde_src).set_index("chieu")
    nguon, dong = [mde_src], []
    for cap, thu_muc in G0.items():
        f = f"{thu_muc}/g0_kiem_dinh_GO.csv"; nguon.append(f)
        d = pd.read_csv(f, dtype={"k": str})
        for dich in [cap[0], cap[1]]:
            g = d[(d.target == dich) & d.k.isin(["10", "20", "50"])]
            b = g.loc[g.delta.idxmax()]
            ng = NGUON_G0[(cap, dich)]
            ch = f"{ng}→{dich}"
            m80 = mde.loc[ch, ["10", "20", "50"]].median()
            tham_do = r"$^{\dagger}$" if "D" in (ng, dich) else ""
            dong.append(f"{chieu(ng, dich)}{tham_do} & {ten_pp(b.method)}, $k={b.k}$ & {so(b.delta)} & "
                        f"[{so(b.ci_lo)}, {so(b.ci_hi)}] & {p_txt(b.p_holm)} & {'GO' if g.dat_GO.any() else 'PIVOT'} & {m80:.3f}")
    ghi("T3_gate0", nguon, "llrlrlr",
        r"Direction & Best transfer & $\Delta$ & 95\% CI & Holm $p$ & Decision & MDE$_{80}$", dong)


def t4():
    """K2: theo nguồn × mức — kết luận, Δ tốt nhất ở k ≤ 50 (họ GO), CI, Holm p, MDE80 trung vị."""
    kl_src, kd_src = "results/k2_v2/k2_ket_luan.csv", "results/k2_v2/k2_kiem_dinh.csv"
    kl = pd.read_csv(kl_src).set_index(["source", "level"])
    kd = pd.read_csv(kd_src, dtype={"k": str})
    go = kd[kd.ho.str.startswith("GO") & kd.k.isin(["10", "20", "50"])]
    dong = []
    for (ng, lv), r in kl.iterrows():
        g = go[(go.source == ng) & (go.level == lv)]
        b = g.loc[g.delta.idxmax()]
        dong.append(f"{TEN[ng]} & {lv.replace('_', chr(92) + '_')} & {r.ket_luan} & {ten_pp(b.method)}, $k={b.k}$ & {so(b.delta)} & "
                    f"[{so(b.ci_lo)}, {so(b.ci_hi)}] & {p_txt(b.p_holm_GO)} & {r.MDE80_trung_vi:.3f}")
    ghi("T4_k2", [kl_src, kd_src], "@{}lllllllr@{}",
        r"Source & Level & Decision & Best transfer & $\Delta$ & 95\% CI & Holm $p$ & MDE$_{80}$", dong)


def t4_rq6():
    """RQ6: TB-HTL − chuyển giao tốt nhất ở k ≤ 50, theo nguồn × mức: khoảng Δ và số phép có ý nghĩa sau Holm."""
    src = "results/k2_v2/k2_kiem_dinh.csv"
    kd = pd.read_csv(src, dtype={"k": str})
    rq6 = kd[kd.ho.str.startswith("RQ6: TB-HTL") & kd.k.isin(["10", "20", "50"])]
    dong = []
    for (ng, lv), t in rq6.groupby(["source", "level"], sort=False):
        dong.append(f"{TEN[ng]} & {lv.replace('_', chr(92) + '_')} & {so(t.delta.min())} & {so(t.delta.max())} & "
                    f"{int((t.p_holm < 0.05).sum())}/{len(t)}")
    ghi("T4_rq6", [src], "llrrr", r"Source & Level & min $\Delta$ & max $\Delta$ & Holm $p<0.05$", dong)


def t4_h5():
    """H5: phép chính L0 − L2 (lợi ích so với PRESEL), Holm trên 12 phép."""
    src = "results/k2_v2/k2_h5.csv"
    d = pd.read_csv(src)
    d = d[d.so_sanh == "L0 − L2"]
    dong = [f"{TEN[r.source]} & {ten_pp(r.method)} & {r.k} & {so(r.delta_loi_ich)} & [{so(r.ci_lo)}, {so(r.ci_hi)}] & "
            f"{p_txt(r.p_holm)} & {'yes' if r.ung_ho_H5 else 'no'}" for r in d.itertuples()]
    ghi("T4_h5", [src], "llrrlrl", r"Source & Method & $k$ & $\Delta$(L0$-$L2) & 95\% CI & Holm $p$ & H5 supported", dong)


def t6_hoa():
    src = "results/g0_tie_neutral/g0_tie_neutral_ket_luan.csv"
    d = pd.read_csv(src)
    dong = [f"{chieu(NGUON_G0[(r.cap, r.dich)], r.dich)} & {r.first} & {r.neutral}" for r in d.itertuples()]
    ghi("T6_tie", [src], "lll", r"Direction & Tie rule: first & Tie rule: neutral", dong)


def t6_coral():
    src = "results/k2_coral/tach_hiep_phuong_sai_tom_tat.csv"
    d = pd.read_csv(src)
    dong = [f"{TEN[r.source]} & {r.toan_phan:.3f} & {r.duong_cheo:.3f} & {r.ngoai_duong_cheo:.3f} & {100 * r.ty_trong_duong_cheo:.1f}\\%"
            for r in d.itertuples()]
    ghi("T6_coral", [src], "lrrrr", r"Source & $\|C_S-C_T\|_F$ & Diag. & Off-diag. & Diag. share$^{\ast}$", dong)


BANG = [t1, t2, t3, t4, t4_rq6, t4_h5, t5, t5_mde, t6_c1, t6_presel, t6_hoa, t6_coral]

if __name__ == "__main__":
    for b in BANG:
        b()
