"""
run_experiments.py
Chạy toàn bộ thực nghiệm Mục 4 (Hình 2) của bài báo:
  12 nhiệm vụ downstream x 5 mức dữ liệu (4/10/20/100/200) = 60 kịch bản
  Mô hình sâu: FS + 4 kịch bản transfer (LH, MLP, LH-E2E, MLP-E2E)
  GBDT: CatBoost/XGBoost có & không Stacking
  Mỗi cấu hình chạy với 10 seeds, đo ROC-AUC trên tập test downstream cố định.

Ví dụ:
  python run_experiments.py --dataset metamimic --data-path data/MetaMIMIC.csv
  python run_experiments.py --dataset metamimic --data-path data/MetaMIMIC.csv --quick   # chạy thử
  python run_experiments.py --dataset yeast --models ft_transformer mlp catboost   # tự tải Yeast từ OpenML
"""
import argparse
import json
import os
import time

import numpy as np
import pandas as pd
import torch

from config import DEEP_MODELS, GBDT_MODELS, TRANSFER_SETUPS, ExpConfig, quick_config
from data import TransferBenchmark, load_metamimic, load_mulan, load_openml_yeast
from gbdt import StackingFeatures, fit_predict_gbdt
from training import auc, finetune, predict_logits, pretrain, train_scratch
from tuning import default_hp, tune_gbdt, tune_pretrain, tune_scratch

RESULT_COLS = ["dataset", "target_idx", "target", "n_samples", "model", "setup", "seed", "auc"]


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--dataset", default="metamimic", choices=["metamimic", "yeast", "emotions", "mulan"])
    p.add_argument("--data-path", default="openml", help="đường dẫn CSV/ARFF; với yeast có thể để 'openml' để tự tải")
    p.add_argument("--n-labels", type=int, default=None, help="số cột nhãn cuối file (Yeast=14, Emotions=6)")
    p.add_argument("--models", nargs="+", default=DEEP_MODELS + GBDT_MODELS)
    p.add_argument("--setups", nargs="+", default=["FS"] + TRANSFER_SETUPS + ["Stacking"])
    p.add_argument("--targets", nargs="+", type=int, default=None, help="chỉ số nhiệm vụ downstream (mặc định: tất cả)")
    p.add_argument("--sizes", nargs="+", type=int, default=None, help="vd: 4 10 20 100 200 (hoặc 400 1000 2000)")
    p.add_argument("--seeds", type=int, default=None, help="số seed (mặc định 10)")
    p.add_argument("--n-trials", type=int, default=None)
    p.add_argument("--no-tune", action="store_true", help="dùng siêu tham số mặc định (Bảng 2-5)")
    p.add_argument("--pretrain-per-seed", action="store_true")
    p.add_argument("--quick", action="store_true", help="cấu hình rút gọn để chạy thử")
    p.add_argument("--fixed-downstream-sample", action="store_true", help="giữ một lần rút n mẫu cho mọi seed (như repo gốc [11])")
    p.add_argument("--batch-size", type=int, default=None, help="mặc định 256 như bài báo; giảm nếu thiếu bộ nhớ")
    p.add_argument("--out-dir", default="outputs")
    p.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    return p.parse_args()


def build_cfg(a) -> ExpConfig:
    cfg = quick_config() if a.quick else ExpConfig()
    if a.sizes: cfg.sample_sizes = a.sizes
    if a.seeds: cfg.seeds = list(range(a.seeds))
    if a.n_trials: cfg.n_trials = a.n_trials
    if a.no_tune: cfg.tune = False
    if a.pretrain_per_seed: cfg.pretrain_per_seed = True
    if a.batch_size: cfg.batch_size = a.batch_size
    if a.fixed_downstream_sample: cfg.resample_per_seed = False
    return cfg


def load_benchmark(a, cfg):
    if a.dataset == "metamimic":
        X, Y, num, cat = load_metamimic(a.data_path)
    elif a.dataset == "yeast" and a.data_path == "openml":
        X, Y, num, cat = load_openml_yeast()
    else:
        n_labels = a.n_labels or {"yeast": 14, "emotions": 6}.get(a.dataset)
        if n_labels is None:
            raise ValueError("Cần --n-labels")
        X, Y, num, cat = load_mulan(a.data_path, n_labels)
    return TransferBenchmark(X, Y, num, cat, cfg, name=a.dataset)


class Cache:
    """Lưu siêu tham số / trọng số pre-train ra đĩa để có thể chạy lại, tiếp tục giữa chừng."""

    def __init__(self, root):
        self.root = root
        os.makedirs(root, exist_ok=True)

    def json(self, key, fn):
        path = os.path.join(self.root, key + ".json")
        if os.path.exists(path):
            return json.load(open(path))
        val = fn()
        json.dump(val, open(path, "w"), indent=2)
        return val

    def torch(self, key, fn):
        path = os.path.join(self.root, key + ".pt")
        if os.path.exists(path):
            return torch.load(path, map_location="cpu")
        val = fn()
        torch.save(val, path)
        return val


