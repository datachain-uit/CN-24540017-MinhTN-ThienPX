# Phân công và minh chứng đóng góp

Trả lời câu 2 mục 7 (review 18/10) và N5 (review 22/10). Mỗi dòng ghi người làm chính và commit chứa sản phẩm.
**Lưu ý về tác giả commit:** kho Git được lập ngày 22/10; hai commit đầu (`d03cd28`, `f65e85a`) do Minh đẩy lên và **gộp sản phẩm của cả hai thành viên** làm trước ngày đó, nên tác giả commit của hai commit này không phản ánh đúng người làm. Bảng dưới đây là căn cứ phân công; từ 23/10 mỗi người commit bằng tài khoản của mình (Minh: `NhatMinh998`, Thiên: `CauBe9x`).

Cập nhật: 24/10/2026. Mỗi thành viên tự xác nhận dòng của mình trước khi commit.

## Tăng Nhật Minh (24540017)

| Sản phẩm | Thư mục / file | Commit |
|---|---|---|
| KB1 v2 (2×2, 4 họ mô hình + TabPFN v2), truy vết bảng KB1 cũ (A5.1c), tái lập trên Colab | `kb1_v2.py`, `kb1_v2_summary.py`, `kb1_tai_dung.py`, `so_sanh_kb1.py`, `results/kb1_v2*`, `results/kb1_AB/` | `d03cd28` |
| Cổng 0 cặp IBM ↔ Job Change (G0-2, G0-3, G0-4), quyết định GO/PIVOT, chạy TabPFN v2 trên Colab | `hr_data.py`, `splits.py`, `g0_23.py`, `g0_decision.py`, `results/g0_23/` | `d03cd28` |
| Làm sạch HR 14.999 và Babushkin, ánh xạ khái niệm cặp A ↔ C, A ↔ D, 2×2 và Cổng 0 cho hai cặp mới, tổng hợp ba cặp | `pairs.py`, `kb1_pair.py`, `kb1_pair_summary.py`, `g0_pair.py`, `pairs_synthesis.py`, `results/kb1_AC`, `kb1_AD`, `g0_AC*`, `g0_AD`, `tong_hop_cap/` | `d03cd28` |
| Kho tái lập: lệnh tái lập từng bảng, kiểm tra tự động, sinh lại báo cáo Word | `TAI_LAP.md`, `tai_lap_bang.sh`, `kiem_tra_tai_lap.py`, `chay_lai_tu_dau.sh`, `bao_cao/` | `d03cd28`, `f65e85a` |
| Tái hiện Levin et al. (KB2) | `kb2_levin/` | `f65e85a` |
| Vẽ lại Hình 4–5 của CARTE từ kết quả của Thiên | `kb2b_carte/ve_hinh_carte.py` | `f65e85a` |
| Bản nháp LaTeX (11/10) | `paper/tbhtl.tex` | `f65e85a` |
| Theo review 22/10: bảng MDE, Friedman mức chiều, danh sách khái niệm K2, đặc tả TB-HTL v0, nhật ký sai lệch | `mde_cong0.py`, `friedman_chieu.py`, `k2_khai_niem.py`, `docs/tbhtl_v0_spec.md`, `deviations.md` | `79a0a4c` |
| Tiền đăng ký K2 | `00_contributions.md`, `prereg/` | `79a0a4c`, `d2f1ef5` |
| K2: mã chạy, phân tích, notebook TabPFN v2; kết quả K2 | `k2_run.py`, `k2_eval.py`, `notebooks/chay_TabPFN_v2_K2_Colab.ipynb`, `results/k2/` | `3112a8f`; kết quả lần chạy theo bản chốt 23/10: `48bf86a` |
| Thăm dò TB-HTL dạng mạng nơ-ron (không dùng cho kết luận) | `tbhtl_thamdo_nn.py`, `tbhtl_thamdo_eval.py` | `79a0a4c` |
| Sửa đổi K2 theo review 24/10 (áp bản vá của GVHD; F1, G-Mean; ghi tỷ lệ hoà; đổi tên lần chạy MLP; tài liệu tiền đăng ký; notebook TabPFN v2 cho 5 mức; kiểm tra tái lập bổ sung) | `k2_run.py`, `k2_eval.py`, `g0_pair.py`, `kiem_tra_tai_lap.py`, `prereg/prereg_k2.yaml`, `deviations.md` mục 9–14, `docs/khai_bao_cong_cu.md` | `0c84285` |
| Kiểm tra mức sàn K2 (nhãn đích xáo trộn) | `k2_muc_san.py`, `results/k2_v2/*xao_tron_dich*`, `results/k2_v2/k2_muc_san.*` | commit sau `0c84285` |

## Phạm Xuân Thiên (24540028)

| Sản phẩm | Thư mục / file | Commit |
|---|---|---|
| Tái hiện CARTE trên 3 bộ dữ liệu rượu (KB2b), đối chiếu với kết quả công bố theo từng seed (GVHD ghi nhận ở review 18/10) | `kb2b_carte/code_thucnghiem_carte.py`, `kb2b_carte/Code_ThucNghiem_CARTE.ipynb`, `kb2b_carte/ket_qua/` | `f65e85a` (do Minh đẩy lên trong commit gộp) |
| EDA bốn miền | `eda/eda_bon_mien.ipynb`, `eda/bang*.csv`, `eda/hinh/` | `b89d1d3`, `8823d07` |
| Phiếu đọc 10 bài ưu tiên; cột phương pháp luận của Bảng 1 | `docs/phieu_doc/`, `docs/phieu_doc/bang1_phuong_phap_luan.csv` | `b89d1d3` (đang hoàn thiện, hạn 28/10) |
| Nhật ký tuần | `docs/nhat_ky_tuan.md` | `e689490`, `b89d1d3` |
| Việc theo review 24/10 (mục 6.5): EDA thêm miền D và khái niệm sau căn chỉnh C1 (25/10); 5 → 10 phiếu đọc (25/10, 28/10); TabPFN v2 cho K2 (30/10); CORAL ở L0, Cổng 0 với `--tie neutral` (04/11) | — | (chưa có) |
| Việc đến 28/10: mục 6.4 review 22/10 (LightGBM, AdaBoost, Brier, ECE, F1, G-Mean, baseline đích chọn trước, XGBoost k nhỏ, xáo trộn nhãn đích), Plan.xlsx (M9), đề xuất hội nghị | — | (chưa có) |

## Chưa xác định

| Sản phẩm | Thư mục | Ghi chú |
|---|---|---|
| Mã cũ của nhóm (notebook pipeline mô hình bảng sâu, script ghép dữ liệu) | `ma_cu_cua_nhom/` | Nhóm điền người làm |

## Công cụ hỗ trợ

Mã, phân tích thống kê và phần lớn văn bản báo cáo được xây dựng với sự hỗ trợ của trợ lý AI (Claude, Anthropic). Nhóm chạy mọi thí nghiệm, kiểm tra kết quả bằng `kiem_tra_tai_lap.py` và chịu trách nhiệm về nội dung. Khai báo chi tiết theo từng file và commit: `docs/khai_bao_cong_cu.md` (V5, review 24/10).
