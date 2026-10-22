"""
tuning.py
Tối ưu siêu tham số bằng Optuna (TPE / Bayesian), 50 trials (Mục 3.4, Phụ lục C).
  - Mô hình transfer: tune trên TOÀN BỘ upstream, chọn theo upstream-val (multi-label AUC)
  - FS & GBDT: tune trên 1 nhãn upstream ngẫu nhiên với SỐ MẪU = số mẫu downstream,
    đánh giá trên upstream-val đầy đủ; FS lưu thêm epoch tốt nhất.
"""
import numpy as np
import optuna

from config import DEFAULT_HPARAMS, ExpConfig
from gbdt import fit_predict_gbdt
from models import build_model
from training import auc, fit

optuna.logging.set_verbosity(optuna.logging.WARNING)


def _maybe_zero(trial, name, low, high, log=True):
    return trial.suggest_float(name, low, high, log=log) if trial.suggest_categorical(f"use_{name}", [True, False]) else 0.0


def suggest_deep(trial, arch: str) -> dict:
    if arch == "ft_transformer":                               # Bảng 2
        return dict(n_layers=trial.suggest_int("n_layers", 1, 4),
                    d_token=trial.suggest_int("d_token", 64, 512, step=8),   # chia hết cho 8 head
                    residual_dropout=_maybe_zero(trial, "residual_dropout", 0.0, 0.2, log=False),
                    attention_dropout=trial.suggest_float("attention_dropout", 0.0, 0.5),
                    ffn_dropout=trial.suggest_float("ffn_dropout", 0.0, 0.5),
                    d_ffn_factor=trial.suggest_float("d_ffn_factor", 2 / 3, 8 / 3),
                    n_heads=8,
                    lr=trial.suggest_float("lr", 1e-5, 1e-3, log=True),
                    weight_decay=trial.suggest_float("weight_decay", 1e-6, 1e-3, log=True))
    if arch == "resnet":                                       # Bảng 3
        return dict(n_layers=trial.suggest_int("n_layers", 1, 8),
                    d_embedding=trial.suggest_int("d_embedding", 64, 512),
                    d=trial.suggest_int("d", 64, 512),
                    d_hidden_factor=trial.suggest_float("d_hidden_factor", 1.0, 4.0),
                    hidden_dropout=trial.suggest_float("hidden_dropout", 0.0, 0.5),
                    residual_dropout=_maybe_zero(trial, "residual_dropout", 0.0, 0.5, log=False),
                    lr=trial.suggest_float("lr", 1e-5, 1e-2, log=True),
                    weight_decay=_maybe_zero(trial, "weight_decay", 1e-6, 1e-3))
    if arch == "mlp":                                          # Bảng 4 (kiểu RTDL: first/middle/last)
        n = trial.suggest_int("n_layers", 1, 8)
        first = trial.suggest_int("d_first", 1, 512)
        middle = trial.suggest_int("d_middle", 1, 512) if n > 2 else first
        last = trial.suggest_int("d_last", 1, 512) if n > 1 else first
        layers = [first] + [middle] * max(n - 2, 0) + ([last] if n > 1 else [])
        return dict(d_layers=layers, d_embedding=trial.suggest_int("d_embedding", 64, 512),
                    dropout=_maybe_zero(trial, "dropout", 0.0, 0.5, log=False),
                    lr=trial.suggest_float("lr", 1e-5, 1e-2, log=True),
                    weight_decay=_maybe_zero(trial, "weight_decay", 1e-6, 1e-3))
    if arch == "tab_transformer":                              # Bảng 5
        return dict(n_heads=trial.suggest_int("n_heads", 2, 8),
                    n_layers=trial.suggest_int("n_layers", 1, 12),
                    d_embedding=trial.suggest_int("d_embedding", 8, 128),
                    attention_dropout=trial.suggest_float("attention_dropout", 0.0, 0.5),
                    ff_dropout=trial.suggest_float("ff_dropout", 0.0, 0.5),
                    lr=trial.suggest_float("lr", 1e-6, 1e-3, log=True),
                    weight_decay=trial.suggest_float("weight_decay", 1e-6, 1e-3, log=True))
    raise ValueError(arch)


