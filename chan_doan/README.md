# chan_doan/ — script chẩn đoán quy tắc hoà của GVHD (gửi kèm Review-2026-10-24)

Giữ nguyên như GVHD gửi để tái lập Bảng A4a–c của review. Chạy từ thư mục gốc của kho Git, có dữ liệu trong `data/`.

    python chan_doan/lam_ties.py 30 2                       # Bảng A4b: tỷ lệ hoà khi chọn λ_s (chỉ dùng nhãn của k mẫu huấn luyện)
    python chan_doan/w_ties2.py --pair AB --data A=data/WA_Fn-UseC_-HR-Employee-Attrition.csv \
        B=data/aug_train.csv --targets A --only RANKAVG_RF --out results/tam_w_ties
    python chan_doan/w_ties2_eval.py w_ties_log2.json        # Bảng A4a, A4c: ba quy tắc chọn w ở Cổng 0, B→A

Ghi chú: `lam_ties.py` dùng `k2_run.tbhtl_fit`, `tbhtl_logit` (không đổi sau sửa đổi 24/10).
