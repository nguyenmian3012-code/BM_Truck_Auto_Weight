# Việc tiếp theo — theo whitepaper 11/11/2026

Căn cứ: [WHITEPAPER.md](../WHITEPAPER.md) mục 1 và mục 5.  
Issue [#2](https://github.com/nguyenmian3012-code/BM_Truck_Auto_Weight/issues/2)–[#11](https://github.com/nguyenmian3012-code/BM_Truck_Auto_Weight/issues/11) là hàng tháng 9. Không làm theo.

## Đang chạy

| Chương trình | Bản | Việc |
|---|---|---|
| BM Auto Cân Desktop | 0.18.44 | COM5, phiếu kg, camera, đẩy mill |
| BM-OCR | 0.18.44 | Đọc biển tại máy, không ghi database |
| BM-ThuDiem | 1.2.0 | COM4, điểm bột, sổ riêng |

## Đã xong trong mã — chưa phải cổng 1%

Những dòng này đã có trong bản đang phát hành. Không làm lại. Cũng không gọi là đã đối sổ.

| # | Việc |
|---|---|
| A | Tách điểm bột sang repo [BM-ThuDiem](https://github.com/nguyenmian3012-code/BM-ThuDiem). AutoCan không mở COM4. |
| B | OCR một ảnh một lượt, chỉ `/read`. Hết vòng `readonly database`. |
| C | Nhánh đọc biển riêng. Tắt bằng `BM_PLATE_BRANCH=0`. Không đoán chữ cái bị thiếu. |
| D | ThuDiem 1.2.0 không hủy phiếu chỉ vì nước rung. Cột giờ, vạch ngày, biểu đồ 10 phiên, nút Clear, trần db 500 MB. |
| E | Đọc AI và sửa tay chỉ là đường vá cho phiếu Nghi hoặc Total fail. |

## Việc kế — cần bằng chứng trên máy, không cần thêm tính năng

| # | Việc | Xong khi |
|---|---|---|
| 1 | Chạy ThuDiem 1.2.0 một ca thật | Mỗi nhịp trên biểu đồ có khô quanh 5000 g và ướt khoảng 300–700 g thì có một dòng, có giờ, khớp đèn máy bột |
| 2 | 20 lượt xe | Mặt Kingbird, số đã khóa, sổ cũ, cùng một xe. Lệch thì sửa cửa 3 giây hoặc ε 20 kg, không thêm màn hình |
| 3 | Camera | `ping 192.168.100.101` và `.102` phải có reply từ chính camera, không phải “Destination host unreachable”. Rồi mới chụp thử |
| 4 | Biển | Ca đêm và ca mất chữ vẫn để Nghi nếu ảnh không đủ chữ. Chỉ siết nhánh khi có ảnh chứng minh luật cũ hoặc nhánh mới ghép sai |
| 5 | Đếm đường vá | Trong một tuần, số phiếu OK tự động nhiều hơn số phiếu Đã sửa và Read AI cộng lại |

## Sau khi 1–5 có số

| # | Việc | Xong khi |
|---|---|---|
| 6 | Khóa trạm production | Sau bảng 20 lượt sạch. Xóa phiếu thử bằng PIN trước lần đẩy thật |
| 7 | 30 ngày lịch lệch dưới 1% với sổ cũ | Có ngày củ mì và ngày hàng khác |
| 8 | Mill và `binhminh_data` thành sổ | Sổ cũ cất. Hết ô gõ biển trên bàn sản xuất |

Không đánh dấu dòng 1–8 khi chưa có phiếu đối chiếu.
