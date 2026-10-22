"""
kb1_v2.py — G0-1: thí nghiệm 2×2 (đủ đặc trưng / khái niệm chung × trong-miền / xuyên-miền)
với nhiều họ mô hình, theo yêu cầu R1 của đánh giá 07/10/2026.

    python kb1_v2.py --ibm data/WA_Fn-UseC_-HR-Employee-Attrition.csv --jc data/aug_train.csv --out results/kb1_v2

Đầu ra: results_kb1v2_<cfg>.csv (mỗi dòng = 1 cấu hình × 1 lần chia), predictions_kb1v2_<cfg>.csv.gz
(dự đoán thô id, y_true, y_score), sanity_kb1v2_<cfg>.txt.
"""
import argparse, hashlib, json, os, time, warnings
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, roc_auc_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder, QuantileTransformer, StandardScaler
from xgboost import XGBClassifier

from hr_data import canonical, full_features, load_ibm, load_jobchange
from splits import make_splits, test_splits

warnings.filterwarnings("ignore")
BINARY = ["male", "gender_other_missing"]

CFG = dict(R=10, test_size=0.2,
           models=dict(LR=dict(C=1.0), RF=dict(n_estimators=300), RF_leaf50=dict(n_estimators=300, min_samples_leaf=50),
                       XGB=dict(n_estimators=300, max_depth=4, learning_rate=0.05, subsample=0.8)),
           encodings=["std", "rank"], concept_sets=["canon4", "canon5"])


def make_model(name, seed):
    p = CFG["models"][name]
    if name == "LR":
        return LogisticRegression(C=p["C"], max_iter=2000)
    if name.startswith("RF"):
        return RandomForestClassifier(**p, n_jobs=-1, random_state=seed)
    return XGBClassifier(**p, eval_metric="logloss", n_jobs=2, random_state=seed, verbosity=0)


# ------------------------------------------------------------------ mã hoá khái niệm chung
class DomainEncoder:
    """std : điền median + chuẩn hoá z, fit trên dữ liệu huấn luyện của mô hình (áp nguyên cho miền kia).
       rank: điền median + QuantileTransformer(normal) fit riêng trên phần train của TỪNG miền (C1)."""

    def __init__(self, kind):
        self.kind = kind

    def _new(self, cols):
        cont = [c for c in cols if c not in BINARY]
        scaler = StandardScaler() if self.kind == "std" else QuantileTransformer(
            output_distribution="normal", n_quantiles=200, random_state=0)
        return ColumnTransformer([("c", make_pipeline(SimpleImputer(strategy="median"), scaler), cont),
                                  ("b", "passthrough", [c for c in cols if c in BINARY])])

    def fit_source(self, C_src):
        self.src = self._new(list(C_src.columns)).fit(C_src)
        return self.src.transform(C_src)

    def transform_target(self, C_tgt_fit, C_tgt_apply):
        if self.kind == "std":                      # thang đo của nguồn
            return self.src.transform(C_tgt_apply)
        tgt = self._new(list(C_tgt_fit.columns)).fit(C_tgt_fit)   # chỉ dùng đặc trưng phần train của đích, không nhãn
        return tgt.transform(C_tgt_apply)


