# Mở POST /api/ingest

Route đã nằm trong `worker/index.js`. Chưa live vì máy này không đăng nhập Cloudflare.

Phiếu là phiếu đơn. Không ghép Vào với Ra. Chưa có biển thì chưa có phiên.

## Lệnh, chạy trên máy đã `wrangler login`

```
npx wrangler d1 create bm-can-xe
```

Gắn `database_id` vừa in vào `wrangler.jsonc`:

```
"d1_databases": [
  { "binding": "TICKETS", "database_name": "bm-can-xe", "database_id": "<id>" }
]
```

```
npx wrangler d1 execute bm-can-xe --remote --file worker/schema.sql
npx wrangler deploy
```

Secret `STATION_KEY` đã có trên worker `bm-can-xe`. Không commit khóa.

Khi route trả 200, app CANcomp tự đẩy hàng đợi. Không bật khóa production trước khi đối 20 lượt sạch.

## Ảnh ghép

`POST /api/ingest` nhận thêm, không bắt buộc:

- `shot`: JPEG base64, tối đa 1 MB sau khi giải. Không gửi thì phiếu vẫn là phiếu cân như cũ.
- `shotName`: tên file, ví dụ `261029-1219-thu.jpg`.

Ảnh vào bucket R2 `bm-can-xe-shots`, khóa `shots/{id}.jpg`. Xem lại bằng `GET /api/shot?id={id}`.

Một lần, trên máy đã `wrangler login`:

```
npx wrangler r2 bucket create bm-can-xe-shots
npx wrangler deploy
```

Cột `shot_key` và `shot_name` được thêm lúc request đầu. OCR chưa chạy ở route này. Desktop hiện chưa gửi trường `shot`.

