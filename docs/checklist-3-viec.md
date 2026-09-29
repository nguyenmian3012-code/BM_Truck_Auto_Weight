# Checklist 3 việc chính — CANcomp

In ra, đánh ✓ từng dòng. Việc B (máy bột) làm song song khi A kẹt dây DTECH.

---

## Việc A — Kingbird → DTECH → màn + CANcomp

Mục tiêu: CANcomp **nghe** kg, màn phụ và sổ cũ không chết.

### A0. Mua / chuẩn đồ

- [ ] DTECH RS232 1→2 (DT-5047) hoặc 1→4 (DT-5044) + adapter DC 5V
- [ ] Cáp **DB25 đực → DB9 đực** (COM2 Kingbird là DB25 **cái**; INPUT DTECH là DB9 **cái**)
- [ ] Cáp DB9 đực–cái bọc nếu OUTPUT DTECH không khớp dây màn (màn có thể cần DB9→DB25)
- [ ] 1 cáp USB→RS232 **FTDI** (ZE533A / FT232) — nhánh CANcomp
- [ ] Mini-PC **CANcomp** Win10/11, Ethernet, không tắt nguồn
- [ ] CoolTerm (hoặc RealTerm) + driver FTDI

### A1. Dán nhãn hiện trường (5 phút, không rút lúc xe lên bàn)

- [ ] Theo dây từ Kingbird: dán `MAN` lên nhánh màn phụ = **COM2 DB25 cái**
- [ ] Dán `SO_CU` lên nhánh máy sổ cũ — **không rút** dây này
- [ ] Chụp 3 ảnh: mặt Kingbird, 2 giắc đã dán, tem KTGN-T100-078 — comment issue #3

### A2. Lấy baud từ sổ cũ (không cần DTECH)

- [ ] Mở phần mềm sổ cũ → Cài đặt / Cổng COM / Baud / Data bits
- [ ] Chụp màn hình, ghi: COM máy tính (vd COM3), baud, 8N1 hay 7E1
- [ ] Không có menu: tìm file `.ini` / `.cfg` cạnh phần mềm, tìm chữ `9600` `1200` `baud`
- [ ] Gửi ảnh issue #3

### A3. Lắp DTECH — cuối ca, không xe

- [ ] Tắt không đụng LOAD CELL
- [ ] Rút **chỉ** dây `MAN` khỏi COM2
- [ ] Cắm: Kingbird COM2 → cáp DB25đực–DB9đực → **INPUT** DTECH
- [ ] OUTPUT1 DTECH → dây màn `MAN` (thêm đầu chuyển nếu giới tính sai)
- [ ] OUTPUT2 DTECH → USB-RS232 FTDI → USB CANcomp
- [ ] Cắm nguồn **DC 5V** DTECH (vào là đèn sáng)
- [ ] **Không** cắm Kingbird vào OUTPUT; **không** cắm PC vào INPUT

### A4. Kiểm tra màn + sổ cũ trước khi mở CoolTerm

- [ ] Màn phụ sáng, số kg khớp mặt Kingbird khi bàn không xe
- [ ] Sổ cũ vẫn đọc được (nhánh `SO_CU` nguyên)
- [ ] Lệch / màn tắt: rút DTECH, cắm lại dây `MAN` như cũ, dừng A3

### A5. CoolTerm trên CANcomp

- [ ] Device Manager: USB FTDI ra COMx (vd COM4) — ghi số cổng
- [ ] CoolTerm: đúng COM, baud ở A2; nếu chưa biết thử **1200 8N1** → 9600 8N1 → 9600 7E1
- [ ] Display ASCII + Hex; Connection → Open; bật ghi file
- [ ] Xe lên bàn (hoặc người đứng thử): màn có số → ô CoolTerm phải có chữ số cùng lúc
- [ ] Im lặng: đổi baud; rồi đảo TX/RX (cáp null-modem); không gõ lệnh vào CoolTerm
- [ ] File `docs/logs/YYYY-MM-DD-kingbird-COM2-<baud>.txt` + comment #3
- [ ] ≥ 10 lượt xe hoặc 30 phút

### A6. Ghi nhận khung tin

- [ ] Spew liên tục hay chỉ khi ổn / khi bấm Print?
- [ ] Có cờ STABLE / mũi tên mặt đồng hồ khớp dòng nào?
- [ ] Dấu `.` hay `,`; đơn vị kg?
- [ ] Đổi file + 5 dòng mẫu vào issue #3 — **A xong** khi đọc được số khớp màn

---

## Việc B — Máy đo củ mì → CANcomp

Mục tiêu: đọc được % điểm, 20 phiếu. **Không cần DTECH.**

### B0. Mua / chuẩn đồ

