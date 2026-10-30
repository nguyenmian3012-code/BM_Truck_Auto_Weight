@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo Man tai xe. Khong tat BM Auto Can. Khong cai them gi.
set PY=
where python >nul 2>&1 && set PY=python
if not defined PY where py >nul 2>&1 && set PY=py -3
if not defined PY (
  echo Khong thay python trong PATH. Khong cai lai Python.
  pause
  exit /b 1
)
start "" http://127.0.0.1:8770/
%PY% "%~dp0bay.py"
echo.
echo Cua so nay giu man tai xe. Tat cua so la tat man va den.
pause
