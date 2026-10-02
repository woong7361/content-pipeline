# 「작업대 설치.bat」 이 부른다 — 다른 PC 에서 차시 작업대 · 초안 파이프라인을 쓸 수 있게 한 번에 준비한다(2026-10-02 사용자 요청:
# "exe 나 bat 클릭으로 실행되게"). 절차와 이유는 docs/다른_PC_설치.md 와 같다. 몇 번을 다시 돌려도 된다 — 이미 된 단계는 건너뛴다.
#
# 사람이 하는 것은 셋뿐이다: 클로드 · 코덱스 로그인(브라우저), gyo6_content 폴더 고르기(또는 새로 받기), 학기 확인.
# 키 · 비밀번호는 만들지도 적지도 않는다. gyo6 에 커밋 · 배포하지 않는다.
#
#   -Yes   묻지 않고 기본값으로(이미 로그인돼 있고 desk/config.json 에 gyo6 경로가 있을 때 — 다시 돌릴 때용)
param([switch]$Yes)

# Stop 으로 두면 PowerShell 5.1 이 네이티브 명령(npm · npx · codex)의 stderr 한 줄만으로도 멈춘다 — 종료 코드로 판정한다
$ErrorActionPreference = "Continue"
[Console]::OutputEncoding = [Text.Encoding]::UTF8
$OutputEncoding = [Text.Encoding]::UTF8
$Project = Split-Path -Parent $PSScriptRoot          # content-harness-pipeline
$Gyo6Url = "https://git.cemware.com/urkr-system/gyo6_content"
$Log = Join-Path $env:TEMP "desk-install-$(Get-Date -Format yyyyMMdd-HHmmss).log"
Start-Transcript -Path $Log | Out-Null

