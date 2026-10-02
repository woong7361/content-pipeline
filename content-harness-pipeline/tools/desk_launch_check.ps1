# "작업대 켜기.bat" 이 서버를 켜기 전에 부른다 — 이미 켜진 작업대가 있으면 그대로 쓸지, 새 코드로 다시 켤지 정한다.
#
# 바로가기는 하나만 둔다(2026-10-01 사용자 요청). 예전에는 이미 켜져 있으면 브라우저만 열어서, 서버 코드가 바뀐 뒤에도
# 예전 서버가 계속 돌았다 — 화면 파일만 새것이라 화면이 깨졌다(problem.md [desk-page-server-version-skew]).
#
# 종료 코드 — bat 이 이것을 보고 움직인다
#   0   지금 켜진 작업대가 없다(원래 꺼져 있었거나 예전 것을 껐다) → 새로 켠다
#   10  켜진 작업대가 최신이다, 또는 사람이 다시 켜기를 미뤘다 → 브라우저만 연다
#   1   다른 프로그램이 포트를 쓰거나 끄지 못했다 → 멈추고 알린다
$ErrorActionPreference = "Stop"
$port = if ($env:DESK_PORT) { [int]$env:DESK_PORT } else { 8790 }   # 시험할 때만 바꾼다
$title = "차시 작업대"

$listen = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue
if (-not $listen) { exit 0 }
$server = Get-CimInstance Win32_Process -Filter "ProcessId=$($listen[0].OwningProcess)"
if ($server.CommandLine -notmatch "lesson_desk\.py") {
    Write-Host "$port 포트를 작업대가 아닌 프로그램이 쓰고 있습니다: $($server.CommandLine)"
    exit 1
}

# 최신인가 — 서버가 '켠 뒤 코드가 바뀌었다(restart_needed)' 고 하거나, 그 값을 모르는 예전 서버면 다시 켠다
$busy = @()
$stale = $true
try {
    $state = Invoke-RestMethod -Uri "http://127.0.0.1:$port/api/state" -TimeoutSec 10
    $stale = ($state.PSObject.Properties.Name -notcontains "restart_needed") -or $state.restart_needed
    foreach ($l in $state.lessons) {
        if ($l.queue_running -or ($l.job -and $l.job.state -eq "running")) { $busy += "차시 $($l.lesson)" }
    }
    $pipe = Invoke-RestMethod -Uri "http://127.0.0.1:$port/api/pipeline" -TimeoutSec 10
    foreach ($r in $pipe.runs) { if ($r.running) { $busy += "초안 $($r.run_id)" } }
} catch {
    Write-Host "켜진 작업대에 상태를 묻지 못했습니다 — 다시 켭니다: $($_.Exception.Message)"
}
if (-not $stale) {
    Write-Host "작업대가 이미 켜져 있고 최신입니다."
    exit 10
}

if ($busy.Count -gt 0) {
    # 바로가기는 창을 최소화해서 띄운다 — 콘솔에 묻으면 안 보이므로 알림 창으로 묻는다
    $text = "작업대 코드가 바뀌어 새로 켜야 합니다.`n`n지금 도는 작업: $($busy -join ', ')`n`n" +
            "지금 다시 켜면 그 작업은 끊기고, AI 작업은 되돌린 뒤 그 차시를 멈춤으로 켭니다.`n" +
            "[아니요]를 누르면 예전 작업대를 그대로 쓰고, 작업이 끝난 뒤 바로가기를 다시 누르면 됩니다.`n`n지금 다시 켤까요?"
    $answer = if ($env:DESK_RESTART_ANSWER) { $env:DESK_RESTART_ANSWER } else {
        if ((New-Object -ComObject WScript.Shell).Popup($text, 0, $title, 4 + 48) -eq 6) { "yes" } else { "no" }
    }
    if ($answer -ne "yes") {
        Write-Host "다시 켜기를 미뤘습니다 — 예전 작업대를 그대로 씁니다."
        exit 10
    }
}

# 서버를 띄운 창(작업대 켜기.bat 의 cmd)째 끈다 — 서버만 끄면 그 창이 '꺼졌습니다' 에서 멈춘 채 남는다
$parent = Get-CimInstance Win32_Process -Filter "ProcessId=$($server.ParentProcessId)" -ErrorAction SilentlyContinue
$target = if ($parent -and $parent.Name -eq "cmd.exe" -and $parent.CommandLine -match "\.bat") { $parent.ProcessId } else { $server.ProcessId }
taskkill /PID $target /T /F | Out-Null
foreach ($i in 1..20) {
    if (-not (Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue)) {
        Write-Host "예전 작업대를 껐습니다 — 새 코드로 켭니다."
        exit 0
    }
    Start-Sleep -Milliseconds 500
}
Write-Host "예전 작업대가 10초 안에 꺼지지 않았습니다."
exit 1
