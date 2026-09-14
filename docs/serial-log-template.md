# Task 2–3 — Log RS232 (đầu cân Kingbird + máy bột)

## Đầu cân KINGBIRD (sau tap COM2)

Thử **theo thứ tự** (mỗi mức ≥ 3 phút, xe lên bàn):

1. **1200 8N1** — mặc định Kingbird nhiều máy VN  
2. **9600 8N1**  
3. **9600 7E1**  
4. 2400 8N1 · 4800 8N1  

File: `docs/logs/YYYY-MM-DD-kingbird-COM2-<baud>.txt`

```
ts_iso	hex	ascii
```

Cần thấy: spew hay chỉ khi **Enter/Print**; có cờ ổn định; kg ASCII.

## Máy bột

Giữ bảng baud cũ: 9600 8N1 trước.
