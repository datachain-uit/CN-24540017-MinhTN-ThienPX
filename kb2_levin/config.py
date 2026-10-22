"""
config.py
Cấu hình thực nghiệm, bám theo bài báo "Transfer Learning with Deep Tabular Models"
(Levin et al., ICLR 2023) và repo chính thức github.com/LevinRoman/tabular-transfer-learning.
"""
from dataclasses import dataclass, field
from typing import List

# 12 nhiệm vụ chẩn đoán của MetaMIMIC (đúng tên cột trong repo gốc, mimic_tools.py)
MIMIC_TARGETS = [
    "diabetes_diagnosed", "hypertensive_diagnosed", "ischematic_diagnosed",
    "heart_diagnosed", "overweight_diagnosed", "anemia_diagnosed",
    "respiratory_diagnosed", "hypotension_diagnosed", "lipoid_diagnosed",
    "atrial_diagnosed", "purpura_diagnosed", "alcohol_diagnosed",
]

DEEP_MODELS = ["ft_transformer", "resnet", "mlp", "tab_transformer"]
GBDT_MODELS = ["catboost", "xgboost"]

# 4 kịch bản transfer (Mục 3.3) + baseline From Scratch
TRANSFER_SETUPS = ["LH", "MLP", "LH-E2E", "MLP-E2E"]   # LH = linear head, E2E = fine-tune toàn bộ

# Giá trị mặc định của các mô hình (cột "Default" trong Bảng 2-5, Phụ lục C)
DEFAULT_HPARAMS = {
    "ft_transformer": dict(n_layers=3, d_token=192, residual_dropout=0.0, attention_dropout=0.2,
                           ffn_dropout=0.1, d_ffn_factor=4 / 3, n_heads=8,
                           lr=1e-4, weight_decay=1e-5),
    "resnet": dict(n_layers=5, d_embedding=128, d=200, d_hidden_factor=3.0, hidden_dropout=0.2,
                   residual_dropout=0.2, lr=1e-4, weight_decay=0.0),
    "mlp": dict(d_embedding=128, d_layers=[300, 200, 300], dropout=0.2, lr=1e-4, weight_decay=1e-5),
    "tab_transformer": dict(n_heads=8, n_layers=6, d_embedding=32, attention_dropout=0.0,
                            ff_dropout=0.0, lr=1e-4, weight_decay=1e-5),
    "catboost": dict(),   # tham số mặc định của thư viện
    "xgboost": dict(),
}


@dataclass
class ExpConfig:
    # --- Chia dữ liệu (Phụ lục B.4; repo: random_state=1, 0.2 test rồi 0.1875 của phần còn lại = 15%)
    test_size: float = 0.20
    val_size_of_rest: float = 0.1875
    split_seed: int = 1
    downstream_sample_seed: int = 0          # repo gốc cố định seed=0 khi rút mẫu downstream
    resample_per_seed: bool = True           # O3 (đánh giá 07/10): rút lại n mẫu theo từng seed; False = như repo gốc
    sample_sizes: List[int] = field(default_factory=lambda: [4, 10, 20, 100, 200])

    # --- Seeds & tuning (Mục 3.4, Phụ lục B.4, C)
    seeds: List[int] = field(default_factory=lambda: list(range(10)))
    n_trials: int = 50
    tune: bool = True
    pretrain_per_seed: bool = False   # False: pre-train 1 lần (seed 0) rồi fine-tune với 10 seeds

    # --- Pre-training (Phụ lục B.6.1)
    pretrain_epochs: int = 500
    pretrain_patience: int = 30
    batch_size: int = 256

    # --- Fine-tuning / from scratch (Phụ lục B.6.1, B.6.3)
    finetune_lr: float = 5e-5          # lr cho feature extractor khi fine-tune
    head_lr: float = 1e-3              # lr của head (repo: hyp_for_transfer.yaml -> head_lr)
    head_warmup_epochs: int = 10       # repo: head_warmup_period (đóng băng FE 10 epoch đầu khi E2E)
    scratch_lr: float = 1e-4
    max_downstream_epochs: int = 200
    downstream_patience: int = 30
    downstream_val_frac: float = 0.20  # với 100/200 mẫu: tách 20% làm val để early stopping (E2E)
    mlp_head_dim: int = 200            # head MLP 2 lớp x 200 neuron (Mục 3.3)

    # --- Đánh giá (Phụ lục B.6.5)
    alpha: float = 0.05                # Wilcoxon rank-sum một phía


def quick_config() -> ExpConfig:
    """Cấu hình rút gọn để chạy thử nhanh (smoke test) – KHÔNG dùng để báo cáo kết quả."""
    return ExpConfig(sample_sizes=[4, 20, 100], seeds=[0, 1, 2], n_trials=2,
                     pretrain_epochs=15, pretrain_patience=5, max_downstream_epochs=40)
