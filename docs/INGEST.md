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
