# Dữ liệu

Dữ liệu gốc không đưa lên Git. Tải từ Kaggle, đặt vào `data/` với đúng tên file dưới đây, rồi kiểm tra:

```bash
sha256sum data/*.csv      # so với cột SHA-256
```

| Miền | File | Bộ dữ liệu | Dòng gốc → sau loại trùng | SHA-256 |
|---|---|---|---|---|
| A | `WA_Fn-UseC_-HR-Employee-Attrition.csv` | IBM HR Analytics Employee Attrition & Performance (kaggle.com/datasets/pavansubhasht/ibm-hr-analytics-attrition-dataset) | 1.470 → 1.470 | `a5c31e38bd7fafc9bc333884eb181b06b41b8e5e488e8f7ccb27199fb3be7659` |
| B | `aug_train.csv` | HR Analytics: Job Change of Data Scientists (kaggle.com/datasets/arashnic/hr-analytics-job-change-of-data-scientists) | 19.158 → 19.084 | `8b78da3482032500df40d5359c36ba4a59e28ccd6fc272b050dcf6dee37f114c` |
| C | `HR_comma_sep.csv` | HR Analytics, 14.999 dòng (nhóm điền link Kaggle đã tải) | 14.999 → 11.991 | `2510e274a90547f34c7b0db5a4ab70282c2710eb54252f14921bf980b81a928c` |
| D | `turnover.csv` | Employee turnover – E. Babushkin (nhóm điền link Kaggle đã tải) | 1.129 → 953 | `5098600655806f73c151b30432cf6697437928a30283e88c5c0a1cffeac65ceb` |

Nếu SHA-256 khác (ví dụ Kaggle cập nhật file), kết quả có thể lệch; ghi lại trong `docs/nhat_ky_tuan.md`.
Loại trùng nằm trong `hr_data.py` (A, B) và `pairs.py` (C, D) và được thực hiện trước khi chia.

## Tệp dự đoán thô của Cổng 0 và KB1 (không đưa lên Git)

Trả lời câu 8.1 review 31/10 (nhắc lại ở câu 8.1 review 01/11); chi tiết ở `deviations.md` mục 35. Tệp nằm trên Drive của nhóm, quyền truy cập hạn chế (nhóm và GVHD); chỉ ghi mã tệp.

| Bản | Tên tệp trên Drive, mã tệp | Kích thước (byte) | SHA-256 | Nội dung | Dùng cho |
|---|---|---|---|---|---|
| 1 | `du_doan_tho_gate0_ban1_thieu_TabPFN.zip`, `16-nyUd0TVqPWxbk6PGpNGZGMBg5MClWa` | 267.598.410 | `71f050ce7697e75a150e5d19b8473a4fe73b35c3596f01067cc5c0b5810c6189` | 14 file `predictions_*.csv.gz`; thiếu 5 file TabPFN v2 (Cổng 0 A↔C, A↔D; KB1 AB, AC, AD) | Tải lên Drive 20:25 ngày 22/10 (tài khoản của Minh). Không phải đầu vào của phần bổ sung Cổng 0 |
| 2 | `du_doan_tho_gate0_ban2.zip`, `1u5BJ-xTxVfbgtrRrDtdDJwim73CiJ-Ln` | 273.505.488 | `864e75b4a61455a5cde173fb10065ebcb230fae757da1e83765870e5e0b0c9e9` | 19 file `predictions_*.csv.gz` (đầy đủ) và `BaoCaoNgay_2026-10-30_ThienPX.docx` (không phải dữ liệu; chưa xác định được ai thêm vào tệp nén) | **Đầu vào của phần bổ sung Cổng 0** (`g0_bo_sung.py chi_so`, Thiên, `1b26af6`); Minh gửi Thiên ngày 31/10, tải lên Drive ngày 01/11 |

Nguồn gốc: các file dự đoán được sinh bởi các lần chạy Cổng 0 và KB1 trên máy chủ đám mây dùng cùng trợ lý AI (môi trường chạy của Minh, như `deviations.md` mục 22) và trên Colab (TabPFN v2), rồi nén bằng Info-ZIP 3.0 trên máy chủ đó. 14 file của bản 1 và 19 file dự đoán của bản 2 trùng từng byte với các file cùng tên trong bản nén ngày 21/10/2026, 13:52 UTC còn lưu trên máy chủ (273.469.666 byte, SHA-256 `a0866dbbd8c0f4202c41a68019e0ee8b4bba5f3349b744470dcde403a57008a1`, 19 file). Lý do bản 1 thiếu 5 file TabPFN v2: chưa xác định được.

| Thư mục trong tệp nén | File | Cấu hình |
|---|---|---|
| `results/g0_23` | `predictions_g0_23_6f2142bf_cpu`, `..._44c64e04_extra`, `..._44c64e04_TabPFN`, `predictions_g0_AB_8cbc7623_rankrf` | 6f2142bf, 44c64e04, 8cbc7623 |
| `results/g0_AC` | `predictions_g0_AC_49df37eb_cpu`, `..._rankrf`, `..._TabPFN` (chỉ bản 2) | 49df37eb |
| `results/g0_AC_consistent` | `predictions_g0_AC_2d7c34f0_cpu`, `..._rankrf` | 2d7c34f0 |
| `results/g0_AD` | `predictions_g0_AD_083937b0_cpu`, `..._rankrf`, `..._TabPFN` (chỉ bản 2) | 083937b0 |
| `results/kb1_v2`, `results/kb1_v2_kaggle` | `predictions_kb1v2_99d14779` (hai bản giống nhau) | 99d14779 |
| `results/kb1_AB`, `kb1_AC`, `kb1_AD` | `predictions_kb1_AC_40a7ef2e_cpu`, `predictions_kb1_AD_4c085b4a_cpu`; các file `_TabPFN` của AB (cf3e982a), AC, AD chỉ có ở bản 2 | 40a7ef2e, 4c085b4a, cf3e982a |

**Danh mục mã băm từng file** (V1, quyết định 3 review 01/11 bản chiều; `tools/danh_muc_zip.py`): `data/du_doan_tho_ban1_sha256.txt` (14 dòng), `data/du_doan_tho_ban2_sha256.txt` (20 dòng). Mỗi dòng: SHA-256, kích thước, giờ ghi trong tệp nén, hệ điều hành đã tạo mục, tên file. Tên tệp trên Drive đổi ngày 02/11 theo review 01/11 (bản 2 trước đó tên `du_doan_tho_gate0_ban2.zip.zip`, bản 1 tên `du_doan_tho_gate0.zip`); mã tệp không đổi.

Theo danh mục: 19 mục dự đoán của bản 2 và 14 mục của bản 1 do Info-ZIP tạo trên hệ Unix; mục `BaoCaoNgay_2026-10-30_ThienPX.docx` trong bản 2 do một công cụ trên **Windows** thêm vào, giờ ghi trong tệp nén 2026-10-30 21:59:48 (giờ của máy Windows). 273.467.035 byte đầu của bản 2 trùng bản nén ngày 21/10 trên máy chủ (`a0866dbb…`): bản 2 là bản đó cộng thêm file báo cáo. Ai thêm file báo cáo: không xác định được từ danh mục.
