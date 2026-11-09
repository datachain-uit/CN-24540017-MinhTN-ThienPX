### 8. Hạn chế (nháp phần sự kiện, Minh và Thiên sửa, thêm nhận định)

**C1 và lỗi ±5,2.** C1 đẩy giá trị nhỏ nhất và lớn nhất của một khái niệm về ±5,2, làm phình phương sai ở những khái niệm có nhiều dòng ở hai đầu (mục 5.4, mục 6). Thay bằng C1_MID, PR-AUC của zero-shot tăng ở cả bốn chiều, chỉ A→C đạt tiêu chí đã chốt (`results/c1_do_nhay/c1_phep_chinh.csv`, `41dc832`). Kết luận chính PIVOT không đổi, nhưng các so sánh ở mức L0 phụ thuộc vào cách căn chỉnh; so sánh với quy tắc −experience là thăm dò, làm sau khi xem kết quả (`deviations.md` mục 21).

**Khái niệm chung ánh xạ thủ công.** Các tập khái niệm được nhóm chốt trước trong `prereg/k2_khai_niem.json`; ánh xạ giữa các lược đồ không kiểm chứng được bằng dữ liệu, và có khái niệm ngược chiều giữa hai miền (thâm niên ở cặp IBM ↔ HR 14.999, mục 2). Phân tích độ nhạy về khái niệm chung làm sau giữa kỳ.

**Nhãn kiểm duyệt ở miền D.** Nhãn 0 của Babushkin là chưa nghỉ tính đến lúc thu thập, nên cặp A↔D chỉ là thăm dò (`deviations.md` mục 2).

**Dữ liệu hư cấu hoặc mô phỏng.** IBM là dữ liệu hư cấu, HR 14.999 là dữ liệu mô phỏng; kết quả trên các miền này chưa khẳng định được hành vi của dữ liệu nhân sự thật.

**Độ lạc quan của baseline chọn sau.** Baseline mạnh nhất của Cổng 0 được chọn sau khi xem kết quả trên tập test, nên có lợi cho phía không chuyển giao. PRESEL, chọn bằng kiểm định chéo trên k mẫu, thấp hơn baseline này ở 12/12 ô k ≤ 50, từ 0,004 đến 0,050, trung bình 0,019 (Bảng 4.3, `1b26af6`). Danh sách ứng viên của PRESEL không có TabPFN v2 và STACK, nên chênh lệch này không chỉ do thời điểm chọn. So sánh chuyển giao − PRESEL ở Cổng 0 không có trong tiền đăng ký nên chưa chạy.

**Mức tái lập.** Xem Bảng 8.1. Độ nhạy C1 trùng từng giá trị; TrAdaBoost và phần bổ sung Cổng 0 chạy trên máy cá nhân chỉ tái lập được về thống kê, cùng kết luận. Kiểm tra đường ống đích B trên máy Thiên lệch 2,25e-7, vượt ngưỡng 1e-9, kể cả khi đã dùng đúng phiên bản gói; lần chạy trên Linux của GVHD đạt, nên khác biệt nằm ở nền tảng, chưa tách được thành phần cụ thể (`deviations.md` mục 29, 38, 42, 43).

**Dòng thêm vào Bảng 8.1 (V6 review 07/11):** Kiểm tra đường ống đích B | Linux (GVHD, review 31/10 A3): 42/42, lệch lớn nhất 8,3e-17, ĐẠT; Windows (máy Thiên, 31/10, 05/11, 06/11): lệch 2,25e-7 ở một giá trị, KHÔNG ĐẠT ngưỡng 1e-9 | `33b16ef`, `8d0cda7` | Cùng phiên bản gói, khác nền tảng; GVHD khép việc tìm nguyên nhân (quyết định 5 review 07/11) | Coi là đạt theo lần chạy của GVHD (`deviations.md` 38, 42, 43)

**Các mục deviations liên quan đến kết quả được trích:** 2 (A↔D thăm dò), 17 (ô suy biến K2), 21 (độ nhạy C1), 23 và 27 (TrAdaBoost, máy chạy), 24 và 26 (CORAL), 28–30 (phần bổ sung Cổng 0), 37 (đính chính, lệch PR-AUC 0,0107), 38 và 41–43 (đích B, CRLF, môi trường), 39 (tệp đầu vào), 40 (ô suy biến F1, G-Mean).

### Bảng 10.2. Hướng 2 – Thiên

| Mục | Nội dung |
|---|---|
| Câu hỏi | Khi đổi mốc so sánh của Cổng 0 từ baseline mạnh nhất chọn sau sang PRESEL (chọn trước, không nhìn tập test), kết luận PIVOT của 4 chiều chính ở k ≤ 50 có đổi không? |
| Bằng chứng hiện có | PRESEL thấp hơn baseline mạnh nhất chọn sau ở 12/12 ô k ≤ 50, từ 0,004 đến 0,050, trung bình 0,019 (`results/g0_bo_sung/results_moi_[A-D].csv`, `1b26af6`; Bảng 4.3). Đây là so sánh mô tả, làm sau khi xem kết quả. Δ tốt nhất của 4 chiều chính so với baseline chọn sau nằm trong −0,088 đến +0,012 (Bảng 4.1, `d03cd28`). So sánh chuyển giao − PRESEL chưa được chạy. |
| Giả thuyết | Với PRESEL làm mốc, cả 4 chiều chính vẫn PIVOT. Giả thuyết sai nếu có chiều đạt Δ ≥ 0,02 và p Holm < 0,05. |
| Thí nghiệm tối thiểu | Dữ liệu: 4 chiều chính A↔B, A↔C. Phương pháp: 8 phương pháp chuyển giao và TrAdaBoost so với PRESEL; baseline mạnh nhất chọn sau (gồm TabPFN v2) báo cáo cạnh để đối chiếu. 30 lần chia của Cổng 0, k = 10, 20, 50, PR-AUC, hiệu bắt cặp theo lần chia. Không huấn luyện lại phương pháp cũ; chỉ tính lại từ kết quả đã commit. |
| Chi phí | Tiền đăng ký và kiểm tra khoảng nửa ngày. Tính lại từ kết quả đã có dưới 1 giờ CPU. Nếu chạy lại PRESEL trong môi trường chuẩn: lần chạy `chi_so` và `moi` bốn đích trước đây hết 80 phút trên máy cá nhân (`deviations.md` mục 30). |
| Tiêu chí thành công | Chốt trước, không nới: Δ ≥ 0,02 và p Holm < 0,05 như GO của Cổng 0, cùng cách lập họ Holm; CI 95 % hiệu chỉnh Nadeau–Bengio; báo MDE. |
| Rủi ro | Rủi ro lớn nhất là hướng được đề xuất sau khi đã xem Bảng 4.3, nên phải tiền đăng ký trước khi chạy. PRESEL không trùng từng giá trị giữa các máy (Bảng 8.1), và MDE ở Cổng 0 khá lớn (trung vị 0,080, Bảng 4.2) nên có thể không phát hiện được chênh lệch nhỏ. Nếu kết quả âm: báo kết quả kèm MDE và khép hướng này, không đổi tiêu chí. |
