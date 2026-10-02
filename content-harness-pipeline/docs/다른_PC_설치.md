# 다른 PC 에서 차시 작업대 · 초안 파이프라인 쓰기 — 설치 절차

> 이 문서는 **AI 에이전트가 위에서부터 그대로 수행**할 수 있게 쓴 절차서다. 사람이 읽어도 된다.
> 환경: **Windows 10/11 · PowerShell**. 명령은 모두 PowerShell 기준이다.
> 마지막 확인: 2026-10-02 · 이 레포 `fix` 브랜치(원격 `origin/fix`) 기준.

## 가장 쉬운 방법 — 「작업대 설치.bat」 더블클릭

아래 1~10단계를 한 번에 하는 설치 파일이 있다: `content-harness-pipeline\작업대 설치.bat`(→ `tools\install_desk.ps1`).

- **레포가 아직 없는 PC**: 이 bat 파일 하나만 복사해 더블클릭 → 받을 폴더를 묻고 `fix` 브랜치를 받은 뒤 이어서 설치한다.
- **레포가 있는 PC**: 레포 안의 bat 을 더블클릭.
- 사람이 하는 것: 클로드 · 코덱스 로그인 창(뜨면 로그인), gyo6_content 폴더 고르기(또는 새로 받기), 학기 확인(Enter = 기본).
- 다시 실행해도 된다 — 된 단계는 건너뛴다. 업데이트할 때도 이걸 다시 누르면 된다.
- 멈추면 화면의 빨간 줄과 기록 파일(`%TEMP%\desk-install-*.log`)을 본다. AI 에이전트는 `tools\install_desk.ps1 -Yes`(묻지 않고 기본값)로 다시 돌릴 수 있다 —
  단 로그인과 gyo6 경로가 이미 정해져 있어야 한다.

설치 파일이 실패했거나 무엇을 하는지 단계별로 보려면 아래 절차를 따른다.

## 0. 에이전트가 지킬 것

- 단계마다 **[확인]** 명령을 돌려 기대한 결과가 나와야 다음 단계로 간다. 안 나오면 멈추고 사람에게 출력 그대로 보고한다.
- **[사람]** 이 붙은 단계는 에이전트가 할 수 없다(브라우저 로그인 · 경로 선택 등). 사람에게 무엇을 해 달라고 정확히 말하고 끝났다는 답을 받은 뒤 이어 간다.
- 하지 않는 것:
  - API 키 · 비밀번호 · 토큰을 만들거나 파일에 적지 않는다. AI 는 CLI 로그인으로만 쓴다(Typecast API 도 쓰지 않는다).
  - `desk/` · `runs/` 를 git 에 올리지 않는다(PC 마다 다른 작업 데이터).
  - gyo6_content 에 커밋 · 푸시하지 않는다. `npm run deploy` 를 돌리지 않는다.
  - 이미 있는 폴더를 지우거나 덮어쓰지 않는다. 같은 이름이 있으면 멈추고 묻는다.
- 한글 파일을 읽을 때는 UTF-8 로 읽는다: `Get-Content -Raw -Encoding utf8 <파일>`.

## 1. 사람에게 먼저 물을 것 [사람]

시작 전에 아래 네 가지를 받는다. 모르면 괄호 안 기본값을 제안한다.

| # | 물을 것 | 기본값 / 예 |
|---|---|---|
| Q1 | 이 레포를 받을 폴더 | `C:\work\content-pipeline` |
| Q2 | gyo6_content 체크아웃 경로. **없으면** 받을 폴더와 접근 권한이 있는지 | 사내 git `https://git.cemware.com/urkr-system/gyo6_content` |
| Q3 | 작업대에 보일 학기 | `3-1,3-2,4-1,4-2` |
| Q4 | 기존 PC 의 작업 기록(`desk/`) · 초안 결과(`runs/`) · PDF 도구(`tools/poppler/`)를 옮겨 올지 | 옮기지 않음(빈 작업대로 시작) · poppler 는 8단계에서 설치 |

이하 `<REPO>` = Q1, `<GYO6>` = Q2 경로로 바꿔 읽는다.

## 2. 필수 프로그램 확인

```powershell
python --version      # 3.12 이상 (검증한 버전 3.12.10)
node -v               # v20 이상 (검증한 버전 v24.18.0)
npm -v
git --version
```

[확인] 넷 다 버전이 나온다. 없는 것은 설치한다(설치에 관리자 권한이 필요하면 [사람]):

```powershell
winget install -e --id Python.Python.3.12
winget install -e --id OpenJS.NodeJS.LTS
winget install -e --id Git.Git
```

설치 후에는 **새 PowerShell 창**에서 다시 확인한다(PATH 반영).

## 3. AI CLI 설치와 로그인

```powershell
npm install -g @anthropic-ai/claude-code
npm install -g @openai/codex
claude --version      # 검증한 버전 2.1.286
codex --version       # 검증한 버전 0.158.0
```

