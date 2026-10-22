# TB-HTL – Học chuyển giao để dự đoán rủi ro nghỉ việc (khóa luận UIT)

Tăng Nhật Minh (24540017), Phạm Xuân Thiên (24540028) – GVHD: ThS. Nguyễn Thị Anh Thư.

Kho này chứa toàn bộ mã, cấu hình và kết quả thô của đề tài.

| Thư mục / file | Nội dung |
|---|---|
| `*.py` ở gốc, `results/` | Thí nghiệm chính: KB1 v2 (2×2), Cổng 0 (G0-1 đến G0-4), ba cặp miền AB/AC/AD, tổng hợp Friedman – Nemenyi |
| `notebooks/` | Notebook Google Colab: tái lập KB1 v2, TabPFN v2 (GPU); `tao_notebook/` sinh lại các notebook |
| `bao_cao/` | Sinh lại báo cáo Word từ kết quả (`bash bao_cao/build_bao_cao.sh`) và các bảng dạng JSON |
| `kb2_levin/` | KB2: tái hiện Levin et al. (ICLR 2023), học chuyển giao với mô hình bảng sâu |
| `kb2b_carte/` | KB2b: tái hiện CARTE trên 3 bộ dữ liệu rượu (Hình 4–5) |
| `ma_cu_cua_nhom/` | Mã cũ của nhóm, lưu để minh chứng |
| `paper/` | Bản nháp bài viết (LaTeX, LNCS) |
| `docs/` | Nhật ký tuần, phiếu đọc tài liệu (Y3), hướng dẫn chi tiết |
| `data/` | Hướng dẫn tải dữ liệu và mã SHA-256 (dữ liệu không đưa lên Git) |

## Tái lập nhanh (khoảng 30 giây, không cần dữ liệu gốc)

```bash
pip install -r requirements.txt
bash tai_lap_bang.sh          # tính lại mọi bảng và hình từ results/*/results_*.csv
python kiem_tra_tai_lap.py    # so từng ô với số trong báo cáo: phải in "TẤT CẢ ĐẠT"
```

Bảng ↔ lệnh ↔ file kết quả: xem **[TAI_LAP.md](TAI_LAP.md)**.

## Sinh lại báo cáo Word

```bash
cd bao_cao && npm install && cd ..
bash bao_cao/build_bao_cao.sh   # -> bao_cao/Bao_cao_tien_do.docx (trùng bản gửi GVHD ngày 21/10)
```

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
