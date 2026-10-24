# Phiếu đọc: [Hollmann et al., 2025] – TabPFN v2   (mã trích dẫn: [25])

- Người đọc: Phạm Xuân Thiên   Ngày: 23/10/2026   Thời gian đọc: 1,5 giờ
- Nơi công bố và hạng: *Nature*, t.637, số 8045, tr. 319–326. Scimago Q1 – Multidisciplinary (tra 23/10/2026)
- DOI: <https://doi.org/10.1038/s41586-024-08328-6>. Trang Nature chuyển hướng sang đăng nhập, chưa truy cập được toàn văn
- Mã nguồn: <https://github.com/PriorLabs/TabPFN> · trọng số: <https://huggingface.co/Prior-Labs/TabPFN-v2-clf>

Phần dưới dựng từ siêu dữ liệu đã kiểm chứng, tài liệu mã nguồn công khai, và số liệu do chính nhóm đo được khi chạy TabPFN v2 trong Cổng 0. Danh sách tác giả lấy từ nguồn thứ cấp, cần xác nhận trên trang Nature trước khi đưa vào tài liệu tham khảo.

```bibtex
@article{hollmann2025accurate,
  title   = {Accurate predictions on small data with a tabular foundation model},
  author  = {Hollmann, Noah and M{\"u}ller, Samuel and Purucker, Lennart and
             Krishnakumar, Arjun and K{\"o}rfer, Max and Hoo, Shi Bin and
             Schirrmeister, Robin Tibor and Hutter, Frank},
  journal = {Nature}, volume = {637}, number = {8045}, pages = {319--326}, year = {2025},
  doi     = {10.1038/s41586-024-08328-6}
}
```

## 1. Bài toán

Xây dựng mô hình nền tảng cho dữ liệu bảng: một mô hình đã tiền huấn luyện sẵn, áp thẳng vào bảng mới không cần huấn luyện lại, chỉ cần một lượt truyền xuôi.

Cơ chế là Prior-data Fitted Network. Mô hình được tiền huấn luyện trên lượng lớn dữ liệu bảng tổng hợp sinh từ một phân phối tiên nghiệm, qua đó học được các thiên kiến quy nạp đặc trưng của dữ liệu bảng. Khi dùng, dữ liệu huấn luyện của người dùng được đưa vào như ngữ cảnh thay vì để cập nhật trọng số.

## 2. Dữ liệu

Tiền huấn luyện trên dữ liệu bảng tổng hợp; số lượng cụ thể cần toàn văn. Đánh giá trên các bộ đối sánh dữ liệu bảng chuẩn; danh sách và quy mô cần toàn văn.

Điểm quan trọng nhất của bài là giới hạn quy mô: mô hình vượt các phương pháp trước đó trên bộ dữ liệu tới khoảng 10.000 mẫu, ngoài mức đó thì không còn áp dụng trực tiếp được.

Nhóm đã kiểm chứng giới hạn này. `TAI_LAP.md` ghi: "TabPFN v2 không chạy ở mức 'toàn bộ' khi tập huấn luyện vượt 10.000 dòng (đích Job Change); ở 2×2 tập huấn luyện được rút phân tầng còn 10.000 dòng." Đúng như bài báo công bố.

## 3. Giao thức đánh giá

| Mục | Bài làm gì | Trang/mục |
|---|---|---|
| Metric báo cáo | Cần toàn văn. Nhiều khả năng ROC-AUC cho phân loại, chưa xác nhận | Nature đòi đăng nhập |
| Chia dữ liệu | Cần toàn văn | Nature đòi đăng nhập |
| Mất cân bằng | Cần toàn văn | Nature đòi đăng nhập |
| Chọn siêu tham số | TabPFN v2 không cần tinh chỉnh, dùng mặc định là đặc điểm chính của bài. Ngân sách tinh chỉnh dành cho baseline: cần toàn văn | Nature đòi đăng nhập |
| Kiểm định thống kê | Cần toàn văn | Nature đòi đăng nhập |
| Công bố mã, dữ liệu | Có. github.com/PriorLabs/TabPFN; trọng số trên HuggingFace dưới giấy phép Prior Labs (Apache 2.0 kèm điều khoản ghi công) | README repo |
| Rủi ro rò rỉ | Cần toàn văn. Kiểm riêng: các bộ đánh giá có nằm trong phân phối tiên nghiệm dùng để sinh dữ liệu tiền huấn luyện không | Nature đòi đăng nhập |

## 4. Kết quả chính

Theo thông cáo của Đại học Freiburg và tóm tắt bài, TabPFN vượt các phương pháp trước đó trên bộ dữ liệu tới khoảng 10.000 mẫu, và nhanh hơn đáng kể vì không phải huấn luyện.

