---
name: kiem-tra-cloudflare
description: Kiểm tra và chẩn đoán kết nối Cloudflare cho việc đưa website lên mạng — token API, mã tài khoản, quyền Pages, mạng của phiên Claude Code. Dùng khi người dùng hỏi "đã kết nối Cloudflare chưa", "kiểm tra token", "sao không deploy được", khi deploy báo lỗi xác thực/mạng, hoặc ngay sau khi người dùng vừa cài biến môi trường.
---

# Kiểm tra Cloudflare

```bash
python cong-cu/trien-khai.py --kiem-tra
```

Đọc kết quả và trả lời anh Trường **bằng một câu kết luận + việc cần làm** (ngắn, cho điện thoại).

| Script báo | Nghĩa là | Anh Trường cần làm |
|---|---|---|
| `Thiếu biến môi trường` | chưa đặt, hoặc đặt rồi nhưng đang ở **phiên cũ** | đặt theo HUONG-DAN-CLOUDFLARE.md bước 3, rồi **mở phiên mới** |
| `Không nối được api.cloudflare.com` / mạng chặn | môi trường đang để mạng "Trusted" | đổi Network access sang **Custom**, thêm `api.cloudflare.com` |
| `Token không hợp lệ` | gõ sai / thiếu ký tự / token đã bị xoá | tạo token mới (bước 1), dán lại |
| `Token hợp lệ nhưng KHÔNG vào được Pages` | sai Account ID, hoặc token thiếu quyền Pages Edit | xem lại bước 1 (quyền) và bước 2 (Account ID) |
| `✔ Sẵn sàng deploy` | mọi thứ ổn | — |

Lỗi khi deploy thật (`wrangler`):
- `Authentication error [code: 10000]` → token không có quyền trên ĐÚNG tài khoản trong
  `CLOUDFLARE_ACCOUNT_ID` (hai biến trỏ hai tài khoản khác nhau).
- `A project with this name already exists` → không xảy ra với script này (nó dùng lại
  project cũ). Gặp thì tên đó thuộc project khác trong cùng tài khoản — đổi `slug`.
- Kẹt ở `npx` tải wrangler → mạng chặn `registry.npmjs.org`: tích lại ô "Also include default
  list of common package managers" trong cài đặt mạng.

**Không bao giờ** in token ra màn hình, không ghi vào tệp, không commit. Cần xem có biến
chưa thì chỉ in độ dài: `python -c "import os;print(len(os.environ.get('CLOUDFLARE_API_TOKEN','')))"`.
