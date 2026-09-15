# Vật tư + việc 2 và 3

Việc 3 (máy bột) **không cần** cáp chia cầu cân. Làm 3 trước nếu 2 kẹt.

## Mua ngay (~700–900 nghìn)

| # | Món | Số | Ghi chú mua | Giá tham khảo |
|---|---|---|---|---|
| 1 | Cáp **USB → RS232 chip FTDI** (Z-Tek ZE533A hoặc tương đương FT232) | **2** | Một cắm máy bột, một cắm đầu cân. **Không** mua dây hồng CH340 nếu có FTDI | ~300–350k/ợi |
| 2 | Cáp RS232 **DB9 đực – DB9 cái**, bọc, 1,5–2 m | 1–2 | Nối dài nếu máy tính sample xa | ~50–80k |
| 3 | Đầu chuyển **DB25 cái → DB9 đực** | 1 | Kingbird COM thường 25 chân; USB-RS232 là 9 chân | ~40–70k |
| 4 | Đầu hàn DB9 đực + DB9 cái + vỏ ốp kim loại | 2 bộ | Chỉ khi phải **tự hàn tap** việc 2 | ~80–120k |

Phần mềm (miễn phí): **CoolTerm** hoặc RealTerm. Bật ghi file + hiện ASCII và Hex.

**Không mua:** cáp Y DB9 “1 đực 2 cái” nối thẳng cả 9 chân — hai máy cùng TX làm sổ cũ loạn.

---

## Việc 3 — máy đo củ mì (làm trước khi 2 kẹt)

Máy đã có RS232. Nếu cổng đó **chưa** cắm máy khác: cắm thẳng USB-RS232, không cần chia.

1. Laptop / PC sample, cài CoolTerm + driver FTDI.
2. Cắm cáp vào máy bột. Windows Device Manager phải thấy COMx (ví dụ COM3).
3. CoolTerm: chọn đúng COM, **9600, 8 bit, None, 1 stop**, Connection → Open. Bật hiện Hex + ghi file log.
4. Đo một mẫu thật (hoặc bấm Print/Send trên máy bột).
5. Thấy số % đọc được → giữ file. Rác / không ra gì → đổi baud: 19200 → 4800 → 2400 → 115200; rồi 9600 **7E1**.
6. Làm đủ **20 phiếu**, mỗi phiếu ghi tay: giờ, % trên màn máy bột, dòng log.
7. Nộp file vào `docs/logs/` + comment issue #4.

Hỏi trên file: spew liên tục hay chỉ khi bấm; dấu `.` hay `,`; 28.4 hay 284?

---

## Việc 2 — Kingbird (nếu kẹt cáp chia)

Làm **theo thứ tự**, cái nào xong trước dùng cái đó.

### 2A — Không cần mua thêm (thử trước)

Mở phần mềm sổ cũ trên máy tính đang nối COM2. Vào Cài đặt / Cổng COM / Baud. **Chụp màn hình** gửi issue #3. Biết baud thì việc 2 nhẹ hơn nhiều.

### 2B — Tap COM1 (màn Sangjin), không đụng COM2

COM1 đang cáp *Shield Control* → màn phụ thường **chỉ nghe** kg. Có thể chạm song song:

```
Kingbird COM1 TX ──┬── RX màn Sangjin
                   └── RX USB-RS232 mill
GND chung. Mill không nối TX.
```

Sổ cũ trên COM2 không đổi.

### 2C — Tap COM2 (nếu 2B không ra số)

Cùng kiểu: TX đầu cân → RX máy cũ **và** RX mill. Mill không nối TX.

Hàn 3 sợi: TX, GND (± shield). Không nối chân TX của hai máy với nhau.

### 2D — Log

CoolTerm, thử **1200 8N1** (Kingbird hay gặp) → 9600 8N1 → 9600 7E1. Xe lên bàn ≥ 30 phút hoặc ≥ 10 lượt. File `docs/logs/YYYY-MM-DD-kingbird-COM-baud.txt`.

---

## Block việc 2 — vẫn làm được

| Block | Làm ngay |
|---|---|
| Chưa có cáp chia / sợ tách COM2 | Việc **3** + bước **2A** (chụp cài đặt sổ cũ) |
| Sổ cũ không cho đụng dây ban ngày | Log đêm / cuối ca; hoặc chỉ tap COM1 |
| Không biết DB25 hay DB9 | Chụp đầu cáp khi rút (đếm lỗ 9 hay 25) gửi issue #3 |
