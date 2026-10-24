"""
k2_run.py — Kịch bản K2 (miền đích nghèo đặc trưng), chạy đúng tiền đăng ký prereg/prereg_k2.yaml
(commit chốt d2f1ef532e2dbc1fae4b0b3d079914b1910be1c4; bản đầu 79a0a4cdb24e8178a5e63dc3c6b013791ed0fab2),
có các sửa đổi theo review 24/10 (deviations.md mục 9–14): quy tắc hoà trung tính, mức L1_core và L2, sửa --shuffle-target,
F1 và G-Mean, ghi số giá trị hoà khi chọn w và λ_s.

    python k2_run.py --data A=data/WA_Fn-UseC_-HR-Employee-Attrition.csv B=data/aug_train.csv C=data/HR_comma_sep.csv
    python k2_run.py ... --shuffle-target          # chạy thử trên NHÃN ĐÍCH XÁO TRỘN (kiểm tra mã, đo thời gian, mức sàn M8)

Đích A (IBM); nguồn B, C riêng; mức lược đồ L0 (theo nguồn), L1 (chính, giữ Age), L1_noAge (độ nhạy),
L1_core (cột IBM của L1, tập khái niệm chung của L0) và L2 (đủ đặc trưng IBM, tập khái niệm chung của Cổng 0);
k ∈ {10, 20, 50, 100}; R = 30 lần chia × M = 5 lần rút (prereg/splits_A_R30_M5.json, kiểm tra sha256).
Mô hình chỉ dùng đích chỉ thấy cột IBM của mức lược đồ; phần chỉ dùng đích tính một lần cho mỗi bộ cột
(L1 dùng chung cho hai nguồn). TabPFN v2 chạy riêng trên Colab (--only TabPFN); CORAL ở L0 do Thiên cài (T4).
Kết quả: results/k2_v2/results_k2_<tag>_<hậu tố>.csv và dự đoán thô dạng npz (float16).
(results/k2/ giữ nguyên lần chạy theo bản chốt 23/10 – commit 48bf86a, deviations.md mục 9.)
"""
import argparse, hashlib, json, os, time, warnings
import numpy as np
import pandas as pd
import yaml
from scipy.optimize import minimize
from sklearn.ensemble import AdaBoostClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, log_loss, roc_auc_score
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier

from hr_data import full_features
from kb1_pair import Enc
import g0_pair
from g0_pair import CFG as G0, anchor_lr, cat_model, onehot_pre, pick_w, rankavg_rf, rankavg_scores, stack_model, xgb
g0_pair.TIE_RULE = "neutral"                       # K2: hoà → w gần 0,5 (deviations.md mục 10 = mục 7 của review 24/10)
from k2_khai_niem import A_KEY, raw_col
from pairs import LOADERS, PAIRS, concepts, parse_data_args

warnings.filterwarnings("ignore")
PRE = yaml.safe_load(open("prereg/prereg_k2.yaml"))
KN = json.load(open(PRE["schemas"]["file"]))
PAIR_OF = {"B": "AB", "C": "AC"}
L1_SET = {"B": "canon5", "C": "ext"}               # tập khái niệm của cặp chứa đúng danh sách L1_shared_with_source
SIGMOID = lambda z: 1 / (1 + np.exp(-np.clip(z, -30, 30)))


# --------------------------------------------------------------------------- chỉ số
def brier_ece(y, p, n_bins=10):
    y, p = np.asarray(y, float), np.asarray(p, float)
    bins = np.minimum((p * n_bins).astype(int), n_bins - 1)
    ece = sum(abs(y[bins == b].mean() - p[bins == b].mean()) * (bins == b).mean() for b in range(n_bins) if (bins == b).any())
    return np.mean((p - y) ** 2), ece


def f1_gmean_at_prior(y_te, score, pi_hat):
    """F1, G-Mean khi gán dương cho ceil(pi_hat · n) điểm cao nhất; pi_hat = tỷ lệ dương của k mẫu huấn luyện
    (không dùng nhãn test). Phụ lục B5, review 24/10."""
    y_te = np.asarray(y_te).astype(int); score = np.asarray(score, float)
    n_pred = max(1, int(np.ceil(pi_hat * len(score))))
    pred = np.zeros(len(score), int)
    pred[np.argsort(-score, kind="stable")[:n_pred]] = 1
    tp = int((pred & y_te).sum()); fp = int((pred & (1 - y_te)).sum())
    fn = int(((1 - pred) & y_te).sum()); tn = int(((1 - pred) & (1 - y_te)).sum())
    f1 = 2 * tp / (2 * tp + fp + fn) if tp else 0.0
    gm = np.sqrt(tp / (tp + fn) * tn / (tn + fp)) if (tp + fn) and (tn + fp) else 0.0
    return f1, gm


