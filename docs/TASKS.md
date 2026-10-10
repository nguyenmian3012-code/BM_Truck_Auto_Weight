# Việc tiếp theo — theo whitepaper 09/10/2026

Căn cứ: [WHITEPAPER.md](../WHITEPAPER.md) mục 5 “Chưa đạt”. File này thay danh sách 10 việc tháng 9 (cửa 2 giây, mock xe đồ chơi, máy bột gửi sẵn `%`) — đó là hướng cũ.

Issue cũ [#2](https://github.com/nguyenmian3012-code/BM_Truck_Auto_Weight/issues/2)–[#11](https://github.com/nguyenmian3012-code/BM_Truck_Auto_Weight/issues/11) viết theo bản 12/09. Đọc để tra lịch sử, không làm theo.

Luật số đang chạy nằm ở app BM Auto Cân Desktop trên CANcomp. Chưa đủ phiếu đối chiếu thì **không** đổi công thức kg hay bột.

## Ưu tiên 1 — đối kg

| # | Việc | Xong khi |
|---|---|---|
| 1 | Khoảng **20 lượt xe thật**: mặt Kingbird, số đã khóa trong app, sổ cũ — cùng một xe | Bảng 20 lượt sạch. Lệch thì sửa cửa hoặc ε, không thêm tính năng |

## Ưu tiên 2 — đối bột

| # | Việc | Xong khi |
|---|---|---|
| 2 | **Vài mẫu bột** đủ chu kỳ khô rồi ướt, đối điểm trong app với đèn điểm trên máy bột | Các mẫu khớp đèn |

## Sau đó — theo thứ tự whitepaper

| # | Việc | Ghi chú |
|---|---|---|
| 3 | Worker có `POST /api/ingest`, từ chối request không `X-Station-Key`, đọc đúng `kg` hoặc `starchPct` | CANcomp không ghi `binhminh_data` |
| 4 | Bật khóa trạm production | Chỉ sau khi bảng 20 lượt sạch. Xóa phiếu thử bằng PIN trước lần đẩy thật |
| 5 | OCR biển trên mill | Khớp trước/sau từ 95% thì điền và khóa; dưới 95% thì pending. Không ô gõ biển |
| 6 | Phiên vào/ra | Chỉ khi biển đáng tin |
| 7 | Một JPEG đi cùng mã phiếu lên mill | Kg không chờ ảnh |
| 8 | Song song sổ cũ ít nhất **30 ngày lịch**, lệch **dưới 1%** | Có ngày củ mì và ngày hàng khác nếu nhà máy cân những hàng đó |
| 9 | Sau cổng 1%: mill và `binhminh_data` là sổ, sổ cũ cất | Ô biển và ô điểm vẫn không gõ tay |

Tuần này: **#1 rồi #2**. Không đánh dấu dòng nào là xong khi chưa có bằng chứng vận hành.
