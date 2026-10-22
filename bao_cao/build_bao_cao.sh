#!/usr/bin/env bash
# Sinh lại báo cáo Word từ kết quả: bao_cao/Bao_cao_tien_do.docx
# Cần Node.js ≥ 18, Python 3, zip/unzip. Lần đầu: (cd bao_cao && npm install)
set -euo pipefail
cd "$(dirname "$0")"
[ -d node_modules/docx ] || npm install --silent
node build.js                                   # -> base.docx (hình 1–2 là chỗ giữ chỗ)
rm -rf _x && mkdir _x && unzip -q base.docx -d _x
python3 post.py _x                              # chèn Hình 1–2 dạng vẽ chỉnh sửa được trong Word
(cd _x && zip -q -X -r ../Bao_cao_tien_do.docx '[Content_Types].xml' _rels docProps word)
rm -rf _x base.docx
echo "Đã tạo bao_cao/Bao_cao_tien_do.docx"
