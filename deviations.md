# Nhật ký sai lệch so với kế hoạch và tiền đăng ký

Mỗi mục: ngày, nội dung, lý do, ảnh hưởng tới kết luận, mã commit. Ghi cả các lần chạy thăm dò để người đọc biết những gì đã được xem trước khi chốt.

| # | Ngày | Nội dung | Lý do | Ảnh hưởng | Commit |
|---|---|---|---|---|---|
| 1 | 21/10/2026 | Cặp A ↔ C: tập khái niệm “consistent” (bỏ thâm niên) chọn **sau** khi xem chiều tác động đơn biến | Thâm niên ngược chiều giữa A (AUC 0,35) và C (0,69) | Chỉ là phân tích phụ; kết luận dùng tập chính (5 khái niệm). Không dùng trong K2 | — (trước khi có Git) |
| 2 | 21/10/2026 | Cặp A ↔ D chạy với nhãn `event` bị kiểm duyệt và thâm niên lấy từ `stag` (thời gian quan sát) | Chưa nhận review 18/10 (M5) | Theo quyết định 2 review 22/10: A ↔ D chỉ là thăm dò, tách khỏi tổng hợp chính và RQ2, RQ4 | — |
| 3 | 23/10/2026 | **Lần chạy thăm dò TB-HTL dạng mạng nơ-ron** (`tbhtl_thamdo_nn.py`): nhánh chung là MLP tiền huấn luyện trên Job Change, nhánh riêng tuyến tính, neo L2-SP; chiều B→A ở mức **đủ đặc trưng (L2)**, k ∈ {10, 20, 50, 100}, R = 30, M = 1. Kết quả: không vượt baseline đích mạnh nhất ở k nào; ngang bản không tiền huấn luyện và bản nhãn nguồn xáo trộn | Chạy trước khi nhận review 22/10 (quyết định 3: TB-HTL chỉ cài trong K2, có đặc tả trước) | **Không dùng cho kết luận.** Không phải TB-HTL v0 theo `docs/tbhtl_v0_spec.md`. Ghi lại vì kết quả đã được xem trước khi chốt đặc tả: bản tuyến tính trong đặc tả được chọn theo Phụ lục B1 của review, không theo kết quả lần chạy này | (điền) |
| 4 | 23/10/2026 | Tổng hợp Friedman: kết quả chính chuyển sang mức chiều (4 chiều AB + AC; đối chiếu 6 chiều), bản 41 khối thành phân tích độ nhạy | N3 review 22/10: các khối không độc lập | Kết luận định tính không đổi; p và CD của bản 41 khối không còn được trình bày như kết quả chính | (điền) |
| 5 | 23/10/2026 | RQ2 phát biểu lại: “chưa phát hiện lợi ích ≥ MDE ở k ≤ 50”, kèm bảng MDE (`results/tong_hop_cap/mde_cong0.csv`) | N1 review 22/10 | Không đổi kết quả; đổi cách phát biểu | (điền) |
| 6 | 17/10 → 23/10/2026 | Chỉ số của H1 đổi từ “AUC xuyên-miền ≥ 90% AUC trong-miền” (Bảng 5, bản 17/10) sang “(AUC xuyên − 0,5)/(AUC trong − 0,5) ≥ 0,8” | Đề xuất của nhóm sau khi xem KB1 v2; GVHD chốt chỉ số mới ngày 18/10 (M6) | Báo cáo cả hai cách. Theo chỉ số mới: A–B với LR + C1 đạt 0,84 và 0,89; không bền theo họ mô hình; A–C 0,02–0,33 | (điền) |
