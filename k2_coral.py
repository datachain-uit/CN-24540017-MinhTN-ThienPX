"""
k2_coral.py — CORAL ở mức L0 của K2 (prereg/prereg_k2.yaml: methods.transfer_L0_only = [CORAL];
QĐ5 review 26/10 giao cho Minh; chi tiết cài đặt chốt ở deviations.md mục 24 trước khi chạy).

CORAL (Sun, Feng, Saenko, AAAI 2016, “Return of frustratingly easy domain adaptation”), đúng Thuật toán 1 của bài:
    C_S = cov(D_S) + I,  C_T = cov(D_T) + I
    D_S* = D_S · C_S^(−1/2) · C_T^(1/2)        (tẩy trắng nguồn rồi tô màu theo hiệp phương sai đích)
    huấn luyện bộ phân loại trên (D_S*, y_S), chấm điểm trực tiếp trên D_T.
Trong K2-L0:
    D_S = khái niệm chung L0 của nguồn sau C1 (giống hệt đầu vào của ZS trong k2_run.py);
    D_T = khái niệm chung L0 của IBM sau C1, C1 phía đích fit trên toàn bộ phần train của lần chia (không nhãn, giả định N9);
    C_T ước lượng trên phần train của lần chia (không dùng dòng test, không dùng nhãn đích);
    bộ phân loại = hồi quy logistic với tham số G0["LR"] như ZS.
CORAL không dùng nhãn đích nên không phụ thuộc k: ghi k = "zero" như ZS, và được so ở mọi k trong k2_eval.py.

    python k2_coral.py --data A=data/WA_Fn-UseC_-HR-Employee-Attrition.csv B=data/aug_train.csv C=data/HR_comma_sep.csv --check
        kiểm tra đường ống: thay hai ma trận căn chỉnh bằng ma trận đơn vị, điểm phải trùng ZS đã công bố trong
        results/k2_v2 ở 60/60 giá trị (2 nguồn × 30 lần chia), lệch < 1e-12. Ghi results/k2_coral/kiem_tra_zs.csv
    python k2_coral.py --data ... --shuffle-target    # mức sàn: nhãn test hoán vị (seed 12345 + r như k2_run.py)
    python k2_coral.py --data ...                     # lần chạy chính → results/k2_v2/results_k2_<tag>_CORAL.csv

Mọi lần chạy ghi git_head, git_dirty, mã băm mã nguồn, file chia, giờ bắt đầu vào file cấu hình cạnh kết quả.
Mã do Claude (Anthropic) sinh, khai báo ở docs/khai_bao_cong_cu.md.
"""
import argparse, glob, hashlib, json, os, subprocess, time
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, roc_auc_score

from k2_run import KN, PAIR_OF, PRE, SIGMOID, brier_ece
from g0_pair import CFG as G0
from kb1_pair import Enc
from pairs import LOADERS, PAIRS, concepts, parse_data_args


def git_state():
    try:
        head = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
        st = subprocess.run(["git", "status", "--porcelain", "--untracked-files=no"], capture_output=True, text=True)
        return dict(git_head=head or None, git_dirty=bool(st.stdout.strip()), git_status=st.stdout.strip())
    except Exception:
        return dict(git_head=None, git_dirty=None, git_status=None)


def mat_pow(C, p):
    """C^p cho ma trận đối xứng xác định dương (phân rã trị riêng)."""
    w, V = np.linalg.eigh(C)
    return (V * w ** p) @ V.T


