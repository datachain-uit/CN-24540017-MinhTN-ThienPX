"""
hr_data.py — Đọc, làm sạch và ánh xạ khái niệm chung cho hai miền nhân sự.

Miền A: IBM HR Analytics Employee Attrition & Performance (1.470 dòng, nhãn Attrition).
Miền B: HR Analytics: Job Change of Data Scientists (19.158 dòng, nhãn target).

Hỗ trợ cả file Kaggle gốc (WA_Fn-UseC_-HR-Employee-Attrition.csv, aug_train.csv)
lẫn bản sao trên GitHub (IBM/employee-attrition-aif360) và gói R dlookr (jobchange).
"""
import numpy as np
import pandas as pd

IBM_DROP = ["EmployeeCount", "Over18", "StandardHours", "EmployeeNumber"]  # hằng số hoặc ID


# --------------------------------------------------------------------------- đọc dữ liệu
def load_ibm(path):
    d = pd.read_csv(path)
    y = (d["Attrition"].astype(str).str.strip().str.lower() == "yes").astype(int).to_numpy()
    X = d.drop(columns=[c for c in IBM_DROP + ["Attrition"] if c in d.columns])
    return X.reset_index(drop=True), y, {"rows_raw": len(d), "rows": len(d), "pos": int(y.sum())}


def load_jobchange(path):
    d = pd.read_csv(path)
    d = d.rename(columns={"city_dev_index": "city_development_index", "job_chnge": "target"})
    if not pd.api.types.is_numeric_dtype(d["target"]):
        d["target"] = (d["target"].astype(str).str.lower() == "yes").astype(int)
    d["target"] = d["target"].astype(int)
    feats = [c for c in d.columns if c not in ("enrollee_id", "target")]
    n_raw = len(d)
    dup = d.duplicated(subset=feats, keep=False)
    conflict = int((d[dup].groupby(feats, dropna=False).target.nunique() > 1).sum())
    d = d.drop_duplicates(subset=feats, keep="first")            # giao thức 6.4: loại trùng trước khi chia
    y = d["target"].to_numpy()
    # Y2: city xác định hoàn toàn city_development_index -> chỉ giữ chỉ số số
    X = d.drop(columns=["enrollee_id", "target", "city"])
    info = {"rows_raw": n_raw, "dup_removed": n_raw - len(d), "conflict_groups": conflict,
            "rows": len(d), "pos": int(y.sum())}
    return X.reset_index(drop=True), y, info


# --------------------------------------------------------------------------- khái niệm chung
EDU_IBM = {1: 1, 2: 2, 3: 3, 4: 4, 5: 5}          # 1 Below College, 2 College, 3 Bachelor, 4 Master, 5 Doctor
EDU_JC = {"Primary School": 0, "High School": 1,   # High School ~ Below College (không ghép với College = 2)
          "Graduate": 3, "Masters": 4, "Phd": 5}


def _exp_years(v):
    if pd.isna(v):
        return np.nan
    v = str(v)
    return 0.0 if v == "<1" else 21.0 if v == ">20" else float(v)


def canonical(X, domain, with_tenure=False):
    """Trả về DataFrame các khái niệm chung (chưa chuẩn hoá thang đo).

    male, gender_other_missing : giới tính (nhị phân + cờ khác/thiếu)
    education                  : thang thứ bậc 0–5 (bảng EDU_*)
    experience                 : số năm kinh nghiệm, chặn trên 21
    training                   : A = số lần đào tạo năm trước; B = số giờ học (khác đơn vị, cần chuẩn hoá theo miền)
    tenure (tuỳ chọn, Y1)      : số năm tại nơi làm hiện tại, chặn 5 (A: YearsAtCompany; B: last_new_job, 'never' -> min(kinh nghiệm, 5))
    """
    out = pd.DataFrame(index=X.index)
    if domain == "A":
        g = X["Gender"].astype(str)
        out["male"] = (g == "Male").astype(float)
        out["gender_other_missing"] = 0.0
        out["education"] = X["Education"].map(EDU_IBM).astype(float)
        out["experience"] = X["TotalWorkingYears"].clip(upper=21).astype(float)
        out["training"] = X["TrainingTimesLastYear"].astype(float)
        if with_tenure:
            out["tenure"] = X["YearsAtCompany"].clip(upper=5).astype(float)
    else:
        g = X["gender"]
        out["male"] = (g == "Male").astype(float)
        out["gender_other_missing"] = (~g.isin(["Male", "Female"])).astype(float)
        out["education"] = X["education_level"].map(EDU_JC).astype(float)
        out["experience"] = X["experience"].map(_exp_years).astype(float)
        out["training"] = X["training_hours"].astype(float)
        if with_tenure:
            lnj = X["last_new_job"].astype(object)
            ten = lnj.map(lambda v: np.nan if pd.isna(v) else 5.0 if v == ">4" else np.nan if v == "never" else float(v))
            never = lnj == "never"
            ten[never] = out.loc[never, "experience"].clip(upper=5)
            out["tenure"] = ten.astype(float)
    return out


def full_features(X):
    """Đủ đặc trưng của miền: số giữ nguyên, phân loại one-hot (thiếu -> hạng mục riêng)."""
    X = X.copy()
    cat = [c for c in X.columns if not pd.api.types.is_numeric_dtype(X[c])]
    for c in cat:
        X[c] = X[c].astype(object).where(X[c].notna(), "MISSING").astype(str)
    return X, cat
