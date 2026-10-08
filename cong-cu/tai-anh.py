"""Tải ảnh từ link về khach-hang/<slug>/anh-goc/

    python cong-cu/tai-anh.py khach-hang/<slug> "<link>" ["<link>" ...]

Nhận:
  · thư mục Google Drive CÔNG KHAI   https://drive.google.com/drive/folders/...  (đi cả thư mục con)
  · tệp Google Drive công khai       https://drive.google.com/file/d/.../view
  · link ảnh trực tiếp               https://.../anh.jpg

Lấy TỆP GỐC (đủ nét), không lấy ảnh thu nhỏ của Drive — cổng thumbnail của Drive trả
về cỡ nó đang có sẵn chứ không phải cỡ mình xin, có lần hỏi 1600 px mà nhận 300 px.

⚠ Mạng phiên Claude Code phải cho phép drive.google.com, drive.usercontent.google.com,
  *.googleusercontent.com (xem HUONG-DAN-CLOUDFLARE.md bước 3).
⚠ Thư mục/tệp Drive phải để "Bất kỳ ai có đường liên kết". Để riêng tư thì Google trả
  trang đăng nhập — script nhận ra (không phải ảnh) và báo, không lưu rác.
"""
import re
import sys
import time
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from thu_vien import tao_slug  # noqa: E402

UA = ("Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/126.0 Mobile Safari/537.36")
TOI_DA_ANH = 80
TOI_DA_BYTE = 25_000_000


def lay(url, nhi_phan=False, thu=3):
    for lan in range(thu):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=60) as r:
                d = r.read(TOI_DA_BYTE + 1)
            return d if nhi_phan else d.decode("utf-8", "replace")
        except Exception as ex:
            if lan == thu - 1:
                print("   ! %s: %s" % (type(ex).__name__, str(ex)[:90]))
                return None
            time.sleep(1.5 * (lan + 1))


def la_anh(d):
    if not d or len(d) < 2000:
        return False
    return (d[:3] == b"\xff\xd8\xff" or d[:8] == b"\x89PNG\r\n\x1a\n"
            or (d[:4] == b"RIFF" and d[8:12] == b"WEBP")
            or d[4:12] in (b"ftypheic", b"ftypheix", b"ftypmif1", b"ftypmsf1"))


def duoi(d):
    if d[:8] == b"\x89PNG\r\n\x1a\n":
        return ".png"
    if d[:4] == b"RIFF":
        return ".webp"
    if d[4:8] == b"ftyp":
        return ".heic"
    return ".jpg"


def kieu_link(u):
    m = re.search(r"/folders/([0-9A-Za-z_-]{10,})", u)
    if m:
        return "thu-muc", m.group(1)
    m = re.search(r"/file/d/([0-9A-Za-z_-]{10,})", u) or re.search(r"[?&]id=([0-9A-Za-z_-]{10,})", u)
    if m and "google" in u:
        return "tep", m.group(1)
    return "truc-tiep", u


def mot_tang(id_tm):
    """Bóc một tầng thư mục Drive công khai → [(id, tên, loại)].
    Mỗi mục có data-id="…" và aria-label="<tên> <Loại> Shared" / "<tên> Shared folder"."""
    h = lay("https://drive.google.com/drive/folders/" + id_tm)
    if not h:
        return []
    ids = []
    for m in re.finditer(r'data-id="([0-9A-Za-z_-]{20,})"', h):
        if m.group(1) not in ids:
            ids.append(m.group(1))
    nhan = []
    for nh in re.findall(r'aria-label="([^"]*?\sShared[^"]*)"', h):
        if nh.endswith("Shared folder"):
            nhan.append((nh[: -len(" Shared folder")].strip(), "Folder"))
        else:
            than = re.sub(r"\s+Shared\b.*$", "", nh).strip()
            p = than.rsplit(" ", 1)
            nhan.append((p[0], p[1]) if len(p) == 2 else (than, "File"))
    return [(f, nhan[i][0] if i < len(nhan) else "anh-%d" % i, nhan[i][1] if i < len(nhan) else "File")
            for i, f in enumerate(ids)]


def liet_ke(id_tm, sau=3):
    ra, hang, da = [], [(id_tm, 0, "")], set()
    while hang and len(ra) < TOI_DA_ANH:
        fid, tang, tien_to = hang.pop(0)
        if fid in da:
            continue
        da.add(fid)
        for x in mot_tang(fid):
            if x[2] == "Folder":
                if tang < sau:
                    hang.append((x[0], tang + 1, tien_to + tao_slug(x[1]) + "-"))
            elif x[2] == "Image":
                ra.append((x[0], tien_to + x[1]))
    return ra


def tai_drive(fid):
    u = "https://drive.usercontent.google.com/download?id=%s&export=download" % fid
    d = lay(u, True)
    if d and d[:200].lstrip()[:1] == b"<":                     # cửa xác nhận quét vi rút
        truong = dict(re.findall(r'name="([^"]+)"\s+value="([^"]*)"', d.decode("utf-8", "replace")))
        if "confirm" in truong:
            d = lay(u + "&confirm=%s&uuid=%s" % (truong["confirm"], truong.get("uuid", "")), True)
    if la_anh(d):
        return d
    d = lay("https://drive.google.com/thumbnail?id=%s&sz=w2000" % fid, True)   # đường lui
    return d if la_anh(d) else None


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(2)
    dich = Path(sys.argv[1]) / "anh-goc"
    dich.mkdir(parents=True, exist_ok=True)
    tong = hong = 0
    for link in sys.argv[2:]:
        kieu, ma = kieu_link(link.strip())
        print("→ %s (%s)" % (link[:80], kieu))
        if kieu == "thu-muc":
            muc = liet_ke(ma)
            if not muc:
                print("   ✘ Không thấy ảnh. Thư mục đã để 'Bất kỳ ai có đường liên kết' chưa?")
                hong += 1
                continue
        elif kieu == "tep":
            muc = [(ma, "anh-drive-" + ma[:6])]
        else:
            muc = [(link, Path(link.split("?")[0]).stem or "anh")]
        for ma_tep, ten in muc:
            d = tai_drive(ma_tep) if kieu != "truc-tiep" else lay(ma_tep, True)
            if not la_anh(d):
                print("   ✘ %s — không phải ảnh (tệp riêng tư hoặc link hỏng)" % ten)
                hong += 1
                continue
            ten_tep = tao_slug(re.sub(r"\.(jpe?g|png|webp|heic)$", "", ten, flags=re.I)) + duoi(d)
            (dich / ten_tep).write_bytes(d)
            tong += 1
            print("   ✔ %-44s %5d KB" % (ten_tep, len(d) // 1024))
    print("\nĐã tải %d ảnh vào %s%s" % (tong, dich, (" · %d hỏng" % hong) if hong else ""))
    if tong:
        print("Bước tiếp: python cong-cu/xu-ly-anh.py %s" % sys.argv[1])
    sys.exit(0 if tong else 1)


if __name__ == "__main__":
    main()
