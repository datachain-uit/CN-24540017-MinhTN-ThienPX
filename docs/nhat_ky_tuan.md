# Nhật ký tuần

Mỗi thành viên thêm một dòng mỗi tuần (O6). Ghi mã băm cấu hình của lần chạy nếu có.

| Tuần | Thành viên | Đã làm (file / commit) | Kết quả, mã băm | Việc tuần sau |
|---|---|---|---|---|
| 15–21/10/2026 | Minh | | | |
| 15–21/10/2026 | Thiên | Làm sạch bộ HR 14.999 (miền C) và Babushkin (miền D); chốt bảng ánh xạ khái niệm cho cặp AC và AD — `pairs.py`. Chạy G0-2 (đường cong học chỉ dùng đích, 6 mô hình gồm TabPFN v2) và KB8 (ngữ nghĩa nhãn, RQ4) — `kb1_pair.py`, `g0_pair.py` | kb1_AC `40a7ef2e`; kb1_AD `4c085b4a`; g0_AC `49df37eb`; g0_AC_consistent `2d7c34f0`; g0_AD `083937b0`. Cổng 0: PIVOT ở cả hai chiều của cả hai cặp | EDA bốn miền; phiếu đọc |
| 22–28/10/2026 | Thiên | EDA bốn miền — `eda/eda_bon_mien.ipynb` (dùng `pairs.LOADERS`; phân tích có nhãn chỉ trên phần train của `rep = 0`); đã chạy trên 3/4 miền. 8 phiếu đọc trong `docs/phieu_doc/`; cập nhật `bang1_phuong_phap_luan.csv` (18 ô) | Commit: `………`. EDA khớp Bảng 12: A 1.470 (16,12%), B 19.158→19.084 (24,92%), C 14.999→11.991 (16,60%). **Xác nhận `tenure` ngược chiều ở cặp AC: AUC 0,355 (A) vs 0,690 (C)**. Miền D thiếu `turnover.csv`. Phiếu đầy đủ: [10], [43], [11], [24], [33]; còn khung: [5], [8], [31] | Tải `turnover.csv`, chạy lại EDA đủ 4 miền; phiếu [25], [32]; bổ sung số trang cho [5], [8], [31]; Plan.xlsx (M9); mục 6.4 |

Mã băm các lần chạy tuần 15–21/10 (để ghi vào cột 4): kb1_v2 99d14779; kb1_AB cf3e982a (TabPFN v2); kb1_AC 40a7ef2e; kb1_AD 4c085b4a; g0_23 6f2142bf / 44c64e04; g0_AC 49df37eb; g0_AC_consistent 2d7c34f0; g0_AD 083937b0.

23/10
Chạy thực nghiệm lại phương pháp CARTE.
Bắt đầu EDA: tạo eda/eda_bon_mien.ipynb với phần đọc 4 bộ dữ liệu bằng from pairs import LOADERS và bảng số dòng, tỷ lệ dương của từng miền. Đang bắt đầu triển khai 