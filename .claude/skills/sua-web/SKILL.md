---
name: sua-web
description: Sửa website của một doanh nghiệp ĐÃ CÓ trong khach-hang/ rồi đưa lên lại — thêm/bớt/sửa sản phẩm, đổi giá, đổi màu, đổi số điện thoại, đổi ảnh bìa, thêm logo, viết lại giới thiệu, gỡ một sản phẩm. Dùng khi người dùng nói "sửa web …", "thêm sản phẩm cho …", "đổi màu web …", "cập nhật giá …", hoặc nhắc tới một doanh nghiệp đã làm web trước đó. Doanh nghiệp chưa có thư mục thì dùng skill lam-web.
---

# Sửa website đã có

## 1. Tìm đúng doanh nghiệp

```bash
git pull --rebase origin main      # phiên trước có thể đã sửa từ máy khác
ls khach-hang/
cat khach-hang/README.md
```
Khớp tên anh Trường nói với thư mục (nói "Minh Long" → `gom-minh-long`). Nhiều thư mục cùng
khớp → hỏi lại bằng nút chọn. Không thư mục nào khớp → chuyển skill `lam-web`.

Đọc `khach-hang/<slug>/web.json` trước khi sửa — đó là nguồn sự thật duy nhất của web này.
**Không sửa trực tiếp `dist/`** — mọi thứ trong đó bị dựng lại từ `web.json`.

## 2. Sửa

| Yêu cầu | Làm gì |
|---|---|
| Thêm sản phẩm | nhận ảnh (xem `../lam-web/references/nhan-anh.md`) vào `anh-goc/` → `xu-ly-anh.py` → đọc bảng xem → thêm mục vào `san_pham` |
| Bớt sản phẩm | xoá mục khỏi `san_pham`. **Giữ** ảnh trong `anh-goc/` (lỡ cần lại) |
| Đổi giá / tên / mô tả | sửa trường tương ứng. Đổi `ten` thì **giữ nguyên `ma`** — link cũ đã gửi qua Zalo vẫn chạy |
| Đổi màu | `python cong-cu/chon-mau.py --hex "#..." --ghi khach-hang/<slug>/web.json` (hoặc `--anh`, `--nganh`) |
| "Màu đậm hơn / nhạt hơn / ấm hơn" | tự chỉnh mã hex rồi chạy lệnh trên — script báo tương phản |
| Đổi ảnh bìa | `giao_dien.anh_bia` = tên ảnh khác; thẻ bìa xoay thêm ảnh các món `noi_bat` |
| Thêm nội dung (giới thiệu, hỏi đáp, điểm nổi bật…) | theo `../lam-web/references/viet-noi-dung.md` — cập nhật `_noi_dung_tu_soan` |
| Thêm logo | ảnh tên có chữ `logo` → `xu-ly-anh.py` → `cong_ty.logo: "logo"` |
| Đổi số điện thoại / Zalo / địa chỉ | `lien_he.*` |
| Đổi phong cách | `giao_dien.phong_cach`: `truyen-thong` / `hien-dai` / `sang-trong` |
| Đổi chữ trên nút / tiêu đề mục | `nhan` — ví dụ `{"san_pham": "Bộ sưu tập", "lien_he_gia": "Nhắn để biết giá"}` |

Luật nội dung giữ nguyên như lúc làm mới: không bịa (`../lam-web/references/viet-noi-dung.md`).

## 3. Dựng — kiểm — đưa lên — lưu

```bash
python cong-cu/trien-khai.py khach-hang/<slug>          # tự dựng lại + kiểm + deploy
```
Sửa lớn về hình ảnh (màu, bìa, phong cách) → soi lại bằng `node cong-cu/chup-man-hinh.mjs khach-hang/<slug>`
trước khi deploy, đọc `soi/dt-trang-chu-man-dau.png`.

```bash
git add khach-hang/<slug> khach-hang/README.md anh-moi
git commit -m "Sửa web <Tên>: <việc đã sửa>"
git push origin HEAD:main
```

## 4. Báo cáo

Link đứng riêng dòng đầu, rồi một hai dòng nói đã đổi gì. Nhắc: điện thoại có thể đang giữ
bản cũ trong bộ nhớ đệm → kéo xuống để tải lại trang.

## Không làm khi chưa được xác nhận rõ ràng

- **Gỡ hẳn website** (xoá project Cloudflare) — không thể hoàn tác, mọi link đã gửi khách chết.
  Phải hỏi lại và chỉ làm khi anh Trường xác nhận bằng chữ.
- Đổi `slug` — đổi địa chỉ web, link cũ chết. Cần thì tạo project mới, giữ project cũ.
- Xoá thư mục `khach-hang/<slug>/`.
