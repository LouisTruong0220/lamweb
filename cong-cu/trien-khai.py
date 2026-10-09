"""Đưa website lên Cloudflare Pages — MỘT lệnh lo hết.

    python cong-cu/trien-khai.py khach-hang/<slug>            # bản chính thức
    python cong-cu/trien-khai.py khach-hang/<slug> --nhap     # bản nháp (link riêng, không đè bản chính)
    python cong-cu/trien-khai.py --kiem-tra                   # chỉ kiểm token / tài khoản / mạng

Cần hai biến môi trường (đặt trong cài đặt môi trường Claude Code — xem HUONG-DAN-CLOUDFLARE.md):
    CLOUDFLARE_API_TOKEN    token có quyền  Account · Cloudflare Pages · Edit
    CLOUDFLARE_ACCOUNT_ID   mã tài khoản Cloudflare

Các bước:
  1. Kiểm token
  2. Tìm project Pages tên = slug; chưa có thì TẠO (wrangler pages deploy KHÔNG tự tạo)
  3. Đọc tên miền thật Cloudflare cấp (tên trùng người khác thì Cloudflare thêm đuôi ngẫu nhiên)
  4. Dựng lại web với đúng địa chỉ đó (sitemap, ảnh xem trước khi chia sẻ link)
  5. Cổng kiểm tra — lỗi là DỪNG
  6. wrangler pages deploy
  7. Mở thử địa chỉ, ghi địa chỉ vào web.json + nhật ký
"""
import argparse
import datetime
import json
import os
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

GOC = Path(__file__).resolve().parent
API = "https://api.cloudflare.com/client/v4"
UA = "lamweb-roboworld/1.0"
NHANH_NHAP = "ban-nhap"

HUONG_DAN_MANG = (
    "Phiên Claude Code chưa được phép ra api.cloudflare.com.\n"
    "  → claude.ai/code → biểu tượng đám mây (tên môi trường) trên ô nhập → bánh răng của môi trường\n"
    "  → Network access: Custom → thêm dòng  api.cloudflare.com  và  *.pages.dev\n"
    "  → tích 'Also include default list of common package managers' → Save.\n"
    "  Xem HUONG-DAN-CLOUDFLARE.md bước 3.")


class LoiCF(Exception):
    pass


