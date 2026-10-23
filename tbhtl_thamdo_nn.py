"""
tbhtl_thamdo_nn.py — LẦN CHẠY THĂM DÒ ngày 23/10/2026 (deviations.md, mục 3). KHÔNG phải TB-HTL v0 theo
docs/tbhtl_v0_spec.md và không dùng cho kết luận. Dạng mạng nơ-ron, chạy ở mức đủ đặc trưng (L2) trước khi nhận review 22/10.

    python tbhtl_thamdo_nn.py --pair AB --data A=data/ibm.csv B=data/aug_train.csv --targets A        # chiều B→A
    python tbhtl_thamdo_eval.py results/g0_23 A                                                 # so với baseline Cổng 0

Giao thức (giống g0_pair.py): 30 lần chia dùng chung (splits.py), k ∈ {10, 20, 50, 100} mẫu có nhãn của miền đích,
cùng tập test 20%; kết quả ghi vào cùng thư mục Cổng 0 nên g0_decision.py so sánh bắt cặp theo lần chia.

Kiến trúc (C1–C4 ở mục B1.2 của báo cáo)
  C1  khái niệm chung mã hoá theo hạng trong từng miền (Enc "rank", fit trên phần train, không dùng nhãn)
  C2  nhánh chung f_s (MLP: khái niệm chung → 16 → 8 → head) + nhánh riêng tuyến tính của từng miền (toàn bộ đặc trưng
      miền, phạt L2 như LR(C = 1) của Cổng 0); logit = head(f_s) + nhánh riêng
  C3  tiền huấn luyện trên toàn bộ miền nguồn, tắt ngẫu nhiên nhánh riêng của nguồn với xác suất ρ
      để nhánh chung tự mang thông tin dự đoán
  C4  head riêng cho miền đích; khởi tạo phần nhánh chung của head từ head nguồn (bắt đầu = zero-shot);
      neo L2-SP: λ·(‖θ_s − θ_s⁰‖² + ‖w_s − w_s⁰‖²); λ ∈ {0,1; 1; 10; 100} chọn bằng kiểm định chéo phân tầng (log-loss) trên chính k mẫu

Biến thể (để trả lời H3b, H3d và đối chứng)
  TBHTL          đầy đủ
  TBHTL_NOANCHOR λ = 0 (tinh chỉnh tự do từ trọng số nguồn)                         → H3d
  TBHTL_SHARED   chỉ nhánh chung + head (bỏ nhánh riêng của đích), λ như TBHTL      → H3b
  TBHTL_SCRATCH  cùng kiến trúc, khởi tạo ngẫu nhiên, không tiền huấn luyện         → lợi ích có đến từ nguồn?
  TBHTL_SHUF     tiền huấn luyện với nhãn nguồn bị xáo trộn (đối chứng G0-4)
"""
import argparse, hashlib, json, os, time
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from sklearn.metrics import average_precision_score, roc_auc_score
from sklearn.model_selection import StratifiedKFold

from hr_data import full_features
from kb1_pair import Enc
from g0_pair import onehot_pre
from pairs import LOADERS, PAIRS, concepts, parse_data_args
from splits import make_splits, test_splits

torch.set_num_threads(2)
CFG = dict(R=30, ks=[10, 20, 50, 100], hidden=16, emb=8, rho=0.4, private="linear",
           pre=dict(epochs=20, batch=256, lr=1e-3, wd=1e-4),
           ft=dict(epochs=200, lr=1e-2, l2_private=0.5),       # 0,5·‖w‖² trên tổng log-loss ≡ LR(C = 1) như baseline Cổng 0
           lam_grid=[0.1, 1.0, 10.0, 100.0], lam_cv="log-loss, hoà thì chọn λ lớn hơn", lam_default=10.0,
           SHUF_seed=0, version="v0")
METHODS = ["TBHTL", "TBHTL_NOANCHOR", "TBHTL_SHARED", "TBHTL_SCRATCH", "TBHTL_SHUF"]


def mlp(d_in, cfg=CFG):
    return nn.Sequential(nn.Linear(d_in, cfg["hidden"]), nn.ReLU(), nn.Linear(cfg["hidden"], cfg["emb"]), nn.ReLU())


