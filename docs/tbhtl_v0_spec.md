# Đặc tả TB-HTL v0 (chốt trước khi viết mã và trước lần chạy K2 đầu tiên)

Theo review 22/10/2026, mục 6.3 và Phụ lục B1. Phạm vi: **chỉ trong kịch bản K2**, đích IBM (A), nguồn Job Change (B) và HR 14.999 (C) chạy riêng, mức lược đồ L0, L1, L1_noAge và — từ sửa đổi 24/10 — L1_core, L2 (`prereg/k2_khai_niem.json`, `prereg/prereg_k2.yaml`), k ∈ {10, 20, 50, 100}, R = 30 lần chia, M = 5 lần rút trong mỗi lần chia. C3 (tắt ngẫu nhiên nhánh riêng khi tiền huấn luyện) để sau giữa kỳ.

## Mô hình

Với nhân viên *i* của miền đích:

    logit p_i = b + s(z_i) + z_i · w_s + x_i · w_p

| Ký hiệu | Ý nghĩa |
|---|---|
| z_i | khái niệm chung với nguồn ở mức lược đồ đang xét, căn chỉnh C1 |
| s(z_i) | logit của mô hình nguồn: LR (C = 1) học trên toàn bộ miền nguồn với z đã căn chỉnh C1; cố định, dùng làm offset |
| x_i | đặc trưng **chỉ đích có** ở mức lược đồ đang xét: các cột IBM của mức đó trừ các cột đã dùng cho khái niệm chung; số chuẩn hoá z-score, phân loại one-hot, fit trên k mẫu |
| w_s | hệ số hiệu chỉnh nhánh chung, phạt ½·λ_s·‖w_s‖² (λ_s lớn → giữ đúng mô hình nguồn) |
| w_p | hệ số nhánh riêng, phạt ½·λ_p·‖w_p‖², **λ_p = 1 cố định** (bằng mức phạt của LR C = 1 trong Cổng 0) |
| b | chặn, không phạt |

Hàm mục tiêu: tổng log-loss trên k mẫu + hai số hạng phạt; tối ưu bằng L-BFGS-B (mã tham khảo Phụ lục B1 của review).

## Thành phần, ablation và giả thuyết cơ chế

| Thành phần | Cài đặt v0 | Ablation | Giả thuyết (kiểm định) |
|---|---|---|---|
| **C1** căn chỉnh | Chuẩn hoá thứ hạng (QuantileTransformer → normal) các khái niệm chung, fit riêng trên phần train của từng miền, không dùng nhãn (như Cổng 0; giả định N9: tổ chức đích có hồ sơ đầy đủ nhưng ít nhãn) | **−C1**: dùng thang đo của nguồn (z-score fit trên nguồn) | H-C1: zero-shot và TB-HTL ở k ≤ 20 giảm khi bỏ C1 |
| **C2** hai nhánh | Nhánh chung = offset s(z) + hiệu chỉnh w_s; nhánh riêng = x với mức phạt riêng λ_p | **−C2**: bỏ nhánh riêng (x có 0 cột). Ở L0, x vốn có 0 cột nên −C2 trùng bản đầy đủ | H-C2: lợi ích của C2 (đầy đủ − (−C2)) tăng từ L0 → L1 → L2 |
| **C4** độ mạnh chuyển giao theo k | λ_s chọn bằng kiểm định chéo phân tầng trên chính k mẫu, số fold = min(3, n_dương, n_âm), lưới chốt trước {0,1; 1; 10; 100; 10⁴}, tiêu chí **log-loss trung bình trên fold kiểm định; hoà thì lấy λ lớn nhất** (tin nguồn khi dữ liệu không phân biệt được); n_fold < 2 → λ_s = 1. *(Bản chốt 23/10: tiêu chí PR-AUC, hoà → λ nhỏ nhất; đổi theo V1 review 24/10, xem mục cuối)* | **−C4**: λ_s = λ_p = 1 cố định — **trùng ANCHOR_LR** của Cổng 0 | H-C4: λ_s được chọn giảm khi k tăng; TB-HTL không gây chuyển giao âm quá 0,01 PR-AUC ở k = 100 |
| Đối chứng | s(z) từ mô hình nguồn học trên **nhãn nguồn xáo trộn** (seed 0), mọi thứ khác giữ nguyên | — | Lợi ích biến mất → lợi ích đến từ tri thức nguồn, không chỉ từ điều chuẩn |

## Khác gì với các baseline đã có