로그인 [사람] — 둘 다 브라우저 로그인이라 사람이 한다:

- 클로드: PowerShell 에서 `claude` 실행 → 안내대로 로그인 → `/exit`
- 코덱스: `codex login`

[확인] 실제로 불러 본다. `codex login status` 는 로컬 파일만 봐서 만료돼도 "로그인됨" 이라고 하므로 믿지 않는다.

```powershell
claude -p "ok 라고만 답해"
codex exec "ok 라고만 답해"
```

둘 다 `ok` 비슷한 답이 오면 된다. `refresh_token_invalidated` · 401 이 보이면 로그인을 다시 한다 [사람].

## 4. 이 레포 받기 (`fix` 브랜치)

```powershell
git clone https://github.com/woong7361/content-pipeline "<REPO>"
cd "<REPO>"
git checkout fix
git log --oneline -1
```

[확인] `fix` 브랜치다(`git branch --show-current` → `fix`). **main 에는 작업대 코드가 없다.**
권한 오류(403)가 나면 [사람] — 이 PC 의 GitHub 계정에 저장소 읽기 권한이 필요하다.

이미 받아 둔 레포면 `git -C "<REPO>" pull` 만 한다.

## 5. Python 패키지

```powershell
cd "<REPO>\content-harness-pipeline"
python -m pip install -r requirement.txt
```

[확인] `python -c "import jsonschema, PIL; print('ok')"` → `ok`

## 6. gyo6_content 준비

Q2 에서 체크아웃이 이미 있으면 받기는 건너뛴다.

```powershell
git clone https://git.cemware.com/urkr-system/gyo6_content "<GYO6>"   # 없을 때만, 권한 필요 [사람]
cd "<GYO6>"
npm install
npx playwright install chromium
```

- `npm install` 이 gyo6 의 playwright 를 깐다. 작업대의 화면 검사 · 기능 테스트(`tools/check_rendered.mjs` ·
  `tools/run_functional_tests.mjs`)는 **gyo6 의 `node_modules/playwright`** 를 쓴다.

[확인]

```powershell
Test-Path "<GYO6>\lessons"                                  # True
Test-Path "<GYO6>\node_modules\playwright\index.js"         # True
npm --prefix "<GYO6>" run build:lesson -- 4-1/01            # 그 차시가 있으면. 끝에 오류 없이 끝난다
```

빌드는 체크아웃 안의 차시 하나로 시험한다(`lessons\<학기>\<차시>\lesson.json` 이 있는 것 — `Get-ChildItem "<GYO6>\lessons\*\*\lesson.json"` 로 고른다).

## 7. (선택) 기존 PC 데이터 옮기기 — Q4 가 "옮김" 일 때만

