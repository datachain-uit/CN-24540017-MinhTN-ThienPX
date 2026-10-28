# Phiếu đọc: [Pereira, 2025] – TrAdaBoost cho dự đoán nghỉ việc với ít nhãn đích   (mã trích dẫn: [44])

- Người lập phiếu: Phạm Xuân Thiên, có công cụ AI hỗ trợ đọc toàn văn tiếng Bồ Đào Nha (khai báo trong `docs/khai_bao_cong_cu.md`)   Ngày: 28/10/2026
- Loại tài liệu: luận văn thạc sĩ, ngành Kỹ thuật sản xuất, Faculdade de Ciências Aplicadas, UNICAMP; người hướng dẫn Cristiano Torezzan (đồng tác giả của [31]); bảo vệ 31/10/2025. Không phải bài bình duyệt, không có hạng Scimago/CORE
- DOI: 10.47749/t/unicamp.2025.1546748 (toàn văn 59 trang, tải từ kho UNICAMP ngày 27/10/2026)
- Căn cứ đưa vào tổng quan: QĐ3 review 25/10. Chỉ dùng ở phần tổng quan; căn cứ của baseline TrAdaBoost là bài gốc Dai và cs., ICML 2007

```bibtex
@mastersthesis{pereira2025turnover,
  author = {Pereira, Jo{\~a}o Pedro de Lima},
  title  = {Aprimoramento da predi{\c{c}}{\~a}o de turnover volunt{\'a}rio por meio da transfer{\^e}ncia de aprendizado},
  school = {Universidade Estadual de Campinas (UNICAMP), Faculdade de Ci{\^e}ncias Aplicadas},
  address = {Limeira, SP},
  year   = {2025},
  doi    = {10.47749/t/unicamp.2025.1546748}
}
```

## 1. Bài toán

Dự đoán nghỉ việc tự nguyện ở tổ chức đích có ít nhãn, bằng cách dùng dữ liệu của một tổ chức nguồn. Nhãn là "đã nghỉ việc" (1) hay "ở lại" (0), không có mốc thời gian. Khung đề xuất gồm ba phần: chuyển giao trực tiếp, thích ứng có giám sát (tinh chỉnh Random Forest hoặc TrAdaBoost) và kiểm tra hiệu năng theo nhóm nhân viên.

## 2. Dữ liệu

Hai bộ Kaggle cùng cấu trúc 9 thuộc tính, dùng 6 thuộc tính chung (đánh giá gần nhất, số dự án, bậc lương, thâm niên, mức hài lòng, giờ làm trung bình tháng) (Bảng 4.1, tr. 37):

- Bộ 1: Stewart (2018), 9.540 dòng, 2.784 nghỉ việc (29,2 %).
- Bộ 2: Huseyn (2017), 14.999 dòng, 3.571 nghỉ việc (23,8 %). Đây chính là bộ HR 14.999, miền C của đề tài, **chưa loại trùng** (nhóm loại 3.008 dòng trùng hoàn toàn, còn 11.991).

Cả hai đều là dữ liệu mô phỏng, cùng tên cột, nên bài toán là chuyển giao **cùng không gian đặc trưng**, khác với đề tài (khái niệm chung giữa các bộ có lược đồ khác nhau).

## 3. Giao thức đánh giá

