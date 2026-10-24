"""
k2_muc_san.py — Tóm tắt kiểm tra mức sàn của K2 (nhãn đích xáo trộn, review 24/10 V6 / review 18/10 M8).

    python k2_muc_san.py results/k2_v2

Đọc results_k2_*_xao_tron_dich.csv. Với nhãn test và nhãn k mẫu đều bị hoán vị, mọi phương pháp phải cho PR-AUC
xấp xỉ tỷ lệ dương của tập test và AUC-ROC xấp xỉ 0,5. Với tập test 294 mẫu, 47 mẫu dương, PR-AUC kỳ vọng của một
bộ điểm ngẫu nhiên là khoảng 0,174 (mô phỏng), cao hơn tỷ lệ dương 0,161 một chút. Ghi k2_muc_san.csv (theo phương pháp) và in tóm tắt.
"""
import glob, sys
import numpy as np
import pandas as pd

folder = sys.argv[1] if len(sys.argv) > 1 else "results/k2_v2"
fs = sorted(glob.glob(f"{folder}/results_k2_*_xao_tron_dich*.csv"))
r = pd.concat([pd.read_csv(f, dtype={"k": str}) for f in fs], ignore_index=True)
# tỷ lệ dương của tập test (nhãn IBM 0,161; xáo trộn giữ nguyên số mẫu dương)
pos = 237 / 1470
by_m = r.groupby("method").agg(n=("pr_auc", "size"), pr_auc=("pr_auc", "mean"), pr_auc_max=("pr_auc", "max"),
                               auc_roc=("auc_roc", "mean")).sort_values("pr_auc", ascending=False)
by_mk = r[r.k != "zero"].groupby(["method", "k"]).pr_auc.mean().unstack("k")
by_m.to_csv(f"{folder}/k2_muc_san.csv")
pd.set_option("display.width", 200)
print(f"{len(fs)} file, {len(r)} dòng; lần chia {sorted(map(int, r.rep.unique()))}, lần rút {sorted(map(int, r.draw.unique()))}; "
      f"tỷ lệ dương tập test ≈ {pos:.3f}")
print(f"PR-AUC trung bình theo phương pháp: {by_m.pr_auc.min():.3f} – {by_m.pr_auc.max():.3f}; "
      f"AUC-ROC trung bình: {by_m.auc_roc.min():.3f} – {by_m.auc_roc.max():.3f}")
print(by_m.round(3).to_string())
print("\nPR-AUC theo nguồn, mức lược đồ:")
print(r.groupby(["source", "level"]).pr_auc.mean().round(3).to_string())
print("\nPR-AUC theo k (trung bình mọi nguồn, mức, lần chia, lần rút):")
print(by_mk.round(3).to_string())
