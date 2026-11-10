### 8. Hạn chế (phần của Thiên)

**C1 và lỗi ±5,2.** Khi đổi C1 sang C1_MID, zero-shot vẫn thua baseline mạnh nhất, nên kết luận PIVOT không đổi. Chỉ một số so sánh ở mức L0, như so với quy tắc −experience, phụ thuộc vào cách căn chỉnh, và có một so sánh phụ đổi chiều; ý này đã nêu ở mục 6 (`results/c1_do_nhay/`, `41dc832`; `deviations.md` mục 21).

**Khái niệm chung ánh xạ thủ công.** Ánh xạ khái niệm chung do nhóm tự làm bằng tay, không có cách kiểm chứng bằng dữ liệu. Có khái niệm còn tác động ngược chiều giữa hai miền, như thâm niên ở IBM và HR 14.999 (mục 2). Việc chốt trước (`prereg/k2_khai_niem.json`) chỉ ngăn việc sửa luật sau khi xem kết quả, chứ không làm phép ánh xạ đúng hơn.

**Nhãn kiểm duyệt ở miền D.** Nhãn 0 ở Babushkin chỉ có nghĩa là chưa nghỉ tính đến lúc thu thập, sau đó người đó vẫn có thể nghỉ. Vì nhãn không chắc chắn như vậy, cặp A↔D chỉ dùng để thăm dò, không đưa vào kết luận chính (`deviations.md` mục 2).

**Dữ liệu hư cấu hoặc mô phỏng.** IBM là dữ liệu hư cấu, HR 14.999 là dữ liệu mô phỏng, và nhóm không có dữ liệu thật của tổ chức nào (mục 9). Vì vậy kết luận chỉ đúng trên các bộ dữ liệu công khai này, chưa nói được gì cho dữ liệu nhân sự thật của một doanh nghiệp.

**Độ lạc quan của baseline chọn sau.** Baseline mạnh nhất của Cổng 0 được chọn sau khi đã nhìn kết quả trên tập test nên được lợi; PRESEL phải chọn trước và chỉ dựa vào k mẫu, nên thấp hơn từ 0,004 đến 0,050 ở k ≤ 50 (Bảng 4.3, `1b26af6`).

**Mức tái lập và kiểm tra đích B.** Kiểm tra đường ống đích B trên máy Thiên lệch 2,25e-7, nhỏ hơn rất nhiều so với chữ số thứ ba mà các bảng báo cáo, và đến từ khác biệt nền tảng giữa Windows và Linux: cùng phiên bản gói, lần chạy trên Linux của GVHD đạt 42/42. Không số nào đã công bố bị đổi; GVHD đã khép việc này (quyết định 5 review 07/11), ngưỡng 1e-9 giữ nguyên, không nới (`deviations.md` mục 42, 43; Bảng 8.1).

**Dòng thêm vào Bảng 8.1 (V6 review 07/11):** Kiểm tra đường ống đích B | Linux (GVHD, review 31/10 A3): 42/42, lệch lớn nhất 8,3e-17, ĐẠT; Windows (máy Thiên, 31/10, 05/11, 06/11): lệch 2,25e-7 ở một giá trị, KHÔNG ĐẠT ngưỡng 1e-9 | `33b16ef`, `8d0cda7` | Cùng phiên bản gói, khác nền tảng; GVHD khép việc tìm nguyên nhân (quyết định 5 review 07/11) | Coi là đạt theo lần chạy của GVHD (`deviations.md` 38, 42, 43)

**Các mục deviations liên quan đến kết quả được trích:** 2 (A↔D thăm dò), 17 (ô suy biến K2), 21 (độ nhạy C1), 23 và 27 (TrAdaBoost, máy chạy), 24 và 26 (CORAL), 28–30 (phần bổ sung Cổng 0), 37 (đính chính, lệch PR-AUC 0,0107), 38 và 41–43 (đích B, CRLF, môi trường), 39 (tệp đầu vào), 40 (ô suy biến F1, G-Mean).

### Bảng 10.2. Hướng 2 – Thiên

| Mục | Nội dung |
|---|---|
| Câu hỏi | Hướng này không so hai baseline với nhau mà hỏi kết luận chuyển giao có giữ được không khi đổi mốc. Mốc cũ của Cổng 0 là baseline mạnh nhất chọn sau nên được lợi; đổi sang PRESEL chọn trước thì mốc công bằng hơn. Câu hỏi: khi đó 4 chiều chính ở k ≤ 50 có còn PIVOT không? |
| Bằng chứng hiện có | PRESEL thấp hơn baseline mạnh nhất chọn sau từ 0,004 đến 0,050 ở k ≤ 50 (Bảng 4.3, `results/g0_bo_sung/results_moi_[A-D].csv`, `1b26af6`); đây là so sánh mô tả, làm sau khi xem kết quả. Ở K2, họ “chuyển giao − đích chọn trước” cho 0/276 phép đạt (`results/k2_v2/k2_kiem_dinh.csv`, `b61ccb3`; mục 8). Tiền đăng ký của Cổng 0 không có phép so với PRESEL, nên Cổng 0 chưa từng so. Cổng 0 cũng khác K2: có 4 chiều, xét cả hai chiều đích, và mốc chọn sau có cả TabPFN v2; vì vậy kết quả 0/276 ở K2 không thay được câu trả lời cho Cổng 0. |
| Giả thuyết | Với PRESEL làm mốc, 4 chiều vẫn PIVOT. Giả thuyết sai nếu có chiều đạt Δ ≥ 0,02 và p Holm < 0,05. Khoảng tin cậy chứa 0 chỉ có nghĩa là chưa phát hiện được khác biệt, không phải là không có khác biệt; muốn khẳng định chuyển giao không có lợi thì phải chốt trước biên ±0,02 và dùng kiểm định tương đương hai phía (TOST). |
| Thí nghiệm tối thiểu | Kết quả chuyển giao và PRESEL đều đã có, chỉ cần tính hiệu bắt cặp (chuyển giao − PRESEL) ở 4 chiều chính, k = 10, 20, 50, 30 lần chia, PR-AUC, không huấn luyện lại. Phương pháp cũ chạy trên máy chủ của Minh còn PRESEL chạy trên máy Thiên, nên phải kiểm hai bên dùng đúng cùng lần chia rồi mới ghép, và ghi rõ mức tái lập. |
| Chi phí | Tính lại từ file kết quả có sẵn, dưới 1 giờ CPU. Nếu phải chạy lại PRESEL thì thêm khoảng 80 phút (`deviations.md` mục 30). |
| Tiêu chí thành công | Giữ đúng như phép GO của Cổng 0, không nới ngưỡng nào. |
| Rủi ro | Hướng này nghĩ ra sau khi đã thấy Bảng 4.3, nên phải tiền đăng ký trước khi tính. MDE ở Cổng 0 có trung vị 0,080 (Bảng 4.2), khá lớn so với ngưỡng 0,02. Nếu kết quả âm thì báo kèm MDE và khép hướng, không nói thành “đã chứng minh không có lợi”. |
