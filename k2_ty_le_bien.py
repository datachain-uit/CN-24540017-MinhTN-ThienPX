"""
k2_ty_le_bien.py — Tỷ lệ dòng ở giá trị nhỏ nhất hoặc lớn nhất của từng khái niệm K2-L0 (trước C1), không dùng nhãn.

Mã nguyên văn Phụ lục B4 review 01/11 (bản chiều), dùng cho mục 5 của bản đủ theo V3 và mục 7.3 review đó:
C1 (QuantileTransformer) đưa mọi dòng ở giá trị nhỏ nhất và lớn nhất của một khái niệm về ±5,2, nên phương sai
sau C1 (results/k2_coral/phuong_sai_khai_niem.csv, 650a8b9) tăng theo tỷ lệ các dòng này.
Khái niệm nhị phân bỏ qua (không qua C1). Điền trung vị trước khi tính, như C1. Ghi chú ở deviations.md (mục ngày 03/11 của Minh).

    python k2_ty_le_bien.py     # chạy trên kho sạch, sau commit chứa file này
    → results/k2_coral/ty_le_bien_sau_C1.csv, results/k2_coral/config_ty_le_bien.json (git_head, git_dirty, phiên bản)

Mã của GVHD; Claude (Anthropic) thêm phần mô tả này và đóng gói, khai báo ở docs/khai_bao_cong_cu.md.
"""
import json
import pandas as pd
from k2_run import PAIR_OF
from pairs import LOADERS, PAIRS, concepts
from tools.moi_truong import moi_truong, trang_thai_git
DUONG_DAN = dict(A="data/WA_Fn-UseC_-HR-Employee-Attrition.csv",
                 B="data/aug_train.csv", C="data/HR_comma_sep.csv")
json.dump(dict(**trang_thai_git(), **moi_truong()),
          open("results/k2_coral/config_ty_le_bien.json", "w"), indent=1)
XA = LOADERS["A"](DUONG_DAN["A"])[0]
rows = []
for s in ("B", "C"):
    pair = PAIR_OF[s]; P = PAIRS[pair]
    Xs = LOADERS[s](DUONG_DAN[s])[0]
    for mien, X in ((s, concepts(pair, s, Xs, P["main"])),
                    ("A", concepts(pair, "A", XA, P["main"]))):
        for c in X.columns:
            if c in P["binary"]:
                continue
            x = X[c].fillna(X[c].median())  # C1 điền trung vị trước khi biến đổi
            rows.append(dict(nguon=s, mien=mien, khai_niem=c, so_muc=x.nunique(),
                             ty_le_bien=((x == x.min()) | (x == x.max())).mean()))
pd.DataFrame(rows).to_csv("results/k2_coral/ty_le_bien_sau_C1.csv", index=False)
