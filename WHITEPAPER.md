# BM Cân Xe Tự Động — Whitepaper

Phiên bản **11/11/2026**. Thay cách làm của bản 09/10/2026.  
Nhà máy tinh bột khoai mì Bình Minh.

Phần mềm đang chạy trên CANcomp:

| Chương trình | Repo | Bản |
|---|---|---|
| BM Auto Cân Desktop | [BM_CANXE_SOFT_CANcomp](https://github.com/nguyenmian3012-code/BM_CANXE_SOFT_CANcomp) | **0.18.44** |
| BM-OCR (cùng gói exe, Python) | cùng repo desktop | **0.18.44** |
| BM-ThuDiem | [BM-ThuDiem](https://github.com/nguyenmian3012-code/BM-ThuDiem) | **1.2.0** |

Mill: [canxe.redtigerhead.com](https://canxe.redtigerhead.com).  
Bản đồ dây: [docs/HE-THONG-CAN-XE-BINH-MINH.md](docs/HE-THONG-CAN-XE-BINH-MINH.md).

Bản 09/10 còn đúng về **đích**. Nó sai về cách làm hiện tại: OCR đã nằm trên CANcomp, điểm bột đã tách sang BM-ThuDiem, AutoCan không còn mở cổng máy bột.

---

## 1. Mục tiêu — không đổi

Bốn câu này là đích. Đổi cách làm được. Bỏ bốn câu này thì không còn là dự án này.

1. **Tự động.** Xe lên bàn thì ra một phiếu kg. Mẫu củ mì thì ra một điểm bột. Không bấm để chốt số. Không gõ kg, không gõ điểm, không gõ biển trên bàn sản xuất.
2. **Đúng.** Số đã khóa là số của lần đứng yên, không phải số đang nhảy. Đúng nghĩa là khớp sổ cũ đang dùng để thanh toán, không phải khớp một công thức tự đặt.
3. **Không bị người sửa phiếu.** Biển chỉ từ ảnh. Điểm chỉ từ máy bột. Phiếu đã khóa không sửa. Người cân không đụng ε, cổng, hay khóa trạm.
4. **Ít máy, chạy nền, ít bảo trì.** Một PC nghe. Một đường HTTPS. Một mill. Cửa sổ mở cùng Windows. Không cài lên máy sổ cũ. Không ghi byte lên đầu cân.

**Cổng ra, chưa đạt:** chạy song song sổ cũ ít nhất **30 ngày lịch**, tỷ lệ phiếu lệch **dưới 1%**. Trước cổng đó, sổ cũ là căn thanh toán. Sau cổng đó, mill và `binhminh_data` mới là sổ. Sổ cũ cất.

Không có barrier, không giữ xe vì thiếu ảnh hoặc thiếu biển.

Ngoại lệ đang có, và phải thu lại: admin được sửa phiếu Nghi hoặc Total fail, và được bấm Đọc AI. Đó là đường vá khi OCR chưa đáng tin. Không phải đích. Đích vẫn là phiếu tự khóa, không gõ.

---

## 2. Ba lớp chữ, đừng trộn

| Lớp | Nghĩa | Ví dụ |
|---|---|---|
| Mục tiêu | Còn khi cách làm đổi | Một số kg đã khóa cho một lượt xe. Biển không gõ tay. |
| Đã chốt | Cách làm đang nằm trong 0.18.44 và ThuDiem 1.2.0 | Cửa cân 3 giây. COM5 chỉ Kingbird. COM4 chỉ BM-ThuDiem. |
| Chưa đạt | Mục tiêu còn đó, chưa có bằng chứng vận hành | 30 ngày lệch dưới 1%. Biển đêm. Đối đèn máy bột. |

“Đã chốt” không có nghĩa “đã đúng với sổ cũ”.

---

## 3. Đã chốt — đang chạy 11/11/2026

### 3.1 Ba chương trình, một PC

CANcomp chạy cả ba. MinhComp chỉ lập trình.

| Việc | Một chỗ |
|---|---|
| Nghe Kingbird, lọc kg, chụp cam, SQLite phiếu xe, đẩy mill | BM Auto Cân Desktop |
| Đọc biển trên ảnh | BM-OCR, `127.0.0.1:8765/read`, không ghi database |
| Nghe máy bột, chấm điểm, sổ thử điểm | BM-ThuDiem |
| Đưa điểm lên mill | BM-ThuDiem thả file, AutoCan gửi. ThuDiem không tự POST |
| Phiên, sổ ngày trên web | Mill |
| Sổ pháp lý sau cổng 1% | `binhminh_data`, chỉ mill ghi |
| Căn thanh toán hôm nay | Sổ cũ |

AutoCan **không** mở COM4. BM-ThuDiem **không** mở COM5.

### 3.2 Dây và cổng

Quyết 15/09/2026 còn hiệu lực: không cài phần mềm mới lên máy sổ cũ, không cắt COM1 của sổ cũ, không nối chung TX của hai máy, TX của CANcomp không nối lên đầu cân.

| Cổng trên CANcomp | Thiết bị | Ai được mở |
|---|---|---|
| COM5 | Kingbird, tap OUTPUT2 của DTECH từ COM2 đầu cân. 1200 8N1. DTR tắt, RTS tắt. Không gửi một byte. | Chỉ AutoCan |
| COM4 | Máy bột, USB-RS232, khung `NNNNNN=` gram viết ngược. 1200 8N1. DTR tắt, RTS tắt. | Chỉ BM-ThuDiem |

Cắm nhầm hai cổng vật lý đã làm mất một phiên cân. Phần mềm không tự đoán cổng.

### 3.3 Cân xe

Đầu cân Kingbird, fact no KTGN-T100-078, serial B231161076.

| | Đã chốt |
|---|---|
| Khung | Sáu chữ số là kg. Ví dụ `.10 057340…` = 57340 kg. |
| Cửa | **3,0 giây**. ε **20 kg**. |
| Sàn | Dưới 80 kg bỏ. Dưới 400 kg không phải đỉnh xe. Trần 120000 kg. |
| Một lượt | Cửa yên đầu tiên. Trung bình các mẫu trong cửa, rồi làm tròn kg. Không phát phiếu thứ hai cho đến khi xe rời bàn. |

Chưa đủ phiếu đối chiếu thì không đổi công thức này.

### 3.4 Điểm bột

Máy bột không gửi sẵn phần trăm. BM-ThuDiem 1.2.0:

| | Đã chốt |
|---|---|
| Khô | Mẫu gần **5000 g** nhất trong khoảng 4200–5800 g. 5004 được chọn hơn 5008. |
| Ướt | Cao nguyên thấp sau khi nhúng, thường **300–700 g**. Phụ lục của mẫu đúng 5 kg là **280 g = 10,0%** đến **670 g = 30,0%**. Chương trình nhận 150–1200 g và lấy trung vị. |
| Công thức | `ướt đối chiếu = 5000 × ướt / khô`, rồi tra Phụ lục 1 của Quyết định 228/1999. 522 g là 22,4%, không phải 24,4%. |
| Cấm | Không tính điểm bằng khô trừ ướt. Không hủy phiếu chỉ vì nước rung quá 12 g. |
| Đóng phiên | Cân dưới 100 g liên tục 1 giây. Có cả khô và ướt thì ghi. Chưa có ướt thì không ghi. |
| Sổ | `thudiem.db`, tách khỏi `cancomp.db`. Trần 500 MB, quá thì xóa phiếu cũ. Không lưu từng khung COM. |

Bột không chặn phiếu kg. Chưa đối đủ với đèn máy bột thì chưa gọi là đúng.

### 3.5 Ảnh và biển

Khi kg khóa, AutoCan chụp ba camera Dahua (F, R, S), ghép một JPEG, rồi đưa **từng ảnh một** cho BM-OCR. Ảnh sau nằm trong hàng đợi đến khi ảnh trước trả ok, nghi hoặc Total fail. Kg không chờ biển.

BM-OCR: YOLOv8 khoanh, PaddleOCR đọc, luật cũ `decide()` vẫn chạy trước. Nhánh `ocr/branch.py` chỉ sửa khi chữ trên ảnh khớp một biển đủ dạng.

| Được | Không được |
|---|---|
| Ghép mảnh của cùng một biển (`70H` + `071.93`) | Bịa chữ cái khi Paddle mất chữ (`510` + `319.46` vẫn Nghi) |
| Đưa `L7OR` + `010.88` thành remooc `70R-010.88`, phiếu Nghi | Biến chữ thừa ở đầu thành mã tỉnh `17OR` rồi gọi OK |
| Để Nghi khi cùng lúc có `70` và `20` | Đổi 7 thành 2 |
| Tắt nhánh bằng `BM_PLATE_BRANCH=0` | Sửa `decide()` để “đoán thêm” |

Log có `[goc]`, `[nhanh]` hoặc `[tat]`.

Đọc AI (Gemini, nút tay, tối đa 5 ảnh Nghi hoặc Total fail, độ chắc từ 70%) không thay BM-OCR và không chạy nền.

Admin sửa phiếu Nghi bằng PIN là đường tạm. Phiếu OK không mở để gõ biển.

### 3.6 App

- WinForms, .NET 8. Không chuyển WPF khi chưa đủ 20 lượt kg khớp sổ.
- Một process AutoCan. Đóng cửa sổ hỏi PIN.
- SQLite phiếu xe ưu tiên `C:\ProgramData\BmCancomp\data\cancomp.db`. Xóa phiếu theo ngày thì xóa cả ảnh của ngày đó, có PIN.
- Mất mạng vẫn giữ phiếu. CANcomp không ghi `binhminh_data`.
- Không commit `STATION_KEY`.

---

## 4. Đã xử lý — đừng làm lại

| Việc | Cách đang giữ |
|---|---|
| BM-OCR kẹt `attempt to write a readonly database`, hai xe trong một phút thì pending mãi | OCR chỉ đọc ảnh. Desktop là chỗ duy nhất ghi `cancomp.db`. Một ảnh một lượt. |
| Cắm và lập trình nhầm COM4 với COM5, mất một phiên cân xe | COM5 chỉ AutoCan. COM4 chỉ BM-ThuDiem. |
| Thử điểm không ra phiếu vì nước rung quá 12 g | 1.2.0 lấy trung vị cao nguyên thấp rồi mới cần cân về 0. |
| Biển giả từ chữ thừa (`17OR-010.88`) và mảnh của cùng một biển bị gọi là hai biển | Nhánh riêng. Luật cũ còn nguyên để tắt được. |
| File thử điểm bị từ chối quyền ở ProgramData | Thả phiếu qua LocalAppData cho AutoCan gửi. |
| Phiên có kg mà không có ảnh | Lần 11/11, ping camera `192.168.100.101` và `.102` trả Destination host unreachable từ máy `.20`. Sửa dây và hub trước khi sửa code chụp. |

---

## 5. Chưa đạt

Không đánh dấu xong.

- [ ] Khoảng 20 lượt kg: mặt Kingbird, số đã khóa, sổ cũ, cùng một xe. Lệch thì sửa cửa hoặc ε, không thêm tính năng.
- [ ] Vài mẫu bột trên 1.2.0 đối với đèn máy bột. Bốn nhịp 11/11 bị rơi là bản cũ, chưa phải bằng chứng bản mới.
- [ ] Biển ban đêm và biển mất một chữ vẫn ra đúng mà không đoán. Nhánh 0.18.44 cố ý để Nghi những ca đó.
- [ ] Camera trả lời ping ổn định rồi mới xét lại code chụp.
- [ ] Đếm phiếu “Đã sửa” và “Read AI”. Nếu đường vá đông hơn đường tự động thì OCR chưa đạt mục 3.
- [ ] Ít nhất 30 ngày lịch lệch dưới 1% với sổ cũ, cả ngày củ mì và ngày hàng khác.
- [ ] Sau cổng đó, mill và `binhminh_data` là sổ. Sổ cũ cất. Hết ô gõ biển.

---

## 6. Cố ý không làm

- Màn phụ tài xế, tablet, barrier, RFID.
- Viết lại PostgreSQL từ app.
- Cài bất cứ thứ gì lên máy sổ cũ.
- MQTT song song HTTPS.
- WPF, hoặc thay app COM bằng trang web.
- Giữ xe vì chưa có ảnh hoặc chưa đọc được biển.
- Người cân sửa ε, cổng, hoặc khóa trạm.
- Đoán biển khi thiếu chữ cái.
- Để AutoCan và BM-ThuDiem cùng mở một cổng COM.
- Để BM-OCR ghi SQLite.

---

## 7. Sửa ở đâu

Sửa luật kg thì sửa AutoCan và ghi lại whitepaper trong ngày.  
Sửa chấm điểm thì chỉ sửa repo BM-ThuDiem.  
Sửa ghép biển thì sửa `ocr/branch.py`, không sửa `decide()` trừ khi luật cũ đang sai một ca đã có ảnh chứng.  
Sửa màu mill thì không phát hành lại exe.

*Hết whitepaper 11/11/2026. Đích vẫn là bốn câu ở mục 1.*
