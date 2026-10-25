# Nhật ký tuần

Mỗi thành viên thêm một dòng mỗi tuần (O6). Ghi mã băm cấu hình của lần chạy nếu có.

| Tuần | Thành viên | Đã làm (file / commit) | Kết quả, mã băm | Việc tuần sau |
|---|---|---|---|---|
| 15–21/10/2026 | Minh | | | |
| 15–21/10/2026 | Thiên | Tái hiện CARTE trên 3 bộ dữ liệu rượu (KB2b) — `kb2b_carte/` (có trong kho từ `f65e85a`, Minh đẩy lên trong commit gộp). *Đính chính 25/10: bản trước của dòng này ghi Thiên làm `pairs.py`, `kb1_pair.py`, `g0_pair.py`, G0-2 và KB8; ghi như vậy là sai, các phần đó do Minh làm (xem `docs/phan_cong.md`)* | Đối chiếu kết quả công bố theo từng seed; GVHD ghi nhận ở review 18/10 | EDA bốn miền; phiếu đọc |
| 22–28/10/2026 | Thiên | EDA bốn miền — `eda/eda_bon_mien.ipynb` (dùng `pairs.LOADERS`; phân tích có nhãn chỉ trên phần train của `rep = 0`); chạy được 3/4 miền. **10** phiếu đọc trong `docs/phieu_doc/`; cập nhật `bang1_phuong_phap_luan.csv` | Commit: `b89d1d3` (24/10). EDA khớp Bảng 12: A 1.470 (16,12%), B 19.158→19.084 (24,92%), C 14.999→11.991 (16,60%). **Xác nhận `tenure` ngược chiều ở cặp AC: AUC 0,355 (A) vs 0,690 (C)**. Miền D thiếu `turnover.csv`. Phiếu đầy đủ: [10], [11], [24], [32], [33], [43]; còn chờ toàn văn: [5], [8], [25], [31] | Tải `turnover.csv`, chạy lại EDA đủ 4 miền; lấy toàn văn [2], [3], [5], [8], [9], [25]; Plan.xlsx (M9); mục 6.4 |
| 22–28/10/2026 | Thiên | Dọn kho theo yêu cầu trưởng nhóm: gỡ 3 file trùng + 3 tệp dữ liệu rượu + 1 `.docx` ở thư mục gốc khỏi Git, khôi phục `kb2b_carte/README.md`. Sửa `docs/giai_trinh_phan_viec_ThienPX.md` cho đúng phần việc (đính chính 25/10). Điền ngày đọc / thời gian đọc cho cả 10 phiếu; điền `bang1_phuong_phap_luan.csv` từ toàn văn [4] (PMC9251085), [6] (PMC10557501), [7] (arXiv 2304.03103) | Commit: `6c056db` (24/10, Bảng 1, phiếu đọc, README); `10207f4` (25/10, dọn thư mục gốc). Bảng 1 mở rộng: 12 dòng, không còn ô `?` trống. **Hai điểm cần sửa Bảng 1**: (a) [4] dùng dữ liệu "thư viện SAS" ~1.500 dòng chứ không gọi tên IBM — Bảng 1 đang ghi "IBM HR"; (b) [6] là mốc ngoài dùng được trực tiếp trên miền A, AUC-ROC 0,7452 < 0,840 (TabPFN v2) và 0,829 (LR) của nhóm → chứng cứ cho PIVOT | Lấy toàn văn 4 bài truy cập mở còn lại ([3], [8], [9] + [25]); xin ý kiến GVHD về việc đưa luận văn UNICAMP 2025 vào Bảng 1 |

Mã băm các lần chạy tuần 15–21/10 (để ghi vào cột 4): kb1_v2 99d14779; kb1_AB cf3e982a (TabPFN v2); kb1_AC 40a7ef2e; kb1_AD 4c085b4a; g0_23 6f2142bf / 44c64e04; g0_AC 49df37eb; g0_AC_consistent 2d7c34f0; g0_AD 083937b0.

## Ghi chú rời

**23/10** — Chạy thực nghiệm lại phương pháp CARTE. Bắt đầu EDA: tạo `eda/eda_bon_mien.ipynb` với phần đọc 4 bộ dữ liệu bằng `from pairs import LOADERS` và bảng số dòng, tỷ lệ dương của từng miền.

**24/10** — Hai sai sót của commit `b89d1d3` đã được xử lý: README khôi phục trong `6c056db` (24/10), các file ở thư mục gốc gỡ khỏi Git trong `10207f4` (25/10):

1. Đẩy lên 3 file trùng ở thư mục gốc (`Code_ThucNghiem_CARTE.ipynb`, `bang_so_sanh.csv`, `ket_qua_cua_toi.csv` — đã có trong `kb2b_carte/`), 3 tệp dữ liệu rượu (~4,3 MB) và 1 `.docx` (742 KB).
2. Commit `8823d07` sửa `kb2b_carte/README.md` ngoài phạm vi phần việc, và làm mất một ô tiêu đề của `eda/eda_bon_mien.ipynb` (−48 dòng) do mở notebook trong IDE rồi lưu lại.