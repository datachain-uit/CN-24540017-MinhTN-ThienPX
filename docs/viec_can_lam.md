# Việc cần làm đến giữa kỳ

Nguồn: Review-2026-10-24, Review-2026-10-25, **Review-2026-10-26 (mục 7.8)** và các việc còn hiệu lực của review 18/10, 22/10. Mỗi người tự cập nhật trạng thái dòng của mình khi xong, **ghi mã commit** (không ghi chung chung – review 26/10, mục 7.6), bằng tài khoản Git của mình. Trạng thái: ☐ chưa làm · ◐ đang làm · ☑ xong.

Cập nhật: 10/11/2026 (dòng của Minh và dòng của Thiên). Dòng của Thiên do Thiên tự cập nhật trạng thái.

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
| 28/10 | Xác nhận dòng của mình trong bảng phân công | R26 7.6 | `docs/phan_cong.md` | ☑ | `8a71fe5` |
| 28/10 | Khai báo công cụ AI (phần của Minh) | R27 7.2 mục 8 | `docs/khai_bao_cong_cu.md` | ☑ | `c98e19a`, `72d112d` |
| 29–30/10 | CORAL ở L0: commit A (mã, `deviations.md` mục 24) → `--check`, mức sàn → commit B → chạy chính | R26 QĐ5, R30 QĐ2 | `k2_coral.py`, `results/k2_coral/`, `results/k2_v2/*CORAL*` | ☑ chạy chính 30/10 sau commit B (mục 26); diễn giải theo V2, QĐ3 review 30/10 | `f4b242e` (A), `423dd08` (B), `b61ccb3` (kết quả) |
| 30/10 | Kết luận K2 chính thức (có TabPFN v2 `fc904d8` và CORAL): `k2_eval.py`, đối chiếu Phụ lục A4 review 30/10 | R30 QĐ2 | `results/k2_v2/k2_ket_luan.csv`, `doi_chieu_review3010_A4.txt` | ☑ PIVOT 10/10, khớp A4 | `b61ccb3` |
| 31/10–01/11 | `.gitattributes` (Phụ lục B2), ghi môi trường chạy vào cấu hình (B3, B2 R31) | R30 V3, R31 V1 | `.gitattributes`, `tools/moi_truong.py` | ☑ `.gitattributes` có từ `a3722ff`; môi trường: deviations 31; sửa `trang_thai_git()` theo R01/11 (deviations 33); pip freeze: `results/moi_truong/pip_freeze_minh.txt` | `5afb0e2`, `d51db74` |
| 01/11 | Script tách khoảng cách hiệp phương sai: commit mã → chạy → commit kết quả | R31 V3, 7.2 | `k2_tach_hiep_phuong_sai.py`, `results/k2_coral/tach_hiep_phuong_sai*.csv` | ☑ kết quả chạy sau `d51db74` (deviations 34) | `5afb0e2`, `d51db74`, `650a8b9` |
| 01/11 | SHA-256, kích thước, mã tệp Drive, cấu hình sinh `du_doan_tho_gate0.zip` vào `data/README.md` (trả lời câu 8.1 R31) | R31 V3, B3 | `data/README.md` | ☑ hai bản trên Drive, mã băm, nguồn gốc (deviations 35); danh mục mã băm từng file, tên tệp (deviations 36, R01/11 chiều V1) | `ee8eef3`, `d2326a1` |
| 31/10–01/11 | Mục 1, 4, 5 của bản đủ | R30 7.2, R31 7.2 | bản đủ 06/11 | ☑ nhận định mục 1, 4, 5, 8 (Minh tự viết); sửa theo review 07/11 trong bản đủ 09/11 | `f98beaa` |
| 02/11 | Phép thử 7 trường hợp; `tools/kiem_ma_commit.py`; sửa 4 ô mã commit; đính chính “7 trường hợp” (deviations 36) | R01/11 chiều V2, QĐ5 | `tools/thu_moi_truong.py`, `tools/kiem_ma_commit.py` | ☑ | `d2326a1` |
| 02/11–06/11 | Mục 0, 8, 10 của bản đủ (cùng Thiên); bảng mức tái lập; rà toàn văn theo bảng kiểm 7.3 R01/11; nộp bản đủ (GVHD dời hạn từ 04/11 sang thứ Sáu 06/11) | R30 7.2, R31 7.2–7.3, R01/11 7.3 | Bản đủ 06/11 | ◐ đã ghép mục 0–10; bảng mức tái lập còn 2 ô; chưa rà chéo | |
| 04/11 | Cập nhật cột kết luận RQ1–RQ6 trong `00_contributions.md` theo kết quả chính thức, mỗi ô ghi file và mã commit | R01/11 QĐ4, V3 | `00_contributions.md` | ☑ (03/11; RQ1–RQ7, deviations 39) | `36f0599` |
| 03/11 | Sửa `data/README.md` theo V2: ngày nhận tệp (tối 30/10), tệp đầu vào chính xác (`a0866dbb…`), hai file kb1v2 khác mã băm; đính chính deviations 35 | R02/11 V2, QĐ3, câu 8 | `data/README.md`, `deviations.md` 39 | ☑ | `36f0599` |
| 03–04/11 | Tỷ lệ dòng ở hai đầu cho mục 5 bản đủ (mã Phụ lục B4 R01/11 chiều): commit mã → chạy trên kho sạch → commit kết quả | R01/11 chiều V3, B4 | `k2_ty_le_bien.py`, `results/k2_coral/ty_le_bien_sau_C1.csv` | ☑ chạy trên kho sạch ở `58be588` (`git_dirty` false) | mã `36f0599`; kết quả `aec973b` |
| 03/11 | Thay Plan.xlsx trên Drive bằng bản của Thiên (Quản lý phiên bản → Tải phiên bản mới lên, giữ mã tệp) | R02/11 7.2 | Plan.xlsx trên Drive | ◐ đã nhận bản của Thiên (05/11, ghi ở `f3305af`); thay trên Drive sau khi Minh kiểm tra | |
| 05–08/11 | Dàn ý tiếng Anh trên Overleaf trước 08:00 ngày 05/11 (thay `docs/dan_y_bai_bao.md`, R02/11 7.4); sửa bài theo góp ý; script sinh T4 và tải nguồn Overleaf vào `paper/taimma2027/` (22:00 ngày 08/11); tài khoản CMT | R31 7.6–7.7, R01/11 QĐ5, 7.4–7.5, R02/11 QĐ4, 7.4 | dàn ý, LaTeX | ◐ khung dàn ý (mẫu IEEE của nhóm, dự án Conf) đưa lên Overleaf tối 04/11; gạch đầu dòng tiếng Anh sinh viên tự viết; hỏi GVHD giữ mẫu IEEE hay đổi sang LNCS | |
| 08–09/11 | Phụ lục B3 R07/11: `sd_hieu_bat_cap.py` → chạy trên kho sạch → commit kết quả; viết lại câu giải thích MDE ở mục 4 và mục 8 ý 1 | R07/11 V1, 7.2 (2) | `sd_hieu_bat_cap.py`, `results/tong_hop_cap/sd_hieu_bat_cap.csv`, bản đủ 09/11 | ☑ trễ một ngày (mất mạng 08/11) | `c48414d`, `f98beaa` |
| 09/11 | Mục 8 ý 4 (Δ lớn nhất ở k = 20); H_B và tiêu chí (3) theo hiệu của hiệu, H_A theo hiệu bắt cặp ở Hướng 1 | R07/11 V1, V3, 7.2 (3) | bản đủ 09/11 (Word) | ☑ số đối chiếu `k2_kiem_dinh.csv` | `b61ccb3` |
| 08/11 | Bảng vừa khổ LNCS (T4 tách T4_k2, T4_rq6; T2 xuống dòng); văn bản bài ra khỏi kho công khai (gỡ `paper/taimma2027/overleaf/`) | R07/11 QĐ1, QĐ4, 7.3, Phụ lục B1 | `paper/taimma2027/` | ☑ trễ một ngày (09/11) | `c48414d` |
| 08/11 | Chuyển Overleaf sang LNCS (mẫu chính thức của Springer), gộp dàn ý của Thiên; bản sao mốc lên Drive | R07/11 QĐ1, 7.3 | Overleaf (dự án Conf), Drive | ◐ khung LNCS đã soạn, chưa đưa lên Overleaf (mất mạng 08/11) | |
| 10/11 | Bản đủ cập nhật cho báo cáo giữa kỳ: ghép phần Thiên tự viết lại (4.5, mục 8, Hướng 2), cập nhật bảng phản hồi mục 0 | R07/11 QĐ3, 7.2; lịch báo cáo giữa kỳ 09–15/11 | bản đủ 10/11 (Word, gửi GVHD) | ☑ ghép từ kho đến `a9bbc15`; rà chéo theo bảng kiểm chưa xong | `a9bbc15` |
| 05–08/11 | Cùng Thiên: slide giữa kỳ, dàn ý bài báo (sinh viên tự viết) | R26 7.8 | slide, dàn ý | ☐ | |

