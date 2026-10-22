"""
kb1_pair.py — Thí nghiệm 2×2 (đủ đặc trưng / khái niệm chung × trong-miền / xuyên-miền) cho một cặp miền bất kỳ.
Tổng quát hoá kb1_v2.py (cặp AB) sang các cặp AC, AD; thêm TabPFN v2 (R1 của đánh giá 07/10/2026).

    python kb1_pair.py --pair AD --data A=data/ibm.csv D=data/turnover.csv
    python kb1_pair.py --pair AB --data A=... B=... --only TabPFN --device cuda      # trên Colab GPU

Với cặp AB và các mô hình CPU, kết quả trùng kb1_v2.py (cùng lần chia, cùng mã hoá).
TabPFN v2: chỉ chạy trên tập khái niệm chính và đủ đặc trưng; nếu tập huấn luyện > 10.000 dòng thì rút ngẫu nhiên
phân tầng 10.000 dòng (giới hạn của TabPFN v2), ghi rõ trong cột n_train.
"""
import argparse, hashlib, json, os, time, warnings
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder, QuantileTransformer, StandardScaler
from xgboost import XGBClassifier

from hr_data import full_features
from pairs import LOADERS, PAIRS, concepts, parse_data_args
from splits import make_splits, test_splits

warnings.filterwarnings("ignore")

CFG = dict(R=10, test_size=0.2,
           models=dict(LR=dict(C=1.0), RF=dict(n_estimators=300), RF_leaf50=dict(n_estimators=300, min_samples_leaf=50),
                       XGB=dict(n_estimators=300, max_depth=4, learning_rate=0.05, subsample=0.8),
                       TabPFN=dict(version="v2", n_estimators=4, max_train=10000)),
           encodings=["std", "rank"])
CPU_MODELS = ["LR", "RF", "RF_leaf50", "XGB"]


class Enc:
    """std: median + z-score fit trên dữ liệu huấn luyện của mô hình (áp nguyên cho miền kia).
       rank: median + QuantileTransformer(normal) fit riêng trên phần train của TỪNG miền (C1)."""

    def __init__(self, kind, binary):
        self.kind, self.binary = kind, binary

    def _new(self, cols):
        cont = [c for c in cols if c not in self.binary]
        sc = StandardScaler() if self.kind == "std" else QuantileTransformer(output_distribution="normal", n_quantiles=200,
                                                                              random_state=0)
        return ColumnTransformer([("c", make_pipeline(SimpleImputer(strategy="median"), sc), cont),
                                  ("b", make_pipeline(SimpleImputer(strategy="most_frequent")), [c for c in cols if c in self.binary])])

    def fit_source(self, C):
        self.src = self._new(list(C.columns)).fit(C)
        return self.src.transform(C)

    def transform_target(self, C_fit, C_apply):
        if self.kind == "std":
            return self.src.transform(C_apply)
        return self._new(list(C_fit.columns)).fit(C_fit).transform(C_apply)


def make_model(name, seed, device="cpu"):
    p = CFG["models"][name]
    if name == "LR":
        return LogisticRegression(C=p["C"], max_iter=2000)
    if name.startswith("RF"):
        return RandomForestClassifier(**p, n_jobs=-1, random_state=seed)
    if name == "XGB":
        return XGBClassifier(**p, eval_metric="logloss", n_jobs=2, random_state=seed, verbosity=0)
    from tabpfn import TabPFNClassifier
    try:
        from tabpfn.constants import ModelVersion
        return TabPFNClassifier.create_default_for_version(ModelVersion.V2, device=device, random_state=seed, n_estimators=p["n_estimators"])
    except Exception:
        return TabPFNClassifier(device=device, random_state=seed, n_estimators=p["n_estimators"])


