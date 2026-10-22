"""
data.py
- Đọc MetaMIMIC (hoặc Yeast/Emotions dạng ARFF/CSV của Mulan)
- Chia 65% upstream-train / 15% upstream-val / 20% downstream-test (cố định qua các seed)
- Tiền xử lý: điền mean, QuantileTransformer (normal) fit trên upstream rồi áp cho downstream,
  biến phân loại thiếu -> hạng mục mới
- Rút mẫu downstream nhỏ (4/10/20/100/200) có phân tầng, đảm bảo đủ 2 lớp
"""
from dataclasses import dataclass
from typing import List, Optional

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OrdinalEncoder, QuantileTransformer

from config import MIMIC_TARGETS, ExpConfig  # noqa


# ----------------------------------------------------------------------------- loaders
def load_metamimic(path: str):
    """MetaMIMIC.csv: subject_id, 171 cột số, gender, 12 cột *_diagnosed."""
    df = pd.read_csv(path)
    targets = [c for c in MIMIC_TARGETS if c in df.columns]
    if len(targets) != 12:
        raise ValueError(f"Chỉ tìm thấy {len(targets)}/12 cột mục tiêu MetaMIMIC trong {path}")
    Y = df[targets].astype(int)
    X = df.drop(columns=targets + [c for c in ["subject_id"] if c in df.columns])
    cat_cols = [c for c in ["gender"] if c in X.columns]
    num_cols = [c for c in X.columns if c not in cat_cols]
    return X, Y, num_cols, cat_cols


def load_mulan(path: str, n_labels: int):
    """Yeast (14 nhãn) / Emotions (6 nhãn) theo định dạng Mulan: n_labels cột cuối là nhãn.
    Hỗ trợ .arff (scipy) hoặc .csv."""
    if path.endswith(".arff"):
        from scipy.io import arff
        data, _ = arff.loadarff(path)
        df = pd.DataFrame(data)
    else:
        df = pd.read_csv(path)
    label_cols = list(df.columns[-n_labels:])
    Y = df[label_cols].apply(lambda s: s.map(lambda v: int(v.decode() if isinstance(v, bytes) else v)))
    X = df.drop(columns=label_cols).astype(float)
    return X, Y, list(X.columns), []


def load_openml_yeast():
    """Yeast (2417 mẫu, 103 đặc trưng, 14 nhãn) tải trực tiếp từ OpenML (https://www.openml.org/d/40597)."""
    from sklearn.datasets import fetch_openml
    X, Y = fetch_openml("yeast", version=4, return_X_y=True, as_frame=True, parser="auto")
    Y = (Y.astype(str).apply(lambda s: s.str.upper()) == "TRUE").astype(int)
    X = X.astype(float)
    return X, Y, list(X.columns), []


# ----------------------------------------------------------------------------- containers
@dataclass
class TabularData:
    x_num: np.ndarray            # đặc trưng số đã chuẩn hoá (cho mạng neuron)
    x_cat: Optional[np.ndarray]  # chỉ số hạng mục (int64) hoặc None
    x_gbdt: np.ndarray           # đặc trưng gốc (đã điền mean) cho GBDT
    y: np.ndarray                # (N,) cho nhị phân, (N, K) cho đa nhãn

    def __len__(self):
        return len(self.y)

    def subset(self, idx):
        return TabularData(self.x_num[idx], None if self.x_cat is None else self.x_cat[idx],
                           self.x_gbdt[idx], self.y[idx])


def stratified_sample(y: np.ndarray, n: int, seed: int) -> np.ndarray:
    """Rút n chỉ số có phân tầng theo y, đảm bảo mỗi lớp có ít nhất 1 mẫu
    (giống stratified_sample_at_least_one_per_class trong repo)."""
    idx_all = np.arange(len(y))
    if n >= len(y):
        return idx_all
    rng = np.random.RandomState(seed)
    classes = np.unique(y)
    try:
        idx, _ = train_test_split(idx_all, train_size=n, stratify=y, random_state=seed)
    except ValueError:
        idx = np.array([], dtype=int)
    if len(np.unique(y[idx])) == len(classes) and len(idx) == n:
        return np.sort(idx)
    # fallback: 1 mẫu/lớp + phần còn lại
    one_each = np.array([rng.choice(idx_all[y == c]) for c in classes])
    rest_pool = np.setdiff1d(idx_all, one_each)
    k = n - len(one_each)
    if k <= 0:
        return np.sort(one_each[:n])
    try:
        rest, _ = train_test_split(rest_pool, train_size=k, stratify=y[rest_pool], random_state=seed)
    except ValueError:
        rest = rng.choice(rest_pool, size=k, replace=False)
    return np.sort(np.concatenate([one_each, rest]))


