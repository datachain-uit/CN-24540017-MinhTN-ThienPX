# 00_contributions.md — Đóng góp, câu hỏi nghiên cứu, giả thuyết và ngưỡng đã chốt

Đề tài: *Ứng dụng học chuyển giao để dự đoán rủi ro nghỉ việc của lực lượng lao động dựa trên các nguồn dữ liệu nhân sự khác nhau*
Nhóm: Tăng Nhật Minh (24540017), Phạm Xuân Thiên (24540028) · GVHD: ThS. Nguyễn Thị Anh Thư

**Ngày chốt:** …/10/2026 · **Mã commit chốt:** (điền sau khi commit) — file này phải được commit **trước** lần chạy K2 đầu tiên (review 18/10, M4; review 22/10, N4). Mọi thay đổi sau ngày chốt ghi vào `deviations.md`.

## 1. Đóng góp (quyết định 2, review 18/10)

Đề tài là **nghiên cứu thực nghiệm có kiểm soát** về điều kiện để chuyển giao xuyên nguồn có ích cho dự đoán nghỉ việc:

- **(a) Giao thức đánh giá** chuyển giao xuyên nguồn: file chia dùng chung, k mẫu lồng nhau, baseline chỉ dùng đích đầy đủ (kể cả TabPFN v2), đối chứng nhãn nguồn xáo trộn, kiểm định hiệu chỉnh và hiệu ứng nhỏ nhất phát hiện được (MDE), tái lập tự động.
- **(b) Phân tích khi nào chuyển giao có ích hoặc có hại**, theo số nhãn đích k, mức trùng khái niệm, ngữ nghĩa nhãn và độ giàu đặc trưng của miền đích.
- TB-HTL là **một phương pháp đơn giản trong bảng so sánh**, chỉ đánh giá trong K2 (quyết định 3, review 22/10), đặc tả ở `docs/tbhtl_v0_spec.md`.

## 2. Quy ước chung

| Mục | Quy ước |
|---|---|
| Chỉ số chính | PR-AUC; phụ: AUC-ROC, Brier, ECE (và F1, G-Mean tại ngưỡng chọn trên k mẫu) |
| Ngưỡng thực tiễn | ΔPR-AUC ≥ **0,02** |
| Kiểm định | hiệu bắt cặp theo lần chia; CI 95% hiệu chỉnh Nadeau–Bengio (n_test/n_train = 0,25); Holm trong mỗi họ so sánh |
| MDE | nửa độ rộng CI = t(0,975; R−1)·SE; MDE (power 80%) = [t(0,975) + t(0,80)]·SE; báo cáo kèm mọi kết luận “không phát hiện” |
| Tiêu chí GO | tồn tại k ≤ 50 mà phương pháp chuyển giao vượt baseline chỉ dùng đích mạnh nhất ≥ 0,02 với CI không chứa 0; ở K2 thêm điều kiện không chuyển giao âm quá 0,01 ở k = 100 |
| Baseline đích | hai cách (M1): **tốt nhất sau khi xem kết quả** (dùng cho GO, thận trọng) và **chọn trước bằng kiểm định chéo trên k mẫu** (dùng để báo cáo), quy tắc ở `prereg/prereg_k2.yaml` |
| Cặp A ↔ D (Babushkin) | **thăm dò**: không dùng cho RQ2, RQ4; tách khỏi tổng hợp chính (quyết định 2, review 22/10) |
| Tổng hợp nhiều chiều | Friedman – Nemenyi ở mức chiều (chỉ mô tả); bản theo khối cặp × chiều × k là phân tích độ nhạy |

## 3. Câu hỏi nghiên cứu, giả thuyết và tiêu chí bác bỏ

Theo bảng mục 6.2 review 18/10, với ba điều chỉnh của review 22/10: (a) RQ4 dùng ba cặp nhưng A ↔ D chỉ là thăm dò; (b) RQ5 là câu hỏi chính của K2; (c) RQ6 (TB-HTL) chỉ đánh giá trong K2.