def cap(X, y, seed, m):
    """Rút phân tầng tối đa max_train dòng cho TabPFN."""
    if m != "TabPFN" or len(y) <= CFG["models"]["TabPFN"]["max_train"]:
        return X, y
    idx, _ = train_test_split(np.arange(len(y)), train_size=CFG["models"]["TabPFN"]["max_train"], stratify=y, random_state=seed)
    return (X.iloc[idx] if hasattr(X, "iloc") else X[idx]), y[idx]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pair", required=True, choices=list(PAIRS))
    ap.add_argument("--data", nargs="+", required=True, help="A=path D=path ...")
    ap.add_argument("--out", default=None)
    ap.add_argument("--R", type=int, default=CFG["R"])
    ap.add_argument("--only", nargs="*", default=None)
    ap.add_argument("--device", default="cpu")
    a = ap.parse_args()
    P = PAIRS[a.pair]; d1, d2 = P["domains"]
    paths = parse_data_args(a.data)
    CFG["R"] = a.R
    models = a.only or CPU_MODELS
    tag = hashlib.md5(json.dumps(dict(CFG, pair=a.pair), sort_keys=True).encode()).hexdigest()[:8]
    suffix = "_".join(models) if a.only else "cpu"
    out = a.out or f"results/kb1_{a.pair}"
    os.makedirs(out, exist_ok=True)

    D, INFO = {}, {}
    for d in (d1, d2):
        X, y, info = LOADERS[d](paths[d]); D[d] = (X, y); INFO[d] = info
        print(d, info, flush=True)
    SP = {d: make_splits(D[d][1], R=a.R, test_size=CFG["test_size"]) for d in D}
    for d in D:
        test_splits(SP[d], D[d][1])
    sets = P["sets"]
    CAN = {(d, cs): concepts(a.pair, d, D[d][0], cs) for d in D for cs in sets}
    FULL = {d: full_features(D[d][0]) for d in D}
    rule_col, rule_sign = P["rule"]

    rows, preds, t0 = [], [], time.time()
    out_csv = f"{out}/results_kb1_{a.pair}_{tag}_{suffix}.csv"

    def record(tgt, setting, feats, enc, model, rep, te, score, n_train):
        y = D[tgt][1][te]
        rows.append(dict(pair=a.pair, target=tgt, setting=setting, features=feats, encoding=enc, model=model, rep=rep,
                         auc_roc=roc_auc_score(y, score), pr_auc=average_precision_score(y, score), n_train=n_train,
                         n_test=len(te), pos_test=int(y.sum()), cfg=tag))
        preds.append(pd.DataFrame(dict(pair=a.pair, target=tgt, setting=setting, features=feats, encoding=enc, model=model,
                                       rep=rep, id=te, y_true=y, y_score=np.round(score, 5))))

    for tgt, src in [(d1, d2), (d2, d1)]:
        for rep in range(a.R):
            tr, te = np.array(SP[tgt][rep]["train"]), np.array(SP[tgt][rep]["test"])
            ytr = D[tgt][1][tr]
            X, cat = FULL[tgt]
            num = [c for c in X.columns if c not in cat]
            for m in models:                                    # (1) trong-miền, đủ đặc trưng
                Xf, yf = cap(X.iloc[tr], ytr, rep, m)
                if m == "TabPFN":
                    pre = ColumnTransformer([("n", "passthrough", num),
                                             ("c", OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1), cat)])
                else:
                    pre = ColumnTransformer([("n", make_pipeline(SimpleImputer(strategy="median"), StandardScaler()), num),
                                             ("c", OneHotEncoder(handle_unknown="ignore"), cat)])
                pipe = make_pipeline(pre, make_model(m, rep, a.device)).fit(Xf, yf)
                record(tgt, "in", "full", "-", m, rep, te, pipe.predict_proba(X.iloc[te])[:, 1], len(yf))
            for cs in sets:                                     # (2) trong-miền và (3) xuyên-miền trên khái niệm chung
                if "TabPFN" in models and cs != P["main"] and models == ["TabPFN"]:
                    continue
                Ct, Cs = CAN[(tgt, cs)], CAN[(src, cs)]
                if not a.only:
                    r = rule_sign * Ct[rule_col].iloc[te].fillna(Ct[rule_col].iloc[tr].median()).to_numpy()
                    record(tgt, "in", cs, "-", "rule", rep, te, r, len(tr))
                for enc in CFG["encodings"]:
                    e_in = Enc(enc, P["binary"]); Ztr = e_in.fit_source(Ct.iloc[tr]); Zte = e_in.src.transform(Ct.iloc[te])
                    e_x = Enc(enc, P["binary"]); Zs = e_x.fit_source(Cs)
                    Zt = e_x.transform_target(Ct.iloc[tr], Ct.iloc[te])
                    for m in models:
                        if m == "TabPFN" and cs != P["main"]:
                            continue
                        Zi, yi = cap(Ztr, ytr, rep, m)
                        mi = make_model(m, rep, a.device).fit(Zi, yi)
                        record(tgt, "in", cs, enc, m, rep, te, mi.predict_proba(Zte)[:, 1], len(yi))
                        Zx, yx = cap(Zs, D[src][1], rep, m)
                        mx = make_model(m, rep, a.device).fit(Zx, yx)
                        record(tgt, f"{src}->{tgt}", cs, enc, m, rep, te, mx.predict_proba(Zt)[:, 1], len(yx))
            print(f"  [{a.pair}] đích {tgt} lần {rep} xong ({time.time() - t0:.0f}s)", flush=True)
            pd.DataFrame(rows).to_csv(out_csv, index=False)

    res = pd.DataFrame(rows); res.to_csv(out_csv, index=False)
    pd.concat(preds).to_csv(out_csv.replace("results_", "predictions_").replace(".csv", ".csv.gz"), index=False, compression="gzip")
    lines = [f"pair={a.pair} cfg={tag} models={models}"] + [f"{d}: {INFO[d]}" for d in D]
    if not a.only:                                              # sanity check: xáo trộn nhãn đích
        rng = np.random.RandomState(0)
        for tgt in (d1, d2):
            aucs = []
            for rep in range(a.R):
                tr, te = np.array(SP[tgt][rep]["train"]), np.array(SP[tgt][rep]["test"])
                C = CAN[(tgt, P["main"])]
                e = Enc("std", P["binary"]); Ztr = e.fit_source(C.iloc[tr])
                m = LogisticRegression(max_iter=2000).fit(Ztr, rng.permutation(D[tgt][1][tr]))
                aucs.append(roc_auc_score(D[tgt][1][te], m.predict_proba(e.src.transform(C.iloc[te]))[:, 1]))
            lines.append(f"Đích {tgt}: LR với nhãn train bị xáo trộn -> AUC-ROC TB {np.mean(aucs):.3f} (kỳ vọng ≈ 0,5); "
                         f"tỷ lệ dương {D[tgt][1].mean():.4f}")
    open(f"{out}/sanity_kb1_{a.pair}_{tag}_{suffix}.txt", "w").write("\n".join(lines))
    json.dump(dict(CFG, pair=a.pair, models_run=models, sets=sets, main=P["main"], binary=P["binary"], rule=P["rule"]),
              open(f"{out}/config_kb1_{a.pair}_{tag}.json", "w"), indent=2, ensure_ascii=False)
    print("\n".join(lines)); print(f"Đã lưu {len(res)} dòng vào {out_csv}")


if __name__ == "__main__":
    main()
