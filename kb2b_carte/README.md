# KB2b – Tái hiện CARTE trên 3 bộ dữ liệu rượu (Hình 4–5 của báo cáo)

| File | Nội dung |
|---|---|
| `code_thucnghiem_carte.py`, `Code_ThucNghiem_CARTE.ipynb` | Mã của nhóm chạy CARTE (num_train 32, 64; seed 1–2) |
| `ket_qua/ket_qua_cua_toi.csv` | 12 lượt chạy của nhóm (R², thời gian) |
| `ket_qua/bang_so_sanh.csv` | Trung bình nhóm ↔ công bố theo bộ và num_train |
| `ket_qua/carte_cong_bo_3_bo_ruou.csv` | Kết quả công bố của CARTE (mọi mô hình), lọc 3 bộ rượu |
| `hinh/` | Hình 4–5 đúng như trong báo cáo |
| `ve_hinh_carte.py` | Vẽ lại hai hình: `python kb2b_carte/ve_hinh_carte.py` (ghi vào `hinh_tai_tao/`) |

Dữ liệu rượu lấy theo kho CARTE (`soda-inria/carte`, thư mục `data/single_tables`), nguyên gốc ở định dạng `.parquet`. Bản `.csv` dùng trong thực nghiệm của nhóm được lưu ở **thư mục gốc của kho**: `wine_pl.csv`, `wine_dot_com_prices.csv`, `wine_vivino_price.csv`. Hàm `wina_pl()` của thư viện `carte-ai` nạp tệp có tên `wine_pl`.
