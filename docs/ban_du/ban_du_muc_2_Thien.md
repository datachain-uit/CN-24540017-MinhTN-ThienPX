### 2. Dữ liệu bốn miền, khái niệm chung và căn chỉnh C1

Đề tài dùng bốn bộ dữ liệu nhân sự công khai, gọi là bốn miền (Bảng 2.1). Bốn miền khác nhau về quy mô, tỷ lệ nghỉ việc và bản chất dữ liệu: IBM là dữ liệu hư cấu, Job Change phản ánh ý định đổi việc, HR 14.999 là dữ liệu mô phỏng, còn Babushkin là dữ liệu thật nhưng nhãn bị kiểm duyệt (nhãn 0 nghĩa là chưa nghỉ tính đến lúc thu thập). Không thể so sánh PR-AUC trực tiếp giữa các miền vì tỷ lệ nghỉ việc khác nhau, mà PR-AUC của mô hình đoán ngẫu nhiên bằng đúng tỷ lệ này.

**Bảng 2.1.** Bốn miền sau khi loại trùng (`eda/bang1_tong_quan_mien.csv`, `d197041`).

| Miền | Bộ dữ liệu | Dòng gốc | Dòng còn lại | Số cột | Tỷ lệ dương | Bản chất |
|---|---|---|---|---|---|---|
| A | IBM | 1.470 | 1.470 | 30 | 16,12 % | Hư cấu |
| B | Job Change | 19.158 | 19.084 | 11 | 24,92 % | Thật, nhãn là ý định đổi việc |
| C | HR 14.999 | 14.999 | 11.991 | 9 | 16,60 % | Mô phỏng |
| D | Babushkin | 1.129 | 953 | 15 | 51,00 % | Thật, nhãn kiểm duyệt |

Nhóm loại bỏ các dòng trùng toàn bộ đặc trưng trước khi chia tập train/test, để một bản ghi không xuất hiện ở cả hai tập; dữ liệu không có mã nhân viên nên không xác định được hai dòng trùng có phải cùng một người hay không. Nếu không, mô hình có thể ghi nhớ dữ liệu đã thấy và cho kết quả kiểm tra cao không thực tế, dẫn đến đánh giá sai hiệu quả mô hình. Miền HR 14.999 mất 3.008 dòng (20,1 %); miền Job Change mất 74 dòng, trong đó có 25 nhóm cùng hồ sơ nhưng khác nhãn; miền Babushkin loại thêm 163 bản ghi được coi là lặp của cùng một người, tức trùng mọi cột trừ 5 điểm tính cách và có nhãn giống nhau (`pairs.py`).

Khái niệm chung là những thuộc tính có ý nghĩa tương đương và xuất hiện trong cả hai bộ dữ liệu của một cặp, chẳng hạn mức độ hài lòng, thâm niên và mức lương. Cặp IBM ↔ Job Change và IBM ↔ HR 14.999 có 5 khái niệm chung, cặp IBM ↔ Babushkin chỉ có 3. Khi một khái niệm có chiều tác động ngược nhau giữa hai miền, việc chuyển giao gặp khó khăn, vì kiến thức học được từ miền nguồn có thể không còn phù hợp, thậm chí dẫn đến dự đoán sai ở miền đích. Ví dụ, thâm niên ngược chiều ở cặp IBM ↔ HR 14.999: AUC một đặc trưng là 0,355 ở IBM và 0,690 ở HR 14.999 (`eda/bang3_chieu_tac_dong.csv`, `d197041`).

C1 được dùng để đưa các khái niệm có thang đo khác nhau giữa các bộ dữ liệu về cùng một thang, giúp chúng có thể so sánh và chuyển giao. Tuy nhiên, mức độ méo dữ liệu phụ thuộc vào tỷ lệ người có giá trị nhỏ nhất và lớn nhất: tỷ lệ này càng cao thì càng nhiều người bị đẩy về hai cực ±5,2, khiến dữ liệu mất đi sự phân bố hợp lý. Ví dụ, evaluation của IBM chỉ có hai giá trị nên mọi dòng đều ở hai đầu; độ lệch chuẩn sau C1 của khái niệm này là 3,75, trong khi ở HR 14.999 chỉ là 1,17 (mục 6; `eda/bang5_khai_niem_sau_C1.csv`, `d197041`).
