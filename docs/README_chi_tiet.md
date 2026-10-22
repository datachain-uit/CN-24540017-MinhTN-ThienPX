# Cổng 0 – KB1 v2 (G0-1): thực nghiệm 2×2 tách mất đặc trưng và lệch miền

Mã cho mục B1.3 và Phụ lục A5.1 của báo cáo sửa theo đánh giá GVHD (07/10/2026).

| File | Chức năng |
|---|---|
| `hr_data.py` | Đọc IBM HR (miền A) và Job Change (miền B), loại dòng trùng của B, ánh xạ khái niệm chung (giới tính, học vấn, kinh nghiệm, đào tạo, tuỳ chọn thâm niên) |
| `splits.py` | File chia dùng chung: train/test 80/20, k mẫu lồng nhau (10 ⊂ 20 ⊂ 50 …), R lần, mỗi tập ít nhất 1 mẫu dương |
| `kb1_v2.py` | Chạy KB1 v2: LR, RF, RF(min_samples_leaf=50), XGBoost × mã hoá (thang nguồn / căn chỉnh theo miền C1) × trong-miền / xuyên-miền; lưu kết quả, dự đoán thô, sanity check, cấu hình có mã băm |
| `kb1_v2_summary.py` | Bảng chính, corrected resampled t-test (Nadeau–Bengio), CI 95% có hiệu chỉnh, Holm, bảng độ nhạy, hình |
| `so_sanh_kb1.py` | So sánh lần chạy trên file Kaggle với lần chạy trong báo cáo, kết luận KHỚP / LỆCH NHỎ / LỆCH |
| `kb1_tai_dung.py` | Truy vết bảng KB1 cũ (mã gốc đã mất): Random Forest mặc định với 5 cách mã hoá 4 khái niệm chung; kết quả ở `results/kb1_tai_dung.csv` (báo cáo mục A5.1c) |
| `g0_23.py` | Cổng 0: G0-2 (LR, RF, XGBoost, CatBoost, stacking; TabPFN v2 qua `--only TabPFN --device cuda`), G0-3 (7 baseline chuyển giao), G0-4 (đối chứng xáo trộn nhãn nguồn); R = 30, k ∈ {10, …, 500, toàn bộ} |
| `g0_decision.py` | Áp tiêu chí GO/PIVOT, kiểm định bắt cặp có hiệu chỉnh, Holm, phân tích cùng họ, đối chứng, Hình 6–7 |
| `results/g0_23/` | Kết quả Cổng 0 ngày 17/10/2026: file chia, kết quả, dự đoán thô, cấu hình, bảng kiểm định, `g0_tom_tat.txt`, `g0_ket_luan.txt` (PIVOT cả hai chiều) |
| `results/kb1_v2/` | Kết quả lần chạy cfg `99d14779` (10 lần chia) |

## Chạy lại

```bash
pip install -r requirements.txt
# Đặt file Kaggle gốc vào data/: WA_Fn-UseC_-HR-Employee-Attrition.csv và aug_train.csv
# Ghi ra thư mục MỚI: mã cấu hình chỉ phụ thuộc tham số, nên cùng R = 10 sẽ trùng tên 99d14779 và đè kết quả cũ
python kb1_v2.py --ibm data/WA_Fn-UseC_-HR-Employee-Attrition.csv --jc data/aug_train.csv --out results/kb1_v2_kaggle
python kb1_v2_summary.py results/kb1_v2_kaggle/results_kb1v2_99d14779.csv
python so_sanh_kb1.py results/kb1_v2/results_kb1v2_99d14779.csv results/kb1_v2_kaggle/results_kb1v2_99d14779.csv
```

Lưu ý dữ liệu: lần chạy trong báo cáo dùng bản sao IBM HR trên GitHub (IBM/employee-attrition-aif360, 1.470 × 35)
và Job Change trong gói R dlookr (19.158 dòng). Nhóm cần chạy lại trên file tải từ Kaggle để xác nhận số liệu.
TabPFN v2 chạy trên Colab GPU (notebook chay_TabPFN_v2_R1_R3_Colab.ipynb, 21/10/2026); kết quả ở `results/kb1_AB/`.

