# content-harness-pipeline

이 파이프라인의 산출물은 **gyo6_content 차시 번들 초안**이다.
기본 경로는 실제 콘텐츠 제작 흐름처럼 기획, 디자인, 인터뷰, 비주얼 설계, 개발을 나누어 실행하는
`produce_lesson.py`다. 최종적으로 `runs/{run_id}/lesson/` 아래에 다음 파일을 만든다.

```text
lesson.json
player-ext.js
player-ext.css
manifest.json
page-map.md
```

`runner.py` 기반의 Markdown 스토리보드 → 단일 HTML 초안 경로는 제거되었다. 새 작업에서
`output/index.html`, `builder`, `design_refine`, `content_refine`, `content_eval` 흐름을 되살리지 않는다.
`build_lesson.py`는 스토리보드에서 바로 lesson을 만드는 단축 경로이며, 기본 제작 파이프라인은 아니다.

## 파일 인코딩

PowerShell에서 한글 파일을 읽을 때는 항상 UTF-8을 명시한다.

```powershell
Get-Content -Raw -Encoding utf8 'lesson.json'
```

`???`가 보이면 원문이 그런 것이 아니라 잘못 읽었을 가능성이 높다. 깨진 문자열을 그대로 옮겨 적지 않는다.

## 기본 원칙

- 구현 전 `docs/실행.md`, `schemas/*.schema.json`, `prompts/*_system.md`를 먼저 확인한다.
- 기존 파일 계약, 파일명 규칙, run 디렉토리 구조를 우선한다.
- LLM stage 사이의 핸드오프는 파일과 JSON payload로만 한다.
- stage 코드나 프롬프트가 임의로 run 디렉토리 전체를 훑어 읽게 만들지 않는다.
- 검증 가능한 형태로 마무리한다. 코드 변경 후 가능한 경우 `build_lesson.py`, `install_lesson.py`, `review_lesson.py`, `validate.py` 계열 검증을 실행한다.

## 실행

명령어는 `content-harness-pipeline` 디렉토리에서 실행한다.

```bash
cd content-harness-pipeline
python -m pip install -r ./requirement.txt
```

콘텐츠 제작형 파이프라인을 실행한다.

```bash
python -B ./produce_lesson.py "../스토리보드.pdf" --run-id g4l02 --gyo6-root {GYO6}
```

인터뷰 직전까지만 만든다.

```bash
python -B ./produce_lesson.py "../스토리보드.pdf" --run-id g4l02 --gyo6-root {GYO6} --through interview
```

인터뷰 답변을 반영해서 이어서 만든다.

```bash
python -B ./produce_lesson.py runs/g4l02 --gyo6-root {GYO6} --start-at interview_brief --interview-notes runs/g4l02/interview/answers.md
```

이미 만든 초안을 LLM 없이 다시 검사한다.

```bash
python -B ./build_lesson.py runs/g4l02 --gyo6-root {GYO6} --check-only
```

배치 전에 무엇을 옮길지만 본다.

```bash
python -B ./install_lesson.py runs/g4l02 --target {GYO6} --lesson 4-1/02 --dry-run
```

**대사 음성 (Typecast 웹 편집기)** — 초안이 끝나고 인물 대표 그림이 있으면 `produce_lesson.py` 가 끝에서
**대본을 내보내고 바탕화면 알림을 띄운 뒤 멈춘다**(`runs/{id}/audio/web/script.md` · 인물별 `script-*.txt`).
사람이 웹 편집기(웹 요금제)에서 인물마다 목소리를 골라 만들고, 내려받은 파일을 `audio/web-inbox/` 에 넣은 뒤
다시 돌린다. 웹 프로젝트는 그대로 남는다.

**Typecast API 는 쓰지 않는다**(2026-09-29 사용자 결정). 웹 요금제와 API 요금제가 따로라 웹 요금제로는
API 를 부를 수 없고, API 요금제는 사지 않는다. 한때 API 로 직접 만드는 경로가 있었으나 뺐다 — 되살리지 않는다.
**가져오기는 화면의 [음성 파일 넣기]로 한다**(2026-10-01 사용자 요청 — 초안 파이프라인 화면 · 차시 작업대 카드 둘 다,
공통 부품 `desk_common.js renderVoice` + `stages/scripts/voice_import.py`). 사용자 확인: 웹 편집기는 **대사 한 줄마다 따로** 내려받는다.
- 여러 파일을 한꺼번에 올리면 자동으로 짝짓는다 — ① 이름에 대사 앞부분이 있으면 **글자**로(번호 · 인물 이름 · 구분자를 뗀 뒤 비슷하면)
  ② 남은 것은 이름 속 번호(없으면 이름) **순서**로. 확인표에서 줄마다 ▶ 새 파일 · ▶ 지금 소리를 듣고 바꾸거나 빼고 [넣기].
- 범위: **빈 대사만**(기본) 또는 **교체 포함**(`voice_lines.collect(include_existing=True)` — 이미 걸린 소리도 `current` 와 함께).
  교체된 예전 소리는 다른 곳에서 안 쓰이면 audioMap 에서 빼고 파일을 보관 폴더(`removed/voice-{세션}/`)로 옮긴다. 효과음은 안 건드린다.
- 받은 확장자 그대로 놓는다(wav 도 — gyo6 빌드가 mp3 로 바꾼다). lesson.json 은 **원래 들여쓰기 · 줄바꿈(CRLF) 그대로** 다시 쓴다 —
  바이트로 읽어야 한다(read_text 는 CRLF 를 LF 로 읽어 파일 전체가 바뀐 것으로 보였다). 실측: 4-1/01 에서 소리 건 10줄만 바뀐다.
- 올린 뒤 대사 글이 바뀌었으면 넣기를 막는다(엉뚱한 줄에 붙지 않게). 넣은 세션은 다시 못 넣는다.
- 작업대는 AI 작업 · 빌드가 도는 중엔 넣기를 막고, 넣으면 바로 빌드한다. 초안은 run 의 `lesson/` 에 넣고 [gyo6에 넣기]로 반영한다.
- 세션: 작업대 `desk/{id}/voice/{작업 번호}/` · 초안 `runs/{run}/audio/import/{작업 번호}/`(files/ · session.json · lesson.before.json).

```bash
python -B ./voice_lesson.py runs/g4l02                  # 대본 내보내기(멈춤, 종료 코드 3) / 받은 파일 확인
python -B ./voice_lesson.py runs/g4l02 --dry-run        # 소리를 붙일 줄·글자 수만
```

넣으면 `lesson/assets/audio/narration/vo-*.<확장자>` 로 놓고 `lesson.json` 에 `audioMap.narration` 과
자리별 필드(컷 `sound` · 문제 `narration` · 힌트 `sound` · 이야기 카드 `narration.audio`)를 건다(`voice_lines.apply`).
배치가 `assets/` 를 통째로 옮기므로 gyo6 `lessons/{슬롯}/{차시}/assets/audio/narration/` 에 놓인다.
런타임이 재생하지 않는 자리(자막만 있는 컷 · 정답/오답 말풍선)는 대본에서 빼고 알린다.
`--no-voice` 로 이 단계를 건너뛴다.

**초안이 끝나면 반드시** 배치 → 빌드 → 화면 검증까지 돌린다. `produce_lesson.py` 의 마지막 검사는
데이터만 보고 화면을 한 번도 열지 않는다. 그래서 끝날 때 이 명령을 안내하고 `verify_required` 를 로그에 남긴다.

```bash
python -B ./install_lesson.py runs/g4l02 --target {GYO6} --lesson 4-1/02
cd {GYO6} && npm run build:lesson -- 4-1/02
python -B ./verify_lesson.py runs/g4l02 --target {GYO6} --lesson 4-1/02            # ①~④ 전부 (LLM 2회)
python -B ./verify_lesson.py runs/g4l02 --target {GYO6} --lesson 4-1/02 --skip-llm # ①~③만 (LLM 0회)
```

걸린 것은 `runs/{id}/verify/to-{담당}.md` 로 나뉜다. 개발·그림 몫은 그 파일을 그대로 넘겨 다시 돌린다.

```bash
# 개발 단계 되먹임 — 지금 산출물을 기준으로 목록만 고친다
python -B ./produce_lesson.py runs/g4l02 --gyo6-root {GYO6} --start-at senior_developer --through develop --screen-report runs/g4l02/verify/to-developer.md
# 그림 다시 굽기 — 목록의 그림만 치우고 다시 굽는다(경로가 빈 항목은 사람이 채운다)
python -B ./produce_lesson.py runs/g4l02 --gyo6-root {GYO6} --start-at asset_render --through render --rerender-from runs/g4l02/verify/to-asset.json
```

고친 뒤에는 배치 → 빌드 → 검증을 다시 돈다.

**사람이 화면을 보고 고칠 것 — 차시 작업대(`lesson_desk.py`)**. 초안·검증이 못 잡고 사람 눈에 걸리는 것을
차시마다 적고, 버튼으로 AI 에게 맡기고 빌드한다. **gyo6 차시 폴더를 직접 고친다**(2026-09-30 사용자 결정 —
run 이 없는 차시가 대부분이고 사람도 gyo6 에서 직접 고친다). run 은 거치지 않는다.

```bash
python -B ./lesson_desk.py --gyo6-root {GYO6}     # http://127.0.0.1:8790 — 경로는 desk/config.json 에 기억
python -B ./lesson_desk.py --semesters 3-1,3-2,4-1,4-2
```

사람은 바탕화면 「차시 작업대」(= `작업대 켜기.bat`, **바로가기는 이것 하나** — 2026-10-01 사용자 요청)를 더블클릭한다.
켜기 전에 `tools/desk_launch_check.ps1` 이 이미 켜진 작업대를 본다 — 꺼져 있으면 켜고, 켜져 있고 최신이면 브라우저만 열고,
**켠 뒤 서버 코드가 바뀌었으면**(`/api/state` 의 `restart_needed`, 그 값이 없는 예전 서버 포함) 서버 창째 끄고 새로 켠다.
도는 작업이 있으면 알림 창(예/아니요)으로 묻는다 — 바로가기가 창을 최소화해 띄워 콘솔 질문은 안 보인다.
예전에는 켜져 있으면 무조건 브라우저만 열어서, 서버 코드를 바꾼 뒤 "다시 켜라" 고 해도 예전 서버가 계속 돌았다
(problem.md `[desk-page-server-version-skew]`). 서버 코드를 바꾸면 두 화면 맨 위에 빨간 띠가 뜬다.
그 창을 닫으면 서버가 꺼진다. Claude Code 대화 안에서 띄운 서버는 대화가 끝나면 같이 꺼질 수 있으므로 사람이 쓸 서버는 따로 켠다.

