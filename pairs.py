"""
pairs.py — Các miền dữ liệu và cặp miền dùng trong đề tài (R3 của đánh giá 07/10/2026).

Miền
  A  IBM HR Analytics Employee Attrition & Performance — nhãn Attrition (đã nghỉ việc); dữ liệu hư cấu, 1.470 dòng
  B  HR Analytics: Job Change of Data Scientists      — nhãn target (ý định đổi việc); ứng viên khóa đào tạo, 19.158 dòng
  C  HR Analytics (HR_comma_sep.csv)                  — nhãn left (đã nghỉ việc); dữ liệu mô phỏng, 14.999 dòng
  D  Employee turnover (E. Babushkin)                  — nhãn event (đã nghỉ việc, có kiểm duyệt); dữ liệu thật, 1.129 dòng

Cặp
  AB  khác ngữ nghĩa nhãn (hành vi ↔ ý định); 4 khái niệm chung (+ thâm niên)
  AC  cùng ngữ nghĩa nhãn; nhiều khái niệm chung (hài lòng, đánh giá, thâm niên, thăng chức, lương; + làm thêm giờ, phòng ban)
  AD  cùng ngữ nghĩa nhãn, D là dữ liệu thật; 3 khái niệm chung (giới tính, tuổi, thâm niên; + nhóm nghề)

Mỗi cặp khai báo: các tập khái niệm (tập chính dùng cho Cổng 0), cột nhị phân (không chuẩn hoá thang đo),
và một quy tắc không cần học dùng làm mốc (cột, dấu).
"""
import numpy as np
import pandas as pd

from hr_data import canonical, load_ibm, load_jobchange


# --------------------------------------------------------------------------- đọc dữ liệu C và D
def _dedup(d, label):
    feats = [c for c in d.columns if c != label]
    n_raw = len(d)
    dup = d.duplicated(subset=feats, keep=False)
    conflict = int((d[dup].groupby(feats, dropna=False)[label].nunique() > 1).sum()) if dup.any() else 0
    d = d.drop_duplicates(subset=feats, keep="first").reset_index(drop=True)
    return d, {"rows_raw": n_raw, "dup_removed": n_raw - len(d), "conflict_groups": conflict}


def load_hr14999(path):
    d = pd.read_csv(path)
    d.columns = [c.strip() for c in d.columns]
    d = d.rename(columns={"sales": "Department", "average_montly_hours": "average_monthly_hours"})
    d["left"] = d["left"].astype(int)
    d, info = _dedup(d, "left")                      # protocol 6.4: loại dòng trùng trước khi chia
    y = d["left"].to_numpy()
    X = d.drop(columns=["left"])
    info.update(rows=len(d), pos=int(y.sum()))
    return X, y, info


def load_babushkin(path):
    for enc in ("utf-8", "latin-1"):
        try:
            d = pd.read_csv(path, encoding=enc)
            break
        except UnicodeDecodeError:
            continue
    for c in d.columns:
        if not pd.api.types.is_numeric_dtype(d[c]):
            d[c] = d[c].astype(str).str.strip()
    d["event"] = d["event"].astype(int)
    d, info = _dedup(d, "event")
    # Cùng một người được ghi nhiều lần (trùng mọi cột trừ 5 điểm tính cách, nhãn luôn giống nhau):
    # giữ một bản ghi/người để tránh rò rỉ giữa train và test.
    psy = ["extraversion", "independ", "selfcontrol", "anxiety", "novator"]
    key = [c for c in d.columns if c not in psy + ["event"]]
    n0 = len(d)
    d = d.drop_duplicates(subset=key, keep="first").reset_index(drop=True)
    info["person_dup_removed"] = n0 - len(d)
    y = d["event"].to_numpy()
    X = d.drop(columns=["event"])
    info.update(rows=len(d), pos=int(y.sum()))
    return X, y, info


LOADERS = {"A": load_ibm, "B": load_jobchange, "C": load_hr14999, "D": load_babushkin}
NAMES = {"A": "IBM HR (nghỉ việc, hư cấu)", "B": "Job Change (ý định đổi việc)",
         "C": "HR Analytics 14.999 (nghỉ việc, mô phỏng)", "D": "Employee turnover – Babushkin (nghỉ việc, dữ liệu thật)"}
SHORT = {"A": "IBM", "B": "Job Change", "C": "HR 14.999", "D": "Babushkin"}


