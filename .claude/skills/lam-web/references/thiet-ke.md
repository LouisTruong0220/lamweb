# Thiết kế — cá nhân hoá mà vẫn chắc tay

Khung giao diện (`cong-cu/khung/giao-dien.css`) đã được soi kỹ ở cỡ điện thoại. Cá nhân hoá
**qua `web.json`**, KHÔNG sửa CSS cho từng doanh nghiệp — sửa CSS là mọi web khác đổi theo.

## Năm núm vặn

| Núm | Ở đâu | Ảnh hưởng |
|---|---|---|
| Màu chủ đạo | `giao_dien.mau_chu_dao` | nút, chữ nhấn, viền, nền nhạt các mục, thanh địa chỉ trình duyệt |
| Phong cách | `giao_dien.phong_cach` | phông tiêu đề + độ bo góc |
| Ảnh bìa | `giao_dien.anh_bia` + các món `noi_bat` | thẻ ảnh xoay vòng ở màn đầu tiên |
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

Thẻ bìa xoay vòng: `anh_bia` trước, rồi ảnh đầu của các món `noi_bat`. Khung 4:5 trên điện thoại,
1:1 trên máy tính, **cắt mép** (object-fit: cover) — chọn ảnh sản phẩm nằm giữa khung.

Thẻ sản phẩm trong lưới cũng cắt mép (khung vuông) cho đều hàng. **Trang chi tiết** thì KHÔNG cắt
(contain) — khách luôn thấy trọn món. Ảnh nào sản phẩm nằm sát mép thì cắt lại ảnh gốc cho cân rồi
chạy lại `xu-ly-anh.py`.

## Tuyến nội dung trang chủ — mục nào hiện khi nào

Theo website mẫu (phong cách Flock/Webflow). Thứ tự cố định; mục thiếu dữ liệu thì tự ẩn.

| # | Mục | Hiệu ứng | Hiện khi |
|---|---|---|---|
| 1 | Bìa | nền lưới + quầng sáng trôi · chữ trượt lên · thẻ ảnh **xoay vòng ảnh sản phẩm**, nghiêng theo chuột · 2 nhãn nổi lắc lư (máy tính) | luôn có |
| 2 | Dải chữ chạy | tên sản phẩm + nhóm chạy ngang vô tận | ≥ 3 tên |
| 3 | Vì sao chọn | thẻ sáng dần theo vị trí cuộn; máy tính: khung ảnh dính bên phải đổi theo; điện thoại: ảnh mở ra ngay trong thẻ | `diem_noi_bat` ≥ 2 |
| 4 | Khám phá sản phẩm | tab với viên thuốc trượt, khung trượt lên khi đổi tab | ≥ 2 sản phẩm có ảnh |
| 5 | Tất cả sản phẩm | thẻ trượt lên lần lượt; máy tính: ảnh phóng + nghiêng khi rê chuột | luôn có |
| 6 | Số liệu | số chạy từ 0 | `so_lieu` **thật** |
| 7 | Quỹ đạo | ảnh sản phẩm xoay quanh logo, chạm để xem | ≥ 4 sản phẩm có ảnh |
| 8 | Lời khách | 3 cột cuộn dọc vô tận | `danh_gia` **thật** ≥ 2 |
| 9 | Giới thiệu | chữ đoạn đầu sáng dần từng từ theo cuộn | `gioi_thieu` |
| 10 | Quy trình | các bước đánh số trượt lên | `quy_trinh` |
| 11 | Hỏi đáp | xổ ra/thu vào, dấu + xoay thành − | `hoi_dap` |
| 12 | Nhận báo giá | form soạn sẵn tin nhắn → mở Zalo / SMS (không cần máy chủ) | có SĐT hoặc Zalo |
| — | Chân trang | tên thương hiệu chữ khổng lồ mờ dần, tự co cho vừa | luôn có |

Mọi hiệu ứng tắt khi điện thoại bật "Giảm chuyển động". Khi JS không chạy, nội dung vẫn hiện đủ.

## Những thứ đã làm sẵn cho điện thoại — đừng phá

- Thanh **Gọi · Zalo · Chỉ đường** dính đáy, trong tầm ngón cái; máy tính thì thành nút tròn nổi.
- Trang sản phẩm: thanh đáy đổi thành **"Hỏi giá qua Zalo"** — bấm là chép sẵn câu hỏi kèm tên
  + link sản phẩm, khách mở Zalo chỉ việc dán.
- Nút **Chia sẻ** dùng bảng chia sẻ của điện thoại (gửi Zalo/Messenger một chạm).
- Mỗi sản phẩm có trang riêng + ảnh xem trước 1200×630 → dán link vào Zalo hiện ảnh đẹp.
- Ảnh vuốt ngang trên trang sản phẩm, có đếm 1/4.
- Chữ thân 17px, nút ≥ 48px, tương phản chữ/nút ≥ 4,5:1, không tràn ngang.
- Ảnh WebP 640/1280 + lazy load → trang chủ ~0,4 MB, mở nhanh trên 4G.