- 목록은 gyo6 `lessons/{학기}/*/lesson.json`(기본 3-1 · 3-2 · 4-1 · 4-2). 왼쪽 사이드바(스크롤해도 따라온다)의
  학년 · 학기 · 차시 버튼은 **보이는 카드만** 바꾼다 — 작업은 서버에서 돌아서 다른 차시를 보고 있어도 계속된다.
- 메모는 이 레포 `desk/{학기-차시}/notes.json`(`stages/scripts/lesson_notes.py`) — gyo6 에 두면 공유 레포가 더러워지고
  `npm run deploy` 가 막힌다. 상태는 대기 → 처리 중 → 확인 대기(된 것) / 열림(못 한 것) → 완료.
  AI 가 끝내도 **사람이 화면을 보고** 닫는다. 번호(U01 …)는 지워도 다시 쓰지 않는다(작업 기록·사용량이 번호로 가리킨다).
- **코드 ∥ 그림·검증**(2026-10-01 사용자 요청) — 차시 안에서 클로드 줄(코드)과 코덱스 줄(그림·검증)이 **함께 돈다**.
  줄마다 한 번에 한 작업. 무엇을 시작할지는 `lesson_notes.runnable_groups` 가 순서로 정한다 — **코드와 그림은 서로
  기다리지 않는다**(바꾸는 파일이 겹치지 않는다. 새 그림을 붙이는 `follow_up` 코드 메모는 그림이 끝난 뒤에 생긴다).
  처음엔 "코드는 위의 그림을 기다린다" 를 넣었다가 상관없는 코드 메모까지 묶여 사용자가 지적해 뺐다
  (problem.md `[desk-parallel-overblocked]`). **검증만 칸막이** — 위에 걸린 것이 없고 두 줄이 다 쉴 때만 돌고, 아래 것은
  검증을 기다린다. 검증은 빌드 뒤 화면을 보고 코드 파일이 바뀌면 해시 가드가 되돌리므로, 코드와 함께 돌면 코드가 고친 것이 지워진다.
  예: 코드 A · 그림 B · 코드 C · 검증 D → A∥B → (A 끝나면) C → 다 끝나면 D. 백업·되돌림은 줄마다 따로 — 코드는 **차시 폴더 전체**,
  그림은 그림 파일만, 검증은 세 파일만 복사하고 표시도 `active-job-{claude|codex}.json` 으로 따로 둔다. 코드가 실패하면 작업 중에
  새로 생긴 파일은 `desk/{id}/orphans/{작업 번호}/` 로 옮긴다. 두 줄이 함께 돌았으면 상대 몫은 안 건드린다 —
  코드 되돌림은 **함께 돈 그림 작업이 실제로 바꾼 그림만** 두고(`image_lane_files`: 끝난 작업은 결과의 `images`, 도는 작업은 그 백업과
  달라진 그림) 없어진 그림은 늘 되살린다(그림 작업은 지우거나 이름을 바꾸지 않으므로 코드 몫). 처음엔 그림 파일을 통째로 안 건드렸는데
  코드가 바꾼 그림 이름까지 안 되돌아갔다. 그림 되돌림은 없어진 그림(코드가 이름을 바꿨거나 치운 것)을 되살리지 않고, 그림 스크립트도
  결과에 없는 새 파일을 치우지 않고 알리기만 한다. 실패·멈춤은 **그 작업의 메모만** 되돌린다. 자동 빌드 · 끝나면 멈춤은 두 줄이 다 끝난 뒤.
  [지금 멈춤]은 두 줄을 다 끊는다. 사용량 기록 정리(`prune_usage`)는 다른 줄이 쓰는 중이면 미룬다.
- **적으면 바로 처리한다**(2026-09-30 사용자 결정). 메모는 대기열에 들어가고, 차시마다 처리기 하나가 **위에서부터** 돈다.
  새 메모는 맨 뒤 또는 고른 메모 앞에 넣고, 대기 중인 메모는 ↑↓ 나 끌어 놓기로 옮긴다(대기 메모끼리만 —
  처리 중인 메모는 끌 수도, 그 위에 놓을 수도 없다. 서버 `move` 도 대기 중인 것만 받는다). 처리기는 줄마다 한 번에
  **같은 종류 연속 묶음**(`runnable_groups`)만 가져가고, 묶음이 끝날 때마다 대기열을 다시 읽는다 — 도는 중에 끼워 넣거나
  옮겨도 반영된다. 같은 종류를 묶는 이유는 AI 호출 고정비(클로드 약 $0.7/회)다.
- **열림(AI 가 못 한 것)은 저절로 다시 돌지 않는다.** 같은 이유로 또 실패하며 비용만 든다. 사람이 [다시 맡기기]를 누른다.
- **메모 종류는 사람이 적을 때 고른다**(2026-09-30 사용자 결정 — AI 가 나누게 하면 클로드를 한 번 더 부른다).
  역할은 사용자가 정했다: **그림·검증은 코덱스, 그 밖은 클로드.**

  | 종류 | 누가 | 스크립트 · 프롬프트 | 바꾸는 것 |
  |---|---|---|---|
  | 코드 | 클로드 | `desk_fix.py` · `prompts/desk_fix_system.md` | **차시 폴더 안의 무엇이든** — 세 파일 · 이름 바꾸기 · 데드코드·안 쓰는 파일 정리 · 메모가 가리키는 md 대로 하기 |

  코드 메모를 처음엔 "세 파일 고치기" 로 좁혀 만들었다가 사용자가 바로잡았다(2026-10-01, problem.md `[desk-code-scope-too-narrow]` —
  "이미지랑 검수만 얘가 하는 게 아니다"). 클로드 허용 명령은 자가 검사 · `mv` · `mkdir` · `cp` 이고 **`rm` 은 막는다** — 지울 파일은
  `desk/{id}/removed/{작업 번호}/` 로 옮긴다. 메모에 적힌 md 경로의 폴더는 `--add-dir` 로 연다. 자가 검사는 **깨진 그림 참조**(작업 전엔
  있던 그림 파일이 이제 없음)도 본다. 끝나고 gyo6 의 차시 폴더 밖이 바뀌었으면(git status) 결과에 ⚠ 로 적는다.
  | 그림 | 코덱스 | `desk_image.py` · `prompts/desk_image_system.md` | `assets/` 그림(같은 경로·크기). 투명은 크로마로 그리고 코드가 지운다 |
  | 검증 | 코덱스 | `desk_verify.py` · `prompts/desk_verify_system.md` | **없다.** 빌드 뒤 http 로 열어 캡처·도구로 확인만 한다 |

- **결과 표시**(2026-09-30 사용자 요청) — AI 결과를 메모에 구조로 붙인다(`lesson_notes.set_result` →
  `result: {kind, label, step, headline, detail, at, job}`). 카드는 결과 배지 + `headline` 한 줄만 보이고, `detail` 과
  작업 기록은 [자세히]로 접어 둔다(기본 접힘, 펼친 상태는 새로고침에도 유지). 세 AI 모두 출력에 `headline`(40자 안팎,
  사람 말) · `detail`(`- ` 한 줄씩, 사람이 알 것 먼저 · 기술 설명은 뒤)을 낸다. headline 이 없으면 detail 첫 문장으로 대신한다.
  다시 맡기면 지난 결과는 치운다. **처리된 메모는 최근에 적은 것이 맨 위**, 대기열은 처리 순서 그대로.
- **두 화면 공통** — 색·버튼·사이드바 틀 CSS 와 `esc`·`tok`·`postJson`·AI 모델 고르기 JS 는 `tools/desk_common.css` ·
  `tools/desk_common.js` 하나다(서버가 `/static/` 으로 정해진 이름만 내준다). 두 페이지에 같은 코드를 다시 복사하지 않는다 —
  2026-10-01 정리 때 모델 고르기 80줄 등이 글자까지 똑같이 두 벌 있었다.
- **종류 고치기**(2026-10-01 사용자 요청 — 그림으로 맡길 것을 코드로 적었다) — 메모마다 종류 칸(`lesson_notes.set_kind`,
  `/api/notes/kind`). 대기 중이면 종류만 바꾸고 자리는 그대로, 처리된 메모는 바꾼 종류로 **다시 대기열에**(지난 결과는 치운다 —
  앞서 다른 AI 가 바꾼 파일은 되돌리지 않는다). 처리 중은 거절. 종류 칸을 연 동안은 2초 새로고침이 목록을 다시 그리지 않는다.
- **대기 메모 글 고치기**(2026-10-02 사용자 요청) — 대기열의 [고치기](`lesson_notes.edit_text`, `/api/notes/text`). **대기 중일 때만** —
  AI 가 집어 간 뒤엔 프롬프트가 이미 나갔으므로 거절한다. 쓰던 글은 `el._edit` 에 두어 2초 새로고침에도 남고, 그새 메모가 처리 중이 되면 칸을 닫는다.
  붙인 그림 · 종류는 그대로(종류는 종류 칸).
- **메모에 그림 붙이기**(2026-10-01 사용자 요청) — 적기 칸에 Ctrl+V · 끌어 놓기로 캡처를 붙이면 [적기] 때 `images`
  (data URL)로 같이 올린다. 서버는 메모를 만든 뒤 같은 요청 안에서 `lesson_notes.attach` 로 `desk/{id}/attachments/{메모}/img-N.확장자`
  에 저장하고 메모의 `images` 에 적는다(png · jpg · webp · gif, 10장 · 장당 15MB — 어기면 메모째 지운다). `prompt_block(note, desk_dir)` 가
  그 **절대 경로**를 메모 끝에 붙여 세 AI 가 열어 보게 한다(desk 폴더는 코드 메모에 `--add-dir` 로 열려 있다). 카드는 `/api/desk/attachment` 로 썸네일.
- **처리기 깨우기** — 한 줄이 도는 동안 처리기는 끝난 작업을 기다린다. 그사이 메모를 적거나 옮기거나 종류를 바꾸면 `kick` 이
  `WAKE[차시]` 에 None 을 넣어 깨운다 — 그러지 않으면 코드가 도는 동안 적은 그림 메모가 코드가 끝날 때까지 쉬는 줄에서 기다린다.
