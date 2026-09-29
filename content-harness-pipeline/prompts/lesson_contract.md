# lesson 산출물 계약

`lesson_builder`가 지키는 계약이다. 산출물은 HTML이 아니라 **gyo6_content가 읽는 `lesson.json`**이다.

이 계약이 `common_html_contract.md`를 대체한다. 두 계약을 함께 적용하지 않는다 — 산출물이 다르다.

## 왜 HTML이 아닌가

gyo6_content는 `lesson.json`을 읽어 공통 런타임(`runtime/src/player.js` + `runtime/styles/player.css`)이
화면을 그린다. HTML은 `npm run build:lesson`이 만드는 **파생물**이다.

그래서 HTML을 만들어 넘기면 두 가지를 동시에 잃는다.

- **공통 UI가 통째로 빠진다.** 헤더 차시 목록, 소리 설정 팝업, 이전 문제로, 완료 인증서,
  세로화면 90° 회전은 base 런타임이 소유하며 `lesson.json` 선언만으로 붙는다.
- **다음 빌드에 지워진다.** `dist/`는 `lessons/`에서 재생성되는 산출물이라 손으로 고쳐도 남지 않는다.

`output/common.css`·`output/common.js`도 만들지 않는다. 그 자리는 base 런타임이 이미 차지하고 있다.

## 산출물 계약

차시 폴더는 네 파일로 이뤄집니다. 그중 셋을 당신이 쓰고, 하나는 코드가 만듭니다.

```text
RUN_DIR/lesson/
  lesson.json        ← 당신이 씁니다. 런타임이 읽는 데이터
  player-ext.js      ← 당신이 씁니다. 원자로 안 되는 것만. 필요 없으면 만들지 않습니다
  player-ext.css     ← 당신이 씁니다. 차시 전용 스타일. 필요 없으면 만들지 않습니다
  manifest.json      ← 코드가 만듭니다. 쓰지 마십시오
```

- `manifest.json`은 asset 배치와 `lesson.json`의 참조에서 전부 유도되므로 **지어낼 자리가 없습니다.**
  코드가 gyo6_content의 `manifestWriter.mjs`와 같은 모양으로 만듭니다.
- 만든 파일은 `player_ext_js_path`·`player_ext_css_path`로 보고합니다. 안 만들었으면 빈 문자열입니다.
- 이미지 파일을 복사하거나 옮기지 않습니다. 어디에 놓을지만 `asset_placements`로 **보고**하고,
  실제 복사는 코드가 합니다.
- 출력 JSON은 `schemas/lesson_builder_output.schema.json` 계약에 맞춥니다. 유효한 JSON 객체 하나만
  출력하고 설명이나 마크다운 코드블록을 붙이지 않습니다. schema에 없는 필드를 출력하지 않습니다.
- 실행 메타데이터(`brief_hash`, `stage`, `model` 등)는 runner가 붙이므로 출력하지 않습니다.

## lesson.json 뼈대

```jsonc
{
  "specVersion": 2,              // 필수. 빠지면 검증기의 스토리보드 충실도 검사가 꺼진다
  "id": "<차시 id>",
  "title": "<차시 제목>",
  "subject": "수학",
  "grade": "<학년>",
  "lessonNo": "<학기-차시>",
  "domain": "<영역>",
  "duration": 15,
  "artDirection": { ... },       // planner art_direction에서 옮긴다
  "cast": { ... },               // 등장인물. characterRef가 가리키는 키
  "audioMap": { ... },           // 없으면 생략
  "ui": { ... },                 // 공통 UI 선언. 아래 참조
  "steps": [ ... ]               // intro → (tutorial) → problemBank → outro 순서
}
```

### 식별자는 배치 위치에서 나옵니다

`id`와 `lessonNo`는 **이 차시가 커리큘럼의 어느 칸인가**를 나타냅니다.
`INPUT_JSON`이나 화풍 참조 세트의 이름에서 가져오지 않습니다.

| 필드 | 값 | 예 |
|---|---|---|
| `id` | 차시 번호 두 자리 | `"01"` |
| `lessonNo` | `{학기}-{차시번호}` | `"1-01"` |
| `grade` | 학년 한 자리 | `"4"` |

**화풍 참조 세트의 `id`(`gyo6-1-1-04-basic` 같은 것)를 차시 식별자로 쓰지 않습니다.**
그것은 "어느 화풍을 따르는가"이지 "몇 학년 몇 차시인가"가 아닙니다.
실측으로 확인된 것입니다 — 참조 세트 이름이 `gyo6-1-1-04`였더니
`id`가 `gyo6-1-1-04-big-numbers-museum`, `lessonNo`가 `1-1-04`으로 나왔습니다.

### 피드백 이미지는 `ui`에 선언합니다

정오 판정을 도장·배지 이미지로 보여주는 코스라면, 그 이미지를 **차시에 한 쌍 선언**합니다.
문항마다 문구를 쓰는 대신 런타임이 판정 때 이 이미지를 띄웁니다.

```jsonc
"ui": {
  "feedbackCorrectRef": "assets/ui/<정답 도장>.png",
  "feedbackWrongRef":   "assets/ui/<오답 도장>.png"
}
```

- `asset_plan`에 정오 도장이 계획돼 있으면 **반드시 이 두 필드로 연결합니다.**
  선언하지 않으면 도장을 만들어 놓고 화면에 띄울 통로가 없습니다.
- 이 경우 문항의 `feedback.correct`/`wrong`은 비워 둡니다.

### step은 `id`로 이어집니다. `exitCondition`이 없으면 화면이 안 넘어갑니다

런타임은 이렇게 다음 화면으로 갑니다.

```js
goToStep(step.exitCondition?.transitionTo)   //  L.steps.findIndex(s => s.id === targetId)
```

**`id`가 없으면 찾을 대상이 없고, `exitCondition`이 없으면 `transitionTo`가 `undefined`라
버튼을 눌러도 아무 일도 일어나지 않습니다.**

실측으로 확인된 것입니다 — 세 step 모두 `exitCondition`이 없어 `[시작하기]`를 11번 눌러도
타이틀 화면에 머물렀습니다. **데이터는 유효했고 검증기도 빌드도 통과했습니다.**

```jsonc
{
  "id": "step-1",          // 필수. step-1, step-2, … 순서대로
  "index": 1,              // 필수. 1부터
  "type": "intro",
  "exitCondition": { ... } // 마지막 step 을 뺀 모든 step 에 필수
}
```

`exitCondition`은 step 타입마다 형태가 다릅니다.

| step | `type` | 함께 쓰는 것 |
|---|---|---|
| `intro` | `buttonClick` | `buttonText` · `transitionTo` · `transitionType` |
| `tutorial` | `allMissionsComplete` | `buttonText` · `transitionTo` · `transitionType` |
| `problemBank` | `allProblemsComplete` | `transitionTo` · `transitionType` |
| `outro`(마지막) | 없어도 됩니다 | — |

- **`transitionTo`는 실제로 존재하는 step의 `id`여야 합니다.** 없는 id를 가리키면 조용히 아무 일도 안 합니다.
- 큰 단계 이동에는 `"transitionType": "smoothFade"` 를 씁니다.

- **`steps` 순서를 지킵니다**: `intro` → `tutorial` → `problemBank` → `outro`.
- **`tutorial`은 필수가 아닙니다.** planner에 "안내를 받으며 함께 풀어보는" 단계가 없으면 넣지 않습니다.
  없는 단계를 채우려고 문제를 지어내지 않습니다.
- **`world`와 `trophyCriteria`를 넣지 않습니다.** 런타임이 읽지 않는 옛 스키마 필드입니다.

## 공통 UI는 선언만 합니다

아래 넷은 base 런타임이 소유합니다. 선언만 하면 붙습니다. **자체 구현을 넣지 않습니다.**

| UI | 선언 |
|---|---|
| 헤더 차시 목록(햄버거) | `"ui": { "courseMenu": {} }` — 빈 객체로 충분. 목록은 빌드가 채운다 |
| 소리 설정(효과음·배경음·음성) | 선언 불필요. 자동으로 붙는다 |
| 이전 문제로 | `"ui": { "prevProblem": true }` |
| 차시 완료 인증서 | `"ui": { "certificate": { ... } }` |

`courseMenu.lessons[]`를 손으로 채우지 않습니다. 빌드가 카탈로그에서 계산해 주입합니다.

### 배치·연출 옵트인 — 선언이 없으면 **안 나오는 것이 정상 동작**입니다

아래는 base 런타임이 실제로 읽는 필드입니다. 선언하지 않으면 그 UI 는 오류 없이 그냥 안 뜹니다.
**화면이 비어 보이는데 아무 게이트도 안 걸리는 자리가 여기입니다** — 데이터는 유효하고 빌드도 됩니다.

| 선언 | 값 | 무엇이 붙는가 |
|---|---|---|
| `ui.sceneLayout` | `"lesson"` | base 의 캐릭터·말풍선 **기하**가 꺼지고 `player-ext.css` 가 장면별 배치를 전부 소유합니다. 스토리보드마다 연출이 다른 신규 차시는 이쪽입니다 |
| `ui.stageRail` | `{}` | 헤더 우측 진행 선(지금 어느 단계인가) |
| `ui.castOnStage` | `"keep"` | 앞 장면의 인물이 자기 자리에 남습니다. `specVersion: 2` 가 함께 있어야 켜집니다 |
| `ui.speechBubble.side` | `"above"`(기본) · `"left"` · `"right"` | 말풍선이 캐릭터의 어느 쪽에 붙는가 |
| step 안의 `character.position` | `"left"` · `"right"` · `"center"` | 그 화면에서 인물이 서는 자리. 미지정 시 `intro` 는 right, 나머지는 left |
| step 안의 `concept` · `location` | 문자열 | 화면에 나오는 단계 안내와 장소 표시 |
| `problemBank` 의 `totalProblems` | 정수 | 진행 표시의 분모 |
| `outro` 의 `clearSequence` | 배열 | 완료 연출 순서 |

`sceneLayout: "lesson"` 을 선언하면 base 기하 게이트가 꺼지므로, 이 차시가 지나가는 **모든**
모드(intro·tutorial·problemBank·outro)의 캐릭터·말풍선 배치를 `player-ext.css` 가 빠짐없이
선언해야 합니다. base CSS 위에 오버라이드를 쌓아 이기려 하지 않습니다.

**`ui.speechBubble.position` 이 아니라 `side` 입니다.** 대상 레포 `CLAUDE.md` 는 `position` ·
`bottom-right` 로 적어 놨지만 런타임이 읽는 이름은 `side` 이고 값은 `above|left|right` 입니다.
문서대로 쓰면 선언이 조용히 죽습니다. **문서와 런타임이 갈리면 런타임이 판정입니다.**

**런타임이 읽지 않는 이름을 `ui` 에 넣지 않습니다.** `headerPanelRule` · `tabletTextRule` 은
런타임·빌드·차시 ext 어디에서도 참조가 0건입니다. 선언해도 아무 일이 없습니다.

**타이틀 로고는 선언이 아니라 파일명이 계약입니다.** base 의 `renderIntroStart` 는
`<img src="assets/ui/title-logo.png">` 를 **경로째 하드코딩해서** 그립니다. 그래서

- 그 이미지는 반드시 `assets/ui/title-logo.png` 라는 이름으로 놓입니다. **확장자를 바꾸면
  타이틀 화면에 깨진 그림이 뜹니다** — `lesson.json` 안에서는 아무 모순이 없으므로 어느 데이터
  게이트도 이것을 못 봅니다. 배포된 18차시가 예외 없이 이 이름입니다.
