"""
g0_23.py — Cổng 0, G0-2 và G0-3 (đánh giá GVHD 07/10/2026, mục 6.1 và Phụ lục B).

G0-2  Đường cong chỉ dùng dữ liệu đích: với k ∈ {10, 20, 50, 100, 200, 500, toàn bộ} mẫu có nhãn của miền đích,
      huấn luyện trên ĐỦ đặc trưng của miền đích: LR, RF, XGBoost (CPU) và TabPFN v2 (GPU, chạy trên Colab).
G0-3  Baseline chuyển giao đơn giản, cùng k và cùng lần chia:
      ZS        zero-shot: LR học trên toàn bộ miền nguồn với 4 khái niệm chung, căn chỉnh theo miền (C1); không dùng nhãn đích
      STK_LR    stacking: LR trên [đặc trưng đích + điểm của mô hình nguồn]
      STK_XGB   stacking: XGBoost trên [đặc trưng đích + điểm của mô hình nguồn]
      OFF_XGB   XGBoost học phần dư với base_margin = logit của mô hình nguồn (khởi tạo từ nguồn)
      DAUME_LR  tăng cường đặc trưng của Daumé III [33]: [chung, bản-nguồn, bản-đích] cho 4 khái niệm + đặc trưng riêng của đích;
                huấn luyện trên toàn bộ nguồn + k mẫu đích
      RANKAVG   trung bình hạng w·hạng(điểm nguồn) + (1 − w)·hạng(LR đích), w ∈ {0; 0,25; 0,5; 0,75; 1} chọn bằng kiểm định chéo trên k mẫu
      ANCHOR_LR LR neo hệ số nguồn: logit = điểm nguồn + [4 khái niệm, đặc trưng đích]·δ, phạt L2 trên δ (kéo về mô hình nguồn, kiểu L2-SP [26])
G0-4  Đối chứng: ZS, STK_LR, RANKAVG, ANCHOR_LR lặp lại với mô hình nguồn học trên nhãn nguồn bị xáo trộn (hậu tố _SHUF);
      nếu chuyển giao thật sự mang thông tin, bản _SHUF phải kém hơn.
Bổ sung cho G0-2 theo benchmark De Vos et al. [43] và Chung et al. [5]: CatBoost (CAT) và stacking LR + RF + XGBoost (STACK).

Giao thức: R = 30 lần chia dùng chung (splits.py); k mẫu lồng nhau, phân tầng, ≥ 1 mẫu dương; siêu tham số mặc định cố định
cho mọi k (không tune ở Cổng 0); tiền xử lý fit trên k mẫu; bộ căn chỉnh C1 của miền đích fit trên đặc trưng (không nhãn)
của phần train miền đích.

    python g0_23.py --ibm data/kaggle/WA_Fn-UseC_-HR-Employee-Attrition.csv --jc data/kaggle/aug_train.csv
    python g0_23.py ... --only TabPFN --device cuda          # trên Colab GPU
"""
import argparse, hashlib, json, os, time, warnings
import numpy as np
import pandas as pd
from scipy.special import logit
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, roc_auc_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder, StandardScaler
from xgboost import XGBClassifier

from hr_data import canonical, full_features, load_ibm, load_jobchange
from splits import make_splits, test_splits
from kb1_v2 import DomainEncoder

warnings.filterwarnings("ignore")

CFG = dict(R=30, ks=[10, 20, 50, 100, 200, 500], full=True, concept_set="canon4", source_model="LR(C=1) + C1 rank",
           LR=dict(C=1.0, max_iter=3000), RF=dict(n_estimators=300),
           XGB=dict(n_estimators=300, max_depth=4, learning_rate=0.05, subsample=0.8),
           TabPFN=dict(version="v2", n_estimators=4, max_train=10000),
           CAT=dict(iterations=500, depth=6, learning_rate=0.05), STACK=dict(base=["LR", "RF", "XGB"], meta="LR", cv="min(5, n_pos, n_neg); 3 khi k = toàn bộ"),
           RANKAVG=dict(grid=[0, 0.25, 0.5, 0.75, 1.0]), ANCHOR=dict(lam=1.0), SHUF_seed=0)
TARGET_ONLY = ["LR", "RF", "XGB", "CAT", "STACK", "TabPFN"]
TRANSFER = ["ZS", "STK_LR", "STK_XGB", "OFF_XGB", "DAUME_LR", "RANKAVG", "ANCHOR_LR"]
CONTROL = ["ZS_SHUF", "STK_LR_SHUF", "RANKAVG_SHUF", "ANCHOR_LR_SHUF"]


def xgb(seed):
    return XGBClassifier(**CFG["XGB"], eval_metric="logloss", n_jobs=2, random_state=seed, verbosity=0)


