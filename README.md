# lamweb: làm website cho đối tác thủ công mỹ nghệ, ngay trên điện thoại

Bộ skill cho **Claude Code** của Roboworld. Gửi tên doanh nghiệp, ảnh và tên sản phẩm, Claude
sẽ tự thiết kế, dựng website và đưa lên **Cloudflare Pages** (miễn phí), rồi trả về đường link.

Dành cho các doanh nghiệp vừa và nhỏ, hộ sản xuất làng nghề (gốm, mây tre, sơn mài, gỗ,
lụa, thêu, cói…): ít chi phí, không rành công nghệ.

## Website làm ra trông thế nào

- **Ưu tiên điện thoại.** Khách của đối tác xem web chủ yếu trên điện thoại.
- **Nền trắng**, màu chủ đạo riêng cho từng doanh nghiệp. Màu lấy từ logo, theo màu doanh
  nghiệp chọn, hoặc theo chất liệu của nghề. Màu nhạt đến đâu thì nút bấm vẫn tự sẫm lại cho
  đủ rõ để đọc.
- Thanh **Gọi · Zalo · Chỉ đường** dính đáy màn hình, nằm trong tầm ngón cái.
- Lưới sản phẩm hai cột, lọc theo nhóm bằng cách vuốt ngang.
- Mỗi sản phẩm có **trang riêng**: ảnh vuốt ngang, nút **"Hỏi giá qua Zalo"** (tự chép sẵn tên
  sản phẩm để khách dán vào Zalo), nút **Chia sẻ** gửi Zalo/Messenger một chạm.
- Dán link sản phẩm vào Zalo sẽ hiện **ảnh xem trước** đẹp.
- Nhẹ, khoảng 0,4 MB cho trang chủ, mở nhanh trên 4G. Có sẵn sitemap và mô tả cho Google.
- Ba phong cách: *truyền thống* · *sang trọng* · *hiện đại*. Claude tự chọn theo nghề.

## Cài đặt một lần

1. **Kết nối GitHub với Claude Code**: mở app Claude, vào tab **Code**, làm theo hướng dẫn
   kết nối GitHub và chọn repo `LouisTruong0220/lamweb`.
2. **Kết nối Cloudflare**: làm theo **[HUONG-DAN-CLOUDFLARE.md](HUONG-DAN-CLOUDFLARE.md)**
   (tạo API Token, lấy Account ID, dán vào Environment variables, mở mạng cho Cloudflare).
3. Mở phiên mới, nhắn *"kiểm tra kết nối Cloudflare"*. Thấy ✔ là xong.

## Dùng hằng ngày (trên điện thoại)

Mở app Claude, vào tab **Code**, chọn repo **lamweb**, rồi nhắn như nói chuyện bình thường.

**Làm web mới:**
> Làm web cho Gốm Minh Long ở Bát Tràng, SĐT 0912 345 678.
> Sản phẩm: bình hoa sen 850k, lọ tỳ bà, đĩa Chu Đậu 1,2 triệu. Ảnh đính kèm.

Cũng có thể dán nguyên tin nhắn Zalo của đối tác vào, Claude tự lọc thông tin.

**Gửi ảnh, chọn một trong ba cách:**

| Cách | Làm thế nào |
|---|---|
| Đính kèm trong chat | bấm 📎 gửi ảnh như nhắn tin |
| Tải lên GitHub (chắc chắn nhất) | mở **github.com/LouisTruong0220/lamweb/tree/main/anh-moi**, bấm **Add file** → **Upload files**, chọn ảnh, bấm **Commit changes**, rồi nhắn Claude "đã tải ảnh" |
| Link Google Drive | gửi link thư mục Drive (để chế độ *Bất kỳ ai có đường liên kết*) |

**Sửa web đã có:**
> Web Gốm Minh Long: thêm sản phẩm "ấm chén men rạn", giá 650k, ảnh đã tải lên
> Đổi màu web Minh Long sang đỏ son
> Sửa giá bình hoa sen thành 900k

**Xem bản nháp trước:** thêm chữ *"bản nháp"* vào tin nhắn. Bản nháp có link riêng, không đè
lên bản chính.

## Bên trong repo

| Thư mục | Chứa gì |
|---|---|
| `.claude/skills/` | 3 skill: `lam-web` · `sua-web` · `kiem-tra-cloudflare` |
| `cong-cu/` | các script: xử lý ảnh, chọn màu, dựng web, kiểm tra, chụp màn hình, đăng lên mạng |
| `khach-hang/<tên>/` | hồ sơ từng doanh nghiệp: `web.json` (nội dung) + ảnh |
| `anh-moi/` | hộp thư ảnh tải lên từ điện thoại |

Mỗi website = một tệp `web.json` + một thư mục ảnh. Dựng lại lúc nào cũng được:
```bash
python cong-cu/trien-khai.py khach-hang/<ten>
```

## Lưu ý

- Repo **công khai**. Ảnh và thông tin liên hệ vốn sẽ đăng lên web công khai nên không sao,
  nhưng **không** đưa lên đây hợp đồng, giấy tờ tuỳ thân, giá vốn của đối tác.
  **Không bao giờ** dán API Token vào đây.
- Claude **không bịa** thông tin doanh nghiệp (năm thành lập, giải thưởng, xuất khẩu, giá…).
  Thiếu gì thì web ẩn mục đó, và Claude báo lại để anh hỏi thêm đối tác.
