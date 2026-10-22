"""
kb1_tai_dung.py — Thử dựng lại cấu hình của bảng KB1 cũ (Random Forest, mã gốc đã mất).

Bảng cũ (RF, 10 lần chia): đủ đặc trưng A 0,796 / B 0,787; 4 đặc trưng chung trong-miền A 0,581 / B 0,561;
xuyên miền B→A 0,498 ± 0,045; A→B 0,567 ± 0,008.

Ý tưởng: giữ RF mặc định và cùng 10 lần chia của KB1 v2, chỉ thay CÁCH ĐƯA 4 khái niệm chung vào mô hình,
theo các lựa chọn hay gặp trong mã "nhanh": mã hoá nhãn chuỗi theo thứ tự chữ cái (LabelEncoder / category codes),
không chặn số năm kinh nghiệm, ghép thang học vấn khác nhau. Lựa chọn nào tái tạo được cả 4 số xuyên/trong miền
thì nhiều khả năng là cấu hình cũ.

    python kb1_tai_dung.py --ibm data/kaggle/WA_Fn-UseC_-HR-Employee-Attrition.csv --jc data/kaggle/aug_train.csv
"""
import argparse
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score, average_precision_score
from hr_data import load_ibm, load_jobchange, canonical
from splits import make_splits

OLD = {"in A": 0.581, "in B": 0.561, "B->A": 0.498, "A->B": 0.567}


def codes(s):
    """Mã hoá nhãn theo thứ tự chữ cái như LabelEncoder / pd.factorize(sort=True); thiếu -> -1."""
    s = s.astype(object)
    cats = sorted(s.dropna().astype(str).unique())
    m = {c: i for i, c in enumerate(cats)}
    return s.map(lambda v: -1 if pd.isna(v) else m[str(v)]).astype(float)


def variant(name, XA, XB):
    """Trả về (CA, CB): 4 cột theo cùng thứ tự gender, education, experience, training."""
    if name == "V0 ánh xạ KB1 v2 (giá trị số, đơn vị gốc)":
        A, B = canonical(XA, "A"), canonical(XB, "B")
        return A[["male", "education", "experience", "training"]], B[["male", "education", "experience", "training"]]
    A = pd.DataFrame({"gender": codes(XA["Gender"]), "education": XA["Education"].astype(float),
                      "experience": XA["TotalWorkingYears"].astype(float), "training": XA["TrainingTimesLastYear"].astype(float)})
    B = pd.DataFrame({"gender": codes(XB["gender"]), "education": codes(XB["education_level"]),
                      "experience": codes(XB["experience"]), "training": XB["training_hours"].astype(float)})
    if name == "V1 mã hoá nhãn chuỗi cho B (học vấn + kinh nghiệm theo chữ cái)":
        return A, B
    if name == "V2 chỉ học vấn B mã hoá theo chữ cái, kinh nghiệm là số":
        B["experience"] = canonical(XB, "B")["experience"]
        return A, B
    if name == "V3 chỉ kinh nghiệm B mã hoá theo chữ cái, học vấn ánh xạ đúng":
        B["education"] = canonical(XB, "B")["education"]
        return A, B
    if name == "V4 như V0 nhưng không chặn kinh nghiệm của A (0–40 năm)":
        A, B = canonical(XA, "A"), canonical(XB, "B")
        A["experience"] = XA["TotalWorkingYears"].astype(float)
        return A[["male", "education", "experience", "training"]], B[["male", "education", "experience", "training"]]
    raise ValueError(name)


VARIANTS = ["V0 ánh xạ KB1 v2 (giá trị số, đơn vị gốc)",
            "V1 mã hoá nhãn chuỗi cho B (học vấn + kinh nghiệm theo chữ cái)",
            "V2 chỉ học vấn B mã hoá theo chữ cái, kinh nghiệm là số",
            "V3 chỉ kinh nghiệm B mã hoá theo chữ cái, học vấn ánh xạ đúng",
            "V4 như V0 nhưng không chặn kinh nghiệm của A (0–40 năm)"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ibm", required=True); ap.add_argument("--jc", required=True)
    ap.add_argument("--R", type=int, default=10); ap.add_argument("--out", default="results/kb1_tai_dung.csv")
    a = ap.parse_args()
    XA, yA, _ = load_ibm(a.ibm); XB, yB, _ = load_jobchange(a.jc)
    SP = {"A": make_splits(yA, R=a.R), "B": make_splits(yB, R=a.R)}
    D = {"A": yA, "B": yB}
    rows = []
    for v in VARIANTS:
        CA, CB = variant(v, XA, XB)
        C = {"A": CA.fillna(-1).to_numpy(), "B": CB.fillna(-1).to_numpy()}
        for tgt, src in [("A", "B"), ("B", "A")]:
            mx = RandomForestClassifier(random_state=0, n_jobs=-1).fit(C[src], D[src])   # nguồn: toàn bộ miền
            for r in range(a.R):
                tr, te = np.array(SP[tgt][r]["train"]), np.array(SP[tgt][r]["test"])
                mi = RandomForestClassifier(random_state=r, n_jobs=-1).fit(C[tgt][tr], D[tgt][tr])
                for setting, m in ((f"in {tgt}", mi), (f"{src}->{tgt}", mx)):
                    s = m.predict_proba(C[tgt][te])[:, 1]
                    rows.append(dict(variant=v, setting=setting, rep=r, auc_roc=roc_auc_score(D[tgt][te], s),
                                     pr_auc=average_precision_score(D[tgt][te], s)))
        print("xong:", v, flush=True)
    res = pd.DataFrame(rows); res.to_csv(a.out, index=False)
    t = res.groupby(["variant", "setting"]).auc_roc.agg(["mean", "std"]).round(3).unstack()
    t.columns = [f"{s} {m}" for m, s in t.columns]
    t = t[[c for k in OLD for c in t.columns if c.startswith(k + " ")]]
    t["|lệch| TB so với bảng cũ"] = np.mean([abs(t[f"{k} mean"] - v) for k, v in OLD.items()], axis=0).round(3)
    pd.set_option("display.width", 250)
    print("\nBảng cũ:", OLD)
    print(t.to_string())


if __name__ == "__main__":
    main()