| Baseline Cổng 0 | Dạng | Khác với TB-HTL v0 |
|---|---|---|
| ANCHOR_LR | offset s(z) + [z, x]·δ, cùng một λ = 1 cho mọi hệ số | TB-HTL tách hai mức phạt và **chọn λ_s theo k** (C4); ANCHOR_LR là ablation −C4 |
| STK_LR | LR trên [x đủ đặc trưng, s(z)] — hệ số của s học tự do | TB-HTL cố định hệ số của s bằng 1 (offset) và neo phần hiệu chỉnh về 0 |
| DAUME_LR | tăng cường đặc trưng chung/riêng, học chung dữ liệu nguồn và đích | TB-HTL không học lại trên dữ liệu nguồn ở bước đích, chỉ dùng s(z) và chọn độ neo theo k |
| RANKAVG-RF | trung bình thứ hạng điểm RF chỉ dùng đích và zero-shot, w chọn bằng kiểm định chéo | TB-HTL là một mô hình tuyến tính duy nhất; RANKAVG-RF trộn điểm sau khi dự đoán |

## Đánh giá (theo tiền đăng ký K2)

- So với: baseline chỉ dùng đích mạnh nhất cùng mức lược đồ (6 baseline + LightGBM, AdaBoost), baseline đích chọn trước bằng kiểm định chéo (M1), 8 baseline chuyển giao, các ablation và đối chứng.
- Chỉ số chính PR-AUC; phụ AUC-ROC, Brier, ECE, F1 và G-Mean (ngưỡng theo tỷ lệ dương của k mẫu). Hiệu bắt cặp theo lần chia (trung bình M = 5 lần rút trước), CI 95% hiệu chỉnh Nadeau–Bengio, Holm trong mỗi họ so sánh, MDE.
- Tiêu chí GO (sửa đổi 24/10, V2): Δ ≥ 0,02 và p sau Holm < 0,05, họ Holm = mọi phương pháp chuyển giao × k ≤ 50 của một (nguồn, mức), cộng điều kiện không chuyển giao âm quá 0,01 ở k = 100. RQ6 so TB-HTL v0 với baseline chuyển giao tốt nhất trong vùng có ích; báo cáo tỷ lệ hoà và phân bố λ_s theo k.
- Rủi ro đã biết (review 22/10): ở L1, Random Forest chỉ dùng đích mạnh hơn LR ở k nhỏ, nên TB-HTL v0 tuyến tính có thể không vượt baseline đích mạnh nhất. Đây là kết quả hợp lệ và phải báo cáo.

## Không đổi sau khi xem kết quả

Mọi thay đổi (lưới λ, tiêu chí chọn λ, cách mã hoá, nhánh riêng phi tuyến…) gọi là v0.1 trở đi và ghi vào `deviations.md` kèm lý do và mã commit.

*Chốt ngày: 23/10/2026 · mã commit: `79a0a4cdb24e8178a5e63dc3c6b013791ed0fab2`*


## Sửa đổi 24/10/2026 (Review-2026-10-24, V1; `deviations.md` mục 10)

| Mục | Bản chốt 23/10 | Sau sửa đổi | Lý do |
|---|---|---|---|
| Tiêu chí chọn λ_s | PR-AUC trung bình trên fold kiểm định | log-loss trung bình trên fold kiểm định | Ở k = 10 (2 mẫu dương, 2 fold) PR-AUC trên fold chỉ nhận vài giá trị: hoà ở 68–78% lần rút (Bảng A4b, review 24/10); log-loss gần như không hoà |
| Khi hoà | λ nhỏ nhất (0,1 – neo yếu nhất) | λ lớn nhất (neo mạnh nhất – tin nguồn) | Quy tắc cũ thiên lệch có hệ thống chống lại chuyển giao ở k nhỏ và làm nhiễu H-C4 |
| Ghi nhận | — | số giá trị λ hoà (`n_hoa`) cho từng lần chọn | Báo cáo tỷ lệ hoà theo k |

Theo quy ước ở mục trên, đổi tiêu chí chọn λ là một thay đổi đặc tả. Thay đổi do GVHD quyết định (quyết định 1, review 24/10) từ chẩn đoán chỉ dùng nhãn của k mẫu huấn luyện, không dùng nhãn test của K2. Tuy vậy, kết quả K2 theo bản chốt 23/10 đã được nhóm xem trước khi nhận review (`deviations.md` mục 9), nên báo cáo trình bày cả hai lần chạy. Tên phương pháp trong mã giữ là `TBHTL`; kết quả của lần chạy theo bản chốt 23/10 ở `results/k2`, sau sửa đổi ở `results/k2_v2`.
