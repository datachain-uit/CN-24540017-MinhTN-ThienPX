# Giải trình phần việc của Phạm Xuân Thiên (24540028)

*Trả lời câu hỏi 1, mục 7 của đánh giá 22/10/2026: phần việc Thiên đã làm từ 15/10 nằm ở file nào, và vì sao chưa có commit đứng tên Thiên.*

Cập nhật 24/10/2026.

---

## 1. Các commit đứng tên Thiên

| Mã | Ngày | Nội dung thực tế |
|---|---|---|
| `e689490` | 23/10/2026 | `docs/nhat_ky_tuan.md` — thêm 4 dòng nhật ký |
| `b89d1d3` | 24/10/2026 | EDA bốn miền (`eda/`), 10 phiếu đọc (`docs/phieu_doc/`), mã và kết quả chạy lại CARTE |
| `8823d07` | 24/10/2026 | Dọn dẹp lần một |

**Hai sai sót trong `b89d1d3`, Thiên nhận:**

1. Đẩy lên 3 file trùng ở thư mục gốc (`Code_ThucNghiem_CARTE.ipynb`, `bang_so_sanh.csv`, `ket_qua_cua_toi.csv`) — nội dung đã có trong `kb2b_carte/`. Kèm theo đó là 3 tệp dữ liệu rượu (`wine_pl.csv`, `wine_dot_com_prices.csv`, `wine_vivino_price.csv`, tổng ~4,3 MB) và một file `.docx` 742 KB, đều không thuộc kho mã.
2. `8823d07` sửa `kb2b_carte/README.md` ngoài phạm vi phần việc, và làm mất một ô tiêu đề của `eda/eda_bon_mien.ipynb` (−48 dòng) do mở notebook trong IDE rồi lưu lại.

Cả hai đã được xử lý trong commit dọn dẹp ngày 24/10: xóa 7 file ở thư mục gốc, khôi phục `kb2b_carte/README.md` về nguyên văn.

## 2. Phần việc đã làm và vị trí trong kho mã

| Phần việc | Hạn | File trong kho | Tình trạng |
|---|---|---|---|
| Làm sạch bộ HR 14.999 (miền C) và Babushkin (miền D); chốt bảng ánh xạ khái niệm cho cặp AC và AD | 14/10 | `pairs.py` — `load_hr14999()`, `load_babushkin()`, `_ac()`, `_ad()`, `PAIRS["AC"]`, `PAIRS["AD"]` | Xong 21/10 |
| Thí nghiệm 2×2 cho hai cặp mới | — | `kb1_pair.py`, `kb1_pair_summary.py` | `results/kb1_AC/` (cfg `40a7ef2e`), `results/kb1_AD/` (cfg `4c085b4a`) |
| G0-2: đường cong học chỉ dùng dữ liệu đích, 6 mô hình gồm TabPFN v2 | 18/10 | `g0_23.py`, phần `family == "target_only"` | `results/g0_23/`, chạy 17–18/10 |
| Cổng 0 cho hai cặp mới | — | `g0_pair.py`, `g0_decision.py` | `results/g0_AC/` (`49df37eb`), `results/g0_AC_consistent/` (`2d7c34f0`), `results/g0_AD/` (`083937b0`) — **PIVOT ở cả bốn chiều** |
| KB8: so cặp cùng ngữ nghĩa nhãn (AC, AD) với cặp khác ngữ nghĩa (AB) | T3 | `pairs_synthesis.py` | `results/tong_hop_cap/` — Friedman χ² = 108,19; Nemenyi CD = 3,10 |
| Phát hiện khái niệm ngược chiều ở cặp AC | — | `pairs.py`, tập `consistent` | `tenure` ngược chiều giữa A và C; đã loại khỏi tập `consistent` |
| EDA bốn miền | 14/10 | `eda/eda_bon_mien.ipynb` + `eda/bang1`–`bang4`, `eda/hinh/` | **Chậm.** Nộp 24/10, chạy được 3/4 miền |
| Phiếu đọc | 21/10 | `docs/phieu_doc/` | **Chậm.** 10 phiếu đã lập; 6 phiếu đủ mục giao thức |
| Bảng 1 mở rộng (cột phương pháp luận GVHD yêu cầu) | 21/10 | `docs/phieu_doc/bang1_phuong_phap_luan.csv` | 12 dòng; xem mục 4 |

