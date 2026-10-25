# Việc cần làm đến giữa kỳ

Nguồn: Review-2026-10-24 (mục 6.2–6.7), các việc còn hiệu lực của review 18/10 và 22/10. Mỗi người tự cập nhật dòng của mình khi xong (ghi mã commit), bằng tài khoản Git của mình. Trạng thái: ☐ chưa làm · ◐ đang làm · ☑ xong.

Cập nhật: 25/10/2026 (Minh, các dòng của Minh; dòng của Thiên do Thiên tự cập nhật).

## Tăng Nhật Minh

| Hạn | Việc | Căn cứ | Sản phẩm | Trạng thái | Commit |
|---|---|---|---|---|---|
| 25/10 | Sửa đổi tiền đăng ký K2 (V1–V3, V6, V7) | R24 6.2 | `k2_run.py`, `k2_eval.py`, `prereg/`, `deviations.md` 9–14 | ☑ | `0c84285` |
| 25/10 | Kiểm tra mức sàn `--shuffle-target` | R24 6.3.1 | `results/k2_v2/*xao_tron_dich*` | ☑ | `a9727e0` |
| 25/10 | Đính chính thứ tự chạy | — | `deviations.md` 15 | ☑ | `2a1bbb0` |
| 25–27/10 | Chạy K2 sau sửa đổi (5 mức, 30 × 5) | R24 6.3.2 | `results/k2_v2/results_k2_*_cpu_*.csv` | ☑ (24/10 21:27 → 25/10) | commit kết quả K2 |
| 27/10 | Hai phép kiểm mới trong `kiem_tra_tai_lap.py` | R24 6.3.3 | mã băm tiền đăng ký; L2 lần rút 0 = Cổng 0 | ☑ (đạt trên kết quả thật: 14 phương pháp × 2 nguồn, lệch 0) | commit kết quả K2 |
| 28/10 | Chạy `k2_eval.py` – bảng K2 sơ bộ (“chưa có TabPFN v2”) | R24 6.3.5 | `results/k2_v2/k2_*.csv` | ☑ (sơ bộ) | commit kết quả K2 |
| 28/10 | Báo cáo Word cập nhật: Bảng 0 phản hồi review 18/10, 22/10, 24/10; B1.2; đổi tên Nội dung 2; Bảng 5 RQ1–RQ7; A ↔ D thăm dò; N7; tên RANKAVG-RF; mã commit | R22 6.6, R24 6.5 | Báo cáo 28/10 | ☐ | |
| 28/10 | Khai báo công cụ AI (phần Minh) | R24 6.6 | `docs/khai_bao_cong_cu.md` | ☑ | `0c84285` |
| 29/10–04/11 | Phân tích RQ5 (GO, H5), RQ6 (TB-HTL, ablation, λ_s theo k) | R24 6.5 | bảng, hình | ☐ | |
| sau 30/10 | Chạy lại `k2_eval.py` khi có TabPFN v2 → kết luận GO, H5 | R24 6.3.5 | `k2_ket_luan.csv` (chính thức) | ☐ | |
| 05–08/11 | Cùng Thiên: slide giữa kỳ, dàn ý bài báo (kịch bản A/B) | R24 6.4 | slide, dàn ý | ☐ | |

## Phạm Xuân Thiên

| Hạn | Việc | Căn cứ | Sản phẩm | Trạng thái | Commit |
|---|---|---|---|---|---|
| 25/10 | EDA bốn miền chạy lại được: thêm **miền D**; phân phối khái niệm chung của **L0, L1 theo miền sau căn chỉnh C1**; AUC đơn biến **đối chiếu Bảng A5.5a–b** | R24 6.5 | `eda/eda_bon_mien.ipynb` | ☑ (đủ A–D; mục 6b sau C1, mục 6c đối chiếu A5.5a–b) | commit EDA 25/10 |
| 25/10 | 5 phiếu đọc theo mẫu; điền dòng tương ứng của Bảng 1 | R24 6.5 | `docs/phieu_doc/`, `bang1_phuong_phap_luan.csv` | ◐ | |
| 25/10 | Viết lại giải trình cho commit `b89d1d3` (ghi đúng phần việc) | phân công 24/10 | `docs/nhat_ky_tuan.md` | ☑ | `54b28ce` |
| 25/10 | Dọn thư mục gốc (3 file trùng `kb2b_carte/`, dữ liệu wine, file Word) | phân công 24/10 | `git rm` | ☑ | `10207f4` |
| 25/10 | Điền dòng tuần 15–21/10 trong nhật ký tuần | R24 QĐ5 | `docs/nhat_ky_tuan.md` | ☑ | `54b28ce` |
| 28/10 | Bổ sung Cổng 0 cho bốn đích: LightGBM, AdaBoost, XGBoost k nhỏ, PRESEL, Brier, ECE, F1, G-Mean (dùng hàm trong `k2_run.py`); xáo trộn nhãn đích B→A | R22 6.4, R24 6.5 | `results/g0_*` | ☐ | |
| 28/10 | Đủ 10 phiếu đọc; sửa nguồn trong Plan.xlsx (M9); đề xuất 2–3 hội nghị | R24 6.5 | `docs/phieu_doc/`, đề xuất | ☐ | |
| 28/10 | Khai báo công cụ AI (phần Thiên) | R24 6.6 | `docs/khai_bao_cong_cu.md` | ☐ | |
| 30/10 | TabPFN v2 cho K2 trên Colab (5 mức) | R24 6.3.4 | `results/k2_v2/*TabPFN*` | ☐ | |
| 04/11 | CORAL ở L0; Cổng 0 với `--tie neutral` cho 6 chiều; bảng chỉ số hiệu chỉnh | R24 6.5 | `results/` | ☐ | |
| 05–08/11 | Cùng Minh: slide giữa kỳ, dàn ý bài báo | R24 6.4 | slide, dàn ý | ☐ | |

## Cả nhóm

| Hạn | Việc | Trạng thái |
|---|---|---|
| từ 25/10, hằng ngày | Mỗi người 1 dòng `docs/nhat_ky_ngay.md` trước 22:00; email ≤ 5 dòng kèm mã commit, luân phiên người gửi | ◐ (Minh bắt đầu 24/10, `dbd3072`) |
| 28/10 | Đề xuất hội nghị (QĐ6 review 22/10) | ☐ |
| giữa kỳ (09–15/11) | Mỗi người tự trình bày phần mã của mình (Minh: `k2_run.py`, TB-HTL v0, `k2_eval.py`; Thiên: EDA, bổ sung Cổng 0, TabPFN v2 K2) | ☐ |

**Không làm trước giữa kỳ:** CARTE, DSN, K1 tập lồng nhau, Babushkin nhãn theo mốc cố định, DANN, L2-SP, SHAP (QĐ2 review 24/10).
