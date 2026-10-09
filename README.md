# BM Cân Xe Tự Động

Hệ thống chụp hình, lưu biển số và cân nặng tự động — nhà máy Bình Minh (tinh bột khoai mì).

- Live: [canxe.redtigerhead.com](https://canxe.redtigerhead.com)
- Worker Cloudflare: `bm-can-xe`. Git webhook không tự build — khi cần bản live, upload `public/index.html` (mill v5, logo BM_7 đã nhúng).
- Phần mềm máy CANcomp, tên hiển thị **BM Auto Cân Desktop** (repo riêng): [BM_CANXE_SOFT_CANcomp](https://github.com/nguyenmian3012-code/BM_CANXE_SOFT_CANcomp) — nghe RS232, lọc cao nguyên, SQLite, sync. Đổi ingest hoặc luật kg thì sửa **cả** repo đó. Không cài bản nháp `cancomp-agent/` trong repo này.
- Bản đồ đã chốt: [docs/HE-THONG-CAN-XE-BINH-MINH.md](./docs/HE-THONG-CAN-XE-BINH-MINH.md) · cách không bỏ sót app: [docs/LIEN-KET-PHAN-MEM-CANCOMP.md](./docs/LIEN-KET-PHAN-MEM-CANCOMP.md)
- Kiến trúc máy cân: [docs/cancomp.md](./docs/cancomp.md) — PC độc lập **CANcomp** + DTECH + sync HTTPS. Một số câu trong file này còn cửa 2 giây và ảnh xám; luật đang chạy nằm ở whitepaper và app.
- Whitepaper: [WHITEPAPER.md](./WHITEPAPER.md) — mục tiêu còn hiệu lực, bản 09/10/2026
- 10 việc: [docs/TASKS.md](./docs/TASKS.md) — issue [#2](https://github.com/nguyenmian3012-code/BM_Truck_Auto_Weight/issues/2)–[#11](https://github.com/nguyenmian3012-code/BM_Truck_Auto_Weight/issues/11). Hàng đợi tháng 9, không thay whitepaper.
- Backup mill không logo: nhánh `backup/v5-pre-logo`

Repo gốc là repo này. Không dùng bản copy `bm-can-xe` (bot import).

---

## Lớp máy (chốt 15/09/2026)

| Máy | Việc |
|---|---|
| Sổ cũ | Giữ nguyên, không cài thêm |
| **CANcomp** | Nghe Kingbird (qua DTECH) + máy bột; lọc cao nguyên; chụp cam + đèn; SQLite; sync canxe |
| canxe.redtigerhead.com | Phiên, OCR pha 1, sổ ngày, sau đó `binhminh_data` |

Chi tiết dây / baud / lọc: [docs/cancomp.md](./docs/cancomp.md), [docs/mua-vat-tu-viec-2-3.md](./docs/mua-vat-tu-viec-2-3.md).

Mill v5 (phiên, biển từ camera, sổ ngày, logo hổ) nằm ở `public/index.html`. Phần nghe cổng COM không nằm trong trang web — nằm ở BM Auto Cân Desktop.

---

## Chiến thuật

Nguồn kích là cân đã khóa, không phải camera tự thấy xe dừng. Cửa đang chốt là **3 giây**, ε 20 kg. Biển chỉ từ camera. Điểm bột chỉ từ RS232.

1. CANcomp đang nghe thiết bị thật. Việc kế là đối sổ cũ. Khóa trạm production chưa bật.
2. Song song sổ cũ ≥ 30 ngày. Lệch dưới 1% thì mill mới là căn thanh toán.
3. Ảnh local không chặn phiếu kg. OCR và đẩy ảnh để sau khi số kg đã khớp.

Đầy đủ, gồm phần hướng cũ đã bỏ: [WHITEPAPER.md](./WHITEPAPER.md).

## Cloudflare

1. Worker **bm-can-xe**
2. Custom domain `canxe.redtigerhead.com`
3. Secret `STATION_KEY` — không commit. App CANcomp gửi header `X-Station-Key`.
4. `POST /api/ingest` chưa có trên worker (đang 404). BM Auto Cân xếp hàng SQLite cho đến khi route trả 2xx.