- **[그림 보기]**(2026-10-01 사용자 요청) — 그림 메모가 고치거나 만든 그림을 카드에서 바로 전·후로 본다.
  그림 작업이 끝나면 결과의 `files` 를 `desk/{id}/after/{작업 번호}/` 에 복사하고 `result.images = [{path, new}]` 를 적는다
  (`keep_result_images`). 전은 작업 전 백업 `backup/{작업 번호}/`, 새 그림(백업에 없던 것)은 후만. 사본을 두는 것은 나중 작업이
  같은 그림을 또 바꿔도 이 메모가 낸 그림을 보이려는 것이다. 이 기능 전에 끝난 메모는 한 번 되채운다(`backfill_result_images` —
  마지막 결과 파일의 경로, 없으면 백업과 지금 파일의 차이. 이때 후는 지금 파일). 그림은 `/api/desk/image`(정해진 두 폴더 안의 그림만).
- 한 묶음 = 한 작업. 작업 전에 바꿀 수 있는 파일을 `desk/{id}/backup/{작업 번호}/` 에 복사한다. 검증 묶음은 빌드 → 검증.
- **빌드 지점**(2026-10-01 사용자 요청 — "A · B 까지 처리하고 빌드한 뒤 C") — 대기열에 종류 `build` 메모로 넣는다([여기까지 빌드]).
  `lesson_notes.BARRIERS` 라 검증처럼 칸막이 — 위에 걸린 것이 다 끝나고 두 줄이 쉴 때 `build_job(checkpoint=…)` 이 돌고,
  아래 메모는 그 빌드가 끝나야 시작한다. 끝나면 그 메모를 완료(멈추면 대기 · 실패면 열림)로 닫는다. 맨 끝 자동 빌드는 그대로 —
  빌드 지점 뒤로 바뀐 것이 없으면 다시 하지 않는다. [빌드] · 자동 빌드 · 빌드 지점이 `build_job` 하나를 같이 쓴다.
- **오른쪽 사이드바**(2026-10-01 사용자 요청) — [화면 보기] [빌드] [커밋 전 점검]은 카드 머리에서 빼 화면 오른쪽 고정 사이드바
  (`renderActions`)에 둔다. 보이는 차시마다 한 줄. 카드 머리에는 멈춤 버튼만 남는다. 좁은 화면(1100px 이하)에선 **왼쪽 사이드바 아래**(2026-10-02 사용자 요청 — 예전엔 본문 위로 올라갔다).
  같은 버튼을 `#act-side` · `#act-left` 두 곳에 그리고 CSS 가 너비로 한쪽만 보인다(DOM 을 옮기지 않는다).
  사이드바의 **AI 모델은 접었다 폈다**(`<details id="m-fold">`, 기본 접힘, 접힌 줄에 지금 설정, 펼침은 localStorage — 두 화면 공용).
- **자동 빌드**(2026-09-30 사용자 요청) — 대기열이 비면 [빌드]와 같은 작업(빌드 → 화면 결함 검사 → 기능 테스트)을 한 번 돈다.
  이번 대기열에서 코드·그림 작업이 **실제로 파일을 바꿨을 때만**(확인 대기로 끝난 메모가 있을 때) 한다. 검증 묶음은 직전에
  빌드하므로 그 뒤로 바뀐 것이 없으면 다시 하지 않는다. 멈춤으로 세웠으면 하지 않는다. 작업마다 빌드하지 않는 이유는
  빌드 + 검사가 4분쯤 걸려 대기열이 그만큼 밀리기 때문이다.
  - 코드: gyo6 는 `--add-dir` 로 열고, 명령은 자가 검사 `stages.scripts.desk_check` 하나만 허용한다. 이 검사는 **작업 전보다
    새로 생긴** 게이트 위반만 본다 — 사람이 만든 차시는 게이트를 처음부터 다 지키지 않으므로 전체를 보면 메모에 없는 곳을 건드린다.
  - 그림: 그리기 전후 픽셀 크기·투명 여부를 대조해 달라졌으면 결과에 ⚠ 로 적는다. 메모가 원하면 **새 그림도 만든다**
    (`assets/<역할>/<이름>.png`, assets/ 밖은 받지 않는다). 9-slice 요청이면 모서리 고정·가운데 평평하게 그리고
    4-1/03 처럼 `<이름>-9slice.json` 을 함께 낸다. 결과는 rendered · created · partial(일부만) · needs_confirm · not_done.
    새 그림을 화면에 붙이는 일은 결과의 `follow_up` 으로 넘기고, 작업대가 **대기열 바로 다음 차례에 코드 메모로** 넣는다.
    실측(2026-09-30, 4-1/04) — 덮어쓰기만 하도록 되어 있어 "CTA 버튼 새로" 를 못 했고, 로고는 실제로 다시 그려 놓고
    결과를 '확인 필요' 로 적어 자동 빌드가 안 돌았다. 그래서 일부만 한 것(partial)도 확인 대기 + 자동 빌드로 센다.
  - 검증: 코덱스는 샌드박스 없이 돌므로 프롬프트만 믿지 않는다 — 전후 해시가 다르면 코드 파일을 되돌리고 실패로 끝낸다.
    판정은 `expected`(메모가 기대하는 상태) → `observed`(본 것) → `result` 순으로 적게 한다. 실측(2026-09-30, 4-1/01) —
    "커졌는지 확인" 메모에 "눈에 띄게 크다" 고 옳게 보고도 메모를 거꾸로 읽어 failed 를 냈다. 기대를 먼저 적으니 뒤집힘이 없어졌다.
  - 결과는 메모마다 된 것(고침·그림 새로 구움·검증 통과) → 확인 대기, 나머지(그림 필요·확인 필요·못 고침·검증 실패 …) → 이유를 달고 다시 열림.
- **빌드 줄 세우기**(2026-09-30 사용자 결정) — AI 작업은 차시끼리 병렬로 돌지만 `build:lesson` 명령은 **gyo6 체크아웃마다
  한 번에 하나**만 돈다([빌드] · 자동 빌드 · 검증 전 빌드 모두). 차시별 빌드라도 gyo6 `postbuild:lesson` →
  `tools/clean-tmp.mjs` 가 레포 전체의 `*.tmp*` 를 지워, 동시에 돌던 다른 차시 빌드의 임시 파일(음성 `이름.tmp.mp3` ·
  webp 캐시 `….<pid>.tmp`)을 지울 수 있다. 뒤 차시는 "빌드 대기 — ○○ 빌드 중". 빌드 뒤 검사·테스트는 병렬.
  작업대 밖에서 사람이 직접 하는 빌드는 못 막는다 — 근본 해결은 gyo6 청소가 자기 차시만 보게 하는 것(팀 확인 필요).
- **빌드에 들어가는 메모**(2026-09-30 사용자 요청) — 빌드마다 **마지막 빌드 뒤에 AI 가 파일을 바꾼 메모**(코드·그림,
  결과 시각 > 빌드 결과물 index.html 수정 시각)를 `note_ids` 로 적는다(`unbuilt_notes`). 빌드 중 상태 줄 "포함: U03, U05",
  이력 "자동 빌드 — U03, U05 포함"(없으면 "새 메모 없음"), 빌드 전에는 "아직 빌드 안 된 메모: …".
- **수정 요청서**(2026-10-01 사용자 요청) — 나중에 오는 수정 요청 PDF 를 차시 카드에 올리면 클로드가 읽고 메모 목록으로 나눈다.
  사용자 결정: **차시 하나씩**, 나눈 항목은 **사람이 본 뒤** [대기열에 넣기]. `start_request` → `desk_request.py` —
  PDF 를 쪽 그림(`pages/page-N.png`, 번들 poppler)으로도 바꾼다(캡처 위 동그라미·손글씨는 글로 안 읽힌다). 클로드는 **읽기만** —
  `Edit` · `Write` · `Bash` 를 거부 목록으로 막는다. 나누는 작업은 파일을 안 바꿔 `SPLITS` 에 따로 둔다(JOBS 에 두면 대기열이 선다).
  카드에서 항목마다 글 · 종류 고치기 · 빼기 뒤 넣으면(`queue_request`) 메모 끝에 요청서 원문과 **쪽 그림 경로**를 붙인다 —
  처리하는 AI 가 원본 쪽을 연다(desk 폴더는 코드 메모에 `--add-dir` 로 열려 있다). 결과 `desk/{id}/requests/{작업 번호}/`.
  실측(2026-10-01, Haiku 27초) — 글 4줄 + 빨간 동그라미 친 배경 캡처 1쪽을 코드 2 · 그림 2 · 검증 1 로 나눴고, 동그라미만 있는 쪽을
  "그 배경의 가운데 인파를 줄이기" 로 옮겼으며, 자리가 모호한 "[확인] 버튼 크게" 에는 질문을 달았다.
- **커밋 전 점검**(2026-10-01 사용자 요청) — 차시를 커밋하기 전에 gyo6 `docs/DELIVERY_QA_CHECKLIST.md`(루트에 같은 사본도 있다)를
  이 차시에 돌리고 **클로드가 걸린 것을 고친다.** 결과는 **작업대에만**(gyo6 에 AUDIT 파일을 쓰면 커밋에 묻는다).
  처음엔 "코드 검사 + 코덱스, 판정만" 이었는데 4-1/03 첫 점검 뒤 사용자가 "클로드가 실행하고 클로드가 고치게" 로 바꿨다
  (problem.md `[desk-qa-judge-only]` — 실패 항목을 사람이 하나씩 메모로 옮겨야 했다).
  `start_qa` — 작업 전 백업(차시 폴더 전체, `active-job-claude.json`) → 빌드 → `stages/scripts/delivery_qa.py`(명령으로 재는 항목 —
  체크리스트 md 를 읽어 항목을 만든다, code.json) → `desk_qa.py`(클로드 — fail · warn · unchecked 를 판정하고 차시 폴더 안에서 고침,
  코드 메모와 같은 범위 · 같은 거부 목록 + `npm` · 허용 `node`, claude.json) → 다시 빌드 → 다시 코드 점검(code-after.json) →
  `desk_qa.py --finalize`(report.json · report.md). 코드로 재는 항목은 **다시 잰 결과가 최종**(고쳤다고 해도 재서 통과해야 "고침").
  공통 런타임 · 빌드 설정 · 그림 다시 그리기는 고치지 않고 `fix_hint` 로 남긴다. 실패 · 멈춤이면 차시 폴더 전체를 되돌린다.
  카드는 `latest_qa` 로 남은 실패 · 확인 필요 · 고친 것(바꾼 파일)을 상태 줄 바로 아래에 보인다(처음엔 메모 목록 밑이라 못 찾았다).
  코드 검사는 배포 21차시로 거짓 경보를 걸렀다 — 파비콘 png(B3 예외), 빌드가 wav→mp3 · png→webp 로 바꾼 것(같은 종류 stem 이면 있음),
  lesson.json 설명문 속 경로 · 메타 자리(`artDirection` · `styleRef` · `*assetPrompt`), ext JS 의 옛 이름 매핑(→ warn, AI 확인),
  차시만 빌드해 목록 페이지에 안 뜨는 것(F3 → warn).
