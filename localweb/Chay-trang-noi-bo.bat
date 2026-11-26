@echo off
cd /d "%~dp0"
echo Trang noi bo, chi doc cancomp.db, khong gui len mang ngoai.
py -3 server.py
if errorlevel 1 python server.py
