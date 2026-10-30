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
set "DB=%ProgramData%\BmCancomp\data\cancomp.db"
if not exist "%DB%" set "DB=%LOCALAPPDATA%\BmCancomp\data\cancomp.db"
if not exist "%DB%" (
  echo Khong thay so phieu tren may nay. File nay chay tren may can, khong phai may lap trinh.
  pause
  exit /b 1
)
if not exist "%~dp0gui-lai-anh.py" (
  echo Thieu file gui-lai-anh.py nam canh file nay. Hay chep ca hai file.
  pause
  exit /b 1
)
set "BM_DB=%DB%"
where python >nul 2>&1 && python "%~dp0gui-lai-anh.py" && goto done
where py >nul 2>&1 && py -3 "%~dp0gui-lai-anh.py" && goto done
echo May can chua co Python. Cai Python 3.10, tick Add python.exe to PATH, roi bam dup lai.
pause
exit /b 1
:done
echo.
echo Xong. Vai giay nua BM Auto Can tu gui lai anh hom nay. Khong tat phan mem.
pause
exit /b 0
