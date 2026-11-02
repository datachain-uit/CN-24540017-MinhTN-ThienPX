"""
tools/danh_muc_zip.py — Danh mục mã băm từng file trong một tệp nén, không giải nén ra đĩa (Phụ lục B2 review 01/11, bản chiều).

    python tools/danh_muc_zip.py <tep.zip> > data/<ten>_sha256.txt

Mỗi dòng: SHA-256, kích thước (byte), giờ ghi trong tệp nén, hệ điều hành đã tạo mục đó, tên file.
Mã theo Phụ lục B2 của GVHD; Claude (Anthropic) đóng gói, khai báo ở docs/khai_bao_cong_cu.md.
"""
import hashlib, sys, zipfile

HE = {0: "Windows/MS-DOS", 3: "Unix"}
with zipfile.ZipFile(sys.argv[1]) as z:
    for i in sorted(z.infolist(), key=lambda i: i.filename):
        if i.is_dir():
            continue
        h = hashlib.sha256(z.read(i.filename)).hexdigest()
        gio = "%04d-%02d-%02d %02d:%02d:%02d" % i.date_time
        print(h, i.file_size, gio, HE.get(i.create_system, i.create_system), i.filename, sep=" ")
