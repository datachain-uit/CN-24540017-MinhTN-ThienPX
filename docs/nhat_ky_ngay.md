# Nhật ký ngày (từ 25/10/2026 đến buổi giữa kỳ)

Theo Review-2026-10-24, mục 6.5 và Phụ lục B6.

- Mỗi tối **trước 22:00**, mỗi thành viên thêm **một dòng** vào bảng dưới và commit bằng **tài khoản Git của mình** (Minh: `NhatMinh998`, Thiên: `CauBe9x`).
- Cùng tối, nhóm gửi GVHD một email ngắn (không quá 5 dòng) kèm mã commit; hai thành viên luân phiên gửi (ngày chẵn: Minh, ngày lẻ: Thiên — nhóm có thể đổi, ghi lại ở đây).
- Ngày không có commit phải ghi lý do. Ghi dòng mới ở cuối bảng, không sửa dòng của ngày đã qua.

| Ngày | Người | Đã làm (file, commit) | Kết quả | Vướng mắc | Việc tiếp |
|---|---|---|---|---|---|
| 24/10/2026 | Minh | Sửa đổi tiền đăng ký K2 theo review 24/10 (`0c84285`); kiểm tra mức sàn + ghi mã commit (`a9727e0`); khai báo công cụ AI (`docs/khai_bao_cong_cu.md`) | Tái lập TẤT CẢ ĐẠT; L2 lần rút 0 trùng Cổng 0; mức sàn đạt (PR-AUC 0,164–0,184, ngẫu nhiên ≈ 0,174); K2 sau sửa đổi bắt đầu chạy 21:27 | K2 sau sửa đổi mất khoảng 7 giờ CPU (thêm L1_core, L2) | 25/10: hoàn tất K2, commit kết quả; theo dõi Thiên commit EDA và phiếu đọc |
| 24/10/2026 | Thiên | Bảng 1 mở rộng, 10 phiếu đọc (`6c056db`); EDA ba miền A–C (`b89d1d3`). Ghi bù ngày 25/10 | Bảng 1 mở rộng 12 dòng, không còn ô trống; 6 phiếu đủ mục giao thức, 4 phiếu chờ toàn văn; EDA khớp Bảng 12 cho A, B, C | Miền D chưa có dữ liệu (`turnover.csv`); 4 bài chưa có toàn văn | 25/10: EDA miền D, phân phối khái niệm sau C1, đối chiếu A5.5a–b |