- **빌드** — `build:lesson` → `check_rendered` → `run_functional_tests`. AI 를 부르지 않는다. AI 작업과 동시에 돌지 않는다
  (빌드가 끝나면 그사이 쌓인 대기열을 이어서 처리한다). **KB 서버 전송은 하지 않는다**
  (서버는 지금처럼 gyo6 에서 `npm run deploy`).
- **이번 작업 끝나면 멈춤**(2026-09-30 사용자 요청) — 도는 AI 작업은 끝까지 마치게 두고 다음 메모로 넘어가지 않고 멈춘다.
  그때까지 바뀐 것이 있으면 바로 빌드하고 "멈춤" 알림을 띄운다(`lesson-config.json` 의 `pause_after`, 멈추면 지운다).
  [지금 멈춤]은 그 작업을 끊고 되돌려 AI 비용을 버리므로, 중간 결과만 보려면 이쪽을 쓴다. 도는 게 없으면 그냥 멈춘다.
- **멈춤 / 다시 시작** — 멈춤은 대기열을 세우고, 도는 작업이 있으면 프로세스 트리를 끊어 **그 작업이 바꾼 것만** 되돌린다
  (그 메모는 대기로 돌아간다). 실패한 작업도 되돌리고 그 메모는 이유를 달고 열림. 그사이 사람이 직접 고친 것도 되돌아간다.
  멈춤 상태는 `desk/{id}/lesson-config.json` 의 `paused`. 작업대가 작업 중에 꺼졌으면 다음에 켤 때 되돌리고 **멈춤으로** 둔다
  (켜자마자 AI 비용이 나가지 않게). 멈추지 않은 차시의 남은 대기열은 켤 때 이어서 처리한다.
- **AI 모델**(2026-09-30 사용자 요청) — 두 화면 사이드바 아래에서 클로드 · 코덱스 모델을 고른다(`desk/config.json` 의
  `claude_model` · `codex_model`, 빈 값 = CLI 기본). 다음 작업부터 적용. 클로드 = 코드 메모 · 초안의 클로드 단계,
  코덱스 = 그림 · 검증 메모 · 초안의 그림 굽기. 목록은 각 CLI 가 받아 둔 파일에서 읽는다 — 클로드
  `~/.claude/cache/model-catalog/*-cc.json`(주 모델 + 그 밖의 버전: Opus 4.8 · 4.7 · 4.6 …), 코덱스 `~/.codex/models_cache.json`.
  **추론 강도**도 고른다 — 모델마다 지원하는 것만 보이고 "기본(추천: …)" 이 맨 위다(Haiku 는 없다). 클로드 `--effort`,
  코덱스 `-c model_reasoning_effort="…"`(`CodexClient.effort` · `ClaudeClient.effort`). 초안은 `--claude-effort` · `--codex-effort`.
  모델을 바꿨는데 그 모델이 고른 강도를 지원하지 않으면 '기본'으로 되돌린다.
  `produce_lesson.py` 는 `--claude-model` · `--codex-model` 을 따로 받는다 — 예전 `--model` 하나는 모든 단계에 같은 이름을
  넘겨서 클로드 모델을 주면 코덱스 단계(그림)가 깨졌다(`model_for`). `--model` 은 둘 다 없을 때만 쓴다.
- **알림**(2026-09-30 사용자 요청) — Windows 바탕화면 알림(`stages/scripts/notify.py`). 실패하면 바로(차시·작업·이유),
  대기열이 끝나면 자동 빌드까지 끝난 뒤 한 번(고침·못 한 것·실패 수 + 빌드 결과). `--no-notify` 로 끈다.
- **실패 이유** — 로그에서 알려진 문구를 찾아 사람이 할 일로 바꾼다(`stages/scripts/desk_failures.py`). 실측(2026-09-30, 4-1/04) —
  그림 굽기가 "종료 코드 1" 로만 두 번 실패했는데 원인은 코덱스 CLI 로그인 만료(`refresh_token_invalidated`)였다.
  `codex login status` 는 로컬 파일만 봐서 "로그인됨" 이라고 한다 — 실제 호출이 되는지는 짧게 불러 봐야 안다.
- **AI 사용량** — 작업마다 토큰·비용·시간. `DESK_STEP`(작업 번호)을 환경 변수로 넘기고 스크립트가 `usage_log.bind(tag=)` 로
  기록에 붙인다. 차시마다 **최근 10개 작업만** 남기고 나머지(번호 없는 옛 기록 포함)는 `usage-log.jsonl` 에서 지운다
  (2026-09-30 사용자 요청). 비용은 클로드만 나온다 — 코덱스는 토큰만 준다.
- **작업 경로** — AI 가 고칠 차시 폴더. 기본은 gyo6 `lessons/{차시}`, 카드에서 바꾸고 [기본으로] 되돌린다
  (`desk/{id}/lesson-config.json`, lesson.json 이 있는 폴더만 받는다). 빌드·화면 보기·검증은 그 폴더가 속한 체크아웃
  (`<root>/lessons/<학기>/<차시>` + `package.json`)에서 한다. 그 모양이 아니면(예: run 의 `lesson/`) 코드·그림만 된다.
- **화면 보기** — `/view/{학기-차시}/…` 로 그 체크아웃의 `dist` 를 http 로 연다. `file://` 은 글꼴을 막아 주아체 등이 안 보인다.
- 작업 로그 `desk/{id}/jobs/`, 이력 `jobs.jsonl`, AI 사용량 `usage-report.md`, 검증 캡처 `desk/{id}/verify/{시각}/`.

**초안 파이프라인 대시보드** — 같은 서버의 `http://127.0.0.1:8790/pipeline`(`stages/scripts/pipeline_status.py`).
run 마다 지금 어느 단계를 도는지, 실행마다·단계마다 토큰·비용·시간, run 전체 단계별 누계를 보여 준다.

여기서 **초안을 만든다**(2026-09-30 사용자 결정 — 인터뷰는 화면 답 칸, gyo6 넣기는 버튼, 음성 단계는 건너뜀).

- [+ 새 초안 만들기] — PDF 를 올리면 `desk/uploads/{run}.pdf` 에 두고 `runs/{run}/desk-draft.json`(넣을 차시 등)을 쓴 뒤
  `produce_lesson.py {pdf} --run-id {run} --through interview --no-voice` 를 돈다.
- **사람에게 묻는 자리는 인터뷰 한 번**(2026-10-02 사용자 결정 — problem.md `[interview-second-round]`). 예전에는 인터뷰 답을 받은 뒤
  `lesson_spec` 이 정할 것(open decision)을 남기면 종료 3 으로 또 멈춰 질문을 다시 받았다(g4l05 에서 21건). 이제 명세 단계는 정하지 못한 것을
  `status: "assumed"`(`정한 값 — 근거`, 학습 내용에 닿으면 `판독 불확실 — 사람 확인 필요`)로 적고, 그래도 `open` 이 남으면 코드(`settle_decisions`)가
  "정하지 못함" 으로 바꿔 진행한다. 정한 것은 `interview/assumed.md`(산출물 카드의 인터뷰 칸)에 모은다 — 틀리면 질문지에 답을 적고 다시 돌린다.
  새는 곳도 막았다 — 디자인이 질문을 문서 표(`| Q-D4 | … |`)에만 적고 `open_questions` 에 안 올리면 인터뷰에 안 실렸다
  (`table_only_questions` 가 표에서 주워 싣는다 · 디자인 프롬프트에도 적었다). 기본 질문 Q1~Q3 를 비우면 "특별한 요구 없음" 으로 본다.
- 답 대기 — 인터뷰 질문을 화면 답 칸에 적는다(`stages/scripts/interview_form.py`). 저장하면
  questions.md 를 **파이프라인이 읽는 모양**(`### Q번호. 질문` + `답: 한 줄`)으로 다시 쓴다. 여러 줄 답은 " / " 로 잇는다 —
  `read_existing_answers` 는 첫 줄만 기억해서 다음 질문지에서 뒷줄이 사라진다. 덮기 전 파일은 `questions.bak-{시각}.md`.
  [답 저장하고 이어서 만들기] → `--start-at interview_brief --interview-notes …/questions.md --no-voice`.
- 인터뷰 전에 멈췄으면 [이어서 만들기]는 올린 PDF 로 처음부터 인터뷰까지 다시 돈다(끝난 단계는 캐시). run 폴더만
  넘기면 스토리보드 경로가 비어 기획 단계가 원본을 못 본다.
- **최종 산출 경로**(2026-10-01 사용자 요청) — 넣을 곳을 run 마다 지정한다(새 초안 폼 · [gyo6에 넣기] 칸, `parse_output_path`).
  `<gyo6 체크아웃>\lessons\<학기>\<차시>` 모양이어야 한다(체크아웃 = `package.json` 이 있는 폴더) — 배치 · 빌드 · 화면 검증을 그
  체크아웃에서 한다. 차시만 적으면(`4-1/05`) 작업대의 gyo6. `desk-draft.json` 의 `target_root` · `slot` 에 기억한다.
  작업대는 설정의 gyo6 하나만 보므로 **다른 체크아웃에 넣은 차시는 작업대에 안 나타난다** — 화면 · 끝 알림에 그렇게 적는다.
- [gyo6에 넣기] — `install_lesson` → `build:lesson`(빌드 줄 세우기) → `verify_lesson --skip-llm`. 같은 차시가 있으면
  막고 [덮어쓰기로 넣기]를 보인다. 넣은 차시는 차시 작업대에 바로 나타난다.
