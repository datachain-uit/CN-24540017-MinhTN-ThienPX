### 4.5 Phần bổ sung Cổng 0 (mô tả, không kiểm định)

Phần này thêm LightGBM, AdaBoost, XGB_SMALLK (k ≤ 50) và PRESEL cho bốn đích, tính Brier, ECE, F1, G-Mean cho các phương pháp cũ từ dự đoán thô, và kiểm tra mức sàn B→A. Mã `g0_bo_sung.py`, tiền đăng ký `prereg/prereg_g0_bo_sung.yaml`, commit A `f3ae09e`, commit B `0a92a58`, kết quả `1b26af6`.

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
| D | 50 | LR 0,569 | LightGBM 0,564 | 0,559 | −0,010 |

Ở 0/12 ô, phương pháp mới cao hơn baseline mạnh nhất đã dùng, nên kết luận PIVOT của Cổng 0 không đổi. PRESEL thấp hơn baseline mạnh nhất chọn sau ở cả 12 ô, trung bình 0,019. Trên 720 ô, PRESEL chọn RF 29,2 %, CAT 24,4 %, LR 24,0 %, XGB 9,9 %, AdaBoost 8,2 %, LightGBM 4,3 %. Danh sách ứng viên của PRESEL không có TabPFN v2 và STACK.

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

Ô suy biến (`deviations.md` mục 40): LightGBM dự đoán hằng số ở mọi lần chia với k = 10, 20 của cả bốn đích (8 ô); XGB và STK_XGB ở k = 10 tại 5 cặp đích (10 ô); PRESEL ở 1 lần (đích D, k = 20, chọn LightGBM). Với tham số mặc định, LightGBM cần ít nhất 20 mẫu ở mỗi lá nên không tách được nút khi k ≤ 20. Các ô này không báo F1, G-Mean.

Mức sàn B→A với nhãn đích xáo trộn: PR-AUC trung bình 0,171–0,186 ở 17 phương pháp, tỷ lệ dương 0,160, không có dấu hiệu rò rỉ nhãn (`results/g0_bo_sung/results_muc_san_BA.csv`, `deviations.md` mục 29).

Kiểm tra đường ống: đích A, D 420/420, đích C 42/42 trùng Cổng 0; đích B lệch 2,25e-7 ở một giá trị trên máy Thiên, vượt ngưỡng 1e-9. Theo quyết định 2 review 31/10 phép kiểm được coi là đạt theo lần chạy của GVHD; nguyên nhân nêu ở `deviations.md` mục 42, 43.