## Phạm Xuân Thiên

| Hạn | Việc | Căn cứ | Sản phẩm | Trạng thái | Commit |
|---|---|---|---|---|---|
| 25/10 | EDA đủ bốn miền; phân phối sau C1; đối chiếu A5.5a–b | R24 6.5, R25 V5 | `eda/` | ☑ | `d197041` |
| 25/10 | Dọn thư mục gốc; đính chính giải trình, nhật ký tuần | R25 V8, V3 | `git rm`, `docs/` | ☑ | `10207f4`, `54b28ce` |
| 26/10 | Khôi phục ô tiêu đề notebook EDA từ `b89d1d3` | R26 V7 | `eda/eda_bon_mien.ipynb` | ☑ | `8b0eeea` |
| 26/10 | Độ nhạy C1: `--check-zs` (ĐẠT) → commit A → mức sàn → commit B | R26 7.3 | `prereg/prereg_c1_do_nhay.yaml`, `c1_do_nhay*.py` | ☑ (commit A 26/10, commit B 27/10) | `1d99e32`, `7d88d5f` |
| 26/10 | Phiếu đọc luận văn UNICAMP 2025 ([44]) và dòng Bảng 1 | R25 7.3, R26 7.4 | `docs/phieu_doc/` | ☑ (28/10, chậm một ngày) | `faa0f6b` |
| 27/10 | Độ nhạy C1 chạy chính; `c1_do_nhay_eval.py` | R26 7.3 | `results/c1_do_nhay/` | ☑ (27/10) | `41dc832` |
| 27/10 | TrAdaBoost: `--check-zs` 3 thiết lập → commit A → mức sàn → commit B (gói mã review 25/10) | R25 7.3, R26 7.4 | `prereg/prereg_trada.yaml`, `tradaboost.py`, `trada_*.py` | ☑ (làm ngày 28/10) | `62f85fe` (A), `ac3193c` (B) |
| 28/10 | TrAdaBoost chạy chính; đoạn tổng quan về luận văn và đoạn kết quả C1 (Thiên tự viết) | R26 7.3, 7.4 | `results/trada/`, đoạn văn | ◐ lần chạy chính xong 28/10; đoạn văn chưa làm (đoạn tổng quan dời sang 04/11 theo R27 QĐ5) | `faa0f6b` |
| 28/10 | Khai báo công cụ AI (phần Thiên); xác nhận bảng phân công; phiếu đọc còn lại; Plan.xlsx; đề xuất 2–3 hội nghị | R25, R26 7.6 | `docs/` | ◐ khai báo, xác nhận phân công: xong 28/10 (`e1fb5f8`); đề xuất hội nghị: 30/10 (`9fdaca8`), thêm hội nghị đã chọn 03/11 (`51aca7e`), đính chính ngày ECML PKDD 2027 06/11; Plan.xlsx: sửa theo Phụ lục C review 18/10, giữ TabICL (quyết định 3 review 01/11), bản sửa gửi Minh thay trên Drive; cột liên hệ với đề tài 28/28 dòng, cột hạn chế 11/28 dòng, 17 dòng ghi chưa đọc toàn văn (`Reviews/Plan_sua_0511.xlsx`, 05/11, gửi Minh); phiếu đọc còn lại dời 04/11 | `e1fb5f8`, `9fdaca8` |
| 30/10 | TabPFN v2 cho K2 (5 mức) trên Colab, ghi `git rev-parse HEAD` + `git status --porcelain` cạnh kết quả | R26 V7 | `results/k2_v2/*TabPFN*` | ☑ (29/10) | `fc904d8` |
| 30/10 | Phần bổ sung Cổng 0 (LightGBM, AdaBoost, XGBoost k nhỏ, PRESEL, Brier, ECE, F1, G-Mean; xáo trộn nhãn B→A) | R22 6.4, R25 QĐ5 | `results/g0_bo_sung/` | ☑ (31/10, trễ một ngày; trong hạn 01/11 của review 30/10) | `f3ae09e` (A), `0a92a58` (B); `1b26af6` (kết quả) |
| 04/11 | `trada_eval.py`; bảng đối chiếu với luận văn | R26 7.4 | bảng | ☑ `trada_eval.py` chạy lại với TabPFN v2 cho K2-L0 (31/10); bảng đối chiếu trong mục 7 bản đủ (05/11, hạn 04/11) | `d8c535a`, `03677a2` |
| 03/11 | Mục 2 và mục 6 của bản đủ (tự viết phần nhận định); 07/11 sửa câu đầu mục 6 theo V3 R01/11 chiều | R02/11 7.2 (1) | `docs/ban_du/` | ☑ (03/11, 21:30) | `9c804eb`, `c43d5fb` |
| 03/11 | Mục 3 của bản đủ; Plan.xlsx: cột hạn chế, liên hệ với đề tài | R02/11 7.2 (2) | `docs/ban_du/`, Plan.xlsx | ◐ mục 3 xong 03/11; Plan.xlsx 05/11: liên hệ 28/28 dòng, hạn chế 11/28 dòng | `9c804eb`, `f3305af` |
| 03/11 | Mục deviations mới cho ý (a): kiểm tra đích B theo lần chạy của GVHD | R02/11 7.2 (3) | `deviations.md` mục 38 | ☑ (03/11); đính chính nguyên nhân ở mục 42, 43 | `51aca7e`, `33b16ef`, `8d0cda7` |
| 03/11 | `de_xuat_hoi_nghi.md`: hội nghị đã chọn TAIMMA 2027; đính chính ngày ECML PKDD 2027 | R02/11 7.2 (4) | `docs/de_xuat_hoi_nghi.md` | ☑ TAIMMA 03/11; ECML 06/11 (nhận review 31/10 ngày 06/11) | `51aca7e`, `8d0cda7` |
| 03/11 | Bảng việc, nhật ký 03/11; `tools/kiem_ma_commit.py` trước khi đẩy | R02/11 7.2 (5) | `docs/` | ☑ (03/11) | `51aca7e` |
| 09/11 | Ô D, k = 50 Bảng 4.3 thành AdaBoost 0,564; tự viết lại câu chữ tiểu mục 4.5 | R07/11 7.2 (1) | `docs/ban_du/ban_du_muc_4_bo_sung_Thien.md` | ☑ ô D 09/11; câu chữ 10/11, trễ một ngày | `44fa1f4`, `fb4860b` |
| 09/11 | Tự viết lại Hướng 2 (Bảng 10.2) và phần sự kiện mục 8 | R07/11 7.2 (4) | `docs/ban_du/ban_du_muc_8_10_Thien.md` | ☑ (10/11, trễ một ngày) | `fb4860b` |
| 09/11 | Sửa câu mục 2 và mục 6; thêm dòng kiểm tra đích B vào Bảng 8.1 và mục 8 | R07/11 7.2 (5) | `docs/ban_du/` | ☑ (09/11; câu mục 8 viết lại 10/11) | `44fa1f4` |
| 09/11 | Rà chéo bản đủ theo bảng kiểm, mỗi dòng ghi tên người rà; khai báo công cụ đến ngày nộp | R07/11 7.2 (6) | bản đủ, `docs/khai_bao_cong_cu.md` | ◐ khai báo cập nhật 10/11; rà chéo chưa làm | |
| 05–08/11 | Cùng Minh: slide giữa kỳ, dàn ý bài báo | R26 7.8 | slide, dàn ý | ◐ `paper/taimma2027/scripts/bang_bai_bao.py` sinh T1, T5, T6 phần C1, PRESEL (07/11); dàn ý phần của Thiên điền vào `paper/taimma2027/overleaf/main.tex` (08/11), chưa đồng bộ lên Overleaf; slide chưa làm | `c17796a`, `4835e9e` |

## Cả nhóm

| Hạn | Việc | Trạng thái |
|---|---|---|
| hằng ngày | Mỗi người 1 dòng `docs/nhat_ky_ngay.md` trước 22:00 (dòng đầu sau mỗi review ghi “đã đọc review ngày …”); email ≤ 5 dòng do sinh viên tự viết, luân phiên người gửi | ◐ |
| 28/10, 22:00 | Bảng phân công thống nhất, mỗi người một commit xác nhận dòng của mình (R26 7.6) | ☑ `8a71fe5` (Minh), `e1fb5f8` (Thiên) |
| giữa kỳ (09–15/11) | Mỗi người tự trình bày phần mã mình commit (Minh: `k2_run.py`, `k2_eval.py`, TB-HTL v0, `k2_quy_tac.py`, CORAL; Thiên: EDA, `c1_do_nhay.py`, TrAdaBoost, bổ sung Cổng 0, TabPFN v2) | ☐ |

**Không làm trước giữa kỳ:** CARTE, DSN, K1 tập lồng nhau, Babushkin nhãn theo mốc cố định, DANN, L2-SP, SHAP, phân tích độ nhạy khái niệm chung (V6 review 25/10), mô phỏng tỷ lệ dương giả của phép kiểm định.
