"""
g0_bo_sung.py — Phần bổ sung Cổng 0 theo mục 6.4 review 22/10 (M1, M7, M8 review 18/10); tiền đăng ký
prereg/prereg_g0_bo_sung.yaml. Không thay đổi kết luận đã chốt của Cổng 0; các phương pháp mới báo cáo cạnh kết quả gốc.

    # (1) Kiểm tra đường ống: LR, RF tính lại bằng đường ống của script phải trùng Cổng 0 đã công bố (in "ĐẠT")
    python g0_bo_sung.py moi --target A --data A=... --check
    # (2) Mức sàn: chiều B→A với nhãn đích xáo trộn (test và k mẫu), R = 5
    python g0_bo_sung.py muc_san --data A=... B=... --R 5
    # (3) Lần chạy chính (chỉ sau khi tiền đăng ký có commit_chot)
    python g0_bo_sung.py moi --target A --data A=...          # B, C, D tương tự
    python g0_bo_sung.py chi_so --du-doan <thư mục dự đoán thô> --data A=... B=... C=... D=...

Chế độ:
  moi      Phương pháp chỉ dùng đích mới cho bốn đích (G0-2): LightGBM, AdaBoost (mặc định thư viện), XGB_SMALLK
           (tham số k nhỏ của prereg_k2.yaml, chỉ k ≤ 50), PRESEL (baseline đích chọn trước bằng kiểm định chéo trên
           k mẫu, hàm preselect của k2_run.py). Cùng file chia, đặc trưng và tiền xử lý như g0_pair.py.
  chi_so   Brier, ECE, F1, G-Mean cho mọi phương pháp đã công bố của Cổng 0, tính từ dự đoán thô (du_doan_tho_gate0.zip).
  muc_san  Chiều B→A với nhãn đích xáo trộn: mọi phương pháp chỉ dùng đích và chuyển giao của Cổng 0 (trừ TabPFN)
           cùng các phương pháp mới; PR-AUC phải xấp xỉ tỷ lệ dương.
Chỉ số: PR-AUC, AUC-ROC; Brier, ECE (10 khoảng đều) trên xác suất; F1, G-Mean khi gán dương cho ceil(π̂·n) điểm cao
nhất, π̂ = tỷ lệ dương của k mẫu (hàm f1_gmean_at_prior của k2_run.py).
"""
import argparse, glob, hashlib, json, os, platform, subprocess, time, warnings
import numpy as np
import pandas as pd
import yaml
from scipy.special import expit
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, roc_auc_score
from sklearn.preprocessing import StandardScaler

import k2_run                                      # import này đặt g0_pair.TIE_RULE = "neutral" (quy tắc của K2)
import g0_pair
from g0_pair import CFG as G0, anchor_lr, cat_model, onehot_pre, rankavg_rf, rankavg_scores, stack_model, xgb
from hr_data import full_features
from k2_run import ada, brier_ece, f1_gmean_at_prior, lgbm, make_target, preselect, xgb_small
from kb1_pair import Enc
from pairs import LOADERS, PAIRS, concepts, parse_data_args
from sklearn.ensemble import RandomForestClassifier

g0_pair.TIE_RULE = "first"                         # Cổng 0 giữ quy tắc hoà cũ (deviations.md mục 10)
warnings.filterwarnings("ignore")

PREREG = "prereg/prereg_g0_bo_sung.yaml"
OUT = "results/g0_bo_sung"
SPLITS = {"A": "results/g0_23/splits_A_R30.json", "B": "results/g0_23/splits_B_R30.json",
          "C": "results/g0_AC/splits_C_R30.json", "D": "results/g0_AD/splits_D_R30.json"}
PUBLISHED = {"A": "results/g0_23/results_g0_23_6f2142bf_cpu.csv", "B": "results/g0_23/results_g0_23_6f2142bf_cpu.csv",
             "C": "results/g0_AC/results_g0_AC_49df37eb_cpu.csv", "D": "results/g0_AD/results_g0_AD_083937b0_cpu.csv"}
