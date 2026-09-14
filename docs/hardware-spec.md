# Task 1 — Spec đầu cân hiện có

Điền từ ảnh 14/09/2026 (nhà cân Bình Minh). Baud **chưa** đo — Task 2.

| Trường | Giá trị |
|---|---|
| Hãng | Mettler Toledo · Kingbird (Changzhou) |
| Model | KINGBIRD |
| Fact no | KTGN-T100-078 |
| Serial | B231161076 |
| Nguồn | 220 VAC / 50 Hz |
| Kiểm định | Tem niêm VN N240 (2640, 2282); tem mặt 01853 N385 hạn 01-27 |
| Cổng | **COM1** RS232 · **COM2** RS232 · **LOAD CELL** (không đụng) |
| Ổ | D-sub có chao (Kingbird cổ: COM1 thường **25 chân**) |
| Đơn vị mặt | kg (G / Net / Pcs / Dyn) |
| Ổn định mặt | Mũi tên dưới số — tắt khi đứng |
| Nút | Zero Tare Clear Total Mode **Enter/Print** |
| Baud trên tem | **Không in** — phải sniff |
| Frame dự kiến | ASCII; thử **1200 8N1** rồi **9600 8N1**, **9600 7E1** (Kingbird hay 1200 mặc định) |
| Spew | Menu F3: 0 liên tục / 1 lệnh / 2 SICS — **chưa biết máy này đang chế độ nào** |

Cáp đang cắm:

| Cổng | Cáp | Đoán |
|---|---|---|
| COM1 | Sangjin *Shield Control Cable* | Màn phụ / điều khiển — **không cắt** |
| COM2 | D-sub đang có máy tính / in | Nhánh sổ cũ — **đây là chỗ tap** |
| LOAD CELL | Sensor | Không chia |

## Chia nhánh — nghe, không nói

Không dùng Y-cable rẻ (nối chung TX hai máy → đụng sổ cũ).

Chỉ **tap TX** của đầu cân:

```
Đầu cân TX  ──┬── RX máy tính cũ (sổ cũ giữ nguyên)
              └── RX USB-RS232 máy mill (chỉ nghe)
Đầu cân RX  ──── TX máy tính cũ
Mill TX          không nối
GND         ──┬── cả hai máy
```

Mua: USB-RS232 FTDI + **cáp monitor/tap RS232** (hoặc hộp 1 TX → 2 RX).  
Tháng song song: sổ cũ vẫn nhận kg như hôm nay.

Xong Task 1. Task 2: log COM2 đã tap, 30 phút xe thật.