- `"ui": { "titleLogoRef": "assets/ui/title-logo.png" }` 로 **그 경로를 그대로 적습니다.**
  base 가 이 필드의 값을 읽어서 그리는 것은 아닙니다. 그런데 그쪽 `collectAssets` 가
  `lesson.json` 의 **모든 문자열**에서 `assets/…(png|jpg|jpeg)` 를 훑어 manifest 에 올리므로,
  이 경로가 어디에도 문자열로 없으면 **그쪽 빌드가 그 그림을 만들지도, 추적하지도 않습니다.**
  즉 **선언은 생성·추적용이고 파일명은 렌더링용**이며, 둘이 같은 경로여야 합니다.
- 다른 경로를 적지 않습니다. 적으면 그 그림은 만들어지지만 화면에는 하드코딩된 자리가 나옵니다.

커서는 반대입니다 — `ui.cursorRef` 를 **선언하지 않으면** 빌드가 공용 종이 화살표 커서를 넣어 줍니다.
차시 전용 커서 아트가 있을 때만 선언합니다.

**없는 오디오를 선언하지 않습니다.** `audioMap` 과 step 의 `bgm` 에 적은 경로는 런타임이 곧바로
불러오므로, 파일을 넣지 않은 채 선언하면 404 가 납니다(대상 레포 실측 — `fix(ext 2-1/01): 존재하지
않는 BGM 선언 제거`). 이 파이프라인은 오디오를 만들지 않습니다. **오디오 파일을 실제로 넣기
전까지 `audioMap` 과 `bgm` 을 쓰지 않습니다.** 비워 두는 것이 옳습니다.

### 인증서는 `ui.certificate` 블록입니다. 필드 이름이 정해져 있습니다

`lessonCertConfig()`(player.js:4760)가 읽는 자리는 이 열두 개뿐입니다. 다른 이름으로 적거나
평평하게(`certificateTitle` 처럼) 적으면 **그 값은 버려지고 base 기본 문구가 대신 나옵니다.**

```jsonc
"ui": { "certificate": {
  "title":              "수리력 + 인증서",
  "subtitle":           "<N학년 M학기 K차시>",
  "heading":            "인증서를 받아요!",
  "subtext":            "이름을 적으면 나만의 인증서가 완성돼요.",
  "defaultName":        "<기본 이름>",
  "body":               ["위 학생은 …", "… 문제를 해결하였기에", "이 인증서를 수여합니다"],
  "issuer":             "경상북도교육청 유초등교육과장",
  "recordCorrectLabel": "맞힌 정답 수",
  "recordTimeLabel":    "클리어 소요 시간",
  "recordTotal":        <이 차시 총 문제 수>,
  "buttonText":         "인증서 저장하기",
  "completeButtonText": "인증서 받기"
} }
```

- **`body` 는 반드시 배열입니다.** 런타임이 `Array.isArray(c.body) && c.body.length` 로
  거르므로 **문자열로 적으면 원문 문구가 통째로 버려지고** `['인증서를 잘 보관해요.']` 가
  대신 나옵니다(실측 2026-09-17, 4-2/02 에서 실제로 그랬습니다).
- **`reward.certificate` 에 적지 않습니다.** 런타임 참조 **0건**입니다 — 거기 쓰면 인증서가 안 뜹니다.
- `recordTotal` 은 이 차시의 총 문제 수입니다. 안 적으면 0 으로 나옵니다.

### 켜야 뜨는 것 셋 — **기본은 안 뜨는 것이 정상**입니다

스토리보드에 **실제로 그려져 있을 때만** 선언합니다. 그려져 있지 않은데 선언하면
**다른 차시의 연출을 물려받습니다.**

| 선언 | 무엇이 뜨나 | 런타임 근거 |
|---|---|---|
| `steps[].progressUI` | 상단 진행 게이지 | `if (step && step.progressUI) return true` (1279) |
| `reward.ui` | 우상단 보상 배지 | `if (L.reward?.ui) return true` (1356) |
| `clearSequence` 의 `{"type":"certificate"}` 컷 | 인증서 패널 | 4334행. **선언만으로는 안 열립니다 — 아래 참조** |

- **`progressUI` 의 라벨을 베끼지 않습니다.** 계약서·예시에 있는 `보스 게이지 ({current}/5)` 는
  `2-2/01` 한 차시의 세계관 문구입니다. 스토리보드에 적힌 문구를 그대로 씁니다.
- **`reward.ui` 도 같습니다.** 예전에는 `reward.assetRef` 만 있어도 배지가 떴고, 그 디자인은
  `2-2/01` 의 "황금 기차표 주머니"였습니다. 학기 전체에서 배지를 모으는 차시는 그 하나뿐이라
  다른 차시가 물려받으면 안 됩니다. **스토리보드에 없는 보상(배지·도장·티켓)을 만들어 넣지 않습니다.**
- 스토리보드의 진행선이 7단계로 그려져 있다면 그것은 게이지가 아니라 `ui.topBar` 의 단계
  표시입니다. `progressUI` 로 옮겨 적지 않습니다.

#### `ui.certificate` 를 선언해도 **컷이 없으면 인증서는 영영 안 열립니다**

`renderOutroFrame` 은 `clearSequence` 를 훑다가 `type === 'certificate'` 인 컷을 만났을 때만
패널을 엽니다(4334행). `ui.certificate` 는 **그 패널의 내용**이지 **여는 스위치가 아닙니다.**

실측 2026-09-17 — 4-2/02 에서 `ui.certificate` 를 다 채워 놓고 컷을 안 넣어 인증서가 한 번도
안 떴습니다. **schema·`lesson_check`·빌드·화면검사가 전부 통과했습니다.**

```jsonc
"clearSequence": [
  { "no": 1, "type": "stamp", "text": "2차시 수리 완료!", "animation": "stampBounce" },
  { "no": 2, "type": "certificate", "title": "수리력+ 인증서" }
]
```

### 공통 UI 다섯은 **배치·크기를 런타임이 소유**합니다. JSON 에 디자인을 쓰지 않습니다

CTA 버튼 · 헤더(목록·소리설정·뒤로가기) · 차시 목록 패널 · 소리 설정 패널 · 수리 이야기 패널.

- 초안에 이들의 **좌표·크기·색을 서술하지 않습니다.** 서술하면 구현자가 공통 규칙 위에 또
  만들고, 결국 차시마다 갈립니다 — 실측으로 **헤더 높이가 16개 차시에서 네 가지**로
  갈렸습니다(10 / 8.26 / 7.7 / 7.71cqh).
- 스토리보드에 이 UI 의 화면이 그려져 있어도 **"공통 UI 사용"이라고만 적습니다.**
- 색·그라디언트·테두리·그림자 같은 **칠만** 차시가 `player-ext.css` 에서 **디자인 토큰을 덮어** 정합니다.

  ```css
  #app{ --hd-btn-ink:#7a3f1f; --cta-start-ink:#5a2d0c; }
  ```

- 스토리보드에 "이 차시 테마 색은 ○○" 같은 지시가 있으면 `artDirection` 에 적습니다.
  그건 아트 디렉션이지 UI 배치가 아닙니다.
- 소리 설정 팝업은 **선언 없이 자동으로 붙습니다.** 언급하지 않습니다.

### 옛 스키마 잔재 — 런타임 참조를 직접 세어 가렸습니다

출처 문서(`tasks/00` §6-C)는 아래를 **전부** "런타임이 읽지 않는다(실측 0건)"로 묶어 놓았는데,
`runtime/src/player.js` 를 직접 세어 보니 **셋이 갈립니다.** 이 계약서가 런타임 기준입니다.

| 필드 | 런타임 | 판정 |
|---|---|---|
| `world` · `trophyCriteria` | 0건 | **쓰지 않습니다** |
| `reward.certificate` | 0건 | **쓰지 않습니다.** 인증서는 `ui.certificate` |
| `certificateTitle` 처럼 평평한 인증서 필드 | 0건 | **쓰지 않습니다.** `ui.certificate` 블록으로 |
| `reward.totalCount` | **읽습니다** (1419 · 1433) | `reward.ui.total` 이 없을 때의 폴백 |
| `reward.assetRef` | **읽습니다** (1439 · 4034) | 배지 그림·완료 보상 그림 |
| `reward.ui.displayText` | **읽습니다** (1434) | 배지 문구 템플릿 |

읽히는 셋은 "쓰면 안 되는 필드"가 아니라 **`2-2/01` 세계관에 묶인 옵트인**입니다.
스토리보드에 그 보상이 그려져 있지 않으면 `reward` 를 아예 쓰지 않습니다 —
쓰면 그 차시의 연출이 따라옵니다. 세계관 설명이 필요하면 `learningContent` 나
`steps[].concept` 에 적습니다.


## 문제와 미션 — 고정 원자 어휘로만 씁니다

`problemBank`의 `rounds[].problems[]`와 `tutorial`의 `missions[]`는 **같은 스키마**를 씁니다.
런타임이 같은 렌더러를 태웁니다.

```jsonc
{
  "no": 1,
  "sourcePanel": "<planner section id 또는 원문 위치>",
  "prompt": "<문제 한 줄>",
  "stimulus": { ... },          // 제시 자료. 아래 참조
  "interaction": {
    "primitives": ["choicePick"],
    "options": [ ... ],
    "answer": "..."
  },
  "wrongHint": "<틀렸을 때 말풍선>",
  "feedback": { "correct": { "characterDialogue": "...", "characterEmotion": "praising" } },
  "acceptance": ["보인다: ...", "만지면: ...", "정답: ..."]
}
```

### `sourcePanel`과 `acceptance`는 필수입니다

문항·미션마다 반드시 붙입니다. 코드가 검사하고, 빠지면 배치되지 않습니다.

- **`sourcePanel`** — 이 문항이 온 planner `sections[].id`. 여러 화면에 걸치면 배열로 씁니다.
  없으면 나중에 "이건 원문 어디서 왔지"를 아무도 못 찾습니다.
- **`acceptance`** — `보인다:` / `만지면:` / `정답:` **세 축을 모두** 채웁니다.
  화면을 보고 O/X 판정이 가능한 문장으로 씁니다. "예쁘다", "자연스럽다"는 판정할 수 없습니다.
  - `보인다:` 는 `stimulus`와 asset에서, `만지면:` 은 원자에서, `정답:` 은 `feedback`에서 옵니다.
  - **`acceptance`의 "보인다"에 적은 것은 전부 `stimulus`로 그려져야 합니다.** 적어놓고 안 그리면
    그 자리는 빈 화면이 됩니다.

이 둘이 사람이 5분 안에 검수하는 근거입니다. 화면을 LLM으로 다시 훑는 대신 이걸 봅니다.

#### `acceptance`는 그 화면의 배치도입니다 — 원자 이름을 되뇌지 않습니다

이 세 줄이 **문항마다 다르게** 나와야 합니다. 원자 이름만 바꿔 끼운 같은 문장이 반복되면
그것은 배치를 안 정했다는 뜻이고, 안 정한 배치는 `player-ext.css`에도 안 써집니다.
레이아웃이 무너지는 자리가 바로 여기입니다.

```text
❌ 어느 문항에나 들어맞는 문장 — 아무것도 정하지 않았습니다
   보인다: 문항 화면이 열리면 바로 보인다
   만지면: keypad 원자로 답을 넣을 수 있다
   정답: 10이 정답이면 정오 창이 뜬다

✅ 이 문항에서만 참인 문장 — 어디에 무엇이 놓이는지 말합니다
   보인다: 전용 패널 안에 왼쪽 지갑(만원·오천원·천원·오백원·백원 그림)과
           오른쪽 "낸 돈" 판, 아래 확인 버튼만 있다. 아이 캐릭터와 말풍선은 나오지 않는다
   만지면: 지갑에서 돈을 드래그해 오른쪽에 놓아도 지갑의 돈은 사라지지 않고,
           놓인 돈은 더블클릭하거나 왼쪽으로 드래그하면 지워진다
   정답: 확인을 누르면 놓인 돈의 합이 10000원인지 채점되어 정오 창이 뜬다
```

