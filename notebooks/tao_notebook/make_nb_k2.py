import json, os
cells = []
def md(s): cells.append({"cell_type": "markdown", "metadata": {}, "source": s})
def code(s): cells.append({"cell_type": "code", "metadata": {}, "execution_count": None, "outputs": [], "source": s})

md("""# TabPFN v2 cho kịch bản K2 (miền đích nghèo đặc trưng)

Chỉ chạy **TabPFN v2** (cần GPU); các phương pháp khác của K2 chạy trên CPU. Thiết kế theo `prereg/prereg_k2.yaml` (bản chốt `d2f1ef5`, **có sửa đổi 24/10**: thêm mức L1_core và L2 — `deviations.md` mục 9–14). Người chạy: **Phạm Xuân Thiên** (review 24/10, mục 6.3, hạn 30/10).

**Trước khi chạy: Runtime → Change runtime type → T4 GPU → Save.**

| Ô | Nội dung | Thời gian ước tính (T4) |
|---|---|---|
| 1 | Lấy mã từ GitHub (repo công khai), tải 3 file dữ liệu | 1–2 phút |
| 2 | Cài TabPFN v2 | 1–2 phút |
| 4 | Lần chia 0–9 → tự tải `tabpfn_k2_rep00-09.zip` | 20–40 phút |
| 5 | Lần chia 10–19 → tự tải `tabpfn_k2_rep10-19.zip` | 20–40 phút |
| 6 | Lần chia 20–29 → tự tải `tabpfn_k2_rep20-29.zip` | 20–40 phút |

Mỗi lần chia có 5 nhóm cột đích (L0 theo từng nguồn, L1 — dùng chung cho L1_core —, L1_noAge, L2) × 5 lần rút × 4 giá trị k.
Nếu Colab ngắt giữa chừng: chạy lại Ô 1–2 rồi chạy tiếp ô chưa xong.

**Sau khi chạy:** giải nén ba file zip vào `results/k2_v2/` của kho Git (giữ nguyên tên file), rồi commit bằng tài khoản Git của người chạy, ví dụ
`git add results/k2_v2/*TabPFN* && git commit -m "K2: TabPFN v2 (Colab T4), lần chia 0–29"`, và ghi một dòng vào `docs/nhat_ky_ngay.md`.""")

md("## Ô 1 – Lấy mã và tải dữ liệu\nBấm **Choose Files**, chọn cùng lúc 3 file: IBM (`WA_Fn-UseC_-HR-Employee-Attrition.csv`), Job Change (`aug_train.csv`), HR 14.999 (`HR_comma_sep.csv`). Tên file khác cũng được. Phải thấy 3 dòng **OK** và **SHA-256 khớp**.")
code("""import os, shutil, glob, csv, hashlib
os.chdir('/content'); shutil.rmtree('/content/repo', ignore_errors=True)
!git clone -q https://github.com/datachain-uit/CN-24540017-MinhTN-ThienPX.git /content/repo
%cd /content/repo
!git log --oneline -3
import yaml
assert "sua_doi_2410" in yaml.safe_load(open("prereg/prereg_k2.yaml")), "kho Git chưa có sửa đổi 24/10 – báo lại cho Minh"
from google.colab import files
up = files.upload()
def detect(cols):
    cols = set(c.strip().lstrip('\\ufeff') for c in cols)
    if {'Attrition', 'TotalWorkingYears'} <= cols: return 'A'
    if 'enrollee_id' in cols and ({'target', 'job_chnge'} & cols): return 'B'
    if {'satisfaction_level', 'left'} <= cols: return 'C'
SHA = {'A': 'a5c31e38bd7fafc9bc333884eb181b06b41b8e5e488e8f7ccb27199fb3be7659',
       'B': '8b78da3482032500df40d5359c36ba4a59e28ccd6fc272b050dcf6dee37f114c',
       'C': '2510e274a90547f34c7b0db5a4ab70282c2710eb54252f14921bf980b81a928c'}
os.makedirs('data', exist_ok=True)
for name, data in up.items():
    cols = next(csv.reader(data.decode('utf-8-sig', errors='ignore').splitlines()), [])
    d = detect(cols)
    if d:
        open(f'data/{d}.csv', 'wb').write(data)
        print(f'OK  miền {d} <- {name}  | SHA-256', 'khớp' if hashlib.sha256(data).hexdigest() == SHA[d] else 'KHÁC (báo lại cho nhóm)')""")

md("## Ô 2 – Cài TabPFN v2 và kiểm tra GPU\nPhải thấy `Tesla T4` và `CUDA: True`.")
code("""!nvidia-smi -L || echo "KHÔNG CÓ GPU – Runtime → Change runtime type → T4 GPU"
!pip -q install "tabpfn==2.1.3" pyyaml
import torch; print('CUDA:', torch.cuda.is_available())""")

md("## Ô 3 – (chỉ khi cần) đăng nhập Hugging Face\nChỉ chạy nếu Ô 4/5 báo lỗi 401/403 khi tải trọng số. Dán token loại **Read**, không lưu token vào notebook.")
code("""from huggingface_hub import login
login()""")

for i, (a, b) in enumerate([(0, 10), (10, 20), (20, 30)]):
    md(f"## Ô {4 + i} – TabPFN v2, lần chia {a}–{b - 1}\nXong sẽ tự tải `tabpfn_k2_rep{a:02d}-{b - 1:02d}.zip` (chỉ gồm file của các lần chia này).")
    code(f"""%cd /content/repo
!python k2_run.py --data A=data/A.csv B=data/B.csv C=data/C.csv --only TabPFN --device cuda --reps {a} {b} --out results/k2_v2 2>&1 | grep -v -i warning
import glob, zipfile; from google.colab import files
z = '/content/tabpfn_k2_rep{a:02d}-{b - 1:02d}.zip'
with zipfile.ZipFile(z, 'w', zipfile.ZIP_DEFLATED) as f:
    for p in glob.glob('results/k2_v2/*TabPFN_rep{a:02d}-{b - 1:02d}*'):
        f.write(p, p.split('/')[-1]); print('  +', p)
files.download(z)""")

nb = {"cells": cells, "metadata": {"colab": {"provenance": [], "gpuType": "T4"}, "accelerator": "GPU",
      "kernelspec": {"display_name": "Python 3", "name": "python3"}, "language_info": {"name": "python"}},
      "nbformat": 4, "nbformat_minor": 0}
os.makedirs("notebooks", exist_ok=True)
json.dump(nb, open("notebooks/chay_TabPFN_v2_K2_Colab.ipynb", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("ok")
