# Phiếu đọc: [Hollmann et al., 2025] – TabPFN v2   (mã trích dẫn trong báo cáo: [25])

- Người đọc: Phạm Xuân Thiên   Ngày: …/10/2026   Thời gian đọc: … giờ
- Nơi công bố và hạng: **Nature**, tập 637, số 8045, tr. 319–326. Scimago **Q1** – Multidisciplinary, thuộc nhóm tạp chí có uy tín cao nhất (tra …/10/2026, Thiên xác nhận lại)
- DOI: <https://doi.org/10.1038/s41586-024-08328-6>
- Mã nguồn: <https://github.com/PriorLabs/TabPFN> · Trọng số: <https://huggingface.co/Prior-Labs/TabPFN-v2-clf>

> ⚠️ **Phạm vi của phiếu này.** Trang Nature chuyển hướng sang đăng nhập, nhóm chưa truy cập được toàn văn.
> Phần dưới dựng từ **siêu dữ liệu đã kiểm chứng**, **tài liệu mã nguồn công khai**, và **số liệu do chính nhóm đo được** khi chạy TabPFN v2 trong Cổng 0.
> Mục 3 còn nhiều ô **?** — cần toàn văn để điền.

```bibtex
@article{hollmann2025accurate,
  title   = {Accurate predictions on small data with a tabular foundation model},
  author  = {Hollmann, Noah and M{\"u}ller, Samuel and Purucker, Lennart and
             Krishnakumar, Arjun and K{\"o}rfer, Max and Hoo, Shi Bin and
             Schirrmeister, Robin Tibor and Hutter, Frank},
  journal = {Nature},
  volume  = {637},
  number  = {8045},
  pages   = {319--326},
  year    = {2025},
  doi     = {10.1038/s41586-024-08328-6}
}
```

> ⚠️ Danh sách tác giả ở trên lấy từ nguồn thứ cấp — **Thiên xác nhận lại trên trang Nature** trước khi đưa vào tài liệu tham khảo.

## 1. Bài toán

Xây dựng **mô hình nền tảng cho dữ liệu bảng**: một mô hình đã tiền huấn luyện sẵn, áp thẳng vào bảng mới **không cần huấn luyện lại**, chỉ cần một lượt truyền xuôi.

Cơ chế là **Prior-data Fitted Network** — mô hình được tiền huấn luyện trên lượng lớn **dữ liệu bảng tổng hợp** sinh từ một phân phối tiên nghiệm, qua đó học được các thiên kiến quy nạp đặc trưng của dữ liệu bảng. Khi dùng, dữ liệu huấn luyện của người dùng được đưa vào như **ngữ cảnh** (in-context learning) thay vì để cập nhật trọng số.

## 2. Dữ liệu

**Tiền huấn luyện:** dữ liệu bảng tổng hợp. **Số lượng cụ thể: ?** *(cần toàn văn)*

**Đánh giá:** các bộ đối sánh dữ liệu bảng chuẩn. **Danh sách và quy mô: ?**

**Giới hạn quy mô — điểm quan trọng nhất của bài:** mô hình vượt các phương pháp trước đó trên **bộ dữ liệu tới khoảng 10.000 mẫu**. Trên mức đó thì không còn áp dụng trực tiếp được.

> ✅ **Nhóm đã kiểm chứng giới hạn này trong thực tế.** `TAI_LAP.md` ghi: *"TabPFN v2 không chạy ở mức 'toàn bộ' khi tập huấn luyện vượt 10.000 dòng (đích Job Change); ở 2×2 tập huấn luyện được rút phân tầng còn 10.000 dòng."* Đúng như bài báo công bố.

## 3. Giao thức đánh giá

