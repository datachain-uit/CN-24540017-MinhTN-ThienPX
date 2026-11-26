# Phiếu đọc: [Pereira & Torezzan, 2024] – Transfer learning cho dự đoán turnover tự nguyện   (mã trích dẫn: [31])

- Người đọc: Phạm Xuân Thiên   Ngày: 26/11/2026   Thời gian đọc: 2,0 giờ
- Nơi công bố và hạng: Anais do LVI Simpósio Brasileiro de Pesquisa Operacional (SBPO 2024), Fortaleza – CE, 04–07/11/2024, do SOBRAPO tổ chức. Hội nghị trong nước của Brazil, chưa tra thấy trong Scimago/CORE, nhiều khả năng không được xếp hạng (cần tra lại cho chắc). Bài chỉ có 5 trang, kiểu bài ngắn
- Link bản chính thức: <https://proceedings.science/p/193706> (PDF tải từ trang này). Không có DOI riêng cho bài, DOI 10.59254/sbpo-2024 là của cả kỷ yếu

```bibtex
@inproceedings{pereira2024transferencia,
  title     = {Transfer{\^e}ncia de aprendizado em modelos de predi{\c{c}}{\~a}o de turnover volunt{\'a}rio},
  author    = {Pereira, Jo{\~a}o Pedro de Lima and Torezzan, Cristiano},
  booktitle = {Anais do LVI Simp{\'o}sio Brasileiro de Pesquisa Operacional (SBPO 2024)},
  address   = {Fortaleza, CE, Brasil},
  year      = {2024},
  url       = {https://proceedings.science/p/193706}
}
```

Tác giả ở FCA-UNICAMP (Limeira, SP), có vẻ là sinh viên + giảng viên hướng dẫn. Bài viết bằng tiếng Bồ Đào Nha, có abstract tiếng Anh (abstract dịch lỗi, "florestas aleatórias" thành "exploited forests"). Khi trích thì để tên gốc tiếng Bồ.

## 1. Bài toán

Doanh nghiệp nhỏ và vừa không đủ dữ liệu để tự train mô hình dự đoán nghỉ việc, nên tác giả hỏi: lấy mô hình train sẵn trên một bộ dữ liệu HR rồi đem dùng cho bộ khác thì có được không? Chỉ thử 2 mô hình là hồi quy logistic (RL) và random forest (FA), lý do là hai mô hình này được dùng nhiều nhất theo tổng quan của Akasheh et al. (2024).

Biến mục tiêu: "Demissão", bằng 1 nếu nhân viên tự xin nghỉ (turnover tự nguyện), phân loại nhị phân (Bảng 1, tr.3). Là nghỉ việc đã xảy ra, không phải ý định. Bài không nói khoảng thời gian.

## 2. Dữ liệu

Hai bộ công khai trên Kaggle (mục 3.1, tr.2):
- Dataset 1: Stewart (2018), "Employee turnover data set", 9.540 dòng, 10 cột (9 thuộc tính + nhãn).
- Dataset 2: Huseyn (2017), "HR analytics data set", 14.999 dòng, 10 cột (9 thuộc tính + nhãn).

Tác giả chọn 2 bộ này vì có nhiều cột giống nhau. Bảng 1 liệt kê 6 thuộc tính chung (điểm đánh giá gần nhất, số dự án, mức lương thấp/trung bình/cao, số năm làm việc, mức hài lòng 0–1, số giờ làm trung bình/tháng) + nhãn.

Chỗ chưa rõ:
- Bài nói mỗi bộ có 9 thuộc tính nhưng Bảng 1 chỉ có 6. Không nói khi chuyển giao thì dùng 6 cột chung hay sao, cũng không nói đã đồng bộ thang đo/mã hóa giữa 2 bộ thế nào.
- Không báo tỉ lệ dương của bộ nào. (Tỉ lệ dương theo phiếu [44] (Bảng 4.1 luận văn, tr. 37): bộ 1 29,2 %, bộ 2 23,8 %.)
- Dataset 2 có 14.999 dòng, 10 cột, đúng các cột như vậy, nên nhiều khả năng là bộ "HR_comma_sep" quen thuộc trên Kaggle. Bộ này là dữ liệu mô phỏng, khoảng 23,8% nghỉ việc và nhóm nhớ là có khoảng 3.000 dòng trùng nhau. Đã đối chiếu: đúng là bộ HR 14.999 (miền C), 3.571 nghỉ việc (23,8 %) theo phiếu [44] (Bảng 4.1 luận văn, tr. 37); 3.008 dòng trùng hoàn toàn, còn 11.991 sau loại trùng (`data/README.md`, `eda/bang1_tong_quan_mien.csv`).
- Dataset 1 chưa rõ là thật hay mô phỏng, cần xem trang Kaggle. Suy ngược từ Hình 1 (mô hình gần như không đoán ra ca dương nào mà accuracy ≈ 0,70) thì tỉ lệ dương của dataset 1 chắc khoảng 30%, nhưng đây chỉ là nhóm ước lượng. Đã đối chiếu: Stewart (2018) có 9.540 dòng, 2.784 nghỉ việc (29,2 %), là dữ liệu mô phỏng theo phiếu [44] (Bảng 4.1 luận văn, tr. 37); ước lượng khoảng 30 % ở trên là đúng.
- Báo cáo tiến độ 22/10 (mục A2) ghi miền C của nhóm là bộ HR 14.999 dòng. Vậy dataset 2 của bài này nhiều khả năng chính là miền C của nhóm.

