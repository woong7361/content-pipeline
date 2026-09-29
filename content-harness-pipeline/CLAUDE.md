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
**가져오기(내려받은 파일 ↔ 대사 짝짓기)는 아직 없다** — 웹 편집기가 내려받는 파일 형식을 본 뒤 만든다.

```bash
python -B ./voice_lesson.py runs/g4l02                  # 대본 내보내기(멈춤, 종료 코드 3) / 받은 파일 확인
python -B ./voice_lesson.py runs/g4l02 --dry-run        # 소리를 붙일 줄·글자 수만
```

가져오기가 생기면 `lesson/assets/audio/narration/vo-*.mp3` 로 놓고 `lesson.json` 에 `audioMap.narration` 과
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
