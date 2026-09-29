# Agent CANcomp (WinForms .NET 8)

Mã: `cancomp-agent/` trên nhánh `app/cancomp-agent`.
Cài trên HP EliteDesk 192.168.30.98. Không cài sổ cũ.

## Luồng

```
Kingbird COM2 → DTECH OUT2 → FTDI COM?
Máy bột PL2303 1200 8N1 khung NNNNNN=  → COM?
        ↓
  BmCancomp.exe  lọc cao nguyên 2s
        ↓
  SQLite C:\ProgramData\BmCancomp\data\cancomp.db
        ↓
  POST /api/ingest  X-Station-Key
        ↓
  canxe.redtigerhead.com
```

Payload: `{ source, kg|starchPct, stable, ts, raw, stationId, id }`.
Không MQTT. Không ghi binhminh_data.

## Lọc

- Bỏ 0 / idle `000000=` / OL / ERR / ngoài dải
- Bỏ người/chó: kg < 400
- Ổn khi max−min < 20 kg (hoặc 0,2 %) trong 2,0 s
- Một số / lượt; reset khi về sàn

## Bảo mật

PIN admin mặc định `2580`. STATION_KEY chỉ nhập trong Admin.
Listen-only: DTR/RTS off, handshake None.

## Deploy ingest worker

Thay `export default` trong `worker/index.js` bằng handler nhận POST `/api/ingest` (xem cuối file trên nhánh này khi đã merge). Secret `STATION_KEY` đã có trên Worker `bm-can-xe`.
