"""Kiểm tra sau `bash tai_lap_bang.sh`: số liệu tính lại có trùng với số trong báo cáo không.

    python kiem_tra_tai_lap.py
In OK/LỖI cho từng mục; mã thoát 1 nếu có lỗi.
"""
import glob, hashlib, json, os, sys
import pandas as pd

os.chdir(os.path.dirname(os.path.abspath(__file__)))
bad = []
def check(name, ok, detail=""):
    print(f"[{'OK ' if ok else 'LỖI'}] {name}" + (f" — {detail}" if detail else ""))
    if not ok:
        bad.append(name)

# 1. Dữ liệu gốc (nếu có)
SHA = {"WA_Fn-UseC_-HR-Employee-Attrition.csv": "a5c31e38bd7fafc9bc333884eb181b06b41b8e5e488e8f7ccb27199fb3be7659",
       "aug_train.csv": "8b78da3482032500df40d5359c36ba4a59e28ccd6fc272b050dcf6dee37f114c",
       "HR_comma_sep.csv": "2510e274a90547f34c7b0db5a4ab70282c2710eb54252f14921bf980b81a928c",
       "turnover.csv": "5098600655806f73c151b30432cf6697437928a30283e88c5c0a1cffeac65ceb"}
for f, h in SHA.items():
    p = f"data/{f}"
    if os.path.exists(p):
        check(f"SHA-256 {f}", hashlib.sha256(open(p, "rb").read()).hexdigest() == h)
    else:
        print(f"[ -- ] {f}: chưa có trong data/ (chỉ cần khi huấn luyện lại hoặc tính Bảng A5.5a–b)")

# 2. Chuỗi ô của các bảng trong báo cáo
for name, skip in [("kb1", ()), ("g0", ()), ("pairs", ("notes", "friedman"))]:
    new, ref = f"bao_cao/{name}.json", f"bao_cao/{name}_trong_bao_cao.json"
    if not os.path.exists(new):
        continue
    a, b = json.load(open(new)), json.load(open(ref))
    keys = [k for k in b if k not in skip]
    diff = [k for k in keys if a.get(k) != b.get(k)]
    if name == "pairs" and not os.path.exists("data/turnover.csv"):
        print("[ -- ] bao_cao/pairs.json: bỏ qua (chưa có dữ liệu gốc)"); continue
    check(f"Bảng trong báo cáo ({name}.json, {len(keys)} khóa)", not diff, f"khác ở {diff}" if diff else "trùng từng ô")

# 3. Kết luận Cổng 0: PIVOT ở mọi chiều của ba cặp
for d in ["g0_23", "g0_AC", "g0_AD", "g0_AC_consistent"]:
    t = open(f"results/{d}/g0_ket_luan.txt").read()
    lines = [l for l in t.splitlines() if ":" in l and not l.startswith("co_")]
    check(f"Cổng 0 {d}: PIVOT", all("PIVOT" in l for l in lines), "; ".join(lines))

# 4. KB1 v2 tái lập trên Colab (18/10): 760/760 kết quả, lệch ≤ 1e-4
a = pd.read_csv("results/kb1_v2/results_kb1v2_99d14779.csv"); b = pd.read_csv("results/kb1_v2_colab_nhom/results_kb1v2_99d14779.csv")
key = ["target", "setting", "features", "encoding", "model", "rep"]
m = a.merge(b, on=key)
dmax = max((m.auc_roc_x - m.auc_roc_y).abs().max(), (m.pr_auc_x - m.pr_auc_y).abs().max())
check("KB1 v2: bản báo cáo ↔ bản nhóm chạy trên Colab", len(m) == len(a) == 760 and dmax <= 1e-4, f"{len(m)} dòng khớp, lệch tối đa {dmax:.6f}")

# 5. Một vài con số chủ chốt trong văn bản
r = pd.concat([a, pd.read_csv("results/kb1_AB/results_kb1_AB_cf3e982a_TabPFN.csv")])
v = lambda t, s, f, e, mo: r[(r.target == t) & (r.setting == s) & (r.features == f) & (r.encoding == e) & (r.model == mo)].auc_roc.mean()
for txt, val, ref in [("LR đủ đặc trưng, đích A", v("A", "in", "full", "-", "LR"), .829),
                      ("LR B→A, C1", v("A", "B->A", "canon4", "rank", "LR"), .621),
                      ("TabPFN v2 đủ đặc trưng, đích A", v("A", "in", "full", "-", "TabPFN"), .840)]:
    check(f"B1.3: {txt} = {ref:.3f}", round(val, 3) == ref, f"{val:.4f}")
fr = open("results/tong_hop_cap/friedman.txt").read().splitlines()
check("Friedman chính: χ² = 108,19, CD = 3,10", "chi2 = 108.19" in fr[0] and "= 3.10" in fr[0], fr[0][:110])
check("Friedman phụ: χ² = 101,36, CD = 2,82", "chi2 = 101.36" in fr[1] and "CD = 2.82" in fr[1], fr[1][:110])

# 6. Review 22/10: Friedman mức chiều (Phụ lục A3) và nửa độ rộng CI (Phụ lục A4)
fc = open("results/tong_hop_cap/friedman_chieu.txt").read()
check("Friedman 6 chiều khớp Phụ lục A3 (χ² = 36,2; CD = 7,45)", "chi2 = 36.18" in fc and "= 7.45" in fc.split("doi_chieu_6_chieu")[1])
md = pd.read_csv("results/tong_hop_cap/mde_cong0.csv")
check("Nửa độ rộng CI khớp Phụ lục A4 (trung vị 0,057; 2/18 ô < 0,02)",
      round(md.nua_do_rong_CI.median(), 3) == 0.057 and int((md.nua_do_rong_CI < .02).sum()) == 2,
      f"trung vị {md.nua_do_rong_CI.median():.4f}")

print("\nKẾT QUẢ:", "TẤT CẢ ĐẠT" if not bad else f"{len(bad)} mục lỗi: {bad}")
sys.exit(1 if bad else 0)