class TwoBranch(nn.Module):
    """logit = head(f_s(z)) + f_p(x).  Nhánh chung: MLP nhỏ trên khái niệm chung; nhánh riêng: tuyến tính trên toàn bộ
    đặc trưng của miền (v0 – tránh quá khớp khi k nhỏ). Nhánh riêng có thể tắt hoặc bị drop ngẫu nhiên (C3)."""

    def __init__(self, d_shared, d_private, use_private=True):
        super().__init__()
        self.fs = mlp(d_shared)
        self.head = nn.Linear(CFG["emb"], 1)
        self.use_private = use_private
        self.fp = nn.Linear(d_private, 1, bias=False) if use_private else None

    def forward(self, z, x=None, drop_p=0.0):
        out = self.head(self.fs(z)).squeeze(1)
        if self.use_private:
            hp = self.fp(x).squeeze(1)
            if self.training and drop_p > 0:               # C3: tắt nhánh riêng cho một phần mẫu
                hp = hp * (torch.rand(len(hp)) >= drop_p).float()
            out = out + hp
        return out


def T(a):
    return torch.as_tensor(np.asarray(a, dtype=np.float32))


def pretrain(Zs, Xs, ys, seed):
    """C3: tiền huấn luyện nhánh chung + nhánh riêng nguồn trên toàn bộ miền nguồn."""
    torch.manual_seed(seed); np.random.seed(seed)
    m = TwoBranch(Zs.shape[1], Xs.shape[1])
    opt = torch.optim.Adam(m.parameters(), lr=CFG["pre"]["lr"], weight_decay=CFG["pre"]["wd"])
    z, x, y = T(Zs), T(Xs), T(ys)
    pos_w = torch.tensor((1 - ys.mean()) / ys.mean())
    lossf = nn.BCEWithLogitsLoss(pos_weight=pos_w)
    n, b = len(y), CFG["pre"]["batch"]
    m.train()
    for _ in range(CFG["pre"]["epochs"]):
        perm = torch.randperm(n)
        for i in range(0, n, b):
            idx = perm[i:i + b]
            opt.zero_grad(); lossf(m(z[idx], x[idx], CFG["rho"]), y[idx]).backward(); opt.step()
    m.eval()
    with torch.no_grad():
        shared_only = m.head(m.fs(z)).squeeze(1)                                 # head chỉ với nhánh chung
    auc_shared = roc_auc_score(ys, shared_only.numpy())
    return m, auc_shared


def finetune(src, Zt, Xt, yt, lam, seed, mode):
    """mode: 'full' | 'shared' | 'scratch'.  Trả về mô hình đích đã huấn luyện trên (Zt, Xt, yt)."""
    torch.manual_seed(seed)
    use_priv = mode != "shared"
    m = TwoBranch(Zt.shape[1], Xt.shape[1], use_private=use_priv)
    anchors = []
    if mode != "scratch":
        m.fs.load_state_dict(src.fs.state_dict())
        m.head.load_state_dict(src.head.state_dict())           # C4: bắt đầu bằng dự đoán zero-shot của nhánh chung
    if use_priv:
        nn.init.zeros_(m.fp.weight)
    if mode != "scratch":
        anchors = [(p, p.detach().clone()) for p in list(m.fs.parameters()) + [m.head.weight]]
    private = use_priv
    opt = torch.optim.Adam(m.parameters(), lr=CFG["ft"]["lr"])
    z, y = T(Zt), T(yt)
    x = T(Xt) if use_priv else None
    lossf = nn.BCEWithLogitsLoss(reduction="sum")               # không trọng số lớp, giống LR của Cổng 0
    mu = CFG["ft"]["l2_private"]
    m.train()
    for _ in range(CFG["ft"]["epochs"]):
        opt.zero_grad()
        loss = lossf(m(z, x), y)
        if anchors and lam > 0:                                 # L2-SP: kéo nhánh chung và head về trọng số nguồn
            loss = loss + lam * sum(((p - p0) ** 2).sum() for p, p0 in anchors)
        if mode == "scratch":                                   # không có nguồn: L2 thường cho nhánh chung và head
            loss = loss + mu * sum((p ** 2).sum() for p in list(m.fs.parameters()) + [m.head.weight])
        if private:
            loss = loss + mu * (m.fp.weight ** 2).sum()
        loss.backward(); opt.step()
    m.eval()
    return m


