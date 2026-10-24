# Phiếu đọc: [Pereira & Torezzan, 2024] – Huấn luyện một bộ, kiểm tra bộ khác   (mã trích dẫn: [31])

- Người đọc: Phạm Xuân Thiên   Ngày: 23/10/2026   Thời gian đọc: 1,0 giờ
- Nơi công bố và hạng: SBPO – *Simpósio Brasileiro de Pesquisa Operacional*, hội nghị Brazil. Chưa tra được hạng CORE, nhiều khả năng không có trong danh mục
- Kỷ yếu: *Anais do LVI SBPO*, 2024, DOI kỷ yếu 10.59254/sbpo-2024. Hội nghị LVI SBPO, Fortaleza, 4–7/11/2024
- Chưa tìm được bản công khai nào. Đã tra: kỷ yếu Galoá (proceedings.science/sbpo/sbpo-2024, chặn 403), OpenAlex, Semantic Scholar, kho UNICAMP, DBLP

## 1. Bài toán

Huấn luyện mô hình trên một bộ dữ liệu Kaggle, kiểm tra trên một bộ khác. Hai bộ chung 6 thuộc tính, cùng ngữ nghĩa nhãn.

Đây là lý do [31] được xếp vào nhóm ưu tiên: trong toàn bộ Bảng 1, đây là bài duy nhất có thiết lập huấn luyện một bộ rồi kiểm tra bộ khác.

## 2. Dữ liệu

Hai bộ Kaggle, chung 6 thuộc tính; tên cụ thể chưa biết. Báo cáo tiến độ 22/10 mục A2 ghi miền C, HR 14.999 dòng, "đã được [8] và [31] dùng", nên nhiều khả năng một trong hai bộ của [31] chính là miền C của nhóm.

Số dòng, số cột, tỷ lệ dương: chưa đọc được bài.

## 3. Giao thức đánh giá

| Mục | Bài làm gì | Trang/mục |
|---|---|---|
| Metric báo cáo | Chỉ accuracy, theo ghi chú sẵn có trong Bảng 1 | chưa có bản công khai |
| Chia dữ liệu | Huấn luyện trên một bộ Kaggle, kiểm tra trên bộ khác | chưa có bản công khai |
| Mất cân bằng | Chưa đọc được bài | chưa có bản công khai |
| Chọn siêu tham số | Chưa đọc được bài | chưa có bản công khai |
| Kiểm định thống kê | Chưa đọc được bài | chưa có bản công khai |
| Công bố mã, dữ liệu | Chưa đọc được bài | chưa có bản công khai |
| Rủi ro rò rỉ | Chưa đọc được bài | chưa có bản công khai |

## 4. Kết quả chính

Chưa đọc được bài. Theo tóm tắt: huấn luyện trên một bộ Kaggle, kiểm tra trên bộ khác, báo cáo accuracy.

Đáng chú ý là bài chỉ báo cáo accuracy. Với dữ liệu nghỉ việc mất cân bằng, accuracy không cho biết mô hình bắt được bao nhiêu ca nghỉ việc, nên nếu bài chỉ có accuracy thì không so trực tiếp với PR-AUC của nhóm được.

## 5. Hạn chế

Do tác giả nêu: chưa đọc được bài.

Do nhóm nhận xét: chỉ dùng accuracy, thiếu thước đo phù hợp với mất cân bằng. Chỉ 6 thuộc tính chung giữa hai bộ, tương đương mức của cặp AB (4 khái niệm) và thấp hơn cặp AC (5–8 khái niệm).

## 6. Liên hệ với đề tài TB-HTL

Dùng ở Bảng 1, và là công trình đối chứng gần nhất: bài duy nhất trong danh mục [1]–[10], [31], [43] có chuyển giao xuyên nguồn.

Khác TB-HTL ở chỗ [31] chỉ xét cặp cùng ngữ nghĩa nhãn, còn đề tài khảo sát cả cùng (AC, AD) lẫn khác (AB); [31] chỉ dùng accuracy, còn đề tài dùng PR-AUC, AUC-ROC và kiểm định có hiệu chỉnh.

Điểm mấu chốt cần kiểm khi đọc được bài: [31] có so sánh với baseline chỉ dùng dữ liệu đích không. Nếu không, bài chưa trả lời được câu hỏi chuyển giao có thực sự giúp ích hay không, và đó chính là chỗ TB-HTL khác biệt vì Cổng 0 lấy đúng tiêu chí này làm căn cứ GO/PIVOT.

## 7. Phát hiện kèm theo: luận văn UNICAMP 2025

Khi tìm bài SBPO 2024, tra ra một luận văn của cùng tác giả thứ nhất, do chính Cristiano Torezzan hướng dẫn:

> *Aprimoramento da predição de turnover voluntário por meio da transferência de aprendizado*
> João Pedro de Lima Pereira, UNICAMP, 2025, công bố 31/10/2025. Tiếng Bồ Đào Nha.
> DOI <https://doi.org/10.47749/t/unicamp.2025.1546748>. Truy cập mở, nhưng kho UNICAMP chặn tải tự động.

Theo mô tả OpenAlex: học chuyển giao bằng TrAdaBoost trên hai bộ dữ liệu HR công khai, mô hình thích ứng sang miền đích bằng một số ít mẫu có nhãn. Gần như trùng khớp với thiết lập Cổng 0.

Hai việc cần quyết. Thứ nhất, luận văn này có phải bản mở rộng của bài SBPO [31] không; nếu đúng thì nó là công trình gần đề tài nhất trong toàn bộ danh mục, gần hơn cả [11] Levin và [24] CARTE. Thứ hai, TrAdaBoost có nên thêm vào danh sách baseline chuyển giao của Cổng 0 không; hiện `g0_23.py` có 8 baseline (ZS, STK_LR, STK_XGB, OFF_XGB, DAUME_LR, RANKAVG, ANCHOR_LR, RANKAVG_RF) nhưng không có TrAdaBoost, vốn là thuật toán chuyển giao kinh điển cho đúng tình huống ít nhãn ở miền đích.

Đánh giá 22/10 ghi "danh sách baseline giữ nguyên theo Phụ lục D của review 07/10, không bổ sung baseline mới", nên việc thêm TrAdaBoost phải hỏi ý GVHD trước. Nhưng phát hiện này cần báo cáo.

Ba hướng lấy bài [31], theo thứ tự ưu tiên: hỏi Minh vì bài nằm trong danh mục của nhóm nên nhiều khả năng Minh đã có PDF khi lập Bảng 1; tra kỷ yếu Galoá theo tác giả Torezzan bằng trình duyệt; tải luận văn UNICAMP 2025 ở link trên.
