# Việc cần làm đến giữa kỳ

Nguồn: Review-2026-10-24, Review-2026-10-25, **Review-2026-10-26 (mục 7.8)** và các việc còn hiệu lực của review 18/10, 22/10. Mỗi người tự cập nhật trạng thái dòng của mình khi xong, **ghi mã commit** (không ghi chung chung – review 26/10, mục 7.6), bằng tài khoản Git của mình. Trạng thái: ☐ chưa làm · ◐ đang làm · ☑ xong.

Cập nhật: 29/10/2026 (dòng của Minh; dòng của Thiên do Thiên tự cập nhật trạng thái).

**Đã bỏ:** K2-XN (QĐ1 review 26/10) – không commit mã K2-XN.

## Tăng Nhật Minh

| Hạn | Việc | Căn cứ | Sản phẩm | Trạng thái | Commit |
|---|---|---|---|---|---|
| 25/10 | Sửa đổi tiền đăng ký K2 (V1–V3, V6, V7) | R24 6.2 | `k2_run.py`, `k2_eval.py`, `prereg/`, `deviations.md` 9–14 | ☑ | `0c84285` |
| 25/10 | Kiểm tra mức sàn K2 | R24 6.3.1 | `results/k2_v2/*xao_tron_dich*` | ☑ | `a9727e0` |
| 25/10 | Đính chính thứ tự chạy | — | `deviations.md` 15 | ☑ | `2a1bbb0` |
| 25/10 | K2 sau sửa đổi (5 mức, 30 × 5), `k2_eval.py` sơ bộ, hai phép kiểm tái lập mới | R24 6.3.2–6.3.5 | `results/k2_v2/` | ☑ (sơ bộ, chưa có TabPFN v2) | `46b6770` |
| 25/10 | Sửa trình bày đặc tả TB-HTL (V9) | R25 V9 | `docs/tbhtl_v0_spec.md`, `deviations.md` 16 | ☑ | `46b6770` |
| 26/10 | Sửa `CLAUDE.md` (quy tắc 2; không chạy nhãn thật trước `commit_chot`; khai nhận có minh chứng) và bảng việc này | R26 7.7 | `CLAUDE.md`, `docs/viec_can_lam.md` | ☑ | `756ebb1` |
| 26/10 | Ghi chú ô suy biến (V5); sửa hai con số trong `00_contributions.md` (V6); ghi bỏ K2-XN; trả lời câu 8.1 | R26 V5, V6, 7.1, 8.1 | `deviations.md` 17–20 | ☑ | `756ebb1` |
| 26/10 | Rà soát tiền đăng ký độ nhạy C1 của Thiên | R26 7.8 | nhận xét trên commit A của Thiên | GVHD đã rà soát commit A thay (QĐ3 review 27/10); Minh rà soát commit B: ☑ đạt (28/10, ghi ở nhật ký 28/10) | `7d88d5f` (commit được rà soát) |
| 26–27/10 | Đường tham chiếu quy tắc ở K2-L0: commit mã + dòng `deviations.md` **trước**, rồi chạy 30 lần chia | R26 7.5 | `k2_quy_tac.py`, `results/k2_quy_tac/` | ☑ | mã `756ebb1`; kết quả `46dac1d` |
| 27/10 | Cổng 0 với `--tie neutral` (6 chiều) | R25 QĐ5 | `results/g0_tie_neutral/` | ☑ PIVOT không đổi 6 chiều | `46dac1d` |
| 28/10 | Báo cáo Word cập nhật theo R26 7.2 và R25 7.6 (Bảng 0 phản hồi review 18/10, 22/10, 24/10, 25/10, 26/10; trình tự chạy K2; bảng K2 sơ bộ; L0 so với quy tắc và mức trần KB1; hạn chế C1 và khái niệm chung; trích dẫn pháp lý; đặc tả TB-HTL). **Phần nhận định do Minh tự viết** | R26 7.2 | Báo cáo 28/10 | ☐ | |
| 28/10 | Xác nhận dòng của mình trong bảng phân công | R26 7.6 | `docs/phan_cong.md` | ☑ | commit xác nhận 28/10 |
| 28/10 | Khai báo công cụ AI (phần của Minh) | R27 7.2 mục 8 | `docs/khai_bao_cong_cu.md` | ☑ | commit khai báo 28/10 |
| 29–30/10 | CORAL ở L0: commit A (mã, `deviations.md` mục 24) → `--check`, mức sàn → commit B → chạy chính | R26 QĐ5 | `k2_coral.py`, `results/k2_coral/`, `results/k2_v2/*CORAL*` | ◐ commit A 29/10 | |
| 31/10–04/11 | Kết luận K2 (GO theo Holm, H5) khi có TabPFN v2; RQ6; CORAL | R26 7.8 | `k2_ket_luan.csv` chính thức | ☐ | |
| 05–08/11 | Cùng Thiên: slide giữa kỳ, dàn ý bài báo (sinh viên tự viết) | R26 7.8 | slide, dàn ý | ☐ | |