KS = ["10", "20", "50", "100", "200", "500", "full"]
SMALL_K = {"10", "20", "50"}
NEW = ["LightGBM", "AdaBoost", "XGB_SMALLK", "PRESEL"]
PROB = {"LR", "RF", "XGB", "CAT", "STACK", "TabPFN", "STK_LR", "STK_XGB", "STK_LR_SHUF", "DAUME_LR"} | set(NEW)
LOGIT = {"ZS", "ZS_SHUF", "ANCHOR_LR", "ANCHOR_LR_SHUF", "OFF_XGB"}           # đưa qua sigmoid trước Brier, ECE
RANK = {"RANKAVG", "RANKAVG_SHUF", "RANKAVG_RF", "RANKAVG_RF_SHUF"}           # điểm hạng: Brier, ECE không áp dụng


def env_state():
    import sklearn
    try:
        head = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
        st = subprocess.run(["git", "status", "--porcelain", "--untracked-files=no"], capture_output=True, text=True)
        git = dict(git_head=head or None, git_dirty=bool(st.stdout.strip()))
    except Exception:
        git = dict(git_head=None, git_dirty=None)
    return dict(git, python=platform.python_version(), platform=platform.platform(), machine=platform.machine(),
                numpy=np.__version__, sklearn=sklearn.__version__, pandas=pd.__version__)


def guard(main_run, allow_dirty):
    """Lần chạy với nhãn thật chỉ sau khi tiền đăng ký có commit_chot và không còn thay đổi chưa commit."""
    st = env_state()
    if main_run:
        if not str(yaml.safe_load(open(PREREG, encoding="utf-8")).get("commit_chot") or "").strip():
            raise SystemExit("prereg_g0_bo_sung.yaml chưa có commit_chot: chỉ được chạy --check hoặc muc_san")
        if st["git_dirty"] and not allow_dirty:
            raise SystemExit("Còn thay đổi chưa commit ở file đã theo dõi: commit (và push) trước lần chạy chính")
    return st


def write_config(name, extra, st):
    os.makedirs(OUT, exist_ok=True)
    cfg = dict(extra, prereg_sha256=hashlib.sha256(open(PREREG, "rb").read()).hexdigest() if os.path.exists(PREREG) else None,
               code_sha256=hashlib.sha256(open(__file__, "rb").read()).hexdigest(), **st,
               started=time.strftime("%Y-%m-%d %H:%M:%S %z"))
    json.dump(cfg, open(f"{OUT}/config_{name}.json", "w", encoding="utf-8", newline="\n"), indent=1, ensure_ascii=False)


def metrics(y, score, kind, pi_hat):
    """PR-AUC, AUC-ROC; Brier, ECE trên xác suất; F1, G-Mean theo ngưỡng tỷ lệ dương của k mẫu (không có ở zero-shot)."""
    y = np.asarray(y).astype(int); score = np.asarray(score, float)
    out = dict(pr_auc=average_precision_score(y, score), auc_roc=roc_auc_score(y, score),
               brier=np.nan, ece=np.nan, f1=np.nan, gmean=np.nan)
    if kind in ("prob", "logit"):
        p = score if kind == "prob" else expit(score)
        out["brier"], out["ece"] = brier_ece(y, p)
    if pi_hat is not None:
        out["f1"], out["gmean"] = f1_gmean_at_prior(y, score, pi_hat)
    return out


def kind_of(m):
    return "prob" if m in PROB else "logit" if m in LOGIT else "rank"