- [ ] 1 cáp USB→RS232 **FTDI** DB9 **đực** (máy bột là DB9 **cái**)
- [ ] Cáp nối dài DB9 nếu CANcomp xa bàn thử
- [ ] CoolTerm cùng máy CANcomp (COM khác với nhánh cân)

### B1. Cắm thẳng

- [ ] Cổng RS232 máy bột **trống** (nếu đang cắm máy khác — chụp ảnh, chưa rút ban ngày)
- [ ] Cắm FTDI vào máy bột + USB CANcomp
- [ ] Device Manager ra COMy (vd COM5) — khác COM nhánh A

### B2. Dò baud

- [ ] CoolTerm: **9600 8N1** trước; Open; Hex + ghi file
- [ ] Đo 1 mẫu thật hoặc bấm Print/Send trên máy bột
- [ ] Thấy số % khớp màn máy → giữ baud. Rác: 19200 → 4800 → 2400 → 115200 → 9600 **7E1**

### B3. 20 phiếu

Với mỗi phiếu ghi tay + file log:

| # | Giờ | % trên màn máy | Dòng CoolTerm | Khớp? |
|---|---|---|---|---|
| 1 |  |  |  |  |
| … |  |  |  |  |
| 20 |  |  |  |  |

- [ ] Spew hay chỉ khi bấm?
- [ ] `28.4` hay `284`? dấu `.` hay `,`?
- [ ] File `docs/logs/YYYY-MM-DD-bot-<baud>.txt` + bảng 20 dòng → issue #4
- [ ] **B xong** khi 20/20 dòng đọc được đúng %

---

## Việc C — Camera + đèn + agent CANcomp + sync canxe

Mục tiêu: kg ổn → đèn → chụp F+R → lưu local → đẩy canxe. Làm **sau khi A đọc được kg** (cam có thể chuẩn bị song song).

### C0. Mạng / cam

- [ ] CANcomp + cam trước + cam sau cùng switch LAN
- [ ] IP tĩnh mỗi cam; ghi user/pass (không để admin/admin lên git công khai)
- [ ] Chụp tem model cam + firmware → `docs/hardware-spec.md` + issue #5/#12
- [ ] Trình duyệt CANcomp mở được web cam
- [ ] Thử tay URL snapshot (hãng sẽ khác nhau), vd `http://IP/cgi-bin/snapshot.cgi` — tải được JPEG
- [ ] Tìm lệnh đèn: LED trên cam / Auxiliary ONVIF / đèn pha + USB-relay

### C1. Chuỗi chụp thủ công (chưa agent)

- [ ] Bật đèn
- [ ] Tải snapshot cam F, cam R
- [ ] Tắt đèn
- [ ] Ảnh đọc được biển (đủ sáng, không loá) — nếu mờ: đổi góc / đèn / focus
- [ ] Lưu 4 cặp ảnh mẫu `docs/logs/cam-F|R-*.jpg`

### C2. Agent local (khi A+B đã có khung tin)

- [ ] CANcomp chạy nền khi mở máy
- [ ] Mở đúng 2 COM (cân + bột), không gửi byte lên Kingbird
- [ ] Lọc cao nguyên: bỏ < ngưỡng; cửa 2 s `max−min < ε`; 1 số / lượt khi về 0
- [ ] Kg ổn → đèn ON 0,3 s → chụp F+R → đèn OFF
- [ ] Ghi SQLite: kg, %, ts, raw, đường dẫn JPEG
- [ ] Mất mạng vẫn ghi local

### C3. Sync canxe

- [ ] `POST https://canxe.redtigerhead.com/api/ingest` + header `X-Station-Key`
- [ ] Hàng đợi: gửi lại khi 5xx / mất net
- [ ] Mill hiện phiên / kg / ảnh (OCR pha 1 trên canxe)
- [ ] **Không** ghi `binhminh_data` từ CANcomp
- [ ] Thử cắt Wi-Fi 10 phút → cắm lại → đủ bản ghi lên web

### C4. Cửa đối chiếu sổ cũ

- [ ] 10 lượt: kg CANcomp vs kg sổ cũ vs mặt Kingbird — sai số = 0
- [ ] 10 phiếu bột: % agent vs màn máy — sai = 0
- [ ] Xong C4 mới nói tới OCR 95% / khóa biển

---

## Thứ tự tuần này

| Ngày | Làm |
|---|---|
| Hôm có hàng | A0+A1+A2 và B0+B1+B2 (B không chờ DTECH) |
| Cuối ca | A3+A4+A5 |
| Ngày cân thường | A6 + B3 |
| Cam về | C0+C1 song song |
| A+B đọc đúng số | C2+C3+C4 |

Rollback A3: rút DTECH, cắm lại dây `MAN` vào COM2 — màn về như cũ.
