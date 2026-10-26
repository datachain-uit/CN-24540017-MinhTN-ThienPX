"""
k2_quy_tac.py — Đường tham chiếu mô tả cho mức L0 của K2 (Review-2026-10-26, quyết định 1; mục 7.5).

Quy tắc một biến đã định nghĩa trong pairs.py (trường "rule" của PAIRS) và đã báo cáo ở KB1:
    nguồn B (cặp AB): điểm = −experience     (khái niệm L0 của nguồn Job Change)
    nguồn C (cặp AC): điểm = −satisfaction   (khái niệm L0 của nguồn HR 14.999)
Không học, không dùng nhãn khi tính điểm, không phụ thuộc k. Giá trị thiếu điền median của phần train.
Chỉ dùng trong bảng mô tả của mức L0: KHÔNG đưa vào họ GO, H5 hay RQ6. Ghi vào deviations.md là đường tham chiếu
thêm sau khi xem kết quả (review 26/10).

    python k2_quy_tac.py --data A=data/WA_Fn-UseC_-HR-Employee-Attrition.csv            # 30 lần chia K2
    python k2_quy_tac.py --data A=... --R 10 --out /tmp/thu                              # thử: phải trùng KB1

Kiểm tra: với --R 10 (trùng 10 lần chia của KB1), trung bình PR-AUC phải là 0,287 (−experience) và 0,189
(−satisfaction), đúng như results/kb1_v2 và results/kb1_AC.
"""
import argparse, hashlib, json, os, subprocess, time
import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score, roc_auc_score

from pairs import LOADERS, PAIRS, concepts, parse_data_args

SPLITS = "prereg/splits_A_R30_M5.json"


def git_state():
    try:
        head = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
        st = subprocess.run(["git", "status", "--porcelain", "--untracked-files=no"], capture_output=True, text=True)
        return dict(git_head=head or None, git_dirty=bool(st.stdout.strip()))
    except Exception:
        return dict(git_head=None, git_dirty=None)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", nargs="+", required=True)
    ap.add_argument("--R", type=int, default=30)
    ap.add_argument("--out", default="results/k2_quy_tac")
    a = ap.parse_args()
    paths = parse_data_args(a.data)
    XA, yA, _ = LOADERS["A"](paths["A"])
    sp_txt = open(SPLITS).read()
    SP = json.loads(sp_txt)[:a.R]
    rows = []
    for src, pair in (("B", "AB"), ("C", "AC")):
        P = PAIRS[pair]
        cot, dau = P["rule"]
        Ct = concepts(pair, "A", XA, P["main"])
        for s in SP:
            tr, te = np.array(s["train"]), np.array(s["test"])
            x = Ct[cot]
            diem = dau * x.iloc[te].fillna(x.iloc[tr].median()).to_numpy()
            rows.append(dict(target="A", source=src, level="L0", method="QUY_TAC", quy_tac=f"{'-' if dau < 0 else '+'}{cot}",
                             k="zero", rep=s["rep"], pr_auc=average_precision_score(yA[te], diem),
                             auc_roc=roc_auc_score(yA[te], diem), n_test=len(te), pos_rate_test=float(yA[te].mean())))
    out = pd.DataFrame(rows)
    os.makedirs(a.out, exist_ok=True)
    out.to_csv(f"{a.out}/quy_tac_L0_R{a.R}.csv", index=False)
    json.dump(dict(R=a.R, splits_file=SPLITS, splits_sha256=hashlib.sha256(sp_txt.encode()).hexdigest(),
                   code_sha256=hashlib.sha256(open(__file__, "rb").read()).hexdigest(), **git_state(),
                   started=time.strftime("%Y-%m-%d %H:%M:%S %z")),
              open(f"{a.out}/config_quy_tac_L0_R{a.R}.json", "w"), indent=1, ensure_ascii=False)
    print(out.groupby(["source", "quy_tac"]).agg(pr_auc=("pr_auc", "mean"), sd=("pr_auc", "std"),
                                                 auc_roc=("auc_roc", "mean"), n=("rep", "count")).round(4))


if __name__ == "__main__":
    main()
