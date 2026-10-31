"""
k2_tach_hiep_phuong_sai.py — Tách khoảng cách hiệp phương sai mà CORAL căn chỉnh ở K2-L0 thành phần đường chéo
(chênh lệch phương sai) và ngoài đường chéo (chênh lệch tương quan). V3 và mục 7.2 review 31/10; QĐ3, V2 review 30/10.

Không dùng nhãn (chỉ đặc trưng). Mô tả, không kiểm định. Với mỗi nguồn (B, C) và mỗi lần chia r của K2:
    D_S = khái niệm chung L0 của nguồn sau C1; D_T = khái niệm chung L0 của IBM sau C1 fit trên phần train của lần chia
    (giống hệt k2_coral.py); C_S = cov(D_S) + I, C_T = cov(D_T[train]) + I; Δ = C_S − C_T
    toàn phần = ‖Δ‖_F; đường chéo = ‖diag(Δ)‖; ngoài đường chéo = ‖Δ − diag(Δ)‖_F;
    tỷ trọng đường chéo = ‖diag(Δ)‖² / ‖Δ‖_F²; kèm phương sai từng khái niệm ở hai miền.
Kiểm tra: ‖Δ‖_F trung bình phải trùng cột cov_gap của results/k2_v2/results_k2_1035e677_CORAL.csv (3,51; 21,31).

    python k2_tach_hiep_phuong_sai.py --data A=data/WA_Fn-UseC_-HR-Employee-Attrition.csv B=data/aug_train.csv C=data/HR_comma_sep.csv
Ghi results/k2_coral/tach_hiep_phuong_sai.csv (theo lần chia), tach_hiep_phuong_sai_tom_tat.csv, phuong_sai_khai_niem.csv
và config_tach_hiep_phuong_sai.json (trạng thái Git, môi trường). Mã do Claude (Anthropic) sinh, khai báo ở docs/khai_bao_cong_cu.md.
"""
import argparse, hashlib, json, os, time
import numpy as np
import pandas as pd

from k2_run import KN, PAIR_OF, PRE
from kb1_pair import Enc
from pairs import LOADERS, PAIRS, concepts, parse_data_args
from tools.moi_truong import moi_truong, trang_thai_git, sha256_lf

OUT = "results/k2_coral"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", nargs="+", required=True)
    ap.add_argument("--R", type=int, default=PRE["repeats"])
    a = ap.parse_args()
    paths = parse_data_args(a.data)
    sp_txt = open(PRE["splits_file"]).read()
    assert hashlib.sha256(sp_txt.encode()).hexdigest() == PRE["splits_sha256"], "file chia khác tiền đăng ký"
    SP = json.loads(sp_txt)[:a.R]
    os.makedirs(OUT, exist_ok=True)
    json.dump(dict(R=a.R, splits_file=PRE["splits_file"], splits_sha256=PRE["splits_sha256"], code_sha256_lf=sha256_lf(__file__),
                   **trang_thai_git(), **moi_truong(), started=time.strftime("%Y-%m-%d %H:%M:%S %z")),
              open(f"{OUT}/config_tach_hiep_phuong_sai.json", "w"), indent=1, ensure_ascii=False)
    XA = LOADERS["A"](paths["A"])[0]
    rows, var_rows = [], []
    for s in ("B", "C"):
        pair = PAIR_OF[s]; P = PAIRS[pair]
        Xs = LOADERS[s](paths[s])[0]
        Cs_, Ct_ = concepts(pair, s, Xs, P["main"]), concepts(pair, "A", XA, P["main"])
        assert sorted(Cs_.columns) == sorted(KN["nguon"][s]["L0"]["khai_niem_chung"])
        cols = list(Cs_.columns)
        enc_s = Enc("rank", P["binary"]); Zs = enc_s.fit_source(Cs_)
        order = [c for c in cols if c not in P["binary"]] + [c for c in cols if c in P["binary"]]   # thứ tự cột của ColumnTransformer
        d = Zs.shape[1]
        Cs = np.cov(Zs, rowvar=False) + np.eye(d)
        for r, sp in enumerate(SP):
            tr = np.array(sp["train"])
            enc_t = Enc("rank", P["binary"]); enc_t.fit_source(Ct_.iloc[tr])
            Zt = enc_t.src.transform(Ct_)[tr]
            Ct = np.cov(Zt, rowvar=False) + np.eye(d)
            D = Cs - Ct; dg = np.diag(D)
            tot = np.linalg.norm(D); dia = np.linalg.norm(dg); off = np.linalg.norm(D - np.diag(dg))
            rows.append(dict(source=s, rep=r, toan_phan=tot, duong_cheo=dia, ngoai_duong_cheo=off, ty_trong_duong_cheo=dia ** 2 / tot ** 2))
            for j, c in enumerate(order):
                var_rows.append(dict(source=s, rep=r, khai_niem=c, phuong_sai_nguon_cong1=Cs[j, j], phuong_sai_IBM_cong1=Ct[j, j]))
    R_ = pd.DataFrame(rows); V = pd.DataFrame(var_rows)
    R_.to_csv(f"{OUT}/tach_hiep_phuong_sai.csv", index=False)
    T = R_.groupby("source")[["toan_phan", "duong_cheo", "ngoai_duong_cheo", "ty_trong_duong_cheo"]].mean()
    T.to_csv(f"{OUT}/tach_hiep_phuong_sai_tom_tat.csv")
    V.groupby(["source", "khai_niem"])[["phuong_sai_nguon_cong1", "phuong_sai_IBM_cong1"]].mean().to_csv(f"{OUT}/phuong_sai_khai_niem.csv")
    cg = pd.read_csv("results/k2_v2/results_k2_1035e677_CORAL.csv").groupby("source").cov_gap.mean()
    print(T.round(4).to_string()); print("Kiểm tra với cov_gap của CORAL:", (T.toan_phan - cg).abs().max())


if __name__ == "__main__":
    main()
