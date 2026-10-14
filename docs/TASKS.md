# Việc tiếp theo — theo whitepaper 09/10/2026

Căn cứ: [WHITEPAPER.md](../WHITEPAPER.md) mục 5 “Chưa đạt”. File này thay danh sách 10 việc tháng 9 (cửa 2 giây, mock xe đồ chơi, máy bột gửi sẵn `%`) — đó là hướng cũ.

Issue cũ [#2](https://github.com/nguyenmian3012-code/BM_Truck_Auto_Weight/issues/2)–[#11](https://github.com/nguyenmian3012-code/BM_Truck_Auto_Weight/issues/11) viết theo bản 12/09. Đọc để tra lịch sử, không làm theo.

Hướng camera đồ chơi, xe đồ chơi, mock cam, mock cân **đã bỏ hẳn** (14/10/2026). Không làm lại.

Luật số đang chạy nằm ở app BM Auto Cân Desktop trên CANcomp. Chưa đủ phiếu đối chiếu thì **không** đổi công thức kg hay bột.

## Trạng thái 14/10/2026

- App desktop: **v0.15.1** (commit `66772bb`, 12/10) — mỗi lần cân là một phiếu đơn; phiên vào/ra thuộc trang canxe.
- Ingest: Worker `POST /api/ingest` **đã deploy**, chưa chạy thật vì **chưa lắp cam thật** tại cầu cân. Xem [INGEST.md](./INGEST.md).

## Ưu tiên 1 — tối ưu app desktop

| # | Việc | Xong khi |
|---|---|---|
| 1 | Tối ưu BM Auto Cân Desktop, mốc gốc v0.15.1 | Bản mới chạy trên CANcomp, luật kg và bột không đổi |

## Ưu tiên 2 — lắp cam thật, chạy ingest thật

| # | Việc | Xong khi |
|---|---|---|
| 2 | Gắn cam tại cầu cân, có ảnh xe thật | Ảnh xe thật về đúng phiếu |
| 3 | Chạy `POST /api/ingest` thật: từ chối request không `X-Station-Key`, đọc đúng `kg` hoặc `starchPct` | Phiếu thật lên mill. CANcomp không ghi `binhminh_data` |

## Sau đó — các dòng “Chưa đạt” còn lại của whitepaper

| # | Việc | Ghi chú |
|---|---|---|
| 4 | Khoảng **20 lượt xe thật**: mặt Kingbird, số đã khóa trong app, sổ cũ — cùng một xe | Lệch thì sửa cửa hoặc ε, không thêm tính năng |
| 5 | **Vài mẫu bột** đủ chu kỳ khô rồi ướt, đối điểm trong app với đèn máy bột | Bột không chặn phiếu kg |
| 6 | Bật khóa trạm production | Chỉ sau khi bảng 20 lượt sạch. Xóa phiếu thử bằng PIN trước lần đẩy thật |
| 7 | OCR biển trên mill | Khớp trước/sau từ 95% thì điền và khóa; dưới 95% thì pending. Không ô gõ biển. Không OCR trên CANcomp |
| 8 | Một JPEG đi cùng mã phiếu lên mill | Kg không chờ ảnh |
| 9 | Song song sổ cũ ít nhất **30 ngày lịch**, lệch **dưới 1%** | Có ngày củ mì và ngày hàng khác nếu nhà máy cân những hàng đó |
| 10 | Sau cổng 1%: mill và `binhminh_data` là sổ, sổ cũ cất | Ô biển và ô điểm vẫn không gõ tay |

Ngày 15/10: **#1**. Không đánh dấu dòng nào là xong khi chưa có bằng chứng vận hành.
