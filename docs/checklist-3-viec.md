# Checklist 3 việc chính — CANcomp

Theo [whitepaper 09/10/2026](../WHITEPAPER.md), mục 5 “Chưa đạt”. In ra, đánh ✓ từng dòng.

Dây và cổng đã chốt (whitepaper 3.1): CANcomp nghe nhánh OUTPUT2 DTECH từ COM2 Kingbird, listen-only. Máy bột cắm thẳng USB-RS232. Cả hai cổng **1200 8N1**, DTR tắt, RTS tắt. Không cài gì lên máy sổ cũ, không cắt COM1, không gửi byte lên đầu cân.

Bản trước của checklist này (dò baud, cửa 2 giây, đọc `%` sẵn từ máy bột) là hướng cũ.

---

## Việc A — Đối kg: khoảng 20 lượt xe thật

Mục tiêu: số đã khóa trong app khớp mặt Kingbird và sổ cũ, cho cùng một xe.

Luật đang chạy (không đổi trong lúc đối): cửa **3,0 giây**, ε **20 kg**. Dưới 80 kg bỏ, dưới 400 kg không phải đỉnh xe, trần 120000 kg. Kg trên phiếu là trung bình cửa yên đầu tiên, làm tròn kg. Một phiếu cho một lượt, đến khi xe rời bàn.

### A1. Trước ca

- [ ] App trên CANcomp đang nghe cân, cửa sổ mở
- [ ] Sổ cũ chạy bình thường — sổ cũ vẫn là căn thanh toán

### A2. Mỗi lượt xe

- [ ] Ghi số đứng yên trên mặt Kingbird
- [ ] Ghi số đã khóa trong app (không phải số live, không phải cột raw)
- [ ] Ghi số sổ cũ cho cùng xe

| # | Giờ | Kingbird | App đã khóa | Sổ cũ | Khớp? |
|---|---|---|---|---|---|
| 1 |  |  |  |  |  |
| … |  |  |  |  |  |
| 20 |  |  |  |  |  |

Lưu ý: số đang hiện, số đã khóa và khung raw có thể lệch nhau khi xe còn trên bàn. Đó không phải lỗi hiển thị. Chỉ so số đã khóa.

### A3. Xử lý lệch

- [ ] Lệch thì sửa cửa hoặc ε, không thêm tính năng
- [ ] Sửa luật kg thì sửa app và ghi lại bản đồ hệ thống trong cùng ngày
- [ ] **A xong** khi bảng khoảng 20 lượt sạch

---

## Việc B — Đối bột: vài mẫu với đèn máy bột

Mục tiêu: điểm bột trong app khớp đèn điểm trên máy bột. Làm sau A, hoặc song song khi chờ xe.

Luật đang chạy: khung `NNNNNN=` là gram viết ngược. Khô lấy mức ổn định **cuối** trước khi số rơi (cửa 4000–6500 g, mẫu khoảng 5000 g). Ướt lấy mức ổn định **cuối** sau khi nhúng. Quy về 5000 g rồi tra Phụ lục Quyết định 228.

### B1. Mỗi mẫu

- [ ] Cân khô đủ chu kỳ (cho thừa rồi bớt, hoặc thiếu rồi thêm — đều được)
- [ ] Cân ướt sau khi nhúng
- [ ] Ghi điểm trên đèn máy bột và điểm trong app (phiếu `starch`)

| # | Giờ | Đèn máy bột | App | Khớp? |
|---|---|---|---|---|
| 1 |  |  |  |  |
| … |  |  |  |  |

- [ ] **B xong** khi vài mẫu đủ chu kỳ khô rồi ướt đều khớp đèn

Bột không chặn phiếu kg.

---

## Việc C — Sau khi A sạch

- [ ] Worker có `POST /api/ingest`, từ chối request không `X-Station-Key`, đọc đúng `kg` hoặc `starchPct`
- [ ] CANcomp **không** ghi `binhminh_data`
- [ ] Xóa phiếu thử bằng PIN, rồi mới bật khóa trạm production
- [ ] Song song sổ cũ ít nhất **30 ngày lịch**, lệch **dưới 1%** (có ngày củ mì và ngày hàng khác nếu nhà máy cân)

Để sau, không làm tuần này: OCR biển trên mill (95%), phiên vào/ra, đẩy ảnh lên mill. Không OCR trên CANcomp. Không giữ xe vì thiếu ảnh hoặc biển.

---

## Thứ tự

| Bước | Làm |
|---|---|
| 1 | A: khoảng 20 lượt xe thật, đối ba nguồn |
| 2 | B: vài mẫu bột, đối đèn |
| 3 | C: ingest, khóa production, rồi 30 ngày song song |