## 3. Giao thức đánh giá

| Mục | Bài làm gì | Trang/mục |
|---|---|---|
| Metric báo cáo | Mục 3.2 nói dùng 4 metric: accuracy, precision, recall, F1. Nhưng Bảng 2 (bảng kết quả chính) chỉ có accuracy. Hình 1 có đủ 4 metric nhưng chỉ cho FA trong thí nghiệm thêm mẫu. Không có AUC hay PR-AUC | mục 3.2 tr.3, Bảng 2 tr.4, Hình 1 tr.4 |
| Chia dữ liệu | Trong cùng 1 bộ: hold-out 80/20. Chuyển giao: train trên 100% bộ nguồn, test trên 100% bộ đích. Thí nghiệm thêm mẫu: thêm 0 → 2000 dòng của bộ đích vào tập train (bước 100). Mỗi thí nghiệm chạy 50 lần, báo trung bình. Không nói có phân tầng không, không nói 50 lần có chia lại dữ liệu không | mục 3.2 tr.3, mục 4 tr.3 |
| Mất cân bằng | Không xử lý gì, cũng không nhắc tới | – |
| Chọn siêu tham số | Không nói. Không ghi số cây, độ sâu, regularization, có chuẩn hóa hay không, mã hóa cột lương thế nào | – |
| Kiểm định thống kê, khoảng tin cậy | Không. Chạy 50 lần nhưng chỉ báo trung bình, không có độ lệch | – |
| Công bố mã, dữ liệu | Mã: không. Dữ liệu: có link Kaggle cho cả 2 bộ | Tài liệu tham khảo tr.5 |
| Rủi ro rò rỉ thông tin | (1) Thí nghiệm thêm mẫu: lấy dòng của bộ đích bỏ vào train, trong khi test là "100%" bộ đích, bài không nói có loại các dòng đó ra khỏi tập test không. Nếu không loại thì mô hình được test trên chính dòng đã học. (2) Nếu dataset 2 đúng là HR_comma_sep thì có nhiều dòng trùng, chia 80/20 ngẫu nhiên sẽ có dòng giống hệt nhau nằm ở cả train và test, giải thích được vì sao FA đạt 0,990 | mục 3.2 tr.3, Hình 1 tr.4 |

## 4. Kết quả chính

Bảng 2 (tr.4), accuracy trung bình 50 lần chạy:

| Mô hình | Test trong cùng bộ (20%) | Test chuyển giao (100% bộ kia) |
|---|---|---|
| FA train bộ 1 | 0,857 | 0,676 (trên bộ 2) |
| FA train bộ 2 | 0,990 | 0,705 (trên bộ 1) |
| RL train bộ 1 | 0,721 | 0,570 (trên bộ 2) |
| RL train bộ 2 | 0,767 | 0,574 (trên bộ 1) |

Hình 1 (tr.4), chỉ có FA, trục ngang là số dòng của bộ đích được thêm vào tập train:
- Bộ 1 → bộ 2: lúc chưa thêm dòng nào thì accuracy khoảng 0,64 nhưng precision, recall, F1 đều khoảng 0,03–0,04. Thêm 100 dòng của bộ 2 là recall lên khoảng 0,92, F1 khoảng 0,79. Thêm 2000 dòng thì accuracy khoảng 0,98, F1 khoảng 0,95.
- Bộ 2 → bộ 1: lúc chưa thêm thì accuracy khoảng 0,70, recall gần 0, F1 gần 0. Càng thêm dòng của bộ 1 thì accuracy càng giảm (xuống khoảng 0,52 ở 2000 dòng). F1 cao nhất chỉ khoảng 0,39 (quanh 300–400 dòng) rồi giảm dần.

Tác giả kết luận: FA tốt hơn RL ở mọi trường hợp. Mô hình train trên bộ 1 dự đoán tốt cho bộ 2, còn mô hình train trên bộ 2 dự đoán bộ 1 rất kém, nên chuyển giao phụ thuộc vào bối cảnh dữ liệu train (mục 5, tr.4).

