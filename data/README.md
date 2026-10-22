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
