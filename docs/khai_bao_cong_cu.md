# Khai báo sử dụng công cụ AI

Theo V5 và quyết định 4 của Review-2026-10-24 (mục 6.6), hạn 28/10/2026. Mẫu theo Phụ lục B6.

**Nguyên tắc từ 24/10/2026**

- Giữ nguyên lịch sử Git, không xoá các dòng đã commit, kể cả các dòng hướng dẫn trong notebook có nhắc tới trợ lý AI.
- Commit nào có phần do công cụ sinh ra thì ghi rõ trong thông điệp commit (dòng `Co-Authored-By:` hoặc câu “mã/văn bản do … sinh, … kiểm tra”).
- Mỗi thành viên tự giải thích được mã và kết quả mình commit. Ở buổi giữa kỳ: Minh trình bày `k2_run.py`, TB-HTL v0 và `k2_eval.py`; Thiên trình bày notebook EDA, phần bổ sung Cổng 0 và TabPFN v2 cho K2.
- Thực hiện theo quy định hiện hành của Trường/Khoa về dùng công cụ AI trong khóa luận (nhóm cần tra cứu và ghi số văn bản vào đây nếu có). Khi viết bài báo: theo quy định của hội nghị đã chọn.

## 1. Tăng Nhật Minh

Minh dùng công cụ AI cho **hai việc**: (1) sinh mã — thí nghiệm Cổng 0, các cặp miền, KB1 v2, K2 (gồm TB-HTL v0), đường tham chiếu quy tắc ở K2-L0, phân tích độ nhạy quy tắc hoà của Cổng 0, mã thống kê (MDE, Friedman, Holm), kho tái lập, mã sinh báo cáo Word và các notebook Colab; (2) viết và chỉnh văn bản — tài liệu nội bộ của kho (tiền đăng ký, đặc tả TB-HTL v0, nhật ký sai lệch, tệp quy ước, bảng việc, bảng phân công, bản khai báo này) và báo cáo tiến độ. Chi tiết theo file và commit ở bảng dưới.

**Thay đổi từ ngày 26/10/2026** (review 26/10, mục 7.2 và 7.8; review 27/10, mục 7.2): phần nhận định trong báo cáo tiến độ, cột vướng mắc và việc tiếp trong nhật ký ngày, email gửi GVHD, luận văn và slide do Minh tự viết; công cụ AI chỉ chỉnh câu chữ, đối chiếu số liệu với file kết quả và lập bảng số liệu (kèm đường dẫn file, mã commit). Báo cáo tiến độ đến ngày 25/10, kể cả phần nhận định, có phần do công cụ soạn (dòng cuối của bảng).

Công cụ: **Claude (Anthropic)**, dùng qua ứng dụng Claude; phiên bản mô hình thay đổi theo phiên làm việc (các phiên ngày 24/10–28/10/2026: Claude Opus 5.5). Thời gian sử dụng: từ ngày 20/09/2026 đến nay.

