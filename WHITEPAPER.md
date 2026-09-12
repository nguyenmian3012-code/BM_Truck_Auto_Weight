# BM Cân Xe Tự Động — Whitepaper triển khai phần cứng & kích hoạt chụp

Phiên bản: 12/09/2026 · Nhà máy Bình Minh (tinh bột khoai mì)  
Host: [canxe.redtigerhead.com](https://canxe.redtigerhead.com)  
Repo: [nguyenmian3012-code/BM_Truck_Auto_Weight](https://github.com/nguyenmian3012-code/BM_Truck_Auto_Weight)

Tài liệu này khóa **chiến thuật**: mô hình nhỏ (mock-up) → đối chiếu 1 tháng với sổ cũ → chính thức khi lỗi cân/đo **< 1%**. Phần mềm mill v5 tạm dừng tính năng mới; công việc tiếp theo là giao tiếp thiết bị.

---

## 0. Hiện trạng thiết bị (đã chốt)

| Hạng mục | Trạng thái |
|---|---|
| Cầu cân xe | **Đã có** — dùng lại, không mua bàn mới |
| Màn phụ tài xế (scoreboard) | Chưa có — không chặn giai đoạn 1 |
| Camera | Tận dụng **IP camera sẵn có**; model cụ thể cung cấp sau, chỉnh firmware/CGI/ONVIF tối thiểu |
| Máy đo điểm củ mì | **Đã có, ra RS232** — baud / khung tin **chưa biết** |
| iPad / tablet chống nước | **Để sau** — thử mẫu giai đoạn 1 trên PC nhà cân |
| PostgreSQL `binhminh_data` | Đã có — không xây lại, chỉ tích hợp khi song song |

Nguyên tắc: **cùng một lớp giao tiếp** cho mock-up và thiết bị thật. Thay driver, không thay phần mềm nghiệp vụ.

---

## 1. Hai bước chạy song song

```
                    ┌─ Bước 1A  Mock-up (xe đồ chơi + cân nhỏ)
                    │   cùng protocol với hệ thật
Chiến thuật ────────┤
                    └─ Bước 1B  Nghe thiết bị thật (RS232 cân + RS232 bột + CGI cam)
                            xác định baud, khung tin, ngôn ngữ

        mọi thứ đạt, không lỗi
                    │
                    ▼
            Thay mock-up bằng thiết bị thật
                    │
                    ▼
        Bước 2 — Chạy SONG SONG sổ cũ  ≥ 30 ngày
                    │
                    ▼
        Tỷ lệ lệch / lỗi cân-đo  < 1%  →  chính thức
        ≥ 1%                         →  giữ song song, sửa driver
```

Bước 1A và 1B **làm cùng lúc**, không chờ nhau.

---

## 2. Lớp giao tiếp chung (không đổi khi lên thiết bị thật)

Ba sự kiện duy nhất phần mềm mill nhận. Mock-up và thiết bị thật **cùng schema**:

```
ScaleEvent     { kg: number, stable: boolean, ts: ISO, raw: string }
CameraShot     { lane: "F" | "R" | "3", jpegGray: bytes, ts: ISO, sharpness: number }
MeterReading   { starchPct: number, ts: ISO, raw: string }   // chỉ củ mì; khóa, không gõ tay
```

Driver:

| Driver | Mock-up | Thật |
|---|---|---|
| `ScaleDriver` | Cân bàn nhỏ / HX711 → **cùng khung tin** đầu cân thật (sau khi 1B giải mã) | RS232/Ethernet đầu cân hiện có |
| `CameraDriver` | IP cam rẻ hoặc điện thoại, gọi **cùng lệnh snapshot** (CGI/ONVIF) | IP cam nhà máy, cùng lệnh |
| `MeterDriver` | Giả lập khung tin máy bột **copy 1:1 từ log 1B** | Máy đo củ mì RS232 |

Khi thay mock → thật: chỉ đổi cổng COM / URL cam. Mill, phiên IN/OUT, luật 95%, sổ ngày **không đổi**.

---

## 3. Kiến trúc kích hoạt chụp tự động (chi tiết)

Mục tiêu: xe lên bàn → **tự chụp**, không bấm nút. Nguồn sự thật là **cân ổn định**, không phải chuyển động trong hình.

### 3.1 Sơ đồ

```
  Loadcell (đã có)
        │
        ▼
  Đầu cân / indicator
        │  (1) luồng kg liên tục  RS232 hoặc Ethernet
        │  (2) bit/cờ STABLE     (nếu đầu cân có)
        ▼
  ┌─────────────────────────────────────────┐
  │  ScaleDriver                            │
  │  - đọc kg                               │
  │  - debounce: |Δkg| < ε  trong ≥ 2,0 s   │
  │  - phát ScaleEvent.stable = true  1 lần │
  └──────────────────┬──────────────────────┘
                     │  cạnh lên (rising edge)
                     ▼
  ┌─────────────────────────────────────────┐
  │  CaptureOrchestrator                    │
  │  1. khóa phiên tạm (đang chụp)          │
  │  2. snapshot Cam F + Cam R  cùng lúc    │
  │  3. kiểm nét (Laplacian / cạnh biển)    │
  │  4. nét thấp → chụp lại 1 lần (tối đa)  │
  │  5. JPEG xám, cạnh ~640 px              │
  │  6. OCR biển F / R                      │
  │  7. khớp ≥ 95% → điền biển, khóa        │
  │     lệch   → pending + Cam 3 (nếu có)   │
  └──────────────────┬──────────────────────┘
                     ▼
              Mill: mở phiên IN / checkout OUT
```

### 3.2 Vì sao nguồn kích là cân, không phải camera

- Camera thấy xe “đứng” khi tài xế còn nhích phanh — kg vẫn nhảy.
- Cầu cân đã có, tín hiệu kg là **số liệu pháp lý** của phiếu.
- Luật nhà máy: chờ **2 giây ổn định** rồi mới chụp — khớp debounce trên `ScaleEvent`.

Camera chỉ **chụp theo lệnh**, không tự quyết “đã đến lúc”.

### 3.3 Định nghĩa “ổn định” (cần đo trên đầu cân thật ở 1B)

Trên mock-up dùng cùng công thức, ε chỉnh sau khi có log thật:

```
stable ⇔  (max(kg) − min(kg)) trong cửa sổ 2,0 s  <  ε
ε khởi điểm:  20 kg  (bàn 60–100 tấn; chỉnh sau hiệu chuẩn)
không phát stable lần 2 cho đến khi xe rời bàn (kg ≈ 0 hoặc dưới tare sàn)
```

Nếu đầu cân **đã có bit STABLE**: dùng bit đó **và** vẫn giữ cửa sổ 2 s (phòng bit nháy).

Nếu đầu cân **chỉ spew số kg**, không bit: ScaleDriver tự tính cửa sổ 2 s.

### 3.4 Chuỗi thời gian một lượt xe

| t | Việc |
|---|---|
| 0,0 s | Bánh lên bàn, kg tăng |
| … | kg dao động |
| T | Cửa sổ 2 s bắt đầu khi dao động < ε |
| T+2,0 | `stable=true` → lệnh snapshot F+R |
| T+2,1 | Ảnh về, nén xám |
| T+2,3 | OCR; khớp ≥95% điền biển, **không cho sửa tay** |
| T+2,5 | Mở phiên IN (hoặc checkout OUT nếu biển đã trong bãi) |

Xe chưa ổn mà cam chụp = ảnh nhòe + kg sai — **cấm** chụp sớm.

### 3.5 Lệnh chụp IP camera (chỉnh nhẹ cam sẵn có)

Driver camera thống nhất một hàm: `snapshot(lane) → JPEG`.

Thử lần lượt (khi có model):

1. **ONVIF** `GetSnapshotUri`
2. **HTTP CGI** kiểu `/cgi-bin/snapshot.cgi` / `/ISAPI/Streaming/channels/101/picture` (Hikvision) / `/onvif-http/snapshot` (Dahua)
3. **RTSP** lấy 1 keyframe (chỉ khi CGI không có)

Mock-up dùng **cùng hàm**, URL trỏ cam rẻ hoặc IP Webcam. Khi đổi cam nhà máy: đổi host/user, không đổi mill.

Cam 3 chỉ bật khi `plateF ≠ plateR` hoặc tin cậy < 95% (biển giấy máy cày).

### 3.6 Chất lượng ảnh & chụp lại

- JPEG **xám**, cạnh dài ~640 px (đủ OCR, nhẹ lưu).
- Nét: phương sai Laplacian dưới ngưỡng → **một** lần chụp lại, rồi pending thủ công (xác nhận người, **không gõ biển**).
- Ảnh gắn `sessionId` + `lane` + `ts`; sau này ghi `binhminh_data`.

### 3.7 Cái mock-up phải mô phỏng được

Cân nhỏ cũng phải phát **cùng** `ScaleEvent` (kể cả giả bit STABLE nếu đầu cân thật có). Xe đồ chơi dán biển; cam mock gọi `snapshot("F"|"R")`. Nếu mock chỉ “bấm nút chụp” thì **không** chứng minh được kiến trúc — đó là lỗ hổng giai đoạn 1.

---

## 4. Bước 1B — Giải mã máy đo củ mì RS232

Máy đã có. Việc: biết **baud, bit, khung tin, tần số**.

### 4.1 Máy tính sample (tạm, không phải tablet)

- 1 máy tính / laptop nhà cân  
- Cáp RS232 + USB-RS232 (FTDI)  
- Phần mềm nghe cổng: ghi **raw hex + ASCII + timestamp** từng dòng, tối thiểu 30 phút lúc cân thật  

Không nối mill cho đến khi đọc được 20 phiếu liên tiếp đúng.

### 4.2 Quét tham số (thứ tự)

| Thử | Baud | Frame |
|---|---|---|
| 1 | **9600** | 8N1 |
| 2 | 19200 | 8N1 |
| 3 | 4800 | 8N1 |
| 4 | 38400 / 115200 | 8N1 |
| 5 | 9600 | 7E1 / 8E1 (nếu 8N1 rác) |

Nhiều máy đo tinh bột VN/CN: 9600 8N1, spew liên tục hoặc khi nhấn “Print/Send”.

### 4.3 Cần trả lời được

1. Máy **tự spew** hay chỉ gửi khi bấm nút trên máy?  
2. Một dòng hay khối STX/ETX?  
3. Dấu phẩy / chấm thập phân? `28.4` hay `28,4` hay `2840` (×0,1)?  
4. Có mã ổn định / đơn vị `%`?  
5. Tần số: Hz spew, hay 1 khung / mẫu?  
6. Có tiếng Việt / mã codepage trong chuỗi không? (thường không — chỉ số)

Log mẫu (giữ nguyên, không sửa):

```
ts=... hex=... ascii=...
```

Sau khi chốt: viết `MeterDriver` đọc **đúng một** khung, map → `MeterReading.starchPct`. Mill **khóa** ô điểm — không input.

### 4.4 Đầu cân (cùng đợt 1B)

Nghe RS232/Ethernet đầu cân hiện có: kg, dấu ổn định, tần số spew. Ra spec `ScaleDriver` — mock-up **bắt chước byte-for-byte** (không invent protocol riêng).

---

## 5. Bước 1A — Prototype mock-up (công suất nhỏ)

Mục đích: chứng minh **cùng protocol**, không chứng minh tải 80 tấn.

### 5.1 Linh kiện gợi ý (size nhỏ)

| Mô phỏng | Linh kiện | Ghi chú |
|---|---|---|
| Cầu cân | Cân bàn 5–20 kg hoặc HX711 + loadcell 5 kg | Arduino/USB xuất **cùng chuỗi** đã sniff ở 1B |
| Xe | Truck đồ chơi | Dán biển VN in giấy (trước + sau) |
| Cam F/R | 2 IP cam rẻ **hoặc** 2 điện thoại app IP Webcam | Gọi cùng CGI/ONVIF wrapper |
| Máy bột | Script phát lại file log RS232 thật (1B) ra COM ảo | Không bịa số |
| Trạm | Cùng mill (canxe) trỏ driver mock | |

Biển giấy trên xe đồ chơi = đúng case “máy cày / biển giả” — luyện nhánh <95%.

### 5.2 Cổng vật lý giống thật

- Mock cân **cắm COM** (USB-RS232), không MQTT riêng kiểu “demo”.  
- Mock cam **HTTP snapshot**, không file JPEG có sẵn trong thư mục (thư mục chỉ dùng khi cam chết — không phải đường chuẩn).  
- Khi 1B ra spec, nạp firmware/script mock **khớp spec** trong tuần.

### 5.3 Checklist “đạt, không lỗi” trước khi thay thiết bị thật

- [ ] Xe đồ chơi lên bàn → 2 s → **tự** hai ảnh F/R  
- [ ] Biển F=R ≥95% → điền, không sửa tay được  
- [ ] F≠R → pending, không mở phiên mù  
- [ ] Checkout OUT khớp phiên mở, khóa sổ ngày  
- [ ] Log máy bột phát lại → ô điểm khóa đúng số  
- [ ] Cùng một mill build với driver mock; không nhánh code “nếu demo thì…” rải trong nghiệp vụ  

---

## 6. Bước 2 — Song song với phương án cũ (1 tháng)

Sau khi driver thật thay mock:

| Việc | Cách |
|---|---|
| Sổ cũ | Giữ nguyên quy trình hiện tại (ghi tay / phần mềm cũ) — **source of truth vận hành** tháng đó |
| Sổ mới | Mill ghi phiên + kg + biển + điểm (nếu có) — **không** ghi đè sổ cũ |
| Đối chiếu mỗi ngày | Biển, kg tổng, kg hàng, IN/OUT, điểm bột (củ mì) |
| Lỗi | `\|kg_mới − kg_cũ\| / kg_cũ ≥ ngưỡng` hoặc sai biển hoặc sai hướng |

**Ngưỡng chính thức:** tỷ lệ phiếu lỗi **< 1%** trên **≥ 30 ngày lịch** (không phải 30 ngày có xe). Mẫu tối thiểu: đủ ngày có củ mì **và** ngày có bột/bao.

Nếu ≥ 1%: giữ song song, sửa driver/ε/cam, **không** cắt sổ cũ.

Khi < 1%: mill + `binhminh_data` thành source of truth; sổ cũ lưu kho. Ô biển camera vẫn không gõ tay.

Tablet thử mẫu chống nước: **sau** cutover, không chặn tháng song song (thử mẫu trên PC nhà cân).

---

## 7. Việc cố ý chưa làm

- Màn phụ tài xế  
- iPad/tablet  
- Cam 3 / cam thùng — khi IP cam nhà máy đã snapshot ổn  
- Barrier, RFID  
- Viết lại PostgreSQL  

---

## 8. Trách nhiệm chống thao túng (giữ nguyên)

- Biển chỉ từ camera; không ô nhập tay trên bàn sản xuất  
- Điểm tinh bột chỉ từ RS232  
- Phiếu đóng (checkout) không sửa  
- Tháng song song: không lấy mill làm căn thanh toán cho đến khi < 1%  

---

*Hết whitepaper. README.md tóm tắt vận hành + con trỏ tới đây.*
