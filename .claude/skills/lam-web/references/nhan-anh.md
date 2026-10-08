# Nhận ảnh từ điện thoại — bốn đường

Phiên Claude Code trên điện thoại chạy trên **máy chủ đám mây**, không phải trên điện thoại.
Ảnh anh Trường đính kèm trong chat **chưa chắc** đã thành tệp trên máy chủ — Claude nhìn thấy
ảnh nhưng có thể không lưu ra đĩa được. Vì vậy phải dò theo thứ tự dưới đây.

## Đường 1 — Ảnh đính kèm trong chat

```bash
ls -la ~/.claude/uploads/ 2>/dev/null
find ~ /tmp -maxdepth 4 -type f \( -iname '*.jpg' -o -iname '*.jpeg' -o -iname '*.png' -o -iname '*.heic' -o -iname '*.webp' \) -mmin -180 2>/dev/null | grep -v node_modules | head -50
```
Có tệp → đưa thẳng vào bước xử lý:
```bash
python cong-cu/xu-ly-anh.py khach-hang/<slug> --them ~/.claude/uploads/*
```
Rồi **chép** bản gốc vào `khach-hang/<slug>/anh-goc/` để phiên sau còn ảnh mà dựng lại
(`cp ~/.claude/uploads/* khach-hang/<slug>/anh-goc/`).

Không có tệp nào mà trong chat vẫn có ảnh → Claude chỉ "nhìn" được, không lưu được.
Dùng ảnh đó để **hiểu** sản phẩm (đặt tên, viết mô tả), nhưng phải xin tệp qua đường 2 hoặc 3.

## Đường 2 — Tải lên thư mục `anh-moi/` trên GitHub (dễ nhất trên điện thoại)

Hướng dẫn anh Trường đúng nguyên văn này (ngắn, làm được bằng một tay):

> 1. Mở **github.com/LouisTruong0220/lamweb/tree/main/anh-moi** trên trình duyệt điện thoại
> 2. Bấm **Add file → Upload files** → **choose your files** → chọn ảnh trong thư viện
> 3. Kéo xuống bấm **Commit changes**
> 4. Nhắn lại tôi "đã tải ảnh"

Sau đó:
```bash
git pull --rebase origin main
mkdir -p khach-hang/<slug>/anh-goc
git mv anh-moi/*.* khach-hang/<slug>/anh-goc/ 2>/dev/null; ls anh-moi
```
`anh-moi/.gitkeep` phải còn lại — đó là thứ giữ thư mục tồn tại cho lần sau. Đừng chuyển nó.

⚠ Nếu cùng lúc `anh-moi/` có ảnh của HAI doanh nghiệp (tải lên mà quên báo) → đọc bảng
xem, chia theo nội dung, hỏi lại nếu không chắc. Đừng gộp bừa.

## Đường 3 — Link Google Drive / link ảnh

Đối tác hay gửi ảnh bằng một thư mục Drive. Thư mục phải để **"Bất kỳ ai có đường liên kết"**.
```bash
python cong-cu/tai-anh.py khach-hang/<slug> "https://drive.google.com/drive/folders/..."
```
Script đi cả thư mục con, lấy **tệp gốc** (đủ nét), tên thư mục con được ghép vào tên ảnh
(`binh-hoa/IMG_01.jpg` → `binh-hoa-img-01.jpg`) — gợi ý tốt để ghép ảnh vào sản phẩm.

Báo "không phải ảnh" → thư mục đang để riêng tư. Báo lỗi mạng → môi trường chưa cho phép
`drive.google.com` (xem HUONG-DAN-CLOUDFLARE.md bước 3).

Ảnh trên Facebook/Zalo **không tải tự động được** (cần đăng nhập) → nhờ lưu về máy rồi đi đường 2.

## Đường 4 — Không có tệp nào

Hỏi lại một lần, đưa đường 2 (copy nguyên khối hướng dẫn ở trên) và đường 3.
Trong lúc chờ có thể dựng sẵn `web.json` phần chữ.

## Sau khi có ảnh

- Ảnh gốc từ điện thoại 3–5 MB/tấm là bình thường. `xu-ly-anh.py` xuất bản 640 px (~40 KB)
  và 1280 px (~120 KB). Web chỉ dùng hai bản đó.
- Ảnh HEIC của iPhone đọc được (script tự cài `pillow-heif`).
- Ảnh chụp nghiêng do cờ xoay EXIF được tự xoay lại đúng chiều.
- Tên tệp có "logo" → giữ thêm bản PNG nền trong cho đầu trang.
