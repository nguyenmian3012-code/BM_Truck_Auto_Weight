# AGENTS.md — BM Cân Xe

Repo này là mill, whitepaper và bản đồ. Không phải phần mềm cổng COM.

Đích không đổi, viết ở [WHITEPAPER.md](WHITEPAPER.md) mục 1:

1. Xe lên bàn thì ra một phiếu kg. Mẫu củ mì thì ra một điểm bột. Không bấm để chốt số.
2. Số khóa phải khớp sổ cũ đang dùng để thanh toán.
3. Biển từ ảnh. Điểm từ máy bột. Người cân không sửa phiếu đã khóa.
4. Một PC, không cài lên máy sổ cũ, không ghi byte lên đầu cân.

Cổng ra: 30 ngày lịch lệch dưới 1%. Chưa tới cổng đó thì sổ cũ vẫn là căn thanh toán.

## Ba repo

| Repo | Được sửa khi |
|---|---|
| Repo này | Mill, whitepaper, task, bản đồ hệ thống |
| [BM_CANXE_SOFT_CANcomp](https://github.com/nguyenmian3012-code/BM_CANXE_SOFT_CANcomp) | Phiếu kg, camera, BM-OCR, COM5 |
| [BM-ThuDiem](https://github.com/nguyenmian3012-code/BM-ThuDiem) | Điểm bột, COM4 |

Sửa luật kg hoặc hợp đồng ingest thì sửa repo phần mềm và whitepaper trong cùng ngày. Sửa điểm bột thì không đụng AutoCan.

## Đừng làm lại

- Không đưa điểm bột trở vào AutoCan.
- Không để hai chương trình mở cùng một cổng COM. COM5 là Kingbird. COM4 là máy bột.
- Không để BM-OCR ghi SQLite.
- Không đoán biển khi thiếu chữ cái. Luật ghép mới nằm ở `ocr/branch.py` của repo desktop. `decide()` là đường lùi.
- Không đổi cửa 3 giây hoặc ε 20 kg khi chưa có bảng đối sổ.
- Không commit `STATION_KEY`.
- Không cài lên máy sổ cũ.

Việc còn lại: [docs/TASKS.md](docs/TASKS.md).