function Step($n, $text) { Write-Host ""; Write-Host "[$n] $text" -ForegroundColor Cyan }
function Ok($text) { Write-Host "    ✔ $text" -ForegroundColor Green }
function Warn($text) { Write-Host "    ! $text" -ForegroundColor Yellow }
function Fail($text) { Write-Host "    ✘ $text" -ForegroundColor Red; throw $text }
function Ask($question, $default) {
    if ($Yes) { return $default }
    $answer = Read-Host "    $question (Enter = $default)"
    if ([string]::IsNullOrWhiteSpace($answer)) { return $default } else { return $answer.Trim() }
}
function Confirm($question) {
    if ($Yes) { return $true }
    $answer = Read-Host "    $question (Y/n)"
    return -not ($answer -match '^(n|no|아니)')
}
function RefreshPath {
    # winget · npm 이 방금 바꾼 PATH 를 이 창에도 반영한다(새 창을 열지 않아도 되게)
    $env:Path = [Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [Environment]::GetEnvironmentVariable("Path", "User") + ";$env:APPDATA\npm"
}
function Has($name) {
    $cmd = Get-Command $name -ErrorAction SilentlyContinue | Select-Object -First 1
    # python 은 Windows 스토어 바로가기(WindowsApps)가 있어도 실제로는 없다(winget 은 원래 거기 있으니 python 만 거른다)
    return [bool]$cmd -and -not ($name -eq "python" -and $cmd.Source -like "*\WindowsApps\*")
}
function WingetInstall($id, $label) {
    if (-not (Has "winget")) { Fail "winget 이 없어 $label 을(를) 설치할 수 없습니다. Microsoft Store 에서 '앱 설치 관리자'를 설치한 뒤 다시 실행하세요." }
    Write-Host "    $label 설치 중 (winget $id) …"
    winget install -e --id $id --accept-source-agreements --accept-package-agreements --silent
    RefreshPath
}
function Run($what, [scriptblock]$block) {
    & $block
    if ($LASTEXITCODE -ne 0) { Fail "$what 실패 (종료 코드 $LASTEXITCODE)" }
}

try {
    Write-Host "차시 작업대 · 초안 파이프라인 설치" -ForegroundColor White
    Write-Host "레포: $Project"
    Write-Host "기록: $Log"
    RefreshPath

    # ── 1. 필수 프로그램 ─────────────────────────────────────────────
    Step 1 "Python · Node.js · Git"
    if (-not (Has "python")) { WingetInstall "Python.Python.3.12" "Python 3.12" }
    if (-not (Has "node")) { WingetInstall "OpenJS.NodeJS.LTS" "Node.js" }
    if (-not (Has "git")) { WingetInstall "Git.Git" "Git" }
    foreach ($tool in "python", "node", "npm", "git") {
        if (-not (Has $tool)) { Fail "$tool 을(를) 찾지 못했습니다. 이 창을 닫고 다시 실행해 보세요(설치 직후엔 PATH 가 늦게 잡힐 때가 있습니다)." }
    }
    Ok ("Python " + (python --version 2>&1) + " · Node " + (node -v) + " · " + (git --version))

    # ── 2. AI CLI ────────────────────────────────────────────────────
    Step 2 "클로드 · 코덱스 CLI"
    if (-not (Has "claude")) { Run "클로드 CLI 설치" { npm install -g @anthropic-ai/claude-code }; RefreshPath }
    if (-not (Has "codex")) { Run "코덱스 CLI 설치" { npm install -g @openai/codex }; RefreshPath }
    Ok ("claude " + (claude --version 2>&1) + " · " + (codex --version 2>&1))

    # ── 3. 로그인 — 실제로 불러 본다(codex login status 는 만료돼도 '로그인됨' 이라 믿지 않는다) ──
    Step 3 "AI 로그인 확인 (짧게 한 번씩 불러 봅니다)"
    $logins = @(
        @{ Name = "클로드"; Test = { claude -p "ok 한 단어로만 답해" 2>&1 | Out-String }; Login = "claude"; Hint = "열린 창에서 안내대로 로그인한 뒤 /exit 를 치고 창을 닫으세요." },
        @{ Name = "코덱스"; Test = { codex exec --skip-git-repo-check "ok 한 단어로만 답해" 2>&1 | Out-String }; Login = "codex login"; Hint = "브라우저에서 로그인을 마치면 열린 창이 저절로 끝납니다. 창을 닫으세요." }
    )
    foreach ($ai in $logins) {
        for ($try = 1; ; $try++) {
            Push-Location $env:TEMP   # 레포 밖에서 부른다 — 레포 안이면 클로드가 CLAUDE.md 까지 읽어 확인 한 번에 비용이 커진다
            $out = & $ai.Test
            $code = $LASTEXITCODE
            Pop-Location
            if ($code -eq 0 -and $out -match "ok") { Ok "$($ai.Name) 호출 됨"; break }
            Warn "$($ai.Name) 호출 실패: $(($out -split "`n" | Where-Object { $_.Trim() } | Select-Object -Last 2) -join ' / ')"
            if ($Yes -or $try -ge 3) { Fail "$($ai.Name) 로그인이 필요합니다. '$($ai.Login)' 을(를) 실행해 로그인한 뒤 다시 설치하세요." }
            Write-Host "    → $($ai.Name) 로그인 창을 엽니다. $($ai.Hint)" -ForegroundColor White
            Start-Process cmd -ArgumentList "/k", "chcp 65001 >nul & $($ai.Login)" -Wait
        }
    }

    # ── 4. Python 패키지 ─────────────────────────────────────────────
    Step 4 "Python 패키지"
    Run "pip 설치" { python -m pip install --disable-pip-version-check -q -r (Join-Path $Project "requirement.txt") }
    Run "패키지 확인" { python -c "import jsonschema, PIL" }
    Ok "jsonschema · Pillow · playwright"

    # ── 5. gyo6_content ──────────────────────────────────────────────
    Step 5 "gyo6_content (작업대가 고치는 차시가 있는 체크아웃)"
    $config = Join-Path $Project "desk\config.json"
    $saved = if (Test-Path $config) { Get-Content -Raw -Encoding utf8 $config | ConvertFrom-Json } else { $null }
    $gyo6 = $null
    if ($saved -and $saved.gyo6_root -and (Test-Path (Join-Path $saved.gyo6_root "lessons"))) {
        if (Confirm "저장된 gyo6 경로를 그대로 씁니까? $($saved.gyo6_root)") { $gyo6 = $saved.gyo6_root }
    }
    while (-not $gyo6) {
        if ($Yes) { Fail "gyo6 경로를 모릅니다 — -Yes 없이 다시 실행해 고르세요." }
        $have = Read-Host "    이 PC 에 gyo6_content 폴더가 이미 있습니까? (Y = 폴더 고르기 / N = 새로 받기)"
        if ($have -match '^(n|no|아니)') {
            $dest = Ask "받을 폴더" (Join-Path $env:USERPROFILE "gyo6_content")
            if ((Test-Path $dest) -and (Get-ChildItem $dest -Force | Select-Object -First 1)) { Warn "이미 있는 폴더라 받지 않습니다: $dest"; continue }
            Write-Host "    $Gyo6Url 받는 중 … (사내 git 로그인 창이 뜨면 로그인하세요)"
            git clone $Gyo6Url $dest
            if ($LASTEXITCODE -ne 0) { Warn "받지 못했습니다 — 권한 · 네트워크를 확인하세요."; continue }
            $gyo6 = $dest
        } else {
            Add-Type -AssemblyName System.Windows.Forms
            $dialog = New-Object System.Windows.Forms.FolderBrowserDialog
            $dialog.Description = "gyo6_content 폴더를 고르세요 (안에 lessons 폴더가 있는 곳)"
            if ($dialog.ShowDialog() -eq "OK") { $gyo6 = $dialog.SelectedPath }
        }
        if ($gyo6 -and -not (Test-Path (Join-Path $gyo6 "lessons"))) { Warn "lessons 폴더가 없습니다 — gyo6_content 가 아닙니다: $gyo6"; $gyo6 = $null }
    }
    $gyo6 = (Resolve-Path $gyo6 -ErrorAction Stop).Path
    Ok "gyo6: $gyo6"
    Push-Location $gyo6
    try {
        if (-not (Test-Path "node_modules\playwright\index.js")) { Write-Host "    npm install (처음엔 몇 분 걸립니다) …"; Run "gyo6 npm install" { npm install --no-fund --no-audit } }
        Run "브라우저(chromium) 설치" { npx playwright install chromium }
    } finally { Pop-Location }
    Ok "gyo6 의 npm 패키지 · playwright 브라우저"

    $default = if ($saved -and $saved.semesters) { $saved.semesters -join "," } else { "3-1,3-2,4-1,4-2" }
    $semesters = Ask "작업대에 보일 학기(쉼표로)" $default
    $found = @()
    foreach ($s in $semesters -split ",") { $found += @(Get-ChildItem (Join-Path $gyo6 "lessons\$($s.Trim())\*\lesson.json") -ErrorAction SilentlyContinue) }
    if ($found.Count -eq 0) { Warn "그 학기들에 차시(lesson.json)가 하나도 없습니다 — 학기 이름을 확인하세요. 설정은 그대로 저장합니다." }
    else { Ok "차시 $($found.Count)개" }

    # 설정 저장 — 서버(lesson_desk.save_settings)와 같은 모양. AI 모델 설정은 있던 값을 둔다. BOM 없는 UTF-8 이어야 한다
    $env:DESK_GYO6 = $gyo6; $env:DESK_SEMESTERS = $semesters
    Run "설정 저장" { python -B -c @"
import json, os, pathlib
p = pathlib.Path(r'$config'); p.parent.mkdir(exist_ok=True)
d = json.loads(p.read_text(encoding='utf-8')) if p.exists() else {}
d['gyo6_root'] = os.environ['DESK_GYO6']
d['semesters'] = [s.strip() for s in os.environ['DESK_SEMESTERS'].split(',') if s.strip()]
for k in ('claude_model', 'codex_model', 'claude_effort', 'codex_effort'): d.setdefault(k, '')
p.write_text(json.dumps(d, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
"@ }
    Ok "desk\config.json"

    # ── 6. PDF 도구 ──────────────────────────────────────────────────
    Step 6 "PDF 도구 (poppler — 수정 요청서 · 스토리보드 PDF 읽기)"
    $bundled = Join-Path $Project "tools\poppler\poppler-26.07.0\Library\bin\pdftoppm.exe"
    if (Test-Path $bundled) { Ok "번들 poppler" }
    else {
        if (-not (Has "pdftoppm")) { WingetInstall "oschwartz10612.Poppler" "poppler" }
        if (Has "pdftoppm") { Ok "pdftoppm" } else { Warn "pdftoppm 을 못 찾았습니다 — 작업대는 쓸 수 있지만 PDF 쪽 그림이 안 나옵니다. 새 창에서 다시 실행해 보세요." }
    }

    # ── 7. 확인 ──────────────────────────────────────────────────────
    Step 7 "동작 확인"
    Push-Location $Project
    try {
        $test = python -B -m unittest tests.test_pipeline_foundations 2>&1 | Out-String
        if ($LASTEXITCODE -ne 0) { Write-Host $test; Fail "단위 테스트 실패" }
        Ok "단위 테스트 통과"
        if (Get-NetTCPConnection -LocalPort 8790 -State Listen -ErrorAction SilentlyContinue) {
            Warn "작업대가 이미 켜져 있어 서버 시험은 건너뜁니다(같은 작업 폴더를 두 서버가 건드리지 않게)."
        } else {
            $server = Start-Process python -ArgumentList "-B", "lesson_desk.py", "--port", "8799", "--no-notify" -PassThru -WindowStyle Hidden
            try {
                $state = $null
                for ($i = 0; $i -lt 20 -and -not $state; $i++) {
                    Start-Sleep -Milliseconds 500
                    try { $state = Invoke-RestMethod "http://127.0.0.1:8799/api/state" -TimeoutSec 3 } catch { }
                }
                if (-not $state) { Fail "시험 서버가 뜨지 않았습니다 — 'python -B lesson_desk.py' 를 직접 실행해 오류를 보세요." }
                $pipe = (Invoke-WebRequest "http://127.0.0.1:8799/pipeline" -UseBasicParsing).StatusCode
                Ok "서버 응답 · 차시 $($state.lessons.Count)개 · 초안 화면 $pipe"
            } finally { Stop-Process -Id $server.Id -Force -ErrorAction SilentlyContinue }
        }
    } finally { Pop-Location }

    # ── 8. 바탕화면 바로가기 ─────────────────────────────────────────
    Step 8 "바탕화면 「차시 작업대」 바로가기"
    $bat = Join-Path $Project "작업대 켜기.bat"
    $lnk = Join-Path ([Environment]::GetFolderPath("Desktop")) "차시 작업대.lnk"
    $shell = New-Object -ComObject WScript.Shell
    $shortcut = $shell.CreateShortcut($lnk)
    $shortcut.TargetPath = $bat
    $shortcut.WorkingDirectory = $Project
    $shortcut.WindowStyle = 7   # 최소화 — 검은 창은 닫으면 안 되므로 숨기지 않고 접어 둔다
    $shortcut.Save()
    Ok $lnk

    Write-Host ""
    Write-Host "설치 끝." -ForegroundColor Green
    Write-Host "  · 바탕화면 「차시 작업대」를 누르면 http://127.0.0.1:8790 이 열립니다(위 탭: 차시 작업대 / 초안 파이프라인)."
    Write-Host "  · 작업 표시줄의 검은 창은 닫지 마세요 — 닫으면 작업대가 꺼집니다."
    Write-Host "  · 업데이트: 이 설치 파일을 다시 실행하거나, 레포에서 git pull 뒤 바로가기를 다시 누르세요."
    if (-not $Yes -and (Confirm "지금 작업대를 켤까요?")) { Start-Process $lnk }
    Stop-Transcript | Out-Null
    exit 0
} catch {
    Write-Host ""
    Write-Host "설치를 멈췄습니다: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "고친 뒤 다시 실행하면 된 단계는 건너뜁니다. 기록: $Log"
    Stop-Transcript | Out-Null
    exit 1
}
