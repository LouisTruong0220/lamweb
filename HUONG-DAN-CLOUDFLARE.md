# Kết nối Cloudflare cho Claude Code trên điện thoại

Làm **một lần**, mất khoảng 10 phút. Xong thì từ điện thoại chỉ cần nhắn
"làm web cho …" là Claude tự đưa web lên mạng.

Có 3 bước:

| Bước | Làm ở đâu | Lấy được gì |
|---|---|---|
| 1 | dash.cloudflare.com | **API Token**: chìa khoá cho phép đăng web |
| 2 | dash.cloudflare.com | **Account ID**: mã tài khoản Cloudflare |
| 3 | claude.ai/code | Cất hai thứ trên vào **Environment variables**, mở mạng cho Cloudflare |

> Bước 1 và 2 làm trên máy tính cho dễ. Điện thoại cũng làm được: mở trình duyệt, bật chế độ
> "Trang web cho máy tính" (Desktop site).

---

## Bước 1: Tạo API Token

1. Vào **https://dash.cloudflare.com/profile/api-tokens** và đăng nhập tài khoản Cloudflare
   của công ty.
2. Bấm **Create Token**.
3. Kéo xuống cuối, ở dòng **Create Custom Token**, bấm **Get started**.
4. Điền như sau:

   | Ô | Điền |
   |---|---|
   | **Token name** | `lamweb-claude-code` |
   | **Permissions** | 3 ô chọn lần lượt: **Account** · **Cloudflare Pages** · **Edit** |
   | **Account Resources** | **Include** · chọn đúng tài khoản công ty |
   | **Client IP Address Filtering** | **để trống** (máy chủ Claude đổi IP liên tục, lọc IP sẽ bị chặn) |
   | **TTL** | để trống, hoặc đặt hết hạn sau 1 năm cho an toàn |

5. Bấm **Continue to summary**, rồi **Create Token**.
6. **Copy token ngay.** Cloudflare chỉ hiện token này **một lần duy nhất**. Dán tạm vào
   Ghi chú của điện thoại; xong bước 3 thì xoá ghi chú đó.

> **Vì sao chỉ cấp quyền Cloudflare Pages · Edit?** Lỡ token bị lộ thì người khác chỉ đăng
> được trang web, không đụng được tên miền, DNS hay thanh toán của công ty.
> Không dùng mẫu "Edit Cloudflare Workers" vì mẫu đó cấp rộng hơn mức cần.

## Bước 2: Lấy Account ID

1. Vào **https://dash.cloudflare.com** và chọn tài khoản công ty.
2. Account ID nằm ở **một trong hai chỗ**:
   - **Trên thanh địa chỉ**: `dash.cloudflare.com/`**`a1b2c3...`**`/home`. Dãy 32 ký tự
     ngay sau dấu `/` đầu tiên chính là Account ID.
   - Hoặc vào **Workers & Pages**. Cột bên phải (hoặc cuối trang trên điện thoại) có mục
     **Account ID**, bấm biểu tượng copy.
3. Account ID **không phải mật khẩu**, nhưng cũng đừng đăng công khai.

## Bước 3: Cất vào Claude Code (Environment variables)

Phiên Claude Code trên điện thoại chạy trong một **môi trường đám mây** (cloud environment).
Biến môi trường đặt ở đó, mọi phiên sau đều tự có.

1. Mở **https://claude.ai/code** (trình duyệt trên điện thoại hoặc máy tính đều được).
2. Ngay trên ô nhập tin nhắn có một nút **hình đám mây kèm tên môi trường** (thường là
   *Default*). Bấm vào nút đó.
3. Ở mục **Cloud**, bấm **biểu tượng bánh răng** cạnh môi trường đang dùng. Hoặc bấm
   **Add cloud environment** để tạo môi trường riêng, đặt tên `Lam web`.
4. Trong hộp thoại, điền 3 phần:

### a) Network access: chọn Custom

Mặc định là **Trusted**, mà Trusted **không cho** ra `api.cloudflare.com`, nên deploy sẽ bị chặn.

- Chọn **Custom**.
- Trong ô **Allowed domains**, dán đúng các dòng sau:
  ```
  api.cloudflare.com
  *.pages.dev
  drive.google.com
  drive.usercontent.google.com
  *.googleusercontent.com
  cdn.playwright.dev
  playwright.download.prss.microsoft.com
  archive.ubuntu.com
  security.ubuntu.com
  ```
- **Tích ô** *Also include default list of common package managers* (để còn tải được
  wrangler và Pillow).

| Tên miền | Để làm gì |
|---|---|
| `api.cloudflare.com` | **bắt buộc**: tạo project và đẩy web lên |
| `*.pages.dev` | mở thử web sau khi đăng |
| `drive.google.com` · `drive.usercontent.google.com` · `*.googleusercontent.com` | tải ảnh từ link Google Drive đối tác gửi |
| `cdn.playwright.dev` · `playwright.download.prss.microsoft.com` · `archive.ubuntu.com` · `security.ubuntu.com` | trình duyệt ảo để Claude chụp web ở cỡ điện thoại, tự soi lỗi |

### b) Environment variables: dán hai dòng

```
CLOUDFLARE_API_TOKEN=dán-token-ở-bước-1
CLOUDFLARE_ACCOUNT_ID=dán-account-id-ở-bước-2
```
- Mỗi biến một dòng, **không có dấu cách** quanh dấu `=`, không cần ngoặc kép.
- Tên biến phải **đúng từng chữ** như trên, vì công cụ đăng web của Cloudflare (wrangler)
  tự đọc đúng hai tên này.

### c) Setup script (không bắt buộc, giúp mỗi phiên khởi động nhanh hơn)

```bash
#!/bin/bash
pip install --quiet pillow pillow-heif 2>/dev/null || pip install --quiet --break-system-packages pillow pillow-heif
npm install -g wrangler@4 >/dev/null 2>&1 || true
```

5. Bấm **Save** (hoặc **Create environment**).
6. **Mở một phiên MỚI.** Phiên đang chạy không tự nhận biến vừa thêm. Lúc tạo phiên, chọn
   repo **LouisTruong0220/lamweb** và môi trường vừa sửa.

## Kiểm tra

Trong phiên mới, nhắn:
> kiểm tra kết nối Cloudflare

Thấy **✔ Sẵn sàng deploy** là xong. Báo lỗi gì thì Claude sẽ chỉ đúng chỗ cần sửa.

---

## Bảo mật: nên biết

- **Ai dùng môi trường này cũng đọc được biến.** Môi trường cá nhân thì chỉ mình anh dùng.
  Đừng chia sẻ phiên ở chế độ Public khi trong phiên có in nội dung biến.
- **Không bao giờ** dán token vào khung chat, vào tệp trong repo, hay gửi qua Zalo.
  Repo `lamweb` để **công khai**, ai cũng đọc được.
- Nghi token bị lộ: vào dash.cloudflare.com/profile/api-tokens, bấm **Roll** (đổi mã) hoặc
  **Delete** token cũ, tạo token mới, rồi dán lại ở bước 3b. Web đã đăng **không** bị ảnh hưởng.
- Cloudflare Pages gói miễn phí: không giới hạn số trang, 500 lần đăng/tháng. Đủ cho hàng trăm
  đối tác.

## Sau này: gắn tên miền riêng cho đối tác

Đối tác mua tên miền riêng (ví dụ `gomminhlong.vn`) thì vào dash.cloudflare.com, chọn
**Workers & Pages**, chọn project, rồi **Custom domains** → **Set up a custom domain**.
Việc này cần quyền quản lý DNS nên làm tay trên web Cloudflare, token ở trên cố ý không có
quyền đó.