# --------------------------------------------------------------------------- mô hình chỉ dùng đích
def lgbm(seed):
    from lightgbm import LGBMClassifier
    return LGBMClassifier(random_state=seed, n_jobs=2, verbose=-1)


def ada(seed):
    return AdaBoostClassifier(random_state=seed)


def xgb_small(seed):
    p = PRE["methods"]["target_only_small_k"]["XGB"]
    return XGBClassifier(**p, eval_metric="logloss", n_jobs=2, random_state=seed, verbosity=0)


def make_target(name, seed):
    return {"LR": lambda: LogisticRegression(**G0["LR"]),
            "RF": lambda: RandomForestClassifier(**G0["RF"], n_jobs=1, random_state=seed),   # n_jobs không đổi kết quả
            "XGB": lambda: xgb(seed), "CAT": lambda: cat_model(seed), "LightGBM": lambda: lgbm(seed),
            "AdaBoost": lambda: ada(seed)}[name]()


def preselect(Ftr, ytr, seed):
    """M1: chọn trước baseline đích bằng kiểm định chéo phân tầng trên k mẫu (PR-AUC); ít mẫu dương → mặc định."""
    cand = PRE["methods"]["target_preselected"]["candidates"]
    n_pos, n_neg = int(ytr.sum()), int(len(ytr) - ytr.sum())
    folds = min(3, n_pos, n_neg)
    if folds < 2:
        return PRE["methods"]["target_preselected"]["fallback_if_folds_lt_2"]
    cv = list(StratifiedKFold(folds, shuffle=True, random_state=seed).split(Ftr, ytr))
    score = {}
    for m in cand:
        aps = []
        for a, b in cv:
            mdl = make_target(m, seed).fit(Ftr[a], ytr[a])
            aps.append(average_precision_score(ytr[b], mdl.predict_proba(Ftr[b])[:, 1]))
        score[m] = np.mean(aps)
    best = max(score.values()); tied = [m for m in cand if score[m] == best]
    fb = PRE["methods"]["target_preselected"]["fallback_if_folds_lt_2"]
    return fb if fb in tied else tied[0]                  # hoà → mô hình dự phòng (RF)


def rankavg_rf_cached(Ftr, ytr, rf_test, scores, tr, te, seed):
    """Giống hệt g0_pair.rankavg_rf (cùng fold, cùng seed, cùng lưới w) nhưng tính điểm RF ngoài-fold MỘT lần cho mọi
    nguồn dùng chung nhóm cột, và dùng lại RF cuối đã fit cho baseline RF (cùng tham số, cùng seed → cùng dự đoán)."""
    from g0_pair import _rank
    n_pos, n_neg = int(ytr.sum()), int(len(ytr) - ytr.sum())
    cv = min(3 if len(ytr) > 1000 else 5, n_pos, n_neg)
    grid = G0["RANKAVG"]["grid"]; out = {}
    if cv >= 2:
        oof = np.zeros(len(ytr)); fold_id = np.zeros(len(ytr), int)
        for f, (a_, b_) in enumerate(StratifiedKFold(cv, shuffle=True, random_state=seed).split(Ftr, ytr)):
            oof[b_] = make_target("RF", seed).fit(Ftr[a_], ytr[a_]).predict_proba(Ftr[b_])[:, 1]; fold_id[b_] = f
    for key, sc in scores.items():
        s_tr, s_te = sc[tr], sc[te]
        if cv >= 2:
            score = []
            for w in grid:
                aps = [average_precision_score(ytr[fold_id == f], w * _rank(s_tr[fold_id == f]) + (1 - w) * _rank(oof[fold_id == f]))
                       for f in range(cv) if 0 < ytr[fold_id == f].sum() < (fold_id == f).sum()]
                score.append(np.mean(aps) if aps else -1)
            w = pick_w(score, grid); n_hoa = sum(v == max(score) for v in score)
        else:
            w, n_hoa = 0.5, 0
        out[key] = (w * _rank(s_te) + (1 - w) * _rank(rf_test), w, n_hoa)
    return out