def goi(phuong_thuc, duong, du_lieu=None):
    token = os.environ.get("CLOUDFLARE_API_TOKEN", "").strip()
    req = urllib.request.Request(API + duong, method=phuong_thuc,
                                 data=json.dumps(du_lieu).encode() if du_lieu is not None else None,
                                 headers={"Authorization": "Bearer " + token, "Content-Type": "application/json",
                                          "User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=40) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as ex:
        than = ex.read().decode("utf-8", "replace")
        try:
            return json.loads(than)
        except ValueError:
            if ex.code in (403, 407) and "cloudflare" not in than.lower():
                raise LoiCF(HUONG_DAN_MANG)
            raise LoiCF("HTTP %d từ Cloudflare: %s" % (ex.code, than[:200]))
    except urllib.error.URLError as ex:
        raise LoiCF("Không nối được api.cloudflare.com (%s).\n%s" % (ex.reason, HUONG_DAN_MANG))


def loi_cf(kq):
    return "; ".join("[%s] %s" % (x.get("code"), x.get("message")) for x in kq.get("errors") or []) or "không rõ"


def kiem_moi_truong():
    thieu = [k for k in ("CLOUDFLARE_API_TOKEN", "CLOUDFLARE_ACCOUNT_ID") if not os.environ.get(k, "").strip()]
    if thieu:
        raise LoiCF("Thiếu biến môi trường: %s\n"
                    "  → claude.ai/code → biểu tượng đám mây → bánh răng của môi trường → Environment variables,\n"
                    "    thêm hai dòng  CLOUDFLARE_API_TOKEN=...  và  CLOUDFLARE_ACCOUNT_ID=...\n"
                    "  → MỞ PHIÊN MỚI (phiên đang chạy không tự nhận biến vừa thêm). Xem HUONG-DAN-CLOUDFLARE.md."
                    % ", ".join(thieu))
    tk = os.environ["CLOUDFLARE_ACCOUNT_ID"].strip()
    kq = goi("GET", "/user/tokens/verify")
    if not kq.get("success"):
        kq = goi("GET", "/accounts/%s/tokens/verify" % tk)   # token kiểu "của tài khoản"
    if not kq.get("success"):
        raise LoiCF("Token không hợp lệ hoặc đã bị thu hồi: %s\n  → Tạo token mới theo HUONG-DAN-CLOUDFLARE.md bước 1."
                    % loi_cf(kq))
    if kq.get("result", {}).get("status") not in (None, "active"):
        raise LoiCF("Token đang ở trạng thái %r (hết hạn/tạm khoá)." % kq["result"]["status"])
    kq = goi("GET", "/accounts/%s/pages/projects?per_page=10" % tk)
    if not kq.get("success"):
        raise LoiCF("Token hợp lệ nhưng KHÔNG vào được Pages của tài khoản %s: %s\n"
                    "  → Kiểm lại CLOUDFLARE_ACCOUNT_ID, và token phải có quyền Account · Cloudflare Pages · Edit\n"
                    "    với Account Resources gồm đúng tài khoản này." % (tk, loi_cf(kq)))
    return tk, kq.get("result_info", {}).get("total_count", len(kq.get("result") or []))


def lay_hoac_tao(tk, ten):
    kq = goi("GET", "/accounts/%s/pages/projects/%s" % (tk, ten))
    if kq.get("success"):
        return kq["result"], False
    ma = [x.get("code") for x in kq.get("errors") or []]
    if 8000007 not in ma:
        raise LoiCF("Không đọc được project %s: %s" % (ten, loi_cf(kq)))
    kq = goi("POST", "/accounts/%s/pages/projects" % tk, {"name": ten, "production_branch": "main"})
    if not kq.get("success"):
        raise LoiCF("Không tạo được project %s: %s" % (ten, loi_cf(kq)))
    return kq["result"], True


def chay(lenh, **kw):
    print("$ " + " ".join(str(x) for x in lenh))
    return subprocess.run(lenh, **kw)


def mo_thu(url, lan=8):
    for i in range(lan):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=20) as r:
                if r.status == 200:
                    return True, "200"
        except urllib.error.HTTPError as ex:
            ly_do = "HTTP %d" % ex.code
            if ex.code in (403, 407) and i == 0:
                return None, "mạng phiên chặn *.pages.dev (không sao — web vẫn đã lên)"
        except Exception as ex:
            ly_do = str(ex)[:80]
        time.sleep(6)
    return False, ly_do


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("thu_muc_khach", nargs="?")
    ap.add_argument("--nhap", action="store_true", help="đẩy bản nháp (nhánh %s), không đụng bản chính" % NHANH_NHAP)
    ap.add_argument("--kiem-tra", action="store_true", help="chỉ kiểm token/tài khoản/mạng")
    a = ap.parse_args()

    try:
        tk, so_pj = kiem_moi_truong()
        print("✔ Token hợp lệ · tài khoản %s… · đang có %d project Pages" % (tk[:6], so_pj))
        if a.kiem_tra or not a.thu_muc_khach:
            ok, ly_do = mo_thu("https://lamweb-kiem-tra-mang.pages.dev", lan=1)
            print("ℹ Thử mở *.pages.dev: %s" % ("được" if ok is not None else ly_do))
            print("✔ Sẵn sàng deploy.")
            return

        goc = Path(a.thu_muc_khach)
        d = json.loads((goc / "web.json").read_text("utf-8"))
        ten = d.get("slug") or goc.name
        pj, moi = lay_hoac_tao(tk, ten)
        mien = pj.get("subdomain") or "%s.pages.dev" % ten
        url_chinh = "https://" + mien
        print("✔ Project %s %s → %s" % (ten, "vừa TẠO MỚI" if moi else "đã có", url_chinh))
        if mien.split(".")[0] != ten:
            print("ℹ Tên %s.pages.dev đã có người dùng — Cloudflare cấp %s" % (ten, mien))

        py = sys.executable
        if chay([py, str(GOC / "dung-web.py"), str(goc), "--url", url_chinh]).returncode:
            raise LoiCF("Dựng web lỗi — xem thông báo ở trên.")
        if chay([py, str(GOC / "kiem-tra-web.py"), str(goc)]).returncode:
            raise LoiCF("Cổng kiểm tra KHÔNG ĐẠT — đã dừng, chưa đẩy gì lên.")

        npx = shutil.which("npx") or shutil.which("npx.cmd")
        if not npx:
            raise LoiCF("Không có npx (Node.js). Phiên đám mây vốn có sẵn — nếu đang chạy máy khác thì cài Node 20+.")
        nhanh = NHANH_NHAP if a.nhap else "main"
        r = chay([npx, "--yes", "wrangler@4", "pages", "deploy", str(goc / "dist"),
                  "--project-name", ten, "--branch", nhanh, "--commit-dirty=true"])
        if r.returncode:
            raise LoiCF("wrangler báo lỗi (xem ở trên). Lỗi 'Authentication error [10000]' → sai ACCOUNT_ID "
                        "hoặc token thiếu quyền Pages Edit.")

        url = "https://%s.%s" % (nhanh, mien) if a.nhap else url_chinh
        ok, ly_do = mo_thu(url + "/")
        if ok:
            print("✔ Đã mở thử %s — chạy tốt" % url)
        elif ok is None:
            print("ℹ Không mở thử được: %s" % ly_do)
        else:
            print("⚠ Chưa mở được %s (%s). Project mới cần 1–2 phút để tên miền chạy — thử lại sau." % (url, ly_do))

        if not a.nhap:
            d["dia_chi_web"] = url_chinh
            (goc / "web.json").write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", "utf-8")
        nk = goc / "nhat-ky.md"
        if not nk.exists():
            nk.write_text("# Nhật ký — %s\n\n| Thời điểm (UTC) | Loại | Địa chỉ |\n|---|---|---|\n"
                          % (d.get("cong_ty", {}).get("ten") or ten), "utf-8")
        with nk.open("a", encoding="utf-8") as f:
            f.write("| %s | %s | %s |\n" % (datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M"),
                                            "bản nháp" if a.nhap else "chính thức", url))
        print("\n══════════════════════════════════════")
        print("  WEB ĐÃ LÊN: %s" % url)
        print("══════════════════════════════════════")
    except LoiCF as ex:
        print("✘ " + str(ex))
        sys.exit(1)


if __name__ == "__main__":
    main()
