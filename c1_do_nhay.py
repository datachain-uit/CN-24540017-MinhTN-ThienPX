"""
c1_do_nhay.py — Phân tích độ nhạy của căn chỉnh C1 cho zero-shot (Review-2026-10-26, quyết định 2).

C1 (kb1_pair.Enc("rank")) dùng QuantileTransformer: với khái niệm ít bậc, giá trị nhỏ nhất và lớn nhất (có hạng
hoà) bị đẩy về ±5,2. Bản đối chứng C1_MID dùng điểm chuẩn theo hạng giữa (mid-rank) của nhóm hoà:
z = Φ⁻¹((số giá trị < v + số giá trị ≤ v) / 2n), fit trên đúng dữ liệu mà C1 fit (nguồn: toàn bộ; đích: phần train
của từng lần chia). Cột nhị phân giữ nguyên như C1. Mô hình nguồn: LR(C = 1) như Cổng 0.

    python c1_do_nhay.py --pair AB --data A=... B=... --check-zs       # ZS với C1 phải trùng Cổng 0 (lệch < 1e-9)
    python c1_do_nhay.py --pair AC --data A=... C=... --check-zs
    python c1_do_nhay.py --pair AB --data A=... B=... --shuffle-target --R 5    # mức sàn
    python c1_do_nhay.py --pair AB --data A=... B=...                  # lần chạy chính (sau khi chốt tiền đăng ký)
    python c1_do_nhay.py --pair AC --data A=... C=...

Zero-shot của K2 ở mức L0 dùng đúng tập khái niệm chính của cặp (AB: canon4; AC: core) nên trùng zero-shot của
Cổng 0 với đích A; vì vậy họ chính chỉ gồm 4 chiều của Cổng 0.
"""
import argparse, hashlib, json, os, time
import numpy as np
import pandas as pd
import yaml
from scipy.stats import norm, spearmanr
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, roc_auc_score

from g0_pair import CFG as G0
from kb1_pair import Enc
from pairs import LOADERS, PAIRS, concepts, parse_data_args

PREREG = "prereg/prereg_c1_do_nhay.yaml"
G0_DIR = {"AB": "results/g0_23", "AC": "results/g0_AC"}


class MidRank:
    """Điểm chuẩn theo hạng giữa cho cột liên tục; cột nhị phân giữ nguyên (như C1)."""

    def __init__(self, binary):
        self.binary = binary

    def fit(self, C):
        self.cols = list(C.columns)
        self.med = {c: float(np.nanmedian(C[c].to_numpy(float))) for c in self.cols}
        self.ref = {}
        for c in self.cols:
            x = C[c].to_numpy(float)
            x = np.where(np.isnan(x), self.med[c], x)
            self.ref[c] = np.sort(x)
        return self

    def transform(self, C):
        out = []
        for c in self.cols:
            x = C[c].to_numpy(float)
            x = np.where(np.isnan(x), self.med[c], x)
            if c in self.binary:
                out.append(x)
                continue
            ref = self.ref[c]; n = len(ref)
            u = (np.searchsorted(ref, x, side="left") + np.searchsorted(ref, x, side="right")) / (2.0 * n)
            out.append(norm.ppf(np.clip(u, 0.5 / n, 1 - 0.5 / n)))
        return np.column_stack(out)