- 알림: 답 대기 · 초안 끝 · gyo6 넣음 · 실패. 작업 로그는 `runs/{run}/desk-jobs/`.
- **산출물 카드**(2026-09-30 사용자 요청) — run 을 고르면 단계 순서대로 그 단계가 낸 파일이 버튼으로 나온다
  (`stages/scripts/run_artifacts.py` 의 `GROUPS`). md · json · css · js 는 누르면 **VS Code 로 연다**(2026-09-30 사용자 요청 —
  서버가 이 PC 에서 `code.cmd` 를 부른다, `open_in_editor`, run 안의 글 파일만). 옆 [보기]는 화면 안 보기 창 — md 는 문서 모양(화면 안의 작은 변환기,
  CDN 없이 — 프록시·오프라인에서 못 받는 일이 있었다), json 은 들여쓰기, PDF 는 새 탭. 그림(원본 쪽 이미지 · 그림 굽기 ·
  화면 검증 캡처)은 썸네일(서버가 320px JPEG 로 줄여 캐시)로 늘어놓고 누르면 원본을 크게, ← → 로 넘기고 Esc 로 닫는다.
  `/api/pipeline/file` 은 run 폴더 안의 정해진 확장자만 연다(`safe_path`). AI 가 쓴 md 안의 HTML 은 esc 해서 그대로 두지 않는다.
- 질문 열쇠는 `produce_lesson.question_key` 와 같아야 짝이 맞는다. `### A3. [구분] 질문`(이미 답한 칸)만 대괄호를 뗀다 —
  `### Q1. [DEC-01] 질문` 의 대괄호는 질문 본문이다. 예전에는 파이프라인이 A 칸 답을 다시 못 읽었다(2026-09-30 고침).

- `produce_lesson.py` 는 `pipeline_start` 에 `pid` · `stages`(이번에 돌 단계)를 적고, 단계마다 `stage_start` 를 남긴다.
  인터뷰에서 멈출 때도 `pipeline_end`(`waiting: interview`)를 남긴다. `verify_lesson.py` 는 `verify_start`(`pid`)를 남긴다.
- **도는 중**은 로그만으로 못 가른다 — 도중에 죽은 실행도 끝 기록이 없다. pid 가 살아 있고 그 프로세스가 시작 기록 즈음에
  생겼을 때만(pid 재사용 거르기) 도는 중이다. 끝 기록 없이 프로세스가 없으면 **끊김**. pid 가 없는 옛 기록은 **끝 기록 없음**.
- 토큰은 `usage-log.jsonl` 호출을 시각으로 실행에 나눠 담는다(끝 기록 뒤 90초까지 — 음성·산출물 검사 단계가 그 뒤에 적힌다).
  시작 기록이 없던 옛 검증은 앞 실행이 끝난 뒤의 `verify_lesson` 호출로 잡는다.

실측(2026-09-30, 4-1/01) — [빌드]의 기능 테스트가 "문1 두 번 틀려도 힌트가 안 뜬다" 로 걸렸는데, 검증 메모로 코덱스에게
맡기니 실제로 끌어 놓고 두 번 틀려 `합계 5000` 힌트가 뜨는 것을 캡처로 확인했다. 도구가 `.pa-hint`·`hint-cast` 만 보고
이 문항의 `.pa-canvas-sum` 을 놓친 거짓 양성이었다(`run_functional_tests.mjs` 힌트 감지 — 아직 안 고침).

완성 화면을 **스토리보드 예시화면과 대조**해 고칠 것 목록을 받는다. 원본 PDF 가 있어야 한다 —
예시화면 그림은 거기에만 있고, 전사한 `.md` 에는 설명 표만 있다.

```bash
python -B ./diff_screens.py runs/g4l02 --target {GYO6} --lesson 4-1/02 --storyboard ../스토리보드.pdf
python -B ./diff_screens.py runs/g4l02 --target {GYO6} --lesson 4-1/02 --storyboard ../스토리보드.pdf --pages 3-10
python -B ./diff_screens.py runs/g4l02 --target {GYO6} --lesson 4-1/02 --storyboard ../스토리보드.pdf --prepare-only
```

대조는 "무엇이 다른가"까지다. **그대로 적용할 수 있는 수정안**까지 받으려면 `--fix-plan` 을 붙인다.
소스(`lesson.json` · `player-ext.css` · `player-ext.js`)를 열어 앵커·현재 값·바꿀 값을 확정한다.

```bash
python -B ./diff_screens.py runs/g4l02 --target {GYO6} --lesson 4-1/02 --storyboard ../스토리보드.pdf --fix-plan
python -B ./diff_screens.py runs/g4l02 --target {GYO6} --lesson 4-1/02 --fix-plan-only   # 이미 있는 대조 결과 재사용
```

`--fix-plan-only` 는 쪽 렌더도 캡처도 대조도 다시 하지 않는다. 대조를 다시 돌리면 같은 값을 또 사서 쓰는 셈이다.

## 파이프라인 흐름

```text
storyboard readability check
      ↓
senior_planner      → planning/content-plan.md
      ↓
senior_designer     → design/wireframe.md + design/concept.md
      ↓
interview           → interview/questions.md + 사람 답변
      ↓
interview_brief     → planning/production-guide.md
      ↓
visual_design       → design/visual-design.md + design/asset-plan.md
                             + design/asset-plan.json   ← 기계용 사본
      ↓
design review log   → review/design-review-log.md
      ↓
   ┌─────────────────────────┬──────────────────────────┐
senior_developer              asset_render                ← **동시에 돈다**
→ lesson/lesson.json          → lesson/assets/*.png
  + page-map.md
  + development-notes.md
   └─────────────────────────┴──────────────────────────┘
      ↓
lesson_check + manifest generation   ← 여기까지 produce_lesson.py. **데이터만** 본다
      ↓
install_lesson
      ↓
gyo6_content build
      ↓
verify_lesson                       ← 화면 검증. 네 층을 싼 것부터
   ① check_rendered                   화면 결함 — 깨진 그림·겹침·넘침·진행 막힘
   ② run_functional_tests             문항마다 오답→재시도·힌트·정답을 **실제로 풀어** 본다
   ③ 캡처                             ②가 끝까지 걸었으면 그 경로의 전 화면(문제 상태·인증서 포함),
                                      멈췄으면 capture_lesson --scene-jump 로 나머지를 채운다
   ④ lesson_review · screen_diff      ③을 보고 판정 / 스토리보드 예시화면과 대조 (①②가 막으면 건너뜀)
      ↓
verify/to-{developer,asset,storyboard,runtime,human}.md   ← 고칠 수 있는 담당자별로 나눈다
```

`produce_lesson.py`는 각 전문가 stage의 산출물을 파일로 남긴다. 최종 개발 산출물은 기존
`lesson_draft_output` 계약을 따르므로 `install_lesson.py`로 바로 이어진다.

### 그림 규격은 **계획·구현·굽기 세 단계가 같은 문서**를 본다

`prompts/lesson_contract.md` 는 `lesson.json` 을 쓰는 단계에만 실린다. 그래서 그림을
**계획하는** 단계(`visual_design`)는 계약서를 한 줄도 못 봤고, 규격을 제 나름대로 다시 정했다.

실측 2026-09-23(`runs/g4l03`) — `asset-plan.json` 이 인물 6장을 `"허리 위까지만, 캔버스 아래
끝에서 허리가 잘림"` 으로 지시하고 `"전신을 작게 그리기"` 를 금지했다. 계약서는 정확히 반대다.
인물은 **전신**으로 그리고, 화면에서 가슴 위만 보이게 **자르는 것은 무대의 `overflow`** 다
(`--char-bottom: -46cqh` 가 머리 0.238 인 전신 비례를 전제한다). 이미 잘린 그림을 무대가 또
잘라 인물이 화면에서 더 작아졌다.

- 그림에 해당하는 규격만 `prompts/asset_spec_contract.md` 로 떼어, `visual_design` ·
  `senior_developer` · 그림 배치 프롬프트에 **모두** 싣는다(`prompt_parts.with_asset_spec`).
- `stages/scripts/asset_plan_check.py` 가 `asset-plan.json` 을 그 규격과 대조한다.
  `enforce_asset_plan()` 이 `visual_design` 직후에 걸고, 걸리면 위반 목록을 그대로 되먹여
  다시 부른다. 다 쓰고도 남으면 **멈추지 않고 크게 적는다** — 계획은 사람이 고칠 수 있는 서류다.

**이 게이트도 산문 판정으로 먼저 지었다가 접었다.** `mustInclude` 의 "무대가 아래를 잘라
**가슴 위만** 보이게 한다" 는 옳은 **설명문**이고 `forbidden` 의 "**발끝** 아래에 여백 두기" 는
옳은 **금지문**인데, 낱말로는 지시문과 못 가른다. 둘 다 거짓 양성으로 걸렸다. 그래서 값을 본다 —
인물 항목은 `"framing": "full-body"` 를 **필드로** 갖는다(`headRatio` 는 적으면 0.20~0.28).

### 투명이라고 적은 그림은 알파를 **잰다**

`transparent: true` 인데 알파가 없으면 화면에서 사각형 판이 된다. 파일은 있으니 예전에는
"끝났다" 로 셌다. `opaque_transparent_assets()` 가 재서 되먹임 목록에 넣고, 끝까지 남으면
보고서의 `skipped` 와 `pipeline-log` 에 남긴다. 판정은 `asset_alpha.has_alpha` 가 한다 —
**모드만 보면 안 된다.** RGBA 로 저장해 놓고 전 픽셀이 불투명한 경우가 있다.

### 개발과 그림은 동시에 돈다

`senior_developer` 와 `asset_render` 는 서로의 산출물을 읽지 않는다. 그림이 보는 것은
`visual_design` 이 낸 목록이고, 개발이 하는 일은 그 목록을 `lesson.json` 의 `assetPrompt` 로
옮겨 적는 것이다. 그래서 줄을 세울 이유가 없었다 — 실측으로 개발 18~36분, 그림 4~37분이었다.

겹치게 만든 장치는 **`design/asset-plan.json`** 하나다. `asset-plan.md` 는 사람이 읽는
문서라 `(공통 5)` 처럼 줄여 쓴 자리가 있어 코드가 그대로 못 쓴다. 그 줄임을 코드가 펼치려
들면 규칙이 바뀔 때마다 조용히 어긋나므로, **줄임 없이 펼친 사본을 `visual_design` 이 함께
낸다.** `asset_jobs()` 는 `lesson.json` 이 있으면 그쪽을, 없으면 사이드카를 읽는다.

- 겹치는 조건은 셋이다. 하나라도 빠지면 예전처럼 줄을 세운다 —
  두 단계가 나란히 선택됐고, 사이드카가 있고, 그림 단계를 건너뛰지 않을 때.
