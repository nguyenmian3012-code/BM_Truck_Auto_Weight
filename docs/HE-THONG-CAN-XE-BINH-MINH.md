# Hệ thống Cân xe Bình Minh — cấu trúc đã chốt

Ngày chốt bản đồ: **25/09/2026**.  
Nhà máy tinh bột khoai mì Bình Minh. Host mill: https://canxe.redtigerhead.com

File này tồn tại ở **hai repo**. Sửa một bên thì đối chiếu bên kia trong cùng ngày. Cách đối chiếu: [LIEN-KET-REPO-CHA.md](LIEN-KET-REPO-CHA.md) (trong repo app) và `docs/LIEN-KET-PHAN-MEM-CANCOMP.md` (trong repo cha).

| Bản | Chỗ |
|---|---|
| Hệ thống (bản này, góc nhìn mill + máy) | https://github.com/nguyenmian3012-code/BM_Truck_Auto_Weight/blob/main/docs/HE-THONG-CAN-XE-BINH-MINH.md |
| Phần mềm CANcomp (cùng nội dung) | https://github.com/nguyenmian3012-code/BM_CANXE_SOFT_CANcomp/blob/main/docs/HE-THONG-CAN-XE-BINH-MINH.md |

Nếu lạc vào một repo và không thấy số liệu: repo kia là chỗ còn lại. Không có repo thứ ba cho cầu cân.

---

## 1. Bốn lớp, không trộn

```
  Sổ cũ (máy đang vận hành)
      │  giữ nguyên, không cài phần mềm mới, không cắt cáp
      │
  Đầu cân Kingbird COM2 ── DTECH 1→2 ── OUTPUT1 → màn / sổ cũ
                          └─ OUTPUT2 → USB-RS232 → CANcomp   (chỉ nghe)
  Máy bột DB9 ────────────── USB-RS232 (PL2303) → CANcomp
  Cam F / cam R (chưa nối vào app 0.1) ── LAN ── CANcomp

  CANcomp   phần mềm BM CANcomp
      │     lọc cao nguyên · SQLite · hàng đợi
      │     HTTPS + X-Station-Key
      ▼
  canxe.redtigerhead.com     mill BM Cân Xe
      │     phiên IN/OUT · biển từ camera · sổ ngày
      │     (sau, khi lệch < 1%) 
      ▼
  PostgreSQL binhminh_data   không nối từ CANcomp
```

| Lớp | Máy / chỗ | Repo sở hữu mã | Được làm | Cấm |
|---|---|---|---|---|
| Sổ cũ | Máy nhà cân hiện tại | Không có trong hai repo này | Giữ quy trình cũ trong tháng song song | Cài agent, cắt COM1, dùng Y-cable nối chung TX |
| Trạm cân | **CANcomp** (thử trước trên **MinhComp**) | `BM_CANXE_SOFT_CANcomp` | Nghe RS232, lọc, SQLite, sync HTTPS. Sau này: đèn + chụp | Ghi Postgres, OCR hai nơi, MQTT, ghi byte lên đầu cân |
| Mill | canxe.redtigerhead.com | `BM_Truck_Auto_Weight` (`worker/`, `cf-site/`) | Phiên, biển, sổ ngày, nhận ingest | Đọc COM (không có cổng trên Cloudflare) |
| Sổ pháp lý sau | `binhminh_data` | Repo cha, khi tới bước tích hợp | Nhận phiếu đã khóa từ mill | CANcomp nối thẳng |

Quyết 15/09/2026, còn hiệu lực: agent **không** cài lên máy sổ cũ. Một PC riêng.

## 2. Phần mềm CANcomp làm gì — yêu cầu đã chốt

Chạy Windows 10 trở lên. Ngôn ngữ: **C# .NET 8**. Bản 0.1 vẽ bằng WinForms. Lớp vẽ sau chuyển **WPF**; phần đọc cổng và lọc giữ nguyên.

