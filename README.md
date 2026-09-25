# BM Cân Xe Tự Động

Hệ thống chụp hình, lưu biển số và cân nặng tự động — nhà máy Bình Minh (tinh bột khoai mì).

- Live: [canxe.redtigerhead.com](https://canxe.redtigerhead.com)
- Phần mềm máy CANcomp (repo riêng, 25/09/2026): [BM_CANXE_SOFT_CANcomp](https://github.com/nguyenmian3012-code/BM_CANXE_SOFT_CANcomp) — nghe RS232, lọc cao nguyên, SQLite, sync. Đổi ingest hoặc luật kg thì sửa **cả** repo đó.
- Bản đồ đã chốt: [docs/HE-THONG-CAN-XE-BINH-MINH.md](./docs/HE-THONG-CAN-XE-BINH-MINH.md) · cách không bỏ sót app: [docs/LIEN-KET-PHAN-MEM-CANCOMP.md](./docs/LIEN-KET-PHAN-MEM-CANCOMP.md)
- Kiến trúc máy cân: [docs/cancomp.md](./docs/cancomp.md) — PC độc lập **CANcomp** + DTECH + sync HTTPS
- Whitepaper: [WHITEPAPER.md](./WHITEPAPER.md)
- 10 việc: [docs/TASKS.md](./docs/TASKS.md) — issue [#2](https://github.com/nguyenmian3012-code/BM_Truck_Auto_Weight/issues/2)–[#11](https://github.com/nguyenmian3012-code/BM_Truck_Auto_Weight/issues/11)

---

## Lớp máy (chốt 15/09/2026)

| Máy | Việc |
|---|---|
| Sổ cũ | Giữ nguyên, không cài thêm |
| **CANcomp** | Nghe Kingbird (qua DTECH) + máy bột; lọc cao nguyên; chụp cam + đèn; SQLite; sync canxe |
| canxe.redtigerhead.com | Phiên, OCR pha 1, sổ ngày, sau đó `binhminh_data` |

Chi tiết dây / baud / lọc: [docs/cancomp.md](./docs/cancomp.md), [docs/mua-vat-tu-viec-2-3.md](./docs/mua-vat-tu-viec-2-3.md).
