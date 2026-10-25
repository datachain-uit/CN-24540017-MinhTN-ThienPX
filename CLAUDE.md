# Quy ước làm việc cho trợ lý AI trong kho này

Kho mã của khóa luận *Ứng dụng học chuyển giao để dự đoán rủi ro nghỉ việc…* — Tăng Nhật Minh (24540017, `NhatMinh998`), Phạm Xuân Thiên (24540028, `CauBe9x`); GVHD ThS. Nguyễn Thị Anh Thư. Cả hai thành viên dùng file này: Claude Code đọc tự động; khi dùng Claude ở nơi khác, dán nội dung file này vào đầu cuộc trò chuyện.

## Quy tắc bắt buộc

1. **Không đổi thiết kế đã chốt.** K2 theo `prereg/prereg_k2.yaml` (bản chốt `d2f1ef5`, sửa đổi 24/10 `0c84285`). Không đổi lưới k, file chia, danh sách khái niệm, quy tắc GO, quy tắc hoà, tập phương pháp. Mọi thay đổi, kể cả chạy thăm dò, ghi vào `deviations.md` kèm lý do và mã commit, **trước** khi chạy.
2. **Không thêm tài liệu tham khảo hay baseline mới** trước giữa kỳ (QĐ7 review 22/10, QĐ5 review 24/10). Danh sách baseline theo Phụ lục D review 07/10. Ý tưởng mới ghi vào mục "Sau giữa kỳ" của `00_contributions.md`.
3. **Mỗi người commit bằng tài khoản của mình**, chỉ commit phần việc của mình. Không commit hộ, không sửa file của người kia khi chưa thống nhất (bảng phân công: `docs/phan_cong.md`, việc và hạn: `docs/viec_can_lam.md`).
4. **Khai báo AI**: commit có phần do công cụ sinh ra phải ghi trong thông điệp commit (ví dụ dòng `Co-Authored-By:`), và cập nhật `docs/khai_bao_cong_cu.md`. Không xoá hay viết lại lịch sử Git; không `git push --force`.
5. **Kho công khai**: không commit dữ liệu (`data/`, CSV ở thư mục gốc), file Word/Excel của review, token, email cá nhân. Dùng `git add <đường dẫn cụ thể>`, không `git add -A`.
6. **Thứ tự**: `git pull --no-rebase` trước khi làm; chạy thí nghiệm chỉ sau khi mã và tiền đăng ký đã commit; ghi đúng giờ và thứ tự trong `deviations.md`.
7. **Nhật ký ngày**: mỗi tối trước 22:00, mỗi người thêm một dòng vào `docs/nhat_ky_ngay.md` (không sửa dòng cũ) và commit.
8. Thành viên phải **tự giải thích được** mã và kết quả mình commit (kiểm tra ở buổi giữa kỳ). Trợ lý giải thích khi được hỏi, không chỉ đưa mã.

## Bản đồ kho

| Phần | File chính |
|---|---|
| Dữ liệu, loại trùng | `data/README.md` (SHA-256), `hr_data.py`, `pairs.py` |
| File chia | `splits.py` (Cổng 0), `splits_k2.py`, `prereg/splits_A_R30_M5.json` |
| Cổng 0, ba cặp miền | `g0_23.py`, `g0_pair.py` (`--tie first` mặc định), `g0_decision.py`, `pairs_synthesis.py` |
| K2 (RQ5, RQ6), TB-HTL v0 | `k2_run.py`, `k2_eval.py`, `k2_muc_san.py`, `docs/tbhtl_v0_spec.md`; kết quả `results/k2` (bản chốt 23/10), `results/k2_v2` (sau sửa đổi) |
| Thống kê | CI hiệu chỉnh Nadeau–Bengio (0,25), Holm, MDE: `k2_eval.py`, `mde_cong0.py`, `friedman_chieu.py` |
| Tái lập | `TAI_LAP.md`, `tai_lap_bang.sh`, `kiem_tra_tai_lap.py` (phải TẤT CẢ ĐẠT trước khi commit) |
| EDA, phiếu đọc (Thiên) | `eda/`, `docs/phieu_doc/` |
| Câu hỏi nghiên cứu, ngưỡng | `00_contributions.md` |

## Quy ước viết

Tiếng Việt, số thập phân dùng dấu phẩy trong văn bản; PR-AUC là chỉ số chính; nêu CI và MDE kèm mọi kết luận "không phát hiện"; không viết "bị bác bỏ" khi chỉ là PIVOT.