# --------------------------------------------------------------------------- chế độ "moi" (G0-2, bốn đích)
def target_only_new(X, cat, y, sp, k, rep, y_fit=None):
    """Điểm của các phương pháp mới trên tập test của một lần chia; trả {phương pháp: (điểm, ghi chú)}."""
    tr_all, te = np.array(sp["train"]), np.array(sp["test"])
    tr = tr_all if k == "full" else np.array(sp["k"][k])
    ytr = (y if y_fit is None else y_fit)[tr]
    pre = onehot_pre(X, cat).fit(X.iloc[tr])
    Ftr, Fte = pre.transform(X.iloc[tr]), pre.transform(X.iloc[te])
    out = {"LightGBM": (lgbm(rep).fit(Ftr, ytr).predict_proba(Fte)[:, 1], None),
           "AdaBoost": (ada(rep).fit(Ftr, ytr).predict_proba(Fte)[:, 1], None)}
    if k in SMALL_K:
        out["XGB_SMALLK"] = (xgb_small(rep).fit(Ftr, ytr).predict_proba(Fte)[:, 1], None)
    if k != "full":                                # PRESEL theo k mẫu; k = toàn bộ không thuộc G0-3/GO
        chosen = preselect(Ftr, ytr, rep)
        out["PRESEL"] = (make_target(chosen, rep).fit(Ftr, ytr).predict_proba(Fte)[:, 1], chosen)
    return out, tr, te, Ftr, Fte, ytr


def run_moi(a):
    st = guard(not a.check, a.allow_dirty)
    paths = parse_data_args(a.data)
    X0, y, info = LOADERS[a.target](paths[a.target])
    X, cat = full_features(X0)
    SP = json.load(open(SPLITS[a.target]))[:a.R]
    name = f"moi_{a.target}" + ("_kiem_tra" if a.check else "")
    write_config(name, dict(che_do="moi", target=a.target, R=a.R, ks=KS, check=a.check, methods=NEW), st)
    rows, t0 = [], time.time()
    for rep, sp in enumerate(SP):
        for k in KS:
            if k != "full" and k not in sp["k"]:
                continue
            if a.check:                            # chỉ LR, RF: phải trùng Cổng 0 đã công bố
                tr = np.array(sp["train"]) if k == "full" else np.array(sp["k"][k]); te = np.array(sp["test"])
                pre = onehot_pre(X, cat).fit(X.iloc[tr])
                Ftr, Fte = pre.transform(X.iloc[tr]), pre.transform(X.iloc[te])
                for m, sc in (("LR", LogisticRegression(**G0["LR"]).fit(Ftr, y[tr]).predict_proba(Fte)[:, 1]),
                              ("RF", RandomForestClassifier(**G0["RF"], n_jobs=-1, random_state=rep).fit(Ftr, y[tr]).predict_proba(Fte)[:, 1])):
                    rows.append(dict(target=a.target, method=m, k=k, rep=rep, pr_auc=average_precision_score(y[te], sc)))
                continue
            out, tr, te, *_ = target_only_new(X, cat, y, sp, k, rep)
            pi = float(y[tr].mean())
            for m, (sc, note) in out.items():
                rows.append(dict(target=a.target, method=m, family="target_only", k=k, rep=rep, n_test=len(te),
                                 pos_rate_test=float(y[te].mean()), chon=note, **metrics(y[te], sc, "prob", pi)))
        print(f"  [moi {a.target}] lần chia {rep} xong ({time.time() - t0:.0f}s)", flush=True)
    df = pd.DataFrame(rows)
    if a.check:
        ref = pd.read_csv(PUBLISHED[a.target], dtype={"k": str})
        ref = ref[(ref.target == a.target) & ref.method.isin(["LR", "RF"])][["method", "k", "rep", "pr_auc"]]
        m = df.merge(ref, on=["method", "k", "rep"], suffixes=("", "_ref"))
        dev = (m.pr_auc - m.pr_auc_ref).abs().max()
        df.to_csv(f"{OUT}/results_{name}.csv", index=False)
        print(f"Đối chiếu LR, RF với Cổng 0 (đích {a.target}): {len(m)}/{len(df)} giá trị, lệch lớn nhất {dev:.2e} →",
              "ĐẠT" if len(m) == len(df) and dev < 1e-9 else "KHÔNG ĐẠT")
        return
    df.to_csv(f"{OUT}/results_{name}.csv", index=False)
    print("Đã lưu", len(df), "dòng vào", f"{OUT}/results_{name}.csv")