# --------------------------------------------------------------------------- TB-HTL v0 (docs/tbhtl_v0_spec.md; Phụ lục B1 review 22/10)
def tbhtl_fit(Xs, Xp, y, s, lam_s, lam_p=1.0):
    X = np.hstack([Xs, Xp]); ds, dp = Xs.shape[1], Xp.shape[1]
    pen = np.r_[np.full(ds, lam_s), np.full(dp, lam_p)]

    def f(w):
        z = w[0] + s + X @ w[1:]; g = 1 / (1 + np.exp(-z)) - y
        return np.sum(np.logaddexp(0, z) - y * z) + 0.5 * np.sum(pen * w[1:] ** 2), np.r_[g.sum(), X.T @ g + pen * w[1:]]
    return minimize(f, np.zeros(1 + ds + dp), jac=True, method="L-BFGS-B").x


def tbhtl_logit(w, Xs, Xp, s):
    return w[0] + s + np.hstack([Xs, Xp]) @ w[1:]


def choose_lam_s(Xs, Xp, y, s, seed, grid=(0.1, 1, 10, 100, 1e4)):
    n_pos = int(y.sum()); n_fold = min(3, n_pos, len(y) - n_pos)
    if n_fold < 2:
        return 1.0, 0
    cv = StratifiedKFold(n_fold, shuffle=True, random_state=seed); score = {}
    for lam in grid:                                       # log-loss trên fold kiểm định (ít hoà hơn PR-AUC khi k nhỏ)
        score[lam] = np.mean([log_loss(y[va], SIGMOID(tbhtl_logit(tbhtl_fit(Xs[tr], Xp[tr], y[tr], s[tr], lam), Xs[va], Xp[va], s[va])), labels=[0, 1])
                              for tr, va in cv.split(Xs, y)])
    best = min(score.values()); tied = [lam for lam in grid if score[lam] <= best + 1e-12]
    return max(tied), len(tied)                            # hoà → λ lớn nhất (tin nguồn); trả về cả số giá trị hoà