def predict(m, Z, X):
    with torch.no_grad():
        return m(T(Z), T(X) if m.use_private else None).numpy()


def choose_lam(src, Zt, Xt, yt, seed, mode="full"):
    """λ* theo log-loss trên kiểm định chéo phân tầng của k mẫu (ổn định hơn AP khi ít mẫu dương);
    hoà thì chọn λ lớn hơn (giữ gần nguồn); quá ít mẫu dương → λ mặc định."""
    n_pos, n_neg = int(yt.sum()), int(len(yt) - yt.sum())
    folds = min(3, n_pos, n_neg)
    if folds < 2:
        return CFG["lam_default"]
    cv = StratifiedKFold(folds, shuffle=True, random_state=seed)
    best, best_ll = CFG["lam_default"], np.inf
    for lam in CFG["lam_grid"]:
        ll = 0.0
        for a, b in cv.split(Zt, yt):
            m = finetune(src, Zt[a], Xt[a], yt[a], lam, seed, mode)
            p = 1 / (1 + np.exp(-np.clip(predict(m, Zt[b], Xt[b]), -30, 30)))
            ll += -np.sum(yt[b] * np.log(p + 1e-9) + (1 - yt[b]) * np.log(1 - p + 1e-9))
        if ll <= best_ll + 1e-9:
            best, best_ll = lam, ll
    return best


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pair", default="AB", choices=list(PAIRS))
    ap.add_argument("--data", nargs="+", required=True)
    ap.add_argument("--targets", nargs="*", default=None)
    ap.add_argument("--R", type=int, default=CFG["R"])
    ap.add_argument("--only", nargs="*", default=METHODS)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    CFG["R"] = a.R
    P = PAIRS[a.pair]; d1, d2 = P["domains"]; paths = parse_data_args(a.data)
    a.out = a.out or ("results/g0_23" if a.pair == "AB" else f"results/g0_{a.pair}")
    a.targets = a.targets or [d1]
    tag = hashlib.md5(json.dumps(dict(CFG, pair=a.pair), sort_keys=True).encode()).hexdigest()[:8]
    os.makedirs(a.out, exist_ok=True)
    json.dump(dict(CFG, pair=a.pair, methods=a.only, cfg=tag), open(f"{a.out}/config_tbhtl_{tag}.json", "w"), indent=1)

    D = {d: LOADERS[d](paths[d])[:2] for d in (d1, d2)}
    CAN = {d: concepts(a.pair, d, D[d][0], P["main"]) for d in D}
    FULL = {d: full_features(D[d][0]) for d in D}
    rows, preds, t0 = [], [], time.time()
    out_csv = f"{a.out}/results_g0_{a.pair}_{tag}_tbhtl.csv"
    log = {}

    for tgt in a.targets:
        src = d2 if tgt == d1 else d1
        # cùng file chia với Cổng 0 (kiểm tra trùng với file đã lưu nếu có)
        SP = make_splits(D[tgt][1], ks=(10, 20, 50, 100, 200, 500), R=a.R); test_splits(SP, D[tgt][1])
        saved = f"{a.out}/splits_{tgt}_R{a.R}.json"
        if os.path.exists(saved):
            assert json.load(open(saved)) == json.loads(json.dumps(SP)), "file chia khác Cổng 0"
            print("File chia trùng với Cổng 0:", saved, flush=True)
        y = D[tgt][1]; X, cat = FULL[tgt]
        # nguồn: C1 cho khái niệm chung, one-hot cho nhánh riêng nguồn; tiền huấn luyện một lần (như mô hình nguồn của Cổng 0)
        enc_s = Enc("rank", P["binary"]); Zs = enc_s.fit_source(CAN[src])
        Xs_raw, cat_s = FULL[src]; Xs = onehot_pre(Xs_raw, cat_s).fit_transform(Xs_raw)
        src_m, auc_sh = pretrain(Zs, Xs, D[src][1].astype(float), seed=0)
        y_shuf = np.random.RandomState(CFG["SHUF_seed"]).permutation(D[src][1]).astype(float)
        src_sh, auc_sh2 = pretrain(Zs, Xs, y_shuf, seed=0) if "TBHTL_SHUF" in a.only else (None, np.nan)
        log[tgt] = dict(auc_shared_head_on_source=round(auc_sh, 4), auc_shared_head_shuffled=round(float(auc_sh2), 4))
        print(f"Tiền huấn luyện trên {src}: AUC của head chỉ dùng nhánh chung = {auc_sh:.3f} (xáo trộn: {auc_sh2:.3f}) "
              f"({time.time() - t0:.0f}s)", flush=True)
        Ct = CAN[tgt]
        for rep in range(a.R):
            sp = SP[rep]; tr_all, te = np.array(sp["train"]), np.array(sp["test"])
            enc_t = Enc("rank", P["binary"]); enc_t.fit_source(Ct.iloc[tr_all])          # C1, không dùng nhãn
            Zt = enc_t.src.transform(Ct)
            for k in [str(k) for k in CFG["ks"]]:
                tr = np.array(sp["k"][k]); ytr = y[tr].astype(float)
                pre = onehot_pre(X, cat).fit(X.iloc[tr])
                Xtr, Xte = pre.transform(X.iloc[tr]), pre.transform(X.iloc[te])
                ztr, zte = Zt[tr], Zt[te]
                lam = None

                def rec(method, m, lam_used):
                    s = predict(m, zte, Xte)
                    rows.append(dict(pair=a.pair, target=tgt, method=method,
                                     family="control" if method.endswith("_SHUF") else "transfer",
                                     k=k, rep=rep, auc_roc=roc_auc_score(y[te], s), pr_auc=average_precision_score(y[te], s),
                                     n_test=len(te), pos_rate_test=y[te].mean(), cfg=tag, lam=lam_used))
                    preds.append(pd.DataFrame(dict(target=tgt, method=method, k=k, rep=rep, id=te, y_true=y[te], y_score=np.round(s, 5))))

                if {"TBHTL", "TBHTL_SHARED"} & set(a.only):
                    lam = choose_lam(src_m, ztr, Xtr, ytr, rep)
                if "TBHTL" in a.only:
                    rec("TBHTL", finetune(src_m, ztr, Xtr, ytr, lam, rep, "full"), lam)
                if "TBHTL_NOANCHOR" in a.only:
                    rec("TBHTL_NOANCHOR", finetune(src_m, ztr, Xtr, ytr, 0.0, rep, "full"), 0.0)
                if "TBHTL_SHARED" in a.only:
                    rec("TBHTL_SHARED", finetune(src_m, ztr, Xtr, ytr, lam, rep, "shared"), lam)
                if "TBHTL_SCRATCH" in a.only:
                    rec("TBHTL_SCRATCH", finetune(src_m, ztr, Xtr, ytr, 0.0, rep, "scratch"), np.nan)
                if "TBHTL_SHUF" in a.only:
                    lam_s = choose_lam(src_sh, ztr, Xtr, ytr, rep)
                    rec("TBHTL_SHUF", finetune(src_sh, ztr, Xtr, ytr, lam_s, rep, "full"), lam_s)
            print(f"  [TB-HTL {a.pair}] đích {tgt} lần {rep} xong ({time.time() - t0:.0f}s)", flush=True)
            pd.DataFrame(rows).to_csv(out_csv, index=False)
    pd.DataFrame(rows).to_csv(out_csv, index=False)
    pd.concat(preds).to_csv(out_csv.replace("results_", "predictions_").replace(".csv", ".csv.gz"), index=False, compression="gzip")
    json.dump(log, open(f"{a.out}/tbhtl_{tag}_co_che.json", "w"), indent=1)
    print("Đã lưu", len(rows), "dòng vào", out_csv)


if __name__ == "__main__":
    main()
