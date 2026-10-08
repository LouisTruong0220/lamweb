---
name: lam-web
description: Tạo website giới thiệu sản phẩm cho một doanh nghiệp/hộ sản xuất thủ công mỹ nghệ (gốm, mây tre, sơn mài, gỗ, lụa, thêu, cói…) từ ảnh sản phẩm + tên sản phẩm + tên công ty, rồi đưa lên Cloudflare Pages và trả về đường link. Dùng MỖI KHI người dùng gửi thông tin một doanh nghiệp/đối tác và muốn "làm web", "tạo website", "dựng trang", "làm trang giới thiệu sản phẩm", kể cả khi chỉ dán tin nhắn Zalo của đối tác kèm vài tấm ảnh. Doanh nghiệp đã có thư mục trong khach-hang/ thì dùng skill sua-web.
---

# Làm website cho một doanh nghiệp

Người dùng là anh Trường (Roboworld), thường gõ trên **điện thoại**. Đầu ra là **một đường link
chạy được**, không phải một bản thiết kế để duyệt.

Mọi lệnh chạy ở **gốc repo**. Đường dẫn trong file này đều tính từ gốc repo.

## Nguyên tắc khi trò chuyện trên điện thoại

- **Hỏi tối đa MỘT lần**, gom mọi câu thiếu vào một tin. Thiếu thứ "nên có" thì cứ làm, ghi
  vào báo cáo cuối, đừng dừng lại hỏi.
- Lựa chọn có sẵn đáp án (phong cách, màu…) → dùng công cụ hỏi có nút bấm, đừng bắt gõ.
- Cập nhật tiến độ bằng **một dòng ngắn**. Không dán log dài, không dán mã.
- Tin cuối: **đường link đứng riêng một dòng ở đầu**, rồi tối đa 5 gạch đầu dòng.

## Bước 0 — Kiểm Cloudflare trước (10 giây)

```bash
python cong-cu/trien-khai.py --kiem-tra
```
Hỏng thì **vẫn làm tiếp** các bước dựng web, nhưng ghi nhớ để cuối cùng báo anh Trường sửa
theo `HUONG-DAN-CLOUDFLARE.md` (thông báo lỗi của script đã chỉ đúng chỗ cần sửa).

## Bước 1 — Gom thông tin

Đọc kỹ tin nhắn, kể cả đoạn dán từ Zalo/Facebook của đối tác. Rút ra:

| Mức | Thông tin |
|---|---|
| **Bắt buộc** | Tên doanh nghiệp · ít nhất 1 cách liên hệ (SĐT / Zalo / Facebook) · ảnh sản phẩm |
| Nên có | Tên + giá từng sản phẩm · địa chỉ · ngành nghề / làng nghề · logo · màu thương hiệu · câu chuyện xưởng |
| Không có thì bỏ qua | Email · giờ mở cửa · quy trình làm · điểm nổi bật |

Thiếu thứ **bắt buộc** → hỏi một tin duy nhất, ví dụ:
> Để làm web cho **Gốm Minh Long**, tôi cần thêm: ① số điện thoại/Zalo ② ảnh sản phẩm
> (gửi ảnh, link Drive, hoặc tải lên GitHub — xem cách bên dưới).

Không bao giờ **tự bịa**: năm thành lập, giải thưởng, "xuất khẩu Nhật Bản", số nghệ nhân,
chất liệu không ai nói, giá. Xem `references/viet-noi-dung.md`.

## Bước 2 — Tạo thư mục

- `slug` = tên ngắn không dấu, gạch ngang, **≤ 30 ký tự** — vì nó thành địa chỉ web
  `https://<slug>.pages.dev`. Ví dụ "Gốm Minh Long Bát Tràng" → `gom-minh-long`.
- `khach-hang/<slug>/` **đã tồn tại** → đây là việc SỬA, chuyển sang skill `sua-web`.
- Chưa có → `mkdir -p khach-hang/<slug>/anh-goc && cp khach-hang/_mau/web.json khach-hang/<slug>/`

## Bước 3 — Nhận ảnh

Chi tiết bốn đường nhận ảnh: `references/nhan-anh.md`. Tóm tắt thứ tự thử:
1. Ảnh đính kèm trong chat → tìm file thật ở `~/.claude/uploads/`
2. Ảnh anh Trường tải lên thư mục `anh-moi/` trên GitHub → `git pull`, rồi `git mv` sang `anh-goc/`
3. Link Google Drive / link ảnh → `python cong-cu/tai-anh.py khach-hang/<slug> "<link>"`
4. Không đường nào có file → hỏi lại, hướng dẫn đường 2 (dễ nhất trên điện thoại)

Rồi:
```bash
python cong-cu/xu-ly-anh.py khach-hang/<slug> [--them <tệp ở ~/.claude/uploads>...]
```
**Đọc `khach-hang/<slug>/anh/bang-xem-*.jpg`** (Read tool) để nhìn hết ảnh một lượt, rồi:
- ghép ảnh vào sản phẩm (một sản phẩm có thể nhiều ảnh: nhiều góc chụp cùng một món)
- nhận ra ảnh logo, ảnh xưởng/nghệ nhân (dùng cho mục Giới thiệu), ảnh đẹp nhất để làm bìa
- ảnh mờ / tối / nghiêng nặng → vẫn dùng nếu không có ảnh khác, nhưng ghi vào báo cáo cuối
- tên ảnh vô nghĩa (`img-2041`) không sao — `web.json` gọi ảnh theo tên đó

## Bước 4 — Chọn màu và phong cách

