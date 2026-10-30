# Mở POST /api/ingest

Route đã nằm trong `worker/index.js`.

Phiếu là phiếu đơn. Không ghép Vào với Ra. Chưa có biển thì chưa có phiên.

## Máy nào được đụng Cloudflare

Chỉ máy đã `wrangler login` (MinhComp), một lần khi đưa bản mới lên. CANcomp không đăng nhập Cloudflare, không chạy `wrangler`, không tạo bucket. CANcomp chạy app desktop, đọc biển bằng Python local, giữ `X-Station-Key`, và POST JSON tới `https://canxe.redtigerhead.com/api/ingest`.

```
npx wrangler d1 execute bm-can-xe --remote --file worker/schema.sql
npx wrangler deploy
```

Secret `STATION_KEY` nằm trên worker `bm-can-xe`. Không commit khóa. `XAI_API_KEY` chỉ khi bật `OCR_ENGINE=xai` sau này.

Cột ảnh, OCR và sân được thêm lúc request đầu nếu bảng cũ chưa có. File `worker/migrate-shot.sql`, `worker/migrate-ocr.sql` và `worker/migrate-yard.sql` là cùng các lệnh ALTER đó.

Khi route trả 200, app CANcomp tự đẩy hàng đợi. Không bật khóa production trước khi đối 20 lượt sạch.

## Ảnh ghép

`POST /api/ingest` nhận thêm, không bắt buộc:

- `shot`: JPEG base64, tối đa 1 MB sau khi giải. Không gửi thì phiếu vẫn là phiếu cân như cũ.
- `shotName`: tên file, ví dụ `261029-1219-thu.jpg`.

Ảnh vào bucket R2 `bm-can-xe-shots`, khóa `shots/{id}.jpg`. Xem lại bằng `GET /api/shot?id={id}`.

Kho ảnh có trần riêng của nhà máy: **3 GB**. Ảnh nào **quá 60 ngày** cũng bị xóa. Một trong hai điều kiện tới trước thì xóa ảnh cũ nhất trước. Phiếu cân (số kg, giờ, biển) không bị xóa theo ảnh. Xóa ảnh không làm phiếu kg mất.

Miễn phí R2 của Cloudflare là khoảng 10 GB cho cả tài khoản, không phải 10 GB cho từng tên miền. Trần 3 GB nằm trong phần miễn phí đó. Bật R2 một lần trong trang Cloudflare (cần thẻ). Sau đó máy lập trình bấm đúp `Day-len-web.bat`. Máy cân không đụng Cloudflare.

Nếu kho ảnh lỗi lúc gửi, phiếu kg vẫn được lưu, ảnh để trống, lần sau gửi lại.

## OCR và sân nhà máy

Ảnh ghép vẫn nằm trên CANcomp, thư mục `shots/`, tối đa 1 MB, giữ 60 ngày tại máy, và được gửi kèm phiếu. Ba ảnh gốc (đúng độ phân giải camera) nằm trong `packs/{id}/`, máy cân tự xóa sau 7 ngày. Ảnh gốc không lên mạng.

Biển đọc trên CANcomp, không đọc trên worker và không đọc trên MinhComp cho lượt đang cân.

Ngân sách 10 giây kể từ lúc xe đứng yên:

1. 0–3 giây: cao nguyên. Đèn bật khi cân đã vượt đỉnh, không đợi hết 3 giây.
2. Ngay sau đó: ba camera chụp một lần. Ảnh ghép và ảnh gốc ra cùng lúc.
3. YOLOv8n (640) tìm khung biển trên ảnh gốc, PaddleOCR chỉ đọc phần biển. Thời gian OCR local khoảng 3 giây.
4. Đối chiếu sổ luồng tại máy. Sổ không lớn theo từng lượt cân.
5. POST một JSON kèm ảnh ghép ≤ 1 MB: biển, biển remooc nếu có, kg, giờ, quen/lạ, thẻ, tên khách nếu có trong sổ.

Chưa đọc được biển thì phiếu vẫn lên, cột biển trống, trạng thái chờ. Đó không phải xe lạ. Xe lạ là biển đã đọc và không có trong sổ: thẻ Khác, không có tên, vẫn vào sân. Lượt đầu là vào. Lượt sau cùng biển là ra và rời sân. Nút Vào/Ra cũ của phiếu cân không bị gộp thành phiên.

Worker không chạy YOLO. `OCR_ENGINE=xai` vẫn tắt. Không cần `XAI_API_KEY`.

Trang `/` là bản V5. Mục “Xe đang trong nhà máy” là ba thẻ sống Nhập mì, Xuất bột, Khác, lấy từ `GET /api/yard`. Ngoại lệ, phiên đã đóng, Camera, Thử mẫu, Sổ ngày giữ nguyên. Phiếu ngày ở `/phieu`.

## Đưa bản này lên web

MinhComp, một lần, sau khi đã bật R2 trên Cloudflare:

Bấm đúp `Day-len-web.bat`. File tự kéo bản mới, tạo kho `bm-can-xe-shots` nếu chưa có, rồi deploy. Không gõ lệnh.

CANcomp giữ bản **0.17.1**. Không cài 0.17.2, bản đó tắt gửi ảnh.

Ảnh của xe cân sau khi web đã nhận ảnh: 0.17.1 tự gửi, không cần máy lập trình.

Ảnh của xe đã cân trong ngày mà web lúc đó bỏ ảnh: chép cả `Gui-lai-anh-hom-nay.bat` và `gui-lai-anh.py` sang máy cân, để BM Auto Cân đang mở, bấm đúp file bat một lần. Phần mềm tự gửi lại ảnh còn trong thư mục `shots`.

`STATION_KEY` đã có trong appsettings của CANcomp. Không ghi vào git. CANcomp không chạy `wrangler`.
