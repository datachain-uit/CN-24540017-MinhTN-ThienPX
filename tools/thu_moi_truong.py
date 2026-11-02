"""
tools/thu_moi_truong.py — Phép thử trang_thai_git() (Phụ lục B1 review 01/11). Chạy ở thư mục gốc của kho:
    python tools/thu_moi_truong.py        # phải in TẤT CẢ ĐẠT, trên máy của cả hai người
Tạo một kho Git tạm, thử 7 trường hợp: kho sạch; chỉ có file .txt mới; .py mới ở thư mục gốc; .py trong thư mục mới;
tên có dấu cách; tên có dấu tiếng Việt; a.py đổi sang CRLF (nội dung giống). Bản d51db74 chỉ có 6 trường hợp (deviations 36). Mã theo Phụ lục B1 của GVHD; Claude (Anthropic) đóng gói.
"""
import os, subprocess, sys, tempfile
sys.path.insert(0, os.getcwd())
from tools.moi_truong import trang_thai_git


def git(*a):
    subprocess.run(["git", *a], check=True, capture_output=True)


def ghi(path, noi_dung):                       # ghi theo byte để Windows không đổi \n thành \r\n
    open(path, "wb").write(noi_dung.encode("utf-8"))


os.chdir(tempfile.mkdtemp())
git("init", "-q")
ghi(".gitattributes", "* text=auto eol=lf\n")
ghi("a.py", "x = 1\n")
git("add", ".")
git("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "init")
loi = []


def kt(ten, mong_doi):
    r = trang_thai_git()
    if r["git_dirty"] != mong_doi:
        loi.append(ten)
    print(ten, "->", r["git_dirty"], r["git_chua_commit"])


kt("kho sạch", False)
ghi("ghi_chu.txt", "x\n"); kt("chỉ có file .txt mới", False)
ghi("c.py", "w = 0\n"); kt(".py mới ở thư mục gốc", True); os.remove("c.py")     # trường hợp thứ bảy (Phụ lục B1 review 01/11, bản chiều)
os.makedirs("moi"); ghi("moi/b.py", "y = 2\n")
kt(".py trong thư mục mới", True); os.remove("moi/b.py")
ghi("a b.py", "z = 3\n"); kt("tên có dấu cách", True); os.remove("a b.py")
ghi("phân_tích.py", "t = 4\n"); kt("tên có dấu tiếng Việt", True)
os.remove("phân_tích.py")
ghi("a.py", "x = 1\r\n"); kt("a.py đổi sang CRLF, nội dung giống", True)
print("TẤT CẢ ĐẠT" if not loi else f"LỖI: {loi}")