- **한쪽이 죽어도 다른 쪽은 끝까지 기다린다.** 그림 굽기를 중간에 끊으면 반쯤 구운 파일이 남는다.
- 끝나면 `report_asset_plan_drift()` 가 계획과 `lesson.json` 의 목록을 대조한다.
  동시 실행이 만드는 **유일한 새 위험**이 이것이다 — 개발자가 경로를 바꿔 적으면 구운 그림이
  고아가 되고 화면이 빈다. 막지는 않는다(배치 단계가 어차피 다시 본다). 조용히 지나가지만 않게 한다.

`asset_render` 의 입력은 `depends_any` 다 — `asset-plan.json` 과 `lesson/lesson.json` 중
**하나만** 있으면 된다. 사이드카가 없는 옛 run 도 그대로 돈다.

### 개발 단계만 되먹임 재시도를 돈다

`senior_developer`는 `check_lesson_standalone`이라는 촘촘한 게이트를 지나므로, 걸린 목록을
**그대로** 프롬프트에 넣어 다시 부른다(`--max-retries`, 기본 2). 요약해서 주면 모델이 다른 곳을
고친다. 실패한 `lesson.json`은 `.rejected`로 옮기고 지운다 — 남기면 다음 실행이 "이미 있음"으로
건너뛰어 깨진 산출물이 조용히 최종본이 된다.

앞 네 단계는 서류(md)를 내고 판정 기준이 schema뿐이라 되먹일 것이 없다. 그래서 루프를 걸지 않는다.

**개발 단계에 계약서가 함께 실린다.** 게이트가 요구하는 것(원자 어휘, step 4종과 `exitCondition`,
`stimulus` 필드, `sourcePanel`·`acceptance` 3줄, `ui` 배치 옵트인, 타이틀 로고 고정 파일명)이
전부 `prompts/lesson_contract.md`에만 적혀 있다. 이어 붙이지 않으면 모델은 그 규칙을 볼 길이
없는데 게이트는 그대로 판정한다 — "모르는 규칙으로 채점당하는" 상태가 된다.

### 개발 단계는 끝내기 전에 자가 검사를 돌린다 — 그 명령 하나만 허용한다

claude 단계는 `--permission-mode acceptEdits` 로 돈다(파일 수정만 허락, 명령은 거부 — 비대화형이라 허락할
사람이 없다). 그래서 개발 단계가 고친 결과를 스스로 확인하지 못하고 다음 검증에서야 알았다.

- 개발 단계에만 `--allowedTools "Bash(python -B -m stages.scripts.self_check:*)"` 를 준다(`SELF_CHECK_TOOLS`).
  `stages/scripts/self_check.py` 는 **읽기만** 한다 — 최종 판정과 같은 게이트 + `player-ext.js` 문법.
  프롬프트 끝에 명령이 실리고 "위반 0 이 될 때까지 고친다" 를 요구한다. 화면은 못 본다(배치·빌드가 필요).
- 모든 claude 호출은 `--setting-sources project` 로 부른다. 사용자 전역 설정(`~/.claude/settings.json`)의
  허용 규칙을 물려받지 않게 하려는 것이다 — 실측으로 전역의 `Bash(node -e ' *)` 등이 파이프라인에도 먹었다.
  PC 마다 전역 설정이 달라도 같은 권한으로 돈다.
- 확인(2026-09-29): 자가 검사는 실행되고 `python -c` · `node -e` 는 "requires approval" 로 거부됐다.
  `git status` 같은 읽기 전용 명령은 Claude Code 가 기본으로 허용한다.
- **확인(2026-10-01): `acceptEdits` 는 작업 폴더 안의 `mkdir` · `mv` · `rm` 같은 파일 명령을 허용 목록과 상관없이 자동 허락한다**
  (Haiku 로 `rm c.txt` 를 시켰더니 돌았다). "허용 목록에 없으면 거부" 는 파일 명령에는 통하지 않는다. 막아야 하면
  `ClaudeClient.disallowed_tools`(`--disallowedTools "Bash(rm:*)"`)로 거부해야 한다 — 같은 시험에서 `rm` · `rm -f` · `rm -rf` · `rmdir`
  가 모두 거부됐다. 지금 거부 목록을 쓰는 것은 차시 작업대 코드 메모뿐이다. 초안 파이프라인의 클로드 단계는 아직 `rm` 을 막지 않는다.

### 토큰·시간은 run 마다 기록한다

LLM 호출은 전부 `codex_client.py` 의 두 클라이언트를 지나므로 **거기서** 시간과 토큰을 잰다(`usage_log.record_call`).
실패·타임아웃도 걸린 시간을 남긴다. 어느 run 에 적을지는 진입 스크립트(`produce_lesson` · `verify_lesson` ·
`diff_screens` · `review_lesson`)가 `usage_log.bind` 로 정하고, 코드 단계(`check_outputs` · 음성 대본 ·
검증 ①②③)는 `usage_log.step` 으로 시간만 잰다. 결과는 `runs/{id}/usage-report.md`.
2026-09-29 이전 run 은 사용량을 버리고 있었으므로 기록이 없다.

실측 — "ok 만 답하라" 는 호출에도 claude 는 입력 약 5만 토큰($0.40)이 든다. CLI 가 저장소 맥락을 매번 읽는
고정비다. 단계가 많을수록 이 고정비가 쌓인다.

### 종료 코드

| 코드 | 뜻 |
|---|---|
| 0 | 이번 실행 범위까지 끝났고 확정된 위반이 없다. `--through interview`로 끊은 경우도 0이다 |
| 2 | 위반이 남았거나, **개발 단계까지 돌았는데 `lesson.json`이 없다.** 배치하지 않는다 |
| 1 | 실행 자체가 실패했다 |
| 3 | (예전) 요구 명세에 정할 것이 남아 멈췄다. **2026-10-02 부터 안 쓴다** — 인터뷰 뒤에는 멈추지 않는다(아래 "사람에게 묻는 자리는 인터뷰 한 번") |

개발까지 갔는데 산출물이 없는 것을 0으로 보고하면 자동화가 실패를 성공으로 읽는다.
`--check-only`로 들어와도 `lesson_draft.json`은 있는데 `lesson.json`이 없으면 2다.

## 역할 경계

### Lesson Draft

- 입력: 스토리보드 원본, gyo6_content 원자/훅/레이아웃 참조
- 출력: `lesson/lesson.json`, `lesson/page-map.md`, `lesson_draft.json`, 선택적 `player-ext.js`, 선택적 `player-ext.css`
- 책임: 스토리보드 내용을 gyo6_content 런타임이 읽는 lesson 데이터로 옮긴다.
- 금지: 스토리보드에 없는 학습 내용·문항·보상 구조 지어내기, `manifest.json` 직접 작성.

### Validator

- 입력: 검사 대상 JSON, schema, gyo6_content 원자 registry
- 출력: PASS/REJECT/ERROR 성격의 검사 결과
- 책임: schema, 필수 조건, 원문 누락, mojibake, 원자 사용 위반처럼 기계적으로 판정 가능한 항목을 막는다.
- 금지: 창작 판단, 임의 수정.

### Install Lesson

- 입력: `runs/{run_id}/lesson/`
- 출력: gyo6_content `lessons/{slot}/{id}/`
- 책임: 대상 폴더 충돌을 확인하고 lesson 번들을 옮긴다. 옮긴 뒤 `runs/{id}/install-record.json` 에
  run 쪽 원본과 gyo6 쪽에 쓴 파일의 해시를 남긴다(`stages/scripts/install_record.py`).
- 금지: 초안 생성, 남의 완성 차시 덮어쓰기, **gyo6 쪽에서 따로 고친 것을 조용히 덮기.**

`--overwrite` 여도 지난 배치 뒤 gyo6 쪽에서 바뀐 파일이 있으면 멈추고 목록을 보여 준다. 기록이 없는
옛 배치는 "지금 놓을 것과 다른 파일" 을 보여 주고 멈춘다(어느 쪽이 새것인지 못 가르므로). gyo6 쪽
수정이 맞으면 run 으로 먼저 가져오고, 버려도 될 때만 `--discard-target-changes` 를 붙인다.

실측(2026-09-29, 4-1/03) — gyo6 쪽에서 그림 6장을 다시 굽고 그림 지시 2곳을 고쳤는데 run 은 몰랐다.
`--overwrite` 가 그것을 경고 없이 덮었다. 화면 결함의 원인도 같았다 — gyo6 쪽에서 다보탑을 탑이
가운데인 그림으로 다시 구웠는데 각 좌표는 탑이 왼쪽인 옛 그림 기준이라 각이 하늘에 떴다.
`verify_lesson.py` 도 이 기록으로 "검사할 화면이 이 run 의 것인가" 를 내용으로 본다(시각만 보면 통과했다).

### Lesson Review

- 입력: 배치·빌드된 차시 화면 캡처, lesson, 선택적 스토리보드
- 출력: `lesson_review_{slot-id}.json`
- 책임: 실제 화면에서 진행 불능, 누락, 가독성 문제를 찾는다.
- 금지: 직접 수정.

### Screen Diff

- 입력: **스토리보드 PDF 쪽 이미지**(번들 poppler 로 렌더), 배치·빌드된 차시 화면 캡처
  (기본은 `--scene-jump` — base 의 `?dev` 장면 이동으로 **문제 화면까지** 찍는다), lesson
- 출력: `screen_diff_{slot-id}.json`, `review/screen-diff-{slot-id}.md`
- 책임: 완성 화면이 **기획된 그림처럼 보이는가**를 쪽 단위로 짝지어 보고, 고칠 것을 적는다.
  배치·비례·색·글자·연출이 대상이고, 항목마다 어느 파일을 고칠지(`lesson.json` ·
  `player-ext.css` · `player-ext.js` · `asset`)까지 정한다.
- provider 는 **codex 고정**이다. 그림을 여는 도구가 그쪽에만 있어서, claude 로 부르면
  경로만 읽고 "봤다"고 답하는 대조가 된다. `asset_render` 가 codex 고정인 것과 같은 이유다.
- 금지: 판정("좋다/나쁘다")만 적기, 직접 수정, 화풍 차이를 `asset` 항목으로 올리기
  (예시화면은 "디자인을 위한 단순 참고용"이라 구성·배치·비례만 지시다).

**Lesson Review 와 축이 다르다.** 게이트는 **결함**을 보고 이 대조는 **의도**를 본다.
둘은 겹치지 않으므로 하나로 합치지 않는다.

