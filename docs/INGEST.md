# Mở POST /api/ingest

Route đã nằm trong `worker/index.js`.

Phiếu là phiếu đơn. Không ghép Vào với Ra. Chưa có biển thì chưa có phiên.

## Máy nào được đụng Cloudflare

Chỉ máy đã `wrangler login` (MinhComp), một lần khi đưa bản mới lên. CANcomp không đăng nhập Cloudflare, không chạy `wrangler`, không tạo bucket. CANcomp chỉ chạy app desktop, giữ `X-Station-Key`, và POST tới `https://canxe.redtigerhead.com/api/ingest`.

```
npx wrangler d1 execute bm-can-xe --remote --file worker/schema.sql
npx wrangler r2 bucket create bm-can-xe-shots
npx wrangler deploy
```

Secret `STATION_KEY` nằm trên worker `bm-can-xe`. Không commit khóa. `XAI_API_KEY` chỉ khi bật `OCR_ENGINE=xai` sau này.

Cột ảnh và OCR được thêm lúc request đầu nếu bảng cũ chưa có. File `worker/migrate-shot.sql` và `worker/migrate-ocr.sql` là cùng các lệnh ALTER đó.

Khi route trả 200, app CANcomp tự đẩy hàng đợi. Không bật khóa production trước khi đối 20 lượt sạch.

## Ảnh ghép

`POST /api/ingest` nhận thêm, không bắt buộc:

- `shot`: JPEG base64, tối đa 1 MB sau khi giải. Không gửi thì phiếu vẫn là phiếu cân như cũ.
- `shotName`: tên file, ví dụ `261029-1219-thu.jpg`.

Ảnh vào bucket R2 `bm-can-xe-shots`, khóa `shots/{id}.jpg`. Xem lại bằng `GET /api/shot?id={id}`.

## OCR

Đường mặc định không gọi model AI.

1. YOLOv8 tìm khung biển trên từng lớp F, R, S, rồi tìm khung chữ trong biển đó.
2. PaddleOCR đọc từng hàng chữ và ghép thành biển. Khớp dạng Việt Nam và độ tin ≥ 0.8 mới ghi `ok`. Lệch giữa hai lớp, hoặc không đủ tin, thì `unread` và biển để trống.

Worker không chạy được YOLO. MinhComp chạy vòng lặp, CANcomp không chạy.

```
pip install -r ocr/requirements.txt
```

Đặt trọng số đã train biển Việt Nam tại `ocr/models/plate.pt` và `ocr/models/char.pt` (không commit). Rồi:

```
STATION_KEY=... python -m ocr --sync
```

Lệnh đó lấy `GET /api/ocr-queue`, tải ảnh, đọc, và `POST /api/ocr` để ghi biển. Desktop vẫn hỏi `GET /api/ocr?id=...`.

Một file để thử: `python -m ocr anh.jpg`.

`OCR_ENGINE=xai` trên worker là đường model AI để sau này, khi nguồn mở đã có số liệu. Chưa bật thì không cần `XAI_API_KEY`. Không làm rớt số kg vì OCR.