Dùng làm mốc so sánh được, và nhóm đã dùng. TabPFN v2 là một trong 6 mô hình chỉ dùng đích của G0-2, chạy trên Colab GPU Tesla T4: 390 lượt ngày 18/10, thêm 300 lượt 2×2 và 840 lượt Cổng 0 ngày 21/10.

PR-AUC trung bình theo k, 30 lần chia, số liệu nhóm tự đo:

| Đích | k = 10 | 20 | 50 | 100 | 200 | 500 | toàn bộ |
|---|---|---|---|---|---|---|---|
| A (IBM) | 0,290 | 0,303 | 0,369 | 0,391 | 0,458 | 0,558 | 0,634 |
| B (Job Change) | 0,324 | 0,364 | 0,409 | 0,455 | 0,489 | 0,517 | — (vượt 10.000 dòng) |
| C (HR 14.999) | 0,413 | 0,505 | 0,779 | 0,919 | 0,945 | 0,957 | 0,972 |
| D (Babushkin) | 0,532 | 0,532 | 0,547 | 0,555 | 0,579 | 0,619 | 0,644 |

Trên đủ đặc trưng miền A, TabPFN v2 đạt AUC-ROC 0,840, cao nhất trong các mô hình nhóm thử, hơn Logistic Regression (0,829).

Xếp hạng Friedman trên 41 khối, 14 phương pháp: TabPFN v2 đứng hạng trung bình 5,829, thứ hai sau Random Forest (4,951) và trên Stacking (6,268). Mọi phương pháp chuyển giao đều xếp sau nó.

Lưu ý về miền D: PR-AUC của TabPFN chỉ 0,532 ở k = 10 trong khi tỷ lệ dương của D là 51%, tức gần như không hơn đoán ngẫu nhiên. Đây là minh hoạ cho việc không so PR-AUC giữa các miền có tỷ lệ dương khác nhau.

## 5. Hạn chế

Do tác giả nêu: giới hạn khoảng 10.000 mẫu, ngoài phạm vi đó mô hình không còn là lựa chọn tốt nhất. Các hạn chế khác cần toàn văn.

Do nhóm nhận xét:
- Giới hạn 10.000 mẫu gây vướng thật: miền B có 19.084 dòng nên không chạy được mức "toàn bộ", phải rút phân tầng xuống 10.000. Bảng kết quả vì vậy có ô trống, cần chú thích khi trình bày.
- Cần GPU. Nhóm phải chạy riêng trên Colab, không gộp được vào luồng CPU của `g0_23.py`.
- Là mô hình hộp đen đã tiền huấn luyện nên khó diễn giải, trong khi RQ5 của đề tài có yêu cầu về khả năng giải thích bằng SHAP.
- Chưa kiểm chứng được khả năng rò rỉ qua phân phối tiên nghiệm. Nếu các bộ đối sánh công khai có ảnh hưởng tới cách sinh dữ liệu tổng hợp thì kết quả sẽ lạc quan. Cần đọc phần mô tả prior trong bài.

## 6. Liên hệ với đề tài TB-HTL

Dùng làm baseline chỉ-dùng-đích mạnh nhất ở nhiều mức k trong G0-2, và là một trong các mô hình của thí nghiệm 2×2 (KB1 v2).

Không có chuyển giao xuyên nguồn. TabPFN v2 huấn luyện và dự đoán trong cùng một bảng; tri thức nó mang theo đến từ dữ liệu tổng hợp lúc tiền huấn luyện, không phải từ miền nguồn của người dùng. Khác TB-HTL ở bốn điểm: nguồn tri thức là dữ liệu tổng hợp sinh từ prior thay vì miền nguồn thật; không dùng miền nguồn; không cần huấn luyện lại; giới hạn khoảng 10.000 mẫu.

TabPFN v2 là đối thủ khó nhất mà TB-HTL phải vượt. Nó cho thấy một phần đáng kể lợi ích mà người ta tưởng đến từ chuyển giao thực ra có thể đạt được chỉ bằng một mô hình nền tảng tốt, không cần miền nguồn nào. Kết quả Friedman của nhóm xác nhận: TabPFN v2 hạng 5,829 trong khi baseline chuyển giao tốt nhất là Daumé+LR chỉ hạng 6,366.

Điều này làm kết luận PIVOT chặt hơn chứ không yếu đi. `g0_decision.py` ghi rõ: nếu là PIVOT thì TabPFN không thể đổi thành GO, nó chỉ làm baseline mạnh hơn. Đây là lập luận quan trọng khi giải thích PIVOT: không phải chuyển giao vô dụng, mà là các baseline chỉ dùng đích đã quá mạnh ở mức k mà đề tài khảo sát.

Cần toàn văn để điền mục 3, ưu tiên metric, giao thức chia, cách sinh dữ liệu tiền huấn luyện, và khả năng rò rỉ qua phân phối tiên nghiệm. Bản arXiv của TabPFN v1 (<https://arxiv.org/abs/2207.01848>) không thay thế được vì v1 và v2 khác nhau đáng kể.