def metrics(y, s):
    return roc_auc_score(y, s), average_precision_score(y, s)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ibm", required=True)
    ap.add_argument("--jc", required=True)
    ap.add_argument("--out", default="results/kb1_v2")
    ap.add_argument("--R", type=int, default=CFG["R"])
    a = ap.parse_args()
    CFG["R"] = a.R
    tag = hashlib.md5(json.dumps(CFG, sort_keys=True).encode()).hexdigest()[:8]
    os.makedirs(a.out, exist_ok=True)

    XA, yA, infoA = load_ibm(a.ibm)
    XB, yB, infoB = load_jobchange(a.jc)
    D = {"A": (XA, yA), "B": (XB, yB)}
    print("A:", infoA, "\nB:", infoB)
    SP = {d: make_splits(D[d][1], R=a.R, test_size=CFG["test_size"]) for d in D}
    for d in D:
        test_splits(SP[d], D[d][1])
    CAN = {(d, cs): canonical(D[d][0], d, with_tenure=(cs == "canon5")) for d in D for cs in CFG["concept_sets"]}
    FULL = {d: full_features(D[d][0]) for d in D}

    rows, preds, t0 = [], [], time.time()

    def record(tgt, setting, feats, enc, model, rep, te, score):
        y = D[tgt][1][te]
        auc, ap_ = metrics(y, score)
        rows.append(dict(target=tgt, setting=setting, features=feats, encoding=enc, model=model, rep=rep,
                         auc_roc=auc, pr_auc=ap_, n_test=len(te), pos_test=int(y.sum()), cfg=tag))
        preds.append(pd.DataFrame(dict(target=tgt, setting=setting, features=feats, encoding=enc, model=model,
                                       rep=rep, id=te, y_true=y, y_score=np.round(score, 5))))

    for tgt, src in [("A", "B"), ("B", "A")]:
        for rep in range(a.R):
            tr, te = np.array(SP[tgt][rep]["train"]), np.array(SP[tgt][rep]["test"])
            ytr = D[tgt][1][tr]
            # (1) trong-miền, đủ đặc trưng
            X, cat = FULL[tgt]
            num = [c for c in X.columns if c not in cat]
            for m in CFG["models"]:
                pre = ColumnTransformer([("n", make_pipeline(SimpleImputer(strategy="median"), StandardScaler()), num),
                                         ("c", OneHotEncoder(handle_unknown="ignore"), cat)])
                pipe = make_pipeline(pre, make_model(m, rep)).fit(X.iloc[tr], ytr)
                record(tgt, "in", "full", "-", m, rep, te, pipe.predict_proba(X.iloc[te])[:, 1])
            # (2) trong-miền và (3) xuyên-miền trên khái niệm chung
            for cs in CFG["concept_sets"]:
                Ct, Cs = CAN[(tgt, cs)], CAN[(src, cs)]
                record(tgt, "in", cs, "-", "rule_neg_experience", rep, te,
                       -Ct["experience"].iloc[te].fillna(Ct["experience"].iloc[tr].median()).to_numpy())
                for enc in CFG["encodings"]:
                    e_in = DomainEncoder(enc)
                    Ztr = e_in.fit_source(Ct.iloc[tr]); Zte = e_in.src.transform(Ct.iloc[te])
                    e_x = DomainEncoder(enc)
                    Zs = e_x.fit_source(Cs)                       # nguồn: dùng toàn bộ miền nguồn
                    Zt = e_x.transform_target(Ct.iloc[tr], Ct.iloc[te])
                    for m in CFG["models"]:
                        mi = make_model(m, rep).fit(Ztr, ytr)
                        record(tgt, "in", cs, enc, m, rep, te, mi.predict_proba(Zte)[:, 1])
                        mx = make_model(m, rep).fit(Zs, D[src][1])
                        record(tgt, f"{src}->{tgt}", cs, enc, m, rep, te, mx.predict_proba(Zt)[:, 1])
            print(f"  đích {tgt} lần {rep} xong ({time.time() - t0:.0f}s)", flush=True)

    res = pd.DataFrame(rows)
    res.to_csv(f"{a.out}/results_kb1v2_{tag}.csv", index=False)
    pd.concat(preds).to_csv(f"{a.out}/predictions_kb1v2_{tag}.csv.gz", index=False, compression="gzip")

    # sanity check (giao thức 6.4)
    lines = [f"cfg={tag}", f"A: {infoA}", f"B: {infoB}"]
    rng = np.random.RandomState(0)
    for tgt in "AB":
        aucs = []
        for rep in range(a.R):
            tr, te = np.array(SP[tgt][rep]["train"]), np.array(SP[tgt][rep]["test"])
            C = CAN[(tgt, "canon4")]
            e = DomainEncoder("std"); Ztr = e.fit_source(C.iloc[tr])
            m = LogisticRegression(max_iter=2000).fit(Ztr, rng.permutation(D[tgt][1][tr]))
            aucs.append(roc_auc_score(D[tgt][1][te], m.predict_proba(e.src.transform(C.iloc[te]))[:, 1]))
        lines.append(f"Đích {tgt}: LR với nhãn train bị xáo trộn -> AUC-ROC TB {np.mean(aucs):.3f} (kỳ vọng ≈ 0,5); "
                     f"PR-AUC của baseline lớp đa số = tỷ lệ dương {D[tgt][1].mean():.4f}")
    open(f"{a.out}/sanity_kb1v2_{tag}.txt", "w").write("\n".join(lines))
    json.dump(CFG, open(f"{a.out}/config_kb1v2_{tag}.json", "w"), indent=2)
    print("\n".join(lines))
    print(f"Đã lưu {len(res)} dòng vào {a.out}/results_kb1v2_{tag}.csv")


if __name__ == "__main__":
    main()
