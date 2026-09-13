# Task 2–3 — Log RS232 (đầu cân + máy bột)

Máy tính sample + USB-RS232 (FTDI). Ghi **raw**, không sửa.

## Thứ tự baud

1. 9600 8N1  
2. 19200 8N1  
3. 4800 8N1  
4. 38400 / 115200 8N1  
5. 9600 7E1 hoặc 8E1 nếu 8N1 ra rác  

Mỗi lần thử ≥ 3 phút. Giữ file khi thấy số **đọc được bằng mắt**.

## Tên file

```
docs/logs/YYYY-MM-DD-indicator-9600-8n1.txt
docs/logs/YYYY-MM-DD-starch-9600-8n1.txt
```

## Dòng log

```
ts_iso	hex	ascii
2026-09-13T07:30:01.012Z	53542c31363838302c6b670d0a	ST,16880,kg
```

## Hỏi trên file (trả lời trong issue)

- Spew liên tục hay chỉ khi bấm Send/Print?
- Một dòng hay khối STX/ETX?
- Dấu `.` hay `,` hay số nguyên ×0,1?
- Có cờ ổn định không?
- Tần số (Hz hoặc 1 khung/mẫu)?

Cần **20 phiếu liên tiếp đúng** trước khi nối mill.