def suggest_gbdt(trial, kind: str) -> dict:
    if kind == "catboost":                                     # Bảng 6
        return dict(iterations=trial.suggest_int("iterations", 2, 1000),
                    depth=trial.suggest_int("depth", 3, 10),
                    learning_rate=trial.suggest_float("learning_rate", 1e-5, 1.0, log=True),
                    bagging_temperature=trial.suggest_float("bagging_temperature", 0.0, 1.0),
                    l2_leaf_reg=trial.suggest_float("l2_leaf_reg", 1.0, 10.0, log=True),
                    leaf_estimation_iterations=trial.suggest_int("leaf_estimation_iterations", 1, 10))
    if kind == "xgboost":                                      # Bảng 7
        return dict(n_estimators=trial.suggest_int("n_estimators", 2, 1000),
                    max_depth=trial.suggest_int("max_depth", 3, 10),
                    min_child_weight=trial.suggest_float("min_child_weight", 1e-8, 1e5, log=True),
                    subsample=trial.suggest_float("subsample", 0.5, 1.0),
                    learning_rate=trial.suggest_float("learning_rate", 1e-5, 1.0, log=True),
                    colsample_bylevel=trial.suggest_float("colsample_bylevel", 0.5, 1.0),
                    colsample_bytree=trial.suggest_float("colsample_bytree", 0.5, 1.0),
                    gamma=_maybe_zero(trial, "gamma", 1e-8, 1e2),
                    reg_lambda=_maybe_zero(trial, "reg_lambda", 1e-8, 1e2),
                    reg_alpha=_maybe_zero(trial, "reg_alpha", 1e-8, 1e2))
    raise ValueError(kind)


def _study(seed):
    return optuna.create_study(direction="maximize", sampler=optuna.samplers.TPESampler(seed=seed))


def _safe(x):
    return -1.0 if (x is None or np.isnan(x)) else x


# ---------------------------------------------------------------- transfer: tune trên toàn bộ upstream
def tune_pretrain(arch, up, cards, cfg: ExpConfig, device, seed=0):
    def objective(trial):
        hp = suggest_deep(trial, arch)
        model = build_model(arch, up["train"].x_num.shape[1], cards, up["train"].y.shape[1], hp)
        _, _, score = fit(model, up["train"], up["val"], epochs=cfg.pretrain_epochs, lr=hp["lr"],
                          weight_decay=hp["weight_decay"], patience=cfg.pretrain_patience,
                          batch_size=cfg.batch_size, device=device, seed=seed)
        trial.set_user_attr("hp", hp)
        return _safe(score)

    st = _study(seed)
    st.optimize(objective, n_trials=cfg.n_trials)
    return st.best_trial.user_attrs["hp"], st.best_value


# ---------------------------------------------------------------- FS: tune trên upstream-subsample
def tune_scratch(arch, proxy, cards, cfg: ExpConfig, device, seed=0):
    def objective(trial):
        hp = suggest_deep(trial, arch)
        model = build_model(arch, proxy["train"].x_num.shape[1], cards, 1, hp)
        _, best_ep, score = fit(model, proxy["train"], proxy["val"], epochs=cfg.max_downstream_epochs,
                                lr=hp["lr"], weight_decay=hp["weight_decay"], patience=cfg.downstream_patience,
                                batch_size=cfg.batch_size, device=device, seed=seed)
        trial.set_user_attr("hp", hp)
        trial.set_user_attr("best_epoch", int(best_ep))
        return _safe(score)

    st = _study(seed)
    st.optimize(objective, n_trials=cfg.n_trials)
    return st.best_trial.user_attrs["hp"], st.best_trial.user_attrs["best_epoch"]


# ---------------------------------------------------------------- GBDT: tune trên upstream-subsample
def tune_gbdt(kind, proxy, cfg: ExpConfig, seed=0):
    def objective(trial):
        params = suggest_gbdt(trial, kind)
        try:
            p = fit_predict_gbdt(kind, params, proxy["train"].x_gbdt, proxy["train"].y, proxy["val"].x_gbdt, seed)
            return _safe(auc(proxy["val"].y, p))
        except Exception:
            return -1.0

    st = _study(seed)
    st.optimize(objective, n_trials=cfg.n_trials)
    params = suggest_gbdt(optuna.trial.FixedTrial(st.best_params), kind)
    return params


def default_hp(arch):
    return dict(DEFAULT_HPARAMS[arch])
