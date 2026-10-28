"""
tradaboost.py — TrAdaBoost cho phân loại nhị phân theo Dai, Yang, Xue & Yu (ICML 2007), Thuật toán 1.

Dùng làm baseline chuyển giao trên KHÁI NIỆM CHUNG (cùng không gian đặc trưng ở nguồn và đích).
    from tradaboost import tradaboost_fit, tradaboost_score
    model = tradaboost_fit(Xs, ys, Xt, yt, n_rounds=50, max_depth=3, init="uniform", seed=0)
    s = tradaboost_score(model, X_test)          # điểm xếp hạng (dùng cho PR-AUC, AUC-ROC, F1 theo ngưỡng tỷ lệ dương)

Cấu hình mặc định (chốt trước khi chạy; xem prereg/prereg_trada.yaml):
    - bộ học cơ sở: cây quyết định độ sâu 3 (random_state = seed)
    - số vòng N = 50; bộ phân loại cuối dùng các vòng t = ceil(N/2) … N như bài gốc
    - khởi tạo trọng số "uniform": đều nhau trên mọi mẫu nguồn và đích (dạng gốc của thuật toán, cấu hình chính);
      "balanced": tổng trọng số của nguồn và của đích bằng nhau (mỗi miền 0,5) – phân tích độ nhạy
    - sai số trên đích được chặn trong [1e-6; 0,499] để beta_t xác định
"""
import numpy as np
from sklearn.tree import DecisionTreeClassifier


def tradaboost_fit(Xs, ys, Xt, yt, n_rounds=50, max_depth=3, init="uniform", seed=0):
    Xs, Xt = np.asarray(Xs, float), np.asarray(Xt, float)
    ys, yt = np.asarray(ys).astype(int), np.asarray(yt).astype(int)
    n, m = len(ys), len(yt)
    X = np.vstack([Xs, Xt]); y = np.r_[ys, yt]
    if init == "balanced":
        w = np.r_[np.full(n, 0.5 / n), np.full(m, 0.5 / m)]
    else:                                                    # "uniform"
        w = np.full(n + m, 1.0 / (n + m))
    beta = 1.0 / (1.0 + np.sqrt(2.0 * np.log(n) / n_rounds))  # hệ số giảm trọng số mẫu nguồn bị sai
    learners, betas = [], []
    for t in range(n_rounds):
        p = w / w.sum()
        h = DecisionTreeClassifier(max_depth=max_depth, random_state=seed + t).fit(X, y, sample_weight=p)
        miss = (h.predict(X) != y).astype(float)             # |h_t(x) − c(x)| với h_t nhận giá trị 0/1
        wt = w[n:]
        eps = float(np.sum(wt * miss[n:]) / wt.sum())
        eps = min(max(eps, 1e-6), 0.499)
        beta_t = eps / (1.0 - eps)
        w = w.copy()
        w[:n] *= beta ** miss[:n]                             # nguồn: mẫu sai bị giảm trọng số
        w[n:] *= beta_t ** (-miss[n:])                        # đích: mẫu sai được tăng trọng số
        learners.append(h); betas.append(beta_t)
    start = int(np.ceil(n_rounds / 2)) - 1                    # vòng ceil(N/2) … N (đánh số từ 1)
    return dict(learners=learners[start:], alphas=np.log(1.0 / np.asarray(betas[start:])))


def tradaboost_score(model, X):
    """Điểm liên tục: sum_t ln(1/beta_t) · (P_t(y = 1 | x) − 1/2). Dấu của điểm trùng quyết định của
    bộ phân loại cuối trong bài gốc khi P_t là 0/1; dùng xác suất của cây để có thứ tự xếp hạng mịn hơn."""
    X = np.asarray(X, float)
    s = np.zeros(len(X))
    for h, a in zip(model["learners"], model["alphas"]):
        pr = h.predict_proba(X)
        p1 = pr[:, list(h.classes_).index(1)] if 1 in h.classes_ else np.zeros(len(X))
        s += a * (p1 - 0.5)
    return s


if __name__ == "__main__":
    # Kiểm thử trên dữ liệu tổng hợp: nguồn và đích cùng quy luật trên phần lớn không gian,
    # đích lệch một phần; đích chỉ có k = 10 mẫu có nhãn (2 mẫu dương).
    from sklearn.metrics import average_precision_score
    rng = np.random.default_rng(0)

    def gen(n, shift):
        X = rng.normal(size=(n, 4))
        z = 1.2 * X[:, 0] - 0.8 * X[:, 1] + shift * X[:, 2] - 1.6
        return X, (rng.random(n) < 1 / (1 + np.exp(-z))).astype(int)

    Xs, ys = gen(5000, 0.0)
    gains, gains_u = [], []
    for seed in range(20):
        Xt_all, yt_all = gen(3000, 0.5)
        pos, neg = np.where(yt_all == 1)[0], np.where(yt_all == 0)[0]
        tr = np.r_[rng.choice(pos, 2, replace=False), rng.choice(neg, 8, replace=False)]
        te = np.setdiff1d(np.arange(len(yt_all)), tr)
        m = tradaboost_fit(Xs, ys, Xt_all[tr], yt_all[tr], init="balanced", seed=seed)
        mu = tradaboost_fit(Xs, ys, Xt_all[tr], yt_all[tr], seed=seed)
        tgt = DecisionTreeClassifier(max_depth=3, random_state=seed).fit(Xt_all[tr], yt_all[tr])
        ap_t = average_precision_score(yt_all[te], tgt.predict_proba(Xt_all[te])[:, 1])
        gains.append(average_precision_score(yt_all[te], tradaboost_score(m, Xt_all[te])) - ap_t)
        gains_u.append(average_precision_score(yt_all[te], tradaboost_score(mu, Xt_all[te])) - ap_t)
    print(f"ΔPR-AUC TrAdaBoost (balanced) − cây chỉ dùng đích: trung bình {np.mean(gains):+.3f}; dương ở {np.mean(np.array(gains) > 0):.0%} lần")
    print(f"ΔPR-AUC TrAdaBoost (uniform)  − cây chỉ dùng đích: trung bình {np.mean(gains_u):+.3f}; dương ở {np.mean(np.array(gains_u) > 0):.0%} lần")
    # Kiểm thử tính đúng: khi nguồn rỗng thông tin (nhãn ngẫu nhiên), trọng số nguồn phải giảm dần
    ysr = rng.integers(0, 2, len(ys))
    Xt_all, yt_all = gen(200, 0.0)
    m_r = tradaboost_fit(Xs, ysr, Xt_all[:40], yt_all[:40], seed=1)
    assert len(m_r["learners"]) == 50 - int(np.ceil(50 / 2)) + 1          # các vòng 25 … 50 (26 bộ học)
    assert np.all(np.isfinite(m_r["alphas"])) and np.all(m_r["alphas"] > 0)
    print("Kiểm thử cấu trúc: đạt")
