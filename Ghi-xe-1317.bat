@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo.
echo  Ghi bien xe 13:17 vao phan mem dang mo.
echo  De BM Auto Can mo. Khong cai ban moi. Khong cai Python.
echo.
set PY=
where python >nul 2>&1 && set PY=python
if not defined PY where py >nul 2>&1 && set PY=py -3
if not defined PY (
  echo Khong thay python. Khong cai lai.
  pause
  exit /b 1
)
%PY% "%~dp0ghi-xe-1317.py"
echo.
echo Neu dong tren noi Da ghi: doi vai giay.
echo App tu gui len web. The Khac se co xe nay.
pause