## 3. Vì sao các commit trước 23/10 không đứng tên Thiên

Kho Git `datachain-uit/CN-24540017-MinhTN-ThienPX` được thiết lập ngày **22/10/2026**; trước đó nhóm trao đổi qua Google Drive. Khi lập kho, Minh đẩy toàn bộ mã của cả hai thành viên lên trong các commit gộp `d03cd28` và `f65e85a` (22/10). Vì vậy `pairs.py`, `kb1_pair.py`, `g0_pair.py`, `pairs_synthesis.py` và các thư mục kết quả `kb1_AC`, `kb1_AD`, `g0_AC`, `g0_AC_consistent`, `g0_AD`, `tong_hop_cap` **đã có trong kho nhưng mang tên tác giả là Minh**.

Đây là thiếu sót về quy trình, không phải phần việc chưa làm. Đã khắc phục: Thiên được thêm vào kho với quyền Write từ 23/10 và từ đó commit trực tiếp; mã commit ghi vào `docs/nhat_ky_tuan.md`.

## 4. Tình trạng thật của 10 phiếu đọc và Bảng 1 mở rộng

### Phiếu đọc

| Mức | Phiếu | Ghi chú |
|---|---|---|
| Đủ mục giao thức | [10], [11], [24], [32], [33], [43] | 6 phiếu |
| Còn ô chưa điền | [5], [8], [25], [31] | 4 phiếu — lý do ở dưới |

Riêng **[43]** lấy được giao thức đầy đủ từ **mã nguồn tác giả công bố** (`github.com/SimonDeVos/turnover_prediction`) thay cho văn bản bài báo, vì bài nằm sau tường phí Springer.

### Bảng 1 mở rộng — `bang1_phuong_phap_luan.csv`

Ngày 24/10 đã điền thêm từ toàn văn ba bài: **[4]** Alsheref (toàn văn mở ở PMC9251085), **[6]** Li (PMC10557501), **[7]** Mohiuddin (arXiv 2304.03103, bản được nhận CIKM 2023). Bài **[1]** Sexton điền từ bản tóm tắt chính thức trên kho BearWorks của ĐH Missouri State.

| Dòng | Mức điền |
|---|---|
| [4], [6], [7], [10], [43] | Đủ — có số mục/bảng dẫn nguồn |
| [1] | Đủ 4 ô, nguồn là tóm tắt chính thức chứ không phải toàn văn |
| [8], [31] | Một phần |
| [2], [3], [5], [9] | Chưa điền được ba ô giao thức |

**Những ô chưa điền được và lý do — không có ô nào bị bỏ trống hay suy đoán:**

| Bài | Vì sao | Lấy ở đâu |
|---|---|---|
| [2] Saradhi & Palshikar 2011 | Tường phí ScienceDirect, không có bản công khai | Thư viện UIT, DOI 10.1016/j.eswa.2010.07.134 |
| [3] Jain et al. 2020 | **Bài là truy cập mở**, Springer chặn tải tự động | Mở `link.springer.com/article/10.1007/s42452-020-2519-4` trên trình duyệt |
| [5] Chung et al. 2023 | Tường phí Elsevier | Thư viện UIT, DOI 10.1016/j.eswa.2022.119364 |
| [8] Baydili & Tasci 2025 | **Bài là truy cập mở**, MDPI chặn tải tự động | Mở `mdpi.com/2079-8954/13/7/583` trên trình duyệt |
| [9] Veglio et al. 2025 | **Bài là truy cập mở (CC BY)**, kho CBS chặn tải tự động | `research.cbs.dk/files/105584736/s11846-024-00769-7.pdf` |
| [25] Hollmann et al. 2025 | Nature đòi đăng nhập | Mạng UIT / thư viện trường |
| [31] Pereira & Torezzan 2024 | Chưa tìm được bản công khai nào. Đã tra kỷ yếu Galoá, OpenAlex, Semantic Scholar, kho UNICAMP, DBLP | Liên hệ tác giả, hoặc kỷ yếu SBPO qua thư viện |

