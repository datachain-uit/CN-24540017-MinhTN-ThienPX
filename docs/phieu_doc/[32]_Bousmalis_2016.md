# Phiếu đọc: [Bousmalis et al., 2016] – Domain Separation Networks   (mã trích dẫn: [32])

- Người đọc: Phạm Xuân Thiên   Ngày: 23/10/2026   Thời gian đọc: 2,5 giờ
- Nơi công bố và hạng: NeurIPS 2016 (khi đó là NIPS). CORE A* theo CORE2023 (<https://portal.core.edu.au/conf-ranks/98/>)
- Link: <https://arxiv.org/abs/1608.06019>. Truy cập mở

```bibtex
@inproceedings{bousmalis2016domain,
  title     = {Domain Separation Networks},
  author    = {Bousmalis, Konstantinos and Trigeorgis, George and Silberman, Nathan and
               Krishnan, Dilip and Erhan, Dumitru},
  booktitle = {Advances in Neural Information Processing Systems}, volume = {29}, year = {2016}
}
```

## 1. Bài toán

Chuyển giao miền không giám sát: có nhãn ở miền nguồn, không có nhãn ở miền đích. Bối cảnh cụ thể là huấn luyện trên ảnh tổng hợp (nhãn miễn phí) rồi áp sang ảnh thật.

Lập luận cốt lõi: các phương pháp trước đó hoặc ánh xạ biểu diễn của miền này sang miền kia, hoặc học biểu diễn bất biến miền, nhưng đều bỏ qua phần đặc thù riêng của từng miền. Tác giả đề xuất mô hình hoá phần riêng đó một cách tường minh.

## 2. Dữ liệu

Toàn bộ là ảnh, không có dữ liệu bảng:

| Cặp miền | Quy mô |
|---|---|
| MNIST → MNIST-M | MNIST-M 59.001 mẫu huấn luyện, 1.000 có nhãn làm validation |
| Synthetic Digits → SVHN | 479.400 ảnh tổng hợp; 73.257 SVHN không nhãn; 26.032 test |
| SVHN → MNIST | 1.000 nhãn MNIST làm validation |
| Synthetic Signs → GTSRB | 90.000 biển báo tổng hợp; 1.280 ảnh GTSRB; 37.929 test; 43 lớp |
| Synthetic Objects → LINEMOD | 16.962 ảnh tổng hợp; 10.673 ảnh thật; 2.655 test; 11 vật thể |

## 3. Giao thức đánh giá

| Mục | Bài làm gì | Trang/mục |
|---|---|---|
| Metric báo cáo | Độ chính xác phân lớp; riêng LINEMOD thêm sai số góc trung bình | Bảng 1, Bảng 2 |
| Chia dữ liệu | Theo chuẩn có sẵn của từng bộ ảnh | Mục 4.1 |
| Mất cân bằng | Không áp dụng, các bộ ảnh đều cân bằng lớp | — |
| Chọn siêu tham số | Dùng một tập đích có nhãn nhỏ, thường 1.000 mẫu, làm validation; áp dụng cùng giao thức cho mọi phương pháp so sánh. Tác giả cũng thử reverse validation nhưng thấy kém tin cậy | Mục 4 |
| Kiểm định thống kê | Không có | — |
| Công bố mã, dữ liệu | Bộ dữ liệu công khai; bài không kèm repo chính thức | — |
| Rủi ro rò rỉ | Dùng nhãn miền đích để chọn siêu tham số. Tác giả tự thừa nhận đây là cận trên và là vấn đề mở nằm ngoài phạm vi bài. Về mặt chặt chẽ thì đây không phải chuyển giao không giám sát thuần tuý | Mục 4 |

## 4. Kết quả chính

Kiến trúc gồm bốn thành phần (mục 3): bộ mã hoá chung `E_c` nắm phần biểu diễn dùng chung giữa hai miền; bộ mã hoá riêng `E_p` cho mỗi miền nắm phần đặc thù; bộ giải mã chung `D` tái tạo ảnh từ tổng hai biểu diễn; bộ phân lớp `G` dự đoán nhãn chỉ từ biểu diễn chung.

Hàm mất mát (mục 3.1–3.2):

```
L = L_task + α·L_recon + β·L_difference + γ·L_similarity
```

`L_task` (Eq. 2) là log-likelihood âm trên mẫu nguồn có nhãn, không dùng nhãn đích. `L_recon` (Eq. 3–4) là MSE bất biến tỷ lệ, áp cho cả hai miền. `L_difference` (Eq. 5) là chuẩn Frobenius bình phương của `H_cᵀ·H_p`, ép trực giao mềm giữa biểu diễn chung và riêng. `L_similarity` có hai lựa chọn: DANN (Eq. 6, đối kháng kèm gradient reversal) hoặc MMD (Eq. 7, nhân RBF).

Độ chính xác (%), Bảng 1:

| Mô hình | MNIST→MNIST-M | SynthDigits→SVHN | SVHN→MNIST | SynthSigns→GTSRB |
|---|---|---|---|---|
| Chỉ nguồn | 56,6 | 86,7 | 59,2 | 85,1 |
| CORAL | 57,7 | 85,2 | 63,1 | 86,9 |
| MMD | 76,9 | 88,0 | 71,1 | 91,1 |
| DANN | 77,4 | 90,3 | 70,7 | 92,9 |
| DSN w/ MMD | 80,5 | 88,5 | 72,2 | 92,6 |
| DSN w/ DANN | 83,2 | 91,2 | 82,7 | 93,1 |
| Chỉ đích (cận trên) | 98,7 | 92,4 | 99,5 | 99,8 |

Không so số trực tiếp được vì toàn bộ là ảnh, nhưng ý tưởng kiến trúc dùng trực tiếp được. Đây là bài gần TB-HTL nhất về mặt tách biểu diễn chung và riêng.

## 5. Hạn chế

Do tác giả nêu:
- Không tìm được cách tinh chỉnh siêu tham số phổ quát cho chuyển giao không giám sát; reverse validation không bám sát độ chính xác trên test; việc chọn mô hình dùng nhãn đích được gọi là cận trên và là vấn đề mở.
- Thêm MMD ở nhiều tầng không cải thiện.
- Khoảng cách tới cận trên vẫn lớn: 83,2% so với 98,7% ở MNIST-M.
- Phương pháp giả định hai miền khác nhau chủ yếu ở thống kê bậc thấp, còn tham số bậc cao tương tự và cùng không gian nhãn.
- Loại Office và Caltech-256 khỏi thực nghiệm vì nhiễu nhãn và biến thiên bậc cao.

Do nhóm nhận xét:
- Giả định "khác nhau ở thống kê bậc thấp, cùng không gian nhãn" không thoả với cặp AB của đề tài: IBM và Job Change khác cả lược đồ lẫn ngữ nghĩa nhãn, chứ không chỉ khác phân phối.
- Kiến trúc cần bộ giải mã tái tạo đầu vào. Với ảnh thì tự nhiên, với dữ liệu bảng chỉ có 4–8 khái niệm chung thì bài toán tái tạo gần như vô nghĩa.
- Không có kiểm định thống kê; chênh lệch 83,2 so với 80,5 không rõ có ý nghĩa hay không.

## 6. Liên hệ với đề tài TB-HTL

Đây là nguồn ý tưởng kiến trúc hai nhánh của TB-HTL (*Two-Branch* Heterogeneous Transfer Learning). Có chuyển giao xuyên nguồn, không giám sát.

Khác TB-HTL ở dạng dữ liệu (ảnh so với bảng) và ở không gian đặc trưng (hai miền cùng không gian so với khác lược đồ). Cơ chế ép tách biệt hai nhánh của DSN là `L_difference` trực giao mềm, còn KB5 (C3) của nhóm dự kiến khảo sát ρ ∈ {0; 0,2; 0,4; 0,6}. DSN không dùng nhãn đích khi huấn luyện nhưng có dùng để chọn siêu tham số, còn Cổng 0 dùng k nhãn đích tường minh với k ∈ {10, …, 500}.

Hai điểm cần nêu khi trích dẫn. Thứ nhất, khi mô tả TB-HTL trong báo cáo phải dẫn [32] và nói rõ phần nào kế thừa (tách chung/riêng, hàm mất mát khác biệt) và phần nào khác (dữ liệu bảng khác lược đồ, có nhãn đích). Thứ hai, vấn đề chọn siêu tham số mà DSN để ngỏ chính là vấn đề nhóm phải giải: tác giả thừa nhận dùng nhãn đích để chọn siêu tham số là cận trên không chính đáng, còn giao thức Cổng 0 dùng k nhãn đích tường minh và so với baseline chỉ dùng đích tại cùng k nên chặt hơn hẳn. Đó là một ưu điểm phương pháp luận đáng nêu.