# --------------------------------------------------------------------------- chế độ "chi_so" (từ dự đoán thô)
def run_chi_so(a):
    st = guard(True, a.allow_dirty)
    paths = parse_data_args(a.data)
    Y = {d: LOADERS[d](p)[1] for d, p in paths.items()}
    SP = {d: json.load(open(f)) for d, f in SPLITS.items()}
    files = sorted(glob.glob(os.path.join(a.du_doan, "**", "predictions_g0_*.csv.gz"), recursive=True))
    files = [f for f in files if "AC_consistent" not in f.replace("\\", "/") and "g0_AC_2d7c34f0" not in f]
    write_config("chi_so", dict(che_do="chi_so", files=[os.path.basename(f) for f in files],
                                lam_tron_du_doan="điểm lưu làm tròn 5 chữ số (g0_pair.py)"), st)
    rows = []
    for f in files:
        p = pd.read_csv(f, dtype={"k": str})
        pair = os.path.basename(f).split("_")[2]
        pair = "AB" if pair == "23" else pair
        for (tgt, m, k, rep), g in p.groupby(["target", "method", "k", "rep"]):
            if k == "zero":
                pi = None
            else:
                sp = SP[tgt][int(rep)]
                tr = sp["train"] if k == "full" else sp["k"][k]
                pi = float(np.asarray(Y[tgt])[tr].mean())
            assert np.array_equal(np.asarray(Y[tgt])[g.id.to_numpy()], g.y_true.to_numpy()), (f, tgt, m, k, rep)
            rows.append(dict(pair=pair, target=tgt, method=m, k=k, rep=int(rep), kieu_diem=kind_of(m),
                             nguon=os.path.basename(f), **metrics(g.y_true, g.y_score, kind_of(m), pi)))
        print(f"  [chi_so] {os.path.basename(f)}: {p.groupby(['target', 'method', 'k', 'rep']).ngroups} ô", flush=True)
    df = pd.DataFrame(rows)
    df.to_csv(f"{OUT}/chi_so_tu_du_doan_tho.csv", index=False)
    print("Đã lưu", len(df), "dòng vào", f"{OUT}/chi_so_tu_du_doan_tho.csv")


