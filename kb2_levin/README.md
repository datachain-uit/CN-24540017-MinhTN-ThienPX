# Tái hiện thực nghiệm "Transfer Learning with Deep Tabular Models" (ICLR 2023)

Bộ code tái hiện thực nghiệm chính (Mục 4, Hình 2) của bài báo, dựa trên bài báo và repo
chính thức github.com/LevinRoman/tabular-transfer-learning (mô hình chuyển thể từ RTDL).

## Cài đặt
    pip install -r requirements.txt

## Dữ liệu
- **MetaMIMIC**: tạo từ MIMIC-IV theo https://github.com/ModelOriented/metaMIMIC (cần quyền PhysioNet).
  File CSV cần có `subject_id`, 171 cột số, `gender`, 12 cột `*_diagnosed`.
- **Yeast / Emotions**: file `.arff` từ Mulan; nhãn là các cột cuối (`--n-labels 14` / `6`).
- Chưa có dữ liệu thật: `python make_synthetic_data.py` sinh CSV giả để chạy thử (không dùng để báo cáo).

## Chạy
    # 1) Chạy thử nhanh
    python make_synthetic_data.py --n 3000 --out data/synthetic_metamimic.csv
    python run_experiments.py --data-path data/synthetic_metamimic.csv --quick --targets 0 --models mlp catboost

    # 2) Đầy đủ như bài báo: 12 nhiệm vụ x {4,10,20,100,200} x 10 seeds, Optuna 50 trials (cần GPU)
    python run_experiments.py --dataset metamimic --data-path data/MetaMIMIC.csv

    # Rẻ hơn: dùng siêu tham số mặc định (Bảng 2-5)
    python run_experiments.py --dataset metamimic --data-path data/MetaMIMIC.csv --no-tune

    # Phụ lục D.9: nhiều dữ liệu downstream hơn
    python run_experiments.py --data-path data/MetaMIMIC.csv --sizes 400 1000 2000 --models ft_transformer mlp catboost

    # Phụ lục D.6: Yeast / Emotions
    python run_experiments.py --dataset yeast --data-path data/yeast.arff --models ft_transformer mlp catboost

    # 3) Tổng hợp: hạng (Wilcoxon rank-sum một phía, p=0.05), heatmap Hình 2/7/9
    python analyze_results.py --results outputs/results_metamimic.csv --exclude tab_transformer

Kết quả được ghi dần vào `outputs/results_<dataset>.csv`; siêu tham số và trọng số pre-train
được cache trong `outputs/cache/`, nên chạy lại cùng lệnh sẽ tiếp tục từ chỗ dừng.
Thiếu bộ nhớ GPU/RAM với FT-Transformer: thêm `--batch-size 64`.

## Ánh xạ tới bài báo
| Bài báo | Code |
|---|---|
| Chia 65/15/20, cố định qua seed (B.4) | `data.TransferBenchmark` (random_state=1 như repo) |
| 11 nhãn upstream / 1 nhãn downstream, 12 phân chia | `TransferBenchmark.upstream / downstream` |
| Rút 4/10/20/100/200 mẫu | `data.stratified_sample` (phân tầng, >=1 mẫu/lớp, seed 0 như repo) |
| Quantile fit trên upstream; điền mean; NaN phân loại -> hạng mục mới (B.5) | `TransferBenchmark.__init__` |
| FT-Transformer, ResNet, MLP, TabTransformer | `models.py` |
| LH / MLP / LH-E2E / MLP-E2E, head MLP 2x200 (3.3) | `training.finetune`, `models.replace_head` |
| Pre-train AdamW, 500 epoch, patience 30, batch 256; fine-tune lr 5e-5, scratch 1e-4 (B.6.1) | `training.pretrain / fit` |
| Chọn epoch: 30 (4,10), 60 (20), 20% val + early stop (E2E, 100/200), 100/200 epoch (frozen MLP/LH) (B.6.3) | `training.downstream_schedule` |
| CatBoost/XGBoost + Stacking (B.6.4) | `gbdt.py` |
| Optuna 50 trials, không gian Bảng 2-7; tune transfer trên toàn upstream, FS/GBDT trên 1 nhãn upstream cùng cỡ mẫu (3.4, C) | `tuning.py` |
| Hạng có ý nghĩa thống kê, ROC-AUC (B.6.5) | `analyze_results.py` |

## Giả định / khác biệt cần biết
- Lấy từ repo (bài báo không nêu): head lr = 1e-3; feature extractor đóng băng 10 epoch đầu khi fine-tune E2E.
- Mặc định pre-train 1 lần (seed 0) rồi fine-tune với 10 seeds; dùng `--pretrain-per-seed` để pre-train theo từng seed.
- Kịch bản frozen giữ feature extractor ở eval mode (dropout/BatchNorm cố định).
- Hạng của mô hình = 1 + số mô hình tốt hơn có ý nghĩa (rank-sum một phía, p<0.05) trên AUC các seed.
- Mô hình stacking upstream dùng tham số mặc định; GBDT có stacking dùng lại siêu tham số đã tune của GBDT thường.
- TabTransformer là bản cài đặt gọn (repo gốc không có); bài báo chỉ báo cáo nó ở Phụ lục D.1.
- Chưa gồm: tiền huấn luyện tự giám sát (MLM, contrastive – Mục 5) và phương pháp pseudo-feature (Mục 6).
