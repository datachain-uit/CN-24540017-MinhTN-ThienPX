### 6. Độ nhạy của căn chỉnh C1

C1 chuyển các giá trị của mỗi khái niệm thành thứ hạng rồi ánh xạ sang phân phối chuẩn. Khi đó những giá trị thấp nhất và cao nhất luôn bị đẩy về hai cực −5,2 và +5,2. Điều này làm dữ liệu bị méo, đặc biệt khi nhiều dòng rơi đúng vào giá trị nhỏ nhất hoặc lớn nhất, vì những người cùng giá trị không còn được phân bố hợp lý ở giữa. Tất cả các phương pháp chuyển giao trong đề tài đều dùng dữ liệu đã qua bước C1. Nếu C1 làm sai lệch dữ liệu đầu vào thì kết quả đánh giá các phương pháp cũng có thể bị ảnh hưởng, khiến khó xác định hiệu quả thực sự của từng phương pháp.

Nhóm xây dựng phiên bản sửa lỗi C1_MID, trong đó những người có cùng giá trị được xếp ở vị trí giữa thay vì bị đẩy về hai cực, và đăng ký trước phép so sánh (commit A `1d99e32`, commit B `7d88d5f`). Kết quả cho thấy điểm số tăng ở cả bốn chiều (Bảng 6.1), nhưng chỉ chiều A→C có mức tăng đủ lớn và đạt tiêu chí đã chốt (|Δ| ≥ 0,02 và p sau Holm < 0,05): PR-AUC tăng từ 0,180 lên 0,211. Chiều B→A cũng tăng nhưng chưa đủ bằng chứng để khẳng định có cải thiện (p sau Holm 0,097).

**Bảng 6.1.** ZS_MID − ZS_C1 theo PR-AUC, 30 lần chia Cổng 0 (`results/c1_do_nhay/c1_phep_chinh.csv`, `41dc832`).

| Chiều | ZS_C1 | ZS_MID | Δ [CI 95%] | p Holm |
|---|---|---|---|---|
| A→B | 0,329 | 0,337 | +0,008 [+0,006; +0,010] | < 0,001 |
| A→C | 0,180 | 0,211 | +0,031 [+0,027; +0,035] | < 0,001 |
| B→A | 0,279 | 0,306 | +0,027 [+0,000; +0,053] | 0,097 |
| C→A | 0,189 | 0,192 | +0,003 [−0,015; +0,020] | 0,76 |

Kết luận chính PIVOT không thay đổi, vì zero-shot ở cả hai bản vẫn kém baseline chỉ dùng đích mạnh nhất ở mọi k ≤ 50 (`results/c1_do_nhay/c1_phep_phu.csv`, `41dc832`). Tuy nhiên, ở nguồn Job Change, mức L0, kết quả lại khác: zero-shot dùng C1_MID (0,306) vượt quy tắc đơn giản −experience (0,284), trong khi zero-shot dùng C1 thì không. Vì vậy, một số kết luận phụ thuộc vào cách căn chỉnh C1, và so sánh này mới chỉ mang tính thăm dò vì được làm sau khi đã xem kết quả.