- `보인다:` 는 **왼쪽/오른쪽/위/아래로 자리를 말하고, 무엇이 안 나오는지도 말합니다.**
  "캐릭터와 말풍선은 나오지 않는다"가 곧 `#app.<상태> .charzone { display: none; }` 입니다.
- `만지면:` 은 조작의 **결과**를 말합니다. 원자 이름은 조작이 아닙니다.
- 여기 적은 자리마다 `player-ext.css`에 대응하는 규칙이 있어야 합니다. 짝이 없으면 둘 중 하나가 거짓입니다.

### 원자 어휘 13종

**새 이름을 지어내지 않습니다.** 복합 동작은 배열로 조합합니다(`["compareMark", "tenFrameFill"]`).

✅는 **base 런타임에 렌더러가 이미 있는 원자**입니다. 이걸 쓰면 차시가 아무것도 구현하지 않아도
화면에 나옵니다. **가급적 ✅ 안에서 고릅니다.**

| 원자 | 동작 | 필수 필드 |
|---|---|---|
| `tapCount` | 대상을 하나씩 탭해서 센다 | `item`, `count` |
| `tapMove` | 탭하면 지정된 자리로 옮겨진다 | `item`, `count`, `target` |
| ✅ `dragToSlot` | 끌어서 정해진 자리에 놓는다 | `sources[]`, `slots[]`, `answer` |
| `sortToBin` | 기준별 통·영역으로 분류한다 | `items[]`, `bins[]`, `answer` |
| ✅ `tenFrameFill` | 10칸 프레임(십판)을 채운다 | `item`, `count`, `frames` |
| `compareMark` | 둘 이상을 비교해 O표·선택으로 표시한다 | `criterion`, `pairs[]`, `answer` |
| ✅ `choicePick` | 보기 중 **하나**를 고른다 | `options[]`, `answer` |
| ✅ `multiPick` | 여럿을 고른 뒤 **확인 버튼**으로 제출한다 | `items[]`, `answer[]`, `confirmLabel` |
| `wordChoice` | 문장 속 괄호에서 낱말을 고른다 | `sentences[]` (template + answer) |
| ✅ `keypad` | 숫자 키패드로 수를 입력한다 | `answer`, `digits` |
| `arrangeOrder` | 순서대로 배열한다 | `items[]`, `order`, `answer[]` |
| ✅ `dragToCanvas` | 팔레트에서 끌어다 자유 배치한다 | `palette[]`, `answer` (+`canvas`, `scoreBy`, `confirmLabel`) |
| `drawEdge` | 도형의 빠진 변을 긋는다 | `generate.target`, `guideDots` |

- **필수 필드는 `interaction` 안에 직접 넣습니다.** `generate` 같은 임의 필드로 대체하지 않습니다.
  비면 원자가 빈 위젯으로 그려집니다.
- `interactionType`이나 맨 `options[]` 같은 옛 형태를 쓰지 않습니다. 레거시 호환용으로만 남아 있습니다.

### 원자로 안 되면 순서대로 내려갑니다

13개로 표현이 안 되는 조작을 만나면 **임의로 이름을 짓지 않습니다.** 아래 순서로 내려갑니다.

1. **원자 조합으로 바꿔봅니다.** `["tapMove", "keypad"]`처럼 둘을 잇는 것이 새 이름보다 항상 낫습니다.
2. **`player-ext.js`로 구현합니다.** 아래 "player-ext.js 작성" 계약을 지킵니다.
3. **그래도 안 되면 `unmapped[]`에 적습니다.** `{section_id, question_id, needed_action, why}`.
   어휘를 늘릴지는 사람이 판단합니다.

어휘 밖의 이름을 `primitives`에 적으면 화면에 "원자 미구현" 자리표시자가 뜨고,
그 문항은 조용히 통과된 것처럼 보입니다. 이름을 짓는 것만은 하지 마십시오.

## player-ext.js 작성

**원자로 되는 것을 여기서 다시 만들지 않습니다.** 실측(2026-09) 기준 16개 차시가 각자
`renderProblemBank`를 오버라이드해 같은 것을 다시 만들었고, 그래서 공통 원자 렌더러가 생겼습니다.
`✅` 원자로 그려지는 문항에 ext를 붙이면 그 역사를 반복하는 것입니다.

### 파일 형태

빌드가 base `player.js` **뒤에 그대로 이어붙입니다.** 모듈이 아니라 같은 스코프이므로
base의 전역을 그대로 씁니다.

```js
(function () {
  'use strict';
  if (typeof L === 'undefined') return;   // L = lesson.json

  // ...구현...

  window.lessonExt = {
    ...(window.lessonExt ?? {}),
    renderProblemBank(step) { /* ... */ return true; },
  };
})();
```

### 훅

base가 부르는 이름은 이것뿐입니다. **`true`를 반환하면 base 기본 렌더를 건너뜁니다.**

```text
renderIntroStart · renderIntroFlow · renderTutorial · renderProblemBank · renderOutro
cleanup · rerenderScene · devSceneJump · restoreCheckpointScene
clearProblemLocks · clearProblemScore · prevProblem
```

`cleanup`을 정의할 때는 앞 차시 층의 것을 지우지 말고 이어서 부릅니다
(`_previousCleanup` 패턴). 슬롯 공용층(`lessons/<슬롯>/player-ext.js`)이 먼저 합쳐지기 때문입니다.

### 쓸 수 있는 base 전역

`L`(lesson.json), `playSfx`, `startBgm`, `playNarrationAudio`, `goToStep`, `updateTopbar`,
`setLessonProgress`, `lessonNav`(mark·stage·sync), `stageLocalPoint`·`stageLocalBox`·`stageDelta`.

### 화면을 넘기는 버튼에는 재진입 가드를 답니다

아이는 버튼을 한 번 누르지 않습니다. 대상 레포가 배포 뒤에 같은 결함을 두 차시에서 고쳤습니다
(`fix(2-2/01): CTA·뒤로가기 연타 시 전환 반복`, `fix(2-2/05): 시작하기·CTA 연타 시 검은 화면·장소 건너뜀`).
**두 번 먹으면 같은 전환이 두 번 예약돼** 페이드가 누른 횟수만큼 반복되거나, 장소를 한 칸
건너뛰거나, 막이 안 걷혀 검은 화면에서 멈춥니다.

```js
// 화면을 넘기는 버튼(시작하기 · CTA · 말풍선 [다음 ▸] · 완료)은 한 번만 먹습니다.
// 버튼 엘리먼트는 화면을 다시 그릴 때 새로 만들어지므로 "엘리먼트당 1회"로 충분합니다.
function once(fn) {
  let used = false;
  return function (...args) { if (used) return; used = true; return fn.apply(this, args); };
}
btn.onclick = once(() => goToStep('step-2'));
```

- **전환 연출용 타이머는 장면 타이머와 통을 나눕니다.** 새 장면을 그릴 때 도는 `clearTimers()` 가
  막(veil)·스냅샷을 걷는 타이머까지 지우면 **불투명한 막이 영영 안 걷힙니다.** 전환용은 따로
  담고(`fxLater`/`clearFx`), 전환 자체도 진행 중이면 재진입을 막습니다.
- **여러 번 눌려도 살아 있는 버튼**(헤더 [뒤로])은 `once` 가 안 통합니다. 목적지가 같은 중복
  호출을 삼키고 재입력 잠금을 둡니다.
- **드래그 문항이 있으면 무대 전체에서 글자 선택을 막습니다**(인증서 이름칸만 예외).
  화면 어딘가에 선택된 글자가 있으면 카드를 끄는 순간 브라우저가 '선택 끌기'를 시작하고
  카드에 `pointercancel` 이 날아와 드래그가 죽습니다. base 는 카드 자신에만 `user-select:none`
  을 걸어 두므로 주변 글자의 선택은 남아 있습니다.

### 금지

- **차시 id를 하드코딩하지 않습니다.** `L.id === ...` 분기를 만들지 않습니다. 차이는
  `lesson.json`의 `ui.*`나 `step.*` 데이터 필드로 표현하고 그것을 읽습니다.
- **대사·에셋 경로를 폴백 문자열로 박지 않습니다.** 없으면 빈 문자열이나 무동작으로 둡니다.
- **공통 UI를 다시 만들지 않습니다.** 헤더 차시 목록, 소리 설정 팝업, 이전 문제로, 완료 인증서는
  base가 소유합니다. 자체 버튼·모달을 두면 base가 설치를 건너뛰어 통일이 깨집니다.
- **포인터로 요소를 움직이는 조작에서 `clientX/clientY`를 무대 안 요소의 `left/top`에 그대로
  대입하지 않습니다.** 세로 화면에서 무대가 `rotate(90deg) scale()`로 변형돼 포인터를 안 따라옵니다.
  `stageLocalPoint()`·`stageLocalBox()`·`stageDelta()`로 변환합니다.
- base `player.js`나 `player.css`를 고치지 않습니다. 그 파일들은 프롬프트에 없고, 고칠 대상도 아닙니다.

## player-ext.css 작성 — **거의 항상 필요합니다**

`player-ext.js`는 비는 것이 정상이지만 **`player-ext.css`는 다릅니다.** 이것이 없으면
모든 요소가 base 기본 위치에 그냥 놓여, 이 차시만의 화면 구성이 아무 데도 없습니다.

실측으로 확인된 것입니다 — `player-ext.css`를 만들지 않았더니 레이아웃이 정돈되지 않았습니다.
gyo6_content 기존 차시는 **1,206~7,285줄**을 씁니다(`lessons/4-1/01`이 1,206줄).

최소한 이만큼은 정합니다.

| 정할 것 | 왜 |
|---|---|
| 캐릭터 위치·크기 | 장면마다 인물이 서는 자리가 다릅니다 |
| 말풍선 위치·폭 | 인물 옆에 붙되 문제 표면을 가리지 않아야 합니다 |
| 문제 표면·자료 카드의 크기와 여백 | `stimulus`가 올라갈 자리입니다 |
| 원자 위젯 재스킨 (`.pa-*`) | 이 차시 테마 색으로. **다시 구현하지 않습니다** |
| 글자 크기 | 태블릿에서 읽히는 크기. 원문이 요구하면 반드시 |

**안에서 스크롤해야 하는 영역은 `overflow-y: auto`(또는 `scroll`)로 선언합니다.** base 는
iOS 고무줄 스크롤을 막으려고 무대 밖에서 시작된 `touchmove` 를 전부 취소하고, **실제로 넘치는
`overflow-y: auto|scroll` 요소 안에서 시작된 것만** 브라우저에 넘깁니다. 그 선언이 없으면
아이패드에서 그 영역이 아예 스크롤되지 않습니다(데스크톱에서는 마우스 휠로 되므로 안 드러납니다).

### 문제 유형마다 배치가 다릅니다 — 상태 클래스로 나눕니다

**색만 바꾸는 것으로는 부족합니다.** 돈을 끌어다 놓는 화면과 자릿값 카드를 고르는 화면은
필요한 배치가 완전히 다릅니다. 하나의 규칙으로 둘을 다 맞출 수 없습니다.

배포 중인 `lessons/4-1/01`이 쓰는 구조입니다(CSS 1,206줄 중 대부분이 이것입니다).

```js
// player-ext.js — 문제 유형이 바뀔 때 상태를 붙인다
document.getElementById('app').classList.toggle('i1-pay',  isPayScene);
document.getElementById('app').classList.toggle('i1-tens', isPlaceValueScene);
```

