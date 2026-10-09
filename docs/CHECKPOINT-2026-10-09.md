# Checkpoint 09/10/2026

Đóng mốc thử cam trên bàn. Chưa lắp thực địa. Đèn và OCR để sau khi có ảnh xe thật.

## Gói phần mềm

- Repo: BM_CANXE_SOFT_CANcomp
- Mốc: v0.14.5, commit d4adda1
- Tải: https://github.com/nguyenmian3012-code/BM_CANXE_SOFT_CANcomp/releases/tag/v0.14.5
- Đang chạy trên CANcomp: nghe hai cân, cao nguyên 3 giây, SQLite, ảnh local ghép F+R trên và S dưới.
- Tên ảnh tự động: thu-ngày-giờ-Vao hoặc Ra, không dấu.
- Chưa gửi ảnh lên /api/ingest.

## Cam, tạm khóa

- Ba con DH-IPC-HFW2449T-AS-IL: .101 F, .102 R, .103 S.
- Trạng thái nghỉ đã khóa: WhiteMode, hồng ngoại Manual và sáng 0, đèn ấm tắt, đèn trộn tắt, hình màu.
- Firmware không nhận Mode=Off cho hồng ngoại.
- Ảnh che vải lúc 12:21 vẫn tím. Chưa chứng minh đèn ấm bật đúng lúc thiếu sáng.
- Quay lại khi cam gắn tại cầu cân và có ảnh xe thật.

## Việc chính trở lại

1. Đối 20 lượt kg và vài phiếu bột với sổ cũ.
2. Worker nhận POST /api/ingest trước khi bật khóa production.
3. Song song sổ cũ ít nhất 30 ngày. Lệch dưới 1% mới là căn thanh toán.
4. Không ghi binhminh_data. Không OCR trên CANcomp.