| Công cụ, phiên bản | Dùng cho | File, commit | Người kiểm tra | Cách kiểm tra |
|---|---|---|---|---|
| Claude | **Sinh mã** thí nghiệm: Cổng 0, cặp miền mới, tổng hợp; mã thống kê (CI hiệu chỉnh Nadeau–Bengio, Holm, MDE, Friedman) và bảng tổng hợp kết quả | `hr_data.py`, `splits.py`, `g0_23.py`, `g0_decision.py`, `pairs.py`, `kb1_pair*.py`, `g0_pair.py`, `pairs_synthesis.py`, `mde_cong0.py`, `friedman_chieu.py` — `d03cd28`, `79a0a4c` | Minh | Chạy lại toàn bộ; `kiem_tra_tai_lap.py` (19/19 mục đạt); GVHD chạy lại độc lập ở review 22/10, 24/10 |
| Claude | **Sinh mã** KB1 v2 và truy vết bảng KB1 cũ | `kb1_v2.py`, `kb1_v2_summary.py`, `kb1_tai_dung.py`, `so_sanh_kb1.py` — `d03cd28` | Minh | Chạy lại trên Colab bằng tài khoản của nhóm: 760/760 kết quả khớp, lệch ≤ 1e-4 |
| Claude | **Sinh mã** K2: danh sách khái niệm, file chia, mã chạy, mã phân tích, TB-HTL v0 | `k2_khai_niem.py`, `splits_k2.py`, `k2_run.py`, `k2_eval.py` — `79a0a4c`, `3112a8f`; sửa đổi 24/10 (dựa trên bản vá của GVHD) — `0c84285`; tóm tắt kiểm tra mức sàn `k2_muc_san.py` — `a9727e0`; script lấy số liệu cho nhật ký `tools/so_lieu_ngay.py` — `46b6770` | Minh | Mã băm file tiền đăng ký sinh lại trùng; mức L2 ở lần rút 0 trùng Cổng 0; kiểm tra mức sàn với nhãn xáo trộn |
| Claude | **Sinh mã** lần chạy thăm dò TB-HTL dạng MLP (không dùng cho kết luận) | `tbhtl_thamdo_nn.py`, `tbhtl_thamdo_eval.py` — `79a0a4c` | Minh | `deviations.md` mục 3, 14 |
| Claude | **Sinh mã** kho tái lập và mã sinh báo cáo Word; notebook Colab và script tạo notebook | `TAI_LAP.md`, `tai_lap_bang.sh`, `kiem_tra_tai_lap.py`, `chay_lai_tu_dau.sh`, `bao_cao/`, `notebooks/` — `d03cd28`, `f65e85a`, `3112a8f` | Minh | Sinh lại báo cáo, so từng ô bảng (`kiem_tra_tai_lap.py`). Các dòng “gửi file … cho Claude/trợ lý” trong notebook là hướng dẫn quy trình lúc đó: Minh chạy notebook trên Colab rồi gửi file kết quả cho trợ lý để tổng hợp vào báo cáo |
| Claude | **Sinh mã** đường tham chiếu quy tắc một biến ở K2-L0 (QĐ1 review 26/10) | `k2_quy_tac.py` — `756ebb1`; kết quả `results/k2_quy_tac/` — `46dac1d` | Minh | Thử R = 10 trùng KB1 (0,287; 0,189); GVHD chạy lại độc lập được 0,284 và 0,189 (review 27/10) |
| Claude | **Sinh mã** phân tích độ nhạy Cổng 0 với quy tắc hoà trung tính (QĐ5 review 25/10) | `g0_tie_neutral_eval.py`, `results/g0_tie_neutral/` — `46dac1d` | Minh | `g0_tie_neutral_eval.py --check` sinh lại `g0_kiem_dinh_GO.csv` đã công bố của 3 cặp: 48/48 dòng mỗi cặp, lệch ≤ 1,1e-16; GVHD chạy độc lập, kết luận khớp (review 27/10) |
| Claude | **Viết và chỉnh văn bản** tài liệu nội bộ: tiền đăng ký, đặc tả TB-HTL v0, nhật ký sai lệch, tệp quy ước cho trợ lý AI, bảng việc, bảng phân công, bản khai báo này, phản hồi review | `00_contributions.md`, `prereg/prereg_k2.yaml`, `docs/tbhtl_v0_spec.md`, `deviations.md` (mục 1–20, 22), `CLAUDE.md`, `docs/viec_can_lam.md`, `docs/phan_cong.md`, `docs/khai_bao_cong_cu.md`, `README.md` — `79a0a4c`, `d2f1ef5`, `0c84285`, `2a1bbb0`, `46b6770`, `756ebb1`, `46dac1d` | Minh | Minh đọc lại, đối chiếu với review và Git, chịu trách nhiệm nội dung; các quyết định thiết kế theo review của GVHD |
| Claude | **Viết và chỉnh văn bản** báo cáo tiến độ và nhật ký ngày | Báo cáo Word đến 25/10 (`bao_cao/build.js`): công cụ soạn cả phần trình bày và nhận định. Từ 26/10: công cụ lập bảng số liệu và chỉnh câu chữ, Minh tự viết nhận định. Nhật ký ngày (`dbd3072`, `f1e39aa`, `a4c6825`, `7824905`): công cụ soạn cột “Đã làm”, “Kết quả” từ Git và file kết quả; Minh viết cột vướng mắc, việc tiếp. Email: Minh viết, có lúc tham khảo gợi ý ý chính của công cụ | Minh | Minh đối chiếu từng số với file kết quả và mã commit trước khi gửi |
| Claude (mã KB2); không dùng (LaTeX) | Tái hiện Levin et al. (KB2), bản nháp LaTeX 11/10 | `kb2_levin/`, `paper/tbhtl.tex` — `f65e85a` | Minh | Chạy `kb2_levin/` trên Colab, so với bài báo; bản nháp LaTeX Minh tự viết

**Phần Minh tự làm:** chạy các thí nghiệm trên Colab và trên máy; quyết định thiết kế theo các review của GVHD; kiểm tra kết quả bằng `kiem_tra_tai_lap.py`; phân công và rà soát công việc trong nhóm (rà soát commit B độ nhạy C1 của Thiên, `7d88d5f`); viết nhận định trong báo cáo từ 26/10, cột vướng mắc và việc tiếp trong nhật ký, email gửi GVHD; commit và chịu trách nhiệm về nội dung.

Minh xác nhận phần 1 ngày 28/10/2026.

## 2. Phạm Xuân Thiên

