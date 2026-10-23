#!/usr/bin/env bash
# Tính lại MỌI bảng và hình của báo cáo từ kết quả thô (results/*/results_*.csv), không huấn luyện lại.
# Khoảng 1–2 phút trên CPU. Bảng ánh xạ A5.5a–b cần thêm dữ liệu gốc trong data/ (xem data/README.md).
# Dùng: bash tai_lap_bang.sh   rồi   python kiem_tra_tai_lap.py
set -euo pipefail
cd "$(dirname "$0")"
L=results/tai_lap_log.txt; : > "$L"
run() { echo ">> $*" | tee -a "$L"; "$@" >> "$L" 2>&1; }

# Bảng 4, Hình 3, A5.1 (KB1 v2 cặp AB: 4 họ mô hình CPU + TabPFN v2)
run python kb1_v2_summary.py results/kb1_v2/results_kb1v2_99d14779.csv
run python kb1_pair_summary.py --pair AB results/kb1_v2/results_kb1v2_99d14779.csv results/kb1_AB/results_kb1_AB_cf3e982a_TabPFN.csv --out results/kb1_AB/tong_hop
# A5.1: đối chiếu lần chạy của nhóm trên Colab (18/10) với bản báo cáo
run python so_sanh_kb1.py results/kb1_v2/results_kb1v2_99d14779.csv results/kb1_v2_colab_nhom/results_kb1v2_99d14779.csv
# Bảng A5.4a–c, Hình 6–7 (Cổng 0 cặp AB)
run python g0_decision.py results/g0_23
# Bảng A5.5c–e (2×2 cặp AC, AD)
run python kb1_pair_summary.py --pair AC results/kb1_AC/results_kb1_AC_40a7ef2e_cpu.csv results/kb1_AC/results_kb1_AC_40a7ef2e_TabPFN.csv --out results/kb1_AC/tong_hop
run python kb1_pair_summary.py --pair AD results/kb1_AD/results_kb1_AD_4c085b4a_cpu.csv results/kb1_AD/results_kb1_AD_4c085b4a_TabPFN.csv --out results/kb1_AD/tong_hop
# Bảng A5.5f–g, Hình 8–9 (Cổng 0 cặp AC, AD; phân tích phụ AC “cùng chiều”)
run python g0_decision.py results/g0_AC AC
run python g0_decision.py results/g0_AD AD
run python g0_decision.py results/g0_AC_consistent AC
# Bảng A5.5h–i, Hình 10 (tổng hợp ba cặp; Friedman 41 khối = độ nhạy)
# Tổng hợp chính ở mức chiều (review 22/10, N3) và bảng MDE (N1); bản 41 khối là phân tích độ nhạy
run python friedman_chieu.py --out results/tong_hop_cap
run python mde_cong0.py --out results/tong_hop_cap
run python pairs_synthesis.py --out results/tong_hop_cap
# Thăm dò TB-HTL dạng MLP 23/10 (deviations.md mục 3), chiều B→A (so với baseline Cổng 0; không đổi kết luận Cổng 0)
run python tbhtl_thamdo_eval.py results/g0_23 A

# Chuỗi ô trong báo cáo Word (bao_cao/*.json)
run python bao_cao/make_kb1_json.py
run python bao_cao/make_g0_json.py
if ls data/WA_Fn-UseC_-HR-Employee-Attrition.csv data/HR_comma_sep.csv data/turnover.csv >/dev/null 2>&1; then
  run python bao_cao/make_pairs_json.py
else
  echo "!! Bỏ qua bao_cao/make_pairs_json.py (A5.5a–i): chưa có dữ liệu gốc trong data/" | tee -a "$L"
fi
echo "Xong. Nhật ký: $L"
