@echo off
rem 차시 작업대 켜기 — 바로가기는 이것 하나다. 더블클릭하면:
rem   꺼져 있으면 켠다 · 켜져 있고 최신이면 브라우저만 연다 · 예전 코드로 켜져 있으면 새로 켠다(도는 작업이 있으면 알림 창으로 묻는다)
rem 이 창을 닫으면 작업대가 꺼지고 돌던 작업이 끊긴다(다음에 켤 때 되돌리고 그 차시를 멈춤으로 둔다). 최소화는 괜찮다.
chcp 65001 >nul
title 차시 작업대 - 이 창을 닫으면 작업대가 꺼집니다
cd /d "%~dp0"

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0tools\desk_launch_check.ps1"
if errorlevel 10 (
  if "%DESK_NO_BROWSER%"=="" start "" http://127.0.0.1:8790
  "%SystemRoot%\System32\timeout.exe" /t 3 >nul
  exit /b 0
)
if errorlevel 1 (
  pause
  exit /b 1
)

echo 차시 작업대를 켭니다. 이 창은 닫지 말고 최소화해 두세요. 끌 때는 Ctrl+C.
if "%DESK_NO_BROWSER%"=="" start "" cmd /c ""%SystemRoot%\System32\timeout.exe" /t 2 >nul & start http://127.0.0.1:8790"
python -B lesson_desk.py %*

echo.
echo 작업대가 꺼졌습니다. 위에 오류가 있으면 확인하세요.
pause
