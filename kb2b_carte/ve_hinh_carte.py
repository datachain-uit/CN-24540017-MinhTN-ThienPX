"""Vẽ lại Hình 4–5 của báo cáo (CARTE: nhóm chạy lại so với kết quả công bố).

    python kb2b_carte/ve_hinh_carte.py [--out kb2b_carte/hinh_tai_tao]
Đầu vào: ket_qua/ket_qua_cua_toi.csv (lần chạy của nhóm, seed 1–2) và
ket_qua/carte_cong_bo_3_bo_ruou.csv (kết quả công bố của CARTE, lọc 3 bộ rượu).
"""
import argparse, os
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

H = os.path.dirname(os.path.abspath(__file__))
ap = argparse.ArgumentParser(); ap.add_argument("--out", default=os.path.join(H, "hinh_tai_tao")); a = ap.parse_args()
os.makedirs(a.out, exist_ok=True)
toi = pd.read_csv(os.path.join(H, "ket_qua", "ket_qua_cua_toi.csv"))
ref = pd.read_csv(os.path.join(H, "ket_qua", "carte_cong_bo_3_bo_ruou.csv"))
ref = ref[ref.random_state.isin([1, 2]) & ref.num_train.isin([32, 64])]
DS = ["wina_pl", "wine_dot_com_prices", "wine_vivino_price"]

fig, axs = plt.subplots(1, 3, figsize=(11, 3.8), constrained_layout=True)
for ax, d in zip(axs, DS):
    t = toi[toi.data_name == d]; c = ref[(ref.data_name == d) & (ref.model == "carte-gnn")]; b = ref[(ref.data_name == d) & (ref.model == "catboost")]
    ax.plot(c.groupby("num_train").score.mean(), "-s", color="#f05a28", lw=2, label="CARTE – công bố (seed 1–2)")
    ax.plot(t.groupby("num_train").score.mean(), "-o", color="#2a78d6", lw=2, label="CARTE – nhóm chạy lại (seed 1–2)")
    ax.scatter(t.num_train, t.score, color="#2a78d6", alpha=.5, s=14)
    ax.plot(b.groupby("num_train").score.mean(), "--^", color="#7f7f7f", lw=2, label="CatBoost không tiền huấn luyện – công bố")
    ax.set_xticks([32, 64]); ax.set_xlim(20, 76); ax.set_title(d, loc="left", fontweight="bold", fontsize=10)
    ax.set_xlabel("Số mẫu huấn luyện"); ax.set_ylabel("R²"); ax.grid(color="#e5e5e5"); ax.spines[["top", "right"]].set_visible(False)
h, l = axs[0].get_legend_handles_labels()
fig.legend(h, l, loc="upper center", ncol=3, frameon=False, bbox_to_anchor=(.5, 1.1))
fig.savefig(os.path.join(a.out, "hinh3_carte_duongcong.png"), dpi=200, bbox_inches="tight", facecolor="white")

m = toi.merge(ref[ref.model == "carte-gnn"], on=["data_name", "num_train", "random_state"], suffixes=("_toi", "_bai"))
r = np.corrcoef(m.score_bai, m.score_toi)[0, 1]
fig, ax = plt.subplots(figsize=(4.2, 4.2), constrained_layout=True)
for d, mk in zip(DS, ["o", "s", "^"]):
    x = m[m.data_name == d]; ax.scatter(x.score_bai, x.score_toi, marker=mk, color="#2a78d6", label=d)
ax.plot([0, .72], [0, .72], "--", color="#666"); ax.set_xlim(0, .72); ax.set_ylim(0, .72)
ax.set_xlabel("R² công bố trong bài báo"); ax.set_ylabel("R² nhóm chạy lại"); ax.grid(color="#e5e5e5"); ax.spines[["top", "right"]].set_visible(False)
ax.set_title(f"{len(m)} lượt chạy, r = {r:.2f}", loc="left", fontweight="bold", fontsize=10); ax.legend(loc="lower right", fontsize=8, frameon=False)
fig.savefig(os.path.join(a.out, "hinh4_carte_tuongquan.png"), dpi=200, bbox_inches="tight", facecolor="white")
print(f"Đã lưu 2 hình vào {a.out}; tương quan r = {r:.3f} trên {len(m)} lượt")
