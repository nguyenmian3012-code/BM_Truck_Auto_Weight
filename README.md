# BM Cân Xe Tự Động

Hệ thống cân xe và điểm bột tự động — nhà máy Bình Minh (tinh bột khoai mì).

Đích, không đổi: xe lên bàn thì ra một phiếu kg, mẫu củ mì thì ra một điểm bột, số đó phải khớp sổ cũ, biển từ ảnh, điểm từ máy, người cân không sửa phiếu đã khóa. Cổng ra là 30 ngày lệch dưới 1%. Viết đủ ở [WHITEPAPER.md](./WHITEPAPER.md).

Đang chạy **11/11/2026** trên CANcomp, ba chương trình:

| Chương trình | Bản | Repo |
|---|---|---|
| BM Auto Cân Desktop | 0.18.44 | [BM_CANXE_SOFT_CANcomp](https://github.com/nguyenmian3012-code/BM_CANXE_SOFT_CANcomp) |
| BM-OCR | 0.18.44, cùng gói desktop | cùng repo |
| BM-ThuDiem | 1.2.0 | [BM-ThuDiem](https://github.com/nguyenmian3012-code/BM-ThuDiem) |

- Live: [canxe.redtigerhead.com](https://canxe.redtigerhead.com)
- Bản đồ: [docs/HE-THONG-CAN-XE-BINH-MINH.md](./docs/HE-THONG-CAN-XE-BINH-MINH.md)
- Việc kế: [docs/TASKS.md](./docs/TASKS.md)
- Guideline cho agent: [AGENTS.md](./AGENTS.md)

Repo gốc là repo này. Không dùng bản copy `bm-can-xe`. Không cài bản nháp `cancomp-agent/`.

---

## Lớp máy

| Máy | Việc |
|---|---|
| Sổ cũ | Giữ nguyên, không cài thêm. Vẫn là căn thanh toán cho đến cổng 1%. |
| CANcomp | AutoCan nghe COM5 (Kingbird). BM-ThuDiem nghe COM4 (máy bột). BM-OCR đọc biển tại chỗ. |
| canxe.redtigerhead.com | Nhận ingest. Chưa phải sổ pháp lý. |

COM5 và COM4 không trộn. Hai chương trình không mở cùng một cổng.

---

## Chiến thuật

Nguồn kích là cân đã khóa, không phải camera tự thấy xe dừng. Cửa cân xe là **3 giây**, ε 20 kg. Điểm bột lấy khô gần 5000 g và ướt khoảng 300–700 g, tra Quyết định 228, không lấy khô trừ ướt.

1. Đối sổ cũ: 20 lượt kg và một ca bột trên ThuDiem 1.2.0. Khóa trạm production chưa phải cổng ra.
2. Song song sổ cũ ≥ 30 ngày. Lệch dưới 1% thì mill mới là căn thanh toán.
3. Ảnh không chặn phiếu kg. Biển đọc trên CANcomp. Chưa đủ chữ thì để Nghi, không đoán.

Đầy đủ: [WHITEPAPER.md](./WHITEPAPER.md).

## Cloudflare

1. Worker **bm-can-xe**
2. Custom domain `canxe.redtigerhead.com`
3. Secret `STATION_KEY` — không commit. App CANcomp gửi header `X-Station-Key`.
4. `POST /api/ingest` nhận `kg` hoặc `starchPct`. CANcomp không ghi `binhminh_data`. Mất mạng thì phiếu nằm SQLite cho đến khi mill trả 2xx.

