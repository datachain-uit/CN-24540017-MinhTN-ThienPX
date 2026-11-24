"""Hình 1 của bài: đường học PR-AUC theo k ở Cổng 0 (V4, quyết định 4 review 20/11-2; deviations 47).
Mô tả, không phải phép kiểm định mới: chỉ đọc g0_bang_duong_cong.csv đã commit (trung bình 30 lần chia).
    python3 paper/taimma2027/scripts/hinh1_duong_hoc.py      # chạy ở thư mục gốc của kho
- Baseline: PR-AUC lớn nhất trong các mô hình chỉ dùng đích (TO trong g0_decision.py) tại mỗi k (chọn sau).
- Chuyển giao: PR-AUC lớn nhất trong 7 phương pháp chuyển giao có dùng nhãn đích (TR trừ ZS) tại mỗi k (chọn sau).
- Ba khung theo miền đích của bốn hướng chính: IBM (nguồn Job Change, HR 14,999), Job Change (nguồn IBM), HR 14,999 (nguồn IBM).
- Vùng tô xám: k ≤ 50, vùng của các phép thử đã chốt. Trên k = 50 chỉ để mô tả.
Ghi paper/taimma2027/figures/fig1_learning_curves.pdf (vector), fig1_values.csv, config_fig1.json (HEAD, trạng thái Git);
in bảng giá trị để đối chiếu Phụ lục A4 review 20/11-2.
"""
import json, os, platform, subprocess, sys
from datetime import datetime, timezone, timedelta
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.getcwd())
from g0_decision import TO, TR, K_ORDER  # noqa: E402

OUT = "paper/taimma2027/figures"
TEN = {"A": "IBM", "B": "Job Change", "C": "HR 14,999"}
# (khung đích, [(thư mục kết quả, nguồn)])
KHUNG = [("A", [("results/g0_23", "B"), ("results/g0_AC", "C")]),
         ("B", [("results/g0_23", "A")]),
         ("C", [("results/g0_AC", "A")])]
MAU_NGUON = {"A": ("#1baf7a", "D", "--"), "B": ("#2a78d6", "s", "--"), "C": ("#eb6834", "^", "-.")}  # màu theo nguồn, cố định
MUC = ["10", "20", "50", "100", "200", "500", "full"]
NHAN_K = ["10", "20", "50", "100", "200", "500", "all"]
assert MUC == K_ORDER


def trang_thai_git():
    try:
        head = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
        st = subprocess.run(["git", "status", "--porcelain", "--untracked-files=no"], capture_output=True, text=True)
        return dict(git_head=head or None, git_dirty=bool(st.stdout.strip()), git_status=st.stdout.strip())
    except OSError:
        return dict(git_head=None, git_dirty=None, git_status=None)


def ty_le_duong(thu_muc, dich):
    """Tỷ lệ dương trung bình trên tập test của đích (đường xám = PR-AUC của bộ xếp hạng ngẫu nhiên)."""
    import glob
    f = sorted(glob.glob(f"{thu_muc}/results_g0_*_cpu.csv"))[0]
    r = pd.read_csv(f)
    return r[r.target == dich].pos_rate_test.mean(), f


