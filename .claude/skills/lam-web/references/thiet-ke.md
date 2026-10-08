# Thiết kế — cá nhân hoá mà vẫn chắc tay

Khung giao diện (`cong-cu/khung/giao-dien.css`) đã được soi kỹ ở cỡ điện thoại. Cá nhân hoá
**qua `web.json`**, KHÔNG sửa CSS cho từng doanh nghiệp — sửa CSS là mọi web khác đổi theo.

## Năm núm vặn

| Núm | Ở đâu | Ảnh hưởng |
|---|---|---|
| Màu chủ đạo | `giao_dien.mau_chu_dao` | nút, chữ nhấn, viền, nền nhạt các mục, thanh địa chỉ trình duyệt |
| Phong cách | `giao_dien.phong_cach` | phông tiêu đề + độ bo góc |
| Ảnh bìa | `giao_dien.anh_bia` + `vi_tri_anh_bia` | ấn tượng đầu tiên trên điện thoại |
| Thứ tự sản phẩm | `noi_bat: true` | món nào lên đầu lưới |
| Mục nào hiện | để trống = ẩn | độ dài trang |

## Phong cách — chọn theo nghề

| Phong cách | Phông tiêu đề | Bo góc | Hợp với |
|---|---|---|---|
| `truyen-thong` | Lora (có chân, ấm) | 10px | gốm, mây tre, cói, sơn mài, gỗ, làng nghề lâu đời — **mặc định** |
| `sang-trong` | Playfair Display (có chân, thanh) | 3px | lụa, trang sức bạc, đồ gỗ cao cấp, quà tặng doanh nghiệp |
| `hien-dai` | Be Vietnam Pro (không chân) | 16px | đồ decor trẻ, nến thơm, đồ len móc, thương hiệu bán online |

Cả ba đều dùng Be Vietnam Pro cho thân bài — phông viết cho tiếng Việt, dấu không bị đè.

## Màu theo nghề (khi không có logo, không có màu riêng)

`python cong-cu/chon-mau.py --nganh <mã>`

| Mã | Màu | Lý do |
|---|---|---|
| `gom` | #1F4E8C xanh men lam | men lam Chu Đậu, Bát Tràng |
| `gom-nau` | #8C4A2F nâu đất nung | men da lươn, gốm Phù Lãng |
| `may-tre` | #7A6A2E vàng rơm sẫm | |
| `coi` | #6F7F3A xanh lục cói | |
| `son-mai` | #9E2A2B đỏ son | |
| `go` | #7B4A2A nâu gỗ gụ | |
| `lua` | #8E3B5F tím hồng lụa | |
| `theu` | #A23B3B đỏ chỉ thêu | |
| `det-tho-cam` | #B1462A đỏ cam thổ cẩm | |
| `da` | #4F5D63 xám đá xanh | |
| `bac-dong` | #8A6D3B đồng thau | |
| `giay-do` | #A67C3D vàng giấy dó | |
| `nen-thom` | #6B4E71 tím oải hương | |
| `tranh` | #2F5D50 xanh lục bảo | tranh Đông Hồ |
| `nong-san` | #3F7A3A xanh lá | |
| `khac` | #2F5D62 xanh mòng két | trung tính, hợp mọi thứ |

**Ảnh sản phẩm có màu nào chiếm ưu thế thì màu chủ đạo nên HÒA với nó, đừng đánh nhau.**
Gốm men lam + màu đỏ chói = rối mắt. Nhìn bảng xem rồi mới quyết.

Logo nhiều màu → `chon-mau.py --anh` lấy màu tươi chiếm diện tích lớn nhất. Ra màu lạ (ví dụ
màu viền mỏng) thì dùng `--hex` với màu mình thấy đúng hơn.

## Ảnh bìa — quan trọng nhất trên điện thoại

Ảnh bìa chiếm gần nửa màn hình đầu tiên. Chọn:
- **sản phẩm rõ, đủ sáng, nền gọn** — hơn là ảnh "nghệ thuật" tối
- ảnh có **cả một nhóm sản phẩm** hoặc **nghệ nhân đang làm** thường tốt hơn một món đơn lẻ
- tránh ảnh có chữ/watermark to, ảnh chụp màn hình, ảnh danh thiếp

Khung bìa tự theo hướng ảnh (dọc 4:5 · vuông 1:1 · ngang 4:3) và **cắt mép** (object-fit: cover).
Sản phẩm lệch về một phía → chỉnh `vi_tri_anh_bia` ("50% 30%" = lấy phần trên hơn;
"30% 50%" = lệch trái). Soi lại bằng `chup-man-hinh.mjs`.

Ảnh trong **thẻ sản phẩm** và **trang chi tiết** thì KHÔNG cắt (contain) — luôn thấy trọn món.

## Mục nào nên hiện

| Mục | Hiện khi |
|---|---|
| Điểm nổi bật | có 2–4 ý **thật** doanh nghiệp nói ra (vẽ tay, nhận khắc logo, ship toàn quốc…) |
| Giới thiệu | có ít nhất 2 câu thông tin thật về xưởng/người làm |
| Quy trình | doanh nghiệp kể quy trình, hoặc có ảnh các công đoạn |
| Danh mục lọc | ≥ 5 sản phẩm và ≥ 2 nhóm |

Trang ngắn mà thật > trang dài mà bịa. Một trang chỉ có bìa + 6 sản phẩm + liên hệ là một
trang tốt.

## Những thứ đã làm sẵn cho điện thoại — đừng phá

- Thanh **Gọi · Zalo · Chỉ đường** dính đáy, trong tầm ngón cái; máy tính thì thành nút tròn nổi.
- Trang sản phẩm: thanh đáy đổi thành **"Hỏi giá qua Zalo"** — bấm là chép sẵn câu hỏi kèm tên
  + link sản phẩm, khách mở Zalo chỉ việc dán.
- Nút **Chia sẻ** dùng bảng chia sẻ của điện thoại (gửi Zalo/Messenger một chạm).
- Mỗi sản phẩm có trang riêng + ảnh xem trước 1200×630 → dán link vào Zalo hiện ảnh đẹp.
- Ảnh vuốt ngang trên trang sản phẩm, có đếm 1/4.
- Chữ thân 17px, nút ≥ 48px, tương phản chữ/nút ≥ 4,5:1, không tràn ngang.
- Ảnh WebP 640/1280 + lazy load → trang chủ ~0,4 MB, mở nhanh trên 4G.
