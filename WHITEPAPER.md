# BM Cân Xe Tự Động — Whitepaper

Phiên bản **09/10/2026**. Thay bản 12/09/2026.  
Nhà máy tinh bột khoai mì Bình Minh.  
Phần mềm đang chạy: [BM Auto Cân Desktop](https://github.com/nguyenmian3012-code/BM_CANXE_SOFT_CANcomp) **0.14.3**, máy CANcomp.  
Mill: [canxe.redtigerhead.com](https://canxe.redtigerhead.com).  
Bản đồ dây và máy: [docs/HE-THONG-CAN-XE-BINH-MINH.md](docs/HE-THONG-CAN-XE-BINH-MINH.md).

Bản 12/09 viết trước khi nghe được khung tin thật. Nhiều đoạn của bản đó là **cách thử**, không phải mục tiêu. File này chỉ giữ mục tiêu, ghi cách làm đã đo và đang chạy, và bỏ cách thử không còn đúng.

Khi một file khác trong repo còn nói cửa 2 giây, ảnh xám 640 px, hoặc điểm bột là một khung `%` sẵn: đó là hướng cũ. Luật số đang chạy nằm ở app 0.14.3. Cổng “đã xong cả hệ thống” vẫn là mục dưới, chưa đạt.

---

## 1. Mục tiêu — không đổi

Bốn câu này là đích. Đổi cách làm được. Bỏ bốn câu này thì không còn là dự án này.

1. **Tự động.** Xe lên bàn thì ra một phiếu kg. Mẫu củ mì thì ra một điểm bột. Không bấm để chốt số. Không gõ kg, không gõ điểm, không gõ biển trên bàn sản xuất.
2. **Đúng.** Số đã khóa là số của lần đứng yên, không phải số đang nhảy. Đúng nghĩa là khớp sổ cũ đang dùng để thanh toán, không phải khớp một công thức tự đặt.
3. **Không bị người sửa phiếu.** Biển chỉ từ ảnh. Điểm chỉ từ máy bột. Phiếu đã khóa không sửa. Người cân không đụng ε, cổng, hay khóa trạm.
4. **Ít máy, chạy nền, ít bảo trì.** Một PC nghe. Một SQLite. Một đường HTTPS. Một mill. Một cửa sổ, mở cùng Windows. Không thêm kênh sync, không OCR hai nơi, không cài lên máy sổ cũ.

**Cổng ra, chưa đạt:** chạy song song sổ cũ ít nhất **30 ngày lịch**, tỷ lệ phiếu lệch **dưới 1%**. Trước cổng đó, sổ cũ là căn thanh toán. Sau cổng đó, mill và `binhminh_data` mới là sổ. Sổ cũ cất.

Không có barrier, không giữ xe vì thiếu ảnh hoặc thiếu biển.

---

## 2. Ba lớp chữ, đừng trộn

| Lớp | Nghĩa | Ví dụ |
|---|---|---|
| Mục tiêu | Còn khi cách làm đổi | Một số kg đã khóa cho một lượt xe. Biển không gõ tay. |
| Đã chốt | Cách làm đang nằm trong app 0.14.3, đã đo trên máy thật | Cửa cân 3 giây. Gram bột viết ngược. |
| Chưa đạt | Mục tiêu còn đó, chưa có bằng chứng vận hành | 30 ngày lệch dưới 1%. OCR biển. |

“Đã chốt” không có nghĩa “đã đúng với sổ cũ”. Có những luật đã khóa trong mã vì đo khung tin ra như vậy, nhưng phiếu kg và điểm bột **chưa** được đối đủ với sổ cũ và đèn máy bột.

---

## 3. Đã chốt

### 3.1 Máy và dây — pass kiến trúc

Quyết 15/09/2026 còn hiệu lực.

- Không cài phần mềm mới lên máy sổ cũ. Không cắt COM1. Không nối chung TX của hai máy.
- CANcomp là PC riêng. Nghe nhánh OUTPUT2 của DTECH từ COM2 Kingbird. TX của CANcomp không nối lên đầu cân.
- Máy bột cắm thẳng USB-RS232, không qua DTECH.
- MinhComp chỉ là máy lập trình, không phải máy vận hành.
- `stationId` trên CANcomp: `BinhMinh-CanXe`.

### 3.2 Cân xe — pass luật đang chạy, chưa pass đối sổ

Đầu cân: Mettler Toledo Kingbird, fact no KTGN-T100-078, serial B231161076.

| | Đã chốt |
|---|---|
| Nghe | Listen-only. 1200 8N1. DTR tắt, RTS tắt. Không gửi một byte. |
| Khung | Sáu chữ số là kg. Ví dụ `.10 057340…` = 57340 kg. |
| Cửa | **3,0 giây**. ε **20 kg**. Nâng từ 2 giây ngày 29/09/2026 vì gần sổ cũ hơn. |
| Sàn | Dưới 80 kg bỏ. Dưới 400 kg không phải đỉnh xe. Trần 120000 kg. |
| Một lượt | Cửa yên đầu tiên. Trung bình các mẫu trong cửa, rồi làm tròn kg. Không phát phiếu thứ hai cho đến khi xe rời bàn. |
| Số lưu | Kg trên phiếu là trung bình cửa đó. Cột raw là khung gây khóa, không phải trung bình. Màn live vẫn chạy tiếp sau khi khóa. |

Ba số có thể lệch nhau trong lúc xe còn trên bàn: số đang hiện, số đã khóa, và khung raw. Đó không phải lỗi hiển thị. Chưa đủ phiếu đối chiếu thì **không** đổi công thức này.

### 3.3 Điểm bột — pass luật đang chạy, chưa pass đối đèn

Máy bột không gửi sẵn một số phần trăm.

| | Đã chốt 29/09/2026, luật cuối từ 30/09 |
|---|---|
| Cổng | 1200 8N1. DTR tắt, RTS tắt. Không 7N1, không software flow. |
| Khung | `NNNNNN=` là gram **viết ngược**. `040500=` = 5040 g. `075000=` = 570 g. `000000=` = 0. |
| Khô | Không lấy mức ổn định đầu. Lấy mức ổn định **cuối** trước khi số rơi. Mẫu hợp lệ khoảng 5000 g (cửa đang dùng 4000–6500 g). Nhân viên có thể cho thừa rồi bớt, hoặc cho thiếu rồi thêm. |
| Ướt | Mức ổn định **cuối** sau khi nhúng. |
| Tra bảng | Quy về 5000 g rồi tra Phụ lục Quyết định 228. Nếu chuỗi 2 vẫn là số lớn, cân ướt = khô − chuỗi 2. |
| Hai dòng | Gram khô chỉ ở máy (`source` kho, không đẩy). Điểm bột là phiếu `starch`. |

Bột không chặn phiếu kg.

### 3.4 App trên CANcomp — pass phần mềm nền

BM Auto Cân Desktop, C# / .NET 8, WinForms. Không chuyển WPF trước khi đủ đối soát kg.

- Một process. Mở lần hai thì đưa cửa sổ cũ lên.
- Mở cùng đăng nhập Windows.
- Đóng hoặc dừng nghe thì hỏi PIN. Người cân không vào ε, cổng, khóa trạm.
- SQLite ưu tiên `C:\ProgramData\BmCancomp\data\cancomp.db`. Phiếu không xóa theo ngày. Raw RS232 chỉ giữ 2 ngày.
- Lưới chính là 50 phiếu mới. Phiếu cũ: nút Tìm phiếu, xuất CSV.
- Mất mạng vẫn giữ phiếu. Hàng đợi kg và điểm nằm local cho đến khi mill trả 2xx.
- Khóa trạm để trống. Chưa đẩy production.

### 3.5 Ảnh — pass mã local, chưa pass vận hành

Trong 0.14 đến 0.14.3, app **có** đường chụp. Trong cấu hình gửi kèm repo, camera đang **tắt**.

Khi bật, lúc kg vừa khóa:

- Ba camera Dahua, làn F / R / S, CGI, đăng nhập Digest.
- Đèn trắng một mức cố định trong lúc chụp. Tắt hồng ngoại. Giữ màu. Không đoán trời tối để quyết định đèn.
- Một JPEG: CAN_F và CAN_R hàng trên, CAN_S hàng dưới rộng bằng hai ảnh trên. Cắt viền đen. Không lưu ba file gốc làm hồ sơ.
- Tên file `thu-yyyyMMdd-HHmmss-Vao` hoặc `Ra`. Phiếu vẫn giữ mã riêng.
- Chữ Vào/Ra trên phiếu và trên tên file là **lần lượt xen kẽ**, không phải xe vào hay xe ra thật.
- Ảnh không chặn phiếu kg. Không OCR trên CANcomp. Không đẩy ảnh lên mill.

---

## 4. Hướng đầu đã điều chỉnh

Giữ mục tiêu ở cột phải. Bỏ cách làm ở cột trái.

| Hướng 12/09 | Điều chỉnh | Mục tiêu vẫn giữ |
|---|---|---|
| Cửa ổn định 2,0 giây, ε 20 kg là số khởi điểm | Cửa **3,0 giây** từ 29/09. ε 20 kg giữ. | Một số cho một lượt, chỉ khi đã đứng yên. |
| Dùng bit STABLE của đầu cân nếu có | Kingbird đang spew kg. App tự tính cửa. Không điều khiển đầu cân. | Nguồn kích là cân, không phải hình. |
| Máy bột gửi sẵn `starchPct` | Khung thật là gram viết ngược, rồi bảng 228, lấy mức cuối mỗi chuỗi | Điểm chỉ từ máy, không ô nhập. |
| Quét baud từ 9600 8N1 | Cả hai cổng chốt **1200 8N1**. Bột phải tắt DTR/RTS. | Nghe đúng khung, không bịa protocol. |
| Ảnh xám, cạnh ~640 px, OCR ngay sau 2 giây | Một JPEG màu ghép ba camera. OCR để sau, trên mill, cùng mã phiếu. | Biển sau này chỉ từ ảnh. Ảnh gắn với phiếu kg đã khóa. |
| Cam thứ ba chỉ khi hai biển lệch | Cam sườn nằm trong ảnh ghép ngay từ đầu. Nhánh “pending vì lệch biển” vẫn chưa làm. | Không mở phiên khi biển chưa đáng tin. |
| Mock-up xe đồ chơi là cổng bắt buộc trước thiết bị thật | Đường đang chạy là nghe máy thật trên CANcomp. Thư mục `cancomp-agent/` và `src/lib/hw/` là nháp, không cài. | Cùng một phiếu cho vận hành. Không thêm nhánh “nếu demo thì…”. |
| Cột vào/ra trên app là phiên IN/OUT | App chỉ đếm xen kẽ để khỏi trống cột. Phiên thật chỉ mở khi đã có biển. | Không mở phiên từ kg trần. |
| Chụp vì thấy xe đứng trong hình | Cấm. Chỉ chụp sau khi kg đã khóa. | Kg là số liệu của phiếu. |

---

## 5. Chưa đạt

Những dòng này còn là mục tiêu. Không đánh dấu xong.

- [ ] Khoảng 20 lượt kg: mặt Kingbird, số đã khóa trong app, và sổ cũ là cùng một xe. Lệch thì sửa cửa hoặc ε, không thêm tính năng.
- [ ] Vài mẫu bột đủ chu kỳ khô rồi ướt, đối với đèn điểm trên máy bột.
- [ ] Worker có `POST /api/ingest`, từ chối request không `X-Station-Key`, đọc đúng `kg` hoặc `starchPct`. CANcomp không ghi `binhminh_data`.
- [ ] Khóa trạm production chỉ bật sau khi bảng 20 lượt sạch. Xóa phiếu thử bằng PIN trước lần đẩy thật, để hàng cũ không bị đẩy nhầm.
- [ ] OCR biển trên mill, khớp trước/sau từ 95% thì điền và khóa. Dưới 95% thì pending. Không ô gõ biển.
- [ ] Phiên vào/ra chỉ khi biển đáng tin.
- [ ] Ảnh một JPEG đi cùng mã phiếu lên mill. Kg không chờ ảnh.
- [ ] Ít nhất 30 ngày lịch lệch dưới 1% với sổ cũ. Mẫu phải có ngày củ mì và ngày hàng khác nếu nhà máy cân những hàng đó.
- [ ] Sau cổng 1%, mill và `binhminh_data` là sổ. Sổ cũ cất. Ô biển và ô điểm vẫn không gõ tay.

---

## 6. Cố ý không làm

- Màn phụ tài xế, tablet, barrier, RFID.
- Viết lại PostgreSQL.
- Cài bất cứ thứ gì lên máy sổ cũ.
- MQTT song song với HTTPS.
- WPF, trang web thay cho app COM, OCR ngay trên CANcomp.
- Giữ xe vì chưa có ảnh hoặc chưa đọc được biển.
- Người cân sửa ε, cổng, hoặc khóa trạm.

---

## 7. Hệ thống mỏng

Đúng hướng bền khi mỗi việc chỉ có một chỗ:

| Việc | Một chỗ |
|---|---|
| Nghe COM, lọc, lưu, chụp local | BM Auto Cân Desktop trên CANcomp |
| Phiên, biển, sổ ngày | Mill trên canxe |
| Sổ pháp lý sau cổng 1% | `binhminh_data`, chỉ mill ghi |
| Căn thanh toán hôm nay | Sổ cũ |

Sửa luật kg hoặc điểm bột thì sửa app và ghi lại bản đồ hệ thống trong cùng ngày. Sửa màu mill thì không phát hành lại exe.

---

*Hết whitepaper 09/10/2026. Bản 12/09 không còn là hướng triển khai.*