def main():
    nguon_doc, dong, nhan = [], [], {}
    plt.rcParams.update({"font.family": "serif", "font.size": 7, "axes.titlesize": 7.5, "axes.labelsize": 7,
                         "xtick.labelsize": 6.5, "ytick.labelsize": 6.5, "legend.fontsize": 6.5, "pdf.fonttype": 42})
    fig, axes = plt.subplots(1, 3, figsize=(4.8, 1.9), sharey=True, constrained_layout=True)
    x = list(range(len(MUC)))
    for ax, (dich, cac_nguon) in zip(axes, KHUNG):
        ax.axvspan(-0.5, 2.5, color="#ecebe7", lw=0, zorder=0)
        base = None
        for thu_muc, ng in cac_nguon:
            f = f"{thu_muc}/g0_bang_duong_cong.csv"; nguon_doc.append(f)
            c = pd.read_csv(f, dtype={"k": str}); c = c[c.target == dich]
            b = c[c.method.isin(TO)].groupby("k").pr_auc.max().reindex(MUC)
            t = c[c.method.isin([m for m in TR if m != "ZS"])].groupby("k").pr_auc.max().reindex(MUC)
            assert b.notna().all() and t.notna().all(), (thu_muc, dich)
            if base is None:
                base = b
            else:  # baseline chỉ dùng đích phải như nhau giữa các cặp (cùng file chia của đích)
                assert (base - b).abs().max() < 1e-9, (thu_muc, dich)
            mau, mk, ls = MAU_NGUON[ng]
            ax.plot(x, t.values, color=mau, marker=mk, ls=ls, lw=1.2, ms=3.2, mec="white", mew=0.5,
                    label=f"best transfer from {TEN[ng]}", zorder=3)
            nhan[f"best transfer from {TEN[ng]}"] = ax.lines[-1]
            for k in MUC:
                dong.append(dict(target=dich, source=ng, k=k, best_target_only=b[k], best_transfer=t[k]))
        ax.plot(x, base.values, color="#0b0b0b", marker="o", lw=1.4, ms=3.2, mec="white", mew=0.5,
                label="best target-only", zorder=4)
        nhan["best target-only"] = ax.lines[-1]
        pr, fr = ty_le_duong(cac_nguon[0][0], dich); nguon_doc.append(fr)
        ax.axhline(pr, color="#9a9994", lw=0.8, zorder=1)
        ax.set_xticks(x); ax.set_xticklabels(NHAN_K, fontsize=5.5)
        ax.set_title(f"Target: {TEN[dich]}", loc="left", fontweight="bold")
        ax.set_xlabel("target labels $k$", labelpad=1)
        ax.set_ylim(0, 1); ax.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
        ax.grid(axis="y", color="#e4e3df", lw=0.5); ax.spines[["top", "right"]].set_visible(False)
        ax.tick_params(length=2, pad=1.5)
    axes[0].set_ylabel("PR-AUC (mean of 30 splits)")
    thu_tu = ["best target-only", "best transfer from IBM", "best transfer from Job Change", "best transfer from HR 14,999"]
    fig.legend([nhan[t] for t in thu_tu], thu_tu, loc="outside upper center", ncol=4, frameon=False,
               handlelength=2.0, columnspacing=1.0, fontsize=5.8)
    os.makedirs(OUT, exist_ok=True)
    fig.savefig(f"{OUT}/fig1_learning_curves.pdf", bbox_inches="tight", pad_inches=0.01,
                metadata={"Creator": "paper/taimma2027/scripts/hinh1_duong_hoc.py", "CreationDate": None, "ModDate": None})
    V = pd.DataFrame(dong)
    V.to_csv(f"{OUT}/fig1_values.csv", index=False, float_format="%.6f")
    cau_hinh = dict(muc_dich="Hình 1, đường học PR-AUC theo k (V4 review 20/11-2; deviations 47)", **trang_thai_git(),
                    nguon=sorted(set(nguon_doc)), python=sys.version.split()[0], pandas=pd.__version__,
                    matplotlib=matplotlib.__version__, platform=platform.platform(),
                    started=datetime.now(timezone(timedelta(hours=7))).strftime("%Y-%m-%d %H:%M:%S %z"))
    with open(f"{OUT}/config_fig1.json", "w", encoding="utf-8", newline="\n") as fh:
        json.dump(cau_hinh, fh, ensure_ascii=False, indent=1); fh.write("\n")

    pd.set_option("display.width", 200)
    print("Baseline chỉ dùng đích mạnh nhất (đối chiếu Phụ lục A4):")
    print(V.drop_duplicates(["target", "k"]).pivot(index="target", columns="k", values="best_target_only")[MUC].round(3).to_string())
    print("\nChuyển giao tốt nhất tại mỗi k:")
    print(V.pivot_table(index=["target", "source"], columns="k", values="best_transfer")[MUC].round(3).to_string())
    print(f"\nTrạng thái Git: HEAD {cau_hinh['git_head']}, dirty = {cau_hinh['git_dirty']}")


if __name__ == "__main__":
    main()