def coral_matrix(Zs, Zt_pool, eps=1.0):
    """A = C_S^(−1/2) · C_T^(1/2), với C = cov + eps · I (eps = 1 như bài gốc)."""
    d = Zs.shape[1]
    Cs = np.cov(Zs, rowvar=False) + eps * np.eye(d)
    Ct = np.cov(Zt_pool, rowvar=False) + eps * np.eye(d)
    return mat_pow(Cs, -0.5) @ mat_pow(Ct, 0.5), np.linalg.norm(Cs - Ct)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", nargs="+", required=True)
    ap.add_argument("--R", type=int, default=PRE["repeats"])
    ap.add_argument("--sources", nargs="*", default=["B", "C"])
    ap.add_argument("--check", action="store_true", help="căn chỉnh = ma trận đơn vị; điểm phải trùng ZS của results/k2_v2")
    ap.add_argument("--shuffle-target", action="store_true", help="mức sàn: hoán vị nhãn test (seed 12345 + r)")
    a = ap.parse_args()
    assert not (a.check and a.shuffle_target)
    paths = parse_data_args(a.data)
    sp_txt = open(PRE["splits_file"]).read()
    assert hashlib.sha256(sp_txt.encode()).hexdigest() == PRE["splits_sha256"], "file chia khác tiền đăng ký"
    SP = json.loads(sp_txt)[:a.R]
    mode = "kiem_tra_zs" if a.check else ("xao_tron_dich" if a.shuffle_target else "chinh")
    out_dir = "results/k2_v2" if mode == "chinh" else "results/k2_coral"
    os.makedirs(out_dir, exist_ok=True)
    cfg = dict(prereg=PRE["commit_chot"], method="CORAL", level="L0", eps=1.0, R=a.R, sources=a.sources, mode=mode)
    tag = hashlib.md5(json.dumps(cfg, sort_keys=True).encode()).hexdigest()[:8]
    meta = dict(cfg, cfg=tag, splits_file=PRE["splits_file"], splits_sha256=PRE["splits_sha256"],
                prereg_file_sha256=hashlib.sha256(open("prereg/prereg_k2.yaml", "rb").read()).hexdigest(),
                code_sha256=hashlib.sha256(open(__file__, "rb").read()).hexdigest(), **git_state(),
                started=time.strftime("%Y-%m-%d %H:%M:%S %z"))
    sfx = {"chinh": "CORAL", "kiem_tra_zs": "CORAL_kiem_tra_zs", "xao_tron_dich": "CORAL_xao_tron_dich"}[mode]
    json.dump(meta, open(f"{out_dir}/config_k2_{tag}_{sfx}.json", "w"), indent=1, ensure_ascii=False)

    XA, yA, _ = LOADERS["A"](paths["A"])
    rows = []
    for s in a.sources:
        pair = PAIR_OF[s]; P = PAIRS[pair]
        Xs, ys = LOADERS[s](paths[s])[:2]
        Cs_, Ct_ = concepts(pair, s, Xs, P["main"]), concepts(pair, "A", XA, P["main"])
        assert sorted(Cs_.columns) == sorted(KN["nguon"][s]["L0"]["khai_niem_chung"]), (s, list(Cs_.columns))
        Zs = Enc("rank", P["binary"]).fit_source(Cs_)               # như k2_run.py (ZS)
        for r, sp in enumerate(SP):
            tr_all, te = np.array(sp["train"]), np.array(sp["test"])
            enc_t = Enc("rank", P["binary"]); enc_t.fit_source(Ct_.iloc[tr_all])
            Zt = enc_t.src.transform(Ct_)
            if a.check:
                A, gap = np.eye(Zs.shape[1]), np.nan
            else:
                A, gap = coral_matrix(Zs, Zt[tr_all])
            lr = LogisticRegression(**G0["LR"]).fit(Zs @ A, ys)
            z = lr.decision_function(Zt[te])
            y = yA[te].copy()
            if a.shuffle_target:
                y = np.random.RandomState(12345 + r).permutation(y)
            br, ece = brier_ece(y, SIGMOID(z))
            rows.append(dict(target="A", source=s, level="L0", group=None, method="CORAL_ID" if a.check else "CORAL", k="zero",
                             rep=r, draw=0, pr_auc=average_precision_score(y, z), auc_roc=roc_auc_score(y, z), cfg=tag,
                             brier=br, ece=ece, cov_gap=gap, n_test=len(te), pos_rate_test=float(y.mean())))
    R_ = pd.DataFrame(rows)

    if a.check:
        fs = [f for f in glob.glob("results/k2_v2/results_k2_*_cpu*.csv")]
        k2 = pd.concat([pd.read_csv(f, dtype={"k": str}) for f in fs])
        zs = k2[(k2.method == "ZS") & (k2.level == "L0")][["source", "rep", "pr_auc", "auc_roc"]].drop_duplicates(["source", "rep"])
        m = R_.merge(zs, on=["source", "rep"], suffixes=("", "_zs"))
        m["lech_pr_auc"] = (m.pr_auc - m.pr_auc_zs).abs(); m["lech_auc_roc"] = (m.auc_roc - m.auc_roc_zs).abs()
        m[["source", "rep", "pr_auc", "pr_auc_zs", "lech_pr_auc", "auc_roc", "auc_roc_zs", "lech_auc_roc"]].to_csv(
            f"{out_dir}/kiem_tra_zs.csv", index=False)
        dmax = max(m.lech_pr_auc.max(), m.lech_auc_roc.max())
        ok = len(m) == len(R_) == len(a.sources) * a.R and dmax < 1e-12
        msg = f"Kiểm tra (căn chỉnh = I): {len(m)}/{len(R_)} giá trị khớp ZS của results/k2_v2, lệch lớn nhất {dmax:.1e} -> {'ĐẠT' if ok else 'LỖI'}"
        open(f"{out_dir}/kiem_tra_zs.txt", "w").write(msg + "\n"); print(msg)
        return
    out = f"{out_dir}/results_k2_{tag}_{sfx}.csv"
    R_.to_csv(out, index=False)
    print(R_.groupby("source").agg(pr_auc=("pr_auc", "mean"), auc_roc=("auc_roc", "mean"), pos=("pos_rate_test", "mean"),
                                   cov_gap=("cov_gap", "mean"), n=("rep", "size")).round(4).to_string())
    print("Đã lưu", out)


if __name__ == "__main__":
    main()
