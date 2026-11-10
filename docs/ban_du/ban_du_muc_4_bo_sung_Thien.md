### 4.5 Phần bổ sung Cổng 0 (mô tả, không kiểm định)

Phần này thêm bốn mô hình chỉ dùng dữ liệu đích là LightGBM, AdaBoost, XGB_SMALLK (k ≤ 50) và PRESEL, các chỉ số Brier, ECE, F1, G-Mean, và một phép kiểm tra mức sàn. Không mô hình nào là phương pháp chuyển giao: phần này chỉ làm mốc so sánh chặt hơn và bổ sung F1 để đối chiếu được với luận văn UNICAMP (mục 7). Mã `g0_bo_sung.py`, tiền đăng ký `prereg/prereg_g0_bo_sung.yaml`, commit A `f3ae09e`, commit B `0a92a58`, kết quả `1b26af6`.

**Hình 4.1.** Đường cong PR-AUC theo k. Dấu x là ô suy biến, đường chấm là tỷ lệ dương của tập test (`docs/ban_du/hinh_g0_bo_sung.png`, sinh bằng `docs/ban_du/ve_hinh_g0_bo_sung.py` từ `results/g0_bo_sung/`, `1b26af6`).

**Bảng 4.3.** Phương pháp mới so với baseline chỉ dùng đích mạnh nhất ở Cổng 0, k ≤ 50, PR-AUC trung bình 30 lần chia (`results/g0_bo_sung/results_moi_[A-D].csv`, `chi_so_tu_du_doan_tho.csv`, `1b26af6`). Mạnh nhất: cao nhất trong LR, RF, XGB, CAT, STACK, TabPFN v2, chọn sau khi xem kết quả test.

| Đích | k | Mạnh nhất (chọn sau) | Tốt nhất trong 4 phương pháp mới | PRESEL | PRESEL − mạnh nhất |
|---|---|---|---|---|---|
| A | 10 | RF 0,321 | PRESEL 0,301 | 0,301 | −0,020 |
| A | 20 | RF 0,341 | PRESEL 0,311 | 0,311 | −0,030 |
| A | 50 | RF 0,405 | PRESEL 0,382 | 0,382 | −0,023 |
| B | 10 | LR 0,346 | PRESEL 0,326 | 0,326 | −0,020 |
| B | 20 | LR 0,385 | PRESEL 0,358 | 0,358 | −0,028 |
| B | 50 | TabPFN v2 0,409 | XGB_SMALLK 0,401 | 0,397 | −0,012 |
| C | 10 | CAT 0,465 | PRESEL 0,445 | 0,445 | −0,020 |
| C | 20 | CAT 0,556 | PRESEL 0,552 | 0,552 | −0,004 |
| C | 50 | CAT 0,791 | PRESEL 0,741 | 0,741 | −0,050 |
| D | 10 | RF 0,536 | PRESEL 0,529 | 0,529 | −0,007 |
| D | 20 | RF 0,538 | PRESEL 0,535 | 0,535 | −0,004 |
| D | 50 | LR 0,569 | AdaBoost 0,564 | 0,559 | −0,010 |

So từng dòng của Bảng 4.3, không ô nào trong 12 ô có phương pháp mới vượt baseline mạnh nhất; ví dụ đích A, k = 10, PRESEL đạt 0,301 so với 0,321 của RF. Vì vậy kết luận PIVOT của Cổng 0 giữ nguyên.

PRESEL thấp hơn baseline mạnh nhất từ 0,004 đến 0,050. Baseline mạnh nhất được chọn sau khi đã nhìn kết quả trên tập test nên được lợi, tương tự xem đáp án rồi mới chọn bài; PRESEL phải chọn trước và chỉ dựa vào k mẫu, nên thấp hơn một chút là bình thường, không phải do mô hình kém.

**Bảng 4.4.** Chỉ số phụ ở k = 50, trung bình 30 lần chia, chỉ để mô tả (`chi_so_tu_du_doan_tho.csv`, `results_moi_[A-D].csv`, `1b26af6`). Điểm phương pháp cũ làm tròn 5 chữ số (`deviations.md` mục 37b).

| Đích | Phương pháp | PR-AUC | Brier | ECE | F1 | G-Mean |
|---|---|---|---|---|---|---|
| A | RF | 0,405 | 0,119 | 0,045 | 0,399 | 0,595 |
| A | PRESEL | 0,382 | 0,131 | 0,087 | 0,396 | 0,593 |
| B | TabPFN v2 | 0,409 | 0,175 | 0,041 | 0,426 | 0,584 |
| B | PRESEL | 0,397 | 0,202 | 0,142 | 0,409 | 0,570 |
| C | CAT | 0,791 | 0,076 | 0,063 | 0,699 | 0,804 |
| C | PRESEL | 0,741 | 0,086 | 0,080 | 0,680 | 0,791 |
| D | LR | 0,569 | 0,293 | 0,195 | 0,552 | 0,537 |
| D | PRESEL | 0,559 | 0,302 | 0,198 | 0,546 | 0,531 |

Với tham số mặc định, LightGBM cần ít nhất 20 mẫu ở mỗi lá, nên với 10–20 mẫu không chia được nhánh nào. Mọi người nhận cùng một điểm, AUC-ROC bằng 0,5; F1 ở các ô này chỉ phụ thuộc thứ tự dòng nên không có ý nghĩa, và được ghi là suy biến (`deviations.md` mục 40). Số ô suy biến: LightGBM k = 10, 20 ở bốn đích (8 ô); XGB và STK_XGB k = 10 ở năm cặp đích (10 ô); PRESEL một lần (đích D, k = 20).

Khi nhãn đích đã bị xáo trộn, mô hình không còn gì để học: PR-AUC ở mức sàn B→A là 0,171–0,186, sát tỷ lệ dương 0,160, tức bằng mức đoán ngẫu nhiên. Vậy đường ống không bị rò rỉ nhãn (`results/g0_bo_sung/results_muc_san_BA.csv`, `deviations.md` mục 29).
