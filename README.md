# BM Cân Xe Tự Động

Hệ thống chụp hình, lưu biển số và cân nặng tự động — nhà máy Bình Minh (tinh bột khoai mì).

- Live: [canxe.redtigerhead.com](https://canxe.redtigerhead.com)
- Worker Cloudflare: `bm-can-xe`
- Whitepaper phần cứng & kích hoạt chụp: [WHITEPAPER.md](./WHITEPAPER.md)
- Backup mill **không logo**: nhánh `backup/v5-pre-logo`
- Mill + logo sạch: nhánh `checkpoint/v5-brand`

Phần mềm mill **tạm dừng** thêm tính năng. Việc tiếp theo: giao tiếp cầu cân, camera IP, máy đo củ mì.

---

## Hiện trạng thiết bị

| Hạng mục | Tình trạng |
|---|---|
| Cầu cân | Đã có (chưa có màn phụ tài xế) |
| Camera | Tận dụng IP cam sẵn có — model giao sau, chỉnh nhẹ CGI/ONVIF |
| Máy đo điểm củ mì | Đã có RS232 — **chưa biết baud / khung tin** |
| Tablet chống nước | Để sau; thử mẫu giai đoạn 1 trên PC |

---

## Chiến thuật (hai bước, làm song song)

**Bước 1A — Mock-up.** Cân nhỏ + xe truck đồ chơi dán biển. Cùng protocol với hệ thật (`ScaleEvent` / `CameraShot` / `MeterReading`). Không bịa giao thức demo.

**Bước 1B — Nghe thiết bị thật.** Máy tính sample + USB-RS232: log raw máy bột và đầu cân; quét baud 9600 8N1 trước. Xác định ngôn ngữ/kiểu dữ liệu trước khi nối mill.

Khi 1A+1B đạt: **thay mock bằng thiết bị thật** (đổi driver, không đổi nghiệp vụ).

**Bước 2 — Song song sổ cũ ≥ 30 ngày.** Đối chiếu kg, biển, IN/OUT, điểm bột. **Lỗi < 1%** → chính thức. ≥ 1% → giữ sổ cũ, sửa driver.

Chi tiết sơ đồ kích hoạt chụp (cân ổn 2 giây → snapshot 2 cam → OCR ≥95%): xem [WHITEPAPER.md §3](./WHITEPAPER.md).

---

## Kích hoạt chụp (tóm tắt)

Nguồn sự thật là **cân ổn định**, không phải camera tự “thấy xe dừng”.

1. Đầu cân spew kg (RS232/Ethernet) ± bit STABLE nếu có.  
2. Driver: `|Δkg| < ε` trong **≥ 2,0 s** → một cạnh `stable`.  
3. Cùng lúc snapshot cam trước + cam sau (CGI/ONVIF). Nét thấp → chụp lại 1 lần. JPEG xám.  
4. Khớp biển ≥ 95% → điền, **không gõ tay**. Lệch → pending (+ cam 3 sau này).

Mock-up phải ra **cùng** chuỗi sự kiện — không được thay bằng nút “chụp thử” trong mill.

---

## Máy đo củ mì RS232

Nối máy tính sample, ghi hex+ASCII. Thử 9600 8N1 → 19200 → 4800. Chốt: spew hay bấm Send, dấu thập phân, tần số. Mill khóa ô điểm — không nhập tay.

---

## Cloudflare (cổng)

Repo **gốc** là repo này. Không dùng bản copy `bm-can-xe` (bot import).

1. dash.cloudflare.com → Worker **bm-can-xe**  
2. Custom domain `canxe.redtigerhead.com` (Proxied CNAME)  
3. Secret `STATION_KEY`  
4. Git webhook đang không tự build — upload `public/index.html` khi cần bản live  

Mã thử: `BinhMinh-CanXe` — đổi trước phát hành.

`main` = cổng. Mill đầy đủ trên `checkpoint/v5-brand`. Whitepaper triển khai: luôn đọc trước khi mua/cắm thiết bị.
