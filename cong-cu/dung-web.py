"""web.json + ảnh đã xử lý → website tĩnh hoàn chỉnh trong khach-hang/<slug>/dist/

    python cong-cu/dung-web.py khach-hang/<slug>
    python cong-cu/dung-web.py khach-hang/<slug> --url https://ten.pages.dev   (trien-khai.py tự truyền)

Tuyến nội dung trang chủ (theo website mẫu Robo Toy — phong cách Flock/Webflow):
    bìa (ảnh sản phẩm thay nhau, thẻ nghiêng theo chuột) → dải chữ chạy → vì sao chọn
    (sáng theo cuộn) → tab khám phá sản phẩm → lưới tất cả sản phẩm → số liệu* → quỹ đạo
    ảnh → lời khách* → giới thiệu (chữ sáng dần) → quy trình → hỏi đáp → nhận báo giá
    (form soạn sẵn tin Zalo/SMS) → chân trang chữ thương hiệu khổng lồ.
    * CHỈ hiện khi web.json có số liệu / lời khách THẬT.

Sinh ra:
    dist/index.html · dist/san-pham/<ma>/index.html · dist/anh/ · dist/og/*.jpg
    dist/404.html · robots.txt · sitemap.xml · _headers · favicon

Mục nào trong web.json để trống thì KHÔNG hiện — không bao giờ in chữ mẫu ra web.
"""
import argparse
import datetime
import html
import json
import re
import shutil
import sys
from pathlib import Path
from urllib.parse import quote

sys.path.insert(0, str(Path(__file__).resolve().parent))
from thu_vien import bang_mau, can_pillow, khong_dau, so_dien_thoai, tao_slug  # noqa: E402

GOC = Path(__file__).resolve().parent
KHUNG = GOC / "khung"

PHONG_CACH = {
    # tên: (phông tiêu đề, độ đậm tiêu đề, bo góc thẻ, tham số Google Fonts)
    "truyen-thong": ("'Lora', Georgia, serif", "600", "20px",
                     "family=Lora:wght@500;600;700&family=Be+Vietnam+Pro:wght@400;500;600;700"),
    "hien-dai":     ("'Be Vietnam Pro', system-ui, sans-serif", "600", "22px",
                     "family=Be+Vietnam+Pro:wght@400;500;600;700"),
    "sang-trong":   ("'Playfair Display', Georgia, serif", "600", "8px",
                     "family=Playfair+Display:wght@500;600;700&family=Be+Vietnam+Pro:wght@400;500;600;700"),
}
PHONG_THAN = "'Be Vietnam Pro', system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif"

NHAN_MAC_DINH = {
    "vi_sao": "Vì sao chọn chúng tôi",
    "kham_pha": "Khám phá sản phẩm",
    "san_pham": "Tất cả sản phẩm",
    "dai_chay": "Sản phẩm của chúng tôi",
    "quy_dao": "",                       # trống → "Bộ sưu tập của <tên>"
    "danh_gia": "Khách hàng nói gì",
    "gioi_thieu": "",                    # trống → "Về <tên>"
    "quy_trinh": "Quy trình làm ra sản phẩm",
    "hoi_dap": "Giải đáp nhanh thắc mắc",
    "lien_he": "Nhận báo giá",
    "nut_chinh": "Xem sản phẩm",
    "nut_bao_gia": "Nhận báo giá",
    "lien_he_gia": "Liên hệ báo giá",
    "tat_ca": "Tất cả",
}

# Biểu tượng Material Icons (Apache 2.0) — SVG nội tuyến, không tải phông biểu tượng.
BIEU = {
    "goi": "M6.62 10.79c1.44 2.83 3.76 5.14 6.59 6.59l2.2-2.2c.27-.27.67-.36 1.02-.24 1.12.37 2.33.57 3.57.57.55 0 1 .45 1 1V20c0 .55-.45 1-1 1-9.39 0-17-7.61-17-17 0-.55.45-1 1-1h3.5c.55 0 1 .45 1 1 0 1.25.2 2.45.57 3.57.11.35.03.74-.25 1.02l-2.2 2.2z",
    "chat": "M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zM6 9h12v2H6V9zm8 5H6v-2h8v2zm4-6H6V6h12v2z",
    "ghim": "M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z",
    "thu": "M20 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 4l-8 5-8-5V6l8 5 8-5v2z",
    "chia_se": "M18 16.08c-.76 0-1.44.3-1.96.77L8.91 12.7c.05-.23.09-.46.09-.7s-.04-.47-.09-.7l7.05-4.11c.54.5 1.25.81 2.04.81 1.66 0 3-1.34 3-3s-1.34-3-3-3-3 1.34-3 3c0 .24.04.47.09.7L8.04 9.81C7.5 9.31 6.79 9 6 9c-1.66 0-3 1.34-3 3s1.34 3 3 3c.79 0 1.5-.31 2.04-.81l7.12 4.16c-.05.21-.08.43-.08.65 0 1.61 1.31 2.92 2.92 2.92s2.92-1.31 2.92-2.92-1.31-2.92-2.92-2.92z",
    "facebook": "M14 13.5h2.5l1-4H14v-2c0-1.03 0-2 2-2h1.5V2.14C17.17 2.1 15.94 2 14.64 2 11.93 2 10 3.66 10 6.7v2.8H7v4h3V22h4v-8.5z",
    "dong_ho": "M11.99 2C6.47 2 2 6.48 2 12s4.47 10 9.99 10C17.52 22 22 17.52 22 12S17.52 2 11.99 2zM12 20c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8zm.5-13H11v6l5.25 3.15.75-1.23-4.5-2.67z",
    "quay_lai": "M20 11H7.83l5.59-5.59L12 4l-8 8 8 8 1.41-1.41L7.83 13H20v-2z",
}
MUI_TEN = '<svg viewBox="0 0 16 16"><path d="M4 12L12 4M5 4h7v7" stroke="currentColor" fill="none" stroke-width="1.8"/></svg>'


def svg(ten, lop=""):
    return '<svg viewBox="0 0 24 24" aria-hidden="true"%s><path d="%s"/></svg>' % (
        ' class="%s"' % lop if lop else "", BIEU[ten])


def e(s):
    return html.escape(str(s or ""), quote=True)


def doan_van(s):
    """Chuỗi có dòng trống → nhiều <p>; danh sách → mỗi phần tử một <p>."""
    if not s:
        return ""
    cac = s if isinstance(s, list) else re.split(r"\n\s*\n", str(s))
    return "".join("<p>%s</p>" % e(x.strip()).replace("\n", "<br>") for x in cac if str(x).strip())


def cat_chu(s, n=158):
    s = re.sub(r"\s+", " ", str(s or "")).strip()
    return s if len(s) <= n else s[: n - 1].rsplit(" ", 1)[0] + "…"


