import json
cells = []
def md(s): cells.append({"cell_type": "markdown", "metadata": {}, "source": s})
def code(s): cells.append({"cell_type": "code", "metadata": {}, "execution_count": None, "outputs": [], "source": s})

md("""# TabPFN v2 cho R1 (KB1 2×2) và các cặp miền mới (R3)

Notebook này chỉ chạy **TabPFN v2** (cần GPU). Các mô hình khác đã chạy sẵn trên CPU.

**Trước khi chạy: bật GPU** – menu **Runtime → Change runtime type → T4 GPU → Save**.

Có 3 phần độc lập (Ô 5, 6, 7). **Mỗi phần tự tải kết quả về máy khi xong**, nên nếu Colab ngắt giữa chừng thì không mất phần đã xong; chỉ cần chạy lại Ô 1–4 rồi chạy tiếp phần còn lại.

| Phần | Nội dung | Dữ liệu cần | Thời gian ước tính (T4) |
|---|---|---|---|
| Ô 5 | R1: TabPFN v2 trong thiết kế 2×2 của KB1, cặp IBM ↔ Job Change | A, B | 40–70 phút |
| Ô 6 | Cặp IBM ↔ Babushkin: 2×2 và Cổng 0 | A, D | 25–40 phút |
| Ô 7 | Cặp IBM ↔ HR 14.999: 2×2 và Cổng 0 | A, C | 60–90 phút |

Gửi lại cho Claude các file `tabpfn_*.zip` được tải về.""")

md("## Ô 1 – Tải file lên\nBấm **Choose Files**, giữ Ctrl chọn cùng lúc: `gate0_kb1_v2.zip` (bản mới nhất) và các file CSV dữ liệu bạn có: IBM, Job Change, HR 14.999 (`HR_comma_sep.csv`), Babushkin (`turnover.csv`). Tên file đặt thế nào cũng được.")
code("""import os, shutil
os.chdir('/content')
shutil.rmtree('/content/up', ignore_errors=True); os.makedirs('/content/up')
from google.colab import files
uploaded = files.upload()
for name, data in uploaded.items():
    open(f'/content/up/{name}', 'wb').write(data)
print('Đã nhận:', list(uploaded))""")

md("## Ô 2 – Giải nén, nhận dạng dữ liệu\nPhải thấy dòng **OK Mã** và ít nhất các miền cần cho phần bạn định chạy.")
code("""import os, glob, zipfile, shutil, csv
os.chdir('/content')
for i, z in enumerate(glob.glob('/content/up/*.zip')):
    with zipfile.ZipFile(z) as f:
        f.extractall(f'/content/up/x{i}')
k = sorted(glob.glob('/content/up/**/kb1_pair.py', recursive=True))      # chỉ bản mã mới có kb1_pair.py
code_dir = os.path.dirname(k[0]) if k else None
print(('OK    Mã gate0_kb1_v2 (bản có kb1_pair.py)' if code_dir else 'THIẾU Mã: file gate0_kb1_v2.zip là bản cũ, tải bản mới nhất'))
def detect(cols):
    cols = set(c.strip().lstrip('\\ufeff') for c in cols)
    if {'Attrition', 'TotalWorkingYears'} <= cols: return 'A'
    if 'enrollee_id' in cols and ({'target', 'job_chnge'} & cols): return 'B'
    if {'satisfaction_level', 'left'} <= cols: return 'C'
    if {'stag', 'event'} <= cols: return 'D'
DATA = {}
for p in sorted(glob.glob('/content/up/**/*.csv', recursive=True)):
    if '/results/' in p: continue
    for enc in ('utf-8-sig', 'latin-1'):
        try:
            with open(p, encoding=enc) as f: cols = next(csv.reader(f), [])
            break
        except UnicodeDecodeError: pass
    d = detect(cols)
    if d and d not in DATA: DATA[d] = p
NAMES = {'A': 'IBM HR', 'B': 'Job Change', 'C': 'HR 14.999', 'D': 'Babushkin'}
for d in 'ABCD':
    print(('OK    ' if d in DATA else '—     ') + f'Miền {d} ({NAMES[d]})' + (f'  ->  {os.path.basename(DATA[d])}' if d in DATA else '  (không có)'))
if code_dir:
    shutil.rmtree('/content/gate0', ignore_errors=True); shutil.copytree(code_dir, '/content/gate0')
    os.makedirs('/content/gate0/data', exist_ok=True)
    for d, p in DATA.items(): shutil.copy(p, f'/content/gate0/data/{d}.csv')
    print('\\nCó thể chạy:', ', '.join(x for x, need in [('Ô 5 (AB)', 'AB'), ('Ô 6 (AD)', 'AD'), ('Ô 7 (AC)', 'AC')] if set(need) <= set(DATA)) or 'chưa đủ dữ liệu')""")

