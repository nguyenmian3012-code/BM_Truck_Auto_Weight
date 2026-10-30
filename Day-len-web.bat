@echo off
chcp 65001 >nul
echo.
echo  Day trang canxe len web. Khong go lenh. Khong doi khoa.
echo.
where git >nul 2>&1 || (echo May nay chua co Git. & pause & exit /b 1)
where node >nul 2>&1 || (echo May nay chua co Node.js. & pause & exit /b 1)
set "ROOT=%USERPROFILE%\BM_Truck_Auto_Weight"
if not exist "%ROOT%\.git" (
  echo Dang tai code...
  git clone --branch main --depth 1 https://github.com/nguyenmian3012-code/BM_Truck_Auto_Weight.git "%ROOT%"
  if errorlevel 1 goto fail
)
cd /d "%ROOT%"
git checkout main
git pull --ff-only
if errorlevel 1 goto fail
echo Dang kiem tra kho anh...
call npx --yes wrangler r2 bucket create bm-can-xe-shots
echo Dang day len Cloudflare...
call npx --yes wrangler deploy
if errorlevel 1 (
  echo.
  echo Neu trinh duyet Cloudflare vua mo, hay dang nhap, roi bam dup file nay lan nua.
  goto fail
)
echo.
echo Xong. Mo https://canxe.redtigerhead.com/
echo Trang chu la ba the. Trang thu cu van o /demo
pause
exit /b 0
:fail
echo Chua xong.
pause
exit /b 1
