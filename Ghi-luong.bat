@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo.
echo  Dien luong Nhap mi / Xuat bot / Khac cho phieu hom nay.
echo  De BM Auto Can dang mo. Khong cai ban moi.
echo.
if not exist "%~dp0flow.py" if exist "%~dp0logic\flow.py" copy /Y "%~dp0logic\flow.py" "%~dp0flow.py" >nul
set PY=
where python >nul 2>&1 && set PY=python
if not defined PY where py >nul 2>&1 && set PY=py -3
if not defined PY (
  echo Khong thay python. Khong cai lai.
  pause
  exit /b 1
)
%PY% "%~dp0ghi-luong.py"
echo.
pause