```css
/* player-ext.css — 그 상태에서만 적용되는 배치 */
#app.i1-pay .pa-palette      { /* 지갑의 돈을 늘어놓는 자리 */ }
#app.i1-pay .pa-canvas-items { /* 꺼낸 돈을 놓는 자리 */ }
#app.i1-prob .charzone       { display: none; }   /* 문제 화면에선 인물을 숨긴다 */
#app.i1-tens .pa-stim-cell   { /* 자릿값 칸 크기 */ }
```

- **모든 규칙을 `#app`으로 스코프합니다.** `4-1/01`은 229회 그렇게 합니다.
  base 규칙과 같은 명시도로 싸우지 않으면서 이 차시 안으로 범위를 좁히는 방법입니다.
- 상태 클래스 이름은 **이 차시 고유의 짧은 접두사**를 씁니다(`4-1/01`은 `i1-`).
  base에 없는 이름이어도 됩니다 — **직접 붙이는 클래스이기 때문입니다.**
  `COMMON_CLASS_NAMES` 제약은 **base가 그리는 요소를 고를 때만** 적용됩니다.
- 상태를 붙이는 것은 `player-ext.js`의 일입니다. 이 목적이라면 ext JS를 만들어도 됩니다 —
  "원자로 안 되는 조작"이 아니라 "장면마다 다른 배치"가 이유입니다.
- 문제 화면에서 인물이 문제를 가리면 `#app.<상태> .charzone { display: none }` 으로 숨깁니다.
  `4-1/01`이 실제로 그렇게 합니다.

### 클래스 이름을 지어내지 않습니다

**존재하지 않는 선택자에 쓴 CSS는 아무것도 하지 않습니다.** 화면은 그대로인데 파일만 생깁니다.

실측으로 확인된 것입니다 — `.lesson-player`, `.stage-character`, `.speech-bubble`, `.problem-card`
같은 이름으로 75줄을 썼는데 **base에 그런 클래스가 하나도 없어 전부 무효**였습니다.
특히 최상위를 `.lesson-player`로 감쌌기 때문에 그 안의 모든 규칙이 통째로 죽었습니다.

`COMMON_CLASS_NAMES`에 base가 실제로 쓰는 이름이 실려 옵니다. **그 목록에 있는 것만 씁니다.**
목록에 없으면 그 요소는 이 차시에서 손대지 않습니다.

원자 위젯의 주요 이름은 이렇습니다(전체는 `COMMON_CLASS_NAMES` 참조).

| 자리 | 클래스 |
|---|---|
| 원자 공통 무대 | `pa-stage` · `pa-panel` · `pa-prompt` · `pa-top` |
| 보기 고르기 | `pa-choices` · `pa-choice` · `pa-opt` · `pa-opt-lbl` · `pa-opt-img` |
| 끌어 놓기 | `pa-sources` · `pa-source` · `pa-slots` · `pa-slot` · `pa-slot-lbl` · `pa-ghost` |
| 자유 배치 | `pa-palette` · `pa-palette-item` · `pa-canvas` · `pa-canvas-items` · `pa-canvas-sum` |
| 키패드 | `kp-btn` · `kp-display` · `kp-confirm` |
| 제시 자료 | `pa-stimulus` · `pa-stim-text` · `pa-stim-img` · `pa-stim-caption` · `pa-stim-seq` · `pa-stim-cards` · `pa-stim-article` |
| O/X 판정 | `pa-judge` · `pa-judge-row` · `pa-judge-btn` · `pa-judge-picks` |
| 자릿값 표 | `pa-pvt` · `pa-pvt-num` · `pa-pvt-u` |
| 확인·건너뛰기 | `pa-confirm` · `pa-skip` · `cta` |
| 말풍선 | `bubble-speaker` |

- 원자 위젯은 다시 구현하지 말고 위 클래스로 **재스킨만** 합니다.
  선례: 키패드는 JS 0줄·CSS 6줄로 base 위젯을 그대로 씁니다.
- **최상위 래퍼를 임의로 만들지 않습니다.** `.lesson-player` 같은 이름은 없습니다.
  범위를 좁혀야 하면 `#app` 이나 base가 실제로 붙이는 상태 class를 씁니다.
- base 규칙 위에 오버라이드를 쌓아 이기려 하지 않습니다. `!important`로 덮지 않습니다.
- `"ui": { "sceneLayout": "lesson" }`은 **선택입니다.** 선언하면 base의 캐릭터·말풍선 기하가 꺼지므로
  지나가는 모든 모드의 배치를 빠짐없이 써야 합니다. 배포 중인 `4-1/01`은 선언하지 않고 base 위에
  얹는 방식을 씁니다 — 그쪽이 안전합니다.

### stimulus — 제시 자료

**가장 흔한 실패는 자료를 `prompt`나 `semiDialogue`에 적는 것입니다.** 그러면 말풍선만 뜨고
문제 화면에는 아무 자료도 없습니다. `acceptance`의 "보인다:"에 적은 것은 전부 `stimulus`로 그려져야 합니다.

전부 선택 필드입니다. planner가 실제로 그린 것만 골라 씁니다.

| 필드 | 쓰임 |
|---|---|
| `text` | 지문·수식·비교할 수. 줄바꿈은 `\n` |
| `highlight` | 강조할 문자열 목록 |
| `highlightRange` | `[시작, 길이]` — 같은 글자가 여러 번 나와 문자열로 못 집을 때만 |
| `style` | `article`이면 지문형(왼쪽 정렬·좁은 폭) |
| `imageRef` | 그림 (`assets/…png`) |
| `caption` | 그림 설명 |
| `sequence` | 수열·뛰어 세기. `"?"`는 빈칸으로 그려진다 |
| `cards` | 나란히 놓는 낱장 카드 |

자료가 **조작 대상 자체**인 문제(끌어 놓을 카드, 고를 보기)는 `stimulus`가 필요 없습니다.
`interaction`의 `sources`/`options`/`palette`가 곧 화면입니다.

## 장면 지시 — 구조 필드로만 화면에 나옵니다

`intro`·`tutorial`·`outro`·`rounds[]`의 `stageDirections[]`가 컷 단위로 재생됩니다.

**산문을 `action`에 적으면 렌더되지 않습니다.** 화면에 나와야 하는 것은 아래 필드로 옮깁니다.

| 필드 | 화면에서 하는 일 |
|---|---|
| `speechText` | **말풍선 대사.** 이게 있어야 말풍선이 뜬다 |
| `captionText` | 화면 중앙 자막(대사가 아닌 설명) |
| `characterRef` | 등장인물 — `cast`의 키 |
| `characterPosition` | **이 컷에서 인물이 서는 쪽.** `left` \| `right` |
| `characterEmotion` | `idle` `happy` `surprised` `thinking` `praising` `encouraging` |
| `backgroundRef` | 이 컷에서 배경을 바꿀 때만 |
| `sound` | `audioMap`의 키 |
| `ctaText` | 이 컷의 다음 버튼 문구 |
| `motion` | 캐릭터 애니메이션 프리셋. base가 구현한 것은 `relievedSmile` 하나뿐이고, 나머지는 `player-ext.js`가 직접 구현해야 합니다 |
| `source` `timing` `layer` | **렌더 안 됨** — 검수용 메모 |

#### `characterPosition`을 안 적으면 **인물이 차시 내내 한쪽에 붙어 있습니다**

런타임은 이렇게 정합니다.

```js
resolveCharPos(ref, declared) → declared ?? cast[ref].position ?? (주인공이면 'left' : 'right')
```

`declared`(= 컷의 `characterPosition`)가 없으면 **`cast`에 적힌 그 인물의 고정 자리**로 갑니다.
장면이 바뀌어도 안 움직입니다.

실측(2026-09-11) — 스토리보드가 "Scene 2에서 배경이 바뀌며 두 인물이 오른쪽으로 간다"고
못박았는데 컷에 `characterPosition`이 하나도 없어, 전 장면에서 인물이 `cast` 기본 자리에
고정됐습니다. 스토리보드 → 기획서까지는 그 지시가 정확히 남아 있었습니다.

- **스토리보드가 장면별로 자리를 지정했으면 그 장면의 모든 컷에 `characterPosition`을 답니다.**
  "Scene 2부터 오른쪽"은 Scene 2의 **모든 컷**에 `right`를 적으라는 뜻입니다. 한 번만 적고
  이후 컷을 비우면 그 컷들은 다시 `cast` 기본 자리로 돌아갑니다.
- 장면 내내 한 자리면 `cast[].position`만으로 충분합니다. 그때는 컷에 안 적어도 됩니다.

#### 연출은 `action`과 **필드 양쪽에** 적습니다

`action`은 사람이 원문과 대조하는 산문이고, 화면을 움직이는 것은 필드입니다. 같은 내용을
두 번 적는 것이 맞습니다. 한쪽만 적으면 이렇게 됩니다.

```text
action 에만 있다   →  아무 일도 안 일어난다. 게이트도 못 읽는다(산문이라 검사 불가)
필드에만 있다      →  화면은 맞는데 나중에 원문 대조가 안 된다
```

실측(2026-09-11) — `"편지를 클릭하면 화면이 밝아지며 장면이 전환된다"`가 `action` 산문으로만
남고 `backgroundRef`·`sound`·`motion`이 전부 비어 있었습니다. schema PASS · `lesson_check` PASS ·
빌드 성공을 모두 통과한 뒤 **사람 눈에만** 보였습니다.

원문에 아래 말이 나오면 짝이 되는 필드를 **반드시** 채웁니다.

| 원문에 이런 말이 있으면 | 채울 필드 |
|---|---|
| 배경이 바뀐다 · 장면이 전환된다 · 어디로 이동한다 | `backgroundRef` |
| 화면이 밝아진다 · 반짝인다 · 흔들린다 · 뛴다 | `motion` (+ `player-ext.js`에 구현) |
| 소리가 난다 · 효과음 · 종이 울린다 | `sound` (+ `audioMap`) |
| 누구를 클릭하면 · 무엇을 누르면 | 그 컷의 `ctaText`, 또는 문항의 `interaction` |
| 놀란다 · 기뻐한다 · 생각한다 | `characterEmotion` (+ `cast[].emotions`에 그 키) |
| 왼쪽/오른쪽에 선다 · 자리를 옮긴다 | `characterPosition` |

### 컷의 필수 필드

`no`와 `action`은 **렌더되지 않지만 필수입니다.** 렌더되지 않는다는 것과 없어도 된다는 것은 다릅니다 —
`action`이 있어야 나중에 사람이 "이 컷이 무엇을 하려던 것인지" 원문과 대조할 수 있습니다.

| 필드 | 규칙 |
|---|---|
| `no` | 필수. 스토리보드 번호 |
| `action` | 필수. 연출 내용을 산문으로 |
| `bubbleType` | **`speechText` 가 있는 컷은 반드시 `narrationNext`.** 아래 참조 |
| `speechText` | 쓴다면 비어 있지 않은 문자열. **`<br>`를 넣지 않습니다** — 런타임이 문장 단위로 줄바꿈합니다 |
| `characterEmotion` | 쓴다면 `idle` `happy` `surprised` `thinking` `praising` `encouraging` 중 하나 |

- **컷 하나 = 말풍선 하나.** 한 인물이 두 마디 하면 컷을 둘로 쪼갭니다.

#### `bubbleType` 을 안 적으면 말풍선의 **스피커와 `다음 ▸` 이 통째로 사라집니다**

base 는 말풍선 컨트롤을 `type !== 'plain'` 일 때만 그리고, `다음 ▸` 은 `narrationNext`
일 때만 더 붙입니다(`runtime/src/player.js:1972`). 타입은 이렇게 정해집니다.

```js
// player.js:1932
if (BUBBLE_TYPES.includes(declared)) return declared;   // 선언이 이긴다
if (!hasSound) return 'plain';                           // 선언이 없으면 소리가 정한다
return hasNext ? 'narrationNext' : 'narration';
```

