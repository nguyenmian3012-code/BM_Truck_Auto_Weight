# Hàn cáp CANcomp — 22/09/2026

Hàng có: HP EliteDesk `192.168.30.98` S/N MXL0530KMH = **CANcomp**. DTECH 5V + 2 dây OUTPUT. Đầu sẵn là DB25 **cái** → DB9 **đực** — **không** cắm được Kingbird COM2 (Çũng là cái).

## Hai dây cần hàn

### Dây 1 — DB9 đực – DB9 đực (thẳng 3 sợi)

Dùng: nối hai ổ **cái** (ví dụ OUTPUT DTECH — nếu đầu dây là cái — với đầu cái khác). Cáp USB-RS232 FTDI thường là **đực** → không cần dây này nếu OUTPUT DTECH đã là **cái**.

Hàn **thẳng**, chỉ 3 chân (không nối 9 chân):

| Tín hiệu | Đầu A đực | Đầu B đực | Màu gợi ý |
|---|---|---|---|
| GND | chân 5 | chân 5 | đen |
| TX→RX đường DTE | chân 3 | chân 2 | vàng |
| RX←TX | chân 2 | chân 3 | cam |

Nếu CoolTerm im: đổi chéo 2↔2 và 3↔3 (thẳng thay vì null). Vẫn **không** hàn chân 1,4,6,7,8,9.

Nhìn đầu đực (kim chỏa ra), ốc ở hai bên:

```
5 4 3 2 1
  9 8 7 6
```

Chân 1 = góc trên bên phải.

### Dây 2 — DB9 cái → 2 sợi hở TX + GND (chỉ nghe)

Dùng khi muốn nghe một đầu **đực** mà không để CANcomp nói. Cắm đầu cái vào đầu đực nguồn; 2 sợi kia vào USB-RS232.

| Sợi | DB9 cái | Vào USB-RS232 (FTDI đực, nhìn kim) |
|---|---|---|
| GND đen | chân 5 | chân 5 |
| TX nguồn (nghe) | chân **2** trước | chân **2** (RX của USB) |
| — | không hàn chân 3 | chân 3 USB **cắt**, quấn băng |

Nhìn đầu **cái** (ổ lỗ):

```
1 2 3 4 5
  6 7 8 9
```

Im lặng: chuyển sợi TX từ chân 2 sang chân **3** của đầu cái (một số nguồn đảo). Không bao giờ nối chân 3 USB.

DTECH đang dùng: **không cần** dây 2. OUTPUT2 → FTDI là đủ. Dây 2 chỉ là phương án dự phòng / nghe thêm.

## Đường đúng với đồ đang có

```
Kingbird COM2 (DB25 cái)
    → cần DB25 ĐỰC → DB9 ĐỰC → INPUT DTECH (cái)
DTECH OUTPUT1 → dây màn MAN
DTECH OUTPUT2 → FTDI → USB CANcomp (192.168.30.98)
DTECH Power 5V — đã cắm
```

Thiếu: đầu **DB25 đực** (mua hoặc hàn). Đầu DB25 cái sẵn trên bàn không cắm vào Kingbird.