def cat_model(seed):
    from catboost import CatBoostClassifier
    return CatBoostClassifier(**CFG["CAT"], verbose=0, random_seed=seed, thread_count=2, allow_writing_files=False)


def stack_model(seed, ytr, full):
    from sklearn.ensemble import StackingClassifier
    from sklearn.model_selection import StratifiedKFold
    n_pos, n_neg = int(ytr.sum()), int(len(ytr) - ytr.sum())
    cv = 3 if full else min(5, n_pos, n_neg)
    if cv < 2:
        return None
    base = [("lr", LogisticRegression(**CFG["LR"])), ("rf", RandomForestClassifier(**CFG["RF"], n_jobs=-1, random_state=seed)),
            ("xgb", xgb(seed))]
    return StackingClassifier(base, final_estimator=LogisticRegression(**CFG["LR"]),
                              cv=StratifiedKFold(cv, shuffle=True, random_state=seed), stack_method="predict_proba", n_jobs=1)


def _rank(v):
    return pd.Series(v).rank(pct=True).to_numpy()


def rankavg_scores(Ftr, ytr, Fte, s_tr, s_te, seed):
    """Chọn w bằng kiểm định chéo phân tầng trên k mẫu (điểm LR ngoài-fold), rồi trộn hạng trên tập test."""
    from sklearn.model_selection import StratifiedKFold
    n_pos, n_neg = int(ytr.sum()), int(len(ytr) - ytr.sum())
    cv = min(5, n_pos, n_neg)
    grid = CFG["RANKAVG"]["grid"]
    if cv >= 2:
        oof = np.zeros(len(ytr)); fold_id = np.zeros(len(ytr), int)
        for f, (a_, b_) in enumerate(StratifiedKFold(cv, shuffle=True, random_state=seed).split(Ftr, ytr)):
            oof[b_] = LogisticRegression(**CFG["LR"]).fit(Ftr[a_], ytr[a_]).decision_function(Ftr[b_]); fold_id[b_] = f
        score = []
        for w in grid:
            aps = []
            for f in range(cv):
                mk = fold_id == f
                if 0 < ytr[mk].sum() < mk.sum():
                    aps.append(average_precision_score(ytr[mk], w * _rank(s_tr[mk]) + (1 - w) * _rank(oof[mk])))
            score.append(np.mean(aps) if aps else -1)
        w = grid[int(np.argmax(score))]
    else:
        w = 0.5
    lr = LogisticRegression(**CFG["LR"]).fit(Ftr, ytr).decision_function(Fte)
    return w * _rank(s_te) + (1 - w) * _rank(lr), w


def anchor_lr(Xtr, ytr, off_tr, Xte, off_te, lam):
    """LR với offset = logit nguồn; tối thiểu hoá log-loss + lam/2·||δ||² (chặn không phạt)."""
    from scipy.optimize import minimize
    n, d = Xtr.shape

    def f(theta):
        b, w = theta[0], theta[1:]
        z = off_tr + b + Xtr @ w
        loss = np.sum(np.logaddexp(0, z) - ytr * z) + 0.5 * lam * w @ w
        g = 1 / (1 + np.exp(-z)) - ytr
        return loss, np.r_[g.sum(), Xtr.T @ g + lam * w]
    th = minimize(f, np.zeros(d + 1), jac=True, method="L-BFGS-B", options=dict(maxiter=500)).x
    return off_te + th[0] + Xte @ th[1:]


def onehot_pre(X, cat):
    num = [c for c in X.columns if c not in cat]
    return ColumnTransformer([("n", make_pipeline(SimpleImputer(strategy="median"), StandardScaler()), num),
                              ("c", OneHotEncoder(handle_unknown="ignore", sparse_output=False), cat)])


def ordinal_pre(X, cat):
    num = [c for c in X.columns if c not in cat]
    return ColumnTransformer([("n", "passthrough", num),
                              ("c", OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1), cat)])