| Mục | Luận văn làm gì | Trang/mục |
|---|---|---|
| Metric báo cáo | Accuracy, precision, recall, F1 ở ngưỡng mặc định; không có AUC-ROC hay PR-AUC | Bảng 5.1–5.5 |
| Chia dữ liệu | Trong miền: 80/20 phân tầng, 50 lần lặp. Chuyển giao trực tiếp: huấn luyện trên toàn bộ nguồn, đánh giá trên toàn bộ đích. Tinh chỉnh: lấy ρ = 1–25 % đích để huấn luyện, phần còn lại để test | 4.4.1–4.4.3 |
| Số nhãn đích tuyệt đối | ρ = 1 %: khoảng 150 nhãn (bộ 2 làm đích) hoặc 95 nhãn (bộ 1); ρ = 10 %: khoảng 1.500 hoặc 954 nhãn. Nhiều hơn hẳn k = 10–100 của Cổng 0 và K2 | suy ra từ 4.2 và 4.4.3 |
| Mất cân bằng | Chuẩn hoá z-score rồi SMOTE, chỉ trên phần huấn luyện, sau khi chia | 4.3.2, tr. 40–41 |
| Chọn siêu tham số | Không mô tả | — |
| Kiểm định thống kê | Đánh dấu "khác biệt có ý nghĩa ở mức 95 %" trong Bảng 5.1, không nêu phép kiểm định; không có khoảng tin cậy cho phép so sánh chuyển giao | Bảng 5.1 |
| Công bố mã, dữ liệu | Dữ liệu công khai trên Kaggle; không thấy liên kết mã | Tài liệu tham khảo |
| Rủi ro rò rỉ | (a) TrAdaBoost "được huấn luyện bằng nguồn và **toàn bộ** miền đích, rồi đánh giá trên chính miền đích đó"; (b) bộ 2 không loại trùng, 20,1 % dòng trùng hoàn toàn có thể nằm ở cả phần train và test của thí nghiệm trong miền | 4.4.3 Abordagem B, tr. 44 |

## 4. Kết quả chính

- Trong miền: Random Forest tốt nhất, F1 0,765 (bộ 1) và 0,981 (bộ 2) (Bảng 5.1).
- Chuyển giao trực tiếp làm F1 của Random Forest giảm còn 0,401 (bộ 1 → bộ 2) và 0,211 (bộ 2 → bộ 1) (Bảng 5.2).
- Tinh chỉnh với 1 % nhãn đích: F1 0,837 (1 → 2) và 0,551 (2 → 1) (Bảng 5.3–5.4).
- TrAdaBoost: F1 0,848 (1 → 2) và 0,700 (2 → 1) (Bảng 5.5). Luận văn kết luận TrAdaBoost tốt nhất khi ρ ≤ 5 %.

Không dùng được làm mốc so sánh trực tiếp: kết quả TrAdaBoost đánh giá trên chính dữ liệu đã huấn luyện, metric khác (F1 thay vì PR-AUC), số nhãn đích khác một bậc độ lớn.

## 5. Hạn chế

Tác giả nêu: chỉ có hai bộ dữ liệu và một số mô hình (Chương 6, tr. 54).

Nhóm nhận xét: (i) không có baseline chỉ dùng cùng số nhãn đích, nên chưa trả lời được chuyển giao có giúp hơn việc học thẳng trên các nhãn đó hay không; (ii) TrAdaBoost và tinh chỉnh được đánh giá theo hai giao thức khác nhau (toàn bộ đích so với phần test riêng), nên phép so sánh A với B ở mục 5.3.3 không công bằng; (iii) ngưỡng F1 mặc định, không phù hợp khi tỷ lệ dương khác nhau giữa hai miền.

## 6. Liên hệ với đề tài TB-HTL

Đây là công trình gần đề tài nhất về câu hỏi (chuyển giao giữa các bộ dữ liệu nhân sự công khai khi đích ít nhãn), nhưng kết luận tích cực của luận văn trái với kết luận PIVOT của Cổng 0. Ba khác biệt giao thức giải thích được một phần: đề tài so với baseline chỉ dùng đích mạnh nhất cùng k, dùng PR-AUC, và loại trùng trước khi chia. Theo QĐ3 review 25/10, đề tài chạy TrAdaBoost trong Cổng 0 và K2-L0 (họ so sánh riêng, `prereg/prereg_trada.yaml`) và báo cáo cả F1 để đối chiếu; bảng đối chiếu với luận văn làm sau khi có `trada_eval.py` (04/11). Dùng ở phần tổng quan và khoảng trống nghiên cứu.
