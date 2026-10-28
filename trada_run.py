"""
trada_run.py — TrAdaBoost (Dai và cs., ICML 2007) làm baseline chuyển giao bổ sung cho Cổng 0 và K2-L0
(Review-2026-10-25, quyết định 3). Họ so sánh riêng, chốt trong prereg/prereg_trada.yaml; không thay đổi
họ Holm đã chốt của Cổng 0 và của K2.

    python trada_run.py --setting g0 --pair AB --data A=... B=...     # Cổng 0, hai chiều A→B và B→A
    python trada_run.py --setting g0 --pair AC --data A=... C=...     # Cổng 0, hai chiều A→C và C→A
    python trada_run.py --setting k2l0 --data A=... B=... C=...       # K2: đích A, mức L0, nguồn B và C, M = 5
    python trada_run.py ... --check-zs          # chỉ tính zero-shot, đối chiếu Cổng 0 / K2 (kiểm tra đường ống)
    python trada_run.py ... --shuffle-target --R 5                    # kiểm tra mức sàn, chạy trước lần chính

Không gian đặc trưng: khái niệm chung theo tập chính của cặp (AB: canon4; AC: core), căn chỉnh C1 ở cả hai miền,
tức đúng không gian của zero-shot trong Cổng 0 và K2. Bộ căn chỉnh của đích fit trên đặc trưng (không nhãn) của
phần train từng lần chia, như Cổng 0. Hai cấu hình: TRADA (khởi tạo đều – chính), TRADA_BAL (cân bằng – độ nhạy).
Chỉ chạy lần chính SAU KHI prereg/prereg_trada.yaml đã được commit.
"""
import argparse, glob, hashlib, json, os, time
import numpy as np
import pandas as pd
import yaml
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, roc_auc_score

from g0_pair import CFG as G0
from k2_run import f1_gmean_at_prior
from kb1_pair import Enc
from pairs import LOADERS, PAIRS, concepts, parse_data_args
from tradaboost import tradaboost_fit, tradaboost_score

PREREG = "prereg/prereg_trada.yaml"
G0_DIR = {"AB": "results/g0_23", "AC": "results/g0_AC"}
K2_SPLITS = "prereg/splits_A_R30_M5.json"
PAIR_OF = {"B": "AB", "C": "AC"}
INITS = {"TRADA": "uniform", "TRADA_BAL": "balanced"}


def git_state():
    """Mã commit đang checkout và cờ có thay đổi chưa commit ở file đã theo dõi (ghi vào file cấu hình)."""
    import subprocess
    try:
        head = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
        st = subprocess.run(["git", "status", "--porcelain", "--untracked-files=no"], capture_output=True, text=True)
        return dict(git_head=head or None, git_dirty=bool(st.stdout.strip()))
    except Exception:
        return dict(git_head=None, git_dirty=None)