# --------------------------------------------------------------------------- chế độ "muc_san" (B→A, nhãn đích xáo trộn)
def run_muc_san(a):
    st = guard(False, True)
    paths = parse_data_args(a.data)
    P = PAIRS["AB"]
    (XA0, yA, _), (XB0, yB, _) = LOADERS["A"](paths["A"]), LOADERS["B"](paths["B"])
    X, cat = full_features(XA0)
    Cs, Ct = concepts("AB", "B", XB0, P["main"]), concepts("AB", "A", XA0, P["main"])
    Zs = Enc("rank", P["binary"]).fit_source(Cs)
    src_lr = LogisticRegression(**G0["LR"]).fit(Zs, yB)
    SP = json.load(open(SPLITS["A"]))[:a.R]
    write_config("muc_san_BA", dict(che_do="muc_san", chieu="B→A", R=a.R, ks=KS[:-1]), st)
    rows, t0 = [], time.time()
    for rep, sp in enumerate(SP):
        tr_all, te = np.array(sp["train"]), np.array(sp["test"])
        y_eval = yA.copy()
        y_eval[te] = np.random.RandomState(12345 + rep).permutation(yA[te])        # như k2_run.py --shuffle-target
        enc_t = Enc("rank", P["binary"]); enc_t.fit_source(Ct.iloc[tr_all])
        Zt = enc_t.src.transform(Ct); s_all = src_lr.decision_function(Zt)

        def rec(m, k, sc, pi):
            rows.append(dict(target="A", source="B", method=m, k=k, rep=rep, pos_rate_test=float(y_eval[te].mean()),
                             **metrics(y_eval[te], sc, kind_of(m), pi)))
        rec("ZS", "zero", s_all[te], None)
        for k in KS[:-1]:
            if k not in sp["k"]:
                continue
            tr = np.array(sp["k"][k])
            y_fit = yA.copy()
            y_fit[tr] = np.random.RandomState(12345 + 1000 * rep + int(k)).permutation(yA[tr])  # giữ đủ hai lớp
            ytr = y_fit[tr]; pi = float(ytr.mean())
            out, _, _, Ftr, Fte, _ = target_only_new(X, cat, yA, sp, k, rep, y_fit=y_fit)
            for m, (sc, _) in out.items():
                rec(m, k, sc, pi)
            rec("LR", k, LogisticRegression(**G0["LR"]).fit(Ftr, ytr).predict_proba(Fte)[:, 1], pi)
            rec("RF", k, RandomForestClassifier(**G0["RF"], n_jobs=-1, random_state=rep).fit(Ftr, ytr).predict_proba(Fte)[:, 1], pi)
            rec("XGB", k, xgb(rep).fit(Ftr, ytr).predict_proba(Fte)[:, 1], pi)
            rec("CAT", k, cat_model(rep).fit(Ftr, ytr).predict_proba(Fte)[:, 1], pi)
            stk = stack_model(rep, ytr, False)
            if stk is not None:
                rec("STACK", k, stk.fit(Ftr, ytr).predict_proba(Fte)[:, 1], pi)
            sc = StandardScaler().fit(s_all[tr, None])
            Str, Ste = np.c_[Ftr, sc.transform(s_all[tr, None])], np.c_[Fte, sc.transform(s_all[te, None])]
            rec("STK_LR", k, LogisticRegression(**G0["LR"]).fit(Str, ytr).predict_proba(Ste)[:, 1], pi)
            rec("STK_XGB", k, xgb(rep).fit(Str, ytr).predict_proba(Ste)[:, 1], pi)
            rec("OFF_XGB", k, xgb(rep).fit(Ftr, ytr, base_margin=s_all[tr]).predict(Fte, output_margin=True, base_margin=s_all[te]), pi)
            v, _ = rankavg_scores(Ftr, ytr, Fte, s_all[tr], s_all[te], rep); rec("RANKAVG", k, v, pi)
            for _, (v, _) in rankavg_rf(Ftr, ytr, Fte, {"": s_all}, tr, te, rep).items():
                rec("RANKAVG_RF", k, v, pi)
            rec("ANCHOR_LR", k, anchor_lr(np.c_[Zt[tr], Ftr], ytr, s_all[tr], np.c_[Zt[te], Fte], s_all[te], G0["ANCHOR"]["lam"]), pi)
            zt_tr, zt_te = Zt[tr], Zt[te]; c = Zs.shape[1]; ps = Ftr.shape[1]
            Xs_aug = np.c_[Zs, Zs, np.zeros((len(Zs), c)), np.zeros((len(Zs), ps))]
            m = LogisticRegression(**G0["LR"]).fit(np.r_[Xs_aug, np.c_[zt_tr, np.zeros_like(zt_tr), zt_tr, Ftr]], np.r_[yB, ytr])
            rec("DAUME_LR", k, m.predict_proba(np.c_[zt_te, np.zeros_like(zt_te), zt_te, Fte])[:, 1], pi)
        print(f"  [muc_san B→A] lần chia {rep} xong ({time.time() - t0:.0f}s)", flush=True)
    df = pd.DataFrame(rows)
    df.to_csv(f"{OUT}/results_muc_san_BA.csv", index=False)
    s = df.groupby("method").agg(pr_auc=("pr_auc", "mean"), ty_le_duong=("pos_rate_test", "mean"))
    print(s.round(3).to_string()); print("PR-AUC trung bình mọi phương pháp:", round(df.pr_auc.mean(), 3),
                                         "| tỷ lệ dương:", round(df.pos_rate_test.mean(), 3))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("che_do", choices=["moi", "chi_so", "muc_san"])
    ap.add_argument("--target", choices=list(SPLITS))
    ap.add_argument("--data", nargs="+", required=True)
    ap.add_argument("--du-doan", dest="du_doan", default=None)
    ap.add_argument("--R", type=int, default=30)
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--allow-dirty", action="store_true", help="chỉ để thử")
    a = ap.parse_args()
    {"moi": run_moi, "chi_so": run_chi_so, "muc_san": run_muc_san}[a.che_do](a)


if __name__ == "__main__":
    main()