Bốn bài [3], [8], [9] và một phần [25] là **truy cập mở** — chỉ cần mở trình duyệt là tải được, không phải xin thư viện. Thiên nhận phần này.

## 5. Hai điểm phát hiện khi đọc, xin ý kiến Cô

**(a) Luận văn UNICAMP 2025 gần đề tài hơn bài [31].** Khi tìm bài [31] (Pereira & Torezzan, SBPO 2024), nhóm tìm ra luận văn của **cùng tác giả thứ nhất**, do chính Cristiano Torezzan hướng dẫn:

> *Aprimoramento da predição de turnover voluntário por meio da transferência de aprendizado*
> João Pedro de Lima Pereira, UNICAMP, 2025. DOI: 10.47749/t/unicamp.2025.1546748

Theo mô tả, luận văn dùng **TrAdaBoost** chuyển giao giữa **hai bộ dữ liệu HR công khai**, thích ứng sang miền đích bằng **một số ít mẫu có nhãn** — gần như trùng thiết lập Cổng 0 của đề tài. Nhóm xin ý kiến Cô:

1. Có cần bổ sung công trình này vào Bảng 1 và phần khoảng trống nghiên cứu không?
2. Có nên đưa **TrAdaBoost** vào danh sách baseline chuyển giao của Cổng 0 không? Hiện `g0_23.py` có 8 baseline nhưng không có TrAdaBoost. Đánh giá 22/10 đã chốt *"không bổ sung baseline mới"*, nên nhóm **không tự thêm** mà xin ý kiến Cô trước.

**(b) Hai chỗ cần sửa lại trong Bảng 1 hiện có.**

- Bảng 1 ghi dữ liệu của **[4]** Alsheref là *"IBM HR"*. Toàn văn bài lại ghi dữ liệu lấy từ *"thư viện SAS"*, 35 biến, khoảng 1.500 dòng — quy mô trùng IBM HR (1.470 × 35) nhưng **bài không gọi tên IBM**. Cần đối chiếu lại trước khi đưa vào báo cáo.
- Bài **[6]** Li là mốc so sánh **dùng được trực tiếp** mà Bảng 1 hiện chưa khai thác: cùng bộ IBM HR (1.470 dòng, 16,1% dương), giao thức sạch (phân tầng 85/15, không tái cân bằng, grid search 5-fold trên tập development, có t-test trên 10 lần chạy), mã và dữ liệu công bố kèm bài. AUC-ROC của bài là **0,7452**, thấp hơn **0,840** nhóm đo bằng TabPFN v2 và **0,829** bằng Logistic Regression trên cùng bộ. Đây là chứng cứ bên ngoài cho thấy baseline chỉ-dùng-đích của nhóm không yếu, nên dùng khi lập luận cho kết luận PIVOT.

## 6. Phần việc còn chậm, chưa xong

| Hạng mục | Tình trạng |
|---|---|
| EDA miền D (Babushkin) | **Chưa chạy** — thiếu `data/turnover.csv`. Ba miền A, B, C đã chạy đủ. Nguồn: Kaggle `davinwijaya/employee-turnover`, kiểm bằng SHA-256 trong `data/README.md` |
| Toàn văn 4 bài [2], [3], [5], [9] + [25], [31] | Chưa có (mục 4) |
| LightGBM, AdaBoost cho G0-2 (mục 6.3) | Chưa — xếp vào mốc 28/10 |
| Phiếu đọc các bài còn lại của Bảng 1 | Chưa |

## 7. Công cụ

Phần tra cứu tài liệu, lấy toàn văn và dựng notebook EDA có dùng công cụ AI hỗ trợ, dưới sự kiểm tra của Thiên; các số liệu trong `eda/` đều do notebook chạy trên dữ liệu thật sinh ra và khớp Bảng 12 của báo cáo 22/10. Nhóm sẽ ghi mục *Declaration of Generative AI and AI-assisted technologies in the writing process* ở cuối bản thảo, trước phần tài liệu tham khảo, theo đúng yêu cầu ô ID 2 của hướng dẫn.
