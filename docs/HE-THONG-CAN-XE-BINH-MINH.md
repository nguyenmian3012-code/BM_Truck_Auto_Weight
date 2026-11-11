# Hệ thống Cân xe Bình Minh — cấu trúc đã chốt

Ngày chốt bản đồ gốc: **25/09/2026**. Cập nhật đang chạy: **11/11/2026**.  
Nhà máy tinh bột khoai mì Bình Minh. Host mill: https://canxe.redtigerhead.com

Đọc mục 0 trước. Phần bên dưới là quyết định tháng 9 còn hiệu lực về dây và sổ cũ. Chỗ nào mục 0 nói khác thì tin mục 0.

File này tồn tại ở **hai repo**. Sửa một bên thì đối chiếu bên kia trong cùng ngày.

| Bản | Chỗ |
|---|---|
| Hệ thống | https://github.com/nguyenmian3012-code/BM_Truck_Auto_Weight/blob/main/docs/HE-THONG-CAN-XE-BINH-MINH.md |
| Phần mềm CANcomp | https://github.com/nguyenmian3012-code/BM_CANXE_SOFT_CANcomp/blob/main/docs/HE-THONG-CAN-XE-BINH-MINH.md |
| Điểm bột | https://github.com/nguyenmian3012-code/BM-ThuDiem |

## 0. Đang chạy 11/11/2026

```
  Sổ cũ                         không cài phần mềm mới
  Kingbird COM2 ── DTECH ── OUTPUT1 → sổ cũ
                         └─ OUTPUT2 → USB-RS232 → CANcomp COM5 → BM Auto Cân 0.18.44
  Máy bột USB-RS232 → CANcomp COM4 → BM-ThuDiem 1.2.0
  Cam F / R / S ── LAN ── CANcomp → AutoCan chụp → BM-OCR đọc biển
  BM-ThuDiem thả file điểm → AutoCan POST /api/ingest → canxe.redtigerhead.com
```

| Luật | |
|---|---|
| COM5 | Chỉ AutoCan. Kingbird. 1200 8N1. Cửa 3 giây, ε 20 kg. |
| COM4 | Chỉ BM-ThuDiem. Gram viết ngược. Khô gần 5000 g. Ướt trung vị khoảng 300–700 g. Tra Quyết định 228. Không lấy khô trừ ướt. |
| OCR | Trên CANcomp, một ảnh một lượt, không ghi SQLite. Không đoán chữ cái thiếu. |
| Thanh toán | Vẫn sổ cũ, cho đến khi 30 ngày lệch dưới 1%. |

Lần kiểm tra mạng 11/11: máy CANcomp thấy địa chỉ `192.168.100.20`. Camera `.101` và `.102` không trả lời ping. Đó là lỗi dây, chưa phải lỗi code chụp.

---

## 1. Bốn lớp, không trộn