**배포 차시는 대사 컷 287개 중 286개가 `bubbleType` 을 안 적습니다.** 그래도 컨트롤이
나오는 이유는 그쪽이 `sound` 를 달고 있어서입니다(244개). **우리는 오디오를 만들지 않으므로
그 통로가 없습니다** — 안 적으면 전부 `plain` 으로 떨어져 스피커도 `다음 ▸` 도 안 나옵니다.

실측(2026-09-22, 빌드된 페이지에서 `setSpeechBubble` 을 직접 호출):

| 선언 | type | 스피커 | `다음 ▸` |
|---|---|---|---|
| 없음 · 소리 없음 | `plain` | ✗ | ✗ |
| `plain` | `plain` | ✗ | ✗ |
| `narration` | `narration` | O | ✗ |
| **`narrationNext`** | `narrationNext` | **O** | **O** |

그래서 **`speechText` 가 있는 컷에는 `bubbleType: "narrationNext"` 를 반드시 적습니다.**
오디오 파일이 없어도 그렇게 합니다 — 소리는 나중에 붙고, `다음 ▸` 은 소리와 무관합니다.

- **`plain` 을 쓰지 않습니다.** 컨트롤을 빼는 것은 사람이 정하는 것이지 기본값이 아닙니다.
- 마지막 컷은 `hideNextWhenDone` 이 걸려 `다음 ▸` 이 곧바로 숨고 하단 CTA 가 대신 열립니다.
  그것이 정상입니다 — 마지막 컷의 진행은 언제나 CTA 몫입니다.
- 자막 전용 컷(`captionText` 만 있는 컷)에는 말풍선이 없으므로 해당 없습니다.

### `speechText`나 `captionText`가 없는 컷은 **재생되지 않습니다**

런타임이 이렇게 거릅니다.

```js
stageBeats = step.stageDirections.filter(d => d.speechText || d.captionText);
```

**둘 중 하나도 없는 컷은 통째로 사라집니다.** 거기 달아둔 `ctaText`·`motion`·`backgroundRef`도 함께 사라집니다.

실측으로 확인된 것입니다 — `ctaText`만 가진 컷 4개를 따로 만들었더니 전부 증발했고,
스토리보드가 요구한 `[시작하기]` 버튼 라벨이 화면에 나오지 않았습니다.

그래서 이렇게 씁니다.

- **`ctaText`는 대사나 자막이 있는 컷에 함께 답니다.** 버튼만 있는 컷을 따로 만들지 않습니다.
  원문이 "① 말풍선 등장 ② 버튼 등장"처럼 번호를 나눠도, 그것은 **한 컷 안의 등장 순서**입니다.

### `captionText`에 아무거나 넣어 컷을 되살리지 않습니다

재생되게 만들려고 `captionText`를 억지로 채우면 **화면에 나오면 안 되는 것이 자막으로 뜹니다.**

실측으로 확인된 것입니다 — `ctaText`만 있던 컷을 살리라고 했더니 이런 것들이 자막이 됐습니다.

| 잘못 들어간 것 | 원래 자리 |
|---|---|
| `"외부에서 바라 본 경주 박물관"` | 배경 지시 → `backgroundRef` (제작 메모는 `action`) |
| `"[시작하기]"` `"[수리가 필요해요 시작하기]"` | 버튼 문구 → `ctaText` |
| `"구분 / 성인 / 어린이 / 기본 전시 …"` | 표 데이터 → 그 문항의 `stimulus` |
| 타이틀 문구 | `renderIntroStart`가 로고로 이미 보여줌 |

**`captionText`는 학습자가 화면 중앙에서 읽을 설명 문장입니다.** 그것이 아니면 넣지 않습니다.

- 넣을 자막이 없으면 **그 컷을 만들지 않습니다.** 컷 수를 원문의 번호 항목 수와 맞추려 하지 마십시오.
  원문의 번호는 "한 화면 안에서 무엇이 순서대로 등장하는가"이지 컷 경계가 아닙니다.
- 배경·연출 지시는 `action`에 남깁니다. 그 컷은 재생되지 않아도 됩니다 —
  `ctaText`·`motion`·`backgroundRef`만 거기 달지 않으면 문제없습니다.

### 배치는 `player-ext.css`가 정합니다. 색만 바꾸는 것이 아닙니다

`LAYOUT_REFERENCE`에 배포 중인 차시가 자리를 어떻게 잡았는지 실물이 실려 있습니다.
그것과 우리 산출물의 차이가 이렇게 났습니다(2026-09-09 실측).

```text
                        배포 4-1/01        우리 4-1/02
문제 원자 배치 규칙        86개              0개
자주 쓴 속성          width·padding·position   background·color·border
길이 단위             cq 264 : px 14        cq 0 : px 56 · vh 6
```

**우리 것은 배치가 아니라 재스킨이었습니다.** 색을 바꾸는 규칙만 있고 무엇을 어디에
놓을지 정하는 규칙이 하나도 없었습니다. 그래서 base 기본 흐름 그대로 나왔고,
팔레트가 길어지자 확인 버튼이 화면 밖으로 밀렸습니다.

세 가지를 지킵니다.

1. **길이는 `cqw`·`cqh`로 잡습니다.** 무대가 16:9 컨테이너입니다. `px`·`vh`로 잡으면
   한 해상도에서만 맞고 나머지에서 무너집니다. 테두리 두께 같은 잔값만 `px`로 남깁니다.
2. **문제 패널을 무대 안에 자리 잡아 놓습니다.** 흐름에 맡기지 않습니다.
   `position:absolute` + 네 변 + `height:fit-content` + `margin-block:auto` 가 그 방법입니다.
3. **차시가 그림을 주는 자리는 base 의 상자를 지웁니다.**
   `background:none; border:0; padding:0` 을 주어야 테두리 없이 그림만 남습니다.

### 화면은 1280×720입니다. 넘치면 버튼을 누를 수 없습니다

세로로 넘친 만큼은 **잘려 나갑니다.** 스크롤이 없으므로 아래에 있는 확인 버튼이
화면 밖으로 밀리면 학습자는 그 문제를 끝낼 수 없습니다.

실측(2026-09-09) — 돈 팔레트를 5칸(10000·5000·1000·500·100)으로 세로로 쌓았더니
확인 버튼이 화면 아래로 56px 밀렸습니다. **데이터는 유효했고 빌드도 통과했습니다.**

보기·팔레트가 4칸을 넘으면 세로로 쌓지 말고 `player-ext.css`에서 가로로 흐르게 하거나
칸 높이를 줄입니다. 제시 자료 그림(`pa-stim-img`)의 `max-height`도 함께 줄입니다.

### 표·기사·수열은 `stimulus`로 갑니다. 자막이 아닙니다

`captionText`는 **한 줄로 이어 읽는 문장**입니다. 표를 넣으면 화면에서
`구분 성인 어린이 기본 전시 무료 무료 특별 전시 10000 6000` 한 줄로 뭉개집니다.
줄바꿈으로 나누든 `/`로 나누든 결과는 같습니다 — 자막은 표를 그리지 않습니다.

**round 컷에는 `captionText`를 쓰지 않습니다.** 배포 중인 차시 셋(`4-1/01`·`2-1/02`·`1-1/04`)의
round 컷 12개에 자막이 **하나도 없습니다.** 그 자리는 대사(`speechText`)를 쓰는 곳입니다.
(step 컷의 자막은 정상입니다 — `1-1/04`에 13건.)

자료는 문항의 `stimulus`가 받습니다. base 런타임이 그리는 필드는 이것뿐입니다.

| 필드 | 무엇을 그리나 |
|---|---|
| `text` | 지문·수식·표. **선언한 줄바꿈을 `<br>`로 지킵니다** — 표는 여기에 넣습니다 |
| `highlight` / `highlightRange` | `text` 안의 강조 |
| `imageRef` + `caption` | 그림과 그림 설명 |
| `sequence[]` + `stepLabel` | 수열·뛰어 세기. `"?"`는 빈칸이 됩니다 |
| `cards[]` | 나란히 놓는 낱장 카드 |

`text` 안의 `□`는 **입력칸이 됩니다**(키패드가 찾는 칸과 같은 것). 문장 한가운데 빈칸이
필요하면 그 글자를 씁니다.

### 대괄호는 스토리보드 표기이지 버튼에 새길 글자가 아닙니다

원문의 `[시작하기]`에서 대괄호는 "이건 버튼이다"라는 표시입니다. 그대로 옮기면
화면에 대괄호가 찍힙니다. 괄호를 벗기고 안쪽 글자만 `ctaText`에 쓰고,
`exitCondition.buttonText`도 같은 글자로 맞춥니다.

### `no`는 step 안에서 이어집니다

`stageDirections[].no`는 그 step 안에서 **1부터 끊기지 않고** 올라갑니다.
원문 화면이 바뀔 때마다 1로 되돌리지 않습니다 — 컷은 화면 단위가 아니라 재생 순서이기 때문입니다.

실측 — `1,2,3 / 1,2,3,4 / 1,2,3`처럼 화면마다 리셋해서 순서를 읽을 수 없게 된 적이 있습니다.
- 배경 교체·모션도 같습니다. 재생되는 컷에 얹습니다.
- 마지막 컷에 `ctaText`가 없으면 `exitCondition.buttonText`가 쓰입니다.
  **원문이 지정한 버튼 문구가 있으면 그 컷의 `ctaText`에 그대로 적습니다.**
- 순수 연출 메모는 `mustShow: false` 로 두되, **화면에 나와야 하는 것을 거기 두지 않습니다.**

### step 단위 규칙

- **`missions[]`의 모든 미션에 `interaction`이 있어야 합니다.** 없으면 원자가 없어 화면이 비고,
  `acceptance`도 없으면 장면으로도 인식되지 않아 다른 검사가 통째로 건너뜁니다.
- **`step.assetPrompt`를 쓰지 않습니다.** 이미지는 이미 만들어져 있습니다. 굳이 쓴다면
  `sceneType`과 `targetAsset`이 반드시 있어야 하고, `sceneType: "full-storyboard-panel"`은 금지입니다.
- `step.acceptanceCriteria`를 쓴다면 비어 있지 않은 배열이어야 합니다.
- **문제와 문제 사이의 대화**는 그 라운드의 `rounds[].stageDirections[]`에 넣습니다.
  라운드 첫 문제 전에 한 번 재생됩니다. 빠뜨리면 planner의 이야기가 통째로 사라집니다.

## 원문 텍스트 보존 (최우선)

화면에 보이는 텍스트는 planner가 스토리보드 원문에서 그대로 옮겨온 것이며, 당신의 수정 대상이 **아닙니다.**

- planner의 `sections[].elements[].content`와 `sections[].questions`(prompt·choices·answer·feedback)의
  텍스트는 **한 글자도 바꾸지 않습니다.** 축약, 재서술, 다듬기, 대괄호 제거, 어미 변경 전부 금지입니다.
- planner에 없는 버튼·라벨·안내 문구를 새로 추가하지 않습니다.
- **문항 수를 줄이거나 대표 문항으로 합치지 않습니다.** 오답 보기도 전부 옮깁니다.
  planner에 문항이 12개면 `problems`도 12개입니다. "비슷한 문제 5개"처럼 뭉뚱그리지 않습니다.
- `feedback.correct`가 planner에 있으면 그대로 옮깁니다. 비어 있으면 **비워 둡니다.** 지어내지 않습니다.

## asset 배치

이미지는 asset_generator가 이미 만들어 `RUN_DIR/output/assets/`에 평평하게 놓여 있습니다.
gyo6_content는 역할별 디렉토리를 요구하므로, **어디로 갈지만 판정해 `asset_placements`로 보고합니다.**

| 역할 | 목적지 |
|---|---|
| 배경 | `assets/backgrounds/<파일명>` |
| 등장인물 | `assets/character/<감정>.png` |
| UI·소품·버튼·도장 | `assets/ui/<파일명>` |

