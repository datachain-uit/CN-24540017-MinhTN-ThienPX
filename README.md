# TB-HTL – Học chuyển giao để dự đoán rủi ro nghỉ việc (khóa luận UIT)

Tăng Nhật Minh (24540017), Phạm Xuân Thiên (24540028) – GVHD: ThS. Nguyễn Thị Anh Thư.

Kho này chứa toàn bộ mã, cấu hình và kết quả thô của báo cáo tiến độ (KB1 v2, Cổng 0, ba cặp miền).

## Tái lập nhanh (khoảng 30 giây, không cần dữ liệu gốc)

```bash
pip install -r requirements.txt
bash tai_lap_bang.sh          # tính lại mọi bảng và hình từ results/*/results_*.csv
python kiem_tra_tai_lap.py    # so từng ô với số trong báo cáo: phải in "TẤT CẢ ĐẠT"
```

Bảng ↔ lệnh ↔ file kết quả: xem **[TAI_LAP.md](TAI_LAP.md)**.

## Huấn luyện lại từ đầu

1. Tải 4 bộ dữ liệu vào `data/` và kiểm tra SHA-256 ([data/README.md](data/README.md)).
2. `bash chay_lai_tu_dau.sh` (khoảng 6–7 giờ CPU).
3. TabPFN v2: chạy hai notebook trong `notebooks/` trên Google Colab GPU (`requirements-colab.txt`).

## Nguyên tắc
- Mọi phương pháp dùng chung file chia (`results/*/splits_*_R30.json`, sinh bởi `splits.py`).
- Tên file kết quả chứa mã băm cấu hình (`results_<thí nghiệm>_<mã băm>_<hậu tố>.csv`), cấu hình đầy đủ lưu ở `config_*.json` cạnh kết quả: đổi cấu hình thì ra file mới, không âm thầm dùng lại kết quả cũ.
- Dự đoán thô (`predictions_*.csv.gz`, id, y_true, y_score) không đưa lên Git vì dung lượng (~270 MB); bản đầy đủ: `du_doan_tho_gate0.zip` trên Drive của nhóm.
- Mỗi tuần mỗi thành viên ghi một dòng vào [docs/nhat_ky_tuan.md](docs/nhat_ky_tuan.md).

Chi tiết từng script: [docs/README_chi_tiet.md](docs/README_chi_tiet.md). Phiếu đọc tài liệu: [docs/phieu_doc/](docs/phieu_doc/).