```
  Sổ cũ (máy đang vận hành)
      │  giữ nguyên, không cài phần mềm mới, không cắt cáp
      │
  (sơ đồ tháng 9, đã bị mục 0 thay. Giữ để đối lịch sử.)
  Đầu cân Kingbird COM2 ── DTECH 1→2 ── OUTPUT1 → màn / sổ cũ
                          └─ OUTPUT2 → USB-RS232 → CANcomp COM5
  Máy bột DB9 ────────────── USB-RS232 → CANcomp COM4 → BM-ThuDiem
  Cam F / R / S ── LAN ── CANcomp → BM-OCR

  CANcomp   BM Auto Cân + BM-OCR + BM-ThuDiem
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
| Trạm cân | **CANcomp** | `BM_CANXE_SOFT_CANcomp` và `BM-ThuDiem` | AutoCan: COM5, ảnh, SQLite xe. ThuDiem: COM4, điểm bột. OCR một lần trên CANcomp, không ghi SQLite | Ghi Postgres, hai chương trình một cổng, MQTT, ghi byte lên đầu cân |
| Mill | canxe.redtigerhead.com | `BM_Truck_Auto_Weight` (`worker/`, `cf-site/`) | Phiên, biển, sổ ngày, nhận ingest | Đọc COM (không có cổng trên Cloudflare) |
| Sổ pháp lý sau | `binhminh_data` | Repo cha, khi tới bước tích hợp | Nhận phiếu đã khóa từ mill | CANcomp nối thẳng |

Quyết 15/09/2026, còn hiệu lực: agent **không** cài lên máy sổ cũ. Một PC riêng.

## 2. Phần mềm CANcomp làm gì — yêu cầu đã chốt

Chạy Windows 10 trở lên. Ngôn ngữ: **C# .NET 8**. Lớp vẽ đang chạy là **WinForms**. Không chuyển WPF trước khi 20 lượt kg khớp sổ cũ.

Yêu cầu:

1. AutoCan chỉ đọc COM5. BM-ThuDiem chỉ đọc COM4. Không chương trình nào đọc cả hai.
2. Bỏ số lúc bàn cân được vệ sinh, số lỗi, số khi cân ở 0, số người đứng (thấp, không phải xe).
3. Cân xe: cửa **3 giây**, ε 20 kg, một số cho một lượt. Điểm bột nằm ở BM-ThuDiem: khô gần 5000 g, ướt là trung vị cao nguyên thấp, tra Quyết định 228. Không lấy khô trừ ướt.
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
| Lọc | Sàn 80 kg. Dưới 400 kg không phải đỉnh xe. ε 20 kg trong **3,0 giây** (nâng từ 2 giây ngày 29/09/2026 để gần sổ cũ). Trần 120000 kg |

### Cổng 2 — máy bột

| | |
|---|---|
| Việc | Điểm hàm lượng bột của củ mì. Ô điểm trên mill khóa, không gõ tay |
| Chip đã gặp | Prolific PL2303 |
| Khung đã chốt 29/09/2026 | `NNNNNN=` là **gram viết ngược**. `040500=` = 5040 g khô. `075000=` = 570 g ướt. `000000=` = 0 |
| Cổng trên CANcomp | **COM4**, chỉ BM-ThuDiem. Không mở từ AutoCan. |
| Cấu hình | **1200 8N1**, DTR tắt, RTS tắt, không software flow. Không 7N1. |
| Lọc đang chạy 11/11 | BM-ThuDiem 1.2.0. Khô: mẫu gần 5000 g trong 4200–5800 g. Ướt: trung vị của cao nguyên 150–1200 g, thường 300–700 g. `5000 × ướt / khô`, tra Phụ lục 228. 522 g = 22,4%. Không dùng khô − ướt. Nước rung không được làm mất phiếu. |

### Bảo mật trên máy

- PIN admin mặc định `2580`, đổi khi cài máy thật.
- `STATION_KEY` chỉ nằm trên máy (`C:\\ProgramData\\BmCancomp\\appsettings.json`), không vào git.
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

SQLite: `C:\\ProgramData\\BmCancomp\\data\\cancomp.db`, bảng `events` (queued / retry / sent / fail, không xóa theo ngày) và `raw_log` (raw RS232, xóa sau 2 ngày). Lưới chính chỉ 50 phiếu mới. Phiếu cũ: nút Tìm phiếu.

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
- Xe lên bàn, cân ổn định 3 giây, rồi mới được chụp. Không chụp vì hình “thấy xe đứng”. Ảnh chưa phải việc của vòng đối sổ.
- Phiên IN/Ra chỉ khi đã có biển tin. Không mở phiên từ kg trần.
- Điểm bột chỉ từ RS232 (phiếu `starch` của app này), không ô nhập.
- OCR chạy trên CANcomp (BM-OCR), một ảnh một lượt, không ghi database. Chưa đủ chữ thì Nghi, không đoán. Không OCR lần hai tự động trên mill.
- Một JPEG ghép dính `eventId` là đủ khi tới lượt ảnh. Không chặn phiếu kg vì chưa đủ ba camera. Đèn trắng, không dùng IR lúc chụp biển.

## 4. Thứ tự đưa vào vận hành

1. CANcomp đang chạy AutoCan 0.18.44, BM-OCR 0.18.44 và BM-ThuDiem 1.2.0. Việc kế: 20 lượt kg và một ca bột đối với sổ cũ và đèn máy. Lệch kg thì sửa ε hoặc cửa, không thêm tính năng.
2. Worker nhận được kg và điểm trước khi bật key production.
3. Sổ cũ vẫn là căn cho đến khi lệch dưới 1% đủ 30 ngày.
4. Ảnh: một `eventId` lúc khóa kg, một JPEG, ACK ảnh mới cho xuống. Không đợi OCR.
5. Không chuyển WPF. Không ghi `binhminh_data` từ CANcomp.

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
5. Nếu chỉ sửa parser / icon / PIN: repo app là đủ. Sửa điểm bột thì chỉ repo BM-ThuDiem.
6. Nếu sửa ghép biển: `ocr/branch.py` trong repo app. Không sửa `decide()` để đoán thêm.

Tìm lại cho nhanh: `BM_CANXE_SOFT_CANcomp`, `BM-ThuDiem`, `BM_Truck_Auto_Weight`.
