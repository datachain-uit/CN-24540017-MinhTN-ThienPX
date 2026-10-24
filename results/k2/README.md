# results/k2 — K2 theo bản chốt tiền đăng ký 23/10/2026 (lần chạy thứ nhất)

- Mã: `k2_run.py` commit `3112a8f` (sha256 f8c79ff…); tiền đăng ký `d2f1ef5`; cấu hình `283c1350`.
- Phạm vi: đích A, nguồn B và C, mức L0, L1, L1_noAge, k ∈ {10, 20, 50, 100}, 30 lần chia × 5 lần rút, phương pháp CPU (chưa có TabPFN v2).
- Chạy 23–24/10/2026, commit `48bf86a` lúc 12:25 ngày 24/10, **trước khi nhận Review-2026-10-24**.
- Các file `k2_*.csv` và `k2_hinh_duong_cong.png` ở đây sinh bằng `k2_eval.py` của commit `48bf86a` (quy tắc GO cũ: CI chưa hiệu chỉnh không chứa 0). Theo quy tắc sau sửa đổi (Holm), chạy `python k2_eval.py <thư mục chép riêng>` để không ghi đè: mọi tổ hợp đều PIVOT.
- Giữ nguyên để đối chiếu; **lần chạy chính sau sửa đổi ở `results/k2_v2`**. Xem `deviations.md` mục 7–9.
