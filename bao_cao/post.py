import re, sys, shutil, os
HERE = os.path.dirname(os.path.abspath(__file__))
d = open(os.path.join(sys.argv[1] if len(sys.argv) > 1 else 'x', 'word', 'document.xml'), encoding='utf-8').read()
f1 = open(os.path.join(HERE, 'hinh_ve', 'fig1.xml'), encoding='utf-8').read()
f2 = open(os.path.join(HERE, 'hinh_ve', 'fig2.xml'), encoding='utf-8').read()
def rep(s, a, b):
    assert a in s, a
    return s.replace(a, b)
f1 = rep(f1, '>Hai nguồn khác cấu trúc<', '>Các nguồn khác cấu trúc<')
f2 = rep(f2, '>20 công trình<', '>37 công trình, phiếu đọc<')
f2 = rep(f2, '>Quy trình đánh giá<', '>Cổng 0 và giao thức<')
f2 = rep(f2, '>hai chiều<', '>đánh giá có kiểm soát<')
f2 = rep(f2, '>hai chiều A ↔ B<', '>nhiều cặp, hai chiều<')
f2 = rep(f2, '>Xử lý mất cân bằng<', '>Hiệu chỉnh xác suất<')
f2 = rep(f2, '>SMOTE, ADASYN, GAN<', '>và công bằng theo giới<')
f2 = rep(f2, '>Module chấm điểm<', '>Phân tích khi nào<')
f2 = rep(f2, '>rủi ro nghỉ việc<', '>chuyển giao có ích<')
for fid, xml in (('FIG1', f1), ('FIG2', f2)):
    pat = re.compile(r'<w:p><w:pPr><w:jc w:val="center"/></w:pPr><w:r><w:t xml:space="preserve">\[\[' + fid + r'\]\]</w:t></w:r></w:p>')
    assert len(pat.findall(d)) == 1, fid
    d = pat.sub(lambda m: '<w:p><w:pPr><w:keepNext/><w:jc w:val="center"/></w:pPr><w:r>' + xml + '</w:r></w:p>', d)
cnt = [0]
def nid(m):
    cnt[0] += 1; return f'docPr id="{cnt[0]}"'
d = re.sub(r'docPr id="\d+"', nid, d)
# also cNvPr ids inside pictures/shapes should be unique-ish; leave
open(os.path.join(sys.argv[1] if len(sys.argv) > 1 else 'x', 'word', 'document.xml'), 'w', encoding='utf-8').write(d)
print('docPr', cnt[0])