| Mục | Bài làm gì | Trang/mục trong bài |
|---|---|---|
| Metric báo cáo | **?** — nhiều khả năng ROC-AUC cho phân loại | ? |
| Chia dữ liệu | **?** | ? |
| Mất cân bằng | **?** | ? |
| Chọn siêu tham số | TabPFN v2 **không cần tinh chỉnh** — dùng mặc định là đặc điểm bán hàng chính của bài. Ngân sách tinh chỉnh dành cho baseline: **?** | ? |
| Kiểm định thống kê, khoảng tin cậy | **?** | ? |
| Công bố mã, dữ liệu | **Có** — github.com/PriorLabs/TabPFN; trọng số trên HuggingFace dưới giấy phép Prior Labs (Apache 2.0 kèm điều khoản ghi công) | README repo |
| Rủi ro rò rỉ thông tin | **?** — cần kiểm riêng: các bộ đánh giá có nằm trong phân phối tiên nghiệm dùng để sinh dữ liệu tiền huấn luyện không | ? |

## 4. Kết quả chính

Theo thông cáo của Đại học Freiburg và tóm tắt bài: TabPFN **vượt các phương pháp trước đó** trên bộ dữ liệu tới khoảng **10.000 mẫu**, và **nhanh hơn đáng kể** vì không phải huấn luyện.

**Có dùng làm mốc so sánh được không? — Có, và nhóm đã dùng.** TabPFN v2 là một trong 6 mô hình **chỉ dùng đích** của G0-2, chạy trên Colab GPU Tesla T4 (390 lượt ngày 18/10, thêm 300 lượt 2×2 và 840 lượt Cổng 0 ngày 21/10).

**Số liệu nhóm tự đo — PR-AUC trung bình theo k, 30 lần chia:**

| Đích | k = 10 | 20 | 50 | 100 | 200 | 500 | toàn bộ |
|---|---|---|---|---|---|---|---|
| **A** (IBM) | 0,290 | 0,303 | 0,369 | 0,391 | 0,458 | 0,558 | **0,634** |
| **B** (Job Change) | 0,324 | 0,364 | 0,409 | 0,455 | 0,489 | 0,517 | — *(vượt 10.000 dòng)* |
| **C** (HR 14.999) | 0,413 | 0,505 | 0,779 | 0,919 | 0,945 | 0,957 | **0,972** |
| **D** (Babushkin) | 0,532 | 0,532 | 0,547 | 0,555 | 0,579 | 0,619 | 0,644 |

Trên đủ đặc trưng miền A, TabPFN v2 đạt **AUC-ROC 0,840** — cao nhất trong các mô hình nhóm thử, hơn Logistic Regression (0,829).

**Xếp hạng Friedman trên 41 khối, 14 phương pháp:** TabPFN v2 đứng **hạng trung bình 5,829**, **thứ hai** sau Random Forest (4,951) và trên Stacking (6,268). Đáng chú ý: **mọi phương pháp chuyển giao đều xếp sau nó**.

> 📌 **Vì sao điều này quan trọng với Cổng 0.** Tiêu chí GO của nhóm là vượt **baseline chỉ-dùng-đích MẠNH NHẤT** tại cùng k, và TabPFN v2 nằm trong nhóm đó. `g0_decision.py` có ghi chú rõ: *"nếu là PIVOT thì TabPFN không thể đổi thành GO — nó chỉ làm baseline mạnh hơn"*. Việc đưa TabPFN v2 vào làm cho kết luận PIVOT **chặt hơn**, không phải yếu đi.

Lưu ý về miền D: PR-AUC của TabPFN chỉ 0,532 ở k = 10, trong khi **tỷ lệ dương của D là 51%** — tức gần như không hơn đoán ngẫu nhiên. Đây là minh hoạ cho việc không so PR-AUC giữa các miền có tỷ lệ dương khác nhau.

## 5. Hạn chế

**Do tác giả nêu:**
- **Giới hạn khoảng 10.000 mẫu** — ngoài phạm vi đó mô hình không còn là lựa chọn tốt nhất.
- *(các hạn chế khác: **?**, cần toàn văn)*