### Verify Lesson (`verify_lesson.py`)

- 입력: 배치·빌드된 차시, `runs/{id}/` (lesson · spec · tests/functional-test-plan.json · asset-plan.json · 스토리보드)
- 출력: `runs/{id}/verify/` — `report.md` · `findings.json` · `test-results.json` · `to-{담당}.md` · `to-asset.json`
- 책임: 위 네 층을 돌리고, 걸린 것을 **고칠 수 있는 담당자**로 나눈다(`stages/scripts/verify_routing.py`).
- 금지: 배치·빌드(만드는 일과 남의 레포를 건드리는 일을 섞지 않는다), 직접 수정,
  못 본 화면이나 못 끝난 검사를 통과로 세기.

**기능 테스트는 어떻게 답을 아는가.** base 의 모든 문제는 `PROBLEM_ATOMS[k].mount(host, spec, ctx)` 를
지난다(ext 원자도 같은 표에 등록된다). 그 mount 를 감싸 사양(정답 포함, `randomizeProblem` 결과까지)과
채점 통로 `ctx.submit` 을 잡는다. `choicePick`·`multiPick`·`keypad`·`judgeRows` 는 **실제 버튼을 눌러** 풀고,
그 밖의 원자(드래그·ext 원자)는 `ctx.submit` 을 직접 불러 **흐름만** 본다. 어느 쪽이었는지는 결과에
`mode: ui | flow-only` 로 반드시 남긴다 — flow-only 는 그 원자의 채점 로직을 안 본 것이다.

**담당자 가르기** — 한 곳에서 다 고치려 하면 엉뚱한 자리를 고친다.

| 담당 | 무엇이 오는가 | 어떻게 보내는가 |
|---|---|---|
| developer | 배치·겹침·기능 실패·진행 막힘·원문과 다른 문구 · **그림↔좌표 불일치** | `--screen-report verify/to-developer.md` 로 개발 단계 재실행 |
| asset | 그림 **자체**가 잘못 그려진 것, 굽지 못한 그림 | `--rerender-from verify/to-asset.json` 으로 그 그림만 다시 굽기 |
| storyboard | 화면 문구가 **스토리보드 원문 그대로**인데 틀렸다는 지적 | 원고 담당 확인 → 인터뷰 답으로 반영 |
| runtime | base(player.js)에서 난 오류 | gyo6 쪽에 알린다 |
| human | `unknown` · 검사 도구가 끝까지 못 돈 것 · "장면 누락?"(구현 누락인지 캡처 누락인지 못 가른 것) | 사람이 담당을 정한다 |

- 그림↔좌표 불일치는 **개발**이다. 구워진 그림을 기준으로 좌표를 맞춘다 — 다시 구워도 같은 자리에 나온다는
  보장이 없다(개발과 그림이 동시에 돌아 개발자는 그림을 못 보고 계획만 보고 좌표를 잡는다).
- 원문 판정은 **인용문이 원문에 그대로 있는가**만 본다(`verbatim_in_source`, 네 글자 이상). 문구 지적
  (`fix_target: lesson.json`)에만 건다 — 배치 지적은 글이 원문과 같아도 개발 몫이다.
- 그림 경로를 못 정하면 `to-asset.json` 에 **빈 경로로 남긴다.** 짐작으로 엉뚱한 그림을 다시 굽지 않는다.
- 막는 것은 `blocking`(코드 판정: ①② 게이트·기능 실패)과 `high`(LLM 의 "이대로 못 내보낸다")다.

### Screen Fix (`--fix-plan`)

- 입력: `screen_diff_{slot-id}.json`, 같은 쪽 이미지와 화면 캡처, **번들 소스 3종**
- 출력: `screen_fix_{slot-id}.json`, `review/screen-fix-{slot-id}.md`
- 책임: 대조 항목을 **그대로 적용할 수 있는 수정안**으로 내린다. 항목마다 파일·앵커(CSS 선택자 ·
  JSON 경로 · 함수명)·현재 값·바꿀 값·환산 근거·확인 방법·딸려 틀어질 것을 채운다.
  적용 순서도 낸다(기하 먼저, 그 위에 얹히는 것 나중).
- 왜 두 번 부르는가: 1차는 그림만 보면 되지만 2차는 **소스까지** 봐야 한다. 한 번에 시키면
  `약 65~70% 로 줄인다` 처럼 그대로 못 고치는 문장이 나온다(실측 2026-09-11).
- 금지: 값을 추측해서 채우기(정할 수 없으면 `needs_decision` 으로 넘긴다), base 수정안 내기,
  `!important`, 데이터로 되는 것을 CSS 로 고치기, 배치로 해결되는 것을 그림 다시 굽기로 넘기기.

## run 디렉토리 구조

```text
runs/{run_id}/
  storyboard.pdf              # 원본 사본. 확장자는 입력에 따라 달라진다.
  pipeline-log.jsonl
  planning/
    content-plan.md
    production-guide.md
  design/
    wireframe.md
    concept.md
    visual-design.md
    asset-plan.md
  interview/
    questions.md
  review/
    design-review-checklist.md
    design-review-log.md
  lesson_draft.json           # lesson 초안 보고서
  screen_diff_{slot-id}.json  # 화면 대조 원본 판정
  screen_fix_{slot-id}.json   # 수정안 원본 판정
  lesson/
    lesson.json
    player-ext.js
    player-ext.css
    manifest.json
    page-map.md
  review/
    storyboard-pages/         # 스토리보드 PDF 쪽 이미지 (pdftoppm)
    {slot-id}/                # 완성 화면 캡처 + capture.json
    screen-diff-{slot-id}.md  # 무엇이 다른가
    screen-fix-{slot-id}.md   # 어느 줄을 무엇으로 — 순서대로 적용한다
  install-record.json         # install_lesson.py — {target|lesson: 원본 해시 · 배치한 파일 해시}
  usage-log.jsonl             # 한 줄 = LLM 호출 1회(시간·토큰·비용) 또는 코드 단계 1개(시간)
  usage-report.md             # 위를 사람이 읽는 표로 — 기록할 때마다 다시 만든다
  verify/                     # verify_lesson.py
    report.md                 # 층별 결과 · 담당자별 건수 · 다음 명령
    findings.json             # 모든 지적 (담당자·심각도·근거 캡처)
    test-results.json         # functional-test-plan 의 케이스별 결과
    rendered.json             # ① check_rendered --json
    lesson_review.json        # ④-1
    screen_diff.json          # ④-2
    to-developer.md · to-asset.md · to-asset.json · to-storyboard.md · to-runtime.md · to-human.md
    screens/                  # ③ 캡처 + ② 상태별 캡처(f*.png) + functional-results.json
    rejected-assets/{시각}/   # --rerender-from 이 치운 원본 그림 (lesson/ 밖 — 배치에 안 섞인다)
```

## 실패에서 배운 것

### 스토리보드 세부는 **어느 단계에서도 요약하지 않는다**

> 규칙화 2026-09-11 · `problem.md` `[planner-storyboard-detail-loss]` 5회 누적 · 전문은 `solved-log.md`

- 스토리보드의 문항·보기·정답·대사·연출 지시는 **어느 단계에서도 요약하지 않는다.**
  지침서·계획서처럼 줄여 쓰는 문서라도 이 항목만은 원문 그대로 옮긴다.
- 각 단계는 자기가 옮긴 항목에 **원본 출처**를 함께 적는다 — 몇 쪽, 설명 표 몇 번,
  아니면 예시화면 그림인지. 출처가 없으면 "무엇이 빠졌는가"를 기계적으로 물을 수 없다.
- 옮기지 못한 것은 **`unmapped`에 사유와 함께 보고한다.** 못 본 것을 안 본 채로 넘기지 않는다.
- 하류 단계는 요약본이 아니라 **원본 문서를 직접 읽을 수 있어야 한다.**
  `STAGES[].depends_on`에 원본을 넣는 것이 프롬프트 문구보다 먼저다.

**손실 지점이 회차마다 달랐다는 것이 이 규칙의 핵심이다.** 한 군데를 막으면 다음은 다른 데서 샌다.

| 회차 | 손실 지점 |
|---|---|
| 1–3 | planner가 문항·보기·정답을 한 줄로 압축 / 정답 공란 / 출제 규칙 소실 |
| 4 | `content-plan.md` → `production-guide.md` 요약. 개발 단계가 원본을 **읽지 않는 구조**였다 |
| 5 | PDF → 전사 `.md`. 설명 표만 옮기고 **예시화면 그림 속 말풍선**을 버렸다 |

재발하면 고치기 전에 **이번엔 어디서 샜는지**부터 적는다.

### 화풍은 **사람이 고른 기준 그림**으로 묶는다 — 말로 정도를 주지 않는다

> 규칙화 2026-09-30 · `problem.md` `[lesson-assets-wholesale-regeneration]` 5회 누적

그림을 통째로 다시 굽는 일이 다섯 번 반복됐다. 4-1/04 한 차시에서만 네 번이었다. 공통 원인은
**화풍을 사람이 정하는 자리가 없다**는 것이다.

- **기준 그림을 먼저 한 장 굽고 사람에게 승인을 받는다.** 승인 전에 나머지를 굽지 않는다.
  역할(배경·인물·UI)마다 기준을 따로 고른다. 아이콘 한 장으로 배경까지 묶었더니 배경이 너무 평면이 됐다.
- 승인된 그림은 `--style-anchor <그 경로>` 로 고정한다. 그 역할의 나머지 그림은 그 파일을 **열어**
  외곽선 굵기·선 색·면 채색·그림자 세기까지 맞춘다.
- 화풍의 **정도**("실사를 조금만")는 말이 아니라 **참고 그림으로** 준다. "반실사"라고 적었더니 사진 쪽으로 너무 갔다.
- 기준 그림이 바뀌면 **그 역할의 그림을 전부** 다시 굽는다. 몇 장만 다시 구우면 한 벌이 깨진다.
  실측(2026-09-30): 배경 8장을 따로 구웠더니 외곽선과 채색이 제각각이었다.
- `--rerender-from` 은 먼저 원본을 `verify/rejected-assets/` 로 치운다. 기준으로 쓸 그림은 **치우기 전에**
  다른 곳에 복사해 두고 그 사본을 가리킨다.

승인을 받으려고 멈추는 자리(인터뷰 뒤 기준 그림 고르기)는 아직 코드에 없다. 지금은 사람이 순서를 지킨다.