# ----------------------------------------------------------------------------- benchmark
class TransferBenchmark:
    """Giữ toàn bộ dữ liệu đã tiền xử lý và tạo các bài toán upstream/downstream."""

    def __init__(self, X: pd.DataFrame, Y: pd.DataFrame, num_cols: List[str], cat_cols: List[str],
                 cfg: ExpConfig, name: str = "metamimic"):
        self.name, self.cfg = name, cfg
        self.target_names = list(Y.columns)
        self.n_targets = len(self.target_names)
        X = X.reset_index(drop=True)
        self.Y = Y.reset_index(drop=True).values.astype(np.float32)

        idx = np.arange(len(X))
        rest, self.idx_test = train_test_split(idx, test_size=cfg.test_size, random_state=cfg.split_seed)
        self.idx_train, self.idx_val = train_test_split(rest, test_size=cfg.val_size_of_rest,
                                                        random_state=cfg.split_seed)
        # Pool cho downstream: upstream train + val (repo gộp val vào train ở stage downstream)
        self.idx_pool = np.concatenate([self.idx_train, self.idx_val])

        # --- số: điền mean (tính trên upstream train)
        Xn = X[num_cols].astype(float)
        means = Xn.iloc[self.idx_train].mean()
        Xn = Xn.fillna(means).fillna(0.0).values
        # --- QuantileTransformer fit trên upstream train (Phụ lục B.5), noise nhỏ như repo
        tr = Xn[self.idx_train].copy()
        stds = np.std(tr, axis=0, keepdims=True)
        tr += (1e-3 / np.maximum(stds, 1e-3)) * np.random.default_rng(0).standard_normal(tr.shape)
        qt = QuantileTransformer(output_distribution="normal",
                                 n_quantiles=max(min(len(tr) // 30, 1000), 10),
                                 subsample=int(1e9), random_state=0)
        qt.fit(tr)
        self.x_num = qt.transform(Xn).astype(np.float32)

        # --- phân loại: NaN -> hạng mục mới, mã hoá ordinal
        if cat_cols:
            Xc = X[cat_cols].astype(object).where(X[cat_cols].notna(), "MissingValue").astype(str)
            enc = OrdinalEncoder(dtype=np.int64).fit(Xc.values)
            self.x_cat = enc.transform(Xc.values)
            self.cat_cardinalities = [len(c) for c in enc.categories_]
        else:
            self.x_cat, self.cat_cardinalities = None, None

        # --- GBDT dùng đặc trưng gốc (không chuẩn hoá)
        self.x_gbdt = Xn.astype(np.float32) if self.x_cat is None else \
            np.hstack([Xn, self.x_cat]).astype(np.float32)
        self.n_num = self.x_num.shape[1]

        print(f"[{name}] N={len(X)} | upstream-train={len(self.idx_train)} "
              f"| upstream-val={len(self.idx_val)} | test={len(self.idx_test)} "
              f"| n_num={self.n_num} | cat={self.cat_cardinalities}")

    # ------------------------------------------------------------------ helpers
    def _make(self, idx, y):
        return TabularData(self.x_num[idx], None if self.x_cat is None else self.x_cat[idx],
                           self.x_gbdt[idx], y)

    def upstream_targets(self, downstream_target: int) -> List[int]:
        return [t for t in range(self.n_targets) if t != downstream_target]

    def upstream(self, downstream_target: int):
        """Bài toán pre-training đa nhãn với K-1 nhãn còn lại."""
        cols = self.upstream_targets(downstream_target)
        return {"train": self._make(self.idx_train, self.Y[self.idx_train][:, cols]),
                "val": self._make(self.idx_val, self.Y[self.idx_val][:, cols])}

    def upstream_single(self, target: int, n: int, seed: int):
        """Dữ liệu proxy để tune siêu tham số cho FS/GBDT: 1 nhãn upstream, n mẫu train,
        val = toàn bộ upstream-val (Mục 3.4)."""
        y_tr = self.Y[self.idx_train, target]
        sub = self.idx_train[stratified_sample(y_tr, n, seed)]
        return {"train": self._make(sub, self.Y[sub, target]),
                "val": self._make(self.idx_val, self.Y[self.idx_val, target])}

    def downstream(self, target: int, n: int, seed: int = None):
        """Bài toán downstream nhị phân với n mẫu huấn luyện; test = 20% cố định.
        seed=None -> dùng downstream_sample_seed cố định (đúng repo gốc [11]);
        seed=s    -> rút lại n mẫu theo từng seed để phương sai phản ánh cả nhiễu dữ liệu (O3)."""
        y_pool = self.Y[self.idx_pool, target]
        s = self.cfg.downstream_sample_seed if seed is None else 1000 + seed
        sub = self.idx_pool[stratified_sample(y_pool, n, s)]
        return {"train": self._make(sub, self.Y[sub, target]),
                "test": self._make(self.idx_test, self.Y[self.idx_test, target]),
                "train_idx": sub}
