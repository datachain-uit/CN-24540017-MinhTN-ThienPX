# Phiếu đọc: [Baydili & Taşçı, 2025] – Mô hình XAI dự đoán nghỉ việc   (mã trích dẫn: [8])

- Người đọc: Phạm Xuân Thiên   Ngày: 23/10/2026   Thời gian đọc: 1,5 giờ
- Nơi công bố và hạng: *Systems* (MDPI), t.13, số 7, số bài 583. Scimago Q2 – Information Systems and Management (tra 23/10/2026)
- DOI: <https://doi.org/10.3390/systems13070583>. Truy cập mở hoàn toàn, giấy phép CC BY

Trang MDPI chặn truy cập tự động (HTTP 403) nên phần dưới dựng từ siêu dữ liệu và tóm tắt đầy đủ qua OpenAlex, cộng với nhận định trong đánh giá 07/10/2026. MDPI đánh số bài chứ không đánh trang, nên bài này không có khoảng trang; thứ còn thiếu là số mục trong bài để dẫn nguồn.

```bibtex
@article{baydili2025predicting,
  title   = {Predicting Employee Attrition: {XAI}-Powered Models for Managerial Decision-Making},
  author  = {Tanyildizi Baydili, {\.I}rem and Ta{\c{s}}{\c{c}}{\i}, Burak},
  journal = {Systems},
  volume  = {13}, number = {7}, pages = {583}, year = {2025},
  doi     = {10.3390/systems13070583}
}
```

Tác giả: İrem Tanyildizi Baydili và Burak Taşçı, Đại học Fırat, Thổ Nhĩ Kỳ. Công bố 15/07/2025.

## 1. Bài toán

Dự đoán nghỉ việc kèm giải thích mô hình, nhắm vào hai hạn chế mà tác giả nêu ở các phương pháp học máy truyền thống: xử lý kém với dữ liệu mất cân bằng lớp, và thiếu tính minh bạch.

Biến mục tiêu là nghỉ việc đã xảy ra, phân loại nhị phân trên cả hai bộ dữ liệu.

## 2. Dữ liệu

Hai bộ HR công khai. Bộ thứ nhất là IBM HR Analytics, chính là miền A của đề tài. Bộ thứ hai bài gọi là "Kaggle HR Analytics", nhiều khả năng là miền C (`HR_comma_sep.csv`, 14.999 dòng).

Căn cứ xác định bộ thứ hai: tóm tắt nêu ba đặc trưng quan trọng nhất theo SHAP là số dự án, mức độ hài lòng, thâm niên tại công ty. Ba biến này đúng là `number_project`, `satisfaction_level`, `time_spend_company`. Khớp với mục A2 của báo cáo tiến độ 22/10 ghi miền C "đã được [8] và [31] dùng".

Hệ quả: [8] dùng đúng hai miền A và C mà nhóm ghép thành cặp AC, nên là mốc tham chiếu trực tiếp cho cặp AC, nhưng chỉ ở phần trong-miền vì [8] không chuyển giao giữa hai bộ.

Số dòng, số cột và tỷ lệ dương của từng bộ chưa lấy được từ tóm tắt.

## 3. Giao thức đánh giá

| Mục | Bài làm gì | Trang/mục |
|---|---|---|
| Metric báo cáo | Accuracy, Precision, Recall, F1, ROC AUC. Không có PR-AUC | cần số mục |
| Chia dữ liệu | Chưa lấy được. Tóm tắt không nêu tỷ lệ hold-out, số fold, số lần lặp, có phân tầng hay không | cần PDF |
| Mất cân bằng | Sinh dữ liệu tổng hợp bằng GAN, so với ROS, SMOTE, ADASYN và kết luận GAN vượt trội. Về thứ tự: đánh giá 07/10/2026 ghi "GAN TRƯỚC khi chia train/test", đây là nguồn gốc nhận định rò rỉ ở Bảng 1, nhưng chưa xác nhận được bằng câu trích và số mục | ưu tiên cao nhất |
| Chọn siêu tham số | Chưa lấy được | cần PDF |
| Kiểm định thống kê | Chưa lấy được; tóm tắt không nhắc tới | cần PDF |
| Công bố mã, dữ liệu | Bộ dữ liệu là công khai. Phần công bố mã chưa xác nhận được, cần đọc mục *Data Availability Statement* | cần PDF |
| Rủi ro rò rỉ | Nghiêm trọng nếu xác nhận được thứ tự GAN rồi mới chia. Sinh mẫu tổng hợp trên toàn bộ dữ liệu rồi mới chia sẽ khiến mẫu "họ hàng" của mẫu kiểm thử lọt vào tập huấn luyện, giải thích vì sao điểm số cao bất thường | cần số mục |

