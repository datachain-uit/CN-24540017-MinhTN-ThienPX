"""
tools/moi_truong.py — Ghi môi trường chạy, trạng thái Git đầy đủ và mã băm không phụ thuộc kiểu xuống dòng
(V3 review 30/10, Phụ lục B3; V1, quyết định 3 và Phụ lục B2 review 31/10). Dùng cho MÃ CHẠY MỚI; không sửa mã đã chạy chính.

    from tools.moi_truong import moi_truong, trang_thai_git, sha256_lf
    json.dump(dict(..., **trang_thai_git(), **moi_truong(), code_sha256_lf=sha256_lf(__file__)), ...)

moi_truong(): Python, nền tảng máy, NumPy, scikit-learn, SciPy, pandas, XGBoost, LightGBM, CatBoost.
trang_thai_git(): git_head; git_dirty = True nếu có file đã theo dõi bị sửa HOẶC file .py/.yaml/.yml chưa theo dõi
  (env_state() cũ bỏ qua file chưa theo dõi, review 31/10 V1); git_chua_commit = danh sách các file đó.
sha256_lf(path): SHA-256 sau khi đổi CRLF → LF (cùng nội dung → cùng mã băm trên mọi hệ điều hành).
Mã do Claude (Anthropic) sinh, khai báo ở docs/khai_bao_cong_cu.md.
"""
import hashlib, importlib, platform, subprocess


def _ver(name):
    try:
        return importlib.import_module(name).__version__
    except Exception:
        return None


def moi_truong():
    env = dict(python=platform.python_version(), platform=platform.platform(), machine=platform.machine())
    for name in ("numpy", "sklearn", "scipy", "pandas", "xgboost", "lightgbm", "catboost"):
        env[name] = _ver(name)
    return env


def trang_thai_git():
    try:
        head = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip() or None
        lines = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True).stdout.splitlines()
    except Exception:
        return dict(git_head=None, git_dirty=None, git_chua_commit=None)
    sua = [l for l in lines if not l.startswith("??")]
    moi = [l for l in lines if l.startswith("??") and l.rstrip().endswith((".py", ".yaml", ".yml"))]
    return dict(git_head=head, git_dirty=bool(sua or moi), git_chua_commit=[l[3:] for l in sua + moi])


def sha256_lf(path):
    return hashlib.sha256(open(path, "rb").read().replace(b"\r\n", b"\n")).hexdigest()
