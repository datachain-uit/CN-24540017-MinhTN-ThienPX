# Phiếu đọc (Y3)

Theo đánh giá 07/10/2026 (Y3): mỗi bài có một phiếu đọc theo [MAU_phieu_doc.md](MAU_phieu_doc.md) — bài toán, dữ liệu, giao thức, kết quả, hạn chế, liên hệ với đề tài — thay vì chỉ lưu PDF và bản dịch máy. Tên file: `[n]_TacGia_Nam.md`.

## 10 bài ưu tiên

Chọn theo mức liên quan trực tiếp tới thí nghiệm của đề tài. Người đọc: Thiên.

| # | Bài | Vì sao ưu tiên | Tình trạng |
|---|---|---|---|
| [5] | Chung et al. 2023 (ESWA) – stacking | Baseline lĩnh vực (STACK trong Cổng 0) | Chờ toàn văn |
| [8] | Baydili & Tasci 2025 (Systems) | Ví dụ rò rỉ: GAN trước khi chia; lý do không dùng làm mốc | Chờ toàn văn |
| [10] | AL-Ali et al. 2026 | Dùng cả IBM và Job Change nhưng đánh giá từng bộ | Đủ |
| [11] | Levin et al. 2023 – transfer với mô hình bảng sâu | Nền cho tiền huấn luyện và FT-Canonical | Đủ |
| [24] | CARTE | Baseline xuyên bảng dựa vào tên cột (KB2b) | Đủ |
| [25] | Hollmann et al. 2025 – TabPFN v2 | Baseline chỉ dùng đích mạnh nhất ở nhiều mức k | Chờ toàn văn |
| [31] | Pereira & Torezzan 2024 (SBPO) | Gần đề tài nhất: huấn luyện một bộ, kiểm tra bộ khác | Chờ toàn văn |
| [32] | Domain Separation Networks | Gần TB-HTL nhất về tách biểu diễn chung/riêng | Đủ |
| [33] | Daumé III – frustratingly easy DA | Baseline DAUME_LR trong Cổng 0 | Đủ |
| [43] | De Vos et al. 2025 | Giao thức benchmark, nguồn các mô hình chỉ dùng đích | Đủ |
| [44] | Pereira 2025, luận văn thạc sĩ UNICAMP | Gần đề tài nhất về câu hỏi: TrAdaBoost giữa hai bộ nhân sự công khai, ít nhãn đích (QĐ3 review 25/10) | Đủ (28/10) |

Tình trạng 24/10: 10/10 phiếu đã lập, đã điền ngày đọc và thời gian đọc. Sáu phiếu đủ mục giao thức; bốn phiếu còn ô chờ toàn văn, nhưng không ô nào để trống hay suy đoán — mỗi ô ghi rõ cần gì và lấy ở đâu.

Lý do bốn phiếu còn chờ:

| Phiếu | Vì sao | Lấy ở đâu |
|---|---|---|
| [5] | Tường phí Elsevier | Thư viện UIT, DOI 10.1016/j.eswa.2022.119364 |
| [8] | Bài truy cập mở, MDPI chặn tải tự động | <https://www.mdpi.com/2079-8954/13/7/583> |
| [25] | Nature đòi đăng nhập | Mạng UIT / thư viện trường |
| [31] | Chưa tìm được bản công khai (đã tra Galoá, OpenAlex, Semantic Scholar, kho UNICAMP, DBLP) | Liên hệ tác giả, hoặc kỷ yếu SBPO qua thư viện |

Riêng [43] lấy được giao thức đầy đủ từ mã nguồn tác giả công bố thay cho văn bản bài báo.

## Bảng 1 mở rộng

`bang1_phuong_phap_luan.csv` là các cột GVHD yêu cầu thêm cho Bảng 1: metric, giao thức chia, xử lý mất cân bằng trước hay sau chia, công bố mã, rủi ro rò rỉ, trang nguồn. 12 dòng, không còn ô trống.

Cập nhật 24/10, điền thêm từ toàn văn: [4] Alsheref (PMC9251085), [6] Li (PMC10557501), [7] Mohiuddin (arXiv 2304.03103, bản được nhận CIKM 2023). Dòng [1] Sexton điền từ tóm tắt chính thức trên kho BearWorks, không phải toàn văn.

| Mức điền | Dòng |
|---|---|
| Đủ, có số mục dẫn nguồn | [4], [6], [7], [10], [43] |
| Đủ bốn ô, nguồn là tóm tắt | [1] |
| Một phần | [8], [31] |
| Chưa điền được ba ô giao thức | [2], [3], [5], [9] |

Bốn dòng chưa điền: [2] tường phí ScienceDirect; [3] truy cập mở nhưng Springer chặn tải tự động; [5] tường phí Elsevier; [9] truy cập mở CC BY nhưng kho CBS chặn tải tự động. Link ghi trong cột `trang_nguon`.

Hai điểm cần sửa lại trong Bảng 1, phát sinh khi đọc toàn văn:

1. [4] — Bảng 1 ghi dữ liệu là "IBM HR", nhưng bài ghi lấy từ thư viện SAS, 35 biến, khoảng 1.500 dòng; quy mô trùng IBM HR (1.470 × 35) nhưng bài không gọi tên IBM. Cần đối chiếu lại.
2. [6] — là mốc so sánh dùng được trực tiếp trên miền A: AUC-ROC 0,7452, thấp hơn 0,840 (TabPFN v2) và 0,829 (Logistic Regression) nhóm đo trên cùng bộ. Giao thức của bài sạch và có kiểm định thống kê nên đây là chứng cứ bên ngoài cho lập luận PIVOT.

Sau 10 bài này, lập phiếu đọc cho các bài còn lại của Bảng 1: [1]–[4], [6], [7], [9].
