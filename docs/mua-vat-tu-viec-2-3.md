# Vật tư + việc 2 và 3

Việc 3 (máy bột) **không cần** cáp chia cầu cân. Làm 3 trước nếu 2 kẹt.

## Đầu DB25 không phải là nhánh nghe

- **Đầu chuyển DB25 → DB9** chỉ đổi *hình giắc* (25 lỗ thành 9 lỗ). Không tạo thêm nhánh.
- **Nhánh nghe** là mối chữ **T** trên 2 sợi: chân **TX** (Kingbird nói) và chân **GND**. Nhánh thứ ba đi vào chân **RX** của USB-RS232. Chân TX của USB-RS232 **cắt, không nối**.

Kingbird đã chia sẵn 2 cổng vật lý (màn + máy cũ). Ta không cần “cổng thứ 3 trên thân máy” — chỉ cần T trên **một** trong hai dây đó.

---

## Chưa biết COM1 / COM2 gắn gì

Đừng rút dây lúc xe lên bàn. Làm 5 phút cuối ca:

1. Theo dây từ Kingbird: sợi Sangjin *Control* → màn phụ; sợi còn lại → máy tính sổ cũ.
2. Dán nhãn lên hai đầu: `MAN` và `SO_CU`.
3. Đếm lỗ giắc (9 hay 25), chụp ảnh gửi issue #3.

Ưu tiên **T vào nhánh MAN** (màn phụ). Màn chỉ nghe, sổ cũ không đụng. Nếu CoolTerm không ra số kg → màn không đi kèm ASCII; lúc đó mới T nhánh `SO_CU`.

---

## Đấu chỉ nghe (không ghi)

RS-232 chuẩn (Kingbird kiểu máy tính):

| Tín hiệu | DB25 | DB9 (phía máy tính / USB-RS232) |
|---|---|---|
| TX — Kingbird **nói** | chân 2 | chân 3 |
| RX — Kingbird **nghe** | chân 3 | chân 2 |
| GND | chân 7 | chân 5 |

Nếu CoolTerm im lặng: đổi chéo TX/RX (một số đầu cân đảo 2 và 3). Vẫn **không** nối TX của USB vào dây.

```
        Kingbird COM (màn hoặc sổ cũ)
                 |
            [nối thẳng 25 chân]
                 |
        ┌── T chỉ 2 sợi ────────────┐
        |                        |
   đường cũ giữ nguyên      nhánh nghe
   (màn hoặc PC sổ cũ)      USB-RS232 FTDI
                               RX ← TX Kingbird
                               GND ← GND
                               TX  cắt / băng keo
```

Cách an toàn nhất: hộp **DB25 đực–cái đi thẳng** (ắn xen giữa đầu cân và dây cũ) + 2 sợi hàn ra chân 2 và 7 tới USB-RS232. Dây cũ vẫn cắm như cũ qua hộp.

---

## Tín hiệu có yếu / nhiễu không?

RS-232 là điện áp ±5…±12 V; đầu thu RX trở khá cao. **Hai** đầu thu (màn + mill, hoặc PC + mill) trên một TX thường **không** làm kg sai — đây là cách nghe công nghiệp hay dùng.

Có thể yếu / nhiễu khi:

- nhánh nghe dài > 3 m, không bọc;
- chạy sát cáp động cơ / biến tần;
- nối nhầm hai TX (Y 9 chân thẳng);
- thiếu GND chung.

Giữ nhánh nghe **ngắn** (dưới 2 m), cáp bọc, GND chắc. Baud 1200 càng dễ sống hơn 9600. Nếu sau này log rác khi xe đềng cơ: mua hộp tap cô lập (Advantech / Moxa) — không cần lúc đầu.

**Không** làm kg trên sổ cũ đổi, nếu chỉ song song RX và không nối TX mill.

---

## Mua ngay (~700–900 nghìn)

| # | Món | Số | Ghi chú |
|---|---|---|---|
| 1 | USB → RS232 **FTDI** (ZE533A / FT232) | 2 | Một bột, một cân. Tránh CH340 |
| 2 | Cáp DB9 đực–cái bọc 1,5–2 m | 1–2 | Nhánh nghe ngắn |
| 3 | Đầu DB25 → DB9 | 1 | Đổi giắc, chưa phải T |
| 4 | Hộp DB25 đực–cái đi thẳng **hoặc** 2 đầu hàn DB25 + vỏ | 1 | Xen vào dây, hàn TX+GND ra |

Không mua Y 9 chân nối cả 9 sợi.

Phần mềm: CoolTerm, bật Hex + ghi file.

---

## Việc 3 — máy bột (làm khi 2 kẹt)

Cắm thẳng USB-RS232 nếu cổng trống. CoolTerm 9600 8N1 → 20 phiếu → issue #4.

## Việc 2 — thứ tự

1. Chụp baud phần mềm sổ cũ (2A).
2. Dán nhãn MAN / SO_CU.
3. T nhánh MAN, CoolTerm 1200 8N1 rồi 9600.
4. Không ra số → T nhánh SO_CU, vẫn chỉ TX+GND.
