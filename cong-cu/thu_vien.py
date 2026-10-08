"""Thư viện dùng chung cho mọi script trong cong-cu/.

Gồm ba nhóm:
  · chữ    — bỏ dấu tiếng Việt, tạo slug, chuẩn hoá số điện thoại
  · màu    — đổi hex ↔ RGB, đo tương phản WCAG, dựng bảng màu từ MỘT màu chủ đạo
  · cài đặt — tự cài Pillow khi phiên đám mây chưa có

Không phụ thuộc thư viện ngoài (trừ hàm can_pillow tự cài Pillow).
"""
import colorsys
import importlib
import re
import subprocess
import sys
import unicodedata


# ─────────────────────────── chữ ───────────────────────────

def khong_dau(s):
    """'Gốm Bát Tràng' → 'Gom Bat Trang'."""
    s = unicodedata.normalize("NFD", str(s or ""))
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return s.replace("đ", "d").replace("Đ", "D")


def tao_slug(s, toi_da=58):
    """'Bình hoa sen men lam!' → 'binh-hoa-sen-men-lam'.

    Cũng là luật đặt tên project Cloudflare Pages: chữ thường, số, gạch ngang,
    không bắt đầu/kết thúc bằng gạch ngang, tối đa 58 ký tự.
    """
    s = khong_dau(s).lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    s = s[:toi_da].strip("-")
    return s or "khong-ten"


SLUG_HOP_LE = re.compile(r"^[a-z0-9](?:[a-z0-9-]{0,56}[a-z0-9])?$")


def so_dien_thoai(s):
    """Chuẩn hoá số điện thoại Việt Nam.

    → (hien_thi, quoc_te, chu_so_zalo) hoặc None nếu không phải số hợp lệ.
      '0912345678'     → ('0912 345 678', '+84912345678', '0912345678')
      '+84 912 345 678'→ như trên
    Số cố định 02x (11 chữ số) vẫn nhận.
    """
    if not s:
        return None
    so = re.sub(r"[^\d+]", "", str(s))
    if so.startswith("+84"):
        so = "0" + so[3:]
    elif so.startswith("84") and len(so) in (11, 12):
        so = "0" + so[2:]
    if not re.fullmatch(r"0\d{9,10}", so):
        return None
    if len(so) == 10:
        hien = "%s %s %s" % (so[:4], so[4:7], so[7:])
    else:
        hien = "%s %s %s" % (so[:3], so[3:7], so[7:])
    return hien, "+84" + so[1:], so


# ─────────────────────────── màu ───────────────────────────

def hex_sang_rgb(h):
    h = str(h).strip().lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    if not re.fullmatch(r"[0-9a-fA-F]{6}", h):
        raise ValueError("Mã màu không hợp lệ: %r (cần dạng #1F4E8C)" % h)
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def rgb_sang_hex(rgb):
    return "#%02X%02X%02X" % tuple(max(0, min(255, round(c))) for c in rgb)


def do_sang_tuong_doi(rgb):
    """Relative luminance theo WCAG 2.x."""
    def kenh(c):
        c = c / 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (kenh(c) for c in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def tuong_phan(a, b):
    """Tỉ lệ tương phản giữa hai màu (hex hoặc RGB). Nền trắng chữ đen = 21."""
    if isinstance(a, str):
        a = hex_sang_rgb(a)
    if isinstance(b, str):
        b = hex_sang_rgb(b)
    la, lb = do_sang_tuong_doi(a), do_sang_tuong_doi(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def tron(a, b, ti_le):
    """Trộn màu a với b; ti_le = phần của a (0..1)."""
    return tuple(a[i] * ti_le + b[i] * (1 - ti_le) for i in range(3))


def lam_dam_den(rgb, nguong, nen=(255, 255, 255)):
    """Giảm độ sáng (giữ sắc độ) cho tới khi tương phản với nền ≥ nguong."""
    h, l, s = colorsys.rgb_to_hls(*(c / 255 for c in rgb))
    for _ in range(200):
        mau = tuple(c * 255 for c in colorsys.hls_to_rgb(h, l, s))
        if tuong_phan(mau, nen) >= nguong:
            return mau
        l = max(0.0, l - 0.01)
    return (0, 0, 0)


TRANG = (255, 255, 255)


def bang_mau(mau_chu_dao):
    """Từ MỘT màu chủ đạo → đủ bộ màu cho giao diện nền trắng.

    Nền LUÔN trắng. Màu chủ đạo chỉ dùng cho điểm nhấn, nút, đường kẻ, nền nhạt.
    Mọi màu đặt CHỮ hoặc làm NỀN CHO CHỮ TRẮNG đều được ép đạt tương phản ≥ 4,5
    (chuẩn AA) — doanh nghiệp đưa màu vàng nhạt thì nút tự sẫm lại cho đọc được,
    chứ không đẩy màu nhạt lên nút rồi chữ trắng biến mất.
    """
    goc = hex_sang_rgb(mau_chu_dao)
    dam = lam_dam_den(goc, 4.6)          # chữ nhấn, nút có chữ trắng
    dam_hon = lam_dam_den(goc, 7.5)      # tiêu đề nhấn, nút khi bấm
    nhat = tron(goc, TRANG, 0.07)        # nền mảng (gần như trắng, ngả màu nhẹ)
    nhat_vua = tron(goc, TRANG, 0.14)    # nền chip, nền ảnh sản phẩm
    vien = tron(goc, TRANG, 0.28)        # đường kẻ, viền thẻ
    return {
        "chinh": rgb_sang_hex(goc),
        "dam": rgb_sang_hex(dam),
        "dam_hon": rgb_sang_hex(dam_hon),
        "nhat": rgb_sang_hex(nhat),
        "nhat_vua": rgb_sang_hex(nhat_vua),
        "vien": rgb_sang_hex(vien),
        "tuong_phan_dam": round(tuong_phan(dam, TRANG), 2),
        "tuong_phan_goc": round(tuong_phan(goc, TRANG), 2),
    }


# ─────────────────────────── cài đặt ───────────────────────────

def can_goi(ten_module, ten_goi=None):
    """Import một module; chưa có thì pip install rồi import lại.

    Phiên Claude Code trên đám mây là máy ảo mới tinh mỗi lần — Pillow chưa chắc có.
    """
    try:
        return importlib.import_module(ten_module)
    except ImportError:
        pass
    goi = ten_goi or ten_module
    print("… đang cài %s (chỉ lần đầu mỗi phiên)" % goi, file=sys.stderr)
    for them in ([], ["--break-system-packages"], ["--user"]):
        r = subprocess.run([sys.executable, "-m", "pip", "install", "--quiet", goi] + them,
                           capture_output=True, text=True)
        if r.returncode == 0:
            break
    importlib.invalidate_caches()
    return importlib.import_module(ten_module)


def can_pillow():
    return can_goi("PIL", "pillow")
