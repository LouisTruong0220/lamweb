# Viết nội dung: tự soạn từ ảnh, nhưng không bịa

Anh Trường thường chỉ gửi **tên công ty + vài tấm ảnh + tên sản phẩm**. Claude phải tự dựng đủ
nội dung cho một trang đầy đặn: khẩu hiệu, giới thiệu, điểm nổi bật, đặc điểm từng món, hỏi đáp.
Người đọc là khách mua lẻ, người đặt quà, chủ cửa hàng nhập hàng. Họ đọc trên điện thoại,
lướt nhanh, và quyết định bằng ảnh cùng vài câu.

## Ba nguồn được phép dùng

| Nguồn | Ví dụ được viết |
|---|---|
| **① Lời anh Trường / đối tác** | mọi thứ họ nói ra: giá, địa chỉ, năm thành lập, nhận làm theo mẫu… |
| **② Thấy rõ trong ảnh** | màu men, hoa văn, dáng, có quai/nắp/ống hút, bề mặt (bóng, nhám, vân gai), số món trong bộ, chất liệu **nhìn là biết** (sứ tráng men, mây đan, gỗ, vải thêu) |
| **③ Đúng theo bản chất loại hàng / danh mục** | công dụng ("bình giữ nhiệt mang theo khi đi làm"), bối cảnh dùng ("hợp bàn trà, phòng khách"), cách bảo quản chung của loại đó, giới thiệu công ty theo danh mục ("X cung cấp cốc sứ, bình giữ nhiệt và ly có ống hút") |

## Bốn thứ KHÔNG BAO GIỜ tự viết

1. **Con số**: năm thành lập, "20 năm kinh nghiệm", số khách, số nghệ nhân, công suất, giá,
   kích thước, dung tích, thời gian giữ nhiệt.
2. **Thành tích, cam kết**: giải thưởng, OCOP, ISO, "xuất khẩu Nhật/châu Âu", bảo hành, đổi trả,
   giao hàng toàn quốc, "nhận số lượng lớn", "in logo theo yêu cầu".
3. **Lời khách / đánh giá / số liệu đếm.** Mục `danh_gia` và `so_lieu` chỉ điền khi có thật.
   Để trống thì web tự ẩn. (Website mẫu có các mục này nhưng toàn số "MẪU", nên KHÔNG chép.)
4. **Chất liệu đoán mò**: "gỗ hương", "gốm Bát Tràng", "inox 304", "lụa tơ tằm". Màu gỗ hay vẻ
   ngoài không đủ để kết luận. Không chắc thì tả hình thức ("thân gỗ màu nâu đỏ, vân rõ").

Không chắc một câu thuộc nguồn nào thì **bỏ câu đó**.

## Đánh dấu phần tự soạn

Ghi vào `"_noi_dung_tu_soan"` những trường Claude soạn từ nguồn ② ③, ví dụ:
```json
"_noi_dung_tu_soan": "Khẩu hiệu, giới thiệu, điểm nổi bật, đặc điểm, hỏi đáp do Claude soạn từ ảnh (08/10/2026). Cần đối tác xác nhận."
```
Báo cáo cuối phải có một dòng nhắc anh Trường **đưa đối tác đọc lại** phần này.

## Quy trình phân tích ảnh → nội dung

Mở `anh/bang-xem-*.jpg`. Với ảnh nào cần xem kỹ (hoa văn, chất liệu) thì mở `anh/<tên>-1280.webp`.

**Bước 1: Lập phiếu từng sản phẩm** (chỉ ghi điều thấy được):
dáng · màu · bề mặt · chi tiết (quai, nắp, ống hút, chân đế, hoa văn) · loại hàng · bối cảnh ảnh
(chụp ở xưởng? trên bàn văn phòng? ảnh studio nền trắng?).

**Bước 2: Rút ra "chân dung" doanh nghiệp từ cả bộ:**
- Nhóm hàng chính là gì → `dong_tren_ten` (ví dụ "Cốc sứ · bình giữ nhiệt · ly có ống hút")
- Chung một nghề/chất liệu → gợi ý phong cách và màu (`thiet-ke.md`)
- Ảnh có nghệ nhân/xưởng → dùng cho `anh_gioi_thieu`, và được viết "làm tại xưởng"
- Ảnh chụp tay bằng điện thoại, không phải ảnh studio → điểm mạnh thật để viết:
  "ảnh chụp chính sản phẩm"

