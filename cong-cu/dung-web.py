"""web.json + ảnh đã xử lý → website tĩnh hoàn chỉnh trong khach-hang/<slug>/dist/

    python cong-cu/dung-web.py khach-hang/<slug>
    python cong-cu/dung-web.py khach-hang/<slug> --url https://ten.pages.dev   (trien-khai.py tự truyền)

Sinh ra:
    dist/index.html                  trang chủ (bìa · nổi bật · sản phẩm · giới thiệu · quy trình · liên hệ)
    dist/san-pham/<ma>/index.html    mỗi sản phẩm một trang — gửi riêng link qua Zalo được, có ảnh xem trước
    dist/anh/…                       chỉ những ảnh web.json có dùng
    dist/og/…jpg                     ảnh xem trước 1200×630 khi chia sẻ link
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
    # tên: (phông tiêu đề, độ đậm tiêu đề, bo góc, tham số Google Fonts)
    "truyen-thong": ("'Lora', Georgia, serif", "600", "10px",
                     "family=Lora:wght@500;600;700&family=Be+Vietnam+Pro:wght@400;500;600;700"),
    "hien-dai":     ("'Be Vietnam Pro', system-ui, sans-serif", "700", "16px",
                     "family=Be+Vietnam+Pro:wght@400;500;600;700"),
    "sang-trong":   ("'Playfair Display', Georgia, serif", "600", "3px",
                     "family=Playfair+Display:wght@500;600;700&family=Be+Vietnam+Pro:wght@400;500;600;700"),
}
PHONG_THAN = "'Be Vietnam Pro', system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif"

NHAN_MAC_DINH = {
    "noi_bat": "Vì sao chọn chúng tôi",
    "san_pham": "Sản phẩm",
    "gioi_thieu": "Về chúng tôi",
    "quy_trinh": "Quy trình làm ra sản phẩm",
    "lien_he": "Liên hệ",
    "xem_san_pham": "Xem sản phẩm",
    "lien_he_gia": "Liên hệ báo giá",
    "tat_ca": "Tất cả",
}

# Biểu tượng Material Icons (Apache 2.0) — vẽ bằng SVG nội tuyến, không tải phông biểu tượng.
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


def svg(ten):
    return '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="%s"/></svg>' % BIEU[ten]


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
        self.zalo = so_dien_thoai(self.lh.get("zalo")) or self.dt
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

    def img(self, ten, alt, sizes, lazy=True, lop=""):
        """Thẻ <img> có srcset 640/1280 + width/height để trang không giật khi ảnh tải."""
        self.anh_dung.add(ten)
        w, h = self.kt(ten, 640)
        return ('<img src="/anh/{t}-640.webp" srcset="/anh/{t}-640.webp 640w, /anh/{t}-1280.webp 1280w" '
                'sizes="{s}" width="{w}" height="{h}" alt="{a}"{l}{c}>').format(
            t=ten, s=sizes, w=w, h=h, a=e(alt),
            l=' loading="lazy" decoding="async"' if lazy else ' fetchpriority="high"',
            c=' class="%s"' % lop if lop else "")

    def anh_dau_sp(self, s):
        for t in s.get("anh") or []:
            if self.co_anh(t):
                return t
        return None

    def anh_bia(self):
        t = self.gd.get("anh_bia")
        if self.co_anh(t):
            return t
        for s in sorted(self.sp, key=lambda x: not x.get("noi_bat")):
            t = self.anh_dau_sp(s)
            if t:
                return t
        return None

    def logo(self):
        t = self.ct.get("logo")
        return t if self.co_anh(t) else None

    # ─── liên kết liên hệ ───
    def link_zalo(self):
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
        fonts = self.pc[3]
        tuyet_doi = (self.url + duong) if self.url else ""
        og_anh = (self.url + anh_og) if (self.url and anh_og) else ""
        bien = (":root{--c:%(chinh)s;--cd:%(dam)s;--cdh:%(dam_hon)s;--cn:%(nhat)s;--cnv:%(nhat_vua)s;--cv:%(vien)s;"
                % self.mau) + "--f-tieu-de:%s;--w-tieu-de:%s;--bo:%s;--f-than:%s}" % (
                    self.pc[0], self.pc[1], self.pc[2], PHONG_THAN)
        r = ['<!doctype html><html lang="vi"><head><meta charset="utf-8">',
             '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">',
             "<title>%s</title>" % e(tieu_de),
             '<meta name="description" content="%s">' % e(mo_ta),
             '<meta name="theme-color" content="%s">' % self.mau["dam"],
             '<meta name="format-detection" content="telephone=no">']
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
              '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?%s&display=swap">' % fonts,
              "<style>%s\n%s</style>" % (bien, self.css)]
        if json_ld:
            r.append('<script type="application/ld+json">%s</script>'
                     % json.dumps(json_ld, ensure_ascii=False).replace("</", "<\\/"))
        r.append("</head><body>")
        return "".join(r)

    def dau_trang(self, trang_chu):
        lg = self.logo()
        hieu = (self.img(lg, "Logo " + self.ten, "120px", lazy=False) if lg
                else '<span class="chu-cai" aria-hidden="true">%s</span>' % e(khong_dau(self.ten)[:1].upper()))
        muc = self.muc_menu() if trang_chu else []
        menu_rong = "".join('<a href="%s">%s</a>' % (h, e(n)) for h, n in muc)
        goi = ('<a class="nut-goi-dau" href="%s">%s<span>%s</span></a>' % (self.link_goi(), svg("goi"), e(self.dt[0]))
               if self.dt else "")
        r = ['<header class="dau"><div class="khung">',
             '<a class="hieu" href="/">%s<b>%s</b></a>' % (hieu, e(self.ten)),
             '<nav class="dau-menu-rong" aria-label="Mục chính">%s</nav>' % menu_rong if menu_rong else "",
             goi, "</div>"]
        if menu_rong:
            r.append('<nav class="menu" aria-label="Mục chính">%s</nav>' % menu_rong)
        r.append("</header>")
        return "".join(r)

    def muc_menu(self):
        m = [("#san-pham", self.nhan["san_pham"])]
        if self.ct.get("gioi_thieu"):
            m.append(("#gioi-thieu", self.nhan["gioi_thieu"]))
        if self.d.get("quy_trinh"):
            m.append(("#quy-trinh", "Quy trình"))
        m.append(("#lien-he", self.nhan["lien_he"]))
        return m

    def thanh_day(self, san_pham=None):
        """Thanh hành động dính đáy màn hình điện thoại — trong tầm ngón cái."""
        nut = []
        if san_pham and self.zalo:
            cau = "Chào %s, tôi muốn hỏi về sản phẩm: %s" % (self.ten, san_pham["ten"])
            if self.url:
                cau += " — %s/san-pham/%s/" % (self.url, san_pham["ma"])
            nut.append('<a class="chinh ngang" href="%s" data-chep="%s">%s<span>Hỏi giá qua Zalo</span></a>'
                       % (self.link_zalo(), e(cau), svg("chat")))
            if self.dt:
                nut.append('<a href="%s" aria-label="Gọi điện">%s<span>Gọi</span></a>' % (self.link_goi(), svg("goi")))
            return '<nav class="thanh-day" aria-label="Liên hệ nhanh">%s</nav>' % "".join(nut)
        if self.dt:
            nut.append('<a class="chinh" href="%s">%s<span>Gọi ngay</span></a>' % (self.link_goi(), svg("goi")))
        if self.zalo:
            nut.append('<a href="%s">%s<span>Zalo</span></a>' % (self.link_zalo(), svg("chat")))
        if self.link_ban_do():
            nut.append('<a href="%s" target="_blank" rel="noopener">%s<span>Chỉ đường</span></a>'
                       % (e(self.link_ban_do()), svg("ghim")))
        elif self.lh.get("facebook"):
            nut.append('<a href="%s" target="_blank" rel="noopener">%s<span>Facebook</span></a>'
                       % (e(self.lh["facebook"]), svg("facebook")))
        return '<nav class="thanh-day" aria-label="Liên hệ nhanh">%s</nav>' % "".join(nut) if nut else ""

    def chan_trang(self):
        nam = datetime.date.today().year
        r = ['<footer class="chan"><div class="khung">',
             "<p>© %d %s</p>" % (nam, e(self.ct.get("ten") or self.ten))]
        if self.lh.get("dia_chi"):
            r.append("<p>%s</p>" % e(self.lh["dia_chi"]))
        if self.d.get("chan_trang"):
            r.append("<p>%s</p>" % e(self.d["chan_trang"]))
        r.append("</div></footer>")
        return "".join(r)

    def cuoi_html(self):
        return "<script>%s</script></body></html>" % self.js

    # ─── thẻ sản phẩm ───
    def the_sp(self, s):
        t = self.anh_dau_sp(s)
        anh = self.img(t, s["ten"], "(min-width:960px) 25vw, (min-width:600px) 33vw, 50vw") if t else ""
        gia = ('<span class="gia">%s</span>' % e(s["gia"]) if s.get("gia")
               else '<span class="gia lien-he">%s</span>' % e(self.nhan["lien_he_gia"]))
        return ('<a class="the-sp" href="/san-pham/%s/" data-dm="%s"><div class="o-anh">%s</div>'
                '<div class="chu"><h3>%s</h3>%s</div></a>') % (s["ma"], e(s.get("danh_muc", "")), anh, e(s["ten"]), gia)

    # ─── trang chủ ───
    def trang_chu(self):
        bia = self.anh_bia()
        mo_ta = cat_chu(self.ct.get("mo_ta_ngan") or self.ct.get("khau_hieu")
                        or "%s — %d sản phẩm" % (self.ten, len(self.sp)))
        ld = {"@context": "https://schema.org", "@type": "Store", "name": self.ct.get("ten") or self.ten,
              "description": mo_ta}
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
        tieu_de = self.ten + (" — " + self.ct["khau_hieu"] if self.ct.get("khau_hieu") else "")

        r = [self.dau_html(tieu_de, mo_ta, "/", "/og/trang-chu.jpg" if bia else "", ld),
             self.dau_trang(True), "<main>"]

        # Bìa
        ty_le = "4/3"
        if bia:
            ds = self.thong_tin_anh().get(bia, {})
            ty_le = {"doc": "4/5", "vuong": "1/1"}.get(ds.get("huong"), "4/3")
        nut = ['<a class="nut chinh" href="#san-pham">%s</a>' % e(self.nhan["xem_san_pham"])]
        if self.zalo:
            nut.append('<a class="nut phu" href="%s">%s Nhắn Zalo</a>' % (self.link_zalo(), svg("chat")))
        elif self.dt:
            nut.append('<a class="nut phu" href="%s">%s Gọi ngay</a>' % (self.link_goi(), svg("goi")))
        r.append('<section class="bia"><div class="khung">')
        if bia:
            r.append('<div class="bia-anh" style="--ty-le-bia:%s;--vi-tri-bia:%s">%s</div>' % (
                ty_le, e(self.gd.get("vi_tri_anh_bia") or "50% 50%"),
                self.img(bia, self.ct.get("mo_ta_anh_bia") or self.ten, "(min-width:960px) 55vw, 100vw", lazy=False)))
        r.append('<div class="bia-chu">')
        if self.ct.get("dong_tren_ten"):
            r.append('<span class="nhan-muc">%s</span>' % e(self.ct["dong_tren_ten"]))
        r.append("<h1>%s</h1>" % e(self.ten))
        if self.ct.get("khau_hieu"):
            r.append('<p class="khau-hieu">%s</p>' % e(self.ct["khau_hieu"]))
        r.append('<div class="hang-nut">%s</div></div></div></section>' % "".join(nut))

        # Điểm nổi bật
        nb = [x for x in self.d.get("diem_noi_bat") or [] if x.get("tieu_de")]
        if nb:
            r.append('<section class="muc nen"><div class="khung"><span class="nhan-muc">%s</span>'
                     '<div class="luoi-noi-bat">%s</div></div></section>' % (
                         e(self.nhan["noi_bat"]),
                         "".join('<div class="the-noi-bat"><h3>%s</h3>%s</div>' % (
                             e(x["tieu_de"]), "<p>%s</p>" % e(x["mo_ta"]) if x.get("mo_ta") else "") for x in nb)))

        # Sản phẩm
        dm = []
        for s in self.sp:
            if s.get("danh_muc") and s["danh_muc"] not in dm:
                dm.append(s["danh_muc"])
        r.append('<section class="muc" id="san-pham"><div class="khung"><h2>%s</h2>' % e(self.nhan["san_pham"]))
        if len(dm) > 1:
            r.append('<div class="loc" role="group" aria-label="Lọc theo loại">'
                     '<button type="button" data-dm="*" aria-pressed="true">%s</button>%s</div>' % (
                         e(self.nhan["tat_ca"]),
                         "".join('<button type="button" data-dm="%s" aria-pressed="false">%s</button>' % (e(x), e(x))
                                 for x in dm)))
        thu_tu = sorted(self.sp, key=lambda x: not x.get("noi_bat"))
        r.append('<div class="luoi-sp">%s</div></div></section>' % "".join(self.the_sp(s) for s in thu_tu))

        # Giới thiệu
        if self.ct.get("gioi_thieu"):
            agt = self.ct.get("anh_gioi_thieu")
            co = self.co_anh(agt)
            r.append('<section class="muc nen" id="gioi-thieu"><div class="khung"><div class="gioi-thieu%s"><div>'
                     '<span class="nhan-muc">%s</span><h2>%s</h2>%s</div>%s</div></div></section>' % (
                         " co-anh" if co else "", e(self.nhan["gioi_thieu"]),
                         e(self.ct.get("tieu_de_gioi_thieu") or self.ct.get("ten") or self.ten),
                         doan_van(self.ct["gioi_thieu"]),
                         self.img(agt, self.ct.get("mo_ta_anh_gioi_thieu") or "Xưởng của " + self.ten,
                                  "(min-width:960px) 45vw, 100vw") if co else ""))

        # Quy trình
        qt = [x for x in self.d.get("quy_trinh") or [] if x.get("tieu_de")]
        if qt:
            r.append('<section class="muc" id="quy-trinh"><div class="khung"><h2>%s</h2><ol class="quy-trinh">%s</ol>'
                     '</div></section>' % (e(self.nhan["quy_trinh"]), "".join(
                         "<li><h3>%s</h3>%s</li>" % (e(x["tieu_de"]), "<p>%s</p>" % e(x["mo_ta"]) if x.get("mo_ta") else "")
                         for x in qt)))

        # Liên hệ
        r.append(self.muc_lien_he())
        r.append("</main>")
        r.append(self.chan_trang())
        r.append(self.thanh_day())
        r.append(self.cuoi_html())
        return "".join(r)

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
            them(self.link_ban_do(), "ghim", "Địa chỉ — bấm để chỉ đường", self.lh["dia_chi"], True)
        if self.lh.get("gio_mo_cua"):
            them("", "dong_ho", "Giờ mở cửa", self.lh["gio_mo_cua"])
        if not dong:
            return ""
        return ('<section class="muc nen" id="lien-he"><div class="khung"><h2>%s</h2>%s<ul class="ds-lien-he">%s</ul>'
                '</div></section>') % (e(self.nhan["lien_he"]),
                                        "<p class=\"mo\">%s</p>" % e(self.lh["loi_moi"]) if self.lh.get("loi_moi") else "",
                                        "".join(dong))

    # ─── trang sản phẩm ───
    def trang_sp(self, s):
        anh = [t for t in (s.get("anh") or []) if self.co_anh(t)]
        mo_ta = cat_chu(s.get("mo_ta_ngan") or s.get("mo_ta") or "%s — %s" % (s["ten"], self.ten))
        ld = {"@context": "https://schema.org", "@type": "Product", "name": s["ten"], "description": mo_ta,
              "brand": {"@type": "Brand", "name": self.ten}}
        if self.url and anh:
            ld["image"] = ["%s/anh/%s-1280.webp" % (self.url, t) for t in anh]
        if s.get("chat_lieu"):
            ld["material"] = s["chat_lieu"]
        so_gia = re.sub(r"[^\d]", "", str(s.get("gia") or ""))
        if so_gia and re.fullmatch(r"[\d.,\s]+(đ|₫|vnđ|vnd|VNĐ|VND)?\s*", str(s["gia"]).strip(), re.I):
            ld["offers"] = {"@type": "Offer", "price": so_gia, "priceCurrency": "VND",
                            "availability": "https://schema.org/InStock"}

        r = [self.dau_html("%s — %s" % (s["ten"], self.ten), mo_ta, "/san-pham/%s/" % s["ma"],
                           "/og/%s.jpg" % s["ma"] if anh else "", ld),
             self.dau_trang(False),
             '<main class="khung"><a class="quay-lai" href="/#san-pham">%s Tất cả sản phẩm</a>'
             '<article class="chi-tiet">' % svg("quay_lai")]

        if anh:
            truot = "".join('<a href="/anh/%s-1280.webp" aria-label="Xem ảnh %d lớn hơn">%s</a>' % (
                t, i + 1, self.img(t, "%s — ảnh %d" % (s["ten"], i + 1) if i else s["ten"],
                                   "(min-width:960px) 50vw, 100vw", lazy=i > 0)) for i, t in enumerate(anh))
            cham = ""
            if len(anh) > 1:
                cham = '<div class="cham">%s</div>' % "".join(
                    '<button type="button" aria-label="Ảnh %d"></button>' % (i + 1) for i in range(len(anh)))
            r.append('<div class="bo-anh"><div class="truot">%s</div>%s%s</div>' % (
                truot, '<span class="dem-anh">1/%d</span>' % len(anh) if len(anh) > 1 else "", cham))

        r.append("<div>")
        if s.get("danh_muc"):
            r.append('<span class="chip-dm">%s</span>' % e(s["danh_muc"]))
        r.append("<h1>%s</h1>" % e(s["ten"]))
        r.append('<p class="gia-lon">%s</p>' % e(s["gia"]) if s.get("gia")
                 else '<p class="gia-lon lien-he">%s</p>' % e(self.nhan["lien_he_gia"]))
        tt = []
        for k, nhan in (("chat_lieu", "Chất liệu"), ("kich_thuoc", "Kích thước"), ("mau_sac", "Màu sắc"),
                        ("xuat_xu", "Nơi làm"), ("bao_hanh", "Bảo hành")):
            if s.get(k):
                tt.append((nhan, s[k]))
        for k, v in (s.get("thong_tin") or {}).items():
            if v:
                tt.append((k, v))
        if tt:
            r.append('<table class="bang-tt">%s</table>' % "".join(
                "<tr><th scope=\"row\">%s</th><td>%s</td></tr>" % (e(a), e(b)) for a, b in tt))
        if s.get("mo_ta"):
            r.append('<div class="mo-ta">%s</div>' % doan_van(s["mo_ta"]))
        r.append('<div class="hang-nut" style="margin-top:20px">')
        if self.dt:
            r.append('<a class="nut phu" href="%s">%s Gọi %s</a>' % (self.link_goi(), svg("goi"), e(self.dt[0])))
        r.append('<button class="nut phu" type="button" data-chia-se>%s Chia sẻ</button></div>' % svg("chia_se"))
        r.append("</div></article>")

        # Sản phẩm khác: ưu tiên cùng danh mục
        khac = [x for x in self.sp if x is not s and x.get("danh_muc") == s.get("danh_muc")]
        khac += [x for x in self.sp if x is not s and x not in khac]
        if khac[:4]:
            r.append('<section class="muc"><h2>Sản phẩm khác</h2><div class="luoi-sp">%s</div></section>'
                     % "".join(self.the_sp(x) for x in khac[:4]))
        r.append("</main>")
        r.append(self.chan_trang())
        r.append(self.thanh_day(s))
        r.append(self.cuoi_html())
        return "".join(r)

    def trang_404(self):
        return "".join([self.dau_html("Không tìm thấy trang — " + self.ten, "Trang không tồn tại.", "/404.html", "", None),
                        self.dau_trang(False),
                        '<main class="khung muc"><h1>Không tìm thấy trang</h1>'
                        '<p class="mo">Đường link có thể đã cũ. Mời Quý khách xem các sản phẩm của chúng tôi.</p>'
                        '<div class="hang-nut"><a class="nut chinh" href="/#san-pham">Xem sản phẩm</a></div></main>',
                        self.chan_trang(), self.thanh_day(), self.cuoi_html()])

    # ─── tệp phụ ───
    def thong_tin_anh(self):
        p = self.anh_vao / "danh-sach.json"
        return json.loads(p.read_text("utf-8")) if p.exists() else {}

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
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><circle cx="32" cy="32" r="32" fill="%s"/>'
            '<text x="32" y="43" font-family="Georgia,serif" font-size="34" font-weight="700" fill="#fff" '
            'text-anchor="middle">%s</text></svg>' % (self.mau["dam"], e(chu)), "utf-8")
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

        ghi = lambda p, s: (p.parent.mkdir(parents=True, exist_ok=True), p.write_text(s, "utf-8"))
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
        print("✔ Đã dựng %s: trang chủ + %d trang sản phẩm · %d ảnh · %.1f MB" % (
            self.ra, len(self.sp), len(self.anh_dung), tong / 1e6))
        print("  Màu chủ đạo %s → nút/chữ nhấn %s (tương phản %.1f:1) · phong cách %s" % (
            self.mau["chinh"], self.mau["dam"], self.mau["tuong_phan_dam"],
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
