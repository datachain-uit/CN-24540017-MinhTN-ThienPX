# results/k2_v2 — K2 sau sửa đổi 24/10/2026 (lần chạy chính)

- Mã và thiết kế: commit `0c84285` (`k2_run.py` sha256 423c03af…); `prereg_k2.yaml` bản ở `a9727e0` (chỉ điền mã commit, kết quả mức sàn). Xem `deviations.md` mục 9–15.
- Kiểm tra mức sàn (nhãn đích xáo trộn): `*_9114f8ed_xao_tron_dich.*`, tóm tắt `k2_muc_san.txt` — đạt.
- Lần chạy chính: cấu hình `cdf6d7ca`; đích A; nguồn B, C; mức L0, L1, L1_noAge, L1_core, L2; k ∈ {10, 20, 50, 100}; 30 lần chia × 5 lần rút; 6 đợt × 5 lần chia (`--reps`), một tiến trình, `OMP_NUM_THREADS=2`; bắt đầu 24/10 21:27, xong 25/10 sáng (giờ máy chạy, UTC+7). Nhật ký: `k2_rep*.log`.
- Phân tích: `python k2_eval.py results/k2_v2` → `k2_ket_luan.csv`, `k2_kiem_dinh.csv`, `k2_h5.csv`, `k2_hoa.csv`, `k2_duong_cong.csv`, `k2_tbhtl_lambda.csv`, `k2_presel_chon.csv`, `k2_hinh_duong_cong.png`, `k2_eval.log`.
- **Sơ bộ – chưa có TabPFN v2** (Thiên chạy trên Colab, hạn 30/10, ghi vào thư mục này). Kết luận GO và H5 chỉ chính thức sau khi có TabPFN v2 (quyết định 3, review 24/10).