| Mã | Câu hỏi | Giả thuyết | Thí nghiệm | Tiêu chí bác bỏ | Trạng thái (23/10) |
|---|---|---|---|---|---|
| RQ1 | Mô hình học ở một nguồn có xếp hạng đúng rủi ro ở nguồn khác trên khái niệm chung, khi chưa dùng nhãn đích? | H1: với mô hình có điều chuẩn và căn chỉnh C1, (AUC xuyên − 0,5)/(AUC trong − 0,5) ≥ 0,8 | KB1 v2 (A–B); 2×2 cặp A–C | Tỷ lệ < 0,8 ở cả hai cặp | **Chưa bác bỏ, ủng hộ một phần**: A–B với LR + C1 đạt 0,84 (B→A) và 0,89 (A→B), nhưng không bền theo họ mô hình (XGBoost A→B 0,62; TabPFN v2 B→A 0,61); A–C với tập chính chỉ 0,02–0,33. Chỉ số này đổi so với bản 17/10 (“≥ 90% AUC”) — ghi ở `deviations.md` mục 6, báo cáo cả hai cách |
| RQ2 | Chuyển giao có giúp khi đích ít nhãn? Đến mức k nào? | H2: ở ít nhất một cặp hoặc kịch bản, tồn tại k* với ΔPR-AUC ≥ 0,02 so với baseline đích mạnh nhất (chọn trước) và CI không chứa 0 | Cổng 0 (bổ sung), K1 (A–C), K2 | Không cặp hoặc kịch bản nào đạt; ghi kèm MDE | **Chưa phát hiện lợi ích ≥ MDE ở k ≤ 50** ở A–B và A–C (bảng MDE mục 4). Không viết “bị bác bỏ” |
| RQ3 | Mức trùng khái niệm ảnh hưởng thế nào? | H3: lợi ích tăng theo số khái niệm chung và lượng thông tin của chúng | K1 với tập khái niệm lồng nhau 2 ⊂ 4 ⊂ 7 (thứ tự chốt theo ngữ nghĩa) | Lợi ích không tăng hoặc giảm khi thêm khái niệm | **Sau giữa kỳ** (quyết định 4, review 22/10) |
| RQ4 | Ngữ nghĩa nhãn ảnh hưởng thế nào? | H4: cùng lượng thông tin của không gian chung, lợi ích ở cặp cùng ngữ nghĩa (A–C) lớn hơn cặp khác ngữ nghĩa (A–B) | So sánh A–C với Cổng 0 A–B, ghép theo AUC trong-miền của không gian chung; A–D chỉ thăm dò | Không khác biệt hoặc ngược chiều; ghi giới hạn do khác quần thể | **Chưa ủng hộ**: cả A–B và A–C đều PIVOT; so sánh chưa ghép được theo lượng thông tin |
| RQ5 | Khi miền đích chỉ có lược đồ hồ sơ tối thiểu, chuyển giao có giúp không? **(câu hỏi chính của K2)** | H5: lợi ích tăng khi đặc trưng của đích giảm (L2 → L1 → L0) | K2: đích IBM, nguồn B và C riêng, L0 và L1 (L2 = Cổng 0) | Không mức lược đồ nào đạt ngưỡng của RQ2 | Chưa chạy — tiền đăng ký ở `prereg/prereg_k2.yaml` |
| RQ6 | TB-HTL có vượt baseline chuyển giao đơn giản trong vùng chuyển giao có ích không? **(chỉ trong K2)** | H6: TB-HTL vượt baseline chuyển giao tốt nhất ≥ 0,02 PR-AUC tại vùng k* và không gây chuyển giao âm quá 0,01 ở k = 100 | TB-HTL v0 (C1 + C2 + C4) và ablation −C1, −C2, −C4, đối chứng xáo trộn, trong K2, k ≤ 100 | Không vượt, hoặc chuyển giao âm > 0,01 | Chưa chạy — đặc tả `docs/tbhtl_v0_spec.md`. Lần chạy thăm dò 23/10 không tính (`deviations.md` mục 3) |
| RQ7 | Yếu tố rủi ro có nhất quán giữa các nguồn? | H7: thứ hạng SHAP của khái niệm chung tương quan dương giữa hai miền | KB7 | Tương quan hạng ≤ 0 hoặc CI 95% chứa 0 | Sau giữa kỳ |

## 4. MDE của Cổng 0 (tính lại từ kết quả thô, `python mde_cong0.py`)

PR-AUC, phép so sánh “chuyển giao tốt nhất − baseline đích mạnh nhất”, R = 30, M = 1. Nửa độ rộng CI / MDE (power 80%):

| Chiều | k = 10 | k = 20 | k = 50 |
|---|---|---|---|
| B→A | 0,047 / 0,066 | 0,052 / 0,074 | 0,051 / 0,073 |
| A→B | 0,058 / 0,083 | 0,012 / 0,017 | 0,035 / 0,050 |
| C→A | 0,062 / 0,088 | 0,069 / 0,098 | 0,079 / 0,112 |
| A→C | 0,194 / 0,275 | 0,215 / 0,305 | 0,151 / 0,214 |
| D→A (thăm dò) | 0,063 / 0,090 | 0,061 / 0,087 | 0,039 / 0,056 |
| A→D (thăm dò) | 0,054 / 0,076 | 0,055 / 0,078 | 0,011 / 0,016 |

Trung vị nửa độ rộng 0,057 (khớp Phụ lục A4, review 22/10); trung vị MDE 0,080. Với thiết kế M = 1, lợi ích thật cỡ 0,02–0,04 gần như luôn cho kết quả PIVOT.

**MDE dự kiến cho K2:** không lớn hơn MDE Cổng 0 cùng chiều ở bảng trên (B→A: 0,066–0,074; C→A: 0,088–0,112), vì K2 lấy trung bình M = 5 lần rút trong mỗi lần chia. Thành phần n_test/n_train = 0,25 không giảm theo M, nên mức giảm có giới hạn; MDE thực tế được tính và báo cáo sau khi chạy.

## 5. Kịch bản trước giữa kỳ

- **Cổng 0** (A–B), đã chạy; bổ sung theo mục 6.4 review 22/10 (LightGBM, AdaBoost, Brier, ECE, F1, G-Mean, baseline đích chọn trước, tham số k nhỏ, xáo trộn nhãn đích) — Thiên chủ trì.
- **K1** (A–C, 5 khái niệm tập chính), đã chạy; tập lồng nhau (RQ3) để sau giữa kỳ.
- **K2** (đích nghèo đặc trưng): tiền đăng ký `prereg/prereg_k2.yaml`; danh sách khái niệm `prereg/k2_khai_niem.json`; file chia `prereg/splits_A_R30_M5.json` — Minh chủ trì.

## 6. Sau giữa kỳ

CARTE và DSN (bắt buộc theo Phụ lục D review 07/10); K1 với tập khái niệm lồng nhau và proxy A-distance; Babushkin với nhãn theo mốc cố định (bỏ thâm niên khỏi khái niệm chung); DANN, L2-SP; SHAP, hiệu chỉnh xác suất và phân tích theo nhóm giới (Y4).