## Phạm Xuân Thiên

| Hạn | Việc | Căn cứ | Sản phẩm | Trạng thái | Commit |
|---|---|---|---|---|---|
| 25/10 | EDA đủ bốn miền; phân phối sau C1; đối chiếu A5.5a–b | R24 6.5, R25 V5 | `eda/` | ☑ | `d197041` |
| 25/10 | Dọn thư mục gốc; đính chính giải trình, nhật ký tuần | R25 V8, V3 | `git rm`, `docs/` | ☑ | `10207f4`, `54b28ce` |
| 26/10 | Khôi phục ô tiêu đề notebook EDA từ `b89d1d3` | R26 V7 | `eda/eda_bon_mien.ipynb` | ☑ | `8b0eeea` |
| 26/10 | Độ nhạy C1: `--check-zs` (ĐẠT) → commit A → mức sàn → commit B | R26 7.3 | `prereg/prereg_c1_do_nhay.yaml`, `c1_do_nhay*.py` | ☑ (commit A 26/10, commit B 27/10) | `1d99e32`, `7d88d5f` |
| 26/10 | Phiếu đọc luận văn UNICAMP 2025 ([44]) và dòng Bảng 1 | R25 7.3, R26 7.4 | `docs/phieu_doc/` | ☑ (28/10, chậm một ngày) | commit nhật ký ngày 28/10 của Thiên; mã bổ sung ở commit kế tiếp |
| 27/10 | Độ nhạy C1 chạy chính; `c1_do_nhay_eval.py` | R26 7.3 | `results/c1_do_nhay/` | ☑ (27/10) | `41dc832` |
| 27/10 | TrAdaBoost: `--check-zs` 3 thiết lập → commit A → mức sàn → commit B (gói mã review 25/10) | R25 7.3, R26 7.4 | `prereg/prereg_trada.yaml`, `tradaboost.py`, `trada_*.py` | ☑ (làm ngày 28/10) | `62f85fe` (A), `ac3193c` (B) |
| 28/10 | TrAdaBoost chạy chính; đoạn tổng quan về luận văn và đoạn kết quả C1 (Thiên tự viết) | R26 7.3, 7.4 | `results/trada/`, đoạn văn | ◐ lần chạy chính xong 28/10; đoạn văn chưa làm (đoạn tổng quan dời sang 04/11 theo R27 QĐ5) | commit nhật ký ngày 28/10 của Thiên |
| 28/10 | Khai báo công cụ AI (phần Thiên); xác nhận bảng phân công; phiếu đọc còn lại; Plan.xlsx; đề xuất 2–3 hội nghị | R25, R26 7.6 | `docs/` | ◐ khai báo, xác nhận phân công: xong 28/10; phiếu đọc còn lại dời 04/11, Plan.xlsx và đề xuất hội nghị dời 30/10 (R27 QĐ5) | commit nhật ký ngày 28/10 của Thiên |
| 30/10 | TabPFN v2 cho K2 (5 mức) trên Colab, ghi `git rev-parse HEAD` + `git status --porcelain` cạnh kết quả | R26 V7 | `results/k2_v2/*TabPFN*` | ☐ | |
| 30/10 | Phần bổ sung Cổng 0 (LightGBM, AdaBoost, XGBoost k nhỏ, PRESEL, Brier, ECE, F1, G-Mean; xáo trộn nhãn B→A) | R22 6.4, R25 QĐ5 | `results/g0_*` | ☐ | |
| 04/11 | `trada_eval.py`; bảng đối chiếu với luận văn | R26 7.4 | bảng | ☐ | |
| 05–08/11 | Cùng Minh: slide giữa kỳ, dàn ý bài báo | R26 7.8 | slide, dàn ý | ☐ | |

## Cả nhóm

| Hạn | Việc | Trạng thái |
|---|---|---|
| hằng ngày | Mỗi người 1 dòng `docs/nhat_ky_ngay.md` trước 22:00 (dòng đầu sau mỗi review ghi “đã đọc review ngày …”); email ≤ 5 dòng do sinh viên tự viết, luân phiên người gửi | ◐ |
| 28/10, 22:00 | Bảng phân công thống nhất, mỗi người một commit xác nhận dòng của mình (R26 7.6) | ☐ |
| giữa kỳ (09–15/11) | Mỗi người tự trình bày phần mã mình commit (Minh: `k2_run.py`, `k2_eval.py`, TB-HTL v0, `k2_quy_tac.py`, CORAL; Thiên: EDA, `c1_do_nhay.py`, TrAdaBoost, bổ sung Cổng 0, TabPFN v2) | ☐ |

**Không làm trước giữa kỳ:** CARTE, DSN, K1 tập lồng nhau, Babushkin nhãn theo mốc cố định, DANN, L2-SP, SHAP, phân tích độ nhạy khái niệm chung (V6 review 25/10), mô phỏng tỷ lệ dương giả của phép kiểm định.