Thiên dùng công cụ AI cho **ba việc**: (1) sinh mã — tái hiện CARTE, notebook EDA bốn miền; (2) chạy các bước kiểm tra và điền tiền đăng ký cho hai phân tích dùng mã tham khảo của GVHD (độ nhạy C1, TrAdaBoost), trong đó mã của GVHD giữ nguyên, không sửa; (3) tra cứu tài liệu, lấy toàn văn, soạn và chỉnh văn bản — phiếu đọc, Bảng 1 mở rộng, bản giải trình, nhật ký, báo cáo ngày. Chi tiết theo file và commit ở bảng dưới.

Công cụ: **Claude (Anthropic)**, dùng qua Claude Code trong VS Code; phiên bản mô hình thay đổi theo phiên làm việc (các phiên ngày 24/10–28/10/2026: Claude Opus 5.5). Các commit từ 25/10 có phần do công cụ sinh ra đều ghi dòng `Co-Authored-By:`.

| Công cụ, phiên bản | Dùng cho | File, commit | Người kiểm tra | Cách kiểm tra |
|---|---|---|---|---|
| Công cụ AI | **Sinh mã** tái hiện CARTE trên 3 bộ dữ liệu rượu (KB2b) | `kb2b_carte/` — `f65e85a` | Thiên | Chạy lại, đối chiếu với kết quả công bố của bài báo theo từng seed (`kb2b_carte/ket_qua/bang_so_sanh.csv`) |
| Claude | **Sinh mã** notebook EDA bốn miền, gồm mục 6b (khái niệm của K2 sau C1) và 6c (đối chiếu Bảng A5.5a–b) | `eda/` — `b89d1d3`, `8823d07`, `d197041`, `8b0eeea` | Thiên | Số dòng, tỷ lệ dương khớp Bảng 12 báo cáo 22/10; AUC đơn biến tính lại khớp Bảng A5.5a–b 13/13; phát hiện ±5,2 của C1 được GVHD kiểm tra lại và xác nhận (review 26/10) |
| Claude | **Chạy kiểm tra và điền tiền đăng ký** độ nhạy C1 trên mã tham khảo của GVHD (không sửa mã) | `prereg/prereg_c1_do_nhay.yaml`, `results/c1_do_nhay/`, `deviations.md` mục 21 — `1d99e32`, `7d88d5f`, `41dc832` | Thiên | `--check-zs` trùng Cổng 0 60/60; mức sàn trùng số GVHD; GVHD so mã trùng từng byte với mã tham khảo (review 27/10) |
| Claude | **Chạy kiểm tra và điền tiền đăng ký** TrAdaBoost trên mã tham khảo của GVHD (không sửa mã) | `prereg/prereg_trada.yaml`, `results/trada/`, `deviations.md` mục 23 — `62f85fe`, `ac3193c`, commit nhật ký ngày 28/10 | Thiên | `--check-zs` trùng Cổng 0 và K2 ở 3 thiết lập (60/60 mỗi thiết lập); mức sàn trong khoảng GVHD đã chạy |
| Claude | **Tra cứu tài liệu, lấy toàn văn, soạn** phiếu đọc và Bảng 1 mở rộng | `docs/phieu_doc/` — `b89d1d3`, `6c056db` | Thiên | Đối chiếu từng ô với toàn văn hoặc tóm tắt chính thức; ô chưa có nguồn ghi rõ lý do, không suy đoán |
| Claude | **Soạn và chỉnh văn bản** bản giải trình, nhật ký tuần, nhật ký ngày, bảng việc, bảng phân công, bản khai báo này; báo cáo ngày gửi GVHD (file Word, không đưa lên kho) | `docs/giai_trinh_phan_viec_ThienPX.md`, `docs/nhat_ky_tuan.md`, `docs/nhat_ky_ngay.md`, `docs/viec_can_lam.md`, `docs/phan_cong.md`, `docs/khai_bao_cong_cu.md` — `54b28ce`, `d197041`, `8b0eeea`, `41dc832`, commit nhật ký ngày 28/10 | Thiên | Thiên đọc lại, đối chiếu với Git và file kết quả trước khi commit và gửi |

**Lưu ý về bản giải trình ngày 24/10:** bản đó do công cụ soạn và đã ghi nhầm phần việc của Minh là của Thiên; Thiên đính chính ngày 25/10 (`54b28ce`) và chịu trách nhiệm về lỗi này.

**Phần Thiên tự làm:** chạy notebook và các lệnh trên máy; commit và push bằng tài khoản `CauBe9x`; đọc review, quyết định thứ tự việc; chịu trách nhiệm về nội dung. Theo review 26/10 và 27/10, phần nhận định trong báo cáo 28/10 (mục 6–7) và đoạn tổng quan về luận văn UNICAMP do Thiên tự viết.

Thiên xác nhận phần 2 ngày 28/10/2026.
