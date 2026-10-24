# Phiếu đọc (Y3)

Theo đánh giá 07/10/2026 (Y3): mỗi bài có một phiếu đọc một trang theo [MAU_phieu_doc.md](MAU_phieu_doc.md) (bài toán, dữ liệu, giao thức, kết quả, hạn chế, liên hệ với đề tài), thay vì chỉ lưu PDF và bản dịch máy. Tên file: `[n]_TacGia_Nam.md`.

## 10 bài ưu tiên (đọc trước 28/10)
Chọn theo mức liên quan trực tiếp tới thí nghiệm của đề tài.

| # | Bài | Vì sao ưu tiên | Người đọc | Xong |
|---|---|---|---|---|
| [5] | Chung et al. 2023 (ESWA) – stacking | Baseline lĩnh vực (STACK trong Cổng 0) | Thiên | 🟡 khung — Elsevier trả phí, chưa có toàn văn |
| [8] | Baydili & Tasci 2025 (Systems) | Ví dụ rò rỉ: GAN trước khi chia; lý do không dùng làm mốc | Thiên | 🟡 khung — cần tải PDF (open access) để lấy số trang |
| [10] | AL-Ali et al. 2026 | Dùng cả IBM và Job Change nhưng đánh giá từng bộ | Thiên | ✅ |
| [31] | Pereira & Torezzan 2024 (SBPO) | Gần đề tài nhất: huấn luyện một bộ, kiểm tra bộ khác | Thiên | 🟡 khung — chưa tìm được bản công khai |
| [43] | De Vos et al. 2025 | Giao thức benchmark, nguồn các mô hình chỉ dùng đích | Thiên | ✅ (giao thức rút từ mã nguồn công bố) |
| [11] | Levin et al. – transfer với mô hình bảng sâu | Nền cho tiền huấn luyện và FT-Canonical | Thiên | ✅ |
| [24] | CARTE | Baseline xuyên bảng dựa vào tên cột (KB2b) | Thiên | ✅ |
| [25] | Hollmann et al. 2025 – TabPFN v2 | Baseline chỉ dùng đích mạnh nhất ở nhiều mức k | Thiên | 🟡 khung — Nature đòi đăng nhập; đã có số liệu nhóm tự đo |
| [32] | Domain Separation Networks | Gần TB-HTL nhất về tách biểu diễn chung/riêng | Thiên | ✅ |
| [33] | Daumé III – frustratingly easy DA | Baseline DAUME_LR trong Cổng 0 | Thiên | ✅ |

**Tình trạng 23/10: 10/10 phiếu đã lập.**

| Mức | Phiếu | Ghi chú |
|---|---|---|
| ✅ Đầy đủ | [10], [11], [24], [32], [33], [43] | 6 phiếu, bảng giao thức kín |
| 🟡 Còn khung | [5], [8], [25], [31] | Chưa truy cập được toàn văn |

Lý do 4 phiếu còn khung: **[5]** Elsevier trả phí · **[8]** MDPI chặn tải tự động (bài là open access, mở trình duyệt tải được) · **[25]** Nature đòi đăng nhập · **[31]** chưa tìm được bản công khai nào.

Riêng **[43]** lấy được giao thức đầy đủ từ **mã nguồn tác giả công bố** thay cho văn bản bài báo.

Chi tiết việc còn thiếu của từng phiếu nằm ở mục *"Việc còn lại"* cuối mỗi tệp.

Sau 10 bài này, làm tiếp các bài còn lại của Bảng 1 ([1]–[4], [6], [7], [9]) để điền đủ [bang1_phuong_phap_luan.csv](bang1_phuong_phap_luan.csv).

## Bảng 1 mở rộng
`bang1_phuong_phap_luan.csv` là các cột GVHD yêu cầu thêm cho Bảng 1 (metric, giao thức chia, xử lý mất cân bằng trước/sau chia, công bố mã). Ô có sẵn nội dung lấy từ đánh giá 07/10 và báo cáo; ô “?” điền từ phiếu đọc, ghi số trang.
