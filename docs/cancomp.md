# CANcomp — máy tính cân độc lập

Quyết 15/09/2026: **không** cài agent lên máy sổ cũ. Một PC riêng (`CANcomp`) nghe dữ liệu, lọc nhiễu, lưu local, đồng bộ lên `canxe.redtigerhead.com`.

```
Kingbird COM2 (DB25 cái)
    ── DTECH 1→2 ── OUTPUT1 → màn phụ (dây cũ)
                     └─ OUTPUT2 → USB-RS232 → CANcomp  (chỉ nghe)

Máy bột DB9 cái ── USB-RS232 ── CANcomp

Cam trước / cam sau (± cam 3) ── LAN ── CANcomp
    snapshot CGI/ONVIF + bật/đèn trước khi chụp

CANcomp  SQLite + hàng đợi
    ── HTTPS + STATION_KEY ── canxe.redtigerhead.com
                                    └─ mill / BM Cân Xe
                                    └─ (sau) binhminh_data
```

Sổ cũ giữ nguyên. BM Bridge = lớp đồng bộ + chất lượng ảnh; có thể chạy **trong** process CANcomp lúc đầu (không tách service).

## Việc CANcomp làm offline

1. Đọc COM USB Kingbird + COM USB máy bột.
2. Lọc **cao nguyên ổn định** (cửa 2 s, bỏ người/chó, một số / lượt).
3. Ghi SQLite ngay (sống khi mất mạng).
4. Khi kg ổn: đèn ON → chụp F+R → đèn OFF → lưu JPEG xám.
5. Sync hàng đợi lên canxe (HTTPS). Mất mạng thì gửi lại.

OCR: **pha 1 forward ảnh lên canxe** (mill đã có). Pha 2 mới OCR local nếu mất mạng dài — không làm hai nơi cùng lúc.

## Camera + đèn

Cùng LAN với CANcomp. Địa chỉ tĩnh.

| Lệnh | Cách |
|---|---|
| Chụp | ONVIF `GetSnapshotURI` hoặc CGI `/cgi-bin/snapshot.cgi` |
| Đèn trên cam | CGI LED / ONVIF Auxiliary / relay sẵn |
| Đèn pha rời | USB-relay hoặc GPIO — cùng chuỗi ON→chụp→OFF |

Chưa biết model cam: ghi vào `docs/hardware-spec.md` khi có tem. Driver để `snapshot(lane)` + `setLight(on)`.

## Sync

Chỉ **một** đường lên mây: `POST https://canxe.redtigerhead.com/api/ingest` + header `X-Station-Key`.
Không MQTT song song. Không ghi PostgreSQL từ CANcomp.

Payload tối thiểu: `{ source, kg|starchPct, stable, ts, raw, shotF?, shotR? }`.

## Máy CANcomp

Mini-PC Windows 10/11, Ethernet + USB 3, không tắt nguồn. Hai FTDI. Cùng switch với camera.