## Cổng 0 (G0-2 đến G0-4)

```bash
python g0_23.py --ibm data/WA_Fn-UseC_-HR-Employee-Attrition.csv --jc data/aug_train.csv             # phần CPU (~12 phút)
python g0_23.py --ibm ... --jc ... --only CAT STACK RANKAVG ANCHOR_LR ZS_SHUF STK_LR_SHUF RANKAVG_SHUF ANCHOR_LR_SHUF --suffix extra   # ~35 phút
python g0_23.py --ibm ... --jc ... --only TabPFN --device cuda                                        # Colab GPU
python g0_decision.py results/g0_23                                                                   # gộp mọi file kết quả, in kết luận
```

> Dự đoán thô (`predictions_*.csv.gz`, khoảng 100 MB) được tách sang `du_doan_tho_gate0.zip`; giải nén chồng lên thư mục này để có đủ.

## Nhiều cặp miền (R3) và TabPFN v2 trong 2×2 (R1) – cập nhật 21/10/2026

| File | Chức năng |
|---|---|
| `pairs.py` | Bộ đọc 4 miền (A IBM, B Job Change, C HR 14.999, D Babushkin), bảng ánh xạ khái niệm chung theo cặp AB / AC / AD. Babushkin: loại 13 dòng trùng và 163 bản ghi lặp cùng một người (trùng mọi cột trừ 5 điểm tính cách, nhãn luôn giống nhau) |
| `kb1_pair.py` | Thí nghiệm 2×2 cho cặp bất kỳ; `--only TabPFN --device cuda` cho TabPFN v2 (tự rút 10.000 dòng khi tập huấn luyện lớn hơn). Với AB cho kết quả trùng `kb1_v2.py` |
| `g0_pair.py` | Cổng 0 (G0-2/3/4) cho cặp bất kỳ. Với AB cho kết quả trùng `g0_23.py` |
| `kb1_pair_summary.py` | Bảng chính, kiểm định có hiệu chỉnh, độ nhạy, hình cho một cặp |
| `g0_decision.py results/g0_AD AD` | Kết luận GO/PIVOT cho một cặp |
| `results/kb1_AB/` | TabPFN v2 trong 2×2 của AB (Colab T4, 21/10); gộp với `results/kb1_v2/` |
| `results/kb1_AC/`, `results/g0_AC/`, `results/g0_AC_consistent/` | Cặp IBM ↔ HR 14.999 (CPU + TabPFN v2) |
| `results/kb1_AD/`, `results/g0_AD/` | Cặp IBM ↔ Babushkin (CPU + TabPFN v2) |
| `pairs_synthesis.py`, `results/tong_hop_cap/` | Tổng hợp ba cặp; Friedman – Nemenyi chính (41 khối, 14 phương pháp gồm TabPFN v2) và phụ (42 khối, bỏ TabPFN v2) |

```bash
python kb1_pair.py --pair AD --data A=data/ibm.csv D=data/turnover.csv
python g0_pair.py  --pair AD --data A=data/ibm.csv D=data/turnover.csv --only LR RF XGB CAT STACK ZS STK_LR STK_XGB OFF_XGB DAUME_LR RANKAVG ANCHOR_LR ZS_SHUF STK_LR_SHUF RANKAVG_SHUF ANCHOR_LR_SHUF --suffix cpu
python kb1_pair_summary.py --pair AD "results/kb1_AD/results_kb1_AD_*.csv"
python g0_decision.py results/g0_AD AD
python kb1_pair_summary.py --pair AB results/kb1_v2/results_kb1v2_99d14779.csv results/kb1_AB/results_kb1_AB_cf3e982a_TabPFN.csv --out results/kb1_AB/tong_hop
python pairs_synthesis.py --out results/tong_hop_cap
```
