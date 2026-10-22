"""Sinh dữ liệu bảng cho mục A5.5 (nhiều cặp miền) từ kết quả trong results/."""
import json, sys
import numpy as np, pandas as pd
sys.path.insert(0, ".")
from sklearn.metrics import roc_auc_score
from pairs import LOADERS, PAIRS, concepts, SHORT

G = "results/"
f = lambda v: "–" if pd.isna(v) else f"{v:.3f}".replace(".", ",")
fs = lambda v: (f"{v:+.3f}").replace(".", ",").replace("-", "−")
NAME = {"LR": "LR", "RF": "Random Forest", "XGB": "XGBoost", "CAT": "CatBoost", "STACK": "Stacking [5]", "TabPFN": "TabPFN v2",
        "ZS": "Zero-shot", "STK_LR": "Stacking điểm nguồn + LR", "STK_XGB": "Stacking điểm nguồn + XGBoost", "OFF_XGB": "XGBoost khởi tạo từ nguồn",
        "DAUME_LR": "Daumé + LR", "RANKAVG": "Trung bình hạng (LR)", "ANCHOR_LR": "LR neo hệ số nguồn", "RANKAVG_RF": "Trung bình hạng RF + nguồn"}
MOD = {"LR": "LR (L2)", "RF": "RF mặc định", "RF_leaf50": "RF (leaf 50)", "XGB": "XGBoost", "TabPFN": "TabPFN v2", "rule": "Quy tắc không học"}
out = {}

# ---- KB1 2×2 cho AC, AD
for pair in ["AC", "AD"]:
    P = PAIRS[pair]; d1, d2 = P["domains"]; ms = P["main"]
    r = pd.concat([pd.read_csv(x) for x in __import__("glob").glob(G + f"kb1_{pair}/results_kb1_{pair}_*.csv")])
    r = r.drop_duplicates(subset=["target", "setting", "features", "encoding", "model", "rep"], keep="last")
    def cell(tgt, st, ft, en, m):
        x = r[(r.target == tgt) & (r.setting == st) & (r.features == ft) & (r.encoding == en) & (r.model == m)]
        return f"{f(x.auc_roc.mean())} ({f(x.pr_auc.mean())})" if len(x) else "–"
    rows = []
    for m in ["LR", "RF", "RF_leaf50", "XGB", "TabPFN", "rule"]:
        if m not in set(r.model):
            continue
        row = [MOD[m]]
        for tgt, src in [(d1, d2), (d2, d1)]:
            if m == "rule":
                row += ["–", cell(tgt, "in", ms, "-", m), "–", "–"]
            else:
                row += [cell(tgt, "in", "full", "-", m), cell(tgt, "in", ms, "std", m),
                        cell(tgt, f"{src}->{tgt}", ms, "std", m), cell(tgt, f"{src}->{tgt}", ms, "rank", m)]
        rows.append(row)
    out[f"kb1_{pair}"] = rows
    # tập phụ (consistent/ext) cho LR
    sens = []
    for cs in P["sets"]:
        for en in ["std", "rank"]:
            row = [cs, en]
            for tgt, src in [(d1, d2), (d2, d1)]:
                row += [cell(tgt, "in", cs, en, "LR").split(" ")[0], cell(tgt, f"{src}->{tgt}", cs, en, "LR").split(" ")[0]]
            sens.append(row)
    out[f"sens_{pair}"] = sens

# ---- bảng ánh xạ và chiều tác động
paths = {"A": "data/WA_Fn-UseC_-HR-Employee-Attrition.csv", "C": "data/HR_comma_sep.csv",
         "D": "data/turnover.csv"}
DATA = {d: LOADERS[d](p) for d, p in paths.items()}
MAP = {"AC": {"satisfaction": ("JobSatisfaction (1–4)", "satisfaction_level (0–1)"), "evaluation": ("PerformanceRating (3–4)", "last_evaluation (0–1)"),
              "tenure": ("YearsAtCompany (năm)", "time_spend_company (năm)"), "promoted_5y": ("YearsSinceLastPromotion ≤ 5", "promotion_last_5years"),
              "pay": ("MonthlyIncome", "salary (low/medium/high)"), "overtime": ("OverTime = Yes", "average_montly_hours > 200"),
              "dept_sales": ("Department = Sales", "Department = sales"), "dept_hr": ("Department = Human Resources", "Department = hr")},
       "AD": {"male": ("Gender = Male", "gender = m"), "age": ("Age", "age"), "tenure": ("YearsAtCompany (chặn 15)", "stag / 12 (tháng → năm, chặn 15)"),
              "prof_hr": ("Department = Human Resources", "profession = HR"), "prof_sales": ("Department = Sales", "profession = Sales")}}
