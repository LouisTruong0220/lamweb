"""Chọn màu chủ đạo cho website — nền LUÔN trắng, màu này chỉ để nhấn.

Ba cách, ưu tiên từ trên xuống:
    python cong-cu/chon-mau.py --hex "#1F4E8C"                 # doanh nghiệp đã có màu
    python cong-cu/chon-mau.py --anh khach-hang/x/anh/logo-640.webp   # lấy từ logo / biển hiệu
    python cong-cu/chon-mau.py --nganh gom                      # theo ngành nghề

Thêm --ghi khach-hang/<slug>/web.json để ghi thẳng vào giao_dien.mau_chu_dao.

In ra bảng màu đầy đủ + độ tương phản. Màu gốc quá nhạt (vàng, hồng phấn…) vẫn
dùng được: nút và chữ nhấn tự lấy bản sẫm đạt chuẩn đọc (≥4,5:1).
"""
import argparse
import colorsys
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from thu_vien import bang_mau, can_pillow, rgb_sang_hex, hex_sang_rgb  # noqa: E402

# Màu gợi ý theo ngành — lấy từ chất liệu/men/sắc truyền thống của chính nghề đó.
MAU_NGANH = {
    "gom":       ("#1F4E8C", "Xanh men lam (gốm Chu Đậu, Bát Tràng)"),
    "gom-nau":   ("#8C4A2F", "Nâu men da lươn / đất nung"),
    "may-tre":   ("#7A6A2E", "Vàng rơm sẫm của mây tre đã hun khói"),
    "coi":       ("#6F7F3A", "Xanh lục cói non"),
    "son-mai":   ("#9E2A2B", "Đỏ son sơn mài"),
    "go":        ("#7B4A2A", "Nâu gỗ gụ"),
    "lua":       ("#8E3B5F", "Tím hồng lụa tơ tằm"),
    "theu":      ("#A23B3B", "Đỏ chỉ thêu"),
    "det-tho-cam": ("#B1462A", "Đỏ cam thổ cẩm"),
    "da":        ("#4F5D63", "Xám đá xanh"),
    "bac-dong":  ("#8A6D3B", "Đồng thau"),
    "giay-do":   ("#A67C3D", "Vàng giấy dó"),
    "nen-thom":  ("#6B4E71", "Tím oải hương"),
    "tranh":     ("#2F5D50", "Xanh lục bảo tranh dân gian"),
    "nong-san":  ("#3F7A3A", "Xanh lá"),
    "khac":      ("#2F5D62", "Xanh mòng két trung tính"),
}


def mau_tu_anh(duong):
    """Tìm màu ĐẶC TRƯNG nhất của logo/ảnh: bỏ trắng, đen, xám; ưu tiên màu tươi
    chiếm nhiều diện tích."""
    can_pillow()
    from PIL import Image
    im = Image.open(duong).convert("RGBA")
    im.thumbnail((200, 200))
    nen = Image.new("RGBA", im.size, (255, 255, 255, 255))
    im = Image.alpha_composite(nen, im).convert("RGB")
    q = im.quantize(colors=10, method=Image.MEDIANCUT)
    bang = q.getpalette()
    tot, diem_tot = None, -1
    for dem, chi_so in q.getcolors():
        r, g, b = bang[chi_so * 3: chi_so * 3 + 3]
        h, l, s = colorsys.rgb_to_hls(r / 255, g / 255, b / 255)
        if l > 0.9 or l < 0.1 or s < 0.18:
            continue                       # trắng, đen, xám — không phải màu thương hiệu
        diem = dem * (0.4 + s)
        if diem > diem_tot:
            tot, diem_tot = (r, g, b), diem
    return rgb_sang_hex(tot) if tot else None


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--hex")
    g.add_argument("--anh")
    g.add_argument("--nganh", choices=sorted(MAU_NGANH))
    ap.add_argument("--ghi", help="đường dẫn web.json để ghi màu vào")
    a = ap.parse_args()

    if a.hex:
        mau, ly_do = rgb_sang_hex(hex_sang_rgb(a.hex)), "mã màu doanh nghiệp đưa"
    elif a.anh:
        mau = mau_tu_anh(a.anh)
        if not mau:
            print("✘ Ảnh gần như không có màu (trắng/đen/xám). Dùng --nganh hoặc --hex.")
            sys.exit(1)
        ly_do = "lấy từ ảnh %s" % Path(a.anh).name
    else:
        mau, ly_do = MAU_NGANH[a.nganh]

    b = bang_mau(mau)
    print("Màu chủ đạo: %s  (%s)" % (b["chinh"], ly_do))
    for k in ("dam", "dam_hon", "nhat", "nhat_vua", "vien"):
        print("  %-9s %s" % (k, b[k]))
    print("Tương phản trên nền trắng: màu gốc %.2f · bản sẫm cho nút/chữ %.2f (cần ≥4,5)"
          % (b["tuong_phan_goc"], b["tuong_phan_dam"]))
    if b["tuong_phan_goc"] < 3:
        print("ℹ Màu gốc khá nhạt — chỉ dùng làm viền/nền nhạt; nút và chữ dùng bản sẫm %s." % b["dam"])

    if a.ghi:
        p = Path(a.ghi)
        d = json.loads(p.read_text("utf-8"))
        d.setdefault("giao_dien", {})["mau_chu_dao"] = b["chinh"]
        p.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", "utf-8")
        print("✔ Đã ghi vào %s" % p)


if __name__ == "__main__":
    main()
