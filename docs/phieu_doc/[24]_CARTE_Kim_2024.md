# Phiếu đọc: [Kim, Grinsztajn & Varoquaux, 2024] – CARTE   (mã trích dẫn: [24])

- Người đọc: Phạm Xuân Thiên   Ngày: 23/10/2026   Thời gian đọc: 4,0 giờ
- Nơi công bố và hạng: ICML 2024, PMLR t.235, tr. 23843–23866. CORE A* theo CORE2023 (<https://portal.core.edu.au/conf-ranks/1121/>)
- Link: <https://proceedings.mlr.press/v235/kim24d.html> · arXiv <https://arxiv.org/abs/2402.16785>. Truy cập mở
- Mã nguồn: <https://github.com/soda-inria/carte>

```bibtex
@inproceedings{kim2024carte,
  title     = {{CARTE}: Pretraining and Transfer for Tabular Learning},
  author    = {Kim, Myung Jun and Grinsztajn, L{\'e}o and Varoquaux, Ga{\"e}l},
  booktitle = {Proceedings of the 41st International Conference on Machine Learning},
  series    = {PMLR}, volume = {235}, pages = {23843--23866}, year = {2024}
}
```

## 1. Bài toán

Với ảnh và văn bản, mô hình tiền huấn luyện là giải pháp mặc định. Với dữ liệu bảng thì không, vì học chuyển giao giữa các bảng vấp phải bài toán tích hợp dữ liệu: phải giải khớp lược đồ (cột nào ứng cột nào) và khớp thực thể (giá trị viết khác nhau cùng chỉ một đối tượng).

CARTE đề xuất kiến trúc không cần cả hai phép khớp đó, nhờ vậy tiền huấn luyện được trên dữ liệu nền chưa hề khớp. Biến mục tiêu do người dùng định nghĩa ở bảng đích, hỗ trợ cả hồi quy lẫn phân loại.

## 2. Dữ liệu

| Vai trò | Bộ | Quy mô |
|---|---|---|
| Tiền huấn luyện | YAGO3 (đồ thị tri thức từ Wikidata) | >18,1 triệu bộ ba, 6,3 triệu thực thể |
| Đánh giá | 51 tập dữ liệu bảng | 40 hồi quy + 11 phân loại |
| So sánh bổ sung | 9 tập của TabLLM | — |

51 tập thu thập từ nghiên cứu ML trước đây và Kaggle, chủ đề đa dạng. Tác giả chọn có chủ ý các tập có tên cột mang ý nghĩa và nhiều ô dạng chữ, khác với phần lớn tập của UCI.

## 3. Giao thức đánh giá

| Mục | Bài làm gì | Trang/mục |
|---|---|---|
| Metric báo cáo | R² cho hồi quy, AUROC cho phân loại. Thêm điểm chuẩn hoá theo Grinsztajn 2022, ρ = 0 cho hồi quy và ρ = 0,5 cho phân loại | Mục 4.2; Phụ lục A.2 |
| Chia dữ liệu | Hold-out với cỡ train hạn chế 32, 64, 128, 256, 512, 1.024, 2.048; phần còn lại làm test. Lặp trên 10 lần chia khác nhau | Phụ lục A.2 |
| Mất cân bằng | Không xử lý, bài không đề cập tái lấy mẫu | — |
| Chọn siêu tham số | Kiểm định chéo 5-fold. CARTE chỉ tinh chỉnh tốc độ học, lưới 6 giá trị [2,5; 5; 7,5] × [1e−4, 1e−3]; các baseline dùng random search 100 vòng; TabPFN dùng mặc định | Phụ lục A.2; Bảng 4 |
| Kiểm định thống kê | Có. Friedman kèm hậu định Conover, trình bày bằng biểu đồ khác biệt tới hạn | Mục 4.2 |
| Công bố mã, dữ liệu | Có. Mô hình tiền huấn luyện 40 MB đi kèm gói pip; toàn bộ 78.980 lượt chạy của benchmark lưu trong repo | Phụ lục A.4 |
| Rủi ro rò rỉ | Thấp. Tiền xử lý số bằng power transform; tiền huấn luyện trên YAGO, tách hoàn toàn khỏi 51 tập đánh giá. Điểm cần lưu ý: CARTE chỉ tinh chỉnh 1 siêu tham số trong khi baseline được random search 100 vòng. Thiên vị này có lợi cho baseline nên kết luận vẫn thận trọng được | Mục 4.1; Phụ lục A.2 |

## 4. Kết quả chính

Mỗi dòng của bảng trở thành một đồ thị hình sao: nút lá là giá trị ô, cạnh mang nhãn là tên cột, nút trung tâm gom thông tin cả dòng. Đặc trưng khởi tạo bằng FastText 300 chiều; giá trị số lấy tích của giá trị với vector nhúng tên cột.

Kiến trúc là Transformer encoder chuyển thành mạng chú ý trên đồ thị, khác ở chỗ self-attention tính từ cả nút lẫn cạnh:

```
Q = X·W_Q        K = (X ⊙ E)·W_K        V = (X ⊙ E)·W_V
```

Tiền huấn luyện tự giám sát bằng contrastive loss InfoNCE trên YAGO: 12 tầng chú ý × 12 đầu, chiều ẩn 300, hơn 9,3 triệu tham số, 1.000.000 bước (~40 epoch), batch 256, AdamW + cosine (5e−6 → 1e−4), warmup 10.000 bước, dropout 0,1, GELU, GPU V100 32GB. Tinh chỉnh xuôi dòng chỉ dùng 1 tầng chú ý để tránh over-smoothing, cộng bagging 10 mô hình.

| Kết quả | Chi tiết |
|---|---|
| Vượt 42 baseline | Nhất quán ở mọi cỡ mẫu, cả hồi quy lẫn phân loại |
| Không cần khớp thực thể | KEN phải khớp thủ công mới tốt; CARTE cho kết quả như nhau dù dùng tên gốc hay tên chuẩn hoá |
| Không cần khớp lược đồ | 275 trường hợp, có hay không khớp cột thủ công cho kết quả tương đương, p = 0,728 |
| Bền với dữ liệu thiếu | Bỏ 10% đặc trưng ở n = 64: CARTE sụt 13,28%, CatBoost sụt 21,70% |
| Thêm bảng nguồn thì tốt hơn | Cả trung vị lẫn cận dưới biến thiên đều cải thiện |

Dùng làm mốc so sánh được, và nhóm đã làm. KB2b tái hiện CARTE trên 3 bộ dữ liệu giá rượu, 12 lượt chạy, đối chiếu với kết quả công bố: tương quan 0,950, chênh lệch tuyệt đối trung bình 0,043, 11/12 lượt chênh dưới 0,10, 5/6 cấu hình nằm trong ±1 độ lệch chuẩn giữa các seed của chính bài báo. Chi tiết ở `kb2b_carte/` và mục A5.3 của báo cáo tiến độ.

## 5. Hạn chế

Do tác giả nêu: chi phí tính toán cao, n = 64 cần 85,4 giây so với khoảng 1 giây của CatBoost, n = 512 cần 315,5 giây, khoảng cách nới rộng khi dữ liệu lớn. Thế mạnh nằm ở dữ liệu nhiều giá trị dạng chữ; trên bộ TabLLM chủ yếu là số thì TabPFN tốt nhất, CARTE chỉ thứ hai. Tài liệu cài đặt khuyến nghị tối thiểu 64 GB RAM cho bảng đơn.

Do nhóm nhận xét:
- Vẫn đòi hỏi biến mục tiêu của hai bảng tương tự nhau về ý nghĩa. Mục 3.3 ghi "chúng ta cần có các kết quả đầu ra y_S và y_T tương tự nhau trên cả hai bảng". CARTE gỡ được khớp lược đồ và khớp thực thể, không gỡ được rào cản ngữ nghĩa nhãn.
- Chỉ tinh chỉnh 1 siêu tham số trong khi baseline được random search 100 vòng; tuy thiên vị theo hướng có lợi cho baseline nhưng vẫn là so sánh không cân.
- Tái hiện của nhóm cho thấy trên tập `wina_pl` tại n = 128, CARTE đứng thứ hai (R² 0,419) sau `tablevectorizer_ridge` (0,421). Ưu thế của CARTE là ở trung bình trên 51 tập, không phải thắng mọi tập.

## 6. Liên hệ với đề tài TB-HTL

Là baseline xuyên bảng dựa vào tên cột (KB2b), và là một trong hai bài gốc của hướng học chuyển giao cho dữ liệu bảng mà đề tài dựa vào, cùng [11] Levin. Có chuyển giao xuyên nguồn, đây là nội dung chính của bài.

Khác TB-HTL ở cách bắc cầu: CARTE dùng biểu diễn đồ thị và nhúng tên cột, TB-HTL ánh xạ khái niệm chung thủ công có kiểm tra chiều tác động. CARTE giả định hai bảng có nhãn tương tự, TB-HTL khảo sát cả cùng (AC, AD) lẫn khác (AB) ngữ nghĩa. CARTE tiền huấn luyện trên YAGO 18,1 triệu bộ ba, TB-HTL không tiền huấn luyện.

Hai điểm quan trọng. CARTE giải được rào cản biểu diễn: KB1 v2 cho thấy ép hai miền về 4 khái niệm chung làm mất khoảng 0,18 AUC trong khi lệch miền chỉ gây mất 0,015, và CARTE cho phép học xuyên bảng mà không phải vứt bỏ cột riêng của từng miền, đúng chỗ mất mát lớn nhất. Nhưng CARTE không giải được rào cản ngữ nghĩa nhãn vì vẫn yêu cầu y_S và y_T tương tự; với cặp AB (hành vi ↔ ý định) điều kiện này không thoả. Đây là ranh giới rõ giữa hai bài toán, nên nêu trong phần thảo luận.

Tham chiếu bổ sung: bản dịch toàn văn `../../CARTE_ban_dich_tieng_viet.md` (ngoài kho Git), mã tái hiện `kb2b_carte/`.