def main():
    a = parse_args()
    cfg = build_cfg(a)
    torch.set_num_threads(max(1, os.cpu_count() or 1))
    bench = load_benchmark(a, cfg)
    # O6/B3: khoá cache và file kết quả theo cấu hình -> không trộn kết quả giữa các cấu hình
    import dataclasses, hashlib
    cfg_json = json.dumps(dict(dataclasses.asdict(cfg), models=sorted(a.models), setups=sorted(a.setups)), sort_keys=True)
    cfg_tag = hashlib.md5(cfg_json.encode()).hexdigest()[:8]
    print(f"Cấu hình {cfg_tag}: {cfg_json}")
    cache = Cache(os.path.join(a.out_dir, "cache", f"{a.dataset}_{cfg_tag}"))
    json.dump(json.loads(cfg_json), open(os.path.join(cache.root, "config.json"), "w"), indent=2)
    res_path = os.path.join(a.out_dir, f"results_{a.dataset}_{cfg_tag}.csv")
    done = pd.read_csv(res_path) if os.path.exists(res_path) else pd.DataFrame(columns=RESULT_COLS)
    done_keys = set(zip(done.target_idx, done.n_samples, done.model, done.setup, done.seed))
    rows = []

    def flush():
        nonlocal rows
        if rows:
            pd.DataFrame(rows, columns=RESULT_COLS).to_csv(res_path, mode="a", header=not os.path.exists(res_path),
                                                           index=False)
            rows = []

    def record(t, n, model, setup, seed, score):
        rows.append([a.dataset, t, bench.target_names[t], n, model, setup, seed, score])
        print(f"  t={t:2d} n={n:4d} {model:15s} {setup:8s} seed={seed} AUC={score:.4f}")

    deep = [m for m in a.models if m in DEEP_MODELS]
    gbdts = [m for m in a.models if m in GBDT_MODELS]
    transfer_setups = [s for s in a.setups if s in TRANSFER_SETUPS]
    targets = a.targets if a.targets is not None else list(range(bench.n_targets))
    cards, dev = bench.cat_cardinalities, a.device

    for t in targets:
        t0 = time.time()
        print(f"\n===== Downstream target {t}: {bench.target_names[t]} =====")
        up = bench.upstream(t)
        n_up = up["train"].y.shape[1]
        rng = np.random.RandomState(1000 + t)
        proxy_target = int(rng.choice(bench.upstream_targets(t)))   # nhãn upstream dùng để tune FS/GBDT

        # ---------- 1) Pre-training (tune trên toàn bộ upstream)
        pre_hp, pre_states = {}, {}
        if transfer_setups:
            for arch in deep:
                pre_hp[arch] = cache.json(f"hp_pretrain_{arch}_t{t}",
                                          lambda: tune_pretrain(arch, up, cards, cfg, dev)[0]
                                          if cfg.tune else default_hp(arch))
                pre_seeds = cfg.seeds if cfg.pretrain_per_seed else [0]
                for s in pre_seeds:
                    def _pt(arch=arch, s=s):
                        m, v, ep = pretrain(arch, pre_hp[arch], up, cards, cfg, dev, seed=s)
                        print(f"  [pretrain] {arch} seed={s}: upstream val AUC={v:.4f} (best epoch {ep})")
                        return {k: x.cpu() for k, x in m.state_dict().items()}
                    pre_states[(arch, s)] = cache.torch(f"pretrained_{arch}_t{t}_s{s}", _pt)

        stackers = {}
        for n in cfg.sample_sizes:
            downs = {s: bench.downstream(t, n, seed=s if cfg.resample_per_seed else None) for s in cfg.seeds}
            te = downs[cfg.seeds[0]]["test"]          # tập test cố định cho mọi seed

            # ---------- 2) Mô hình sâu
            for arch in deep:
                if "FS" in a.setups:
                    if cfg.tune:
                        hp_fs, ep_fs = cache.json(f"hp_fs_{arch}_t{t}_n{n}", lambda: list(tune_scratch(
                            arch, bench.upstream_single(proxy_target, n, seed=0), cards, cfg, dev)))
                    else:
                        hp_fs, ep_fs = default_hp(arch), None
                    for s in cfg.seeds:
                        if (t, n, arch, "FS", s) in done_keys: continue
                        m = train_scratch(arch, hp_fs, downs[s]["train"], cards, cfg, dev, seed=s, n_epochs=ep_fs)
                        record(t, n, arch, "FS", s, auc(te.y, predict_logits(m, te, dev)))
                for setup in transfer_setups:
                    for s in cfg.seeds:
                        if (t, n, arch, setup, s) in done_keys: continue
                        state = pre_states[(arch, s if cfg.pretrain_per_seed else 0)]
                        m = finetune(arch, pre_hp[arch], state, n_up, setup, downs[s]["train"], cards, cfg, dev, seed=s)
                        record(t, n, arch, setup, s, auc(te.y, predict_logits(m, te, dev)))
                flush()

            # ---------- 3) GBDT (FS và Stacking)
            for kind in gbdts:
                params = cache.json(f"hp_{kind}_t{t}_n{n}", lambda: tune_gbdt(
                    kind, bench.upstream_single(proxy_target, n, seed=0), cfg) if cfg.tune else default_hp(kind))
                if "Stacking" in a.setups:
                    if kind not in stackers:
                        stackers[kind] = StackingFeatures(kind, up["train"].x_gbdt, up["train"].y)
                    st = stackers[kind]
                    Xte_st = st.transform(te.x_gbdt)
                for s in cfg.seeds:
                    tr = downs[s]["train"]
                    if "FS" in a.setups and (t, n, kind, "FS", s) not in done_keys:
                        p = fit_predict_gbdt(kind, params, tr.x_gbdt, tr.y, te.x_gbdt, s)
                        record(t, n, kind, "FS", s, auc(te.y, p))
                    if "Stacking" in a.setups and (t, n, kind, "Stacking", s) not in done_keys:
                        p = fit_predict_gbdt(kind, params, stackers[kind].transform(tr.x_gbdt), tr.y, Xte_st, s)
                        record(t, n, kind, "Stacking", s, auc(te.y, p))
                flush()
        print(f"  -> xong target {t} trong {(time.time() - t0) / 60:.1f} phút")
    flush()
    print(f"\nKết quả lưu tại {res_path}. Chạy: python analyze_results.py --results {res_path}")


if __name__ == "__main__":
    main()
