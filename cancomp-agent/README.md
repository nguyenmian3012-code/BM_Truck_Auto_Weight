# BM CANcomp — agent Windows

Phần mềm cài trên máy **CANcomp** (HP EliteDesk 192.168.30.98).
Không cài lên máy sổ cũ.

## Việc nó làm

1. Nghe 2 cổng RS232 (listen-only, không ghi byte lên đầu cân).
2. Bỏ số 0 / idle / rác vệ sinh / người đứng bàn.
3. Lấy **một** giá trị cao nguyên ổn định ≥ 2 giây (`max − min < ε`).
4. Ghi SQLite local (`C:\ProgramData\BmCancomp\data\cancomp.db`) — sống khi mất mạng.
5. `POST https://canxe.redtigerhead.com/api/ingest` + header `X-Station-Key`.
6. Cài đặt khóa PIN admin (mặc định `2580`).

## Cổng mặc định

| Nguồn | Khung | Baud |
|---|---|---|
| Kingbird COM2 → DTECH OUTPUT2 → FTDI | ASCII kg | 1200 8N1 rồi 9600 |
| Máy bột Prolific PL2303 | `NNNNNN=` idle `000000=` | 1200 8N1, DTR/RTS tắt |

Lần trước COM5 để 7N1 + RTS/DTR On + software flow → phải trả 8N1, flow tắt.

## Cài

```bat
winget install Microsoft.DotNet.SDK.8
cd cancomp-agent
dotnet restore
dotnet publish -c Release -r win-x64 --self-contained false -o C:\BmCancomp
```

Chạy `C:\BmCancomp\BmCancomp.exe`.

PIN admin mặc định `2580`. Dán STATION_KEY trong Admin. Không commit secret.
Không ghi binhminh_data từ agent.
