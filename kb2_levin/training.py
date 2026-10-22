"""
training.py
Vòng lặp huấn luyện chung + 3 quy trình:
  pretrain()      : multi-label trên upstream (AdamW, tối đa 500 epoch, patience 30)
  finetune()      : 4 kịch bản LH / MLP / LH-E2E / MLP-E2E (Mục 3.3, Phụ lục B.6.3)
  train_scratch() : baseline From Scratch trên downstream
"""
import copy
import random

import numpy as np
import torch
import torch.nn as nn
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split

from config import ExpConfig
from data import TabularData
from models import build_model, freeze_feature_extractor, replace_head


def set_seed(seed: int):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)


def _tensors(d: TabularData, device):
    xn = torch.as_tensor(d.x_num, device=device)
    xc = None if d.x_cat is None else torch.as_tensor(d.x_cat, device=device)
    return xn, xc


@torch.no_grad()
def predict_logits(model, d: TabularData, device, bs: int = 256) -> np.ndarray:
    model.eval()
    xn, xc = _tensors(d, device)
    out = [model(xn[i:i + bs], None if xc is None else xc[i:i + bs]).float().cpu() for i in range(0, len(d), bs)]
    out = torch.cat(out).numpy()
    return out[:, 0] if (out.ndim == 2 and out.shape[1] == 1 and d.y.ndim == 1) else out


def auc(y: np.ndarray, scores: np.ndarray) -> float:
    """ROC-AUC; với đa nhãn lấy trung bình macro trên các nhãn có đủ 2 lớp."""
    if y.ndim == 1:
        return float(roc_auc_score(y, scores)) if len(np.unique(y)) > 1 else float("nan")
    vals = [roc_auc_score(y[:, j], scores[:, j]) for j in range(y.shape[1]) if len(np.unique(y[:, j])) > 1]
    return float(np.mean(vals)) if vals else float("nan")


def fit(model, train: TabularData, val: TabularData = None, *, epochs: int, lr: float, weight_decay: float,
        device, seed: int, batch_size: int = 256, patience: int = None, head_lr: float = None,
        head_warmup_epochs: int = 0):
    """Huấn luyện bằng AdamW + BCEWithLogits. Nếu có val: chọn epoch tốt nhất theo ROC-AUC
    và dừng sớm theo patience. Trả về (model, số epoch tốt nhất, điểm val tốt nhất)."""
    set_seed(seed)
    model.to(device)
    frozen = getattr(model, "_frozen", False)
    fe = [p for n, p in model.named_parameters() if not n.startswith("head.") and p.requires_grad]
    hd = [p for n, p in model.named_parameters() if n.startswith("head.") and p.requires_grad]
    groups = ([{"params": fe, "lr": lr}] if fe else []) + [{"params": hd, "lr": head_lr or lr}]
    opt = torch.optim.AdamW(groups, weight_decay=weight_decay)
    loss_fn = nn.BCEWithLogitsLoss()

    xn, xc = _tensors(train, device)
    y = torch.as_tensor(train.y, device=device)
    n = len(train)
    g = torch.Generator().manual_seed(seed)
    best_score, best_epoch, best_state = -np.inf, 0, None

    for ep in range(epochs):
        if fe and head_warmup_epochs:          # repo: lr của feature extractor = 0 trong giai đoạn warm-up head
            opt.param_groups[0]["lr"] = 0.0 if ep < head_warmup_epochs else lr
        model.train()
        if frozen:                              # FE đóng băng: giữ eval mode (dropout/BN cố định)
            for name, m in model.named_children():
                if name != "head":
                    m.eval()
        perm = torch.randperm(n, generator=g).to(device)
        for i in range(0, n, batch_size):
            idx = perm[i:i + batch_size]
            if len(idx) == 1 and n > 1:         # tránh lỗi BatchNorm với batch 1 mẫu
                continue
            out = model(xn[idx], None if xc is None else xc[idx])
            target = y[idx]
            if target.ndim == 1:
                out = out.squeeze(-1)
            loss = loss_fn(out, target)
            opt.zero_grad(set_to_none=True)
            loss.backward()
            opt.step()

        if val is not None:
            score = auc(val.y, predict_logits(model, val, device))
            if score > best_score:
                best_score, best_epoch, best_state = score, ep + 1, copy.deepcopy(model.state_dict())
            elif patience is not None and (ep + 1 - best_epoch) > patience:
                break
    if val is not None and best_state is not None:
        model.load_state_dict(best_state)
    else:
        best_epoch = epochs
    return model, best_epoch, best_score


