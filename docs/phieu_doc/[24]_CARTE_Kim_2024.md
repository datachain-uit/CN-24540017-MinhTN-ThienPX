# Phiếu đọc: [Kim, Grinsztajn & Varoquaux, 2024] – CARTE   (mã trích dẫn trong báo cáo: [24])

- Người đọc: Phạm Xuân Thiên   Ngày: …/10/2026   Thời gian đọc: … giờ
- Nơi công bố và hạng: **ICML 2024** – *International Conference on Machine Learning*, PMLR tập 235, tr. 23843–23866. CORE **A\*** theo CORE2023 (tra tại <https://portal.core.edu.au/conf-ranks/1121/>)
- Link bản chính thức: <https://proceedings.mlr.press/v235/kim24d.html> · arXiv <https://arxiv.org/abs/2402.16785>
- Mã nguồn: <https://github.com/soda-inria/carte>
- Công bố 21/07/2024. Truy cập mở.

```bibtex
@inproceedings{kim2024carte,
  title     = {{CARTE}: Pretraining and Transfer for Tabular Learning},
  author    = {Kim, Myung Jun and Grinsztajn, L{\'e}o and Varoquaux, Ga{\"e}l},
  booktitle = {Proceedings of the 41st International Conference on Machine Learning},
  series    = {PMLR},
  volume    = {235},
  pages     = {23843--23866},
  year      = {2024}
}
```

## 1. Bài toán

Với ảnh và văn bản, mô hình tiền huấn luyện là giải pháp mặc định. Với dữ liệu bảng thì không, vì học chuyển giao giữa các bảng vấp phải bài toán **tích hợp dữ liệu**: phải giải *khớp lược đồ* (cột nào ứng cột nào) và *khớp thực thể* (giá trị viết khác nhau cùng chỉ một đối tượng).

CARTE đề xuất một kiến trúc **không cần cả hai phép khớp đó**, nhờ vậy tiền huấn luyện được trên dữ liệu nền chưa hề khớp.

Biến mục tiêu: do người dùng định nghĩa ở bảng đích — hỗ trợ cả hồi quy lẫn phân loại.

## 2. Dữ liệu

| Vai trò | Bộ | Quy mô |
|---|---|---|
| Tiền huấn luyện | **YAGO3** (đồ thị tri thức từ Wikidata) | >18,1 triệu bộ ba, 6,3 triệu thực thể |
| Đánh giá | **51 tập dữ liệu bảng** | 40 hồi quy + 11 phân loại |
| So sánh bổ sung | 9 tập của TabLLM | — |

51 tập thu thập từ nghiên cứu ML trước đây và Kaggle, chủ đề đa dạng (tai nạn, bầu cử, thù lao, thực phẩm, nhà hàng). Tác giả chọn có chủ ý các tập **có tên cột mang ý nghĩa và nhiều ô dạng chữ**, khác với phần lớn tập của UCI.

## 3. Giao thức đánh giá

| Mục | Bài làm gì | Trang/mục trong bài |
|---|---|---|
| Metric báo cáo | **R²** cho hồi quy, **AUROC** cho phân loại. Thêm *điểm chuẩn hoá* (normalized score) theo Grinsztajn 2022, với ρ = 0 cho hồi quy và ρ = 0,5 cho phân loại | Mục 4.2; Phụ lục A.2 |
| Chia dữ liệu | Hold-out với cỡ train hạn chế: **32, 64, 128, 256, 512, 1.024, 2.048**; phần còn lại làm test. Lặp trên **10 lần chia train/test** khác nhau | Phụ lục A.2 |
| Mất cân bằng | **Không xử lý** — bài không đề cập tái lấy mẫu | — |
| Chọn siêu tham số | Kiểm định chéo **5-fold**. **CARTE chỉ tinh chỉnh tốc độ học** (lưới 6 giá trị: [2,5; 5; 7,5] × [1e−4, 1e−3]); các baseline dùng **random search 100 vòng**; TabPFN dùng giá trị mặc định | Phụ lục A.2; Bảng 4 |
| Kiểm định thống kê, khoảng tin cậy | **Có** — kiểm định **Friedman** kèm hậu định **Conover**, trình bày bằng biểu đồ khác biệt tới hạn | Mục 4.2 |
| Công bố mã, dữ liệu | **Có** — github.com/soda-inria/carte; mô hình tiền huấn luyện 40 MB đi kèm gói pip; **toàn bộ 78.980 lượt chạy** của benchmark lưu trong repo (`results_carte_baseline_singletable.csv`) | Phụ lục A.4 |
| Rủi ro rò rỉ thông tin | **Thấp.** Tiền xử lý số bằng power transform; mã hoá khái niệm chung fit riêng trên phần train của từng miền (C1). Tiền huấn luyện trên YAGO, hoàn toàn tách khỏi 51 tập đánh giá. Điểm cần lưu ý: **chỉ tinh chỉnh 1 siêu tham số** cho CARTE trong khi baseline được random search 100 vòng — thiên vị này **có lợi cho baseline**, nên kết luận thận trọng | Mục 4.1; Phụ lục A.2 |

## 4. Kết quả chính

**Phương pháp.** Mỗi dòng của bảng trở thành một **đồ thị hình sao**: nút lá là giá trị ô, cạnh mang nhãn là tên cột, nút trung tâm gom thông tin cả dòng. Đặc trưng khởi tạo bằng **FastText 300 chiều**; giá trị số lấy tích của giá trị với vector nhúng tên cột.

Kiến trúc là Transformer encoder chuyển thành mạng chú ý trên đồ thị, với điểm khác biệt là **self-attention tính từ cả nút lẫn cạnh**:

```
Q = X·W_Q        K = (X ⊙ E)·W_K        V = (X ⊙ E)·W_V
```

Tiền huấn luyện tự giám sát bằng **contrastive loss InfoNCE** trên YAGO: 12 tầng chú ý × 12 đầu, chiều ẩn 300, >9,3 triệu tham số, 1.000.000 bước (~40 epoch), batch 256, AdamW + cosine (5e−6 → 1e−4), warmup 10.000 bước, dropout 0,1, GELU. Chạy trên GPU NVIDIA V100 32GB.

Tinh chỉnh xuôi dòng chỉ dùng **1 tầng chú ý** (tránh over-smoothing) cộng bagging 10 mô hình.

**Kết quả:**

| Kết quả | Chi tiết |
|---|---|
| Vượt 42 baseline | Nhất quán ở mọi cỡ mẫu, cả hồi quy lẫn phân loại |
| **Không cần khớp thực thể** | KEN phải khớp thủ công mới tốt; CARTE cho kết quả như nhau dù dùng tên gốc hay tên chuẩn hoá |
| **Không cần khớp lược đồ** | 275 trường hợp, có/không khớp cột thủ công cho kết quả tương đương, **p = 0,728** |
| Bền với dữ liệu thiếu | Bỏ 10% đặc trưng ở n = 64: CARTE sụt 13,28%, CatBoost sụt 21,70% |
| Thêm bảng nguồn thì tốt hơn | Cả trung vị lẫn cận dưới biến thiên đều cải thiện |

**Có dùng làm mốc so sánh được không? — Có, và nhóm đã làm.** KB2b đã tái hiện CARTE trên 3 bộ dữ liệu giá rượu, 12 lượt chạy, đối chiếu với kết quả công bố: **tương quan 0,950**, chênh lệch tuyệt đối trung bình **0,043**, 11/12 lượt chênh dưới 0,10, 5/6 cấu hình nằm trong khoảng ±1 độ lệch chuẩn giữa các seed của chính bài báo. Chi tiết ở `kb2b_carte/` và mục A5.3 của báo cáo tiến độ.

## 5. Hạn chế

**Do tác giả nêu:**
- **Chi phí tính toán cao:** n = 64 cần 85,4 giây so với ~1 giây của CatBoost; n = 512 cần 315,5 giây. Khoảng cách nới rộng khi dữ liệu lớn.
- **Thế mạnh nằm ở dữ liệu nhiều giá trị dạng chữ.** Trên bộ TabLLM (chủ yếu số, lực lượng phân loại thấp), **TabPFN tốt nhất, CARTE chỉ thứ hai**.
- Tài liệu cài đặt khuyến nghị tối thiểu **64 GB RAM** cho bảng đơn, 128 GB cho đa bảng.

**Do nhóm nhận xét:**
- **Vẫn đòi hỏi biến mục tiêu của hai bảng tương tự nhau về ý nghĩa** (mục 3.3: *"chúng ta cần có các kết quả đầu ra y_S và y_T tương tự nhau trên cả hai bảng"*). CARTE gỡ được khớp lược đồ và khớp thực thể, **không gỡ được rào cản ngữ nghĩa nhãn**.
- Chỉ tinh chỉnh 1 siêu tham số trong khi baseline được random search 100 vòng — tuy thiên vị theo hướng có lợi cho baseline nhưng vẫn là so sánh không cân.
- Tái hiện của nhóm cho thấy trên tập `wina_pl` tại n = 128, CARTE **đứng thứ hai** (R² 0,419) sau `tablevectorizer_ridge` (0,421) — tức ưu thế của CARTE là ở **trung bình trên 51 tập**, không phải thắng mọi tập.

## 6. Liên hệ với đề tài TB-HTL

**Dùng ở đâu:** là **baseline xuyên bảng dựa vào tên cột** (KB2b), và là một trong hai bài gốc của hướng học chuyển giao cho dữ liệu bảng mà đề tài dựa vào (cùng [11] Levin).

**Có chuyển giao xuyên nguồn không: CÓ** — đây là nội dung chính của bài.

**Khác gì với TB-HTL:**

| | CARTE [24] | TB-HTL |
|---|---|---|
| Cách bắc cầu giữa hai bảng | Biểu diễn đồ thị + nhúng **tên cột** | Ánh xạ khái niệm chung thủ công, có kiểm tra chiều tác động |
| Có cần khớp cột không | Không | Có — và đó là giới hạn nhóm đang đo |
| Ngữ nghĩa nhãn | **Giả định hai bảng có nhãn tương tự** | Khảo sát cả cùng (AC, AD) lẫn khác (AB) ngữ nghĩa |
| Tiền huấn luyện | YAGO, 18,1 triệu bộ ba | Không tiền huấn luyện |
| Chi phí | Cao (85 s ở n = 64) | Thấp hơn nhiều |

**Hai giá trị trực tiếp cho đề tài:**

1. **CARTE giải được rào cản biểu diễn.** Thực nghiệm KB1 v2 cho thấy ép hai miền về 4 khái niệm chung làm mất khoảng **0,18 AUC**, trong khi lệch miền chỉ gây mất **0,015**. CARTE cho phép học xuyên bảng mà không phải vứt bỏ các cột riêng của từng miền — đúng chỗ mất mát lớn nhất.

2. **CARTE không giải được rào cản ngữ nghĩa nhãn**, vì vẫn yêu cầu `y_S` và `y_T` tương tự. Với cặp AB của nhóm (hành vi ↔ ý định), điều kiện này **không thoả**. Đây là ranh giới rõ ràng giữa hai bài toán, nên nêu trong phần thảo luận.

---

## Ô cần điền vào `bang1_phuong_phap_luan.csv`

Bài này thuộc **Bảng 2** (nền tảng học chuyển giao), không phải Bảng 1. Không cần điền ô nào.

---

## Việc còn lại

Phiếu này **đã đầy đủ**. Nguồn tham chiếu bổ sung có sẵn trong kho của nhóm:

- Bản dịch tiếng Việt toàn văn: `../../CARTE_ban_dich_tieng_viet.md` *(ngoài kho Git)*
- Mã và kết quả tái hiện: `kb2b_carte/`
- Kết quả công bố của tác giả, lọc 3 bộ rượu: `kb2b_carte/ket_qua/carte_cong_bo_3_bo_ruou.csv`
