"""
so_sanh_kb1.py — So sánh kết quả KB1 v2 chạy trên file Kaggle với lần chạy trong báo cáo.

    python so_sanh_kb1.py results/kb1_v2/results_kb1v2_99d14779.csv results/kb1_v2_kaggle/results_kb1v2_99d14779.csv

In ra: chênh lệch AUC-ROC / PR-AUC trung bình theo từng ô (đích × thiết lập × khái niệm × mã hoá × mô hình),
ô lệch lớn nhất, và kết luận KHỚP / LỆCH NHỎ / LỆCH. Lưu bảng chi tiết cạnh file thứ hai (_so_sanh.csv).
"""
import sys
import pandas as pd

TOL_MATCH, TOL_SMALL = 0.002, 0.01   # |Δ| ≤ 0,002: khớp (sai khác do làm tròn/thư viện); ≤ 0,01: lệch nhỏ
KEYS = ["target", "setting", "features", "encoding", "model"]


def main(old_path, new_path):
    old, new = pd.read_csv(old_path), pd.read_csv(new_path)
    for name, r in (("cũ", old), ("mới", new)):
        print(f"[{name}] {len(r)} dòng, số lần chia = {r.rep.nunique()}, "
              f"n_test A = {r[r.target == 'A'].n_test.iloc[0]}, n_test B = {r[r.target == 'B'].n_test.iloc[0]}, "
              f"dương test B = {r[r.target == 'B'].pos_test.iloc[0]}")
    a = old.groupby(KEYS)[["auc_roc", "pr_auc"]].mean()
    b = new.groupby(KEYS)[["auc_roc", "pr_auc"]].mean()
    m = a.join(b, lsuffix="_cu", rsuffix="_moi", how="outer")
    missing = m[m.isna().any(axis=1)]
    if len(missing):
        print(f"Cảnh báo: {len(missing)} ô chỉ có ở một bên (cấu hình khác nhau?)")
    m = m.dropna()
    m["d_auc"] = m.auc_roc_moi - m.auc_roc_cu
    m["d_pr"] = m.pr_auc_moi - m.pr_auc_cu
    worst = max(m.d_auc.abs().max(), m.d_pr.abs().max())
    out = new_path.replace(".csv", "_so_sanh.csv")
    m.round(4).to_csv(out)

    pd.set_option("display.width", 200)
    print("\n10 ô lệch AUC-ROC lớn nhất:")
    print(m.reindex(m.d_auc.abs().sort_values(ascending=False).index).head(10)
          [["auc_roc_cu", "auc_roc_moi", "d_auc", "pr_auc_cu", "pr_auc_moi", "d_pr"]].round(3).to_string())

    # Các ô được dùng trong Bảng 4 của báo cáo
    main_cells = m.loc[[i for i in m.index if i[2] in ("full", "canon4") and i[3] in ("-", "std", "rank")]]
    print(f"\nLệch tuyệt đối lớn nhất (mọi ô): {worst:.4f}; riêng các ô của Bảng 4: "
          f"{max(main_cells.d_auc.abs().max(), main_cells.d_pr.abs().max()):.4f}")
    if worst <= TOL_MATCH:
        print("KẾT LUẬN: KHỚP — ghi một dòng xác nhận vào B1.3/A5.1, không cần sửa Bảng 4.")
    elif worst <= TOL_SMALL:
        print("KẾT LUẬN: LỆCH NHỎ — số liệu ở chữ số thứ ba thay đổi; cập nhật Bảng 4 bằng file mới, kết luận giữ nguyên.")
    else:
        print("KẾT LUẬN: LỆCH — dữ liệu Kaggle khác bản sao; dùng file mới cho Bảng 4 và kiểm tra lại 4 nhận định ở B1.3.")
    print(f"Bảng chi tiết: {out}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