Yêu cầu:

1. Đọc liên tục hai cổng COM RS232.
2. Bỏ số lúc bàn cân được vệ sinh, số lỗi, số khi cân ở 0, số người đứng (thấp, không phải xe).
3. Chỉ lấy giá trị **cao và đứng yên** — cửa 2 giây, không nhảy. Một số cho một lượt xe hoặc một mẫu bột.
4. Admin đơn giản bằng PIN. Người cân không sửa ε, không sửa cổng, không thấy `STATION_KEY`.
5. Đẩy lên mill **đúng cấu trúc** phía dưới. Mất mạng thì giữ local rồi gửi lại.
6. Tháng đối chiếu: mill không phải căn thanh toán cho đến khi lệch với sổ cũ **dưới 1%** trên ít nhất 30 ngày lịch (whitepaper repo cha).

### Cổng 1 — cầu cân xe

| | |
|---|---|
| Đầu cân | Mettler Toledo Kingbird (Changzhou), model KINGBIRD, fact no KTGN-T100-078, serial B231161076 |
| Nguồn | 220 VAC / 50 Hz. Tem kiểm định mặt 01853 N385 hạn 01-27 |
| Cổng dùng để nghe | **COM2** RS232. COM1 đang sang cáp Shield — không cắt. LOAD CELL không chia |
| Cách nghe | Tap TX của đầu cân sang RX của USB-RS232. TX của CANcomp **không nối**. GND chung |
| Bộ chia | DTECH 1→2. OUTPUT1 giữ đường cũ. OUTPUT2 sang CANcomp |
| Khung | ASCII kg. Baud không in tem. Thử **1200 8N1** rồi 9600. Spew menu F3 chưa biết (0 liên tục / 1 lệnh / 2 SICS) |
| Lọc | Sàn 80 kg. Dưới 400 kg không phải đỉnh xe. ε 20 kg trong 2,0 giây. Trần 120000 kg |

### Cổng 2 — máy bột

| | |
|---|---|
| Việc | Điểm hàm lượng bột của củ mì. Ô điểm trên mill khóa, không gõ tay |
| Chip đã gặp | Prolific PL2303 |
| Khung đã gặp 25/09/2026 | `NNNNNN=` — ví dụ nghỉ `000000=` |
| Cấu hình đã chốt vì sự cố COM5 | **1200 8N1**, DTR tắt, RTS tắt, không software flow. Không trả về 7N1 |
| Lọc | Sàn 0,05 %. Đỉnh tối thiểu 5 %. ε 0,2 điểm trong 2,0 giây. Trần 80 % |

### Bảo mật trên máy

- PIN admin mặc định `2580`, đổi khi cài máy thật.
- `STATION_KEY` chỉ nằm trên máy (`C:\ProgramData\BmCancomp\appsettings.json`), không vào git.
- App chạy `asInvoker`, không xin quyền admin Windows. Ghi vào ProgramData nên lần đầu có thể cần quyền ghi thư mục đó.

### Đồng bộ

Chỉ **một** đường lên mây:

```
POST https://canxe.redtigerhead.com/api/ingest
Header: X-Station-Key: <secret worker bm-can-xe>
```

Body cân (`source = kingbird`): `id`, `stationId`, `kg`, `stable: true`, `ts` ISO có offset +07:00, `raw`.  
Body bột (`source = starch`): cùng các field, thay `kg` bằng `starchPct`.

`stationId` bản thử MinhComp: `MinhComp-Draft`.  
`stationId` CANcomp: `BinhMinh-CanXe`.

SQLite: `C:\ProgramData\BmCancomp\data\cancomp.db`, bảng `events` (queued / retry / sent / fail) và `raw_log`.