# ============================================================================ pre-training
def pretrain(arch: str, hp: dict, up: dict, cards, cfg: ExpConfig, device, seed: int = 0):
    d_out = up["train"].y.shape[1]
    model = build_model(arch, up["train"].x_num.shape[1], cards, d_out, hp)
    model, best_ep, val_auc = fit(model, up["train"], up["val"], epochs=cfg.pretrain_epochs, lr=hp["lr"],
                                  weight_decay=hp["weight_decay"], patience=cfg.pretrain_patience,
                                  batch_size=cfg.batch_size, device=device, seed=seed)
    return model, val_auc, best_ep


# ============================================================================ fine-tuning
def downstream_schedule(n: int, setup: str):
    """Chọn số epoch theo Phụ lục B.6.3. Trả về (epochs, dùng_val_early_stopping)."""
    e2e, mlp_head = setup.endswith("E2E"), setup.startswith("MLP")
    if n <= 10:
        return 30, False
    if n <= 20:
        return 60, False
    if e2e or setup == "FS":
        return None, True                      # 20% val + early stopping (patience 30)
    return (100 if mlp_head else 200), False


def _split_val(train: TabularData, frac: float, seed: int):
    idx = np.arange(len(train))
    try:
        tr, va = train_test_split(idx, test_size=frac, stratify=train.y, random_state=seed)
    except ValueError:
        tr, va = train_test_split(idx, test_size=frac, random_state=seed)
    return train.subset(tr), train.subset(va)


def finetune(arch: str, hp: dict, pretrained_state: dict, n_up: int, setup: str, train: TabularData,
             cards, cfg: ExpConfig, device, seed: int):
    model = build_model(arch, train.x_num.shape[1], cards, n_up, hp)
    model.load_state_dict(pretrained_state)
    replace_head(model, 1, mlp_head=setup.startswith("MLP"), hidden=cfg.mlp_head_dim)
    e2e = setup.endswith("E2E")
    if not e2e:
        freeze_feature_extractor(model)
    epochs, use_val = downstream_schedule(len(train), setup)
    val = None
    if use_val:
        train, val = _split_val(train, cfg.downstream_val_frac, seed)
        epochs = cfg.max_downstream_epochs
    model, _, _ = fit(model, train, val, epochs=epochs, lr=cfg.finetune_lr, weight_decay=hp["weight_decay"],
                      head_lr=cfg.head_lr, head_warmup_epochs=cfg.head_warmup_epochs if e2e else 0,
                      patience=cfg.downstream_patience, batch_size=cfg.batch_size, device=device, seed=seed)
    return model


# ============================================================================ from scratch
def train_scratch(arch: str, hp: dict, train: TabularData, cards, cfg: ExpConfig, device, seed: int,
                  n_epochs: int = None):
    """n_epochs: số epoch tốt nhất tìm được khi tune trên upstream-subsample (Phụ lục B.6.3).
    Nếu None (không tune) thì dùng lịch giống E2E."""
    model = build_model(arch, train.x_num.shape[1], cards, 1, hp)
    val = None
    if n_epochs is None:
        n_epochs, use_val = downstream_schedule(len(train), "FS")
        if use_val:
            train, val = _split_val(train, cfg.downstream_val_frac, seed)
            n_epochs = cfg.max_downstream_epochs
    lr = hp.get("lr", cfg.scratch_lr)
    model, _, _ = fit(model, train, val, epochs=n_epochs, lr=lr, weight_decay=hp["weight_decay"],
                      patience=cfg.downstream_patience, batch_size=cfg.batch_size, device=device, seed=seed)
    return model