Nhóm thấy kết luận về chuyển giao không khớp với số liệu của chính bài:
- Theo Bảng 2 thì hướng 1 → 2 (0,676) còn thấp hơn hướng 2 → 1 (0,705), ngược với câu kết luận.
- Theo Hình 1, ở điểm 0 dòng (tức chuyển giao thật sự, không có dữ liệu đích) thì F1 của cả hai hướng đều gần 0. Nghĩa là chuyển giao thẳng thất bại cả hai chiều, mô hình gần như đoán tất cả là "ở lại".
- Nếu bộ 2 có khoảng 23,8% nghỉ việc thì chỉ cần đoán "tất cả ở lại" là đã được accuracy khoảng 0,76, cao hơn 0,676 của mô hình chuyển giao.
- Hướng 1 → 2 chỉ "tốt" sau khi thêm dòng của bộ 2 vào train. Bộ 2 lại rất dễ (FA đạt 0,990 trong cùng bộ), nên đây là mô hình học trực tiếp bộ 2 chứ không phải chuyển giao, chưa kể nghi rò rỉ như đã ghi ở mục 3.

Không dùng làm mốc so sánh số được: chỉ có accuracy, không có baseline lớp đa số, không có độ lệch, nghi rò rỉ. Nhưng nên dùng như ví dụ cho thấy chuyển giao thẳng giữa 2 bộ HR có thể thất bại.

## 5. Hạn chế

Do tác giả nêu: bài không có mục hạn chế. Kết luận chỉ nói chuyển giao phụ thuộc bối cảnh và cần dữ liệu train đa dạng hơn.

Do nhóm nhận xét:
- Kết luận về chuyển giao ngược với Bảng 2 và Hình 1 (xem mục 4).
- Đánh giá bằng accuracy trên dữ liệu mất cân bằng, không có baseline đoán lớp đa số, không báo tỉ lệ dương.
- Không so sánh với mô hình chỉ train trên dữ liệu đích ở cùng số lượng mẫu. Ví dụ ở điểm "thêm 500 dòng" phải so với mô hình chỉ train trên 500 dòng đó, thì mới biết dữ liệu nguồn có giúp gì không (đúng ý định nghĩa negative transfer của [39]).
- Không mô tả tiền xử lý, siêu tham số, cách khớp cột giữa 2 bộ, nên không làm lại được. Không công bố mã.
- Chỉ có 2 bộ, và cả 2 đều là dữ liệu mô phỏng (theo phiếu [44] (Bảng 4.1 luận văn, tr. 37)).
- Không có độ lệch hay kiểm định dù đã chạy 50 lần.
- Nghi rò rỉ ở thí nghiệm thêm mẫu và do dòng trùng.

## 6. Liên hệ với đề tài TB-HTL

Đây là bài gần với đề tài nhất trong mấy bài đã đọc: chuyển giao xuyên nguồn giữa các bộ dữ liệu nghỉ việc dạng bảng, dùng tập đặc trưng chung. Dùng ở phần tổng quan, mục các nghiên cứu liên quan trực tiếp, và để chỉ ra khoảng trống: bài đã đặt đúng câu hỏi nhưng cách đánh giá chưa đủ để trả lời.

Đề tài cần làm khác bài này ở các điểm:
- Báo AUC-ROC, PR-AUC, F1 và có baseline đoán lớp đa số, không chỉ dùng accuracy.
- Có baseline chỉ-đích cùng thuật toán, cùng số mẫu đích, rồi tính NTG theo [39].
- Các dòng đích dùng để train phải tách hẳn khỏi tập test đích.
- Khử dòng trùng trước khi chia.
- Báo độ lệch, khoảng tin cậy qua các lần lặp.
- Mô tả rõ cách ghép cột chung và chuẩn hóa thang đo giữa các bộ.

Bộ 2 có vẻ trùng với miền C của nhóm (xem mục 2), còn bộ 1 (Stewart 2018) thì có thể cân nhắc thêm làm miền phụ. Đã đối chiếu: bộ 2 là miền C; cả hai bộ đều là dữ liệu mô phỏng, tỉ lệ dương 29,2 % và 23,8 %, bộ 2 có 3.008 dòng trùng (theo phiếu [44] (Bảng 4.1 luận văn, tr. 37); `data/README.md`).

Bài này là bước đầu của [44] (luận văn thạc sĩ 2025 cùng tác giả Pereira, người hướng dẫn là Torezzan). Ở [44] tác giả chuyển sang dùng TrAdaBoost với ít nhãn đích, nên khi viết tổng quan thì để [31] trước, [44] sau, cho thấy hướng này đã đi tiếp tới đâu.

Có chuyển giao xuyên nguồn, nhưng chỉ là train ở bộ này rồi đem nguyên mô hình sang bộ kia, hoặc gộp thêm dòng. Không có phương pháp chuyển giao nào cụ thể (không reweight, không căn chỉnh miền).
