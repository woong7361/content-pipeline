@echo off
rem 차시 작업대 · 초안 파이프라인 설치 — 더블클릭 한 번(2026-10-02 사용자 요청). 몇 번을 다시 실행해도 된다.
rem  · 이 레포 안(content-harness-pipeline)에 있으면 바로 tools\install_desk.ps1 을 돈다.
rem  · 이 파일만 다른 PC 에 복사해 실행하면 레포(fix 브랜치)를 먼저 받아 온 뒤 같은 설치를 돈다.
chcp 65001 >nul
title 차시 작업대 설치
setlocal

if exist "%~dp0tools\install_desk.ps1" (
  powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0tools\install_desk.ps1" %*
  goto :end
)

echo 레포가 없습니다 — 먼저 받아 옵니다.
where git >nul 2>nul
if errorlevel 1 (
  echo Git 설치 중 ...
  winget install -e --id Git.Git --accept-source-agreements --accept-package-agreements --silent
  set "PATH=%PATH%;%ProgramFiles%\Git\cmd"
)
where git >nul 2>nul
if errorlevel 1 (
  echo Git 을 찾지 못했습니다. 이 창을 닫고 다시 실행하세요.
  goto :end
)

set "DEST=%USERPROFILE%\content-pipeline"
set /p "DEST=레포를 받을 폴더 (Enter = %DEST%): "
if exist "%DEST%\.git" (
  git -C "%DEST%" fetch origin
  git -C "%DEST%" checkout fix
  git -C "%DEST%" pull --ff-only
) else (
  git clone -b fix https://github.com/woong7361/content-pipeline "%DEST%"
)
if not exist "%DEST%\content-harness-pipeline\tools\install_desk.ps1" (
  echo 설치 스크립트를 찾지 못했습니다: %DEST%\content-harness-pipeline\tools\install_desk.ps1
  echo 받기가 실패했으면 GitHub 계정 권한과 네트워크를, 받았다면 fix 브랜치가 최신인지 확인하세요.
  goto :end
)
powershell -NoProfile -ExecutionPolicy Bypass -File "%DEST%\content-harness-pipeline\tools\install_desk.ps1" %*

:end
echo.
pause