## 4. Kết quả chính

Mô hình: tiền xử lý bằng label encoding và MinMax scaling, cân bằng lớp bằng GAN, bộ mã hoá Transformer 3 tầng phân lớp nhị phân, SHAP giải thích ở mức toàn cục và cục bộ.

| Bộ dữ liệu | Accuracy | Precision | Recall | F1 | AUC |
|---|---|---|---|---|---|
| IBM | 92,00% | 96,67% | 87,00% | 91,58% | 96,32% |
| Kaggle (≈ miền C) | 96,95% | 97,28% | 96,60% | 96,94% | 99,15% |

Ma trận nhầm lẫn trên IBM: GAN 3 dương tính giả và 13 âm tính giả; ROS 24 và 23; SMOTE 20 và 20. ROC AUC của ROS và SMOTE khoảng 87%, ADASYN 84,24%.

Đặc trưng quan trọng nhất theo SHAP: IBM là mức hài lòng công việc, tuổi, số năm với quản lý hiện tại; Kaggle là số dự án, mức hài lòng, thâm niên tại công ty.

Không dùng làm mốc so sánh được, đây là kết luận đã chốt trong Bảng 1. AUC 99,15% trên bộ HR 14.999 là mức gần như không thể đạt được nếu giao thức sạch; để đối chiếu, mô hình đủ đặc trưng của nhóm trên miền A chỉ đạt AUC-ROC 0,829 và TabPFN v2 đạt 0,840. Precision 96,67% cùng Recall 87,00% trên bộ 16% ca dương cũng bất thường. Nếu GAN thật sự chạy trước khi chia thì toàn bộ bảng kết quả mất giá trị tham chiếu.

## 5. Hạn chế

Do tác giả nêu: cần kiểm chứng khả năng tổng quát hoá trên nhiều ngành nghề khác nhau; cần hướng tới cài đặt nhẹ, chạy thời gian thực.

Do nhóm nhận xét:
- Thứ tự GAN và chia dữ liệu là vấn đề lớn nhất. Nếu sinh mẫu tổng hợp trước khi chia thì mọi con số ở mục 4 đều mất giá trị tham chiếu.
- Không báo cáo PR-AUC. Với dữ liệu mất cân bằng, Accuracy và ROC AUC đều dễ gây hiểu nhầm.
- Không có kiểm định thống kê hay khoảng tin cậy.
- Dùng hai bộ dữ liệu nhưng không có thử nghiệm chuyển giao nào giữa chúng, đúng khoảng trống mà đề tài nhắm tới.
- Cả hai bộ đều là dữ liệu hư cấu hoặc mô phỏng, không có dữ liệu thật.

## 6. Liên hệ với đề tài TB-HTL

Dùng ở Bảng 1, và là ví dụ điển hình về rò rỉ trong phần lập luận vì sao đề tài phải dùng file chia chung và chỉ fit bộ tiền xử lý trên phần train.

Không có chuyển giao xuyên nguồn: hai bộ dữ liệu được xử lý và đánh giá riêng rẽ. Khác TB-HTL ở chỗ [8] cân bằng bằng GAN và nghi ngờ áp dụng trước khi chia, còn nhóm chỉ fit trên phần train từng lần lặp; [8] dùng Accuracy, F1, ROC AUC còn nhóm lấy PR-AUC làm chính; [8] không kiểm định còn nhóm dùng Nadeau–Bengio có hiệu chỉnh cộng Holm.

Vì [8] dùng đúng hai bộ A và C, nó là mốc trong-miền gần nhất với cặp AC. Chênh lệch giữa AUC 99,15% của họ và 0,829 của nhóm trên dữ liệu tương đương chính là minh chứng mạnh nhất cho tầm quan trọng của giao thức chống rò rỉ, nên đưa so sánh này vào phần thảo luận.

Bài truy cập mở, chỉ cần tải PDF. Ưu tiên khi có: xác nhận thứ tự GAN và chia dữ liệu kèm số mục, vì đây là căn cứ cho kết luận rò rỉ ở Bảng 1.
