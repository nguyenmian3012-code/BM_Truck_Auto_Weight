@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo BM-OCR. De BM Auto Can dang mo. Khong cai them gi.
set PY=
where python >nul 2>&1 && set PY=python
if not defined PY where py >nul 2>&1 && set PY=py -3
if not defined PY (
  echo Khong thay python trong PATH. Khong cai lai Python.
  pause
  exit /b 1
)
start "" http://127.0.0.1:8771/
%PY% "%~dp0bm_ocr.py"
echo.
echo Cua so nay giu BM-OCR chay. Tat cua so la tat trang theo doi.
pause