def detect_domain(columns):
    """Nhận dạng miền theo tên cột (dùng trong notebook Colab)."""
    cols = set(c.strip().lstrip("﻿") for c in columns)
    if {"Attrition", "TotalWorkingYears"} <= cols:
        return "A"
    if "enrollee_id" in cols and ({"target", "job_chnge"} & cols):
        return "B"
    if {"satisfaction_level", "left"} <= cols:
        return "C"
    if {"stag", "event"} <= cols:
        return "D"
    return None


# --------------------------------------------------------------------------- khái niệm chung theo cặp
def _ab(X, dom, cset):
    out = canonical(X, dom, with_tenure=(cset == "canon5"))
    return out


def _ac(X, dom, cset):
    out = pd.DataFrame(index=X.index)
    if dom == "A":
        out["satisfaction"] = X["JobSatisfaction"].astype(float)                    # 1–4
        out["evaluation"] = X["PerformanceRating"].astype(float)                    # 3–4
        out["tenure"] = X["YearsAtCompany"].astype(float)                           # năm
        out["promoted_5y"] = (X["YearsSinceLastPromotion"] <= 5).astype(float)      # xấp xỉ "được thăng chức trong 5 năm"
        out["pay"] = X["MonthlyIncome"].astype(float)                               # thu nhập tháng (thang khác C)
        if cset == "ext":
            out["overtime"] = (X["OverTime"].astype(str) == "Yes").astype(float)
            out["dept_sales"] = (X["Department"] == "Sales").astype(float)
            out["dept_hr"] = (X["Department"] == "Human Resources").astype(float)
    else:
        out["satisfaction"] = X["satisfaction_level"].astype(float)                 # 0–1
        out["evaluation"] = X["last_evaluation"].astype(float)                      # 0–1
        out["tenure"] = X["time_spend_company"].astype(float)                       # năm
        out["promoted_5y"] = X["promotion_last_5years"].astype(float)
        out["pay"] = X["salary"].map({"low": 0, "medium": 1, "high": 2}).astype(float)  # bậc lương
        if cset == "ext":
            out["overtime"] = (X["average_monthly_hours"] > 200).astype(float)      # > 200 giờ/tháng ≈ làm thêm giờ
            out["dept_sales"] = (X["Department"] == "sales").astype(float)
            out["dept_hr"] = (X["Department"] == "hr").astype(float)
    if cset == "consistent":
        # Phân tích phụ (chọn SAU khi xem nhãn): bỏ thâm niên vì chiều tác động ngược nhau giữa A (AUC 0,35) và C (0,69)
        out = out.drop(columns=["tenure"])
    return out


def _ad(X, dom, cset):
    out = pd.DataFrame(index=X.index)
    if dom == "A":
        out["male"] = (X["Gender"].astype(str) == "Male").astype(float)
        out["age"] = X["Age"].astype(float)
        out["tenure"] = X["YearsAtCompany"].clip(upper=15).astype(float)            # D tối đa ≈ 15 năm
        if cset == "ext":
            out["prof_hr"] = (X["Department"] == "Human Resources").astype(float)
            out["prof_sales"] = (X["Department"] == "Sales").astype(float)
    else:
        out["male"] = (X["gender"] == "m").astype(float)
        out["age"] = X["age"].astype(float)
        out["tenure"] = (X["stag"] / 12).clip(upper=15).astype(float)               # stag tính theo tháng
        if cset == "ext":
            out["prof_hr"] = (X["profession"] == "HR").astype(float)
            out["prof_sales"] = (X["profession"] == "Sales").astype(float)
    return out


PAIRS = {
    "AB": dict(domains=("A", "B"), fn=_ab, sets=["canon4", "canon5"], main="canon4",
               binary=["male", "gender_other_missing"], rule=("experience", -1), label_semantics="khác (hành vi ↔ ý định)"),
    "AC": dict(domains=("A", "C"), fn=_ac, sets=["core", "consistent", "ext"], main="core",
               binary=["promoted_5y", "overtime", "dept_sales", "dept_hr"], rule=("satisfaction", -1),
               label_semantics="giống (hành vi ↔ hành vi)"),
    "AD": dict(domains=("A", "D"), fn=_ad, sets=["core", "ext"], main="core",
               binary=["male", "prof_hr", "prof_sales"], rule=("tenure", -1), label_semantics="giống (hành vi ↔ hành vi)"),
}


def concepts(pair, dom, X, cset):
    return PAIRS[pair]["fn"](X, dom, cset)


def parse_data_args(items):
    """['A=path', 'D=path'] -> {'A': 'path', 'D': 'path'}"""
    out = {}
    for it in items:
        k, v = it.split("=", 1)
        out[k.strip().upper()] = v
    return out
