# Phiếu đọc: [Baydili & Taşçı, 2025] – Mô hình XAI dự đoán nghỉ việc   (mã trích dẫn trong báo cáo: [8])

- Người đọc: Phạm Xuân Thiên   Ngày: …/10/2026   Thời gian đọc: … giờ
- Nơi công bố và hạng: *Systems* (MDPI), ISSN 2079-8954. Scimago **Q2** – Information Systems and Management (tra …/10/2026, Thiên xác nhận lại trên scimagojr.com)
- DOI / link bản chính thức: <https://doi.org/10.3390/systems13070583>
- Truy cập mở hoàn toàn (gold OA, giấy phép CC BY)

> ⚠️ **Phạm vi của phiếu này.** Trang MDPI chặn truy cập tự động (HTTP 403), nên phần dưới đây dựng từ **siêu dữ liệu và tóm tắt đầy đủ qua OpenAlex**, cộng với nhận định đã có trong đánh giá 07/10/2026 của GVHD.
> **Chưa có số trang.** Bài là truy cập mở — Thiên mở link trên, bấm *Download PDF*, rồi điền số trang vào bảng mục 3.

```bibtex
@article{baydili2025predicting,
  title   = {Predicting Employee Attrition: {XAI}-Powered Models for Managerial Decision-Making},
  author  = {Tanyildizi Baydili, {\.I}rem and Ta{\c{s}}{\c{c}}{\i}, Burak},
  journal = {Systems},
  volume  = {13},
  number  = {7},
  pages   = {583},
  year    = {2025},
  doi     = {10.3390/systems13070583}
}
```

Tác giả: **İrem Tanyildizi Baydili** và **Burak Taşçı**, Đại học Fırat, Thổ Nhĩ Kỳ. Công bố 15/07/2025.

## 1. Bài toán

Dự đoán nghỉ việc kèm giải thích mô hình, nhắm vào hai hạn chế mà tác giả nêu ở các phương pháp học máy truyền thống: **xử lý kém với dữ liệu mất cân bằng lớp**, và **thiếu tính minh bạch**.

Biến mục tiêu là nghỉ việc đã xảy ra (hành vi), phân loại nhị phân trên cả hai bộ dữ liệu.

## 2. Dữ liệu

Hai bộ dữ liệu HR công khai:

| Bộ | Ghi chú |
|---|---|
| IBM HR Analytics | Chính là **miền A** của đề tài (1.470 dòng) |
| "Kaggle HR Analytics" | **Nhiều khả năng là miền C của đề tài** (HR_comma_sep.csv, 14.999 dòng) — xem lập luận dưới |

> 🔍 **Căn cứ xác định bộ thứ hai.** Tóm tắt nêu ba đặc trưng quan trọng nhất theo SHAP của bộ Kaggle là **số dự án, mức độ hài lòng, thâm niên tại công ty**. Ba biến này đúng là `number_project`, `satisfaction_level`, `time_spend_company` — các cột của `HR_comma_sep.csv`. Điều này khớp với mục A2 của báo cáo tiến độ 22/10: *"Dữ liệu mô phỏng, đã được [8] và [31] dùng."*
>
> **Hệ quả cho đề tài:** [8] dùng đúng hai miền A và C mà nhóm đang ghép thành cặp AC. Vì vậy số liệu của [8] là mốc tham chiếu trực tiếp cho cặp AC — **nhưng chỉ ở phần trong-miền**, vì [8] không chuyển giao giữa hai bộ.

Số dòng, số cột và tỷ lệ dương của từng bộ chưa lấy được từ tóm tắt; cần đọc PDF.

## 3. Giao thức đánh giá

| Mục | Bài làm gì | Trang/mục trong bài |
|---|---|---|
| Metric báo cáo | Accuracy, Precision, Recall, F1, **ROC AUC**. Không có PR-AUC | *(cần số trang)* |
| Chia dữ liệu | **Chưa lấy được** — tóm tắt không nêu tỷ lệ hold-out, số fold, số lần lặp, có phân tầng hay không | *(cần PDF)* |
| Mất cân bằng | **Sinh dữ liệu tổng hợp bằng GAN.** So sánh với ROS, SMOTE, ADASYN và kết luận GAN vượt trội. **Trước hay sau khi chia:** đánh giá 07/10/2026 của GVHD ghi **"GAN TRƯỚC khi chia train/test"** — đây là nguồn gốc nhận định rò rỉ ở Bảng 1. **Cần xác nhận bằng số trang trong PDF** | *(cần số trang — ưu tiên cao nhất)* |
| Chọn siêu tham số | **Chưa lấy được** | *(cần PDF)* |
| Kiểm định thống kê, khoảng tin cậy | **Chưa lấy được**; tóm tắt không nhắc tới | *(cần PDF)* |
| Công bố mã, dữ liệu | Bộ dữ liệu là công khai. **Phần công bố mã chưa xác nhận được** | *(cần PDF)* |
| Rủi ro rò rỉ thông tin | **Rò rỉ nghiêm trọng nếu xác nhận được thứ tự GAN → chia.** Sinh mẫu tổng hợp trên toàn bộ dữ liệu rồi mới chia sẽ khiến mẫu "họ hàng" của mẫu kiểm thử lọt vào tập huấn luyện. Điều này giải thích vì sao điểm số cao bất thường | *(cần số trang)* |

## 4. Kết quả chính

Mô hình: tiền xử lý bằng label encoding và MinMax scaling → cân bằng lớp bằng GAN → **bộ mã hoá Transformer 3 tầng** phân lớp nhị phân → SHAP giải thích ở mức toàn cục và cục bộ.