기존 PC 의 `<기존 REPO>\content-harness-pipeline\` 아래 폴더를 같은 자리에 복사한다. 사람이 USB · 공유 폴더로 건네준 경로에서 복사한다 [사람].

| 폴더 | 내용 | 주의 |
|---|---|---|
| `desk\` | 차시별 메모 · 작업 기록 · 백업 · AI 모델 설정 | `desk\config.json` 의 `gyo6_root` 가 **기존 PC 경로**다 → 9단계에서 `--gyo6-root` 로 덮어쓴다 |
| `runs\` | 초안 run 들 | 용량이 크다 |
| `tools\poppler\` | PDF → 그림 도구(약 119MB) | 옮기면 8단계를 건너뛴다 |

`desk\*\lesson-config.json` 에 기존 PC 의 작업 경로가 적혀 있을 수 있다. 작업대 카드의 "작업 경로" 가 이상하면 카드에서 [기본으로]를 누른다.

## 8. PDF 도구 (poppler)

수정 요청서 나누기 · 스토리보드 PDF 읽기 · 화면 대조가 `pdftoppm` 을 쓴다. 코드는 `tools\poppler\poppler-26.07.0\Library\bin` 을
먼저 찾고 없으면 PATH 를 본다. 7단계에서 옮겼으면 건너뛴다.

```powershell
winget install -e --id oschwartz10612.Poppler
```

[확인] **새 PowerShell 창**에서 `pdftoppm -v` → 버전이 나온다.

## 9. 처음 켜기와 동작 확인

처음 한 번은 gyo6 경로를 알려 준다(`desk\config.json` 에 기억 — 다음부터는 생략).
에이전트는 **시험용 포트**로 켜서 확인하고 끈다(사람이 쓸 서버는 10단계 바로가기로 따로 켠다).

```powershell
cd "<REPO>\content-harness-pipeline"
$p = Start-Process python -ArgumentList '-B','lesson_desk.py','--gyo6-root',"<GYO6>",'--semesters','<Q3>','--port','8799','--no-notify' -PassThru -WindowStyle Hidden
Start-Sleep 4
$s = Invoke-RestMethod http://127.0.0.1:8799/api/state
"차시 수: $($s.lessons.Count) · gyo6: $($s.gyo6_root)"
(Invoke-WebRequest http://127.0.0.1:8799/pipeline -UseBasicParsing).StatusCode    # 200
(Invoke-WebRequest http://127.0.0.1:8799/static/desk_common.js -UseBasicParsing).StatusCode   # 200
Stop-Process -Id $p.Id
```

[확인]
- 차시 수가 1 이상이고 gyo6 경로가 `<GYO6>` 다. 0 이면 학기 폴더 이름(Q3)과 `lessons\<학기>\<차시>\lesson.json` 이 있는지 본다.
- `/pipeline` · `/static/desk_common.js` 가 200.
- `Invoke-RestMethod` 가 접속 실패면 서버가 바로 죽은 것이다 — 같은 명령을 `-WindowStyle Hidden` 없이 돌려 오류를 사람에게 보여 준다.
  흔한 원인: `처음에는 --gyo6-root 로…`(경로 빠짐) · `gyo6_content 가 아니다(lessons/ 가 없다)`(경로가 틀림).

단위 테스트도 돌린다(LLM 을 부르지 않는다):

```powershell
python -B -m unittest tests.test_pipeline_foundations
```

[확인] 마지막 줄이 `OK`.

## 10. 바로가기 만들기

사람이 매번 쓰는 것은 `작업대 켜기.bat` 하나다. 바탕화면에 「차시 작업대」 바로가기를 만든다(최소화 창으로 실행):

```powershell
$bat = Join-Path "<REPO>\content-harness-pipeline" "작업대 켜기.bat"
$lnk = Join-Path ([Environment]::GetFolderPath('Desktop')) "차시 작업대.lnk"
$w = New-Object -ComObject WScript.Shell
$sc = $w.CreateShortcut($lnk)
$sc.TargetPath = $bat
$sc.WorkingDirectory = Split-Path $bat
$sc.WindowStyle = 7
$sc.Save()
Test-Path $lnk     # True
```

## 11. 사람에게 넘길 안내 (그대로 전달)

- 바탕화면 **「차시 작업대」** 를 더블클릭 → 브라우저에 `http://127.0.0.1:8790` 이 열린다.
  - 위 탭 **차시 작업대**(`/`) · **초안 파이프라인**(`/pipeline`).
  - 작업 표시줄의 검은 창은 **닫지 말고** 둔다(닫으면 작업대가 꺼지고 돌던 AI 작업이 끊긴다).
- 이 PC 에서만 열린다(`127.0.0.1`). 다른 PC 브라우저로는 접속할 수 없다 — PC 마다 따로 켠다.
- AI 비용은 이 PC 에 로그인한 클로드 · 코덱스 계정으로 나간다. 모델은 사이드바 맨 아래 **▸ AI 모델** 에서 고른다.
- 새 차시는 gyo6 `lessons\<학기>\<차시>\lesson.json` 이 생기면 몇 초 안에 작업대에 저절로 나타난다(다시 켤 필요 없음).
- 레포를 새로 pull 받아 서버 코드가 바뀌면 화면 위에 **빨간 띠**가 뜬다 → 바로가기를 다시 누르면 새 코드로 켜진다.
- 같은 차시를 두 PC 에서 동시에 고치지 않는다(gyo6 커밋 때 부딪힌다).
- 쓰는 법은 작업대 화면의 **사용법**, 자세한 설명은 `docs\작업대_안내.md` · `docs\초안_파이프라인_안내.md`.

## 12. 업데이트 (다음부터)

```powershell
git -C "<REPO>" pull
python -m pip install -r "<REPO>\content-harness-pipeline\requirement.txt"
```

그다음 바로가기를 다시 누른다(돌던 작업이 있으면 알림 창으로 먼저 묻는다).

## 문제가 생기면

| 증상 | 원인 · 할 일 |
|---|---|
| 그림 · 검증 메모가 "종료 코드 1" 로만 실패 | 코덱스 로그인 만료일 때가 많다 → 3단계 [확인] 명령으로 확인, `codex login` [사람] |
| 코드 메모가 바로 실패 | `claude` 가 PATH 에 없거나 로그인 안 됨 → 3단계 |
| [빌드]가 실패 | `<GYO6>` 에서 `npm install` 을 안 했거나 그 차시 빌드 자체가 깨짐 → 6단계 [확인]의 빌드 명령을 직접 돌려 본다 |
| 수정 요청서 나누기가 실패 · 쪽 그림 없음 | poppler 없음 → 8단계 |
| 화면이 깨져 보이고 위에 빨간 띠 | 서버가 예전 코드 → 바로가기를 다시 누른다 |
| 차시가 하나도 안 보임 | 학기 목록(Q3)과 gyo6 경로 확인 → `python -B lesson_desk.py --gyo6-root "<GYO6>" --semesters <Q3>` 로 한 번 켜서 다시 기억시킨다 |
| 8790 포트가 이미 쓰는 중 | 다른 작업대가 켜져 있다. 바로가기가 알아서 확인한다. 직접 켤 때는 `--port` 로 다른 번호 |
