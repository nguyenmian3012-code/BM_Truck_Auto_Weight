# Mở POST /api/ingest

Route đã nằm trong `worker/index.js`.

Phiếu là phiếu đơn. Không ghép Vào với Ra. Chưa có biển thì chưa có phiên.

## Máy nào được đụng Cloudflare

Chỉ máy đã `wrangler login` (MinhComp), một lần khi đưa bản mới lên. CANcomp không đăng nhập Cloudflare, không chạy `wrangler`, không tạo bucket. CANcomp chạy app desktop, đọc biển bằng Python local, giữ `X-Station-Key`, và POST JSON tới `https://canxe.redtigerhead.com/api/ingest`.

```
npx wrangler d1 execute bm-can-xe --remote --file worker/schema.sql
npx wrangler r2 bucket create bm-can-xe-shots
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

## OCR và sân nhà máy

Ảnh ghép trong `shots/` vẫn đi kèm phiếu, tối đa 1 MB, giữ 60 ngày. Đường đó không đổi.

Biển đọc trên CANcomp, không đọc trên worker và không đọc trên MinhComp cho lượt đang cân. Ba ảnh gốc (đúng độ phân giải camera) nằm trong `packs/{id}/`, máy cân tự xóa sau 7 ngày. Ảnh gốc không lên mạng.

Ngân sách 10 giây kể từ lúc xe đứng yên:

1. 0–3 giây: cao nguyên. Đèn bật khi cân đã vượt đỉnh, không đợi hết 3 giây.
2. Ngay sau đó: ba camera chụp một lần. Ảnh ghép và ảnh gốc ra cùng lúc.
3. YOLOv8n (640) tìm khung biển trên ảnh gốc, PaddleOCR chỉ đọc phần biển. Thời gian OCR local khoảng 3 giây.
4. Đối chiếu sổ luồng tại máy. Sổ không lớn theo từng lượt cân.
5. POST một JSON nhỏ: biển, biển remooc nếu có, kg, giờ, quen/lạ, thẻ, tên khách nếu có trong sổ.

Chưa đọc được biển thì phiếu vẫn lên, cột biển trống, trạng thái chờ. Đó không phải xe lạ. Xe lạ là biển đã đọc và không có trong sổ: thẻ Khác, không có tên, vẫn vào sân. Lượt đầu là vào. Lượt sau cùng biển là ra và rời sân. Nút Vào/Ra cũ của phiếu cân không bị gộp thành phiên.

Worker không chạy YOLO. `OCR_ENGINE=xai` vẫn tắt. Không cần `XAI_API_KEY`.

Trang `/` là ba thẻ Nhập mì, Xuất bột, Khác. Trang thử cũ ở `/demo`. Phiếu ngày ở `/phieu`.

## Sáng mai

MinhComp, một lần:

```
npx wrangler d1 execute bm-can-xe --remote --file worker/schema.sql
npx wrangler r2 bucket create bm-can-xe-shots
npx wrangler deploy
```

`schema.sql` trên bảng đã có sẽ báo cột trùng. Khi đó dùng `worker/migrate-yard.sql` cho cột còn thiếu, hoặc để request đầu tự ALTER. Bucket đã có thì bỏ lệnh tạo bucket.

CANcomp:

```
pip install -r ocr/requirements.txt
```

Đặt `ocr/models/plate.pt` và `ocr/models/char.pt` cạnh app (không commit). Mở BM Auto Cân. App tự gọi `python -m ocr --serve` nếu cổng 8765 còn trống. Process phải đứng sẵn trước xe đầu tiên, nếu không lần nạp model trễ quá 10 giây và biển để trống.

Mở Sổ luồng (PIN), nhập biển quen, tên khách hoặc nhà cung cấp, và thẻ. Sổ trống thì mọi biển đọc được đều là xe lạ.

`STATION_KEY` đã có trong appsettings của CANcomp. Không ghi vào git. CANcomp không chạy `wrangler`.

Chưa có hai file `.pt` thì số kg và ảnh ghép vẫn lên. Biển chưa đọc được.