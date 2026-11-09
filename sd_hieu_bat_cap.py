"""
sd_hieu_bat_cap.py — Độ lệch chuẩn của hiệu bắt cặp (chuyển giao − đích) giữa 30 lần chia ở các chiều A↔C của Cổng 0.

Mã Phụ lục B3 review 07/11 (mục 7.2, việc 2; V1): giải thích MDE lớn ở chiều A→C theo phương sai của hiệu bắt cặp,
không theo tỷ lệ dương. Cặp so lấy đúng cặp dùng để tính MDE trong results/tong_hop_cap/mde_cong0.csv (79a0a4c);
điểm từng lần chia lấy từ results/g0_AC/. Phân tích mô tả trên kết quả đã commit, không chạy mô hình, không dùng nhãn mới.
Kết quả phải trùng Phụ lục A2 review 07/11. Ghi chú ở deviations.md (mục ngày 08/11 của Minh).

    python sd_hieu_bat_cap.py     # chạy trên kho sạch, sau commit chứa file này
    → results/tong_hop_cap/sd_hieu_bat_cap.csv, results/tong_hop_cap/config_sd_hieu_bat_cap.json (git_head, git_dirty, phiên bản)

Mã của GVHD; Claude (Anthropic) thêm phần mô tả và dòng ghi trạng thái Git (quy tắc 6), khai báo ở docs/khai_bao_cong_cu.md.
"""
import json
import pandas as pd
from tools.moi_truong import moi_truong, trang_thai_git

json.dump(dict(**trang_thai_git(), **moi_truong()),
          open("results/tong_hop_cap/config_sd_hieu_bat_cap.json", "w"), indent=1)
d = 'results/g0_AC/'
x = pd.concat(pd.read_csv(d + f) for f in ['results_g0_AC_49df37eb_cpu.csv',
              'results_g0_AC_49df37eb_rankrf.csv', 'results_g0_AC_49df37eb_TabPFN.csv'])
m = pd.read_csv('results/tong_hop_cap/mde_cong0.csv')
rows = []
for _, r in m[m.chieu.isin(['A→C', 'C→A'])].iterrows():
    s = x[(x.target == r.chieu[-1]) & (x.k.astype(str) == str(r.k))]
    p = s.pivot_table(index='rep', columns='method', values='pr_auc')
    b, t = p[r.baseline_dich], p[r.chuyen_giao_tot_nhat]
    rows.append(dict(chieu=r.chieu, k=r.k, sd_delta=(t - b).std(),
                     sd_dich=b.std(), sd_chuyen_giao=t.std(), tuong_quan=b.corr(t)))
pd.DataFrame(rows).to_csv('results/tong_hop_cap/sd_hieu_bat_cap.csv', index=False)
