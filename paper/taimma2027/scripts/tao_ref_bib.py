"""Sinh BibTeX cho bài TAIMMA 2027 từ danh mục tài liệu đã chốt của nhóm (bao_cao/refs.js).
    python paper/taimma2027/scripts/tao_ref_bib.py      # chạy ở thư mục gốc của kho
Ghi paper/taimma2027/tables/refs_nhom.bib; dòng chú thích trên mỗi mục ghi số tài liệu trong báo cáo tiến độ.
Chỉ thêm ngoài refs.js hai tài liệu đã được GVHD quyết định (CLAUDE.md quy tắc 2, QĐ3 review 25/10):
luận văn UNICAMP 2025 (bibtex trong phiếu đọc) và TrAdaBoost (Dai và cs., ICML 2007).
Mục có "và cộng sự" chưa đủ tên tác giả: ghi "and others" và đánh dấu TODO để bổ sung trước khi nộp.
"""
import re, subprocess, unicodedata

SRC = "bao_cao/refs.js"
OUT = "paper/taimma2027/tables/refs_nhom.bib"


def commit_cua(path):
    return subprocess.run(["git", "log", "-1", "--format=%h", "--", path], capture_output=True, text=True).stdout.strip()


def ascii_(s):
    return "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c)).replace("đ", "d").replace("Đ", "D")


def tac_gia(s):
    khac = "và cộng sự" in s
    s = re.sub(r"\s*và cộng sự.*$", "", s)
    ten = [t.strip() for t in re.split(r",\s*|\s+và\s+", s) if t.strip()]
    ten = [re.sub(r"^(.+?) (\S+) III$", r"\2 III, \1", t) for t in ten]       # "H. Daumé III" -> "Daumé III, H."
    return " and ".join(ten + (["others"] if khac else [])), khac


def khoa(ten, nam, tieu_de):
    a1 = ten.split(" and ")[0]
    a1 = a1.split(",")[0] if "," in a1 else a1                           # dạng "Họ III, Tên"
    dau = [w for w in a1.split() if w not in ("III", "Jr.")]
    ho = "".join(w for w in dau[1:] if w[0].islower() or w in ("De", "Van")) + dau[-1] if len(dau) > 1 else dau[-1]
    ho = re.sub(r"[^a-z]", "", ascii_(ho).lower())
    tu = next(w for w in (re.sub(r"[^a-z]", "", ascii_(x).lower()) for x in re.split(r"[\s:]+", tieu_de)) if w and w not in ("a", "an", "the"))
    return f"{ho}{nam}{tu}"


def mot_muc(so, dong):
    m = re.match(r"(.+?), “(.+?),?” (.*)$", dong)
    ten, khac = tac_gia(m.group(1))
    tieu_de, con = m.group(2).rstrip(","), m.group(3)
    con = re.sub(r"^\(([^)]*)\),\s*", "", con)                     # chú thích tên viết tắt sau tiêu đề
    nam = re.findall(r"(?:^|[\s,(])((?:19|20)\d{2})(?=[.,;)]|\s|$)", con)[-1]
    f = {"author": ten, "title": "{" + tieu_de + "}", "year": nam}
    noi = re.search(r"\*(.+?)\*", con)
    if "arXiv" in con:
        loai = "misc"; f["note"] = re.search(r"arXiv:\S+?(?=,)", con).group(0) + ", preprint"
    elif con.startswith("trong"):
        loai = "inproceedings"; f["booktitle"] = noi.group(1)
    else:
        loai = "article"; f["journal"] = noi.group(1)
    for nhan, truong in [(r"tập (\d+)", "volume"), (r"số ([\d–]+)", "number"), (r"PMLR tập (\d+)", "volume")]:
        x = re.search(nhan, con)
        if x: f[truong] = x.group(1)
    x = re.search(r"tr\. ([\w–-]+)", con) or re.search(r"Art\. (\w+)", con)
    if x: f["pages"] = x.group(1).replace("–", "--")
    x = re.search(r"DOI: (\S+?)\.?$", con)
    if x: f["doi"] = x.group(1)
    k = khoa(ten, nam, tieu_de)
    dau = f"% [{so}] {SRC}" + ("  TODO: bổ sung đủ tên tác giả trước khi nộp" if khac else "")
    f = {a: (b.replace("&", r"\&") if a in ("journal", "booktitle") else b) for a, b in f.items()}
    than = ",\n".join(f"  {a} = {{{b}}}" for a, b in f.items())
    return k, f"{dau}\n@{loai}{{{k},\n{than}\n}}"


def main():
    js = open(SRC, encoding="utf-8").read()
    muc = re.findall(r"'\[(\d+)\] (.+?)',\s*$", js, flags=re.M)
    ra = [f"% Sinh bởi paper/taimma2027/scripts/tao_ref_bib.py từ {SRC} (commit {commit_cua(SRC)}). Không sửa tay.",
          "% Lưu ý: số [44] trong refs.js là TabICL; trong phiếu đọc và bản đủ, [44] là luận văn UNICAMP."]
    khoa_da = {}
    for so, dong in muc:
        k, s = mot_muc(so, dong)
        assert k not in khoa_da, (k, so, khoa_da.get(k))
        khoa_da[k] = so; ra.append(s)
    phieu = "docs/phieu_doc/[44]_Pereira_2025_UNICAMP.md"
    b = re.search(r"```bibtex\n(.+?)```", open(phieu, encoding="utf-8").read(), flags=re.S).group(1).strip()
    ra.append(f"% Luận văn UNICAMP 2025, {phieu} (commit {commit_cua(phieu)}); QĐ3 review 25/10\n{b}")
    ra.append("% TrAdaBoost, bài gốc của tradaboost.py; QĐ3 review 25/10. TODO: đối chiếu trang với bản chính thức\n"
              "@inproceedings{dai2007boosting,\n  author = {Dai, Wenyuan and Yang, Qiang and Xue, Gui-Rong and Yu, Yong},\n"
              "  title = {{Boosting for transfer learning}},\n  booktitle = {Proc. 24th Int. Conf. on Machine Learning (ICML)},\n"
              "  pages = {193--200},\n  year = {2007}\n}")
    with open(OUT, "w", encoding="utf-8", newline="\n") as fo:
        fo.write("\n\n".join(ra) + "\n")
    print(len(muc) + 2, "mục ->", OUT)
    for k, so in sorted(khoa_da.items(), key=lambda x: int(x[1])):
        print(f"[{so}] {k}")


if __name__ == "__main__":
    main()