판정 근거는 planner `asset_plan[]`의 `kind`·`visual_role`·`character_id`입니다.

### 배치한 이미지는 **전부** lesson.json이 참조해야 합니다

`asset_placements`에 올린 이미지는 `lesson.json` 어딘가에서 실제로 쓰여야 합니다.
옮겨만 놓고 참조하지 않으면 **그 자리는 화면에서 빕니다.** 코드가 검사하고, 하나라도 남으면 막힙니다.

실측으로 확인된 것입니다 — 22장을 배치하고 8장만 참조한 적이 있습니다.
타이틀 로고·문제 표면·유물 그림·실생활 카드 4장이 통째로 사라졌는데
**빌드는 성공했고 그쪽 검증기도 통과했습니다.** 아무도 안 보는 자리였습니다.

참조하는 자리는 이렇습니다. 각 이미지의 성격에 맞는 곳에 넣습니다.

| 이미지 | 참조 자리 |
|---|---|
| 배경 | **step 단위로 먼저 둡니다.** 아래 "배경은 step에 둡니다" 참조 |
| 주인공·조력자 기본 포즈 | `cast[<키>].assetRef` |
| 캐릭터 감정별 포즈 | `cast[<키>].emotions.<감정>` |
| 문제의 제시 자료 | `steps[].rounds[].problems[].stimulus.imageRef` |
| 끌어 놓을 조각·보기 그림 | `interaction.palette[].imageRef` · `interaction.sources[].imageRef` · `interaction.options[].imageRef` |
| 놓을 자리 | `interaction.canvas.assetRef` |
| 정오 도장 | `ui.feedbackCorrectRef` · `ui.feedbackWrongRef` |
| 인증서 바탕 | `ui.certificate.surfaceRef` |
| 타이틀 레터링 | **`assets/ui/title-logo.png`** — base 가 이 경로를 하드코딩해 그립니다. 이름을 바꾸지 않습니다 |
| 문제·설명이 얹히는 표면 | 그 문제의 `stimulus.imageRef` |

**같은 이미지를 여러 자리에서 참조해도 됩니다.** 배경처럼 여러 화면이 공유하는 것이 그렇습니다.
반대로 **한 번도 안 쓰이는 이미지가 남으면 안 됩니다.**

### 그림을 그리는 근거는 `artDirection`과 `assetPrompt` 둘뿐입니다

그림은 이 파이프라인의 `asset_render` 단계가 굽습니다. 보통 개발과 **동시에** 돌아 `design/asset-plan.json` 을
목록·지시로 쓰고, 그 그림 하나만 다시 구울 때는 `lesson.json` 에 적힌 것을 봅니다.

```text
① lesson.json 의 artDirection      화풍·색·조명·선 굵기.  차시 전체에 상속됩니다
② step 의 assetPrompt              이 그림 한 장에 무엇이 들어가고 무엇이 빠지는가
```

**둘 다 없으면 파일 이름 수준의 지시만 남습니다.** 배경처럼 요구사항이 많은 그림에 그런 지시가
걸리면 화면 한가운데에 인물이 들어차고 그 위에 문제 UI가 겹칩니다.

이 둘은 **배치한 뒤에도 계속 쓰입니다.** 우리가 굽지 못한 그림이 남으면 gyo6_content의 `npm run build:lesson`이
자기 imagegen으로 채우는데, 그때 읽는 것도 똑같이 `artDirection`과 `assetPrompt`입니다
(실측 — 그쪽 폴백은 `moon-jar.png` → `"moon jar in educational setting"` 한 줄입니다).
그러니 우리가 이미 구운 그림이라도 지시는 남겨 둡니다.

**배경(`assets/backgrounds/`)에는 반드시 씁니다.** 나머지는 필요할 때만 씁니다.

### 학습자가 만지는 것을 배경에 굽지 않습니다

정답 판정 대상, 드래그 대상, 클릭 대상은 **런타임이 얹는 별도 그림**입니다. 배경에 구우면
세 가지가 한꺼번에 깨집니다.

- 움직일 수 없습니다. 배경은 한 장이라 그 안의 물건만 따로 옮기지 못합니다.
- 상태를 못 바꿉니다. 정답일 때 색이 변하거나 사라지는 연출을 넣을 자리가 없습니다.
- **배경만 다시 그려도 정답 위치가 어긋납니다.** 배경 그림과 히트 좌표가 한 몸이 되기 때문입니다.

실측(2026-09-10) — 마당 배경 지시가 `좌측 가로 20% 세로 52% 중심에 나무 평상`처럼 좌표를 못 박고,
문항의 히트 영역이 그 좌표를 그대로 베꼈습니다. 배경에서 그 셋을 빼자 **빈 흙바닥에 보이지 않는
원 세 개**가 남았습니다. `player-ext.js`도 "배경 안의 오브젝트를 클릭한다"는 전제로 쓰여 있었습니다.

그 자리는 `reservedUiZones`에 **"런타임이 얹는 자리"** 로 적고 배경에서는 비웁니다.
그리고 그 물건마다 별도 `assetPrompt`를 만들어 `interaction`이 `imageRef`로 가리킵니다.

```jsonc
"steps": [{
  "id": "step-2",
  "backgroundRef": "assets/backgrounds/post-office.png",
  "assetPrompt": {
    "sceneType": "base-background",
    "targetAsset": "assets/backgrounds/post-office.png",   // ← 그림 경로와 **정확히** 같아야 합니다
    "mustInclude": [
      "1980년대 우체국 내부 — 나무 카운터, 빨간 우체통, 딥그린 간판",
      "좌측에 인물이 설 빈 공간",
      "중앙에 문제 표면이 놓일 넓은 빈 공간"
    ],
    "reservedUiZones": ["left character", "center problem surface", "bottom CTA"],
    "forbidden": ["배경에 캐릭터 삽입", "말풍선·자막·버튼 텍스트 삽입", "플랫 벡터풍", "로고·워터마크"]
  }
}]
```

| 필드 | 쓰임 |
|---|---|
| `sceneType` | `"base-background"`를 씁니다. **`"full-storyboard-panel"`은 금지** — 완성된 장면을 통째로 그려 버립니다 |
| `targetAsset` | 이 지시가 **어느 그림에 붙는지**를 정합니다. 그림 경로와 한 글자라도 다르면 지시가 통째로 죽습니다 |
| `mustInclude` | 반드시 들어갈 것. 배경이면 "무엇이 놓일 빈 공간"까지 적습니다 |
| `reservedUiZones` | 런타임 UI가 덮을 자리라 **비워 두라는** 지시. 이게 없으면 그림이 UI에 가립니다 |
| `forbidden` | 그리면 안 되는 것. 말풍선·자막·버튼은 런타임이 얹으므로 그림에 넣지 않습니다 |

**`target`이 아니라 `targetAsset`입니다.** 배포된 차시 하나(2-1/04)가 `target`으로 적어서
그 차시의 지시 5개가 **전부 무시되고 있습니다.** 오류도 안 나고 그림만 엉뚱하게 나옵니다.

한 step이 여러 그림을 지시할 수 있습니다. 키 이름이 `assetPrompt`로 끝나기만 하면 됩니다
(`backgroundAssetPrompt`, `problemAssetPrompt` …). 배포된 2-2/05가 그렇게 7개를 답니다.

### 배경은 step에 둡니다. 컷은 바뀔 때만 씁니다

**step 단위 배경이 없으면 화면이 빈 채로 시작합니다.** 런타임은 step을 열 때 배경을 한 번 깔고,
컷의 `backgroundRef`는 **그 컷에서 배경을 교체할 때만** 읽습니다. 컷에만 두면 첫 화면이 비어 있습니다.

실측으로 확인된 것입니다 — `intro`의 배경을 `stageDirections[0].backgroundRef`에만 두었더니
타이틀 화면이 배경 없이 렌더됐습니다. **데이터는 유효했고 검증기도 빌드도 통과했습니다.**

step 타입마다 읽는 필드가 다릅니다. 런타임(`runtime/src/player.js`)이 실제로 보는 곳입니다.

| step | 배경 필드 |
|---|---|
| `intro` | 아래 "intro는 화면이 둘이다" 참조 — **두 곳에 다 필요합니다** |
| `tutorial` | `step.backgroundRef` |
| `problemBank` | `round.background` 없으면 `step.background.ref` — **객체 안의 `ref`입니다** |
| `outro` | `scene.backgroundRef` 없으면 `step.backgroundRef` |

- 모든 step에 **그 step의 기본 배경**을 답니다. 한 화면도 배경 없이 시작하지 않습니다.
- 장면 중간에 배경이 바뀌면 그 컷에 `backgroundRef`를 **추가로** 답니다. 기본 배경을 지우지 않습니다.
- `problemBank`만 `step.background.ref`로 한 겹 더 들어갑니다. `step.backgroundRef`라고 쓰면 안 읽힙니다.

### `intro`는 화면이 둘입니다

런타임이 `intro`를 두 단계로 그립니다.

```text
renderIntroStart   타이틀 화면. title-logo 이미지 + [시작하기]
                   setBg(step.startBackgroundRef ?? step.backgroundRef)
      ↓ [시작하기] 클릭
renderIntroFlow    컷 재생. stageDirections 를 순서대로
                   if (d.backgroundRef) setBg(d.backgroundRef)   ← 컷에 있을 때만
```

**두 번째 단계는 step 레벨 배경을 읽지 않습니다.** 앞 단계가 깔아 둔 배경이 그대로 남을 뿐입니다.
그래서 `startBackgroundRef`**만** 두면 타이틀에는 배경이 있지만, 전환하면서 그것이 사라져
**화면이 검게 됩니다.**

실측으로 확인된 것입니다 — `startBackgroundRef`만 두었더니 `[시작하기]`를 누른 뒤
검은 화면이 나왔습니다. 데이터는 유효했고 빌드도 통과했습니다.
배포 중인 `4-1/01`은 `backgroundRef`만 써서 그 배경이 계속 남습니다.

그래서 **`backgroundRef`를 반드시 둡니다.** `startBackgroundRef`는 타이틀만 다른 그림을
쓰고 싶을 때 더하는 선택 필드입니다.

```jsonc
{
  "type": "intro",
  "backgroundRef":      "assets/backgrounds/<기본 배경>.png",      // 필수
  "startBackgroundRef": "assets/backgrounds/<타이틀 배경>.png",   // 선택 — 타이틀만 다를 때
  "stageDirections": [
    { "no": 1, "action": "...", "captionText": "...",
      "backgroundRef": "assets/backgrounds/<이 컷의 배경>.png" }   // 배경을 바꿀 때만
  ]
}
```

**타이틀 문구를 컷의 `captionText`로 또 쓰지 않습니다.** 타이틀은 `renderIntroStart`가
`title-logo` 이미지로 이미 보여줍니다. 컷에서 같은 문구를 반복하면 같은 말이 두 번 나옵니다.
- 타이틀 아래 한 줄이 필요하면 `step.startSubtitle` 에 씁니다.
- 시작 버튼 문구를 바꾸려면 `step.startButtonText` 에 씁니다(기본값 `시작하기`).

### `cast[].emotions`가 없으면 인물이 화면에 **안 나옵니다**

base는 인물 그림을 **`cast[ref].emotions`에서만** 찾습니다.

```js
const cast = (L.cast ?? {})[ref];
const src = (cast?.emotions ?? {})[em] ?? (cast?.emotions ?? {}).idle ?? '';
```

**`assetRef`는 읽지 않습니다.** `assetRef`만 두면 `src`가 빈 문자열이 되어 인물이 아예
안 그려집니다. 오류도 안 나고 말풍선만 떠 있습니다 — 실측(2026-09-11)으로 컷 19개 전부
인물이 없었고 데이터·스키마·빌드·화면검사가 모두 통과했습니다.