**Bước 3: Viết từng trường** theo bảng dưới.

## Từng trường

| Trường | Cách viết | Nguồn |
|---|---|---|
| `dong_tren_ten` | nghề · địa phương, hoặc 2–3 nhóm hàng, ≤ 45 ký tự | ①②③ |
| `nhan_badge` | 1–2 từ trong viên nhãn: "Ảnh thật", "Thủ công", "Làng nghề" (chỉ khi đúng) | ①② |
| `tieu_de_bia` | câu lớn nhất trang, 5–9 chữ, nói về **giá trị khi dùng**, không phải tên công ty. Ví dụ "Đồ uống ngon hơn trong chiếc cốc vừa ý", "Gốm men lam cho góc nhà thêm ấm" | ③ |
| `tieu_de_bia_nhan` | 2–4 chữ NẰM TRONG `tieu_de_bia` để tô màu gradient | |
| `khau_hieu` | 1 câu ≤ 20 chữ: bán gì, cho ai/ở đâu dùng | ②③ |
| `diem_bia` | 3 ý ≤ 5 chữ có dấu ✓: "Ảnh chụp sản phẩm thật", "Hỏi giá qua Zalo", "12 mẫu sản phẩm" | ①② + sự thật của chính trang web |
| `mo_ta_ngan` | 120–155 ký tự: tên + nhóm hàng + điểm khác biệt. Hiện trên Google và khi gửi link Zalo | ①②③ |
| `gioi_thieu` | 2–3 đoạn. Đoạn 1 (≤ 35 chữ) thành **chữ sáng dần khi cuộn**, nên phải là câu hay nhất: doanh nghiệp làm gì, cho ai. Đoạn sau: cách làm việc **đúng theo cấu tạo trang** (ảnh thật, hỏi giá Zalo) hoặc điều đối tác kể | ①③ |
| `diem_noi_bat` | 3–4 thẻ, tiêu đề ≤ 6 chữ + 1 câu, kèm `anh`. Mỗi thẻ có ảnh minh hoạ, đổi theo khi cuộn | ①②③ |
| `san_pham[].dac_diem` | 3 gạch đầu dòng ≤ 8 chữ, **thấy được trong ảnh** hoặc công dụng của loại hàng | ②③ |
| `san_pham[].mo_ta` | 2 đoạn ngắn: tả (②), rồi dùng vào việc gì (③) | ②③ |
| `hoi_dap` | 2–4 câu. Chỉ những câu trả lời được bằng ①, bằng cách web hoạt động ("biết giá thế nào"), hoặc bằng kiến thức chung về loại hàng (dùng/bảo quản). Không hỏi đáp về giao hàng, bảo hành, đổi trả trừ khi đối tác nói | ①③ |
| `lien_he.loi_moi` | 1 câu mời điền form | |

Ví dụ thật, chỉ từ ba tấm ảnh chụp trên bàn văn phòng: `khach-hang/hoang-ha-global/web.json`.

## Giọng văn

- Mộc, ấm, cụ thể. Một chi tiết thật đáng giá hơn mười tính từ.
- Câu ≤ 20 chữ, đoạn ≤ 3 câu. Xưng "chúng tôi", gọi "Quý khách".
- Cấm sáo rỗng: "uy tín – chất lượng – giá rẻ", "số 1", "hàng đầu", "đẳng cấp", "tinh hoa",
  "sứ mệnh", "tầm nhìn", "cam kết 100%".

| Đừng | Nên |
|---|---|
| Sản phẩm chất lượng cao, mẫu mã đa dạng | Men xanh dương bóng, lòng cốc trắng nên dễ nhìn màu trà |
| Uy tín hàng đầu thị trường | Mọi ảnh trên trang là ảnh chụp chính sản phẩm |
| Giá cả cạnh tranh nhất | (bỏ, để "Liên hệ báo giá") |

## Số, giá, tên miền

- Giá: giữ đúng cách đối tác viết, thêm "đ" nếu thiếu. Không có giá thì để trống.
- `slug` ngắn, dễ đọc qua điện thoại: `gom-minh-long`, không phải `cong-ty-tnhh-gom-su-minh-long`.
