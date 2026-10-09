"""Cổng kiểm tra TRƯỚC KHI deploy. Có LỖI là trien-khai.py dừng, không đẩy lên.

    python cong-cu/kiem-tra-web.py khach-hang/<slug>

Kiểm:
  web.json  — slug đúng luật Cloudflare · có tên · có ít nhất một cách liên hệ · số điện
              thoại đúng dạng · mã sản phẩm không trùng · ảnh khai trong web.json có thật
              · không còn chữ mẫu ("Lorem", "TODO", "[điền]", "Tên sản phẩm"…)
  màu       — bản sẫm dùng cho nút đạt tương phản ≥4,5 trên nền trắng
  dist/     — mọi trang có title, description, viewport, lang="vi" · mọi <img> có alt
              + width/height · mọi link nội bộ trỏ tới tệp có thật · tệp nào quá nặng
"""
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from thu_vien import SLUG_HOP_LE, bang_mau, so_dien_thoai, tao_slug  # noqa: E402

CHU_MAU = re.compile(r"lorem|ipsum|\btodo\b|\bxxx+\b|\[điền|\[dien|<điền|tên sản phẩm\s*\d*$|mô tả sản phẩm|"
                     r"0123\s?456\s?789|0900\s?000\s?000|example\.com|công ty abc", re.I)
TRANG_NANG_KB = 300
ANH_NANG_KB = 400


