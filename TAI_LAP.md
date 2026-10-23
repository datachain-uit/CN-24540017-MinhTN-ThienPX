# Bảng và hình trong báo cáo ↔ lệnh tái lập

`bash tai_lap_bang.sh` chạy tất cả các lệnh ở cột 2 (từ kết quả thô, không huấn luyện lại); `python kiem_tra_tai_lap.py` so với số trong báo cáo.
Cột 4 là lệnh huấn luyện lại (cần dữ liệu gốc; xem `chay_lai_tu_dau.sh`).

| Báo cáo | Lệnh tính bảng/hình | Kết quả thô | Huấn luyện lại |
|---|---|---|---|
| Bảng 4, Hình 3, bảng kiểm định A5.1 | `python kb1_pair_summary.py --pair AB results/kb1_v2/results_kb1v2_99d14779.csv results/kb1_AB/results_kb1_AB_cf3e982a_TabPFN.csv --out results/kb1_AB/tong_hop` → `bao_cao/make_kb1_json.py` | `results/kb1_v2/`, `results/kb1_AB/` | `kb1_v2.py` (CPU, ~15 phút); TabPFN v2: `notebooks/chay_TabPFN_v2_R1_R3_Colab.ipynb` |
| Bảng A5.1b (độ nhạy) | như trên (`*_ma_hoa.csv`) | như trên | như trên |
| Đối chiếu Colab (A5.1, 760/760 khớp) | `python so_sanh_kb1.py results/kb1_v2/results_kb1v2_99d14779.csv results/kb1_v2_colab_nhom/results_kb1v2_99d14779.csv` | `results/kb1_v2_colab_nhom/` | `notebooks/chay_KB1_v2_tren_Colab.ipynb` |
| Bảng A5.1c (truy vết KB1 cũ) | – (bảng in trực tiếp) | `results/kb1_tai_dung.csv` | `kb1_tai_dung.py` (~5 phút) |
| Bảng A5.4a–c, Hình 6–7 (Cổng 0 AB) | `python g0_decision.py results/g0_23` → `bao_cao/make_g0_json.py` | `results/g0_23/` | `g0_23.py` (3 lượt CPU) + `g0_pair.py --suffix rankrf`; TabPFN v2: `notebooks/chay_TabPFN_v2_Cong0_Colab.ipynb` |
| Bảng A5.5a–b (ánh xạ, chiều tác động) | `bao_cao/make_pairs_json.py` (cần dữ liệu gốc) | – | – |
| Bảng A5.5c–e (2×2 cặp AC, AD) | `python kb1_pair_summary.py --pair AC|AD ...` → `bao_cao/make_pairs_json.py` | `results/kb1_AC/`, `results/kb1_AD/` | `kb1_pair.py --pair AC|AD` |
| Bảng A5.5f, Hình 8–9 (Cổng 0 AC, AD) | `python g0_decision.py results/g0_AC AC`, `... results/g0_AD AD` | `results/g0_AC/`, `results/g0_AD/` | `g0_pair.py --pair AC|AD` |
| Bảng A5.5g (AC, tập “cùng chiều”) | `python g0_decision.py results/g0_AC_consistent AC` | `results/g0_AC_consistent/` | `g0_pair.py --pair AC --cset consistent` |
| Bảng A5.5h–i, Hình 10 (tổng hợp, Friedman – Nemenyi) | `python pairs_synthesis.py --out results/tong_hop_cap` | các thư mục trên | – |
| Thăm dò TB-HTL dạng MLP 23/10, B→A (deviations.md mục 3) | `python tbhtl_thamdo_eval.py results/g0_23 A` | `results/g0_23/results_g0_AB_76199ef8_tbhtl.csv` | `tbhtl_thamdo_nn.py --pair AB --targets A` (~10 phút CPU) |
| Friedman mức chiều (4 chiều chính; 6 chiều đối chiếu) – review 22/10 N3 | `python friedman_chieu.py` | `results/*/g0_bang_duong_cong.csv` | – |
| Bảng MDE Cổng 0 – review 22/10 N1 | `python mde_cong0.py` | `results/g0_23`, `g0_AC`, `g0_AD` | – |
| Danh sách khái niệm L0, L1 của K2 (tiền đăng ký) | `python k2_khai_niem.py --ibm data/WA_Fn-UseC_-HR-Employee-Attrition.csv` | `prereg/k2_khai_niem.json` | – |
| File chia K2 (R = 30, M = 5; lần rút 0 trùng Cổng 0) | `python splits_k2.py --ibm data/WA_Fn-UseC_-HR-Employee-Attrition.csv` | `prereg/splits_A_R30_M5.json` (sha256 trong `prereg/prereg_k2.yaml`) | – |
| K2 – miền đích nghèo đặc trưng (RQ5, RQ6; tiền đăng ký `prereg/prereg_k2.yaml`, commit `d2f1ef5`) | `python k2_eval.py results/k2` | `results/k2/results_k2_*.csv` | `k2_run.py` (CPU, ~3,5 giờ trên 2 nhân; chia lần chia bằng `--reps`) và `notebooks/chay_TabPFN_v2_K2_Colab.ipynb` (TabPFN v2) |
| Hình 4–5 (CARTE, KB2b) | `python kb2b_carte/ve_hinh_carte.py` | `kb2b_carte/ket_qua/` | `kb2b_carte/code_thucnghiem_carte.py` |
| Toàn bộ báo cáo Word | `bash bao_cao/build_bao_cao.sh` | `bao_cao/*_trong_bao_cao.json` + hình trong `results/` | – |

Ghi chú về mã băm: `g0_23` có hai mã (`6f2142bf` cho lượt CPU đầu, `44c64e04` sau khi thêm CatBoost, stacking, TabPFN v2 vào cấu hình). Các phương pháp chung giữa hai lượt cho kết quả trùng; `g0_decision.py` gộp mọi file trong thư mục.
TabPFN v2 không chạy ở mức “toàn bộ” khi tập huấn luyện vượt 10.000 dòng (đích Job Change); ở 2×2 tập huấn luyện được rút phân tầng còn 10.000 dòng.