| Bộ dữ liệu | Accuracy | Precision | Recall | F1 | AUC |
|---|---|---|---|---|---|
| IBM | 92,00% | 96,67% | 87,00% | 91,58% | 96,32% |
| Kaggle (≈ miền C) | **96,95%** | 97,28% | 96,60% | 96,94% | **99,15%** |

Đặc trưng quan trọng nhất theo SHAP: IBM — *mức hài lòng công việc, tuổi, số năm với quản lý hiện tại*; Kaggle — *số dự án, mức hài lòng, thâm niên tại công ty*.

**Có dùng làm mốc so sánh được không? — KHÔNG.** Đây là kết luận đã chốt trong Bảng 1 của nhóm, và số liệu củng cố thêm:

- AUC 99,15% trên bộ HR 14.999 là mức gần như không thể đạt được nếu giao thức sạch. Để đối chiếu: trong thực nghiệm của nhóm, mô hình **đủ đặc trưng** trên miền A chỉ đạt AUC-ROC 0,829, và TabPFN v2 đạt 0,840.
- Precision 96,67% với Recall 87,00% trên IBM, một bộ có khoảng 16% ca dương, cũng là mức bất thường.
- Nếu GAN thật sự chạy trước khi chia thì toàn bộ bảng kết quả không dùng làm mốc được.

## 5. Hạn chế

**Do tác giả nêu:**
- Cần kiểm chứng khả năng tổng quát hoá trên nhiều ngành nghề khác nhau.
- Cần hướng tới cài đặt nhẹ, chạy thời gian thực.

**Do nhóm nhận xét:**
- Thứ tự GAN và chia dữ liệu là vấn đề lớn nhất. Nếu sinh mẫu tổng hợp trước khi chia, mọi con số ở mục 4 đều mất giá trị tham chiếu.
- Không báo cáo PR-AUC. Với dữ liệu mất cân bằng, Accuracy và ROC AUC đều dễ gây hiểu nhầm.
- Không có kiểm định thống kê hay khoảng tin cậy.
- Dùng hai bộ dữ liệu nhưng **không có thử nghiệm chuyển giao nào** giữa chúng — đúng khoảng trống mà đề tài nhắm tới.
- Cả hai bộ đều là dữ liệu hư cấu hoặc mô phỏng; không có dữ liệu thật.

## 6. Liên hệ với đề tài TB-HTL

**Dùng ở đâu:** Bảng 1 (tổng quan), và là **ví dụ điển hình về rò rỉ** trong phần lập luận vì sao đề tài phải dùng file chia chung và chỉ fit bộ tiền xử lý trên phần train.

**Có chuyển giao xuyên nguồn không: KHÔNG.** Hai bộ dữ liệu được xử lý và đánh giá riêng rẽ.

**Khác gì với TB-HTL:**

| | Baydili & Taşçı [8] | TB-HTL |
|---|---|---|
| Bộ dữ liệu | IBM + HR 14.999 (≈ miền A và C của nhóm) | 4 miền, 3 cặp chuyển giao |
| Chuyển giao | Không | Có |
| Xử lý mất cân bằng | GAN, **nghi ngờ áp dụng trước khi chia** | Chỉ fit trên phần train từng lần lặp |
| Thước đo | Accuracy, F1, ROC AUC | PR-AUC là chính |
| Kiểm định | Không | Nadeau–Bengio có hiệu chỉnh + Holm |

**Giá trị trực tiếp:** vì [8] dùng đúng hai bộ A và C, nó là mốc *trong-miền* gần nhất với cặp AC của nhóm. Nhưng chênh lệch giữa AUC 99,15% của họ và 0,829 của nhóm trên dữ liệu tương đương chính là minh chứng mạnh nhất cho tầm quan trọng của giao thức chống rò rỉ — nên đưa so sánh này vào phần thảo luận.

---

## Ô cần điền vào `bang1_phuong_phap_luan.csv` (dòng `[8]`)

| Cột | Giá trị |
|---|---|
| `metric_bao_cao` | Accuracy, Precision, Recall, F1, ROC AUC. **Không có PR-AUC.** IBM: 92,00/96,67/87,00/91,58/96,32. Kaggle: 96,95/97,28/96,60/96,94/99,15 |
| `giao_thuc_chia` | **?** — cần PDF |
| `mat_can_bang_truoc_hay_sau_chia` | GAN sinh dữ liệu tổng hợp (so với ROS, SMOTE, ADASYN). GAN **TRƯỚC** khi chia train/test *(theo đánh giá 07/10; cần xác nhận số trang)* |
| `cong_bo_ma` | **?** — cần PDF |
| `rui_ro_ro_ri_ghi_chu` | Rò rỉ: số liệu có nguy cơ bị thổi phồng; không dùng làm mốc. Bộ thứ hai nhiều khả năng là HR 14.999 = miền C của nhóm. AUC 99,15% so với 0,829 của nhóm trên dữ liệu tương đương |
| `trang_nguon` | **Chưa có** — cần mở PDF |

---

## Việc còn lại của phiếu này

Bài **truy cập mở**, chỉ cần mở <https://www.mdpi.com/2079-8954/13/7/583> và bấm *Download PDF*. Khi có PDF, bổ sung:

1. **Ưu tiên cao nhất:** xác nhận **thứ tự GAN và chia dữ liệu**, ghi số trang. Đây là căn cứ cho kết luận rò rỉ ở Bảng 1.
2. Tỷ lệ hold-out, số fold, số lần lặp, có phân tầng hay không
3. Cách chọn siêu tham số
4. Có kiểm định thống kê hay không
5. Mục công bố mã
6. Xác nhận bộ "Kaggle HR Analytics" đúng là `HR_comma_sep.csv` 14.999 dòng
7. Số trang cho từng dòng của bảng mục 3