def jobs(a, D):
    """Danh sách (đích, nguồn, cặp, file chia, các k, số lần rút)."""
    if a.setting == "g0":
        d1, d2 = PAIRS[a.pair]["domains"]
        return [(t, s, a.pair, f"{G0_DIR[a.pair]}/splits_{t}_R30.json", a.ks or ["10", "20", "50", "100", "200", "500"], 1)
                for t, s in ((d1, d2), (d2, d1))]
    sha = yaml.safe_load(open("prereg/prereg_k2.yaml"))["splits_sha256"]
    assert hashlib.sha256(open(K2_SPLITS).read().encode()).hexdigest() == sha, "file chia K2 khác tiền đăng ký"
    return [("A", s, PAIR_OF[s], K2_SPLITS, a.ks or ["10", "20", "50", "100"], a.M) for s in ("B", "C")]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--setting", choices=["g0", "k2l0"], required=True)
    ap.add_argument("--pair", choices=["AB", "AC"])
    ap.add_argument("--data", nargs="+", required=True)
    ap.add_argument("--R", type=int, default=30); ap.add_argument("--M", type=int, default=5)
    ap.add_argument("--ks", nargs="*", default=None)
    ap.add_argument("--check-zs", action="store_true")
    ap.add_argument("--shuffle-target", action="store_true")
    ap.add_argument("--out", default="results/trada")
    ap.add_argument("--allow-dirty", action="store_true", help="cho phép chạy khi còn thay đổi chưa commit (chỉ để thử)")
    a = ap.parse_args()
    assert a.setting == "k2l0" or a.pair, "--setting g0 cần --pair"
    main_run = not (a.check_zs or a.shuffle_target)
    gs = git_state()
    if main_run:
        assert os.path.exists(PREREG), "chưa có prereg/prereg_trada.yaml (phải commit trước lần chạy chính)"
        if not str(yaml.safe_load(open(PREREG)).get("commit_chot") or "").strip():
            raise SystemExit("prereg_trada.yaml chưa có commit_chot: chỉ được chạy --check-zs hoặc --shuffle-target")
        if gs["git_dirty"] and not a.allow_dirty:
            raise SystemExit("Còn thay đổi chưa commit ở file đã theo dõi: commit (và push) trước lần chạy chính")
    paths = parse_data_args(a.data)
    D = {d: LOADERS[d](p)[:2] for d, p in paths.items()}
    name = a.pair if a.setting == "g0" else "k2l0"
    cfg = dict(setting=a.setting, pair=name, R=a.R, M=a.M, ks=a.ks, inits=INITS, shuffle_target=a.shuffle_target,
               check_zs=a.check_zs, n_rounds=50, max_depth=3,
               prereg_file_sha256=hashlib.sha256(open(PREREG, "rb").read()).hexdigest() if os.path.exists(PREREG) else None)
    tag = hashlib.md5(json.dumps(cfg, sort_keys=True).encode()).hexdigest()[:8]
    suffix = "kiem_tra_zs" if a.check_zs else ("xao_tron_dich" if a.shuffle_target else "cpu")
    os.makedirs(a.out, exist_ok=True)
    json.dump(dict(cfg, cfg=tag, code_sha256=hashlib.sha256(open(__file__, "rb").read()).hexdigest(),
                   tradaboost_sha256=hashlib.sha256(open("tradaboost.py", "rb").read()).hexdigest(), **gs,
                   started=time.strftime("%Y-%m-%d %H:%M:%S %z")),
              open(f"{a.out}/config_trada_{name}_{tag}_{suffix}.json", "w"), indent=1, ensure_ascii=False)
    rows, t0 = [], time.time()

    for tgt, src, pair, sp_file, KS, M in jobs(a, D):
        P = PAIRS[pair]; (Xs, ys), (Xt, yt) = D[src], D[tgt]
        Cs, Ct = concepts(pair, src, Xs, P["main"]), concepts(pair, tgt, Xt, P["main"])
        Zs = Enc("rank", P["binary"]).fit_source(Cs)                 # nguồn: toàn bộ, như mô hình nguồn của Cổng 0
        lr_src = LogisticRegression(**G0["LR"]).fit(Zs, ys) if a.check_zs else None
        SP = json.load(open(sp_file))[:a.R]
        y_eval = yt.copy()
        level = "G0" if a.setting == "g0" else "L0"
        for r, s in enumerate(SP):
            tr_all, te = np.array(s["train"]), np.array(s["test"])
            if a.shuffle_target:
                y_eval[te] = np.random.RandomState(12345 + r).permutation(yt[te])
            enc_t = Enc("rank", P["binary"]); enc_t.fit_source(Ct.iloc[tr_all])   # C1 phía đích: không dùng nhãn
            Zt = enc_t.src.transform(Ct)
            base = dict(setting=a.setting, pair=pair, target=tgt, source=src, level=level, rep=r, cfg=tag,
                        n_test=len(te), pos_rate_test=float(y_eval[te].mean()))
            if a.check_zs:
                z = lr_src.decision_function(Zt)[te]
                rows.append(dict(base, method="ZS", k="zero", draw=0, pr_auc=average_precision_score(y_eval[te], z),
                                 auc_roc=roc_auc_score(y_eval[te], z)))
                continue
            draws = [s["k"]] if a.setting == "g0" else s["draws"][:M]
            for m, draw in enumerate(draws):
                for k in KS:
                    tr = np.array(draw[k]); ytr = yt[tr]
                    if a.shuffle_target:
                        ytr = np.random.RandomState(12345 + 1000 * r + 10 * m + int(k)).permutation(ytr)
                    for meth, init in INITS.items():
                        mdl = tradaboost_fit(Zs, ys, Zt[tr], ytr, init=init, seed=r)
                        sc = tradaboost_score(mdl, Zt[te])
                        f1, gm = f1_gmean_at_prior(y_eval[te], sc, float(ytr.mean()))
                        rows.append(dict(base, method=meth, k=k, draw=m, pr_auc=average_precision_score(y_eval[te], sc),
                                         auc_roc=roc_auc_score(y_eval[te], sc), f1=f1, gmean=gm))
            print(f"  [TRADA {name}] đích {tgt} ← nguồn {src}: lần chia {r} xong ({time.time() - t0:.0f}s)", flush=True)
    out = pd.DataFrame(rows)
    f = f"{a.out}/results_trada_{name}_{tag}_{suffix}.csv"
    out.to_csv(f, index=False)
    print("Đã lưu", len(out), "dòng vào", f)
    if a.check_zs:
        check_zs(out, a.setting, a.pair)


def check_zs(out, setting, pair):
    """Đối chiếu zero-shot vừa tính với kết quả đã công bố (Cổng 0 hoặc K2 bản chốt 23/10)."""
    if setting == "g0":
        fs = [f for f in glob.glob(f"{G0_DIR[pair]}/results_g0_*cpu.csv") if "_tie_" not in f]
        ref = pd.concat([pd.read_csv(f, dtype={"k": str}) for f in fs])
        ref = ref[ref.method == "ZS"][["target", "rep", "pr_auc"]]
        key = ["target", "rep"]
    else:
        fs = glob.glob("results/k2/results_k2_*_cpu_rep*.csv")
        ref = pd.concat([pd.read_csv(f, dtype={"k": str}) for f in fs])
        ref = ref[(ref.method == "ZS") & (ref.level == "L0")][["source", "rep", "pr_auc"]]
        key = ["source", "rep"]
    m = out.merge(ref, on=key, suffixes=("", "_ref"))
    dev = (m.pr_auc - m.pr_auc_ref).abs().max()
    print(f"Đối chiếu ZS: {len(m)} cặp giá trị, lệch tuyệt đối lớn nhất = {dev:.2e} →", "ĐẠT" if dev < 1e-9 else "KHÔNG ĐẠT")


if __name__ == "__main__":
    main()