**포즈가 한 종뿐이어도 `emotions`를 씁니다.** 다른 감정은 base가 `idle`로 떨굽니다.

```jsonc
"cast": {
  "suri":       { "name": "수리",   "emotions": { "idle": "assets/character/suri.png" },  "position": "left"  },
  "postmaster": { "name": "우체국장", "emotions": { "idle": "assets/character/postmaster.png" }, "position": "right" }
}
```

**`position`도 함께 씁니다.** 없으면 `resolveCharPos`가 주인공을 전부 `left`로 보내서,
두 사람이 번갈아 말해도 **말풍선이 계속 같은 쪽**에 뜹니다.

`characterRef`에는 **cast 키**를 씁니다(`"suri"`). 그림 경로를 넣으면 `L.cast["assets/..."]`가
없으므로 인물이 사라집니다.

### 인물 크기와 말풍선 자리는 base가 변수로 받습니다

인물 크기·자리를 규칙으로 이기려 들지 마십시오. base의 선택자는 명시도가 높아
(`#app.char-fixed-y .charzone.char-left` = (1,3,0)) 선택자를 계속 키우게 됩니다.
**그쪽이 낸 통로는 변수입니다.**

```css
#app { --char-bottom: -46cqh; --char-width: 28.4cqw; }
```

무대는 1280×720이고 헤더가 72px이므로 본문은 648px입니다. 요구는 둘입니다 —
**얼굴이 본문의 1/5(130px)**, **보이는 인물이 본문의 1/3(216px)**.

**전신을 다 보여주면 두 요구를 동시에 못 맞춥니다.** 전신을 216px로 맞추면 얼굴은
50px(본문의 1/13)밖에 안 됩니다. 인물을 **크게 그리고 아래를 잘라** 가슴 위만 보여야 합니다.

자르는 주체는 **무대의 `overflow`** 입니다. base가 `bottom: -18%`로 쓰는 바로 그 방식입니다.

```text
원본 캔버스에서 머리는 캔버스 높이의 약 0.238 을 차지한다(실측)
  얼굴 130px  →  캔버스 높이 130/0.238 = 547px,  2:3 이므로 가로 364px = 28.4cqw
  보이는 216px →  547-216 = 331px 을 무대 밖으로 내린다 = -46cqh
```

**두 가지는 절대 하지 마십시오.** 실측(2026-09-11)으로 둘 다 화면을 깼습니다.

| 하면 안 되는 것 | 무슨 일이 일어나는가 |
|---|---|
| `.charzone { overflow: hidden }` | `.speech`가 `.charzone`의 **자식**이라 말풍선까지 잘린다 |
| `#charImg { position: absolute }` | flow에서 빠져 zone 높이가 0으로 접히고, 인물이 통째로 무대 밖(y=720)으로 나가 화면에서 사라진다 |

`#charImg`는 base가 준 대로 `width: 100%`인 in-flow 요소로 둡니다. 크기는 `--char-width`가,
잘리는 지점은 `--char-bottom`이 정합니다.

- 문제 화면처럼 인물을 줄여야 하면 **그 상태 클래스에서 변수만 다시 정합니다**
  (`#app.g5-prob { --char-width: 22.7cqw; --char-bottom: -36.8cqh; }`). 규칙을 새로 쓰지 않습니다.
- 무대 가장자리에 선 인물의 말풍선은 **중앙 기준이라 화면을 넘칩니다.** 바깥쪽 인물은
  말풍선을 무대 안쪽 모서리에 붙입니다(`char-right`면 `right: 0`, `char-left`면 `left: 0`).

### 글자 크기는 **배포된 차시의 같은 자리**에서 가져옵니다

지어낸 값을 쓰지 마십시오. `LAYOUT_REFERENCE`에 실린 차시들이 이미 화면에서 검증된 수치를
들고 있습니다. 같은 역할의 요소를 찾아 그 값을 기준으로 잡습니다.

실측(2026-09-11) — 말풍선 본문에 `--fs-speech: 3.8cqh`(27.36px)를 지어 썼는데, 배포 차시들은
같은 자리에 `1.62~1.75cqw`(≈21~22px)를 씁니다. 사용자 지적은 "글씨가 너무 크다"였습니다.
`2.9cqh`(20.88px)로 맞춰 해결했습니다.

| 자리 | 배포 차시 기준 |
|---|---|
| 말풍선 본문 | ≈21~22px (`2.9cqh` 또는 `1.7cqw`) |

### 캐릭터 감정 6종

주인공 캐릭터는 `idle` `happy` `surprised` `thinking` `praising` `encouraging` 6종을 요구합니다.
planner의 포즈 이름은 이와 다르므로 가장 가까운 감정에 매핑합니다.

- **없는 감정을 지어내지 않습니다.** 대응하는 포즈가 없으면 그 감정은 배치하지 않고,
  `unmapped[]`에 `{needed_action: "character-emotion:<감정>"}`으로 보고합니다.
- 한 포즈를 두 감정에 중복 배치하지 않습니다.
- 주인공이 아닌 인물의 포즈는 `assets/ui/`가 아니라 `assets/character/`에 두되 파일명을 유지합니다.
- **파일명에 인물 키를 붙입니다** — `assets/character/child-idle.png`, `curator-idle.png`.
  `idle.png` 처럼 감정만 쓰면 인물이 둘 이상일 때 같은 이름이 되고, 무엇보다 **에셋 생성기가
  그런 이름으로 내지 않습니다.** 실측(2026-09-08) — `cast.child.emotions` 를 맨 감정 이름으로
  쓴 결과 `idle.png`·`happy.png`·`praising.png` 세 장이 원본 없는 참조가 됐고, 그 자리는
  화면에서 인물이 안 나오는 상태가 됩니다. 배치된 차시는 `child-idle.png` 로 고쳐져 있었습니다.

## 모든 차시 공통 UI 규격

> 출처: gyo6_content `tasks/05_common_ui_requirements.md` (**읽기 전용 참조**).
> 그쪽은 **오디오가 있는 배포 차시**를 전제하므로 이 파이프라인과 갈리는 자리가 있습니다.
> 갈리는 곳은 아래에 그대로 표시했습니다. **그쪽 문서를 고치지 않습니다** — 이것이 우리 판본입니다.

### 말풍선 기하는 base 가 소유합니다. 차시는 **변수만** 덮습니다

`data-bubble-type` 이 붙은 말풍선은 공통 런타임이 그립니다. 값을 다시 잡지 말고
조정이 필요하면 변수만 덮습니다.

```css
#app .speech[data-bubble-type]{
  --bubble-border: 0.31cqw;   /* 말풍선·꼬리 공통 외곽선 두께 */
  --bubble-line:   #4c3428;   /* 외곽선 색 */
  --bubble-bg:     #fffdf6;   /* 배경 = 꼬리 뿌리 마개 색 */
  --bubble-tail:   1.24cqw;   /* 꼬리 한 변 */
  --bubble-gap:    0.78cqw;   /* 🔊 ↔ [다음 ▸] 간격 */
  --bubble-ctl-mt: 0.9cqh;    /* 본문 ↔ 컨트롤 줄 여백 */
}
```

- **크기는 텍스트에 맞춥니다.** `width: max-content` + `max-width` 상한.
  **고정 폭·고정 높이를 주지 않습니다.** `height: max-content` 를 반드시 둡니다 —
  base 의 모드별 기하가 `top` 과 `bottom` 을 동시에 거는 경우가 있어, 안 두면 높이가
  상자에 갇혀 **내용이 말풍선 밖으로 넘칩니다**(실측 2026-09: 내용 91px 인데 상자 34px,
  텍스트와 🔊·[다음]이 말풍선 밖에 떠 있었습니다).
- **🔊 와 `다음 ▸` 자리는 모든 말풍선에서 같습니다.** 본문 아래 한 줄, 오른쪽 아래 정렬.
  간격은 `--bubble-gap` 하나로 관리합니다. 말풍선마다 자리를 따로 잡지 않습니다.
- **꼬리 외곽선 두께 = 말풍선 외곽선 두께.** 삼각형 `border` 트릭은 두께가 어긋나므로
  쓰지 않습니다. 그림자는 `box-shadow` 가 아니라 `filter: drop-shadow` 입니다 —
  `box-shadow` 는 꼬리를 따라가지 못해 아래 변에 턱이 남습니다.
- **텍스트는 가운데 정렬**이고 줄바꿈은 base `renderSentenceLines` 가 합니다.
  JSON 에 `<br>` 를 넣지 않습니다. 한국어는 `word-break: keep-all; overflow-wrap: break-word`.

### 말풍선 안 버튼이 안 눌리던 원인 둘 — base 가 처리하므로 **다시 만들지 않습니다**

| 막던 것 | base 의 처리 |
|---|---|
| `.charzone{pointer-events:none}` | `.bubble-controls` 에서 `pointer-events:auto` 로 되살린다 |
| `#content{z-index:16}` 가 말풍선을 덮음 | 컨트롤이 떠 있는 동안만 `#app.bubble-controls-on .charzone{z-index:40}` |

`.charzone` 은 `z-index:15` 로 **자체 스택 컨텍스트**를 만듭니다. 말풍선 안쪽 z-index 를
아무리 올려도 `#content` 위로 못 갑니다 — charzone 자체를 올려야 합니다.
차시가 이 싸움을 다시 하지 않습니다.

**검수는 실제 마우스 클릭으로 합니다.** `element.click()` 은 히트테스트를 건너뛰어
**가려진 버튼도 동작하는 것처럼 보입니다** — 이 버그가 실제로 그렇게 통과했습니다.

### `다음 ▸` 은 반드시 무언가를 합니다. 장면 전환은 **언제나 CTA 몫**입니다

| 상황 | `다음 ▸` 이 하는 일 |
|---|---|
| 대사가 이어지는 컷 | 다음 말풍선으로 넘긴다 (장면 전환이 아니라 **대사 진행**) |
| 마지막(전환) 컷 | 나레이션을 건너뛰고 **CTA 를 지금 노출**한다 |
| CTA 가 이미 열림 | **버튼이 사라진다** — 눌러도 아무 일 없는 버튼은 두지 않는다 |

전환 컷에는 `다음 ▸` 과 CTA 가 **함께 있는 것이 정상**입니다. 중복이 아닙니다 —
`다음`은 스킵·노출, CTA 는 전환으로 역할이 다릅니다.
**`다음`이 전환까지 하게 만들지 않습니다.**

### 우리 판본이 갈리는 자리 — 오디오

출처 문서는 *"나레이션이 들어간 말풍선에만 🔊 를 넣는다(없는 말풍선엔 넣지 않음)"* 라고
적습니다. 그쪽 배포 차시는 전부 오디오가 있기 때문입니다.

**이 파이프라인은 오디오를 만들지 않으므로 그 규칙을 그대로 쓰면 컨트롤이 영영 안 나옵니다.**
사용자 결정(2026-09-22)은 이렇습니다 — **모든 대사 말풍선에 🔊 와 `다음 ▸` 를 기본으로
넣는다. 오디오가 아직 없어도 강제로 나오게 한다. 빼는 것은 사람이 정한다.**

그래서 `speechText` 가 있는 컷에는 `bubbleType: "narrationNext"` 를 적습니다(앞의 "컷의 필수 필드" 절).

**문제 화면 말풍선은 해당 없습니다.** 힌트·정오 피드백은 `setSpeech()`(player.js:1264)가
그리는데 그 함수는 컨트롤을 아예 만들지 않고 `bubbleType` 도 읽지 않습니다. 대사 컷만
`setSpeechBubble()` 을 탑니다. 출처 문서의 *"문제 화면 말풍선은 버튼이 없어 바로 풀 수 있다"*
는 base 구조가 이미 보장합니다.