def git_state():
    import subprocess
    try:
        head = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
        st = subprocess.run(["git", "status", "--porcelain", "--untracked-files=no"], capture_output=True, text=True)
        return dict(git_head=head or None, git_dirty=bool(st.stdout.strip()))
    except Exception:
        return dict(git_head=None, git_dirty=None)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pair", choices=["AB", "AC"], required=True)
    ap.add_argument("--data", nargs="+", required=True)
    ap.add_argument("--R", type=int, default=30)
    ap.add_argument("--check-zs", action="store_true")
    ap.add_argument("--shuffle-target", action="store_true")
    ap.add_argument("--allow-dirty", action="store_true", help="chỉ để thử")
    ap.add_argument("--out", default="results/c1_do_nhay")
    a = ap.parse_args()
    main_run = not (a.check_zs or a.shuffle_target)
    gs = git_state()
    if main_run:
        assert os.path.exists(PREREG), "chưa có prereg/prereg_c1_do_nhay.yaml"
        if not str(yaml.safe_load(open(PREREG)).get("commit_chot") or "").strip():
            raise SystemExit("prereg_c1_do_nhay.yaml chưa có commit_chot: chỉ được chạy --check-zs hoặc --shuffle-target")
        if gs["git_dirty"] and not a.allow_dirty:
            raise SystemExit("Còn thay đổi chưa commit ở file đã theo dõi: commit (và push) trước lần chạy chính")
    paths = parse_data_args(a.data)
    P = PAIRS[a.pair]; d1, d2 = P["domains"]
    D = {d: LOADERS[d](paths[d])[:2] for d in (d1, d2)}
    cfg = dict(pair=a.pair, R=a.R, check_zs=a.check_zs, shuffle_target=a.shuffle_target, concept_set=P["main"],
               prereg_file_sha256=hashlib.sha256(open(PREREG, "rb").read()).hexdigest() if os.path.exists(PREREG) else None)
    tag = hashlib.md5(json.dumps(cfg, sort_keys=True).encode()).hexdigest()[:8]
    suffix = "kiem_tra_zs" if a.check_zs else ("xao_tron_dich" if a.shuffle_target else "cpu")
    os.makedirs(a.out, exist_ok=True)
    json.dump(dict(cfg, cfg=tag, code_sha256=hashlib.sha256(open(__file__, "rb").read()).hexdigest(), **gs,
                   started=time.strftime("%Y-%m-%d %H:%M:%S %z")),
              open(f"{a.out}/config_c1_{a.pair}_{tag}_{suffix}.json", "w"), indent=1, ensure_ascii=False)
    rows = []
    for tgt, src in ((d1, d2), (d2, d1)):
        (Xs, ys), (Xt, yt) = D[src], D[tgt]
        Cs, Ct = concepts(a.pair, src, Xs, P["main"]), concepts(a.pair, tgt, Xt, P["main"])
        Zs = Enc("rank", P["binary"]).fit_source(Cs)                     # C1 như Cổng 0
        lr_c1 = LogisticRegression(**G0["LR"]).fit(Zs, ys)
        Ms = MidRank(P["binary"]).fit(Cs).transform(Cs)                  # C1_MID
        lr_mid = LogisticRegression(**G0["LR"]).fit(Ms, ys)
        SP = json.load(open(f"{G0_DIR[a.pair]}/splits_{tgt}_R30.json"))[:a.R]
        y_eval = yt.copy()
        for r, s in enumerate(SP):
            tr_all, te = np.array(s["train"]), np.array(s["test"])
            if a.shuffle_target:
                y_eval[te] = np.random.RandomState(12345 + r).permutation(yt[te])
            enc_t = Enc("rank", P["binary"]); enc_t.fit_source(Ct.iloc[tr_all])
            z_c1 = lr_c1.decision_function(enc_t.src.transform(Ct))[te]
            base = dict(pair=a.pair, target=tgt, source=src, rep=r, cfg=tag, n_test=len(te),
                        pos_rate_test=float(y_eval[te].mean()))
            rows.append(dict(base, method="ZS_C1", pr_auc=average_precision_score(y_eval[te], z_c1),
                             auc_roc=roc_auc_score(y_eval[te], z_c1)))
            if a.check_zs:
                continue
            Mt = MidRank(P["binary"]).fit(Ct.iloc[tr_all]).transform(Ct)
            z_mid = lr_mid.decision_function(Mt)[te]
            rho = spearmanr(z_c1, z_mid).correlation                         # không dùng nhãn
            rows.append(dict(base, method="ZS_MID", pr_auc=average_precision_score(y_eval[te], z_mid),
                             auc_roc=roc_auc_score(y_eval[te], z_mid), spearman_c1_mid=rho))
        print(f"  [C1] {src} → {tgt}: xong {len(SP)} lần chia", flush=True)
    out = pd.DataFrame(rows)
    f = f"{a.out}/results_c1_{a.pair}_{tag}_{suffix}.csv"
    out.to_csv(f, index=False)
    print("Đã lưu", len(out), "dòng vào", f)
    if a.check_zs:
        fs = [x for x in os.listdir(G0_DIR[a.pair]) if x.startswith("results_g0_") and x.endswith("cpu.csv")]
        ref = pd.concat([pd.read_csv(f"{G0_DIR[a.pair]}/{x}") for x in fs])
        ref = ref[ref.method == "ZS"][["target", "rep", "pr_auc"]]
        m = out.merge(ref, on=["target", "rep"], suffixes=("", "_ref"))
        dev = (m.pr_auc - m.pr_auc_ref).abs().max()
        print(f"Đối chiếu ZS (C1) với Cổng 0: {len(m)} cặp, lệch lớn nhất {dev:.2e} →", "ĐẠT" if dev < 1e-9 else "KHÔNG ĐẠT")


if __name__ == "__main__":
    main()