### 옵트인 선언은 그 선언이 **요구하는 나머지와 한 묶음**이다

> 규칙화 2026-09-22 · `problem.md` `[gates-pass-but-screen-empty]` 9회 누적

base 가 `ui.*` 나 컷 필드로 켜 주는 기능은 **켜기만 해서는 화면이 완성되지 않는다.**
켠 쪽이 나머지를 채운다 — 무엇을 채워야 하는지 모르면 **켜지 않는다.**

실측 두 건이 같은 형태였다. 초안 3개가 전부 켜 놓고 전부 나머지를 안 채웠는데
**게이트·빌드·화면검사가 다 통과했다.**

| 켠 것 | 채워야 하는 나머지 | 안 채우면 |
|---|---|---|
| 컷의 `speechText` | `bubbleType: "narrationNext"` | 스피커·`다음 ▸` 이 통째로 안 나온다 |
| `ui.castOnStage: "keep"` | `#app .cast-extra img { width: 100% }` | 말하지 않는 인물이 원본 픽셀로 떠서 혼자 거대해진다 |

**말풍선 컨트롤** — base 는 `type !== 'plain'` 일 때만 컨트롤을 그리고 `다음 ▸` 은
`narrationNext` 에서만 붙인다(`player.js:1972`). 선언이 없으면 **소리가 타입을 정한다**
(`resolveBubbleType`, 1932행 — `if (!hasSound) return 'plain'`). 배포 17차시는 대사 컷
287개 중 286개가 선언을 안 하고도 멀쩡한데, 그쪽은 `sound` 를 달고 있어서다(244개).
**우리는 오디오를 만들지 않으므로 그 통로가 없다** — 안 적으면 전부 `plain` 이다.

사용자 결정(2026-09-22): **모든 말풍선에 `다음` 버튼과 스피커 아이콘을 기본으로 넣는다.
오디오가 아직 없어도 강제로 나오게 한다. 빼는 것은 사람이 정한다.**
그래서 `plain` 은 기본값이 아니다. `speechText` 가 있는 컷에는 `narrationNext` 를 적는다.

**말하지 않는 인물** — `updateCastExtras`(1876행)가 만드는 `<img>` 에는 클래스도 id 도 없다.
base CSS 는 말하는 쪽만 `#charImg{width:100%}`(player.css:487)로 잡고 `.cast-extra img` 에는
크기를 안 준다(2390행은 `display`·`filter` 뿐). `castOnStage:"keep"` 인 배포 4차시는
**예외 없이** 차시 CSS 에서 크기를 준다 — 문서에만 없었던 사실상의 계약이었다.

게이트 두 종을 넣었다. 둘 다 **배포 17차시 거짓 양성 0건**을 먼저 확인했다.

- `bubble_controls_missing` — **소리가 하나도 없는 차시**에서만 건다. 오디오가 있으면
  선언 없이도 컨트롤이 켜지므로 거기 걸면 거짓 양성 286건이다.
- `cast_extra_unsized` — `castOnStage:"keep"` 인데 `.cast-extra img` 에 `width`/`height` 가 없으면 건다.

### 연출·배치 지시는 산문이 아니라 **필드로만** 화면에 닿는다

컷의 `action` 산문에 `"편지를 클릭하면 화면이 밝아지며 전환"`이라고 적어도 아무 일도 안 일어난다.
런타임은 `backgroundRef`·`motion`·`sound`·`characterEmotion`·`characterPosition`만 읽는다.
그리고 **산문은 어떤 게이트도 못 읽는다** — schema PASS · `lesson_check` PASS · 빌드 성공을
전부 통과한 뒤 사람 눈에만 걸렸다(2026-09-11, 3-1/05에서 장면별 인물 위치와 전환 연출이 전멸).

연출은 `action`(사람이 원문과 대조하는 자리)과 필드(화면을 움직이는 자리) **양쪽에** 적는다.

### 중간 단계가 요약하면 하류는 **그 존재 자체를 모른다**

같은 사고의 상류 원인이 이것이다. 스토리보드 → `planning/content-plan.md`까지는 장면별
인물 배치표가 정확히 남아 있었는데, `interview_brief`가 `production-guide.md`로 요약하면서
떨어뜨렸다. 그런데 `senior_developer.depends_on`에는 `content-plan.md`가 없어 개발 단계가
원본 계획을 **읽을 수조차 없었다.**

- 하류가 원본을 직접 볼 수 있게 `depends_on`을 넓히는 것이 프롬프트 문구보다 먼저다.
- 요약 단계에는 "이 표는 줄이지 말고 그대로 옮긴다"를 명시한다.
- 누락을 기계적으로 물으려면 **출처가 있어야 한다.** 컷의 `source`가 그 자리다.

### 게이트는 배포 차시에서 거짓 양성 0건일 때만 넣는다

`action` 산문의 키워드로 빠진 필드를 추론하는 게이트를 만들어 배포 차시에 돌렸더니 거짓 양성
3건이 나왔다 — 오디오 전용 컷의 표정 지시, 같은 배경 안의 서사적 "장면 전환", base가 이미
하는 CTA 페이드인. **산문에서 의도를 추론하는 게이트는 0 거짓 양성이 안 된다. 넣지 않는다.**

대신 **필드가 있는가**만 보면 갈린다. 배포 17개 차시의 컷 606개가 전부 `source`와 `layer`를
들고 있었고(예외 0건) 우리 차시만 0이었다. `timing`·`motion`·`sound`는 차시별 편차가 커서
못 쓴다. 새 게이트를 만들기 전에 **배포 차시에서 그 신호가 갈리는지부터 센다.**

### 학습자 경로만 밟으면 **문제 화면은 한 장도 안 찍힌다**

`tools/capture_lesson.mjs` 는 학습자가 누르는 길을 그대로 밟는다. "눌러도 안 넘어가는" 결함이
그 과정에서 드러나므로 맞는 설계다. 그런데 그 길은 **문제 앞에서 멈춘다** — 드래그·선 긋기·
키패드를 자동으로 풀 수 없기 때문이다.

실측(2026-09-11) — 3-1/05 에서 찍힌 15장이 전부 컷씬이었고 미션 다섯 개의 배치는 한 장도
안 찍혔다. 화면 대조가 문제 배치를 한 건도 안 낸 것은 판정을 안 해서가 아니라 **볼 수가
없어서**였다. 안 찍힌 화면은 어떤 검사도 못 본다.

- 배치를 보는 것이 목적이면 `--scene-jump` 를 쓴다. base 가 `?dev` 로 여는 장면 이동
  패널(`.dev-scene-jump`)에 장면·대화 묶음·문제마다 버튼이 있어 풀지 않고 전부 닿는다.
- 패널은 찍을 때 숨기고, 누르는 것은 페이지 안에서 `el.click()` 으로 한다 —
  숨긴 요소는 좌표 클릭이 안 먹는다.
- **두 모드를 다 남긴다.** 장면 이동은 진행 가능 여부를 못 본다(전부 점프하므로).
  그건 기본 모드와 `check_rendered.mjs` 의 몫이다.

### 움직이는 화면에서는 playwright 기본 클릭이 **영영 안 눌린다**

`page.click()` 은 요소가 "visible · enabled · **stable**" 해질 때까지 기다린다. 그런데 이
런타임은 버튼이 계속 움직인다 — 타이틀 숨쉬기, 말풍선 팝, 커서 따라다니기. 그래서 버튼이
끝내 안정되지 않고 클릭이 타임아웃한다.

실측(2026-09-11) — `tools/capture_lesson.mjs` 가 타이틀의 `편지를 클릭하세요` 를 못 눌렀고,
실패를 `.catch(() => {})` 로 삼킨 뒤 **같은 버튼을 15번 다시 눌러** 같은 화면 15장을 남겼다.
`stuck` 검사에도 안 걸렸다 — 타이틀이 애니메이션 중이라 픽셀 지문이 매번 달랐기 때문이다.
`review_lesson.py` 도 같은 캡처기를 쓰므로 그동안 같은 것을 보고 있었다.

- 일반 클릭이 실패하면 **`force: true` 로 한 번 더** 누른다.
- **삼키지 않는다.** force 가 필요했다는 사실을 `click_notes` 에 남긴다 — 그게 "버튼이
  가려졌다"는 신호일 수도 있다.
- 겹쳐서 못 누르는 것은 `tools/check_rendered.mjs` 가 따로 본다. 캡처기의 일은 끝까지 도는 것이다.

### 문자열 매칭 게이트는 주석을 먼저 걷어낸다

`check_ext_css`는 `.charzone`·`.speech`·`!important`·단위를 문자열로 찾는다. 그래서 CSS
주석에 적은 경고 문구를 규칙으로 읽었다 — `.charzone 에 overflow:hidden 을 걸면 안 된다`는
주석이 `layout_conflict`로 잡혀 멀쩡한 번들이 반려됐고, 주석의 `216px`·`547px` 같은 실측
메모가 px 카운트에 섞여 cq:px 비율까지 왜곡했다. 줄 앞이 `/*`인지만 보는 필터로는 **블록
주석의 둘째 줄부터** 못 막는다. `strip_css_comments()`로 본문만 남겨 검사한다.

### base가 `var(--...)`로 통로를 냈으면 **변수만 바꾼다**

인물 크기·자리를 규칙으로 이기려다 두 번 연속 화면을 깼다.

| 한 것 | 일어난 일 |
|---|---|
| `.charzone { overflow: hidden }` | `.speech`가 `.charzone`의 자식이라 말풍선까지 잘렸다 |
| `#charImg { position: absolute }` | zone 높이가 0으로 접혀 인물이 무대 밖(y=720)으로 나갔다 |

base의 `#app.char-fixed-y .charzone.char-left`는 명시도 (1,3,0)이라 밖에서 이기려면 선택자를
계속 키우게 된다. 그쪽은 이미 `--char-bottom`·`--char-width`로 통로를 냈다. 그리고 수치는
지어내지 말고 **배포된 차시의 같은 자리 값**을 찾아 기준으로 삼는다.

## 금지

- `runner.py` 기반 HTML 파이프라인을 다시 호출하거나 문서화하지 않는다.
- `output/index.html`을 초안 산출물로 삼지 않는다.
- builder/design/content 루프를 새 초안 경로로 되살리지 않는다.
- 모델이 `manifest.json`을 쓰게 하지 않는다. manifest는 코드가 만든다.
- 사용자 확인 없이 배치 대상의 기존 production 차시를 덮어쓰지 않는다.
