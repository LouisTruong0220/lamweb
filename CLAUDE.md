# lamweb — Làm website cho đối tác thủ công mỹ nghệ

Repo này giúp **anh Trường (Roboworld)** làm website giới thiệu sản phẩm cho các doanh nghiệp
nhỏ, hộ sản xuất thủ công mỹ nghệ — những đơn vị ít chi phí, không rành công nghệ. Anh Trường
gửi tên doanh nghiệp + ảnh + tên sản phẩm → Claude dựng web, đưa lên Cloudflare Pages, trả link.

Anh Trường thường dùng **Claude Code trên điện thoại** (phiên chạy trên máy chủ đám mây).

## Cách trả lời

- Tiếng Việt. Xưng "tôi", gọi "anh Trường" hoặc "Sếp".
- Viết cho **màn hình điện thoại**: ngắn, mỗi ý một dòng, link đứng riêng một dòng.
  Không dán log, không dán mã trừ khi được hỏi.
- Hỏi thì gom vào **một** tin, ưu tiên câu hỏi có nút chọn.

## Ba skill

| Skill | Khi nào |
|---|---|
| `lam-web` | doanh nghiệp MỚI — chưa có thư mục trong `khach-hang/` |
| `sua-web` | doanh nghiệp ĐÃ CÓ — thêm/sửa sản phẩm, đổi màu, đổi số… |
| `kiem-tra-cloudflare` | hỏi về kết nối, hoặc deploy báo lỗi |

## Luật cứng

1. **Tự soạn nội dung từ ảnh — nhưng không bịa.** Được viết điều anh Trường/đối tác nói, điều
   THẤY RÕ trong ảnh, và điều đúng theo bản chất loại hàng. Cấm tự viết con số, thành tích, cam
   kết, lời khách, chất liệu đoán mò. Chi tiết: `.claude/skills/lam-web/references/viet-noi-dung.md`.
   Phần tự soạn ghi vào `_noi_dung_tu_soan` và nhắc anh Trường đưa đối tác đọc lại.
2. **Nền web luôn trắng.** Màu doanh nghiệp chỉ để nhấn. Chọn màu qua `cong-cu/chon-mau.py`,
   không gõ tay mã màu vào CSS.
3. **Không sửa `cong-cu/khung/giao-dien.css` cho riêng một doanh nghiệp.** Khung dùng chung —
   sửa ở đó là mọi web khác đổi theo. Cá nhân hoá qua `web.json`. Muốn cải tiến khung cho TẤT CẢ
   thì được, nhưng phải dựng lại + soi lại ít nhất một web cũ bằng `chup-man-hinh.mjs`.
4. **Không sửa `dist/`** — nó bị dựng lại từ `web.json` mỗi lần deploy.
5. **Khoá Cloudflare chỉ nằm trong biến môi trường** (`CLOUDFLARE_API_TOKEN`,
   `CLOUDFLARE_ACCOUNT_ID`). Không in ra, không ghi vào tệp, không commit. Repo này **CÔNG KHAI**.
6. **Không đưa lên repo thứ riêng tư** của đối tác: CCCD, hợp đồng, giá vốn, số tài khoản,
   ảnh người không đồng ý xuất hiện. Thứ gì đã lên web công khai thì lên repo được.
7. **Xong việc thì commit và đẩy thẳng `main`** (`git push origin HEAD:main`). Repo của một người
   dùng; đẩy nhánh riêng thì phiên sau trên điện thoại (mở từ `main`) không thấy hồ sơ vừa làm.
   Bị từ chối → đẩy nhánh hiện tại và nhắn anh Trường bấm gộp.
8. **Không xoá project Cloudflare, không đổi `slug` của web đã chạy** khi chưa được xác nhận bằng
   chữ — link đã gửi cho khách sẽ chết.

## Bản đồ

```
cong-cu/                    dây chuyền — chạy ở gốc repo
  xu-ly-anh.py              ảnh gốc → WebP 640/1280 + bảng xem để Claude nhìn một lượt
  tai-anh.py                tải ảnh từ link Google Drive / link ảnh
  chon-mau.py               màu chủ đạo từ mã hex / logo / ngành → bảng màu đạt tương phản
  dung-web.py               web.json + ảnh → dist/ (trang chủ + trang từng sản phẩm)
  kiem-tra-web.py           cổng kiểm tra — lỗi là không deploy
  chup-man-hinh.mjs         chụp cỡ điện thoại, bắt tràn ngang / nút nhỏ / chữ nhỏ
  trien-khai.py             tạo project + dựng + kiểm + deploy + mở thử — MỘT lệnh
  khung/                    CSS + JS dùng chung mọi web
khach-hang/
  README.md                 danh sách mọi web đã làm + địa chỉ
  _mau/web.json             mẫu rỗng
  <slug>/web.json           NGUỒN SỰ THẬT của một web
  <slug>/anh-goc/           ảnh gốc
  <slug>/anh/               ảnh đã xử lý (web dùng cái này)
  <slug>/nhat-ky.md         các lần deploy
anh-moi/                    hộp thư ảnh: anh Trường tải ảnh lên đây từ điện thoại
```
