"""huong1_mde_D.py — MDE thiết kế cho Hướng 1 (V4 review 12/11; quyết định 6 review 20/11-2; deviations 48).
Tính để lập kế hoạch, không phải phép kiểm định, không chạy mô hình: chỉ đọc kết quả K2 đã commit (results/k2_v2).
    python huong1_mde_D.py        # chạy ở thư mục gốc của kho
Hướng 1 đề xuất hiệu của hiệu D = (CORAL − ZS) trên C1 − (CORAL − ZS) trên C1_MID ở mức L0 (nguồn B, C).
CORAL và ZS không dùng nhãn đích nên mỗi lần chia có một giá trị (trung bình M lần rút, như k2_eval.combo_table).
- d1 = (CORAL − ZS) trên C1, theo lần chia (R = 30): Δ, CI 95% hiệu chỉnh Nadeau–Bengio (0,25), MDE80 — dùng chính hàm của k2_eval.py.
- Phần trên C1_MID chưa chạy, nên MDE của D lấy theo giả định độ lệch chuẩn của (CORAL − ZS) trên C1_MID bằng trên C1
  và tương quan ρ giữa hai phiên bản: sd(D) = sd(d1)·sqrt(2(1 − ρ)). Báo ρ = 0 (thận trọng), 0,5 và 0,75.
- TOST ±0,02 (dùng lại phép đọc ngưỡng 0,02 của việc 1, CI 95%): (CORAL − ZS) tương đương 0 khi cả CI 95% nằm trong (−0,02; +0,02).
Ghi results/k2_coral/huong1_mde_D.csv và config_huong1_mde_D.json (HEAD, trạng thái Git).
"""
import json, platform, subprocess, sys
from datetime import datetime, timezone, timedelta
import numpy as np
import pandas as pd
from scipy import stats

from k2_eval import load, combo_table, RATIO

OUT = "results/k2_coral"
RHO = [0.0, 0.5, 0.75]


def trang_thai_git():
    try:
        head = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
        st = subprocess.run(["git", "status", "--porcelain", "--untracked-files=no"], capture_output=True, text=True)
        return dict(git_head=head or None, git_dirty=bool(st.stdout.strip()), git_status=st.stdout.strip())
    except OSError:
        return dict(git_head=None, git_dirty=None, git_status=None)


def mde80(sd, J):
    se = np.sqrt(1 / J + RATIO) * sd
    return (stats.t.ppf(.975, J - 1) + stats.t.ppf(.80, J - 1)) * se


def main():
    r = load("results/k2_v2")
    dong = []
    for src in ["B", "C"]:
        T = combo_table(r, src, "L0")
        pr = T.pr_auc.unstack("rep")
        coral, zs = pr.loc[("CORAL", "zero")], pr.loc[("ZS", "zero")]
        assert coral.index.is_unique and zs.index.is_unique
        d1 = (coral - zs).dropna()
        J = len(d1); assert J == 30, J
        sd = d1.std(ddof=1)
        se = np.sqrt(1 / J + RATIO) * sd
        t975 = stats.t.ppf(.975, J - 1)
        lo, hi = d1.mean() - t975 * se, d1.mean() + t975 * se
        row = dict(source=src, level="L0", n_rep=J, coral_pr=coral.mean(), zs_pr=zs.mean(), delta_C1=d1.mean(),
                   ci_lo=lo, ci_hi=hi, sd_d1=sd, MDE80_d1=mde80(sd, J),
                   TOST_002_tuong_duong=bool(lo > -0.02 and hi < 0.02))
        for rho in RHO:
            row[f"MDE80_D_rho{rho:g}"] = mde80(sd * np.sqrt(2 * (1 - rho)), J)
        dong.append(row)
    T = pd.DataFrame(dong)
    T.to_csv(f"{OUT}/huong1_mde_D.csv", index=False, float_format="%.6f", lineterminator="\n")
    cau_hinh = dict(muc_dich="MDE thiết kế cho Hướng 1 (V4 review 12/11; deviations 48)", ratio=RATIO, rho=RHO,
                    nguon="results/k2_v2 (k2_eval.load, combo_table)", **trang_thai_git(),
                    python=sys.version.split()[0], pandas=pd.__version__, platform=platform.platform(),
                    started=datetime.now(timezone(timedelta(hours=7))).strftime("%Y-%m-%d %H:%M:%S %z"))
    with open(f"{OUT}/config_huong1_mde_D.json", "w", encoding="utf-8", newline="\n") as fh:
        json.dump(cau_hinh, fh, ensure_ascii=False, indent=1); fh.write("\n")
    pd.set_option("display.width", 200)
    print(T.round(3).T.to_string())
    print(f"\nTrạng thái Git: HEAD {cau_hinh['git_head']}, dirty = {cau_hinh['git_dirty']}")


if __name__ == "__main__":
    main()