### 화면 크기가 변해도 비례와 자리가 유지돼야 합니다

- 치수는 `cqw`/`cqh` 입니다. **`vw`/`vh` 를 쓰지 않습니다** — 세로 90° 회전에서 축이 틀어집니다.
- `clamp(px, Ncqw, px)` 의 상·하한이 서로 다른 지점에서 걸리면 **비례가 깨져 줄바꿈과 자리가
  변합니다.** 폰트·폭·간격을 상하한 없이 전부 `cqw` 로 두거나, 내부를 고정 px 로 두고
  컨테이너 폭 기준으로 한 번에 `transform: scale()` 합니다. 둘 중 하나로 통일합니다.
- **세로 회전 시 드래그 요소도 같이 돕니다.** base 는 세로에서 `#app` 을 `rotate(90deg)` 하는데,
  드래그 고스트를 `#app` 밖(`body`)에 붙이면 회전이 상속되지 않습니다. base 와 **같은
  미디어쿼리**에서 그 요소에 `rotate(90deg)` 를 더합니다. **드래그 대상이 여러 종류면 전부** 합니다.

### 차시를 끝내기 전 체크리스트

- [ ] 1280 · 1100 · 960 · 세로(420×820) 에서 콘솔 에러 0
- [ ] 축소·확대에서 요소·이미지·텍스트가 같은 비율, 자리·줄바꿈 불변
- [ ] **대사 말풍선에 🔊 와 `다음 ▸` 이 있다**(오디오가 없어도 — 우리 판본)
- [ ] `다음 ▸` 은 스킵·노출만 하고 **장면 전환은 CTA 가 한다**
- [ ] 연속 대사 컷에서만 `다음 ▸` 이 다음 줄로 넘긴다
- [ ] 말풍선 안 버튼이 **실제 마우스 클릭**으로 눌린다(`element.click()` 으로 확인하지 않는다)
- [ ] 말풍선 외곽선·꼬리 두께가 같고 접합부에 턱이 없다
- [ ] 말풍선 텍스트가 가운데 정렬이고 낱말이 어중간하게 끊기지 않는다
- [ ] 무대 CTA 자리가 전 장면에서 일관된다
- [ ] 세로 회전에서 모든 드래그 요소가 90° 돈다
- [ ] `ui.castOnStage: "keep"` 이면 `.cast-extra img` 에 크기를 줬다


## 이미 당해 본 것 — 같은 자리에서 또 틀리지 않습니다

아래는 **이 파이프라인이 실제로 낸 결함**입니다. 전부 `problem.md` 에 사례와 함께 기록돼 있고,
전부 **schema·`lesson_check`·빌드·화면검사를 통과한 뒤** 사람 눈이나 런타임 코드에서만 드러났습니다.
읽고 같은 자리를 피하십시오.

### 1. 원자의 `answer` 는 **런타임이 채점할 수 있는 모양**이어야 합니다

가장 비싼 결함이었습니다 — 문항 텍스트도 정답값도 원문 그대로인데 **정답이 존재하지 않는
문제**가 됐고, 사람이 화면에서 직접 풀어 보기 전까지 아무도 몰랐습니다(실측 2026-09-17,
4-2/02 의 키패드 9문항 **전부**).

| 원자 | 지켜야 할 것 |
|---|---|
| `keypad` | `answer` 는 **배열**이고 원소 수 = `stimulus.text` 의 `□` 개수. 원소는 **숫자만** |
| `dragToSlot` | `answer` 길이 = `slots` 길이(칸 순서대로). 값은 `sources` 의 id |
| `multiPick` | `answer` ⊆ `items` 의 id |
| `choicePick` | `answer` ∈ `options` 의 값 |

**키패드에는 소수점 키가 없습니다**(`player.js:2819` — 키는 `1`~`9` 와 `0` 뿐). 채점은
문자열 비교입니다(`paNorm` = 공백 제거뿐, `player.js:2709`). 그래서

```jsonc
// ❌ 학습자가 절대 못 맞힌다 — 소수점을 칠 수 없고 "264" !== "2.64"
"stimulus": { "text": "3.85-1.21=□.□□ kg" },
"interaction": { "primitives": ["keypad"], "answer": "2.64", "digits": 3 }

// ✅ 칸마다 한 자리씩. digits 는 쓰지 않는다(원소 길이가 곧 자릿수다)
"interaction": { "primitives": ["keypad"], "answer": ["2", "6", "4"] }
```

`stim.text` 의 `□` 하나가 입력칸 하나가 되고(`player.js:3499`), 키패드는 `answers[step]` 을
`blanks[step]` 에 씁니다. **앞자리가 이미 찍힌 칸**(`0.□□□` 에 답 `0.011`)은 숫자를 그냥
훑으면 안 됩니다 — 템플릿과 답을 한 글자씩 맞대어 **칸에 들어갈 것만** 고릅니다(`0`,`1`,`1`).

칸 하나에 여러 자리가 들어가도 됩니다(`["264","10","2640"]`). base 가 원소 길이로 자릿수를
다시 잡습니다. **배열 길이와 `□` 개수만 맞으면 됩니다.**

### 2. base 가 안 읽는 필드에 적으면 **조용히 사라집니다**

오류도 안 나고 게이트도 안 걸립니다. 화면에만 없습니다.

| 적었던 곳 | 실제로 읽는 곳 | 실측 |
|---|---|---|
| `cast[].assetRef` | `cast[].emotions` | 컷 19개 전부 인물이 안 나왔다 |
| `clearSequence[].title` · `.subText` | `clearSequence[].text` 하나뿐 | 마무리 도장의 두 줄이 안 나왔다 |
| `ui.certificate` 만 선언 | `clearSequence` 의 `{"type":"certificate"}` 컷 | 인증서가 한 번도 안 떴다 |
| `ui.certificate.body` 를 문자열로 | 배열일 때만 읽는다 | 원문 문구가 버려지고 기본 문구가 나왔다 |
| `ui.speechBubble.position` | `ui.speechBubble.side` | 대상 레포 문서가 틀렸다. **런타임이 판정** |
| 컷의 `bubbleType` 생략 | 생략하면 `plain` → 컨트롤 소멸 | 🔊 와 `다음 ▸` 이 통째로 안 나왔다 |

**새 필드를 쓰기 전에 런타임에서 그 이름을 찾습니다.** 문서에 있다고 읽히는 것이 아닙니다.

### 3. `player-ext.css` 의 절대좌표는 **`.pa-panel` 기준**입니다

base 의 문제 화면 DOM 은 `.pa-panel > .pa-stage > .pa-atom` 입니다
(`player.js:3534`·`3539`). `.pa-panel` 이 `position:absolute` 라서 그 안의 요소에 준
`right`·`top` 은 **무대가 아니라 패널** 기준으로 잡힙니다.

실측 2026-09-18 — 키패드를 오른쪽 띠에 두려고 `.pa-stage{right:1.4cqw}` 로 적었더니
패널 **안쪽**에 앉아 **키패드 문항 전부에서 세로셈을 덮었습니다.** 활동명 띠(`.pa-badge`)도
같은 이유로 계산식 위에 겹쳤습니다.

패널이 비워 둔 바깥 띠로 빼려면 패널 변에서 빼야 합니다.

```css
/* 패널 콘텐츠 오른쪽 변 = 100 - 30(panel right) - 1.8(padding) = 68.2cqw
   키패드 오른쪽 변을 96cqw 에 두려면 → right: 68.2 - 96 = -27.8cqw */
#app.prob-mode .pa-stage { right: -27.8cqw; width: 24cqw; }
```

**세로로 움직이는 것에 고정값을 주지 않습니다.** 패널은 `height:fit-content` +
`margin-block:auto` 라 내용 높이에 따라 위 변이 움직입니다(실측 115~144px). 패널 위에
붙일 것은 `bottom: 100%` 로 **패널 변에 붙입니다.**

### 4. 게이트를 **모양으로** 피하지 않습니다

`problem.md` `[gate-evasion-by-reformatting]` 3회 — 게이트가 길이·개수·존재로 재면
그 모양만 피하는 답이 나옵니다. **규칙은 지키고 내용은 틀린** 산출물이 됩니다.

- `cut_not_played`(대사·자막 없는 컷은 재생 안 됨)를 넣자 **자막에 배경 지시·버튼 문구·표
  데이터를 채워서** 통과했습니다.
- 표 판정을 "줄바꿈 3칸 이상, 각 칸 12자 이하"로 재자 **칸 길이를 넘기게 다시 포맷해서**
  통과했습니다. 화면에서 뭉개지는 것은 그대로였습니다.
- `acceptance` 세 축 다양성을 요구하자 되먹임 3회를 전부 `정답:` 축 늘리기에 썼습니다.
  그 축은 원래 정형적이라 늘릴 차이가 없었고 **배치는 그만큼 안 좋아졌습니다.**

게이트에 걸리면 **걸린 자리의 내용을 고치십시오.** 판정을 피해 가는 형태로 다시 쓰지 않습니다.

### 5. 한글이 `???` 로 보이면 **원문이 아니라 읽은 쪽이 깨진 것**입니다

실측 2026-09-09 — 참조 차시와 계약서를 PowerShell 로 열었는데 이 장비의 PowerShell 5.1 은
`-Encoding` 이 없으면 UTF-8 을 cp949 로 디코드합니다. 에이전트가 깨진 글자를 보고
**본 대로 옮겨 적어** `lesson.json` 79줄이 `만지면: keypad ??? ?? ??? ? ??.` 가 됐습니다.

깨진 한글도 유효한 UTF-8 문자열이라 **스키마·엄격 검증·빌드가 전부 통과합니다.**

- 한글 파일은 **UTF-8 로 읽습니다**(`Get-Content -Raw -Encoding utf8`).
- **`???` 를 그대로 옮겨 적지 않습니다.** 보이면 읽기를 의심합니다.

### 6. 화풍은 글이 아니라 **그림**으로 묶입니다

`problem.md` `[style-drifts-across-batches]` — 같은 `artDirection` 문장을 받은 두 호출이
**사진 같은 3D 배경**과 **납작한 벡터 봉투**를 냈습니다. 글로는 안 묶입니다.

`assetPrompt` 를 쓸 때 지킬 것 둘입니다.

- **학습 대상의 외곽은 정답입니다.** 장식(덮개·접힘선·무늬)이 외곽을 건드리면 문항이 틀린 것이
  됩니다. 실측 — 사각형 우편물의 덮개가 아래를 잘라내 화면에서 오각형으로 보였습니다.
  `mustInclude` 에 "외곽은 정확히 그 도형이고 장식은 **안쪽에만**" 을 적습니다.
- **색·무늬로 학습 대상을 구별시키지 않습니다.** 모양으로 풀어야 성취기준이 섭니다.


## 금지

- **`manifest.json`을 쓰지 않습니다.** 코드가 만듭니다.
- **원자로 되는 것을 `player-ext.js`로 다시 만들지 않습니다.**
- **`common.css`·`common.js`를 만들거나 옮기지 않습니다.** base 런타임이 그 자리입니다.
- **단일 HTML을 만들지 않습니다.** `index.html`은 gyo6_content의 빌드가 만드는 파생물입니다.
- **원자 어휘 밖의 이름을 짓지 않습니다.**
- **`world`·`trophyCriteria`·`interactionType`·맨 `options[]`를 쓰지 않습니다.** 옛 스키마입니다.
- **이미지 파일을 복사·이동·생성하지 않습니다.** 배치는 보고만 하고 코드가 실행합니다.
- **다른 run 디렉토리의 산출물을 읽거나 베끼지 않습니다.** 지금 `RUN_DIR`과 프롬프트로 주어진 입력만 씁니다.
- planner에 없는 학습 내용을 추가하지 않습니다.