**Do nhóm nhận xét:**
- Giới hạn 10.000 mẫu gây vướng thật trong đề tài: miền B có 19.084 dòng nên **không chạy được mức "toàn bộ"**, phải rút phân tầng xuống 10.000. Bảng kết quả vì vậy có ô trống, cần chú thích khi trình bày.
- Cần GPU. Nhóm phải chạy riêng trên Colab, không gộp được vào luồng CPU của `g0_23.py`.
- Là mô hình hộp đen đã tiền huấn luyện — khó diễn giải, trong khi RQ5 của đề tài có yêu cầu về khả năng giải thích (SHAP).
- **Chưa kiểm chứng được khả năng rò rỉ qua phân phối tiên nghiệm**: nếu các bộ dữ liệu đối sánh công khai có ảnh hưởng tới cách sinh dữ liệu tổng hợp thì kết quả sẽ lạc quan. Cần đọc phần mô tả prior trong bài.

## 6. Liên hệ với đề tài TB-HTL

**Dùng ở đâu:** **baseline chỉ-dùng-đích mạnh nhất** ở nhiều mức k trong G0-2, và là một trong các mô hình của thí nghiệm 2×2 (KB1 v2).

**Có chuyển giao xuyên nguồn không: KHÔNG.** TabPFN v2 huấn luyện và dự đoán **trong cùng một bảng**. Tri thức nó mang theo đến từ **dữ liệu tổng hợp lúc tiền huấn luyện**, không phải từ miền nguồn của người dùng.

**Khác gì với TB-HTL:**

| | TabPFN v2 [25] | TB-HTL |
|---|---|---|
| Nguồn tri thức | Dữ liệu bảng **tổng hợp** sinh từ prior | **Miền nguồn thật** của người dùng |
| Có dùng miền nguồn không | Không | Có |
| Cần huấn luyện lại không | Không — một lượt truyền xuôi | Có |
| Giới hạn quy mô | ~10.000 mẫu | Không |
| Vai trò trong Cổng 0 | **Baseline chỉ dùng đích** | Phương pháp được đánh giá |

**Điểm mấu chốt:** TabPFN v2 là **đối thủ khó nhất** mà TB-HTL phải vượt. Nó cho thấy một phần đáng kể lợi ích mà người ta tưởng đến từ "chuyển giao" thực ra có thể đạt được **chỉ bằng một mô hình nền tảng tốt, không cần miền nguồn nào cả**. Kết quả Friedman của nhóm xác nhận: TabPFN v2 hạng 5,829, trong khi **baseline chuyển giao tốt nhất (Daumé+LR) chỉ hạng 6,366**.

Đây là lập luận quan trọng cần nêu khi giải thích kết luận PIVOT: không phải chuyển giao vô dụng, mà là **các baseline chỉ dùng đích đã quá mạnh** ở mức k mà đề tài khảo sát.

---

## Ô cần điền vào `bang1_phuong_phap_luan.csv`

Bài này thuộc **Bảng 2** (nền tảng học trên dữ liệu bảng), không phải Bảng 1. Không cần điền ô nào.

---

## Việc còn lại của phiếu này

Cần toàn văn để điền mục 3. Ba hướng lấy bài:

1. Mạng UIT / thư viện trường (Nature qua Springer Nature)
2. Tìm bản chấp nhận đăng trên trang nhóm tác giả (AutoML Freiburg, Frank Hutter) — nhiều nhóm tự lưu bản PDF
3. Bản arXiv tiền thân của TabPFN v1 (<https://arxiv.org/abs/2207.01848>) — **không thay thế được**, vì v1 và v2 khác nhau đáng kể

Khi có bài, ưu tiên điền: **metric, giao thức chia, cách sinh dữ liệu tiền huấn luyện**, và kiểm riêng khả năng rò rỉ qua phân phối tiên nghiệm.