md("## Ô 3 – Kiểm tra GPU và cài TabPFN v2\nPhải thấy `Tesla T4` và `CUDA: True`. Các dòng chữ đỏ *dependency conflicts* của pip có thể bỏ qua.")
code("""!nvidia-smi -L || echo "KHÔNG CÓ GPU – vào Runtime → Change runtime type → T4 GPU"
!pip -q install "tabpfn==2.1.3"
import torch; print('CUDA:', torch.cuda.is_available())""")

md("## Ô 4 – (chỉ khi cần) đăng nhập Hugging Face\nChỉ chạy ô này nếu Ô 5/6/7 báo lỗi 401/403 khi tải trọng số. Dán token loại **Read**.")
code("""from huggingface_hub import login
login()""")

md("## Ô 5 – R1: TabPFN v2 trong thiết kế 2×2 của KB1 (IBM ↔ Job Change)\nKhoảng 40–70 phút. Xong sẽ tự tải về `tabpfn_kb1_AB.zip`.")
code("""%cd /content/gate0
!python kb1_pair.py --pair AB --data A=data/A.csv B=data/B.csv --only TabPFN --device cuda 2>&1 | grep -v -i warning
import shutil; from google.colab import files
shutil.make_archive('/content/tabpfn_kb1_AB', 'zip', '/content/gate0/results', 'kb1_AB')
files.download('/content/tabpfn_kb1_AB.zip')""")

md("## Ô 6 – Cặp IBM ↔ Babushkin: TabPFN v2 cho 2×2 và Cổng 0\nKhoảng 25–40 phút. Xong sẽ tự tải về `tabpfn_AD.zip`.")
code("""%cd /content/gate0
!python kb1_pair.py --pair AD --data A=data/A.csv D=data/D.csv --only TabPFN --device cuda 2>&1 | grep -v -i warning
!python g0_pair.py --pair AD --data A=data/A.csv D=data/D.csv --only TabPFN --device cuda 2>&1 | grep -v -i warning
import shutil, os; from google.colab import files
os.makedirs('/content/out_AD', exist_ok=True)
for d in ['kb1_AD', 'g0_AD']:
    if os.path.isdir(f'/content/gate0/results/{d}'): shutil.copytree(f'/content/gate0/results/{d}', f'/content/out_AD/{d}', dirs_exist_ok=True)
shutil.make_archive('/content/tabpfn_AD', 'zip', '/content/out_AD')
files.download('/content/tabpfn_AD.zip')""")

md("## Ô 7 – Cặp IBM ↔ HR 14.999: TabPFN v2 cho 2×2 và Cổng 0\nKhoảng 60–90 phút. Xong sẽ tự tải về `tabpfn_AC.zip`.")
code("""%cd /content/gate0
!python kb1_pair.py --pair AC --data A=data/A.csv C=data/C.csv --only TabPFN --device cuda 2>&1 | grep -v -i warning
!python g0_pair.py --pair AC --data A=data/A.csv C=data/C.csv --only TabPFN --device cuda 2>&1 | grep -v -i warning
import shutil, os; from google.colab import files
os.makedirs('/content/out_AC', exist_ok=True)
for d in ['kb1_AC', 'g0_AC']:
    if os.path.isdir(f'/content/gate0/results/{d}'): shutil.copytree(f'/content/gate0/results/{d}', f'/content/out_AC/{d}', dirs_exist_ok=True)
shutil.make_archive('/content/tabpfn_AC', 'zip', '/content/out_AC')
files.download('/content/tabpfn_AC.zip')""")

nb = {"cells": cells, "metadata": {"colab": {"provenance": [], "gpuType": "T4"}, "accelerator": "GPU",
      "kernelspec": {"display_name": "Python 3", "name": "python3"}, "language_info": {"name": "python"}},
      "nbformat": 4, "nbformat_minor": 0}
json.dump(nb, open('notebooks/chay_TabPFN_v2_R1_R3_Colab.ipynb', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('ok')
