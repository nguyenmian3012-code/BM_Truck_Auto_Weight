# Liên kết phần mềm CANcomp

Người sửa mill đọc file này trước khi đổi đường cân.

| | |
|---|---|
| Repo phần mềm (exe trên CANcomp / MinhComp) | https://github.com/nguyenmian3012-code/BM_CANXE_SOFT_CANcomp |
| File trong repo đó | `docs/LIEN-KET-REPO-CHA.md`, `docs/HE-THONG-CAN-XE-BINH-MINH.md`, `IngestClient.cs`, `Parsers.cs` |
| Bản đồ hệ thống (bản ở repo này) | [HE-THONG-CAN-XE-BINH-MINH.md](./HE-THONG-CAN-XE-BINH-MINH.md) |

Tách ngày 25/09/2026. Repo này giữ mill, whitepaper, spec phần cứng. Repo kia giữ tai RS232.

## Đừng bỏ sót

| Bạn vừa sửa | Phải đụng repo phần mềm? |
|---|---|
| `POST /api/ingest`, tên field `kg` / `starchPct`, header `X-Station-Key` | Có. Đối chiếu `IngestPayload` cùng ngày. |
| Phiên, biển số, 95%, sổ ngày, loại hàng | Không. |
| Baud, COM, DTR/RTS, khung máy bột, ε, cửa 2 giây | Có, đó là mã của họ. Repo này chỉ cập nhật `docs/cancomp.md` và `docs/hardware-spec.md`. |
| Camera / đèn | Spec ở đây. Code chụp sẽ vào repo phần mềm khi làm (chưa có ở bản 0.1). |

Worker `main` tại lúc tách (`9a1f5db`) chưa có route `/api/ingest`. Phần mềm đã POST theo hợp đồng trong `docs/cancomp.md` và xếp hàng SQLite cho đến khi có HTTP 2xx.

Tìm ngược: trong repo phần mềm, cụm `BM_Truck_Auto_Weight`.