def make_tabpfn(device, seed):
    from tabpfn import TabPFNClassifier
    try:                                    # tabpfn >= 2.2: chọn đúng trọng số v2
        from tabpfn.constants import ModelVersion
        return TabPFNClassifier.create_default_for_version(ModelVersion.V2, device=device, random_state=seed,
                                                           n_estimators=CFG["TabPFN"]["n_estimators"])
    except Exception:                       # tabpfn 2.0.x – 2.1.x: mặc định là v2
        return TabPFNClassifier(device=device, random_state=seed, n_estimators=CFG["TabPFN"]["n_estimators"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ibm", required=True); ap.add_argument("--jc", required=True)
    ap.add_argument("--out", default="results/g0_23")
    ap.add_argument("--R", type=int, default=CFG["R"])
    ap.add_argument("--only", nargs="*", default=None, help="chỉ chạy các phương pháp này (vd. TabPFN)")
    ap.add_argument("--device", default="cpu")
    ap.add_argument("--targets", nargs="*", default=["A", "B"])
    ap.add_argument("--suffix", default=None, help="hậu tố tên file kết quả")
    a = ap.parse_args()
    CFG["R"] = a.R
    tag = hashlib.md5(json.dumps(CFG, sort_keys=True).encode()).hexdigest()[:8]
    methods = a.only or [m for m in TARGET_ONLY + TRANSFER if m != "TabPFN"]
    suffix = a.suffix or ("_".join(methods) if a.only else "cpu")
    os.makedirs(a.out, exist_ok=True)
    json.dump(dict(CFG, methods=methods, cfg=tag), open(f"{a.out}/config_g0_23_{tag}.json", "w"), indent=1, ensure_ascii=False)

    XA, yA, infoA = load_ibm(a.ibm); XB, yB, infoB = load_jobchange(a.jc)
    D = {"A": (XA, yA), "B": (XB, yB)}
    print("A:", infoA, "\nB:", infoB, "\ncfg:", tag, "| phương pháp:", methods, flush=True)
    SP = {d: make_splits(D[d][1], ks=tuple(CFG["ks"]), R=a.R) for d in D}
    for d in D:
        test_splits(SP[d], D[d][1])
        json.dump(SP[d], open(f"{a.out}/splits_{d}_R{a.R}.json", "w"))
    CAN = {d: canonical(D[d][0], d) for d in D}
    FULL = {d: full_features(D[d][0]) for d in D}

    rows, preds, t0 = [], [], time.time()
    out_csv = f"{a.out}/results_g0_23_{tag}_{suffix}.csv"

    def record(tgt, method, k, rep, te, score):
        y = D[tgt][1][te]
        rows.append(dict(target=tgt, method=method, family="transfer" if method in TRANSFER else "control" if method in CONTROL else "target_only",
                         k=k, rep=rep, auc_roc=roc_auc_score(y, score), pr_auc=average_precision_score(y, score),
                         n_test=len(te), pos_rate_test=y.mean(), cfg=tag))
        preds.append(pd.DataFrame(dict(target=tgt, method=method, k=k, rep=rep, id=te, y_true=y, y_score=np.round(score, 5))))

    for tgt in a.targets:
        src = "B" if tgt == "A" else "A"
        X, cat = FULL[tgt]; y = D[tgt][1]
        Cs, Ct = CAN[src], CAN[tgt]
        # mô hình nguồn: cố định cho mọi lần chia (chỉ dùng miền nguồn)
        enc_s = DomainEncoder("rank"); Zs = enc_s.fit_source(Cs)
        src_lr = LogisticRegression(**CFG["LR"]).fit(Zs, D[src][1])
        y_shuf = np.random.RandomState(CFG["SHUF_seed"]).permutation(D[src][1])
        src_shuf = LogisticRegression(**CFG["LR"]).fit(Zs, y_shuf)              # G0-4: nhãn nguồn bị xáo trộn
        for rep in range(a.R):
            sp = SP[tgt][rep]
            tr_all, te = np.array(sp["train"]), np.array(sp["test"])
            # C1 cho miền đích: fit trên đặc trưng của phần train (không dùng nhãn)
            enc_t = DomainEncoder("rank"); enc_t.fit_source(Ct.iloc[tr_all])
            Zt_all = enc_t.src.transform(Ct)                       # mọi dòng đích, cùng thang với nguồn
            s_all = src_lr.decision_function(Zt_all)                # logit của mô hình nguồn
            sh_all = src_shuf.decision_function(Zt_all)
            if "ZS" in methods:
                record(tgt, "ZS", "zero", rep, te, s_all[te])
            if "ZS_SHUF" in methods:
                record(tgt, "ZS_SHUF", "zero", rep, te, sh_all[te])
            ks = [str(k) for k in CFG["ks"] if str(k) in sp["k"]] + (["full"] if CFG["full"] else [])
            for k in ks:
                tr = tr_all if k == "full" else np.array(sp["k"][k])
                ytr = y[tr]
                need_oh = (set(TARGET_ONLY + TRANSFER + CONTROL) - {"TabPFN", "ZS", "ZS_SHUF"}) & set(methods)
                if need_oh:
                    pre = onehot_pre(X, cat).fit(X.iloc[tr])
                    Ftr, Fte = pre.transform(X.iloc[tr]), pre.transform(X.iloc[te])
                if "LR" in methods:
                    record(tgt, "LR", k, rep, te, LogisticRegression(**CFG["LR"]).fit(Ftr, ytr).predict_proba(Fte)[:, 1])
                if "RF" in methods:
                    m = RandomForestClassifier(**CFG["RF"], n_jobs=-1, random_state=rep).fit(Ftr, ytr)
                    record(tgt, "RF", k, rep, te, m.predict_proba(Fte)[:, 1])
                if "XGB" in methods:
                    record(tgt, "XGB", k, rep, te, xgb(rep).fit(Ftr, ytr).predict_proba(Fte)[:, 1])
                if "CAT" in methods:
                    record(tgt, "CAT", k, rep, te, cat_model(rep).fit(Ftr, ytr).predict_proba(Fte)[:, 1])
                if "STACK" in methods:
                    m = stack_model(rep, ytr, k == "full")
                    if m is not None:
                        record(tgt, "STACK", k, rep, te, m.fit(Ftr, ytr).predict_proba(Fte)[:, 1])
                for sfx, sc_all in (("", s_all), ("_SHUF", sh_all)):
                    if "RANKAVG" + sfx in methods:
                        v, w = rankavg_scores(Ftr, ytr, Fte, sc_all[tr], sc_all[te], rep)
                        record(tgt, "RANKAVG" + sfx, k, rep, te, v); rows[-1]["w"] = w
                    if "ANCHOR_LR" + sfx in methods:
                        Xa_tr, Xa_te = np.c_[Zt_all[tr], Ftr], np.c_[Zt_all[te], Fte]
                        record(tgt, "ANCHOR_LR" + sfx, k, rep, te,
                               anchor_lr(Xa_tr, ytr, sc_all[tr], Xa_te, sc_all[te], CFG["ANCHOR"]["lam"]))
                    if "STK_LR" + sfx in methods and sfx:
                        sc = StandardScaler().fit(sc_all[tr, None])
                        m = LogisticRegression(**CFG["LR"]).fit(np.c_[Ftr, sc.transform(sc_all[tr, None])], ytr)
                        record(tgt, "STK_LR_SHUF", k, rep, te, m.predict_proba(np.c_[Fte, sc.transform(sc_all[te, None])])[:, 1])
                if "TabPFN" in methods and not (k == "full" and len(tr) > CFG["TabPFN"]["max_train"]):
                    op = ordinal_pre(X, cat).fit(X.iloc[tr])
                    m = make_tabpfn(a.device, rep).fit(op.transform(X.iloc[tr]), ytr)
                    record(tgt, "TabPFN", k, rep, te, m.predict_proba(op.transform(X.iloc[te]))[:, 1])
                if {"STK_LR", "STK_XGB"} & set(methods):
                    sc = StandardScaler().fit(s_all[tr, None])
                    Str, Ste = np.c_[Ftr, sc.transform(s_all[tr, None])], np.c_[Fte, sc.transform(s_all[te, None])]
                    if "STK_LR" in methods:
                        record(tgt, "STK_LR", k, rep, te, LogisticRegression(**CFG["LR"]).fit(Str, ytr).predict_proba(Ste)[:, 1])
                    if "STK_XGB" in methods:
                        record(tgt, "STK_XGB", k, rep, te, xgb(rep).fit(Str, ytr).predict_proba(Ste)[:, 1])
                if "OFF_XGB" in methods:
                    m = xgb(rep).fit(Ftr, ytr, base_margin=s_all[tr])
                    record(tgt, "OFF_XGB", k, rep, te, m.predict(Fte, output_margin=True, base_margin=s_all[te]))
                if "DAUME_LR" in methods:
                    zt_tr, zt_te = Zt_all[tr], Zt_all[te]; ps = Ftr.shape[1]; c = Zs.shape[1]
                    Xs_aug = np.c_[Zs, Zs, np.zeros((len(Zs), c)), np.zeros((len(Zs), ps))]
                    Xt_aug = np.c_[zt_tr, np.zeros_like(zt_tr), zt_tr, Ftr]
                    Xte_aug = np.c_[zt_te, np.zeros_like(zt_te), zt_te, Fte]
                    m = LogisticRegression(**CFG["LR"]).fit(np.r_[Xs_aug, Xt_aug], np.r_[D[src][1], ytr])
                    record(tgt, "DAUME_LR", k, rep, te, m.predict_proba(Xte_aug)[:, 1])
            print(f"  đích {tgt} lần {rep} xong ({time.time() - t0:.0f}s)", flush=True)
            pd.DataFrame(rows).to_csv(out_csv, index=False)          # lưu dần, mất phiên vẫn giữ kết quả

    pd.DataFrame(rows).to_csv(out_csv, index=False)
    pd.concat(preds).to_csv(out_csv.replace("results_", "predictions_").replace(".csv", ".csv.gz"), index=False, compression="gzip")
    print("Đã lưu", len(rows), "dòng vào", out_csv)


if __name__ == "__main__":
    main()
