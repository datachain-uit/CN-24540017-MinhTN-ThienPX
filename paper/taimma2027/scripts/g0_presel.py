"""Cổng 0: phương pháp chuyển giao − PRESEL, ghép theo lần chia (V2, mục 6.1 và 6.2 việc 2 review 20/11; deviations 46).
Kiểm tra độ vững sau, không thuộc tiền đăng ký, không chạy mô hình: chỉ đọc kết quả đã commit.
    python3 paper/taimma2027/scripts/g0_presel.py        # chạy ở thư mục gốc của kho
- Chuyển giao: 8 phương pháp Cổng 0 (TR trong g0_decision.py), đọc như g0_decision.main (bỏ TBHTL*).
- PRESEL: results/g0_bo_sung/results_moi_<đích>.csv (cùng file chia splits_<đích>_R30.json với Cổng 0).
- ZS không dùng nhãn đích: lấy dòng k = "zero", ghép với PRESEL ở từng k = 10, 20, 50.
- CI hiệu chỉnh Nadeau–Bengio (0,25) bằng đúng hàm corrected() của g0_decision.py; luật Cổng 0: GO nếu Δ ≥ 0,02 và cận dưới > 0.
- "Kém có ý nghĩa": cận trên < 0. Holm trên 24 phép của một chiều chỉ để báo cáo.
Ghi results/g0_bo_sung/g0_presel_kiem_dinh.csv, g0_presel_tom_tat.csv, config_g0_presel.json (mã commit, trạng thái Git).
"""
import glob, json, os, platform, subprocess, sys
from datetime import datetime, timezone, timedelta
import pandas as pd

sys.path.insert(0, os.getcwd())
from g0_decision import corrected, holm, TR, KS_DECIDE, RATIO  # noqa: E402

G0 = {"AB": "results/g0_23", "AC": "results/g0_AC", "AD": "results/g0_AD"}
NGUON = {("AB", "A"): "B", ("AB", "B"): "A", ("AC", "A"): "C", ("AC", "C"): "A", ("AD", "A"): "D", ("AD", "D"): "A"}
OUT = "results/g0_bo_sung"


def trang_thai_git():
    try:
        head = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
        st = subprocess.run(["git", "status", "--porcelain", "--untracked-files=no"], capture_output=True, text=True)
        return dict(git_head=head or None, git_dirty=bool(st.stdout.strip()), git_status=st.stdout.strip())
    except OSError:
        return dict(git_head=None, git_dirty=None, git_status=None)


def doc_cong0(thu_muc):
    files = sorted(glob.glob(f"{thu_muc}/results_g0_23_*.csv") + glob.glob(f"{thu_muc}/results_g0_[A-D][A-D]_*.csv"))
    r = pd.concat([pd.read_csv(f) for f in files], ignore_index=True)
    r = r[~r.method.astype(str).str.startswith("TBHTL")]
    r["k"] = r["k"].astype(str)
    return r, files


def main():
    cau_hinh = dict(muc_dich="Cổng 0: chuyển giao − PRESEL (V2 review 20/11; deviations 46)", ratio=RATIO,
                    ks=KS_DECIDE, phuong_phap=TR, **trang_thai_git(),
                    python=sys.version.split()[0], pandas=pd.__version__, platform=platform.platform(),
                    started=datetime.now(timezone(timedelta(hours=7))).strftime("%Y-%m-%d %H:%M:%S %z"))
    nguon_doc, dong = [], []
    for cap, thu_muc in G0.items():
        r, files = doc_cong0(thu_muc); nguon_doc += files
        for dich in cap:
            f = f"{OUT}/results_moi_{dich}.csv"
            if f not in nguon_doc:
                nguon_doc.append(f)
            p = pd.read_csv(f, dtype={"k": str})
            rt = r[r.target == dich]
            zs = rt[rt.method == "ZS"].set_index("rep").pr_auc
            for k in KS_DECIDE:
                base = p[(p.method == "PRESEL") & (p.k == k)].set_index("rep").pr_auc
                rk = rt[rt.k == k]
                for m in TR:
                    cand = zs if m == "ZS" else rk[rk.method == m].set_index("rep").pr_auc
                    if not len(cand):
                        continue
                    # Kiểm tra ghép theo lần chia (Phụ lục A2 review 21/11): mỗi rep một dòng, đủ R = 30 cặp
                    assert cand.index.is_unique and base.index.is_unique, (dich, k, m)
                    d = (cand - base).dropna()
                    assert len(d) == 30, (dich, k, m, len(d))
                    mean, lo, hi, pv = corrected(d.to_numpy())
                    dong.append(dict(cap=cap, source=NGUON[(cap, dich)], target=dich, k=k, method=m,
                                     presel_pr=base.mean(), method_pr=cand.mean(), delta=mean, ci_lo=lo, ci_hi=hi,
                                     p_corr=pv, n_rep=len(d)))
    T = pd.DataFrame(dong)
    for _, g in T.groupby(["cap", "target"]):
        T.loc[g.index, "p_holm"] = holm(g.p_corr.to_numpy())
    T["dat_GO"] = (T.delta >= 0.02) & (T.ci_lo > 0)
    T["tot_hon_y_nghia"] = T.ci_lo > 0
    T["kem_y_nghia"] = T.ci_hi < 0
    T["thu_do"] = (T.source == "D") | (T.target == "D")
    os.makedirs(OUT, exist_ok=True)
    T.to_csv(f"{OUT}/g0_presel_kiem_dinh.csv", index=False)

    tom = []
    for (cap, dich), g in T.groupby(["cap", "target"], sort=False):
        b = g.loc[g.delta.idxmax()]
        tom.append(dict(chieu=f"{b.source}→{dich}", tham_do=bool(b.thu_do), so_phep=len(g), dat_GO=int(g.dat_GO.sum()),
                        tot_hon_y_nghia=int(g.tot_hon_y_nghia.sum()), kem_y_nghia=int(g.kem_y_nghia.sum()),
                        delta_max=b.delta, ci_lo=b.ci_lo, ci_hi=b.ci_hi, method=b.method, k=b.k))
    S = pd.DataFrame(tom)
    S.to_csv(f"{OUT}/g0_presel_tom_tat.csv", index=False)
    cau_hinh["nguon"] = nguon_doc
    with open(f"{OUT}/config_g0_presel.json", "w", encoding="utf-8", newline="\n") as fh:
        json.dump(cau_hinh, fh, ensure_ascii=False, indent=1)
        fh.write("\n")

    pd.set_option("display.width", 200)
    print(S.round(3).to_string(index=False))
    chinh = T[~T.thu_do]
    print(f"\nTổng: {int(T.dat_GO.sum())}/{len(T)} phép đạt luật Cổng 0; {int(T.tot_hon_y_nghia.sum())} tốt hơn có ý nghĩa; "
          f"bốn hướng chính: {int(chinh.kem_y_nghia.sum())}/{len(chinh)} kém có ý nghĩa.")
    print(f"Trạng thái Git: HEAD {cau_hinh['git_head']}, dirty = {cau_hinh['git_dirty']}")


if __name__ == "__main__":
    main()
