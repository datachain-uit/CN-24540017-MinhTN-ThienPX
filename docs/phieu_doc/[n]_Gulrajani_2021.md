# Phiếu đọc: [Gulrajani & Lopez-Paz, 2021] – In Search of Lost Domain Generalization (DomainBed)   (mã trích dẫn: chưa có số, xem ghi chú dưới)

- Người đọc: Phạm Xuân Thiên   Ngày: 26/11/2026   Thời gian đọc: 2,0 giờ
- Nơi công bố và hạng: ICLR 2021 (International Conference on Learning Representations). CORE: A* (theo CORE2023, chưa tra lại trên portal)
- Bản chính thức: OpenReview ICLR 2021, <https://openreview.net/forum?id=lQdXeXDoWtI> (mở lại kiểm link). Bản đã đọc: arXiv 2007.01434 v1 (2/7/2020), lúc đó còn ghi "Preprint. Under review"

Mã trích dẫn: bài chưa có trong danh mục `bao_cao/refs.js` (đang hết ở [44]), mới chỉ thêm vào `BaoCao/ref_bib_them_2511.bib` với khóa `gulrajani2021search`. Khi chốt danh mục thì đánh số rồi đổi tên file `[n]_...` cho khớp.

Lưu ý: số liệu trong phiếu lấy từ arXiv v1. Bản ICLR hình như có cập nhật thêm thuật toán và chạy lại bảng, nên trước khi trích con số vào báo cáo phải mở bản OpenReview đối chiếu lại Bảng 4. Số trang bên dưới là trang của bản arXiv v1.

```bibtex
@inproceedings{gulrajani2021search,
  title     = {In Search of Lost Domain Generalization},
  author    = {Gulrajani, Ishaan and Lopez-Paz, David},
  booktitle = {International Conference on Learning Representations (ICLR)},
  year      = {2021},
  url       = {https://openreview.net/forum?id=lQdXeXDoWtI}
}
```

Hai tác giả ở Facebook AI Research, ghi chú trong bài là xếp tên theo ABC, đóng góp ngang nhau.

## 1. Bài toán

Bài hỏi: các thuật toán domain generalization (DG) có thật sự hữu ích trong điều kiện thực tế không? Lý do đặt câu hỏi là các bài trước so sánh không cùng điều kiện (khác dataset, khác kiến trúc, khác cách chọn mô hình), có bài còn không nói chọn siêu tham số thế nào.

Bài này không có biến mục tiêu kiểu HR. Bài toán DG ở mục 2 (tr.2–3): có dữ liệu có nhãn của d_tr miền huấn luyện, phải dự đoán tốt trên một miền test chưa thấy, và lúc train hoàn toàn không có dữ liệu nào của miền test (khác domain adaptation vì DA còn có dữ liệu không nhãn của miền đích, xem Bảng 2 tr.3).

## 2. Dữ liệu

7 bộ ảnh nhiều miền, chi tiết ở Phụ lục C (tr.24):

| Bộ | Số miền | Số lớp | Số ảnh | Ghi chú |
|---|---|---|---|---|
| Colored MNIST | 3 | 2 | 70.000 | tổng hợp, màu tương quan với nhãn theo từng miền |
| Rotated MNIST | 6 (0°–75°) | 10 | 70.000 | tổng hợp |
| PACS | 4 | 7 | 9.991 | thật |
| VLCS | 4 | 5 | 10.729 | thật |
| Office-Home | 4 | 65 | 15.588 | thật |
| Terra Incognita | 4 (vị trí bẫy ảnh) | 10 | 24.788 | thật |
| DomainNet | 6 | 345 | 586.575 | thật |

Tất cả đều công khai, DomainBed có sẵn script tải. Ảnh thật resize về 224×224. Bài phân biệt 2 loại: bộ tổng hợp (biết trước đặc trưng nào tổng quát được nên không được augment kiểu xoay ảnh, vì như vậy là dùng prior quá nhiều) và bộ thật (mục 4.1, tr.5–6).

