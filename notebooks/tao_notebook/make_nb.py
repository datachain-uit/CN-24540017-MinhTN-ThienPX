import json
cells = []
def md(s): cells.append({"cell_type": "markdown", "metadata": {}, "source": s})
def code(s): cells.append({"cell_type": "code", "metadata": {}, "execution_count": None, "outputs": [], "source": s})

md("""# Chạy lại KB1 v2 trên file Kaggle gốc

**Cách dùng:** bấm lần lượt nút ▶ ở từng ô, từ trên xuống dưới (hoặc menu **Runtime → Run all**).

Chuẩn bị sẵn trên máy 3 file (để nguyên file .zip tải từ Kaggle cũng được, notebook tự giải nén):
1. `gate0_kb1_v2.zip` (file Claude gửi)
2. File CSV miền A – **IBM HR Analytics Employee Attrition & Performance** (tên gì cũng được, hoặc file .zip tải từ Kaggle)
3. File CSV miền B – **HR Analytics: Job Change of Data Scientists** (bản *train* có cột `target`; tên gì cũng được)""")

md("## Ô 1 – Tải file lên\nSau khi bấm ▶, bên dưới ô hiện nút **Choose Files / Chọn tệp**. Bấm vào, chọn cả 3 file cùng lúc (giữ phím Ctrl để chọn nhiều file), rồi bấm Open. Đợi đến khi hiện chữ *100% done* cho mỗi file.")
code("""import os, glob, zipfile, shutil
os.chdir('/content')
shutil.rmtree('/content/up', ignore_errors=True); os.makedirs('/content/up')
from google.colab import files
uploaded = files.upload()
for name, data in uploaded.items():
    open(f'/content/up/{name}', 'wb').write(data)
print('Đã nhận:', list(uploaded))""")

md("## Ô 2 – Giải nén và tìm đúng file\nÔ này tự giải nén mọi file .zip vừa tải lên và nhận ra file nào là miền A, file nào là miền B **theo nội dung**, nên tên file đặt thế nào cũng được. Nếu báo **THIẾU**, quay lại Ô 1 tải thêm file còn thiếu.")
code("""import os, glob, zipfile, shutil, csv
os.chdir('/content')
for i, z in enumerate(glob.glob('/content/up/*.zip')):
    with zipfile.ZipFile(z) as f:
        f.extractall(f'/content/up/x{i}')
# Nhận dạng theo NỘI DUNG (dòng tiêu đề), không phụ thuộc tên file
ibm = jc = None
for p in sorted(glob.glob('/content/up/**/*.csv', recursive=True)):
    with open(p, encoding='utf-8-sig', errors='ignore') as f:
        cols = next(csv.reader(f), [])
    if 'Attrition' in cols and 'TotalWorkingYears' in cols and not ibm:
        ibm = p
    elif 'enrollee_id' in cols and ('target' in cols or 'job_chnge' in cols) and not jc:
        jc = p
k = sorted(glob.glob('/content/up/**/kb1_v2.py', recursive=True))
code_dir = os.path.dirname(k[0]) if k else None
ok = True
for label, p in [('Mã gate0_kb1_v2', code_dir), ('Miền A – IBM HR (có cột Attrition)', ibm), ('Miền B – Job Change (có cột enrollee_id, target)', jc)]:
    print(('OK    ' if p else 'THIẾU ') + label + ('  ->  ' + os.path.basename(p) if p else ''))
    ok = ok and bool(p)
if ok:
    shutil.rmtree('/content/gate0', ignore_errors=True)
    shutil.copytree(code_dir, '/content/gate0')
    os.makedirs('/content/gate0/data', exist_ok=True)
    shutil.copy(ibm, '/content/gate0/data/WA_Fn-UseC_-HR-Employee-Attrition.csv')
    shutil.copy(jc, '/content/gate0/data/aug_train.csv')
    print('\\nSẵn sàng. Chạy tiếp Ô 3.')""")

md("## Ô 3 – Chạy KB1 v2 (khoảng 15–30 phút)\nKhông cần GPU. Ô sẽ in tiến độ từng lần chia (`đích A lần 0 xong …`). Đừng đóng tab trong lúc chạy.\n\nKiểm tra 2 dòng đầu phải là: `A: … 'rows': 1470, 'pos': 237` và `B: … 'rows_raw': 19158, 'dup_removed': 74, 'rows': 19084, 'pos': 4755`.")
code("""%cd /content/gate0
!pip -q install xgboost
!python kb1_v2.py --ibm data/WA_Fn-UseC_-HR-Employee-Attrition.csv --jc data/aug_train.csv --out results/kb1_v2_kaggle 2>&1 | grep -v -i warning""")

md("## Ô 4 – Tổng hợp và so sánh với số trong báo cáo\nDòng **KẾT LUẬN** ở cuối cho biết: KHỚP / LỆCH NHỎ / LỆCH.")
code("""%cd /content/gate0
!python kb1_v2_summary.py results/kb1_v2_kaggle/results_kb1v2_99d14779.csv > results/kb1_v2_kaggle/summary_print.txt
!python so_sanh_kb1.py results/kb1_v2/results_kb1v2_99d14779.csv results/kb1_v2_kaggle/results_kb1v2_99d14779.csv""")

md("## Ô 5 – Tải kết quả về máy\nTrình duyệt sẽ tải về file `ket_qua_kb1_v2_kaggle.zip`. Gửi file này cho Claude để cập nhật báo cáo, và lưu vào thư mục chung của nhóm.")
code("""import shutil, os
os.chdir('/content/gate0')
shutil.make_archive('/content/ket_qua_kb1_v2_kaggle', 'zip', 'results', 'kb1_v2_kaggle')
from google.colab import files
files.download('/content/ket_qua_kb1_v2_kaggle.zip')""")

nb = {"cells": cells, "metadata": {"colab": {"provenance": []}, "kernelspec": {"display_name": "Python 3", "name": "python3"},
      "language_info": {"name": "python"}}, "nbformat": 4, "nbformat_minor": 0}
json.dump(nb, open('notebooks/chay_KB1_v2_tren_Colab.ipynb', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('ok')
