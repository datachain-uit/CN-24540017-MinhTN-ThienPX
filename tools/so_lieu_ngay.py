"""so_lieu_ngay.py — In các sự kiện trong ngày từ Git để làm căn cứ viết nhật ký ngày (docs/nhat_ky_ngay.md).

    python tools/so_lieu_ngay.py                  # hôm nay, mọi người
    python tools/so_lieu_ngay.py 2026-10-26 NhatMinh998

Chỉ liệt kê dữ kiện (commit, file đổi, kết luận trong các file k2_*_ket_luan.csv nếu có). Phần nhận định,
vướng mắc và việc tiếp theo trong nhật ký do sinh viên tự viết (quy định 7.4, review 25/10).
Mã do Claude (Anthropic) sinh, khai báo ở docs/khai_bao_cong_cu.md.
"""
import datetime as dt, glob, subprocess, sys
day = sys.argv[1] if len(sys.argv) > 1 else dt.date.today().isoformat()
who = sys.argv[2] if len(sys.argv) > 2 else None
nxt = (dt.date.fromisoformat(day) + dt.timedelta(days=1)).isoformat()
cmd = ["git", "log", f"--since={day} 00:00", f"--until={nxt} 00:00", "--no-merges", "--format=%h|%an|%ad|%s", "--date=format:%H:%M"]
if who:
    cmd.append(f"--author={who}")
log = [l.split("|", 3) for l in subprocess.run(cmd, capture_output=True, text=True).stdout.splitlines()]
print(f"Ngày {day}: {len(log)} commit" + (f" của {who}" if who else ""))
for h, a, t, s in log:
    files = subprocess.run(["git", "show", "--name-only", "--format=", h], capture_output=True, text=True).stdout.split()
    print(f"  {t}  {h}  {a}: {s}  ({len(files)} file: {', '.join(files[:6])}{' …' if len(files) > 6 else ''})")
for f in sorted(glob.glob("results/*/k2*ket_luan*.csv")):
    import pandas as pd
    k = pd.read_csv(f)
    print(f"\n{f}: " + "; ".join(f"{r.source}-{r.level} {r.ket_luan}" for r in k.itertuples()))
