# Màn tài xế và đèn cột

Nhánh riêng. Chưa gắn vào app cân đang chạy, chưa đẩy lên web.

## Màn hình

Tivi mở Chrome, hoặc máy cân mở trang rồi cast tab sang Chromecast. Trang ở máy cân, cổng 8770, để đồng hồ 4 giây không chờ internet.

Bấm đúp `Mo-man-tai-xe.bat`. Dòng in ra có địa chỉ WiFi. Chromecast chỉ chiếu tab của máy đang mở trang.

Xe chưa nối thì xem thử: `python bay.py --demo`.

## Đèn cột

Hộp riêng. Chỉ cắm 24V. WiFi. Không dây tín hiệu về máy cân.

Firmware `firmware/tower/tower.ino` chạy trên ESP32. Sửa bốn dòng đầu: tên WiFi, mật khẩu, IP máy cân, cổng 8770. Nguồn 24V qua mạch hạ 5V nuôi board. Bốn relay bật đèn đỏ, vàng, xanh và còi. Hết liên lạc quá 2 giây thì tắt hết.

## Đèn

| Lúc | Màn | Đèn |
|---|---|---|
| Cân về 0, dưới 200 kg | Sẵn sàng | Tắt hết |
| Xe đang lên, số kg còn tăng | Vào chậm | Vàng |
| Đã đứng, từ 2.000 kg | Giữ yên, đếm 4 giây | Đỏ |
| Hết 4 giây, đang đọc biển | Đang xử lý | Đỏ |
| Có biển | Được đi, hiện biển, kg, khách, luồng, vào/ra | Xanh, còi kêu khoảng 1 giây |
| Không đọc được sau 8 giây | Xuống xe, báo văn phòng | Đỏ, không còi |
| Số kg bắt đầu giảm | Đang rời | Xanh tắt, vàng khoảng 3 giây rồi tắt, tới khi về 0 |
| Văn phòng sửa xong và app gửi lại biển | Được đi | Xanh và còi |

App cân hiện chụp sau 3 giây đứng yên. Màn này đếm 4 giây. Khi nối thật, app phải chụp đúng lúc đếm về 0. Việc nối là bước sau, không nằm trong bản đang cân hôm nay.

App gửi vào `POST /scale` khoảng 5 lần một giây:

```json
{"kg": 18600, "plate": "", "ocr": "pending", "customer": "", "card": "", "visit": ""}
```

`ocr` là `ok`, `pending` hoặc `bad`. `card` là `nhap_mi`, `xuat_bot` hoặc `khac`. `visit` là `vao` hoặc `ra`.
