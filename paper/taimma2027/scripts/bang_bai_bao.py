"""Sinh bảng cho bài TAIMMA 2027 từ kết quả đã commit (mục 7.5 review 01/11, Phụ lục B4).
    python paper/taimma2027/scripts/bang_bai_bao.py        # chạy ở thư mục gốc của kho
Ghi tables/T*.tex; dòng đầu mỗi file ghi file nguồn và mã commit. Không sửa số trên Overleaf.
T1, T5, phần C1 và PRESEL của T6: Thiên. T2, T3, T4, phần hoà và CORAL của T6: Minh thêm hàm vào BANG.
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


BANG = [t1, t5, t5_mde, t6_c1, t6_presel]

if __name__ == "__main__":
    for b in BANG:
        b()