def nut(href, chu, kieu="chinh", mui=None, bieu=None, them=""):
    """Nút hiệu ứng của mẫu: chữ cuộn lên khi rê chuột + mũi tên trượt chéo.
    Chữ lặp hai lần cho hiệu ứng cuộn → đọc màn hình dùng aria-label, phần lặp aria-hidden."""
    if mui is None:
        mui = kieu == "chinh"
    the = "button" if href is None else "a"
    thuoc = ' href="%s"' % e(href) if href is not None else ""
    return ('<{t}{h} class="btn btn-{k}" aria-label="{c}"{x}>{b}<span class="roll" aria-hidden="true"><span>{c}</span>'
            '<span>{c}</span></span>{m}</{t}>').format(
        t=the, h=thuoc, k=kieu, c=e(chu), x=them, b=svg(bieu, "bt") if bieu else "",
        m='<span class="mui" aria-hidden="true">%s%s</span>' % (MUI_TEN, MUI_TEN) if mui else "")


class Dung:
    def __init__(self, thu_muc, url):
        self.goc = Path(thu_muc)
        self.d = json.loads((self.goc / "web.json").read_text("utf-8"))
        self.anh_vao = self.goc / "anh"
        self.ra = self.goc / "dist"
        self.url = (url or self.d.get("dia_chi_web") or "").rstrip("/")
        self.ct = self.d.get("cong_ty", {})
        self.lh = self.d.get("lien_he", {})
        self.gd = self.d.get("giao_dien", {})
        self.nhan = dict(NHAN_MAC_DINH, **(self.d.get("nhan") or {}))
        self.ten = self.ct.get("ten_ngan") or self.ct.get("ten") or "Doanh nghiệp"
        self.mau = bang_mau(self.gd.get("mau_chu_dao") or "#2F5D62")
        self.pc = PHONG_CACH.get(self.gd.get("phong_cach"), PHONG_CACH["truyen-thong"])
        self.sp = [s for s in self.d.get("san_pham", []) if s.get("ten")]
        for s in self.sp:
            s["ma"] = tao_slug(s.get("ma") or s["ten"])
        self.anh_dung = set()
        self.kich_thuoc = {}
        self.dt = so_dien_thoai(self.lh.get("dien_thoai"))
        z = str(self.lh.get("zalo") or "").strip()
        self.zalo_url = z if z.startswith("http") else ""      # Zalo Official Account: zalo.me/s/...
        self.zalo = ((self.lh.get("ten_zalo") or "Zalo Official Account", "", "") if self.zalo_url
                     else so_dien_thoai(z) or self.dt)
        self.css = (KHUNG / "giao-dien.css").read_text("utf-8")
        self.js = (KHUNG / "tuong-tac.js").read_text("utf-8")

    # ─── ảnh ───
    def co_anh(self, ten):
        return bool(ten) and (self.anh_vao / ("%s-640.webp" % ten)).exists()

    def kt(self, ten, co):
        k = (ten, co)
        if k not in self.kich_thuoc:
            from PIL import Image
            with Image.open(self.anh_vao / ("%s-%d.webp" % (ten, co))) as im:
                self.kich_thuoc[k] = im.size
        return self.kich_thuoc[k]

    def img(self, ten, alt, sizes, lazy=True, them=""):
        """<img> có srcset 640/1280 + width/height để trang không giật khi ảnh tải."""
        self.anh_dung.add(ten)
        w, h = self.kt(ten, 640)
        return ('<img src="/anh/{t}-640.webp" srcset="/anh/{t}-640.webp 640w, /anh/{t}-1280.webp 1280w" '
                'sizes="{s}" width="{w}" height="{h}" alt="{a}"{l}{x}>').format(
            t=ten, s=sizes, w=w, h=h, a=e(alt), x=them,
            l=' loading="lazy" decoding="async"' if lazy else ' fetchpriority="high"')

    def anh_sp(self, s):
        return [t for t in (s.get("anh") or []) if self.co_anh(t)]

    def anh_dau_sp(self, s):
        a = self.anh_sp(s)
        return a[0] if a else None

    def sp_noi_bat(self, toi_da=5):
        nb = [s for s in self.sp if s.get("noi_bat") and self.anh_dau_sp(s)]
        if len(nb) < 2:
            nb += [s for s in self.sp if s not in nb and self.anh_dau_sp(s)]
        return nb[:toi_da]

    def anh_bia(self):
        t = self.gd.get("anh_bia")
        if self.co_anh(t):
            return t
        nb = self.sp_noi_bat(1)
        return self.anh_dau_sp(nb[0]) if nb else None

    def logo(self):
        t = self.ct.get("logo")
        return t if self.co_anh(t) else None

    def gia(self, s, lop="gia"):
        return ('<span class="%s">%s</span>' % (lop, e(s["gia"])) if s.get("gia")
                else '<span class="%s lien-he">%s</span>' % (lop, e(self.nhan["lien_he_gia"])))

    def dac_diem(self, s):
        """Danh sách gạch đầu dòng của một sản phẩm: dac_diem, rồi tới thông số có sẵn."""
        ds = [x for x in (s.get("dac_diem") or []) if x]
        if not ds:
            for k, nh in (("chat_lieu", "Chất liệu"), ("kich_thuoc", "Kích thước"), ("mau_sac", "Màu sắc")):
                if s.get(k):
                    ds.append("%s: %s" % (nh, s[k]))
        return ds

    # ─── liên kết liên hệ ───
    def link_zalo(self):
        if self.zalo_url:
            return self.zalo_url
        return "https://zalo.me/%s" % self.zalo[2] if self.zalo else ""

    def link_goi(self):
        return "tel:%s" % self.dt[1] if self.dt else ""

    def link_ban_do(self):
        if self.lh.get("ban_do"):
            return self.lh["ban_do"]
        if self.lh.get("dia_chi"):
            return "https://www.google.com/maps/search/?api=1&query=" + quote(self.lh["dia_chi"])
        return ""

    # ─── khung trang ───
    def dau_html(self, tieu_de, mo_ta, duong, anh_og, json_ld):
        tuyet_doi = (self.url + duong) if self.url else ""
        og_anh = (self.url + anh_og) if (self.url and anh_og) else ""
        bien = (":root{--c:%(chinh)s;--cd:%(dam)s;--cd2:%(dam_2)s;--cdh:%(dam_hon)s;--rgb:%(rgb)s;--cn:%(nhat)s;"
                "--cnv:%(nhat_vua)s;--cv:%(vien)s;" % self.mau) + \
               "--f-tieu-de:%s;--w-tieu-de:%s;--r-xl:%s;--f-than:%s}" % (self.pc[0], self.pc[1], self.pc[2], PHONG_THAN)
        r = ['<!doctype html><html lang="vi"><head><meta charset="utf-8">',
             '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">',
             "<title>%s</title>" % e(tieu_de),
             '<meta name="description" content="%s">' % e(mo_ta),
             '<meta name="theme-color" content="%s">' % self.mau["dam"],
             '<meta name="format-detection" content="telephone=no">',
             "<script>document.documentElement.classList.add('js')</script>"]
        if tuyet_doi:
            r.append('<link rel="canonical" href="%s">' % e(tuyet_doi))
            r.append('<meta property="og:url" content="%s">' % e(tuyet_doi))
        r += ['<meta property="og:type" content="website">',
              '<meta property="og:locale" content="vi_VN">',
              '<meta property="og:site_name" content="%s">' % e(self.ten),
              '<meta property="og:title" content="%s">' % e(tieu_de),
              '<meta property="og:description" content="%s">' % e(mo_ta)]
        if og_anh:
            r += ['<meta property="og:image" content="%s">' % e(og_anh),
                  '<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">',
                  '<meta name="twitter:card" content="summary_large_image">']
        r += ['<link rel="icon" href="/favicon.svg" type="image/svg+xml">',
              '<link rel="apple-touch-icon" href="/apple-touch-icon.png">',
              '<link rel="preconnect" href="https://fonts.googleapis.com">',
              '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>',
              '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?%s&display=swap">' % self.pc[3],
              "<style>%s\n%s</style>" % (bien, self.css)]
        for ld in (json_ld if isinstance(json_ld, list) else [json_ld]):
            if ld:
                r.append('<script type="application/ld+json">%s</script>'
                         % json.dumps(ld, ensure_ascii=False).replace("</", "<\\/"))
        r.append('</head><body><div class="con-tro" aria-hidden="true"></div>')
        return "".join(r)

    def muc_menu(self):
        m = [("/#san-pham", "Sản phẩm")]
        if self.ct.get("gioi_thieu"):
            m.append(("/#gioi-thieu", "Về chúng tôi"))
        if self.d.get("hoi_dap"):
            m.append(("/#hoi-dap", "Hỏi đáp"))
        m.append(("/#lien-he", "Liên hệ"))
        return m

    def dau_trang(self, trang_chu):
        lg = self.logo()
        hieu = (self.img(lg, "Logo " + self.ten, "120px", lazy=False) if lg
                else '<i aria-hidden="true">%s</i>' % e(khong_dau(self.ten)[:1].upper()))
        menu = "".join('<a href="%s">%s</a>' % (h, e(n)) for h, n in self.muc_menu())
        return ('<header class="nav%s"><div class="khung nav-in">'
                '<a class="logo" href="/" aria-label="%s — trang chủ">%s<b>%s</b></a>'
                '<nav class="menu" id="menu" aria-label="Mục chính">%s</nav>'
                '<div class="nav-cta">%s<button class="burger" type="button" aria-label="Mở menu" aria-controls="menu" '
                'aria-expanded="false"><span></span><span></span><span></span></button></div></div></header>') % (
            "" if trang_chu else " dac", e(self.ten), hieu, e(self.ten), menu,
            nut("/#lien-he", self.nhan["nut_bao_gia"]).replace('class="btn', 'class="an-dt btn', 1))

    def thanh_day(self, san_pham=None):
        """Thanh hành động dính đáy màn hình điện thoại — trong tầm ngón cái."""
        n = []
        if san_pham and self.zalo:
            cau = "Chào %s, tôi muốn hỏi về sản phẩm: %s" % (self.ten, san_pham["ten"])
            if self.url:
                cau += " — %s/san-pham/%s/" % (self.url, san_pham["ma"])
            n.append('<a class="chinh ngang" href="%s" data-chep="%s" aria-label="Hỏi giá qua Zalo">%s<span>Hỏi giá qua Zalo</span></a>'
                     % (self.link_zalo(), e(cau), svg("chat")))
            if self.dt:
                n.append('<a href="%s" aria-label="Gọi điện">%s<span>Gọi</span></a>' % (self.link_goi(), svg("goi")))
            return '<nav class="thanh-day" aria-label="Liên hệ nhanh">%s</nav>' % "".join(n)
        if self.dt:
            n.append('<a class="chinh" href="%s" aria-label="Gọi ngay">%s<span>Gọi ngay</span></a>' % (self.link_goi(), svg("goi")))
        if self.zalo:
            n.append('<a href="%s" aria-label="Nhắn Zalo">%s<span>Zalo</span></a>' % (self.link_zalo(), svg("chat")))
        if self.link_ban_do():
            n.append('<a href="%s" target="_blank" rel="noopener" aria-label="Chỉ đường">%s<span>Chỉ đường</span></a>'
                     % (e(self.link_ban_do()), svg("ghim")))
        elif self.lh.get("facebook"):
            n.append('<a href="%s" target="_blank" rel="noopener" aria-label="Facebook">%s<span>Facebook</span></a>'
                     % (e(self.lh["facebook"]), svg("facebook")))
        return '<nav class="thanh-day" aria-label="Liên hệ nhanh">%s</nav>' % "".join(n) if n else ""

    def chan_trang(self):
        nam = datetime.date.today().year
        lg = self.logo()
        hieu = (self.img(lg, "Logo " + self.ten, "120px") if lg
                else '<i aria-hidden="true">%s</i>' % e(khong_dau(self.ten)[:1].upper()))
        cot_sp = "".join('<li><a href="/san-pham/%s/">%s</a></li>' % (s["ma"], e(s["ten"])) for s in self.sp[:5])
        lh = []
        if self.dt:
            lh.append('<li><a href="%s">Gọi %s</a></li>' % (self.link_goi(), e(self.dt[0])))
        if self.zalo:
            lh.append('<li><a href="%s">%s</a></li>' % (self.link_zalo(), e(self.zalo[0] if self.zalo_url else "Zalo " + self.zalo[0])))
        if self.lh.get("facebook"):
            lh.append('<li><a href="%s" target="_blank" rel="noopener">Facebook</a></li>' % e(self.lh["facebook"]))
        if self.lh.get("email"):
            lh.append('<li><a href="mailto:%s">%s</a></li>' % (e(self.lh["email"]), e(self.lh["email"])))
        if self.lh.get("dia_chi"):
            lh.append('<li><a href="%s" target="_blank" rel="noopener">%s</a></li>' % (e(self.link_ban_do()), e(self.lh["dia_chi"])))
        chu_lon = self.ten.upper()
        co = min(16.0, 125.0 / max(len(chu_lon), 1))   # ước lượng; JS chỉnh lại cho vừa khít
        return ('<footer><div class="khung"><div class="foot">'
                '<div><a class="logo" href="/">%s<b>%s</b></a>%s</div>'
                '<div><h5>Sản phẩm</h5><ul>%s</ul></div>'
                '%s</div>'
                '<div class="chu-lon" aria-hidden="true" style="--co-chu-lon:%.1fvw">%s</div>'
                '<div class="copy"><span>© %d %s</span>%s</div></div></footer>') % (
            hieu, e(self.ten),
            "<p>%s</p>" % e(self.ct.get("mo_ta_ngan")) if self.ct.get("mo_ta_ngan") else "",
            cot_sp, '<div><h5>Liên hệ</h5><ul>%s</ul></div>' % "".join(lh) if lh else "",
            co, e(chu_lon), nam, e(self.ct.get("ten") or self.ten),
            "<span>%s</span>" % e(self.d["chan_trang"]) if self.d.get("chan_trang") else "")

    def cuoi_html(self):
        return "<script>%s</script></body></html>" % self.js

    # ─── thẻ sản phẩm ───
    def the_sp(self, s, tre=0):
        t = self.anh_dau_sp(s)
        anh = (self.img(t, s["ten"], "(min-width:992px) 25vw, (min-width:600px) 33vw, 50vw") if t
               else '<span class="chua-anh">%s<small>Ảnh đang cập nhật</small></span>' % e(self.ten))
        return ('<a class="the-sp reveal%s" href="/san-pham/%s/" data-dm="%s"><div class="o-anh">%s</div>'
                '<div class="chu"><h3>%s</h3>%s<span class="xem">Xem chi tiết <span aria-hidden="true">→</span></span></div></a>') % (
            " d%d" % tre if tre else "", s["ma"], e(s.get("danh_muc", "")), anh, e(s["ten"]), self.gia(s))

    # ═════════ TRANG CHỦ — từng mục ═════════
    def muc_bia(self):
        nb = self.sp_noi_bat(5)
        bia = self.anh_bia()
        anh_xoay = []
        if bia:
            anh_xoay.append((bia, next((s for s in self.sp if bia in (s.get("anh") or [])), None)))
        for s in nb:
            t = self.anh_dau_sp(s)
            if t and t not in [a for a, _ in anh_xoay]:
                anh_xoay.append((t, s))

        def nhan_anh(s):
            if not s:
                return "<span>%s</span>" % e(self.ten)
            return "<span>%s</span><small>%s</small>" % (e(s["ten"]), e(s.get("gia") or self.nhan["lien_he_gia"]))

        imgs = []
        for i, (t, s) in enumerate(anh_xoay):
            imgs.append(self.img(t, s["ten"] if s else self.ct.get("mo_ta_anh_bia") or self.ten,
                                 "(min-width:992px) 45vw, 92vw", lazy=i > 0,
                                 them=' class="hien"' * (i == 0) + ' data-nhan="%s"' % e(nhan_anh(s))))
        tieu_de = self.ct.get("tieu_de_bia") or self.ten
        nhan_manh = self.ct.get("tieu_de_bia_nhan")
        h1 = e(tieu_de)
        if nhan_manh and nhan_manh in tieu_de:
            h1 = h1.replace(e(nhan_manh), '<span class="grad-text">%s</span>' % e(nhan_manh), 1)
        elif not self.ct.get("tieu_de_bia"):
            h1 = '<span class="grad-text">%s</span>' % h1
        badge = ""
        if self.ct.get("dong_tren_ten"):
            badge = '<div class="badge reveal">%s<span>%s</span></div>' % (
                "<b>%s</b>" % e(self.ct["nhan_badge"]) if self.ct.get("nhan_badge") else "", e(self.ct["dong_tren_ten"]))
        diem = [x for x in (self.ct.get("diem_bia") or []) if x][:3]
        nut_phu = (nut(self.link_zalo(), "Nhắn Zalo", "ma", bieu="chat") if self.zalo
                   else nut(self.link_goi(), "Gọi ngay", "ma", bieu="goi") if self.dt else "")
        so_dm = len({s.get("danh_muc") for s in self.sp if s.get("danh_muc")})
        hang = ['<div><span>Sản phẩm</span><b>%d mẫu</b></div>' % len(self.sp)]
        if so_dm > 1:
            hang.append('<div><span>Nhóm hàng</span><b>%d nhóm</b></div>' % so_dm)
        elif self.zalo:
            hang.append('<div><span>Báo giá</span><b>Qua Zalo</b></div>')
        if self.dt:
            hang.append('<div class="o3"><span>Hotline</span><b>%s</b></div>' % e(self.dt[0]))
        noi = ""
        if len(nb) >= 2:
            noi = ('<div class="noi n1">%s<small>%s</small></div><div class="noi n2">%s<small>%s</small></div>' % (
                e(nb[0]["ten"]), e(nb[0].get("gia") or self.nhan["lien_he_gia"]),
                e(nb[1]["ten"]), e(nb[1].get("gia") or self.nhan["lien_he_gia"])))
        san_khau = ""
        if imgs:
            san_khau = ('<div class="san-khau reveal d2"><div class="the-bia">'
                        '<div class="the-bia-dau"><span><span class="cham-song"></span>%s</span><span>%d mẫu sản phẩm</span></div>'
                        '<div class="bia-anh">%s<div class="nhan-anh">%s</div></div>'
                        '<div class="the-bia-hang">%s</div></div>%s</div>') % (
                e(self.ten), len(self.sp), "".join(imgs), nhan_anh(anh_xoay[0][1]), "".join(hang), noi)
        return ('<section class="hero"><div class="hero-nen" aria-hidden="true"><div class="luoi"></div><div class="sang"></div>'
                '<div class="sang s2"></div></div><div class="khung hero-wrap"><div>%s'
                '<h1 class="reveal d1">%s</h1>%s%s<div class="hero-nut reveal d4">%s%s</div></div>%s</div></section>') % (
            badge, h1,
            '<p class="sub reveal d2">%s</p>' % e(self.ct.get("khau_hieu") or self.ct.get("mo_ta_ngan"))
            if (self.ct.get("khau_hieu") or self.ct.get("mo_ta_ngan")) else "",
            '<div class="hero-diem reveal d3">%s</div>' % "".join('<div><i>✓</i>%s</div>' % e(x) for x in diem) if diem else "",
            nut("#san-pham", self.nhan["nut_chinh"]), nut_phu, san_khau)

    def muc_dai_chay(self):
        chu = [s["ten"] for s in self.sp]
        for s in self.sp:
            if s.get("danh_muc") and s["danh_muc"] not in chu:
                chu.append(s["danh_muc"])
        if len(chu) < 3:
            return ""
        return ('<section class="dai-chay" aria-label="%s"><div class="khung"><p>%s</p><div class="marquee">'
                '<div class="marquee-track">%s</div></div></div></section>') % (
            e(self.nhan["dai_chay"]), e(self.nhan["dai_chay"]), "".join("<span>%s</span>" % e(x) for x in chu))

    def muc_vi_sao(self):
        nb = [x for x in self.d.get("diem_noi_bat") or [] if x.get("tieu_de")]
        if len(nb) < 2:
            return ""
        kho_anh = [t for s in self.sp for t in self.anh_sp(s)] or [None]
        muc, canh = [], []
        for i, x in enumerate(nb):
            t = x.get("anh") if self.co_anh(x.get("anh")) else kho_anh[i % len(kho_anh)]
            anh_nho = '<div class="anh-muc">%s</div>' % self.img(t, x["tieu_de"], "92vw") if t else ""
            muc.append('<div class="chon-item%s" data-i="%d"><div class="so">%02d</div><div><h4>%s</h4>%s%s</div></div>' % (
                " active" if i == 0 else "", i, i + 1, e(x["tieu_de"]),
                "<p>%s</p>" % e(x["mo_ta"]) if x.get("mo_ta") else "", anh_nho))
            if t:
                canh.append('<div class="canh%s">%s<b>%s</b></div>' % (
                    " on" if i == 0 else "", self.img(t, x["tieu_de"], "45vw"), e(x["tieu_de"])))
        return ('<section class="cach" id="vi-sao"><div class="khung"><div class="dau-muc reveal"><h2>%s</h2>%s</div>'
                '<div class="chon-wrap"><div><div class="chon-list">%s</div><div class="chon-cta reveal">%s</div></div>'
                '<div class="chon-vis" aria-hidden="true">%s</div></div></div></section>') % (
            e(self.nhan["vi_sao"]),
            "<p>%s</p>" % e(self.ct["phu_de_vi_sao"]) if self.ct.get("phu_de_vi_sao") else "",
            "".join(muc), nut("#lien-he", self.nhan["nut_bao_gia"]), "".join(canh))

    def muc_kham_pha(self):
        ds = self.sp_noi_bat(4)
        if len(ds) < 2:
            return ""
        tabs, panes = [], []
        for i, s in enumerate(ds):
            tabs.append('<button class="tab-link%s" type="button" role="tab" data-t="%d" aria-selected="%s">%s</button>' % (
                " cur" if i == 0 else "", i, "true" if i == 0 else "false", e(s["ten"])))
            ticks = "".join('<div><i>✓</i>%s</div>' % e(x) for x in self.dac_diem(s))
            panes.append('<div class="tab-pane%s" role="tabpanel"><div><h3>%s</h3>%s%s%s%s</div><div class="pane-anh">%s</div></div>' % (
                " cur" if i == 0 else "", e(s["ten"]),
                "<p>%s</p>" % e(cat_chu(s.get("mo_ta"), 260)) if s.get("mo_ta") else "",
                '<p class="gia-tab">%s</p>' % e(s["gia"]) if s.get("gia") else "",
                '<div class="ticks">%s</div>' % ticks if ticks else '<div style="height:22px"></div>',
                nut("/san-pham/%s/" % s["ma"], "Xem chi tiết"),
                self.img(self.anh_dau_sp(s), s["ten"], "(min-width:992px) 45vw, 92vw")))
        return ('<section class="cach" id="kham-pha"><div class="khung"><div class="dau-muc reveal"><h2>%s</h2></div>'
                '<div class="tabs-menu reveal" role="tablist"><span class="tab-pill" aria-hidden="true"></span>%s</div>'
                '<div class="reveal">%s</div></div></section>') % (
            e(self.nhan["kham_pha"]), "".join(tabs), "".join(panes))

    def muc_luoi(self):
        dm = []
        for s in self.sp:
            if s.get("danh_muc") and s["danh_muc"] not in dm:
                dm.append(s["danh_muc"])
        loc = ""
        if len(dm) > 1:
            loc = ('<div class="loc" role="group" aria-label="Lọc theo nhóm">'
                   '<button type="button" data-dm="*" aria-pressed="true">%s</button>%s</div>') % (
                e(self.nhan["tat_ca"]),
                "".join('<button type="button" data-dm="%s" aria-pressed="false">%s</button>' % (e(x), e(x)) for x in dm))
        thu_tu = sorted(self.sp, key=lambda x: not x.get("noi_bat"))
        return ('<section class="cach" id="san-pham"><div class="khung"><div class="dau-muc reveal"><h2>%s</h2>'
                '<p>%d mẫu — chạm vào sản phẩm để xem ảnh lớn và hỏi giá</p></div>%s<div class="luoi-sp" id="luoi-sp">%s</div>'
                '</div></section>') % (
            e(self.nhan["san_pham"]), len(self.sp), loc,
            "".join(self.the_sp(s, i % 4) for i, s in enumerate(thu_tu)))

    def muc_so_lieu(self):
        sl = [x for x in self.d.get("so_lieu") or [] if x.get("nhan") and str(x.get("so", "")).strip()]
        if not sl:
            return ""
        o = []
        for x in sl[:4]:
            so = re.sub(r"[^\d]", "", str(x["so"]))
            o.append('<div class="o-so"><div class="n grad-text"><span class="dem" data-to="%s">%s</span>%s</div><p>%s</p></div>' % (
                so, e(x["so"]), e(x.get("hau_to", "")), e(x["nhan"])))
        return ('<section style="padding:10px 0 60px"><div class="khung"><div class="luoi-so reveal" style="--so-o:%d">%s</div>'
                '</div></section>') % (len(o), "".join(o))

    def muc_quy_dao(self):
        anh = []
        for s in self.sp:
            t = self.anh_dau_sp(s)
            if t:
                anh.append((t, s))
        if len(anh) < 4:
            return ""
        ngoai = [("50%", "0"), ("100%", "50%"), ("50%", "100%"), ("0", "50%")]
        trong = [("85%", "15%"), ("15%", "85%"), ("15%", "15%")]

        def nut_qd(vt, t, s):
            return '<a class="nut-qd" href="/san-pham/%s/" style="left:%s;top:%s" aria-label="%s">%s</a>' % (
                s["ma"], vt[0], vt[1], e(s["ten"]), self.img(t, s["ten"], "80px"))
        v1 = "".join(nut_qd(ngoai[i], *anh[i]) for i in range(min(4, len(anh))))
        v2 = "".join(nut_qd(trong[i], *anh[4 + i]) for i in range(min(3, len(anh) - 4)))
        lg = self.logo()
        loi = self.img(lg, self.ten, "160px") if lg else e(khong_dau(self.ten)[:1].upper())
        tieu_de = self.nhan["quy_dao"] or "Bộ sưu tập của %s" % self.ten
        return ('<section class="cach muc-qd"><div class="khung"><div class="dau-muc reveal"><h2>%s</h2><p>%d mẫu sản phẩm — chạm để xem</p></div>'
                '<div class="quy-dao reveal"><div class="vong">%s</div><div class="vong v2">%s</div><div class="vong v3"></div>'
                '<div class="loi">%s</div></div></div></section>') % (e(tieu_de), len(anh), v1, v2, loi)

    def muc_danh_gia(self):
        dg = [x for x in self.d.get("danh_gia") or [] if x.get("loi") and x.get("ten")]
        if len(dg) < 2:
            return ""

        def the(x):
            return ('<div class="t-card"><div class="q">“</div><p>%s</p><div class="t-who"><i>%s</i><div><b>%s</b>%s</div></div></div>'
                    % (e(x["loi"]), e(khong_dau(x["ten"]).split()[-1][:1].upper()), e(x["ten"]),
                       "<small>%s</small>" % e(x["vai"]) if x.get("vai") else ""))
        cot = []
        for c in range(3):
            ds = dg[c:] + dg[:c]
            the_html = "".join(the(x) for x in ds)
            cot.append('<div class="cot c%d">%s%s</div>' % (c + 1, the_html, the_html))
        return ('<section class="cach"><div class="khung"><div class="dau-muc reveal"><h2>%s</h2></div>'
                '<div class="testi reveal">%s</div></div></section>') % (e(self.nhan["danh_gia"]), "".join(cot))

    def muc_gioi_thieu(self):
        gt = self.ct.get("gioi_thieu")
        if not gt:
            return ""
        cac = gt if isinstance(gt, list) else re.split(r"\n\s*\n", str(gt))
        cac = [x.strip() for x in cac if str(x).strip()]
        agt = self.ct.get("anh_gioi_thieu")
        return ('<section class="cach" id="gioi-thieu"><div class="khung gt-wrap"><span class="the-nhan reveal">%s</span><div>'
                '<p class="scrub">%s</p>%s%s</div></div></section>') % (
            e(self.nhan["gioi_thieu"] or "Về %s" % self.ten), e(cac[0]),
            '<div class="gt-them reveal">%s</div>' % "".join("<p>%s</p>" % e(x) for x in cac[1:]) if len(cac) > 1 else "",
            '<div class="gt-anh reveal">%s</div>' % self.img(agt, self.ct.get("mo_ta_anh_gioi_thieu") or "Xưởng của " + self.ten,
                                                             "(min-width:992px) 70vw, 100vw") if self.co_anh(agt) else "")

    def muc_quy_trinh(self):
        qt = [x for x in self.d.get("quy_trinh") or [] if x.get("tieu_de")]
        if not qt:
            return ""
        return ('<section class="cach" id="quy-trinh"><div class="khung"><div class="dau-muc reveal"><h2>%s</h2></div>'
                '<ol class="quy-trinh">%s</ol></div></section>') % (
            e(self.nhan["quy_trinh"]), "".join(
                '<li class="reveal"><h4>%s</h4>%s</li>' % (e(x["tieu_de"]), "<p>%s</p>" % e(x["mo_ta"]) if x.get("mo_ta") else "")
                for x in qt))

    def muc_chung_nhan(self):
        cn = [x for x in self.d.get("chung_nhan") or [] if self.co_anh(x.get("anh"))]
        if not cn:
            return ""
        o = "".join('<a class="o-cn reveal%s" href="/anh/%s-1280.webp" aria-label="Xem %s"><span class="khung-cn">%s</span><b>%s</b></a>' % (
            " d%d" % (i % 4) if i % 4 else "", x["anh"], e(x.get("ten") or "giấy chứng nhận"),
            self.img(x["anh"], x.get("ten") or "Giấy chứng nhận", "(min-width:992px) 20vw, 45vw"), e(x.get("ten") or ""))
            for i, x in enumerate(cn))
        return ('<section class="cach nen-nhat" id="chung-nhan"><div class="khung"><div class="dau-muc reveal"><h2>%s</h2>%s</div>'
                '<div class="luoi-cn">%s</div></div></section>') % (
            e(self.nhan.get("chung_nhan") or "Chứng nhận chất lượng"),
            "<p>%s</p>" % e(self.ct["phu_de_chung_nhan"]) if self.ct.get("phu_de_chung_nhan") else "", o)

    def muc_hoi_dap(self):
        hd = [x for x in self.d.get("hoi_dap") or [] if x.get("hoi") and x.get("dap")]
        if not hd:
            return ""
        return ('<section class="cach" id="hoi-dap"><div class="khung"><div class="dau-muc reveal"><h2>%s</h2></div>'
                '<div class="faq-list">%s</div></div></section>') % (
            e(self.nhan["hoi_dap"]), "".join(
                '<div class="faq-item reveal%s"><button class="faq-q" type="button" aria-expanded="%s">%s<span class="pm" aria-hidden="true"></span></button>'
                '<div class="faq-a"><div><p>%s</p></div></div></div>' % (
                    " mo" if i == 0 else "", "true" if i == 0 else "false", e(x["hoi"]), e(x["dap"]))
                for i, x in enumerate(hd)))

    def muc_lien_he(self):
        dong = []

        def them(link, bieu, nho, lon, ngoai=False):
            the = "a" if link else "div"
            thuoc = ' href="%s"%s' % (e(link), ' target="_blank" rel="noopener"' if ngoai else "") if link else ""
            dong.append('<li><%s%s><span class="bieu">%s</span><span><small>%s</small><strong>%s</strong></span></%s></li>'
                        % (the, thuoc, svg(bieu), e(nho), e(lon), the))
        if self.dt:
            them(self.link_goi(), "goi", "Gọi điện", self.dt[0])
        if self.zalo:
            them(self.link_zalo(), "chat", "Nhắn Zalo", self.zalo[0])
        if self.lh.get("facebook"):
            them(self.lh["facebook"], "facebook", "Facebook", self.lh.get("ten_facebook") or "Trang Facebook", True)
        if self.lh.get("email"):
            them("mailto:" + self.lh["email"], "thu", "Email", self.lh["email"])
        if self.lh.get("dia_chi"):
            them(self.link_ban_do(), "ghim", "Địa chỉ — chạm để chỉ đường", self.lh["dia_chi"], True)
        if self.lh.get("gio_mo_cua"):
            them("", "dong_ho", "Giờ mở cửa", self.lh["gio_mo_cua"])
        for x in self.lh.get("khac") or []:
            if not (x.get("nhan") and x.get("gia_tri")):
                continue
            link = x.get("link") or ""
            if not link and x.get("bieu") == "goi" and so_dien_thoai(x["gia_tri"]):
                link = "tel:" + so_dien_thoai(x["gia_tri"])[1]
            them(link, x.get("bieu") if x.get("bieu") in BIEU else "ghim", x["nhan"], x["gia_tri"],
                 link.startswith("http"))
        if not dong:
            return ""
        form = ""
        if self.zalo or self.dt:
            lua_chon = "".join("<option>%s</option>" % e(s["ten"]) for s in self.sp) + "<option>Sản phẩm khác</option>"
            gui = []
            if self.zalo:
                gui.append(nut(None, "Gửi qua Zalo", them=' type="submit" data-cach="zalo"'))
            if self.dt:
                gui.append(nut(None, "Gửi tin nhắn SMS", "ma", them=' type="submit" data-cach="sms"'))
            form = ('<form class="dat" data-ten="%s" data-zalo="%s" data-sdt="%s" novalidate>'
                    '<label>Họ và tên*<input name="ten" required autocomplete="name" placeholder="Họ tên của Quý khách"></label>'
                    '<label>Số điện thoại*<input name="sdt" type="tel" required autocomplete="tel" inputmode="tel" placeholder="09xx xxx xxx"></label>'
                    '<label>Sản phẩm quan tâm<select name="sp">%s</select></label>'
                    '<label>Số lượng<input name="sl" inputmode="numeric" placeholder="Ví dụ: 50 chiếc"></label>'
                    '<label class="rong">Lời nhắn<textarea name="nhan" placeholder="Màu, kích thước, khắc chữ, thời gian cần hàng…"></textarea></label>'
                    '<div class="rong hang-gui">%s</div>'
                    '<p class="rong ghi-chu-form">Web không lưu thông tin. Bấm gửi là điện thoại soạn sẵn tin nhắn để Quý khách gửi thẳng cho chúng tôi.</p>'
                    '</form>') % (e(self.ten), e(self.link_zalo()), e(self.dt[1] if self.dt else ""), lua_chon, "".join(gui))
        loi_moi = self.lh.get("loi_moi") or "Cho chúng tôi biết mẫu và số lượng Quý khách cần — điền vài dòng là xong."
        return ('<section class="cach" id="lien-he"><div class="khung"><div class="dat-wrap reveal">'
                '<div><h2>%s</h2><p class="mo">%s</p><ul class="ds-lh">%s</ul></div>%s</div></div></section>') % (
            e(self.nhan["lien_he"]), e(loi_moi), "".join(dong), form)

    def trang_chu(self):
        bia = self.anh_bia()
        mo_ta = cat_chu(self.ct.get("mo_ta_ngan") or self.ct.get("khau_hieu")
                        or "%s — %d sản phẩm" % (self.ten, len(self.sp)))
        ld = {"@context": "https://schema.org", "@type": "Store", "name": self.ct.get("ten") or self.ten, "description": mo_ta}
        if self.url:
            ld["url"] = self.url + "/"
            if bia:
                ld["image"] = self.url + "/og/trang-chu.jpg"
        if self.dt:
            ld["telephone"] = self.dt[1]
        if self.lh.get("dia_chi"):
            ld["address"] = {"@type": "PostalAddress", "streetAddress": self.lh["dia_chi"], "addressCountry": "VN"}
        if self.lh.get("email"):
            ld["email"] = self.lh["email"]
        ld_hd = None
        hd = [x for x in self.d.get("hoi_dap") or [] if x.get("hoi") and x.get("dap")]
        if hd:
            ld_hd = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
                {"@type": "Question", "name": x["hoi"], "acceptedAnswer": {"@type": "Answer", "text": x["dap"]}} for x in hd]}
        tieu_de = self.ten + (" — " + self.ct["khau_hieu"] if self.ct.get("khau_hieu") else "")
        return "".join([
            self.dau_html(tieu_de, mo_ta, "/", "/og/trang-chu.jpg" if bia else "", [ld, ld_hd]),
            self.dau_trang(True), "<main>",
            self.muc_bia(), self.muc_dai_chay(), self.muc_vi_sao(), self.muc_kham_pha(), self.muc_luoi(),
            self.muc_so_lieu(), self.muc_quy_dao(), self.muc_danh_gia(), self.muc_gioi_thieu(), self.muc_chung_nhan(), self.muc_quy_trinh(),
            self.muc_hoi_dap(), self.muc_lien_he(),
            "</main>", self.chan_trang(), self.thanh_day(), self.cuoi_html()])

    # ═════════ TRANG SẢN PHẨM ═════════
    def trang_sp(self, s):
        anh = self.anh_sp(s)
        mo_ta = cat_chu(s.get("mo_ta_ngan") or s.get("mo_ta") or "%s — %s" % (s["ten"], self.ten))
        ld = {"@context": "https://schema.org", "@type": "Product", "name": s["ten"], "description": mo_ta,
              "brand": {"@type": "Brand", "name": self.ten}}
        if self.url and anh:
            ld["image"] = ["%s/anh/%s-1280.webp" % (self.url, t) for t in anh]
        if s.get("chat_lieu"):
            ld["material"] = s["chat_lieu"]
        so_gia = re.sub(r"[^\d]", "", str(s.get("gia") or ""))
        if so_gia and re.fullmatch(r"[\d.,\s]+(đ|₫|vnđ|vnd)?\s*", str(s["gia"]).strip(), re.I):
            ld["offers"] = {"@type": "Offer", "price": so_gia, "priceCurrency": "VND",
                            "availability": "https://schema.org/InStock"}

        r = [self.dau_html("%s — %s" % (s["ten"], self.ten), mo_ta, "/san-pham/%s/" % s["ma"],
                           "/og/%s.jpg" % s["ma"] if anh else "", ld),
             self.dau_trang(False),
             '<main class="trang-sp"><div class="khung"><a class="quay-lai" href="/#san-pham">%s Tất cả sản phẩm</a>'
             '<article class="chi-tiet">' % svg("quay_lai")]
        if anh:
            truot = "".join('<a href="/anh/%s-1280.webp" aria-label="Xem ảnh %d lớn hơn">%s</a>' % (
                t, i + 1, self.img(t, "%s — ảnh %d" % (s["ten"], i + 1) if i else s["ten"],
                                   "(min-width:992px) 50vw, 100vw", lazy=i > 0)) for i, t in enumerate(anh))
            cham = ""
            if len(anh) > 1:
                cham = '<div class="cham">%s</div>' % "".join(
                    '<button type="button" aria-label="Ảnh %d"></button>' % (i + 1) for i in range(len(anh)))
            r.append('<div class="bo-anh reveal"><div class="truot">%s</div>%s%s</div>' % (
                truot, '<span class="dem-anh">1/%d</span>' % len(anh) if len(anh) > 1 else "", cham))
        r.append('<div class="reveal d1">')
        if s.get("danh_muc"):
            r.append('<span class="chip-dm">%s</span>' % e(s["danh_muc"]))
        r.append("<h1>%s</h1>" % e(s["ten"]))
        r.append('<p class="gia-lon">%s</p>' % e(s["gia"]) if s.get("gia")
                 else '<p class="gia-lon lien-he">%s</p>' % e(self.nhan["lien_he_gia"]))
        if s.get("dac_diem"):
            r.append('<div class="ticks">%s</div>' % "".join('<div><i>✓</i>%s</div>' % e(x) for x in s["dac_diem"] if x))
        tt = []
        for k, nh in (("chat_lieu", "Chất liệu"), ("kich_thuoc", "Kích thước"), ("mau_sac", "Màu sắc"),
                      ("xuat_xu", "Nơi làm"), ("bao_hanh", "Bảo hành")):
            if s.get(k):
                tt.append((nh, s[k]))
        tt += [(k, v) for k, v in (s.get("thong_tin") or {}).items() if v]
        if tt:
            r.append('<table class="bang-tt">%s</table>' % "".join(
                '<tr><th scope="row">%s</th><td>%s</td></tr>' % (e(a), e(b)) for a, b in tt))
        if s.get("mo_ta"):
            r.append('<div class="mo-ta">%s</div>' % doan_van(s["mo_ta"]))
        nut_sp = []
        if self.zalo:
            cau = "Chào %s, tôi muốn hỏi về sản phẩm: %s" % (self.ten, s["ten"])
            if self.url:
                cau += " — %s/san-pham/%s/" % (self.url, s["ma"])
            nut_sp.append(nut(self.link_zalo(), "Hỏi giá qua Zalo", them=' data-chep="%s"' % e(cau)))
        if self.dt:
            nut_sp.append(nut(self.link_goi(), "Gọi " + self.dt[0], "ma", bieu="goi"))
        nut_sp.append(nut(None, "Chia sẻ", "ma", bieu="chia_se", them=' type="button" data-chia-se'))
        r.append('<div class="hang-nut">%s</div></div></article></div>' % "".join(nut_sp))

        khac = [x for x in self.sp if x is not s and x.get("danh_muc") == s.get("danh_muc")]
        khac += [x for x in self.sp if x is not s and x not in khac]
        if khac[:4]:
            r.append('<section class="cach"><div class="khung"><div class="dau-muc reveal"><h2>Sản phẩm khác</h2></div>'
                     '<div class="luoi-sp">%s</div></div></section>' % "".join(self.the_sp(x, i) for i, x in enumerate(khac[:4])))
        r += ["</main>", self.chan_trang(), self.thanh_day(s), self.cuoi_html()]
        return "".join(r)

    def trang_404(self):
        return "".join([self.dau_html("Không tìm thấy trang — " + self.ten, "Trang không tồn tại.", "/404.html", "", None),
                        self.dau_trang(False),
                        '<main class="trang-sp"><div class="khung cach"><h1>Không tìm thấy trang</h1>'
                        '<p class="mo" style="margin:14px 0 24px">Đường link có thể đã cũ. Mời Quý khách xem các sản phẩm của chúng tôi.</p>'
                        '%s</div></main>' % nut("/#san-pham", "Xem sản phẩm"),
                        self.chan_trang(), self.thanh_day(), self.cuoi_html()])

    # ─── tệp phụ ───
    def anh_og(self, ten_anh, dich):
        """Ảnh xem trước khi chia sẻ link (Zalo/Facebook): 1200×630 JPG, ảnh nằm trọn
        trên nền nhạt — không cắt mất sản phẩm."""
        from PIL import Image
        nen = Image.new("RGB", (1200, 630), self.mau["nhat_vua"])
        im = Image.open(self.anh_vao / ("%s-1280.webp" % ten_anh)).convert("RGB")
        im.thumbnail((1200, 630), Image.LANCZOS)
        nen.paste(im, ((1200 - im.width) // 2, (630 - im.height) // 2))
        dich.parent.mkdir(parents=True, exist_ok=True)
        nen.save(dich, "JPEG", quality=82, optimize=True, progressive=True)

    def bieu_tuong(self):
        from PIL import Image, ImageDraw, ImageFont
        chu = khong_dau(self.ten)[:1].upper() or "W"
        (self.ra / "favicon.svg").write_text(
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><defs><linearGradient id="g" x1="0" x2="1">'
            '<stop offset=".15" stop-color="%s"/><stop offset="1" stop-color="%s"/></linearGradient></defs>'
            '<rect width="64" height="64" rx="18" fill="url(#g)"/>'
            '<text x="32" y="43" font-family="Georgia,serif" font-size="34" font-weight="700" fill="#fff" '
            'text-anchor="middle">%s</text></svg>' % (self.mau["dam"], self.mau["dam_2"], e(chu)), "utf-8")
        lg = self.logo()
        o = Image.new("RGB", (180, 180), "white")
        if lg:
            im = Image.open(self.anh_vao / ("%s-640.webp" % lg)).convert("RGBA")
            im.thumbnail((150, 150), Image.LANCZOS)
            o.paste(im, ((180 - im.width) // 2, (180 - im.height) // 2), im)
        else:
            o = Image.new("RGB", (180, 180), self.mau["dam"])
            try:
                f = ImageFont.load_default(size=96)
            except TypeError:
                f = ImageFont.load_default()
            ImageDraw.Draw(o).text((90, 92), chu, fill="white", font=f, anchor="mm")
        o.save(self.ra / "apple-touch-icon.png")

    def chay(self):
        can_pillow()
        if self.ra.exists():
            shutil.rmtree(self.ra)
        (self.ra / "anh").mkdir(parents=True)

        def ghi(p, s):
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(s, "utf-8")
        ghi(self.ra / "index.html", self.trang_chu())
        for s in self.sp:
            ghi(self.ra / "san-pham" / s["ma"] / "index.html", self.trang_sp(s))
        ghi(self.ra / "404.html", self.trang_404())

        for t in sorted(self.anh_dung):
            for co in (640, 1280):
                shutil.copy2(self.anh_vao / ("%s-%d.webp" % (t, co)), self.ra / "anh")
        bia = self.anh_bia()
        if bia:
            self.anh_og(bia, self.ra / "og" / "trang-chu.jpg")
        for s in self.sp:
            t = self.anh_dau_sp(s)
            if t:
                self.anh_og(t, self.ra / "og" / ("%s.jpg" % s["ma"]))
        self.bieu_tuong()

        ghi(self.ra / "_headers",
            "/anh/*\n  Cache-Control: public, max-age=604800\n/og/*\n  Cache-Control: public, max-age=86400\n")
        if self.url:
            ghi(self.ra / "robots.txt", "User-agent: *\nAllow: /\nSitemap: %s/sitemap.xml\n" % self.url)
            nay = datetime.date.today().isoformat()
            dong = ["<url><loc>%s/</loc><lastmod>%s</lastmod></url>" % (self.url, nay)] + [
                "<url><loc>%s/san-pham/%s/</loc><lastmod>%s</lastmod></url>" % (self.url, s["ma"], nay) for s in self.sp]
            ghi(self.ra / "sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n'
                '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">%s</urlset>\n' % "".join(dong))
        else:
            ghi(self.ra / "robots.txt", "User-agent: *\nAllow: /\n")

        tong = sum(p.stat().st_size for p in self.ra.rglob("*") if p.is_file())
        muc = [m for m, co in (("dải chữ chạy", self.muc_dai_chay()), ("vì sao chọn", self.muc_vi_sao()),
                               ("tab khám phá", self.muc_kham_pha()), ("số liệu", self.muc_so_lieu()),
                               ("quỹ đạo", self.muc_quy_dao()), ("lời khách", self.muc_danh_gia()),
                               ("giới thiệu", self.muc_gioi_thieu()), ("chứng nhận", self.muc_chung_nhan()), ("quy trình", self.muc_quy_trinh()),
                               ("hỏi đáp", self.muc_hoi_dap())) if co]
        print("✔ Đã dựng %s: trang chủ + %d trang sản phẩm · %d ảnh · %.1f MB" % (
            self.ra, len(self.sp), len(self.anh_dung), tong / 1e6))
        print("  Mục đang hiện: bìa · %s · lưới sản phẩm · nhận báo giá" % " · ".join(muc) if muc else
              "  Mục đang hiện: bìa · lưới sản phẩm · nhận báo giá (web.json còn mỏng — xem skill lam-web bước 5)")
        print("  Màu %s → gradient %s→%s (tương phản %.1f:1) · phong cách %s" % (
            self.mau["chinh"], self.mau["dam"], self.mau["dam_2"], self.mau["tuong_phan_dam"],
            self.gd.get("phong_cach") or "truyen-thong"))
        if not self.url:
            print("ℹ Chưa có địa chỉ web → chưa có sitemap/og:image tuyệt đối. trien-khai.py sẽ dựng lại kèm --url.")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("thu_muc_khach")
    ap.add_argument("--url", help="địa chỉ web thật, vd https://gom-minh-long.pages.dev")
    a = ap.parse_args()
    Dung(a.thu_muc_khach, a.url).chay()


if __name__ == "__main__":
    main()
