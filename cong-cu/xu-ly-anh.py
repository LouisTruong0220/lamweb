"""Ảnh gốc của doanh nghiệp → ảnh nhẹ, đúng chiều, sẵn sàng lên web.

    python cong-cu/xu-ly-anh.py khach-hang/<slug>
    python cong-cu/xu-ly-anh.py khach-hang/<slug> --them ~/.claude/uploads/*.jpg

Đọc:  khach-hang/<slug>/anh-goc/   (đi cả thư mục con) + các tệp ở --them
Ghi:  khach-hang/<slug>/anh/<ten>-640.webp     ảnh cho thẻ sản phẩm trên điện thoại
      khach-hang/<slug>/anh/<ten>-1280.webp    ảnh lớn cho trang chi tiết / màn rộng
      khach-hang/<slug>/anh/<ten>.png          CHỈ với ảnh có chữ "logo" trong tên (giữ nền trong)
      khach-hang/<slug>/anh/danh-sach.json     kích thước, hướng ảnh, màu trung bình
      khach-hang/<slug>/anh/bang-xem-N.jpg     tấm ghép nhiều ảnh có ghi tên — Claude đọc
                                               MỘT tấm này là thấy hết sản phẩm, khỏi mở từng ảnh

Tên ảnh = slug của tên tệp gốc ('Bình hoa sen (1).JPG' → 'binh-hoa-sen-1').
Chạy lại nhiều lần không sao: ảnh đã xử lý và không đổi thì bỏ qua.
"""
import argparse
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from thu_vien import tao_slug, can_pillow, can_goi, rgb_sang_hex  # noqa: E402

DUOI_ANH = {".jpg", ".jpeg", ".png", ".webp", ".heic", ".heif", ".bmp", ".tif", ".tiff", ".gif"}
CO_ANH = (640, 1280)
CHAT_LUONG = 80
ANH_QUA_NHO = 500        # cạnh dài dưới mức này → cảnh báo, ảnh sẽ mờ trên điện thoại


def mo_anh(duong):
    can_pillow()
    from PIL import Image, ImageOps
    if duong.suffix.lower() in (".heic", ".heif"):
        heif = can_goi("pillow_heif", "pillow-heif")
        heif.register_heif_opener()
    im = Image.open(duong)
    im = ImageOps.exif_transpose(im)      # ảnh điện thoại hay nằm ngang vì cờ EXIF
    return im


def la_logo(ten):
    return "logo" in ten


def luu_cac_co(im, dich_goc, logo):
    from PIL import Image
    co_trong_suot = im.mode in ("RGBA", "LA") or (im.mode == "P" and "transparency" in im.info)
    if co_trong_suot:
        im = im.convert("RGBA")
    else:
        im = im.convert("RGB")
    for co in CO_ANH:
        ban = im.copy()
        if max(ban.size) > co:
            ban.thumbnail((co, co), Image.LANCZOS)
        ban.save("%s-%d.webp" % (dich_goc, co), "WEBP", quality=CHAT_LUONG, method=6)
    if logo:
        ban = im.copy()
        ban.thumbnail((512, 512), Image.LANCZOS)
        ban.save("%s.png" % dich_goc, "PNG", optimize=True)
    return im


def mau_trung_binh(im):
    from PIL import Image
    return rgb_sang_hex(im.convert("RGB").resize((1, 1), Image.BOX).getpixel((0, 0)))


