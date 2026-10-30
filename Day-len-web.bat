@echo off
chcp 65001 >nul
echo.
echo  Day trang canxe len web. Khong go lenh. Khong doi khoa.
echo  Lan chay lai se khong hoi 3 cau nhu lan dau. Dieu do la dung.
echo  Neu thay "already exists": kho anh da co, cu de cua so chay tiep.
echo  Ten go nham bm_can_xe_shots se bi bo. Ten dung la SHOTS.
echo.
where git >nul 2>&1 || (echo May nay chua co Git. & pause & exit /b 1)
where node >nul 2>&1 || (echo May nay chua co Node.js. & pause & exit /b 1)
set "ROOT=%USERPROFILE%\BM_Truck_Auto_Weight"
if not exist "%ROOT%\.git" goto fresh
cd /d "%ROOT%"
git fetch origin main
if errorlevel 1 goto fresh
git reset --hard origin/main
if errorlevel 1 goto fresh
goto ready
:fresh
echo Dang tai lai code sach, bo ten binding go nham...
cd /d "%USERPROFILE%"
if exist "%ROOT%" rmdir /s /q "%ROOT%"
git clone --branch main --depth 1 https://github.com/nguyenmian3012-code/BM_Truck_Auto_Weight.git "%ROOT%"
if errorlevel 1 goto fail
cd /d "%ROOT%"
:ready
echo.
echo Dang mo kho anh. Neu kho da co, dong "already exists" la binh thuong.
set CI=true
call npx --yes wrangler r2 bucket create bm-can-xe-shots --binding SHOTS --update-config false
echo.
echo Buoc kho anh xong. Ten binding luc dua len web la SHOTS.
echo Neu dong tren co "enable R2" hoac 10042: mo Cloudflare, bat R2, roi bam dup file nay lan nua.
echo.
echo Dang day trang len web...
call npx --yes wrangler deploy
if errorlevel 1 (
  echo.
  echo Chua len web. Neu Cloudflare bao thieu kho anh, hay bat R2 roi bam dup lan nua.
  echo Neu trinh duyet Cloudflare vua mo, hay dang nhap, roi bam dup file nay lan nua.
  echo Neu git bao loi vi file bi sua: xoa thu muc
  echo   %ROOT%
  echo roi bam dup file nay lan nua.
  goto fail
)
echo.
echo Xong. Mo https://canxe.redtigerhead.com/
echo Trang giu ban V5. Ba the nam trong muc Xe dang trong nha may.
echo Anh toi da 3 GB. Anh qua 60 ngay thi xoa. Cai nao den truoc thi xoa truoc.
echo.
echo Anh da can hom nay: chep HAI file sau sang may can, de BM Auto Can dang mo, bam dup file bat.
echo   %ROOT%\Gui-lai-anh-hom-nay.bat
echo   %ROOT%\gui-lai-anh.py
echo Xe 13:17, bien 70H-082.61: chep them hai file nay sang may can roi bam dup.
echo   %ROOT%\Ghi-xe-1317.bat
echo   %ROOT%\ghi-xe-1317.py
pause
exit /b 0
:fail
echo Chua xong.
pause
exit /b 1