## 3. Giao thức đánh giá

| Mục | Bài làm gì | Trang/mục |
|---|---|---|
| Metric báo cáo | Accuracy trên miền test (out-of-distribution). Với mỗi dataset lấy trung bình qua các miền test, rồi trung bình qua 3 lần chạy | mục 5.1 tr.7, Bảng 4 tr.8 |
| Chia dữ liệu | Mỗi lần giấu 1 miền làm test, train trên các miền còn lại, lặp qua hết các miền. Trong mỗi miền chia 80/20: 80% để train và đánh giá cuối, 20% để chọn siêu tham số. Gộp train/val/test gốc của dataset rồi chia lại ngẫu nhiên theo seed. Không nói có phân tầng không | mục 5 tr.7, Phụ lục C tr.24 |
| Mất cân bằng | Không đề cập, không xử lý gì | – |
| Chọn siêu tham số | Random search 20 lần cho mỗi thuật toán × mỗi miền test. Có 3 cách chọn mô hình: (1) training-domain validation: gộp phần 20% của các miền train, chọn mô hình có acc cao nhất trên đó; (2) leave-one-domain-out CV: train d_tr mô hình, mỗi cái bỏ ra 1 miền train để đánh giá, lấy trung bình rồi train lại trên đủ d_tr miền; (3) oracle: chọn trên validation của chính miền test, giới hạn 20 lần truy vấn, không cho early stopping, chỉ lấy checkpoint cuối. Không gian tìm kiếm ở Bảng 8 | mục 3.1 tr.4, Bảng 8 tr.26 |
| Kiểm định thống kê, khoảng tin cậy | Có sai số chuẩn (±) qua 3 lần lặp toàn bộ thí nghiệm (mỗi lần random lại siêu tham số, khởi tạo trọng số và cách chia). Không có kiểm định thống kê | mục 5 tr.7 |
| Công bố mã, dữ liệu | Có: <https://github.com/facebookresearch/DomainBed> (bản v1 còn ghi "coming soon", giờ đã có repo). Dữ liệu công khai | mục 4 tr.5 |
| Rủi ro rò rỉ thông tin | Đây chính là chủ đề của bài. Tác giả chỉ ra nhiều bài trước có thể đã chọn siêu tham số trên dữ liệu test. Với Rotated MNIST, cách dựng cũ dùng chung 1000 chữ số cho mọi miền, tác giả coi đó là rò dữ liệu test nên chia đều toàn bộ MNIST cho các miền | mục 3 tr.3, mục 4.3 tr.6 |

Tổng cộng bài train 45.900 mạng nơ-ron (tr.7).

Nhóm để ý thêm vài điểm:
- Nói "không thuật toán nào hơn ERM một cách đáng kể" (tr.7) nhưng thực ra chỉ dựa vào việc chênh lệch < 1 điểm và các khoảng ±, không có test thống kê nào. Với 3 lần lặp thì ± cũng khá thô.
- ResNet-50 dùng bản pretrain trên ImageNet (Phụ lục D.1 tr.25). ImageNet là ảnh chụp thật nên khá gần với miền Photo/Real, bài không bàn chuyện này có tính là "đã thấy" miền test hay không.
- Phương án oracle vẫn được báo cáo đầy đủ trong Bảng 4, nhưng tác giả nói rõ không coi đây là cách benchmark hợp lệ.

## 4. Kết quả chính

Bảng 4 (tr.8), accuracy trung bình 7 bộ:

| Cách chọn mô hình | ERM | Tốt nhất |
|---|---|---|
| Training-domain validation | 67,0 | CORAL 67,2, Mixup 67,1 |
| Leave-one-domain-out CV | 63,8 | MMD 64,7 |
| Oracle (test-domain) | 68,9 | MMD 69,4 |