class DocHTML(HTMLParser):
    def __init__(self):
        super().__init__()
        self.img, self.link, self.meta, self.title, self.lang, self._t = [], [], {}, "", "", False

    def handle_starttag(self, tag, at):
        a = dict(at)
        if tag == "html":
            self.lang = a.get("lang", "")
        elif tag == "img":
            self.img.append(a)
        elif tag in ("a", "link") and a.get("href"):
            self.link.append(a["href"])
        elif tag == "meta":
            self.meta[a.get("name") or a.get("property") or ""] = a.get("content", "")
        elif tag == "title":
            self._t = True
        if tag == "img" and a.get("srcset"):
            self.link += [x.strip().split(" ")[0] for x in a["srcset"].split(",")]
        if tag == "img" and a.get("src"):
            self.link.append(a["src"])

    def handle_endtag(self, tag):
        if tag == "title":
            self._t = False

    def handle_data(self, d):
        if self._t:
            self.title += d


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)
    goc = Path(sys.argv[1])
    loi, canh = [], []
    p = goc / "web.json"
    if not p.exists():
        print("✘ Không có %s" % p)
        sys.exit(1)
    try:
        d = json.loads(p.read_text("utf-8"))
    except json.JSONDecodeError as ex:
        print("✘ web.json sai cú pháp JSON: %s" % ex)
        sys.exit(1)

    ct, lh, gd = d.get("cong_ty", {}), d.get("lien_he", {}), d.get("giao_dien", {})
    slug = d.get("slug", "")
    if not SLUG_HOP_LE.match(slug):
        loi.append("slug %r sai luật Cloudflare (chữ thường không dấu, số, gạch ngang, ≤58 ký tự) — gợi ý: %s"
                   % (slug, tao_slug(ct.get("ten_ngan") or ct.get("ten") or "")))
    if slug != goc.name:
        canh.append("slug %r khác tên thư mục %r" % (slug, goc.name))
    if not (ct.get("ten") or ct.get("ten_ngan")):
        loi.append("Thiếu tên doanh nghiệp (cong_ty.ten)")
    if not any(lh.get(k) for k in ("dien_thoai", "zalo", "facebook", "email")):
        loi.append("Không có cách liên hệ nào (điện thoại / Zalo / Facebook / email)")
    for k in ("dien_thoai", "zalo"):
        if lh.get(k) and not so_dien_thoai(lh[k]) and not (k == "zalo" and str(lh[k]).startswith("https://zalo.me/")):
            loi.append("lien_he.%s = %r không phải số điện thoại Việt Nam hợp lệ" % (k, lh[k]))
    try:
        b = bang_mau(gd.get("mau_chu_dao") or "#2F5D62")
        if b["tuong_phan_dam"] < 4.5:
            loi.append("Màu nút %s chỉ đạt tương phản %.2f" % (b["dam"], b["tuong_phan_dam"]))
    except ValueError as ex:
        loi.append(str(ex))

    sp = d.get("san_pham") or []
    if not sp:
        loi.append("Chưa có sản phẩm nào")
    ma_da = set()
    for i, s in enumerate(sp):
        ten = s.get("ten") or "(sản phẩm #%d)" % (i + 1)
        if not s.get("ten"):
            loi.append("Sản phẩm #%d thiếu tên" % (i + 1))
        ma = tao_slug(s.get("ma") or s.get("ten") or "")
        if ma in ma_da:
            loi.append("Trùng mã sản phẩm %r — đặt 'ma' khác cho %s" % (ma, ten))
        ma_da.add(ma)
        if not s.get("anh"):
            canh.append("%s chưa có ảnh" % ten)
        for t in s.get("anh") or []:
            if not (goc / "anh" / ("%s-640.webp" % t)).exists():
                loi.append("%s: ảnh %r không có trong anh/ (chạy xu-ly-anh.py? sai tên?)" % (ten, t))
    for x in d.get("chung_nhan") or []:
        if not (goc / "anh" / ("%s-640.webp" % x.get("anh"))).exists():
            loi.append("chung_nhan: ảnh %r không có trong anh/" % x.get("anh"))
    for k, v in (("anh_bia", gd.get("anh_bia")), ("logo", ct.get("logo")), ("anh_gioi_thieu", ct.get("anh_gioi_thieu"))):
        if v and not (goc / "anh" / ("%s-640.webp" % v)).exists():
            loi.append("%s = %r không có trong anh/" % (k, v))

    def quet(o, duong=""):
        if isinstance(o, dict):
            for k, v in o.items():
                quet(v, duong + "." + k)
        elif isinstance(o, list):
            for i, v in enumerate(o):
                quet(v, "%s[%d]" % (duong, i))
        elif isinstance(o, str) and CHU_MAU.search(o):
            loi.append("Còn chữ mẫu ở %s: %r" % (duong.lstrip("."), o[:60]))
    quet(d)

    dist = goc / "dist"
    if not (dist / "index.html").exists():
        loi.append("Chưa dựng web — chạy cong-cu/dung-web.py trước")
    else:
        for trang in sorted(dist.rglob("*.html")):
            ten = trang.relative_to(dist).as_posix()
            ht = trang.read_text("utf-8")
            h = DocHTML()
            h.feed(ht)
            if not h.title.strip():
                loi.append("%s: thiếu <title>" % ten)
            if ten != "404.html" and not h.meta.get("description"):
                loi.append("%s: thiếu mô tả" % ten)
            if "width=device-width" not in h.meta.get("viewport", ""):
                loi.append("%s: thiếu viewport cho điện thoại" % ten)
            if h.lang != "vi":
                loi.append("%s: thiếu lang=\"vi\"" % ten)
            for im in h.img:
                if not (im.get("alt") or "").strip():
                    loi.append("%s: ảnh %s thiếu alt" % (ten, im.get("src")))
                if not (im.get("width") and im.get("height")):
                    canh.append("%s: ảnh %s thiếu width/height (trang sẽ giật khi tải)" % (ten, im.get("src")))
            for l in set(h.link):
                if not l.startswith("/") or l.startswith("//"):
                    continue
                l = l.split("#")[0].split("?")[0]
                if not l:
                    continue
                dich = dist / l.lstrip("/")
                if l.endswith("/"):
                    dich = dich / "index.html"
                if not dich.exists():
                    loi.append("%s: link hỏng %s" % (ten, l))
            kb = len(ht.encode("utf-8")) / 1024
            if kb > TRANG_NANG_KB:
                canh.append("%s nặng %d KB" % (ten, kb))
        for f in (dist / "anh").glob("*"):
            kb = f.stat().st_size / 1024
            if kb > ANH_NANG_KB:
                canh.append("Ảnh %s nặng %d KB" % (f.name, kb))

    for c in canh:
        print("⚠ " + c)
    for l in loi:
        print("✘ " + l)
    if loi:
        print("\nKHÔNG ĐẠT — %d lỗi, %d cảnh báo. Sửa xong chạy lại." % (len(loi), len(canh)))
        sys.exit(1)
    print("✔ ĐẠT — %d sản phẩm, %d cảnh báo." % (len(sp), len(canh)))


if __name__ == "__main__":
    main()