Nền **luôn trắng**. Màu chủ đạo chỉ để nhấn. Thứ tự ưu tiên:
1. Doanh nghiệp đã có màu → `python cong-cu/chon-mau.py --hex "#xxxxxx" --ghi khach-hang/<slug>/web.json`
2. Có logo → `--anh khach-hang/<slug>/anh/logo-640.webp`
3. Không có gì → `--nganh <ngành>` (bảng màu theo nghề trong `references/thiet-ke.md`)

Màu nhạt (vàng, hồng phấn) vẫn được: script tự sinh bản sẫm cho nút đạt chuẩn đọc.
Phong cách (`giao_dien.phong_cach`): `truyen-thong` · `hien-dai` · `sang-trong` — chọn theo
`references/thiet-ke.md`. Anh Trường không nói gì thì tự chọn, **không hỏi**.

## Bước 5 — Phân tích ảnh rồi viết `web.json`

Anh Trường thường chỉ gửi tên + ảnh. **Claude tự soạn đủ nội dung** cho một trang đầy đặn,
theo `references/viet-noi-dung.md` (bắt buộc đọc: ba nguồn được dùng, bốn thứ cấm bịa).

1. Mở bảng xem, **lập phiếu từng sản phẩm** (dáng · màu · bề mặt · chi tiết · bối cảnh ảnh).
2. Rút ra chân dung doanh nghiệp → `dong_tren_ten`, phong cách, màu.
3. Điền theo thứ tự trang hiện ra:
   `tieu_de_bia` + `tieu_de_bia_nhan` → `khau_hieu` → `diem_bia` (3 ý) → `diem_noi_bat` (3–4, có `anh`)
   → `san_pham[].dac_diem` (3 ý) + `mo_ta` → `gioi_thieu` (đoạn đầu ≤ 35 chữ) → `hoi_dap` (2–4).
4. Ghi `_noi_dung_tu_soan` liệt kê phần tự soạn.

Mỗi mục trên trang chỉ hiện khi đủ dữ liệu (bảng ở `references/thiet-ke.md`). Trang càng nhiều
mục càng giống website mẫu. Nhưng `so_lieu` và `danh_gia` **chỉ điền khi có thật**.

Những điểm hay sai:
- `ma` sản phẩm: ngắn (2–5 từ không dấu). Nó thành link `/san-pham/<ma>/` gửi qua Zalo.
- `gia`: **chỉ ghi khi được cho**. Không có thì để trống, web hiện "Liên hệ báo giá".
- `noi_bat: true` cho 2–4 món đẹp nhất. Các món này lên ảnh bìa xoay vòng, tab Khám phá và đầu lưới.
- `danh_muc`: chỉ đặt khi có ≥ 2 nhóm và ≥ 5 sản phẩm.
- `zalo` trống thì web dùng `dien_thoai` cho nút Zalo.
- Không viết chữ giữ chỗ. Cổng kiểm tra sẽ chặn.

## Bước 6 — Dựng, kiểm, soi

```bash
python cong-cu/dung-web.py khach-hang/<slug>
python cong-cu/kiem-tra-web.py khach-hang/<slug>
```
Rồi **soi bằng mắt ở cỡ điện thoại** (nên làm, nhưng không chặn deploy nếu không cài được):
```bash
npm i --no-save playwright >/dev/null 2>&1 && npx playwright install --with-deps chromium >/dev/null 2>&1
node cong-cu/chup-man-hinh.mjs khach-hang/<slug>
```
Đọc `khach-hang/<slug>/soi/dt-trang-chu-man-dau.png` (màn đầu), rồi lần lượt `dt-trang-chu-muc-NN.png`
(mỗi mục một ảnh đúng khung điện thoại) và `mt-trang-chu.png` (máy tính). Ảnh toàn trang
`dt-trang-chu.png` chỉ để xem bố cục — ô ảnh trống trong đó là giới hạn của Chromium, KHÔNG phải lỗi.
Hỏi mình:
ảnh bìa có thấy rõ sản phẩm không (sai thì đổi `anh_bia` / bỏ `noi_bat` của món có ảnh xấu) · tên có bị
xuống dòng xấu không · ảnh nào lệch tông hẳn so với phần còn lại.

## Bước 7 — Đưa lên mạng

```bash
python cong-cu/trien-khai.py khach-hang/<slug>
```
Script tự tạo project, dựng lại với đúng địa chỉ, kiểm tra, deploy, mở thử. Mặc định là
**bản chính thức**. Anh Trường nói "bản nháp" / "cho xem trước" → thêm `--nhap`.

Lỗi thì đọc dòng `✘` — script đã ghi cách sửa. Đừng thử lại cùng lệnh khi chưa đổi gì.

## Bước 8 — Lưu vào GitHub

Thêm/cập nhật một dòng trong bảng ở `khach-hang/README.md`, rồi:
```bash
git add khach-hang/<slug> khach-hang/README.md anh-moi
git commit -m "Web <Tên doanh nghiệp>: <tóm tắt>"
git push origin HEAD:main
```
Đẩy thẳng `main` (xem CLAUDE.md) để phiên sau thấy hồ sơ. Bị từ chối thì đẩy nhánh hiện tại
và nói anh Trường bấm gộp (merge).

## Bước 9 — Báo cáo (viết cho màn hình điện thoại)

```
https://gom-minh-long.pages.dev

• 12 sản phẩm, 3 nhóm · màu xanh men lam lấy từ logo
• Giới thiệu, điểm nổi bật, hỏi đáp tôi soạn từ ảnh — nhờ đối tác đọc lại
• Nút Gọi / Zalo / Chỉ đường dính đáy màn hình
• Thiếu giá 7 món → đang hiện "Liên hệ báo giá"
• Ảnh "binh-07" hơi tối — có ảnh khác thì gửi tôi thay
Muốn sửa gì cứ nhắn, ví dụ "đổi màu đỏ", "thêm sản phẩm".
```