VN = {"satisfaction": "Mức hài lòng", "evaluation": "Đánh giá hiệu suất", "tenure": "Thâm niên", "promoted_5y": "Thăng chức trong 5 năm",
      "pay": "Mức lương", "overtime": "Làm thêm giờ", "dept_sales": "Phòng/nghề kinh doanh", "dept_hr": "Phòng/nghề nhân sự",
      "male": "Giới tính nam", "age": "Tuổi", "prof_hr": "Phòng/nghề nhân sự", "prof_sales": "Phòng/nghề kinh doanh"}
for pair in ["AC", "AD"]:
    d1, d2 = PAIRS[pair]["domains"]; ext = "ext"
    C1, C2 = concepts(pair, d1, DATA[d1][0], ext), concepts(pair, d2, DATA[d2][0], ext)
    core = list(concepts(pair, d1, DATA[d1][0], PAIRS[pair]["main"]).columns)
    rows = []
    for c in C1.columns:
        a1, a2 = roc_auc_score(DATA[d1][1], C1[c]), roc_auc_score(DATA[d2][1], C2[c])
        same = "Cùng chiều" if (a1 - .5) * (a2 - .5) > 0 else "**Ngược chiều**"
        if abs(a1 - .5) < .02 or abs(a2 - .5) < .02:
            same = "Gần như không có tín hiệu ở một miền"
        rows.append([VN[c] + ("" if c in core else " (tập mở rộng)"), MAP[pair][c][0], MAP[pair][c][1], f(a1), f(a2), same])
    out[f"map_{pair}"] = rows

# ---- Cổng 0: bảng GO cho AC, AD, AC_consistent
for key, folder, pair in [("go_AC", "g0_AC", "AC"), ("go_AD", "g0_AD", "AD"), ("go_ACc", "g0_AC_consistent", "AC")]:
    try:
        T = pd.read_csv(G + folder + "/g0_kiem_dinh_GO.csv")
    except FileNotFoundError:
        continue
    d1, d2 = PAIRS[pair]["domains"]; rows = []
    for tgt, src in [(d1, d2), (d2, d1)]:
        g = T[T.target == tgt]
        for k in [10, 20, 50]:
            gk = g[g.k == k]
            if not len(gk):
                continue
            b = gk.iloc[0]; best = gk.loc[gk.delta.idxmax()]
            rows.append([f"{src}→{tgt}", str(k), f"{NAME[b.best_target_only]} ({f(b.base_pr)})", f"{NAME[best.method]} ({f(best.method_pr)})",
                         fs(best.delta), f"[{fs(best.ci_lo)}; {fs(best.ci_hi)}]", "Có" if best.dat_GO else "Không"])
    out[key] = rows
    c = pd.read_csv(G + folder + "/g0_doi_chung_xao_tron.csv")
    out[key + "_zs"] = {t: fs(c[(c.target == t) & (c.method == "ZS")].delta.iloc[0]) for t in (d1, d2) if len(c[(c.target == t) & (c.method == "ZS")])}
    cu = pd.read_csv(G + folder + "/g0_bang_duong_cong.csv")
    out[key + "_zspr"] = {t: f(cu[(cu.target == t) & (cu.method == "ZS")].pr_auc.iloc[0]) for t in (d1, d2)}

# ---- tổng hợp nhiều cặp
S = pd.read_csv(G + "tong_hop_cap/tong_hop_theo_cap.csv")
out["synth"] = [[r.cap, r.chieu, r.nhan, f(r.in_full_LR), f(r.in_KN_LR), f(max(r.cross_std_LR, r.cross_C1_LR)), f(r.ZS_pr) + f" / {f(r.ty_le_duong)}",
                 r.chuyen_giao_tot_nhat.replace(".", ",").replace("-", "−").replace("@k=", "k = "), "GO" if r.GO else "PIVOT"] for r in S.itertuples()]
fr = open(G + "tong_hop_cap/friedman.txt").read().splitlines()[0]
out["friedman"] = fr
rk = pd.read_csv(G + "tong_hop_cap/friedman_hang.csv")
out["ranks"] = [[r.phuong_phap, r.nhom, f"{r.hang_TB:.2f}".replace(".", ",")] for r in rk.itertuples()]
json.dump(out, open("bao_cao/pairs.json", "w"), ensure_ascii=False, indent=1)
print({k: (len(v) if isinstance(v, list) else v) for k, v in out.items()})
