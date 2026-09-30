@echo off
rem 차시 작업대 켜기 — 더블클릭하면 서버를 켜고 브라우저를 연다.
rem 이 창을 닫으면 작업대가 꺼지고 돌던 작업이 끊긴다(다음에 켤 때 되돌리고 그 차시를 멈춤으로 둔다). 최소화는 괜찮다.
chcp 65001 >nul
title 차시 작업대 - 이 창을 닫으면 작업대가 꺼집니다
cd /d "%~dp0"

rem 이미 켜져 있으면 브라우저만 연다
netstat -ano | findstr /r /c:":8790 .*LISTENING" >nul
if not errorlevel 1 (
  echo 작업대가 이미 켜져 있습니다. 브라우저만 엽니다.
  if "%DESK_NO_BROWSER%"=="" start "" http://127.0.0.1:8790
  timeout /t 3 >nul
  exit /b 0
)

echo 차시 작업대를 켭니다. 이 창은 닫지 말고 최소화해 두세요. 끌 때는 Ctrl+C.
if "%DESK_NO_BROWSER%"=="" start "" cmd /c "timeout /t 2 >/dev/null & start http://127.0.0.1:8790"
python -B lesson_desk.py %*

echo.
echo 작업대가 꺼졌습니다. 위에 오류가 있으면 확인하세요.
pause
