"""
tools/kiem_ma_commit.py — Kiểm ô mã commit trước khi đẩy commit nhật ký (Phụ lục B3, quyết định 5 review 01/11, bản chiều).

    python tools/kiem_ma_commit.py        # chỉ đẩy khi lệnh không in gì (mã thoát 0)

Dòng ☑ trong docs/viec_can_lam.md phải có mã commit ở cột cuối và không có dạng “commit dd/mm”;
docs/khai_bao_cong_cu.md không có “— commit dd/mm”. Mã theo Phụ lục B3 của GVHD; Claude (Anthropic) đóng gói.
"""
import re, sys

MA = re.compile(r"`[0-9a-f]{7,40}`")
CHUNG = re.compile(r"commit[^`|]{0,14}\d{2}/\d{2}")
loi = []
for so, dong in enumerate(open("docs/viec_can_lam.md", encoding="utf-8"), 1):
    o = [c.strip() for c in dong.strip().strip("|").split("|")]
    if len(o) >= 6 and "☑" in o[-2] and (not MA.search(o[-1]) or CHUNG.search(o[-1])):
        loi.append(f"viec_can_lam.md dòng {so}: {o[-1]}")
for so, dong in enumerate(open("docs/khai_bao_cong_cu.md", encoding="utf-8"), 1):
    for m in re.finditer(r"—\s*" + CHUNG.pattern, dong):
        loi.append(f"khai_bao_cong_cu.md dòng {so}: {m.group(0)}")
print("\n".join(loi))
sys.exit(1 if loi else 0)
