"""
k2_khai_niem.py — Sinh danh sách khái niệm của các mức lược đồ L0, L1 cho kịch bản K2 (review 22/10, mục 6.2–6.3).

    python k2_khai_niem.py --ibm data/WA_Fn-UseC_-HR-Employee-Attrition.csv --out prereg/k2_khai_niem.json

Quy tắc (chốt trước khi chạy K2, không chọn theo hiệu năng):
  Đích A (IBM); nguồn B (Job Change) và C (HR 14.999), mỗi nguồn chạy riêng.
  - Khái niệm = một cột (hoặc một giá trị của cột phân loại) của IBM có trong bảng ánh xạ của ít nhất một cặp trong pairs.py.
  - Một khái niệm “có ở” bộ dữ liệu X nếu bảng ánh xạ A ↔ X có nó (ở bất kỳ tập khái niệm nào của cặp, trừ tập
    “consistent” vì tập này chọn sau khi xem nhãn).
  - L0(nguồn) : đúng tập khái niệm CHÍNH đã chốt của cặp A ↔ nguồn (B: 4 khái niệm canon4; C: 5 khái niệm core,
                gồm cả thâm niên ngược chiều).
  - L1        : các khái niệm có ở ít nhất 2 trong 4 bộ dữ liệu công khai (A, B, C, D). Đích chỉ thấy các cột IBM tương ứng.
                Phần chung với nguồn ở L1 = mọi khái niệm của cặp A ↔ nguồn nằm trong L1.
  - L2        : đủ đặc trưng (thiết lập Cổng 0, dùng làm mốc, không chạy lại).
  Mô hình chỉ dùng đích chỉ thấy các cột IBM của mức lược đồ đang xét.
"""
import argparse, hashlib, json, os
import pandas as pd

from pairs import PAIRS, concepts, load_ibm

# Cột IBM gốc tương ứng với từng khái niệm (khoá dùng để đếm số bộ dữ liệu có khái niệm)
A_KEY = {"male": "Gender", "gender_other_missing": "Gender", "education": "Education", "experience": "TotalWorkingYears",
         "training": "TrainingTimesLastYear", "tenure": "YearsAtCompany", "satisfaction": "JobSatisfaction",
         "evaluation": "PerformanceRating", "promoted_5y": "YearsSinceLastPromotion", "pay": "MonthlyIncome",
         "overtime": "OverTime", "dept_sales": "Department=Sales", "prof_sales": "Department=Sales",
         "dept_hr": "Department=Human Resources", "prof_hr": "Department=Human Resources", "age": "Age"}
SKIP_SETS = {"consistent"}


def raw_col(key):
    return key.split("=")[0]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ibm", required=True)
    ap.add_argument("--out", default="prereg/k2_khai_niem.json")
    a = ap.parse_args()
    XA = load_ibm(a.ibm)[0]

    # khái niệm của từng cặp, theo từng tập (tính thật bằng hàm ánh xạ trong pairs.py)
    sets = {}
    for pair, P in PAIRS.items():
        other = [d for d in P["domains"] if d != "A"][0]
        sets[other] = {cs: list(concepts(pair, "A", XA, cs).columns) for cs in P["sets"] if cs not in SKIP_SETS}
        sets[other]["_main"] = P["main"]
    unknown = {c for o in sets.values() for cs, cols in o.items() if cs != "_main" for c in cols} - set(A_KEY)
    assert not unknown, f"thiếu khoá IBM cho: {unknown}"

    # số bộ dữ liệu có từng khoá khái niệm
    have = {}
    for other, o in sets.items():
        for cs, cols in o.items():
            if cs == "_main":
                continue
            for c in cols:
                have.setdefault(A_KEY[c], {"A"}).add(other)
    L1_keys = sorted(k for k, ds in have.items() if len(ds) >= 2)
    L1_cols = sorted({raw_col(k) for k in L1_keys})
    only_D = sorted(k for k in L1_keys if have[k] == {"A", "D"})

    out = dict(quy_tac=__doc__.split("Quy tắc")[1].strip(), dich="A", nguon={}, L1_cot_IBM=L1_cols,
               L1_khoa=L1_keys, so_bo_du_lieu={k: sorted(v) for k, v in sorted(have.items())},
               L1_chi_nho_D=only_D, ghi_chu_D="Babushkin (D) là thăm dò (quyết định 2, review 22/10); các khoá chỉ có nhờ D được liệt kê ở L1_chi_nho_D")
    for src in ["B", "C"]:
        o = sets[src]
        main = o[o["_main"]]
        allc = sorted({c for cs, cols in o.items() if cs != "_main" for c in cols}, key=lambda c: list(A_KEY).index(c))
        l1_shared = [c for c in allc if A_KEY[c] in L1_keys]
        out["nguon"][src] = dict(
            L0=dict(khai_niem_chung=main, cot_IBM_dich_thay=sorted({raw_col(A_KEY[c]) for c in main})),
            L1=dict(khai_niem_chung=l1_shared, cot_IBM_dich_thay=L1_cols),
            L2=dict(ghi_chu="đủ đặc trưng IBM – thiết lập Cổng 0 (results/g0_23, results/g0_AC), không chạy lại"))
    s = json.dumps(out, ensure_ascii=False, indent=1, sort_keys=False)
    out["sha256_8"] = hashlib.sha256(s.encode()).hexdigest()[:8]
    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
    json.dump(out, open(a.out, "w"), ensure_ascii=False, indent=1)
    print(json.dumps({k: v for k, v in out.items() if k != "quy_tac"}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