# --------------------------------------------------------------------------- chính
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", nargs="+", required=True)
    ap.add_argument("--R", type=int, default=PRE["repeats"]); ap.add_argument("--M", type=int, default=PRE["draws_per_split"])
    ap.add_argument("--sources", nargs="*", default=["B", "C"])
    ap.add_argument("--levels", nargs="*", default=["L0", "L1", "L1_noAge", "L1_core", "L2"])
    ap.add_argument("--shuffle-target", action="store_true", help="chạy thử trên nhãn đích xáo trộn (seed 12345)")
    ap.add_argument("--only", nargs="*", default=None, help="vd. TabPFN (Colab)")
    ap.add_argument("--device", default="cpu")
    ap.add_argument("--out", default="results/k2_v2")
    ap.add_argument("--reps", type=int, nargs=2, default=None, metavar=("TU", "DEN"), help="chỉ chạy lần chia TU..DEN-1 (chia việc cho 2 tiến trình)")
    a = ap.parse_args()
    paths = parse_data_args(a.data)
    sp_txt = open(PRE["splits_file"]).read()
    assert hashlib.sha256(sp_txt.encode()).hexdigest() == PRE["splits_sha256"], "file chia khác tiền đăng ký"
    assert hashlib.sha256(open(PRE["schemas"]["file"], "rb").read()).hexdigest().startswith("3943e157"), "file khái niệm khác tiền đăng ký"
    SP = json.loads(sp_txt)[:a.R]
    KS = [str(k) for k in PRE["k_grid"]]
    cfg = dict(prereg=PRE["commit_chot"], sua_doi=PRE["sua_doi_2410"]["phien_ban"], tie=g0_pair.TIE_RULE, R=a.R, M=a.M, sources=a.sources, levels=a.levels, shuffle_target=a.shuffle_target, only=a.only)
    tag = hashlib.md5(json.dumps(cfg, sort_keys=True).encode()).hexdigest()[:8]
    suffix = "xao_tron_dich" if a.shuffle_target else ("_".join(a.only) if a.only else "cpu")
    REPS = range(*a.reps) if a.reps else range(a.R)
    if a.reps:
        suffix += f"_rep{a.reps[0]:02d}-{a.reps[1] - 1:02d}"
    os.makedirs(a.out, exist_ok=True)
    json.dump(dict(cfg, cfg=tag, prereg_file_sha256=hashlib.sha256(open("prereg/prereg_k2.yaml", "rb").read()).hexdigest(),
                   code_sha256=hashlib.sha256(open(__file__, "rb").read()).hexdigest(), started=time.strftime("%Y-%m-%d %H:%M:%S %z")),
              open(f"{a.out}/config_k2_{tag}_{suffix}.json", "w"), indent=1, ensure_ascii=False)

    XA, yA, _ = LOADERS["A"](paths["A"])
    y_eval = yA.copy()                       # nhãn dùng để chấm điểm trên tập test
    FA, catA = full_features(XA)
    SRC = {s: LOADERS[s](paths[s])[:2] for s in a.sources}

    # ---- nhóm cột đích (phần chỉ dùng đích tính một lần cho mỗi nhóm) và các tổ hợp (nguồn, mức) dùng nhóm đó
    groups = {}
    for s in a.sources:
        for lv in a.levels:
            if lv == "L2":                                   # đủ đặc trưng IBM, cùng lần rút M = 5
                cols = list(FA.columns)
            else:
                base = "L0" if lv == "L0" else "L1"
                cols = list(KN["nguon"][s][base]["cot_IBM_dich_thay"])
                if lv == "L1_noAge":
                    cols = [c for c in cols if c != "Age"]
            gname = f"L0_{s}" if lv == "L0" else ("L1" if lv == "L1_core" else lv)   # L1_core dùng lại phần chỉ dùng đích của L1
            groups.setdefault(gname, dict(cols=cols, combos=[]))["combos"].append((s, lv))
    print({g: (len(v["cols"]), v["combos"]) for g, v in groups.items()}, flush=True)

    # ---- mô hình nguồn cho mỗi (nguồn, mức): C1 (rank) và thang nguồn (−C1); nhãn thật và xáo trộn
    SM = {}
    for s in a.sources:
        P = PAIRS[PAIR_OF[s]]; Xs, ys = SRC[s]
        for lv in a.levels:
            wide = lv in ("L1", "L1_noAge")                  # chỉ L1 và L1_noAge dùng tập khái niệm mở rộng
            cset = L1_SET[s] if wide else P["main"]
            Cs, Ct = concepts(PAIR_OF[s], s, Xs, cset), concepts(PAIR_OF[s], "A", XA, cset)
            want = KN["nguon"][s]["L1" if wide else "L0"]["khai_niem_chung"]
            assert sorted(Cs.columns) == sorted(want), (s, lv, list(Cs.columns), want)
            enc_r = Enc("rank", P["binary"]); Zr = enc_r.fit_source(Cs)
            enc_s = Enc("std", P["binary"]); Zst = enc_s.fit_source(Cs)
            ysh = np.random.RandomState(0).permutation(ys)
            covered = sorted({raw_col(A_KEY[c]) for c in Cs.columns})
            SM[(s, lv)] = dict(Ct=Ct, binary=P["binary"], covered=covered, Zs=Zr,
                               lr=LogisticRegression(**G0["LR"]).fit(Zr, ys), lr_sh=LogisticRegression(**G0["LR"]).fit(Zr, ysh),
                               ys=ys, Ct_std=enc_s.src.transform(Ct), lr_std=LogisticRegression(**G0["LR"]).fit(Zst, ys))

    rows, preds, t0 = [], {}, time.time()
    out_csv = f"{a.out}/results_k2_{tag}_{suffix}.csv"
    methods_only = set(a.only) if a.only else None

    cur = {}                                  # tỷ lệ dương của k mẫu đang xét (ngưỡng F1, G-Mean)

    def rec(src, lv, grp, method, k, r, m, te, score, prob=None, **extra):
        y = y_eval[te]
        row = dict(target="A", source=src, level=lv, group=grp, method=method, k=k, rep=r, draw=m,
                   pr_auc=average_precision_score(y, score), auc_roc=roc_auc_score(y, score), cfg=tag, **extra)
        if prob is not None:
            row["brier"], row["ece"] = brier_ece(y, prob)
        if k != "zero":                       # zero-shot không có k mẫu → không có ngưỡng theo k mẫu
            row["f1"], row["gmean"] = f1_gmean_at_prior(y, score, cur["pi"])
        rows.append(row)
        key = f"{src}|{lv}|{method}|{k}"
        preds.setdefault(key, np.full((a.R, a.M, len(te)), np.nan, np.float16))[r, m] = score

    for r in REPS:
        sp = SP[r]
        tr_all, te = np.array(sp["train"]), np.array(sp["test"])
        if a.shuffle_target:                 # kiểm tra mức sàn: xáo trộn nhãn test, giữ số mẫu dương
            y_eval[te] = np.random.RandomState(12345 + r).permutation(yA[te])
        # C1 phía đích: fit trên đặc trưng của toàn bộ phần train (không nhãn) – như Cổng 0 (giả định N9)
        T = {}
        for key, sm in SM.items():
            enc_t = Enc("rank", sm["binary"]); enc_t.fit_source(sm["Ct"].iloc[tr_all])
            Zt = enc_t.src.transform(sm["Ct"])
            T[key] = dict(Zt=Zt, s=sm["lr"].decision_function(Zt), sh=sm["lr_sh"].decision_function(Zt),
                          s_std=sm["lr_std"].decision_function(sm["Ct_std"]))
            if methods_only is None:
                rec(key[0], key[1], None, "ZS", "zero", r, 0, te, T[key]["s"][te], SIGMOID(T[key]["s"][te]))
                rec(key[0], key[1], None, "ZS_SHUF", "zero", r, 0, te, T[key]["sh"][te], SIGMOID(T[key]["sh"][te]))
        for m, draw in enumerate(sp["draws"][:a.M]):
            for k in KS:
                tr = np.array(draw[k]); ytr = yA[tr]
                if a.shuffle_target:             # xáo trộn trong k mẫu: giữ đủ hai lớp như lần rút gốc
                    ytr = np.random.RandomState(12345 + 1000 * r + 10 * m + int(k)).permutation(ytr)
                cur["pi"] = float(ytr.mean())
                for gname, g in groups.items():
                    cols = g["cols"]; Xg = FA[cols]; catg = [c for c in catA if c in cols]
                    pre = onehot_pre(Xg, catg).fit(Xg.iloc[tr])
                    Ftr, Fte = pre.transform(Xg.iloc[tr]), pre.transform(Xg.iloc[te])
                    gl = "L0" if gname.startswith("L0") else gname
                    gs = gname[-1] if gname.startswith("L0") else None
                    if methods_only and "TabPFN" in methods_only:
                        from g0_pair import make_tabpfn, ordinal_pre
                        op = ordinal_pre(Xg, catg).fit(Xg.iloc[tr])
                        pr = make_tabpfn(a.device, r).fit(op.transform(Xg.iloc[tr]), ytr).predict_proba(op.transform(Xg.iloc[te]))[:, 1]
                        rec(gs, gl, gname, "TabPFN", k, r, m, te, pr, pr)
                        continue
                    # ---- chỉ dùng đích
                    P_ = {}
                    for name in ["LR", "RF", "XGB", "CAT", "LightGBM", "AdaBoost"]:
                        P_[name] = make_target(name, r).fit(Ftr, ytr).predict_proba(Fte)[:, 1]
                        rec(gs, gl, gname, name, k, r, m, te, P_[name], P_[name])
                    st = stack_model(r, ytr, False)
                    if st is not None:
                        p = st.fit(Ftr, ytr).predict_proba(Fte)[:, 1]; rec(gs, gl, gname, "STACK", k, r, m, te, p, p)
                    if int(k) <= 50:
                        p = xgb_small(r).fit(Ftr, ytr).predict_proba(Fte)[:, 1]; rec(gs, gl, gname, "XGB_SMALLK", k, r, m, te, p, p)
                    ch = preselect(Ftr, ytr, r)
                    rec(gs, gl, gname, "PRESEL", k, r, m, te, P_[ch], P_[ch], chosen=ch)
                    # ---- chuyển giao, theo từng nguồn dùng nhóm cột này
                    sc_all = {(c, sfx): T[c][kk] for c in g["combos"] for sfx, kk in (("", "s"), ("_SHUF", "sh"))}
                    for (c, sfx), (v, w, nh) in rankavg_rf_cached(Ftr, ytr, P_["RF"], sc_all, tr, te, r).items():
                        rec(c[0], c[1], gname, "RANKAVG_RF" + sfx, k, r, m, te, v, None, w=w, n_hoa=nh)
                    for (src, lv) in g["combos"]:
                        sm, tt = SM[(src, lv)], T[(src, lv)]
                        s_all, sh_all, Zt = tt["s"], tt["sh"], tt["Zt"]
                        for sfx, sc in (("", s_all), ("_SHUF", sh_all)):
                            g0_pair.LAST_N_TIED = 0
                            v, w = rankavg_scores(Ftr, ytr, Fte, sc[tr], sc[te], r)
                            rec(src, lv, gname, "RANKAVG" + sfx, k, r, m, te, v, None, w=w, n_hoa=g0_pair.LAST_N_TIED)
                            z = anchor_lr(np.c_[Zt[tr], Ftr], ytr, sc[tr], np.c_[Zt[te], Fte], sc[te], G0["ANCHOR"]["lam"])
                            rec(src, lv, gname, "ANCHOR_LR" + sfx, k, r, m, te, z, SIGMOID(z))
                            scl = StandardScaler().fit(sc[tr, None])
                            mdl = LogisticRegression(**G0["LR"]).fit(np.c_[Ftr, scl.transform(sc[tr, None])], ytr)
                            p = mdl.predict_proba(np.c_[Fte, scl.transform(sc[te, None])])[:, 1]
                            rec(src, lv, gname, "STK_LR" + sfx, k, r, m, te, p, p)
                        scl = StandardScaler().fit(s_all[tr, None])
                        p = xgb(r).fit(np.c_[Ftr, scl.transform(s_all[tr, None])], ytr).predict_proba(np.c_[Fte, scl.transform(s_all[te, None])])[:, 1]
                        rec(src, lv, gname, "STK_XGB", k, r, m, te, p, p)
                        mx = xgb(r).fit(Ftr, ytr, base_margin=s_all[tr])
                        z = mx.predict(Fte, output_margin=True, base_margin=s_all[te]); rec(src, lv, gname, "OFF_XGB", k, r, m, te, z, SIGMOID(z))
                        Zs = sm["Zs"]; c = Zs.shape[1]; ps = Ftr.shape[1]
                        Xs_aug = np.c_[Zs, Zs, np.zeros((len(Zs), c)), np.zeros((len(Zs), ps))]
                        mdl = LogisticRegression(**G0["LR"]).fit(np.r_[Xs_aug, np.c_[Zt[tr], np.zeros_like(Zt[tr]), Zt[tr], Ftr]], np.r_[sm["ys"], ytr])
                        p = mdl.predict_proba(np.c_[Zt[te], np.zeros_like(Zt[te]), Zt[te], Fte])[:, 1]
                        rec(src, lv, gname, "DAUME_LR", k, r, m, te, p, p)
                        # ---- TB-HTL v0 và ablation (đặc tả docs/tbhtl_v0_spec.md)
                        priv = [c for c in cols if c not in sm["covered"]]
                        if priv:
                            pp = onehot_pre(FA[priv], [c for c in catA if c in priv]).fit(FA[priv].iloc[tr])
                            Xp_tr, Xp_te = pp.transform(FA[priv].iloc[tr]), pp.transform(FA[priv].iloc[te])
                        else:
                            Xp_tr, Xp_te = np.zeros((len(tr), 0)), np.zeros((len(te), 0))
                        E = np.zeros((len(tr), 0)), np.zeros((len(te), 0))
                        Zstd = sm["Ct_std"]
                        for name, (xs_tr, xs_te, xp_tr, xp_te, s_vec, lam) in {
                                "TBHTL": (Zt[tr], Zt[te], Xp_tr, Xp_te, s_all, None),
                                "TBHTL_mC1": (Zstd[tr], Zstd[te], Xp_tr, Xp_te, tt["s_std"], None),
                                "TBHTL_mC2": (Zt[tr], Zt[te], E[0], E[1], s_all, None),
                                "TBHTL_mC4": (Zt[tr], Zt[te], Xp_tr, Xp_te, s_all, 1.0),
                                "TBHTL_SHUF": (Zt[tr], Zt[te], Xp_tr, Xp_te, sh_all, None)}.items():
                            lam, nh = (lam, 0) if lam is not None else choose_lam_s(xs_tr, xp_tr, ytr, s_vec[tr], r)
                            w = tbhtl_fit(xs_tr, xp_tr, ytr, s_vec[tr], lam)
                            z = tbhtl_logit(w, xs_te, xp_te, s_vec[te])
                            rec(src, lv, gname, name, k, r, m, te, z, SIGMOID(z), lam=lam, n_hoa=nh)
        print(f"  [K2] lần chia {r} xong ({time.time() - t0:.0f}s)", flush=True)
        pd.DataFrame(rows).to_csv(out_csv, index=False)
    pd.DataFrame(rows).to_csv(out_csv, index=False)
    np.savez_compressed(out_csv.replace("results_", "predictions_").replace(".csv", ".npz"), test_idx=np.array([s["test"] for s in SP]), **preds)
    print("Đã lưu", len(rows), "dòng vào", out_csv)


if __name__ == "__main__":
    main()
