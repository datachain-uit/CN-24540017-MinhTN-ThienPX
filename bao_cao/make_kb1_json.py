"""Sinh kb1.json (Bảng 4, bảng kiểm định A5.1, bảng độ nhạy) cho cặp AB từ KB1 v2 (CPU) + TabPFN v2 (Colab)."""
import glob, json
import numpy as np, pandas as pd
from scipy import stats
G = "results/"
r = pd.concat([pd.read_csv(f) for f in [G + "kb1_v2/results_kb1v2_99d14779.csv"] + glob.glob(G + "kb1_AB/results_kb1_AB_*_TabPFN.csv")])
r["model"] = r["model"].replace({"rule_neg_experience": "rule"})
r = r.drop_duplicates(subset=["target", "setting", "features", "encoding", "model", "rep"], keep="last")
f = lambda v: f"{v:.3f}".replace(".", ",")
sg = lambda v: f"{v:+.3f}".replace(".", ",")
pv = lambda p: "< 0,001" if p < .001 else f"{p:.3f}".replace(".", ",")
NM = {"LR": "Logistic Regression (L2)", "RF": "Random Forest (mặc định)", "RF_leaf50": "Random Forest (min_samples_leaf = 50)", "XGB": "XGBoost", "TabPFN": "TabPFN v2"}
MS = ["LR", "RF", "RF_leaf50", "XGB", "TabPFN"]
def sel(t, st, ft, en, m):
    return r[(r.target == t) & (r.setting == st) & (r.features == ft) & (r.encoding == en) & (r.model == m)].sort_values("rep")
def cell(t, st, ft, en, m):
    x = sel(t, st, ft, en, m); return f"{f(x.auc_roc.mean())} ({f(x.pr_auc.mean())})"
main = []
for m in MS:
    main.append([NM[m], cell("A", "in", "full", "-", m), cell("A", "in", "canon4", "rank", m), cell("A", "B->A", "canon4", "rank", m), cell("A", "B->A", "canon4", "std", m),
                 cell("B", "in", "full", "-", m), cell("B", "in", "canon4", "rank", m), cell("B", "A->B", "canon4", "rank", m), cell("B", "A->B", "canon4", "std", m)])
main.append(["Quy tắc “− kinh nghiệm” (không học)", "–", cell("A", "in", "canon4", "-", "rule"), "–", "–", "–", cell("B", "in", "canon4", "-", "rule"), "–", "–"])
tests = []
for en, enn in [("rank", "Căn chỉnh theo miền (C1)"), ("std", "Thang đo của nguồn")]:
    rows = []
    for t, s in [("A", "B"), ("B", "A")]:
        for m in MS:
            a = sel(t, "in", "canon4", en, m).set_index("rep").auc_roc; b = sel(t, f"{s}->{t}", "canon4", en, m).set_index("rep").auc_roc
            d = (b - a).dropna().to_numpy(); J = len(d)
            se = np.sqrt((1 / J + .25) * d.var(ddof=1)); tt = d.mean() / se; pc = 2 * stats.t.sf(abs(tt), J - 1); h = stats.t.ppf(.975, J - 1) * se
            p0 = stats.ttest_rel(b.loc[a.index], a).pvalue
            rows.append(dict(en=enn, dir=f"{s}→{t}", m=NM[m], a=a.mean(), b=b.mean(), d=d.mean(), lo=d.mean() - h, hi=d.mean() + h, p0=p0, pc=pc))
    ps = np.array([x["pc"] for x in rows]); o = np.argsort(ps); n = len(ps); holm = np.empty(n); run = 0
    for i, j in enumerate(o):
        run = max(run, min(1, (n - i) * ps[j])); holm[j] = run
    for x, ph in zip(rows, holm):
        tests.append([x["en"], x["dir"], x["m"], f(x["a"]), f(x["b"]), sg(x["d"]).replace("−", "-"), f"[{sg(x['lo'])}; {sg(x['hi'])}]".replace("+", ""),
                      pv(x["p0"]), pv(x["pc"]), pv(ph), f(x["b"] / x["a"])])
sens = []
for cs, csn in [("canon4", "4 KN"), ("canon5", "5 KN (+ thâm niên)")]:
    for en, enn in [("std", "Thang đo nguồn"), ("rank", "C1")]:
        for m in ["LR", "XGB", "TabPFN"]:
            if not len(sel("A", "in", cs, en, m)):
                continue
            sens.append([csn, enn, m if m != "TabPFN" else "TabPFN v2"] + [f(sel(t, st, cs, en, m).auc_roc.mean()) for t, st in [("A", "in"), ("A", "B->A"), ("B", "in"), ("B", "A->B")]])
json.dump(dict(main=main, tests=tests, sens=sens), open("bao_cao/kb1.json", "w"), ensure_ascii=False, indent=1)
for k in (main, tests, sens):
    for x in k: print(x)