def bang_xem(thu_muc_anh, cac_ten, moi_tam=20, cot=4, o=300):
    """Ghép ảnh nhỏ có ghi tên thành vài tấm JPG để Claude xem một lượt."""
    from PIL import Image, ImageDraw, ImageFont
    try:
        font = ImageFont.load_default(size=22)
    except TypeError:                      # Pillow cũ
        font = ImageFont.load_default()
    ra = []
    for so, dau in enumerate(range(0, len(cac_ten), moi_tam), 1):
        nhom = cac_ten[dau:dau + moi_tam]
        hang = (len(nhom) + cot - 1) // cot
        tam = Image.new("RGB", (cot * o, hang * (o + 34)), "white")
        ve = ImageDraw.Draw(tam)
        for i, ten in enumerate(nhom):
            x, y = (i % cot) * o, (i // cot) * (o + 34)
            im = Image.open(thu_muc_anh / ("%s-640.webp" % ten)).convert("RGBA")
            im.thumbnail((o - 10, o - 10))
            tam.paste(im, (x + (o - im.width) // 2, y + (o - im.height) // 2), im)
            ve.text((x + 6, y + o + 4), ten[:26], fill="black", font=font)
        dich = thu_muc_anh / ("bang-xem-%d.jpg" % so)
        tam.save(dich, "JPEG", quality=72)
        ra.append(dich)
    return ra


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("thu_muc_khach", help="khach-hang/<slug>")
    ap.add_argument("--them", nargs="*", default=[], help="thêm tệp ảnh ở chỗ khác (vd ~/.claude/uploads/...)")
    ap.add_argument("--lam-lai", action="store_true", help="xử lý lại cả ảnh đã có")
    a = ap.parse_args()

    goc = Path(a.thu_muc_khach)
    vao = goc / "anh-goc"
    ra = goc / "anh"
    ra.mkdir(parents=True, exist_ok=True)

    nguon = []
    if vao.exists():
        nguon += sorted(p for p in vao.rglob("*") if p.is_file() and p.suffix.lower() in DUOI_ANH)
    for t in a.them:
        p = Path(os.path.expanduser(t))
        if p.is_file() and p.suffix.lower() in DUOI_ANH:
            nguon.append(p)
    if not nguon:
        print("✘ Không thấy ảnh nào trong %s (và --them)." % vao)
        print("  Đưa ảnh vào thư mục đó (tải lên GitHub, hoặc chạy cong-cu/tai-anh.py với link Drive) rồi chạy lại.")
        sys.exit(1)

    tep_ds = ra / "danh-sach.json"
    cu = json.loads(tep_ds.read_text("utf-8")) if tep_ds.exists() else {}
    ds, da_dung, canh_bao = {}, set(), []

    for p in nguon:
        ten = tao_slug(p.stem)
        n = 2
        while ten in da_dung:
            ten = "%s-%d" % (tao_slug(p.stem), n)
            n += 1
        da_dung.add(ten)

        dich_goc = ra / ten
        da_co = (ra / ("%s-640.webp" % ten)).exists() and ten in cu
        if da_co and not a.lam_lai and cu[ten].get("nguon") == str(p) \
                and cu[ten].get("mtime") == int(p.stat().st_mtime):
            ds[ten] = cu[ten]
            continue
        try:
            im = mo_anh(p)
        except Exception as e:
            canh_bao.append("Không mở được %s (%s) — bỏ qua" % (p.name, e))
            continue
        w, h = im.size
        im = luu_cac_co(im, dich_goc, la_logo(ten))
        huong = "vuong" if abs(w - h) / max(w, h) < 0.12 else ("ngang" if w > h else "doc")
        ds[ten] = {
            "nguon": str(p), "mtime": int(p.stat().st_mtime),
            "rong": w, "cao": h, "huong": huong,
            "mau_trung_binh": mau_trung_binh(im),
            "logo": la_logo(ten),
            "kb_640": round((ra / ("%s-640.webp" % ten)).stat().st_size / 1024),
        }
        if max(w, h) < ANH_QUA_NHO:
            canh_bao.append("%s chỉ %d×%d px — sẽ mờ, nên xin ảnh gốc lớn hơn" % (p.name, w, h))
        print("✔ %-40s %4d×%-4d %s" % (ten, w, h, huong))

    tep_ds.write_text(json.dumps(ds, ensure_ascii=False, indent=1), "utf-8")
    for cu_tam in ra.glob("bang-xem-*.jpg"):
        cu_tam.unlink()
    tam = bang_xem(ra, [t for t in ds if not ds[t]["logo"]] + [t for t in ds if ds[t]["logo"]])

    print("\nTổng: %d ảnh → %s" % (len(ds), ra))
    print("Bảng xem (đọc để biết ảnh nào là sản phẩm gì): " + ", ".join(str(t) for t in tam))
    for c in canh_bao:
        print("⚠ " + c)


if __name__ == "__main__":
    main()
