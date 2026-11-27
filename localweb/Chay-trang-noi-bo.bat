@echo off
cd /d "%~dp0"
echo Noi bo 0.4. Tat ban dang chay o cong 8780.
for /f "tokens=5" %%p in ('netstat -ano ^| findstr :8780 ^| findstr LISTENING') do taskkill /F /PID %%p >nul 2>&1
echo Trang noi bo, chi doc cancomp.db, khong gui len mang ngoai.
py -3 server.py
if errorlevel 1 python server.py
