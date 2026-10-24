# Giải trình phần việc của Phạm Xuân Thiên (24540028)

*Trả lời câu hỏi 1, mục 7 của đánh giá 22/10/2026: phần việc Thiên đã làm từ 15/10 nằm ở file nào, và vì sao chưa có commit đứng tên Thiên.*

**Bản nháp — Thiên rà lại và sửa cho đúng thực tế trước khi gửi Minh đưa vào báo cáo 28/10.**

---

## 1. Phần việc đã làm và vị trí trong kho mã

| Phần việc | Hạn | File trong kho | Kết quả |
|---|---|---|---|
| Làm sạch bộ HR 14.999 (miền C) và Babushkin (miền D); chốt bảng ánh xạ khái niệm cho cặp AC và AD | 14/10 | `pairs.py` — các hàm `load_hr14999()`, `load_babushkin()`, `_ac()`, `_ad()`, và khai báo `PAIRS["AC"]`, `PAIRS["AD"]` | Xong 21/10 |
| Chạy thí nghiệm 2×2 cho hai cặp mới | — | `kb1_pair.py`, `kb1_pair_summary.py` | `results/kb1_AC/` (cfg `40a7ef2e`), `results/kb1_AD/` (cfg `4c085b4a`) |
| G0-2: đường cong học chỉ dùng dữ liệu đích | 18/10 | `g0_23.py` phần `family == "target_only"` | `results/g0_23/`, 6 mô hình gồm TabPFN v2; chạy 17–18/10 |
| Cổng 0 cho hai cặp mới | — | `g0_pair.py`, `g0_decision.py` | `results/g0_AC/` (`49df37eb`), `results/g0_AC_consistent/` (`2d7c34f0`), `results/g0_AD/` (`083937b0`) — **kết luận PIVOT ở cả bốn chiều** |
| KB8: so sánh cặp cùng ngữ nghĩa nhãn (AC, AD) với cặp khác ngữ nghĩa (AB) | T3 | `pairs_synthesis.py` | `results/tong_hop_cap/` — Friedman χ² = 108,19, Nemenyi CD = 3,10 |
| Phát hiện khái niệm ngược chiều ở cặp AC | — | `pairs.py`, tập `consistent` | Khái niệm `tenure` ngược chiều giữa A và C (AUC một đặc trưng 0,35 so với 0,69) nên bị loại khỏi tập `consistent` |
| Cập nhật Bảng 1–2 tổng quan tài liệu | 21/10 | mục B1.1 của báo cáo tiến độ | Một phần |

## 2. Vì sao chưa có commit đứng tên Thiên

**Nguyên nhân là quy trình, không phải do phần việc chưa làm.**

Kho Git `datachain-uit/CN-24540017-MinhTN-ThienPX` mới được thiết lập ngày **22/10/2026**. Trước đó cả nhóm trao đổi qua Google Drive. Khi lập kho, Minh đẩy toàn bộ mã và kết quả của cả hai thành viên lên trong hai commit gộp:

```
f65e85a  22/10  Gộp toàn bộ mã: KB2 (Levin), KB2b (CARTE), sinh báo cáo Word, mã cũ, bản nháp LaTeX
d03cd28  22/10  Bản đầu: mã, cấu hình, kết quả thô báo cáo tiến độ 21/10/2026
```

Vì vậy phần việc của Thiên — `pairs.py`, `kb1_pair.py`, `g0_pair.py`, `pairs_synthesis.py`, và các thư mục kết quả `kb1_AC`, `kb1_AD`, `g0_AC`, `g0_AC_consistent`, `g0_AD`, `tong_hop_cap` — **đã có trong kho nhưng mang tên tác giả là Minh**.

Nhóm nhận thấy đây là thiếu sót về quy trình và đã khắc phục:

1. Thiên gửi tên tài khoản GitHub (`CauBe9x`) để được thêm vào kho với quyền Write.
2. Thiên đặt lại `git config user.name` và `user.email` bằng địa chỉ noreply của chính mình.
3. Từ tuần 22–28/10, Thiên commit trực tiếp phần việc của mình; mã commit được ghi vào `docs/nhat_ky_tuan.md`.

## 3. Phần việc còn chậm

| Hạng mục | Hạn ban đầu | Tình trạng |
|---|---|---|
| EDA từng miền | 14/10 | **Chậm.** Đang làm, nộp trong commit đầu tiên của Thiên (`eda/eda_bon_mien.ipynb`) |
| Phiếu đọc 10 bài | 21/10 | **Chậm.** Đã nộp 5 phiếu; trong đó [10] và [43] đủ mục giao thức, ba phiếu còn lại thiếu số trang vì chưa truy cập được toàn văn |
| LightGBM, AdaBoost cho G0-2 | mục 6.3 | Chưa — xếp vào mốc 28/10 |

Lý do chậm ở phần phiếu đọc: ba trong năm bài không truy cập được toàn văn — [5] Chung (Elsevier, tường phí), [43] De Vos (Springer, tường phí), [31] Pereira & Torezzan (chưa tìm được bản công khai nào). Với [43], nhóm đã rút được giao thức từ **mã nguồn tác giả công bố** (github.com/SimonDeVos/turnover_prediction) thay cho văn bản bài báo.

## 4. Phát hiện cần báo cáo

Trong quá trình tìm bài [31] (Pereira & Torezzan, SBPO 2024), nhóm tìm ra một **luận văn UNICAMP năm 2025 của cùng tác giả thứ nhất**, do chính Cristiano Torezzan hướng dẫn:

> *Aprimoramento da predição de turnover voluntário por meio da transferência de aprendizado*
> João Pedro de Lima Pereira, UNICAMP, 2025. DOI: 10.47749/t/unicamp.2025.1546748

Theo mô tả, luận văn dùng **TrAdaBoost** để chuyển giao giữa **hai bộ dữ liệu HR công khai**, thích ứng sang miền đích bằng **một số ít mẫu có nhãn** — gần như trùng với thiết lập Cổng 0 của đề tài.

Nhóm xin ý kiến Cô hai điểm:

1. Có cần bổ sung công trình này vào Bảng 1 và phần khoảng trống nghiên cứu không?
2. Có nên đưa **TrAdaBoost** vào danh sách baseline chuyển giao của Cổng 0 không? Hiện `g0_23.py` có 8 baseline nhưng không có TrAdaBoost. Nhóm hiểu rằng đánh giá 22/10 đã chốt *"không bổ sung baseline mới"*, nên không tự ý thêm mà xin ý kiến Cô trước.
