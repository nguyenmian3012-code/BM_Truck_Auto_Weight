# Mở POST /api/ingest

Route đã nằm trong `worker/index.js`.

Phiếu là phiếu đơn. Không ghép Vào với Ra. Chưa có biển thì chưa có phiên.

## Máy nào được đụng Cloudflare

Chỉ máy đã `wrangler login` (MinhComp), một lần khi đưa bản mới lên. CANcomp không đăng nhập Cloudflare, không chạy `wrangler`, không tạo bucket. CANcomp chỉ chạy app desktop, giữ `X-Station-Key`, và POST tới `https://canxe.redtigerhead.com/api/ingest`.

```
npx wrangler d1 execute bm-can-xe --remote --file worker/schema.sql
npx wrangler r2 bucket create bm-can-xe-shots
npx wrangler secret put XAI_API_KEY
npx wrangler deploy
```

Secret `STATION_KEY` và `XAI_API_KEY` đã (hoặc sẽ) nằm trên worker `bm-can-xe`. Không commit khóa.

Cột ảnh và OCR được thêm lúc request đầu nếu bảng cũ chưa có. File `worker/migrate-shot.sql` và `worker/migrate-ocr.sql` là cùng các lệnh ALTER đó.

Khi route trả 200, app CANcomp tự đẩy hàng đợi. Không bật khóa production trước khi đối 20 lượt sạch.

## Ảnh ghép

`POST /api/ingest` nhận thêm, không bắt buộc:

- `shot`: JPEG base64, tối đa 1 MB sau khi giải. Không gửi thì phiếu vẫn là phiếu cân như cũ.
- `shotName`: tên file, ví dụ `261029-1219-thu.jpg`.

Ảnh vào bucket R2 `bm-can-xe-shots`, khóa `shots/{id}.jpg`. Xem lại bằng `GET /api/shot?id={id}`.

## OCR

Có ảnh thì worker gọi lớp `ocr/read-plate.js` sau khi đã lưu phiếu. Model `grok-4.7` đọc riêng ba lớp CAN_F, CAN_R, CAN_S. Biển chỉ được chốt khi khớp dạng Việt Nam và độ tin ≥ 0.8. Không khóa, lỗi mạng, hoặc JSON hỏng thì `ocrStatus` là `pending` và biển để trống. Đọc xong mà không đủ tin thì `unread`, vẫn không bịa biển.

Desktop gửi ảnh cùng phiếu, rồi hỏi `GET /api/ocr?id={id}` với header `X-Station-Key` cho đến khi ra `ok` hoặc `unread`.

Không có khóa xAI thì cân vẫn vào. Không làm rớt số kg vì OCR.