**Trạng thái mill tại 25/09/2026:** hợp đồng trên đã viết trong `docs/cancomp.md` của repo cha. File `worker/index.js` trên `main` (`9a1f5db`) chưa gắn route `/api/ingest`. App xếp hàng và thử lại. Chưa có 2xx thì chưa có phiếu trên mill.

Khi thêm route, checklist bắt buộc:

- [ ] Worker repo cha đọc đúng field `kg` hoặc `starchPct`, không đổi tên một phía.
- [ ] Header đúng `X-Station-Key`.
- [ ] Từ chối request không key.
- [ ] Không để CANcomp ghi `binhminh_data`.
- [ ] Sửa xong thì ghi một dòng vào cả hai bản file này.

## 3. Mill làm gì — không làm trên CANcomp

Theo whitepaper và mill v5 trong repo cha:

- Biển số chỉ từ camera. Khớp trước/sau ≥ 95% thì điền, không gõ tay. Dưới 95% thì pending.
- Xe lên bàn, cân ổn định 2 giây, rồi mới chụp. Không chụp vì hình “thấy xe đứng”.
- Phiên IN mở khi vào. Checkout OUT khóa sổ ngày (tổng, hàng, xe, lấy/xả).
- Điểm bột chỉ từ RS232 (chính là phiếu `starch` của app này), không ô nhập.
- OCR pha 1: ảnh đưa lên mill. OCR local trên CANcomp chỉ xét khi mất mạng dài — không làm hai bộ OCR cùng lúc.
- Camera + đèn: ON → chụp F và R → OFF → JPEG xám. **Chưa code trong app 0.1.** Spec nằm ở `docs/cancomp.md` repo cha. Khi code, code nằm trong repo app này, spec vẫn trỏ từ repo cha.

## 4. Thứ tự đưa vào vận hành

1. MinhComp: nghe COM thật (nếu có cáp) hoặc đối chiếu log. Lọc phải ra **một** số đúng đỉnh, không ra số vệ sinh.
2. Viết `/api/ingest` trên worker — cùng lúc đối chiếu payload repo app.
3. Chạy song song sổ cũ ≥ 30 ngày. Sổ cũ vẫn là căn vận hành trong tháng đó.
4. Lệch / lỗi cân-đo < 1% thì mill mới thành căn. Ngược lại giữ song song, sửa ε hoặc parser ở repo app, không cắt sổ cũ.
5. Cài lên CANcomp sau khi bản MinhComp ổn. Không cài bản đang lệch.
6. WPF thay WinForms khi sắp xếp cửa sổ — không chặn bước nghe COM nếu WinForms 0.1 đã lọc đúng.
7. Camera, đèn, rồi mới `binhminh_data`.

## 5. Cố ý chưa làm

- Màn phụ tài xế, tablet, barrier, RFID.
- Viết lại PostgreSQL.
- Cài bất cứ thứ gì lên máy sổ cũ.
- Hai đường sync (MQTT song song HTTPS).

## 6. Khi cập nhật hệ thống — đừng bỏ repo app

Làm đủ trước khi đóng việc:

1. Việc có đụng kg, điểm bột, cổng COM, hoặc `/api/ingest` không? Nếu có, mở **cả hai** repo.
2. Sửa mã ở repo sở hữu (bảng mục 1 và file liên kết).
3. Nếu luật lọc hoặc hợp đồng JSON đổi: sửa **cả hai** bản `HE-THONG-CAN-XE-BINH-MINH.md` (cha và app) trong cùng commit-ngày.
4. Nếu chỉ sửa màu mill, biển số, sổ ngày: repo cha là đủ. Không cần phát hành lại exe.
5. Nếu chỉ sửa parser / icon / PIN: repo app là đủ. Thêm một câu vào `docs/cancomp.md` của repo cha khi phần cứng hoặc baud đổi.

Tìm lại cho nhanh: trong repo cha tìm cụm `BM_CANXE_SOFT_CANcomp`. Trong repo app tìm cụm `BM_Truck_Auto_Weight`.
