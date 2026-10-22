"""
gbdt.py
CatBoost / XGBoost baseline, có và không có Stacking (Mục 3.3, Phụ lục B.6.4):
  - XGBoost: 11 bộ phân loại nhị phân trên 11 nhãn upstream
  - CatBoost: 1 mô hình MultiLogloss dự đoán cả 11 nhãn upstream
  Xác suất dự đoán được nối thêm vào đặc trưng downstream.
"""
import numpy as np


def make_gbdt(kind: str, params: dict, seed: int):
    if kind == "xgboost":
        from xgboost import XGBClassifier
        return XGBClassifier(**params, random_state=seed, tree_method="hist", n_jobs=-1, eval_metric="logloss")
    if kind == "catboost":
        from catboost import CatBoostClassifier
        p = dict(params)
        if "bagging_temperature" in p:
            p.setdefault("bootstrap_type", "Bayesian")
        return CatBoostClassifier(**p, random_seed=seed, verbose=0, thread_count=-1, allow_writing_files=False)
    raise ValueError(kind)


def fit_predict_gbdt(kind, params, X_tr, y_tr, X_te, seed):
    model = make_gbdt(kind, params, seed)
    model.fit(X_tr, y_tr.astype(int))
    return model.predict_proba(X_te)[:, 1]


class StackingFeatures:
    """Huấn luyện các mô hình GBDT upstream một lần cho mỗi downstream target, sau đó sinh
    xác suất của các nhãn upstream để nối vào dữ liệu downstream."""

    def __init__(self, kind: str, X_up: np.ndarray, Y_up: np.ndarray, seed: int = 0):
        self.kind = kind
        if kind == "xgboost":
            from xgboost import XGBClassifier
            self.models = [XGBClassifier(random_state=seed, tree_method="hist", n_jobs=-1,
                                         eval_metric="logloss").fit(X_up, Y_up[:, j].astype(int))
                           for j in range(Y_up.shape[1])]
        elif kind == "catboost":
            from catboost import CatBoostClassifier
            self.model = CatBoostClassifier(loss_function="MultiLogloss", random_seed=seed, verbose=0,
                                            thread_count=-1, allow_writing_files=False)
            self.model.fit(X_up, Y_up.astype(int))
        else:
            raise ValueError(kind)

    def transform(self, X: np.ndarray) -> np.ndarray:
        if self.kind == "xgboost":
            probs = np.column_stack([m.predict_proba(X)[:, 1] for m in self.models])
        else:
            probs = np.asarray(self.model.predict_proba(X))
        return np.hstack([X, probs]).astype(np.float32)