- ERM cài cẩn thận (ResNet-50, augment mạnh, tune kỹ) đã vượt mọi kết quả từng công bố trên RMNIST, PACS, VLCS, Office-Home (Bảng 1 tr.2), ví dụ PACS 85,7 so với 84,5 của Asadi et al.
- Với cùng điều kiện thì không thuật toán nào hơn ERM quá 1 điểm trung bình.
- Cách chọn mô hình ảnh hưởng rõ: training-domain validation cho kết quả tốt hơn LODO CV trên nhiều bộ. Oracle cao hơn khoảng 2%, theo tác giả là dư địa để cải thiện.
- Colored MNIST thì gần như mọi thuật toán chỉ khoảng 52% (bài toán 2 lớp), tức là không học được đặc trưng bất biến. Chỉ khi dùng oracle thì IRM mới lên được 70,2.

Có dùng làm mốc so sánh trực tiếp không: không, vì là dữ liệu ảnh. Bài có giá trị ở phần giao thức chứ không phải ở con số.

## 5. Hạn chế

Do tác giả nêu (mục 6 "Outlook", tr.7–9):
- Kết quả oracle có thể lạc quan (vì nhìn được miền test) hoặc bi quan (vì giới hạn 20 truy vấn).
- Tác giả tự hỏi các dataset này có hợp lý không, vd ngoài đời muốn phân loại tranh hoạt hình thì cứ gán nhãn vài ảnh hoạt hình là xong. Tác giả đề xuất dùng bài toán thật hơn như ảnh y tế ở nhiều bệnh viện.
- Mỗi thuật toán DG đều dựa trên một giả định bất biến không kiểm chứng được, nên tốt hay không còn tùy bài toán.
- Không khẳng định các thuật toán kia không thể vượt ERM, chỉ là trong điều kiện này thì khó.

Do nhóm nhận xét:
- Chỉ có ảnh, không có dữ liệu bảng. Không rõ kết luận "ERM là đủ mạnh" có đúng với dữ liệu bảng nhỏ như HR không.
- Không có kiểm định thống kê, chỉ có 3 lần lặp.
- Chỉ dùng accuracy. Terra Incognita là ảnh bẫy camera, loại dữ liệu này thường lệch lớp, nhưng bài không báo phân bố lớp nên không biết accuracy có bị ảnh hưởng không.
- Đọc bản arXiv v1, cần kiểm lại với bản ICLR.

## 6. Liên hệ với đề tài TB-HTL

Dùng ở phần tổng quan (định nghĩa DG khác DA, Bảng 2 của bài rất tiện để trích) và quan trọng hơn là ở phần phương pháp đánh giá. Hai khuyến nghị của bài nên trích nguyên văn:
- Recommendation 1 (tr.4): "A domain generalization algorithm should be responsible for specifying a model selection method."
- Recommendation 2 (tr.4): "Researchers should disclaim any oracle-selection results as such and specify policies to limit access to the test domain."

Áp vào đề tài: khi train trên miền A (IBM) rồi đánh giá trên miền khác thì không được tune trên miền đích. Nhóm phải ghi rõ trong báo cáo là dùng training-domain validation hay LODO, còn nếu có chạy kiểu oracle thì phải tách riêng và ghi chú là oracle. → nên kiểm lại code Cổng 0 xem hiện đang chọn siêu tham số trên tập nào.

Bài cũng cho lý do phải có baseline ERM mạnh: train gộp các nguồn, tune cẩn thận, rồi mới so phương pháp chuyển giao với nó. Nếu phương pháp của nhóm chỉ hơn ERM yếu thì không nói lên được gì.

Có chuyển giao xuyên miền (đúng là chủ đề chính), nhưng khác TB-HTL ở chỗ: DG không dùng tí dữ liệu đích nào, các miền cùng không gian đầu vào và cùng tập nhãn. Nếu các miền trong đề tài khác nhau về tập đặc trưng thì không bê nguyên DomainBed sang được, chỉ mượn giao thức.
