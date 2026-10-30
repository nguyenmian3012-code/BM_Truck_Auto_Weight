@echo off
chcp 65001 >nul
echo.
echo  Gui lai anh hom nay len web. De BM Auto Can dang mo. Khong cai ban moi.
echo.
where curl >nul 2>&1 || (echo May nay chua co curl. & pause & exit /b 1)
curl -s -o "%TEMP%\bm-shot-probe.txt" -w "%%{http_code}" "https://canxe.redtigerhead.com/api/shot?id=does-not-exist" > "%TEMP%\bm-shot-code.txt"
set /p CODE=<"%TEMP%\bm-shot-code.txt"
if not "%CODE%"=="404" (
  echo Web chua san sang nhan anh. Ma tra ve: %CODE%
  echo Hay bat R2 roi bam dup Day-len-web.bat tren may lap trinh truoc.
  pause
  exit /b 1
)
set "BM_DB="
set "PYEXE="
where python >nul 2>&1 && set "PYEXE=python"
if not defined PYEXE where py >nul 2>&1 && set "PYEXE=py -3"
if not defined PYEXE (
  echo Khong goi duoc python. Khong cai lai Python 3.10, may da co san.
  echo Dong cua so Setup. Bam Close.
  pause
  exit /b 1
)
%PYEXE% "%~dp0gui-lai-anh.py"
if errorlevel 1 (
  echo.
  echo Chua gui duoc. Dong loi nam phia tren. Khong cai lai Python.
  pause
  exit /b 1
)
echo.
echo Xong. Vai giay nua BM Auto Can tu gui lai anh hom nay. Khong tat phan mem.
pause
exit /b 0
