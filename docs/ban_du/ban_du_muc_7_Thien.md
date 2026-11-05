### 7. TrAdaBoost và đối chiếu với luận văn UNICAMP

Công trình gần đề tài nhất là luận văn UNICAMP 2025 [44] sử dụng TrAdaBoost, nên nhóm chạy phương pháp này theo giao thức của đề tài để so sánh trực tiếp, trong một họ Holm riêng gồm 18 phép (`prereg/prereg_trada.yaml`, `ac3193c`). Kết quả cho thấy 15/18 phép TrAdaBoost kém baseline chỉ dùng đích mạnh nhất có ý nghĩa thống kê và không có phép nào đạt (Bảng 7.1).

**Bảng 7.1.** TRADA − baseline chỉ dùng đích mạnh nhất theo PR-AUC, họ Holm 18 phép, k = 10, 20, 50 (`results/trada/trada_kiem_dinh.csv`, `d8c535a`).

| Thiết lập | Chiều | Δ thấp nhất đến cao nhất | Số phép kém có ý nghĩa | Số phép đạt |
|---|---|---|---|---|
| Cổng 0 | B→A | −0,198 đến −0,113 | 3/3 | 0/3 |
| Cổng 0 | C→A | −0,224 đến −0,141 | 3/3 | 0/3 |
| Cổng 0 | A→B | −0,135 đến −0,063 | 2/3 | 0/3 |
| Cổng 0 | A→C | −0,270 đến −0,202 | 3/3 | 0/3 |
| K2-L0 | B→A | −0,037 đến +0,002 | 1/3 | 0/3 |
| K2-L0 | C→A | −0,082 đến −0,056 | 3/3 | 0/3 |
| Tổng | | | 15/18 | 0/18 |

**Bảng 7.2.** Đối chiếu giao thức với luận văn [44] (số của luận văn theo phiếu đọc `docs/phieu_doc/[44]_Pereira_2025_UNICAMP.md`, `faa0f6b`).

| Khía cạnh | Luận văn [44] | Đề tài |
|---|---|---|
| Không gian đặc trưng | Hai bộ cùng cấu trúc, dùng 6 thuộc tính chung (Bảng 4.1, tr. 37) | Khái niệm chung giữa các lược đồ khác nhau, căn chỉnh C1 |
| Loại trùng | Không; bộ HR 14.999 có 20,1 % dòng trùng hoàn toàn | Có, trước khi chia |
| Số nhãn đích | ρ = 1–25 %; ρ = 1 %: khoảng 95–150 nhãn (mục 4.2, 4.4.3) | k = 10–100; Cổng 0 đến k = 500 (5,2 % phần huấn luyện của HR 14.999) |
| Metric | Accuracy, precision, recall, F1 ở ngưỡng mặc định (Bảng 5.1–5.5) | PR-AUC là chỉ số chính; F1 ở ngưỡng theo tỷ lệ dương của k mẫu, chỉ để mô tả |
| Baseline chỉ dùng nhãn đích | Không có | Mạnh nhất cùng k, gồm TabPFN v2 |
| Đánh giá TrAdaBoost | Trên chính miền đích đã dùng để huấn luyện (mục 4.4.3, tr. 44) | Tập test tách riêng, 30 lần chia |
| Kiểm định | Đánh dấu có ý nghĩa ở mức 95 %, không nêu phép kiểm định (Bảng 5.1) | CI hiệu chỉnh Nadeau–Bengio, Holm |
| Kết quả TrAdaBoost | F1 0,848 (bộ 1 → bộ 2) và 0,700 (bộ 2 → bộ 1) (Bảng 5.5), cao hơn Random Forest tinh chỉnh với 1 % nhãn: 0,837 và 0,551 (Bảng 5.3–5.4) | 0/18 phép đạt; 15/18 phép kém có ý nghĩa (Bảng 7.1) |

**Bảng 7.3.** Các ô gần luận văn nhất: A→C, đích HR 14.999, trung bình 30 lần chia. Không có ô suy biến. TRADA: `results/trada/results_trada_AC_ac4aaa4c_cpu.csv` (`faa0f6b`); RF, TabPFN v2: `results/g0_bo_sung/chi_so_tu_du_doan_tho.csv` (`1b26af6`).

| k | Tỷ lệ phần huấn luyện | TRADA PR-AUC | TRADA F1 | RF PR-AUC | RF F1 | TabPFN v2 PR-AUC | TabPFN v2 F1 |
|---|---|---|---|---|---|---|---|
| 100 | 1,0 % | 0,770 | 0,730 | 0,873 | 0,791 | 0,919 | 0,862 |
| 200 | 2,1 % | 0,842 | 0,799 | 0,925 | 0,862 | 0,945 | 0,900 |
| 500 | 5,2 % | 0,859 | 0,812 | 0,950 | 0,908 | 0,957 | 0,919 |

TabPFN v2 là baseline chỉ dùng đích mạnh nhất theo PR-AUC ở cả ba ô. Điểm RF và TabPFN v2 tính từ dự đoán thô làm tròn 5 chữ số (`deviations.md` mục 37b).

Ba phép còn lại không phân biệt được với baseline: A→B, k = 10 (Δ −0,063, p Holm 0,619, MDE80 0,142) và K2-L0 B→A, k = 10 và 20 (Δ +0,002 và −0,006, p Holm 1,000, MDE80 0,036 và 0,027). MDE80 tính theo công thức của `mde_cong0.py` từ khoảng tin cậy trong `results/trada/trada_kiem_dinh.csv`.

Kết quả của đề tài và của luận văn chưa thể kết luận là mâu thuẫn, vì hai bên sử dụng cách đánh giá và thiết lập thí nghiệm khác nhau (Bảng 7.2). Khác biệt đáng chú ý nhất là TrAdaBoost trong luận văn được đánh giá trên chính dữ liệu đã dùng để huấn luyện, khiến kết quả có thể bị thổi phồng. Trong khi đó, khi đánh giá trên tập test tách riêng, ở k = 100 PR-AUC của TRADA (0,770) thấp hơn TabPFN v2 (0,919) là 0,149 (Bảng 7.3).
