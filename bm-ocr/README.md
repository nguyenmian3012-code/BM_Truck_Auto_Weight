# BM-OCR

Trang theo dõi trên máy cân. Một danh sách lượt trong ngày, ảnh cạnh biển máy đọc được. Lượt sót ảnh, không đọc được, biển sai dạng, hoặc hai camera không khớp nằm trong khung ngoại lệ.

Không thay BM Auto Cân. Không đụng trang web. Sửa biển thì ghi vào sổ cân sẵn có; app đang mở sẽ gửi lên web trong vài giây.

## Chạy

Chép cả thư mục `bm-ocr` vào máy cân. BM Auto Cân đang mở. Bấm đúp `BM-OCR.bat`. Trình duyệt mở `http://127.0.0.1:8771/`.

- Đúng: giữ biển đang hiện.
- Sai, ghi biển này: gõ biển đúng rồi bấm.
- Đọc lại: hỏi bộ đọc ở cổng 8765 bằng ảnh gốc F, R, S. Biển mới khác biển đã lưu thì thành ngoại lệ, không tự ghi đè.

Chỉ nghe máy cân. Máy khác trong mạng không mở được.
