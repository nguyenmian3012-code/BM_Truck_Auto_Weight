# Liên kết phần mềm CANcomp

Người sửa mill đọc file này trước khi đổi đường cân. Ngày cập nhật **11/11/2026**.

| | |
|---|---|
| Phiếu kg, camera, BM-OCR | https://github.com/nguyenmian3012-code/BM_CANXE_SOFT_CANcomp — bản **0.18.44** |
| Điểm bột | https://github.com/nguyenmian3012-code/BM-ThuDiem — bản **1.2.0** |
| Đích và việc còn lại | [WHITEPAPER.md](../WHITEPAPER.md), [TASKS.md](./TASKS.md) |
| Bản đồ | [HE-THONG-CAN-XE-BINH-MINH.md](./HE-THONG-CAN-XE-BINH-MINH.md) |

Ba repo. Repo này giữ mill và whitepaper. Không có đường thứ tư.

## Đừng bỏ sót

| Bạn vừa sửa | Repo nào |
|---|---|
| `POST /api/ingest`, field `kg` hoặc `starchPct`, header `X-Station-Key` | Repo này và `IngestClient.cs` của AutoCan. ThuDiem không tự POST. |
| Cửa 3 giây, ε 20 kg, COM5 | Repo AutoCan. Không đổi khi chưa có bảng đối sổ. |
| Khô, ướt, bảng 228, COM4 | Chỉ repo BM-ThuDiem. |
| Ghép biển | `ocr/branch.py` trong repo AutoCan. `decide()` là đường lùi. |
| Màu mill, sổ ngày trên web | Repo này. Không phát hành lại exe. |

COM5 chỉ AutoCan. COM4 chỉ BM-ThuDiem. BM-OCR không ghi SQLite.

Tìm ngược: cụm `BM_Truck_Auto_Weight` trong hai repo phần mềm.
