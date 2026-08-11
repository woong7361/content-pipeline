# 재사용 Source 설계

content-harness-pipeline에서 반복해서 쓰는 캐릭터, asset, HTML 패턴, debug 도구를
`source/` 아래에 reference catalog로 관리하기 위한 설계 문서다.

이 설계의 1차 목표는 자동화가 아니라 **사람과 AI가 재사용 대상을 쉽게 고르고 reference path로 넘길 수 있는 구조**를 만드는 것이다.
따라서 초기 버전은 Markdown 목록과 이미지 reference를 중심으로 시작한다.

## 현재 상태

이 문서는 설계와 현재 구현을 함께 담는다.
`production/1-2/08/index.html`을 기준으로 컴포넌트 축을 먼저 진행했다.

| 영역 | 상태 | 위치 |
|---|---|---|
| 컴포넌트 1차 추출 (6개) | 완료, 전부 `candidate` | `source/common/components/` |
| 컴포넌트별 단독 확인 페이지 | 6개 모두 있음 | `source/common/components/[component]/preview.html` |
| 조립 확인 페이지 | 있음 | `source/common/components/example/index.html` |
| 이미지 catalog (3·4장) | 미착수 | — |
| teacher source | 미착수 | — |
| 파이프라인 연결 (8장) | 미연결, 수동 경로 전달만 가능 | — |

아직 다른 차시에 재사용해본 적이 없다.
다음 마일스톤은 컴포넌트를 실제로 한 번 이식해보고 `approved`로 올릴지 판단하는 것이다.

---

## 1. 핵심 원칙

### 1.1 이미지를 source of truth로 둔다

캐릭터와 asset은 텍스트 설명보다 이미지가 기준이다.

- md의 description은 검색과 선택을 돕는 짧은 설명이다.
- 실제 화풍, 비율, 선, 재질, 버튼 깊이, 표정 언어는 reference image를 직접 보고 판단한다.
- description을 길게 써서 이미지를 대체하지 않는다.
- 서로 충돌하면 이미지가 description보다 우선한다.

### 1.2 md는 catalog와 사용 계약만 담는다

Markdown 문서는 다음 정도만 담는다.

- 어떤 reference인지
- 어디에 있는지
- 언제 쓰는지
- 쓰면 안 되는 경우
- 관련된 기존 run 또는 production 출처

프롬프트 본문처럼 장황한 작화 지시는 넣지 않는다.
작화 지시가 필요하면 teacher별 style 문서에 짧게 모으고, 최종 판단은 이미지로 한다.

### 1.3 common과 teacher를 분리한다

- `source/common`: 특정 선생님이나 콘텐츠 세계관에 묶이지 않는 재사용 도구와 패턴
- `source/[teacher]`: 선생님별 캐릭터, asset 스타일, reference image

공통으로 보이더라도 선생님 정체성이 강하게 묻은 것은 `common`으로 올리지 않는다.
예를 들어 특정 선생님 얼굴이나 의상이 들어간 말풍선/CTA는 teacher source에 둔다.

### 1.4 run 산출물은 후보, source는 확정본

`runs/.../output/assets/...`는 재사용 후보의 출처일 뿐이다.
재사용하기로 확정한 파일은 `source/` 아래로 복사해 안정 경로를 만든다.

나중에 파이프라인에 넘기는 reference path는 가능하면 `source/...`를 사용한다.

---

## 2. 디렉토리 구조

초기 구조는 단순하게 둔다.

```text
content-harness-pipeline/source/
  common/
    components/          # 구현됨. 상세는 7장
      AGENTS.md
      _shared/
      example/
      [component]/

    AGENTS.md            # 미구현
    assets.md            # 미구현
    assets/              # 미구현
      speech-bubble/
      feedback/
      cta/
      header/
      list/
      debug/

  [teacher]/             # 미구현
    AGENTS.md
    characters.md
    assets.md
    style.md
    assets/
      characters/
      backgrounds/
      props/
      ui/
      cta/
```

항목이 많아지기 전까지는 `assets.md`, `characters.md`, `style.md` 정도만 둔다.
분량이 커지면 `feedback.md`, `speech-bubble.md`, `headers.md`처럼 나눈다.

디렉토리 설명은 `README.md`가 아니라 **`AGENTS.md`**로 둔다.
그 디렉토리에서 작업하는 AI가 자동으로 먼저 읽는 파일이기 때문이다.
사람용 소개가 따로 필요해지면 그때 `README.md`를 추가하고, 제약과 사용 절차는 `AGENTS.md`에 남긴다.

이 source에는 두 개의 축이 있다.

| 축 | 위치 | 다루는 것 | 현재 상태 |
|---|---|---|---|
| 이미지 catalog | `common/assets/`, `[teacher]/` | 재사용 이미지와 사용 계약 (3·4장) | 미착수 |
| 컴포넌트 | `common/components/` | HTML/CSS/JS 재사용 원본 (7장) | 1차 추출 완료 |

두 축은 독립적으로 진행할 수 있다.
컴포넌트 축이 먼저 진행됐으므로, 지금 실제로 존재하는 계약은 7장 기준이다.

---

## 3. Common Source

`source/common`은 콘텐츠마다 반복되는 기능과 형태를 관리한다.

### 3.1 관리 대상

| Category | 예시 | 관리 방식 |
|---|---|---|
| debug | scene jumper, question seek, `__contentHarnessShowScene` | 코드 패턴 description + reference HTML path |
| speech-bubble | 빈 말풍선 surface, feedback bubble | image reference + use/avoid |
| feedback | 정답/오답 도장, center effect | image reference + 상태별 사용 계약 |
| cta | ticket button, start/next/save button body | image reference + label overlay 정책 |
| header | title banner, chapter plaque, section medallion | image reference + fixed text 정책 |
| list | 선택지 카드, 문제 리스트, gallery list | HTML 패턴 + surface asset |
| input | keypad, number block, drag/drop slot | HTML/JS 패턴 + body asset |
| component | clock body, gauge body, meter body | fixed body asset + variable overlay 정책 |
| result | certificate, completion board | image reference + text safe zone |

### 3.2 Common asset catalog 항목 템플릿

```md
## speech-bubble-basic

![speech-bubble-basic](assets/speech-bubble/basic.png)

- Path: `source/common/assets/speech-bubble/basic.png`
- Type: `speech_bubble`
- Status: `candidate | approved | deprecated`
- Description: 캐릭터 머리 옆에 붙는 빈 말풍선 표면. 짧은 대사와 feedback 문구에 사용.
- Source:
  - `runs/YYYY-MM-DD_xxxxx/output/assets/...`
- Use when:
  - `dialogue` channel
  - 짧은 정답/오답 반응
- Avoid:
  - 긴 설명문
  - 문제 본문
  - 화면 하단 자막 카드처럼 사용
- Text policy: HTML text overlay
- Notes:
  - 한 콘텐츠 안에서는 말풍선 스타일을 섞지 않는다.
```

### 3.3 Debug catalog 항목 템플릿

Debug 도구는 이미지가 아니라 HTML/JS 패턴이므로 reference path와 설명을 중심으로 둔다.

```md
## scene-debug-jumper

- Type: `debug_tool`
- Status: `candidate | approved | deprecated`
- Reference paths:
  - `runs/YYYY-MM-DD_xxxxx/output/index.html`
- Description: scene, question index, solved state를 바로 이동시키는 개발용 패널.
- Use when:
  - QA에서 특정 scene이나 문항을 빠르게 확인해야 할 때
  - long flow 콘텐츠의 중간 화면을 반복 수정할 때
- Avoid:
  - 최종 production UI로 노출
- Required hooks:
  - `data-qa-scene`
  - `data-qa-order`
  - `window.__contentHarnessShowScene(sceneId)`
```

---

## 4. Teacher Source

`source/[teacher]`는 선생님별 캐릭터와 asset 스타일을 관리한다.
여기서는 같은 선생님/브랜드 안에서 일관성을 유지하는 것이 목적이다.

### 4.1 `characters.md`

캐릭터는 pose 목록보다 identity 기준이 먼저다.

```md
# Characters

## teacher

![teacher-identity](assets/characters/teacher-idle.png)

- Identity source: `source/[teacher]/assets/characters/teacher-idle.png`
- Description: 수업을 이끄는 선생님 캐릭터.
- Status: `approved`
- Invariants:
  - 얼굴, 머리, 의상, 비율 유지
  - pose별로 다른 인물처럼 보이면 실패
- Avoid:
  - 다른 선생님 캐릭터와 얼굴/의상 혼합
  - pose마다 팔레트나 등신 변화

### Poses

| Pose | Path | Description | Use |
|---|---|---|---|
| idle | `assets/characters/teacher-idle.png` | 기본 대기 자세 | 일반 안내 |
| explaining | `assets/characters/teacher-explaining.png` | 손짓하며 설명 | 개념 설명 |
| praising | `assets/characters/teacher-praising.png` | 칭찬/축하 | 정답 feedback |
```

### 4.2 `assets.md`

선생님 스타일에 묶인 UI, props, backgrounds를 관리한다.

```md
## teacher-main-cta

![teacher-main-cta](assets/cta/main-ticket.png)

- Path: `source/[teacher]/assets/cta/main-ticket.png`
- Type: `cta_surface`
- Status: `approved`
- Description: 선생님 콘텐츠에서 기본 CTA로 쓰는 티켓형 버튼 몸체.
- Text policy: HTML text overlay
- Use when:
  - 시작하기
  - 다음 활동으로 이동
  - 완료 후 저장/이동
- Avoid:
  - 문제 보기 카드
  - 긴 문장 설명판
```

### 4.3 `style.md`

style 문서는 짧은 작화 계약만 담는다.
이미지를 대체하는 상세 프롬프트가 되면 안 된다.

```md
# Style

## Summary

- Audience: 초등 저학년
- Tone: 밝고 또렷한 수업 안내
- Line: 중간 굵기의 깨끗한 외곽선
- Color: 고채도지만 눈부시지 않은 교육용 팔레트
- Lighting: 맑은 낮 조명, 단순한 셀 명암
- UI surface: 두께와 눌림감이 보이는 물리적 버튼/판

## Reference Priority

1. 캐릭터 identity source image
2. 같은 캐릭터의 기존 pose image
3. teacher asset reference image
4. common asset reference image
5. description text

## Avoid

- 같은 캐릭터를 pose마다 다른 인물처럼 생성
- common asset과 teacher asset의 화풍 혼합
- CSS/SVG 패널처럼 보이는 raster asset
```

---

## 5. Status 정책

각 catalog 항목은 상태를 가진다.

| Status | 의미 |
|---|---|
| `candidate` | run/production에서 발견한 재사용 후보. 아직 기준 asset은 아님 |
| `approved` | source로 복사했고 다음 작업에서 reference로 써도 됨 |
| `deprecated` | 과거 reference. 새 작업에서는 쓰지 않음 |

초기에는 엄격한 검수 절차를 만들지 않는다.
대신 실제로 여러 번 재사용해도 흔들리지 않는 항목만 `approved`로 올린다.

---

## 6. Path와 이름 규칙

### 6.1 파일명

파일명은 기능과 상태를 먼저 드러낸다.

```text
speech-bubble-basic.png
feedback-stamp-correct.png
feedback-stamp-wrong.png
cta-ticket-primary.png
header-chapter-plaque.png
clock-body-round.png
teacher-idle.png
teacher-explaining.png
teacher-praising.png
```

권장 순서:

```text
{domain}-{object}-{variant}.{ext}
{character}-{pose}.{ext}
```

### 6.2 경로

md에는 항상 `source/` 기준 안정 경로를 적는다.

```md
- Path: `source/common/assets/feedback/feedback-stamp-correct.png`
```

기존 산출물 경로는 `Source`에만 적는다.

```md
- Source:
  - `runs/2026-07-22_ch8c0719/output/assets/feedback_stamp_correct.png`
```

---

## 7. 컴포넌트 분리와 단일 HTML 합성

최종 산출물 계약은 여전히 `output/index.html` 단일 파일이다.
하지만 재사용 원본은 컴포넌트 단위로 분리해 관리한다.

즉 source 단계와 output 단계의 책임을 나눈다.

| 단계 | 형태 | 목적 |
|---|---|---|
| `source/common/components/...` | html/css/js/assets 분리 | 재사용, 수정, 검토가 쉬운 원본 |
| `runs/.../output/index.html` | 단일 HTML inline | 배포/검수 계약 유지 |

### 7.1 컴포넌트 디렉토리 구조

```text
source/common/components/
  CLAUDE.md              # 범위 선언, 추출 목록, 사용 절차, 규칙
  AGENTS.md -> CLAUDE.md # 심링크

  _shared/
    base.css             # 토큰, #stage 1920x1080, .scene 기본 계약
    preview.css          # preview 전용 harness
    preview.js           # preview 전용 harness

  example/               # 전 컴포넌트 조립 확인 페이지
    index.html
    style.css
    script.js
    assets/

  speech-bubble/
    component.md
    template.html
    preview.html         # 이 컴포넌트만 띄우는 확인 페이지
    style.css
    behavior.js
    assets/

  keypad/
    component.md
    template.html
    preview.html
    style.css
    behavior.js

  debug-jumper/
    component.md
    template.html
    preview.html
    style.css
    behavior.js
```

모든 파일이 항상 필요하지는 않다.

- 정적 surface만 있으면 `component.md`와 asset만 둘 수 있다.
- 동작이 없는 HTML 조각이면 `behavior.js`를 생략한다.
- asset이 없는 debug 도구는 `assets/`를 생략한다.
- runtime만 담당해 고정 마크업이 없으면 `template.html`을 생략한다(`scene-controller`).

#### `template.html`은 조각이다

`template.html`에는 `<head>`도, `<link>`도, `<script>`도 없다.
최종 HTML에 inline할 **마크업 조각**이므로 그래야 맞다.
브라우저에서 직접 열면 스타일도 동작도 없는 것이 정상이고, 실행 확인은 `example/index.html`에서 한다.

다만 조각만 봐도 무엇과 함께 써야 하는지 알 수 있어야 한다.
따라서 각 `template.html` 맨 위에 다음을 적은 주석 헤더를 둔다.

- 이 파일이 단독 실행되지 않는 조각이라는 사실
- 함께 넣어야 하는 CSS / JS / asset
- 호출해야 하는 runtime API
- 확인 경로 (`example/index.html`)

JS가 채우는 자리(`keypad`의 키 그리드, `debug-jumper`의 scene 목록)는 마크업이 비어 있으므로,
**호출을 빠뜨리면 빈 채로 남는다**는 점을 주석에 명시한다.

#### `_shared/base.css`

컴포넌트마다 반복되던 토큰과 stage 계약을 한 곳에 모은다.

- 폰트/색/z-index/easing/duration/radius/shadow 토큰
- `#viewport`, `#stage` (1920x1080, `transform-origin: center`), `.c-bg`, `.hidden`
- `box-sizing`, form 요소 font 상속 같은 최소 reset

컴포넌트 `style.css`는 이 토큰을 쓰는 것을 전제로 한다.
따라서 최종 HTML로 inline할 때 `base.css`를 먼저 넣고 컴포넌트 CSS를 넣는다.

#### 확인 경로는 두 층이다

| 페이지 | 무엇을 보는가 |
|---|---|
| `[component]/preview.html` | 그 컴포넌트 **하나만**. 상태 전환과 경계값을 버튼으로 직접 밟는다 |
| `example/index.html` | 컴포넌트들이 **함께** 놓였을 때 겹치거나 깨지지 않는지 |

둘은 대체재가 아니다. 컴포넌트를 고쳤으면 `preview.html`로 그 컴포넌트가 혼자 성립하는지 보고,
`example/`로 조합이 성립하는지 본다.

`preview.html`은 `_shared/preview.css`와 `_shared/preview.js`가 제공하는 harness를 쓴다.
harness는 상단 HUD, 컨트롤 버튼, stage 스케일링만 담당하고 컴포넌트 로직에는 관여하지 않는다.

```js
Preview.mount({ title, path, note });
Preview.control("전체 비활성", () => CommonKeypad.setEnabled(root, false));
Preview.log("setEnabled(root, false)");
```

`preview.html`이 실어야 할 것:

- `_shared/base.css` → `_shared/preview.css` → 그 컴포넌트의 `style.css`
- 그 컴포넌트의 `behavior.js`, 그리고 `_shared/preview.js`
- 그 컴포넌트가 실제로 의존하는 것만 추가로 (예: `debug-jumper`는 `scene-controller`가 필요하다)

의존하지 않는 컴포넌트를 preview에 끌어오지 않는다.
**preview가 무엇을 로드하는지가 그 컴포넌트의 실제 의존 목록**이므로, 편의로 다 넣으면 그 정보가 사라진다.

`preview.html`과 `example/`에서만 외부 폰트 CDN을 쓴다. 최종 output에는 옮기지 않는다.
`_shared/preview.*`도 preview 전용이므로 최종 output에 inline하지 않는다.

### 7.2 `component.md` 템플릿

```md
# Speech Bubble

- Type: `ui_component`
- Status: `candidate | approved | deprecated`
- Final output: inline into `output/index.html`
- Assets:
  - `assets/speech-bubble-basic.png`
- Slots:
  - `text`
- States:
  - hidden
  - visible
- Required classes:
  - `.c-speechBubble`
  - `.left-speaker` or `.right-speaker` or `.top-speaker`
- Runtime API:
  - `CommonSpeechBubble.show(el, text)`
  - `CommonSpeechBubble.hide(el)`
- Use when:
  - 캐릭터 대사
  - 짧은 feedback 대사
- Avoid:
  - 긴 설명문
  - 문제 본문
  - 화면 하단 자막 카드
- Integration notes:
  - 최종 HTML에서는 CSS/JS를 inline한다.
  - asset path는 output 기준 `assets/...`로 변환한다.
```

필수 항목은 `Type`, `Status`, `Source`, `Use when`, `Avoid`다.
나머지는 해당 컴포넌트에 실제로 있을 때만 적는다.

- `Source`: 이 조각을 어느 산출물에서 뽑았는지. 1차 추출은 전부 `production/1-2/08/index.html`이다.
- `Runtime API`: 다른 곳에서 쓸 때 실제로 호출해야 하는 함수. 동작이 있는 컴포넌트에는 반드시 적는다.
- `Required DOM`: 컴포넌트가 바깥에 요구하는 구조(`#stage`, `.scene` 등).

### 7.3 상태 관리 원칙

컴포넌트 상태는 전역 store로 시작하지 않는다.
DOM 자체를 상태 저장소로 쓰고, `behavior.js`가 그 DOM만 건드린다.

상태 표현은 두 가지를 모두 허용한다.
어느 쪽을 쓸지는 **상태가 배타적인지**로 정한다.

| 상황 | 표현 | 예 |
|---|---|---|
| 상태가 서로 배타적이고 2~3개 | `data-state` | speech-bubble `hidden`/`visible` |
| 전환 애니메이션이 겹치거나 상태가 덧붙는 성격 | class | scene `active`/`leaving`, stamp `show` |
| 브라우저가 이미 의미를 가진 상태 | 네이티브 속성 | keypad `disabled`, panel `hidden` |

`data-state`로 전부 통일하지 않는다.
scene 전환은 나가는 화면과 들어오는 화면이 한동안 공존하므로 단일 `data-state`로 표현할 수 없고,
입력 비활성화는 `disabled`가 접근성까지 처리하므로 class로 흉내내지 않는다.

배타 상태 예시:

```html
<div class="c-speechBubble right-speaker" data-component="speech-bubble" data-state="hidden">
  <span data-slot="text"></span>
</div>
```

```css
.c-speechBubble {
  opacity: 0;
  pointer-events: none;
}

.c-speechBubble[data-state="visible"] {
  opacity: 1;
  pointer-events: auto;
}
```

```js
function show(el, text) {
  el.querySelector("[data-slot='text']").textContent = text;
  el.dataset.state = "visible";
}
```

겹치는 상태 예시:

```js
previous.classList.remove("active");
previous.classList.add("leaving");
setTimeout(() => previous.classList.remove("leaving"), 460);
next.classList.add("active");
```

현재 컴포넌트별 실제 상태 계약은 다음과 같다.

| Component | 상태 표현 | 값 |
|---|---|---|
| `scene-controller` | class | `active`, `leaving` |
| `speech-bubble` | `data-state` | `hidden`, `visible` |
| `feedback-layer` | class | `show` |
| `keypad` | 네이티브 | `disabled` (키 단위) |
| `ticket-button` | 네이티브 + `:hover`/`:active` | `disabled` |
| `debug-jumper` | 네이티브 + class | `hidden`, 현재 항목 `current` |

책임은 다음처럼 나눈다.

| 책임 | 담당 |
|---|---|
| 어떤 상태가 있는가 | `component.md` |
| 상태별 고정 asset과 CSS 표현 | `style.css` |
| 상태 전환 함수 | `behavior.js` |
| 현재 scene에서 언제 상태를 바꾸는가 | scene controller / builder |
| 실제 최종 inline 결과 | `output/index.html` |

### 7.4 컴포넌트 네이밍 규칙

컴포넌트 루트와 내부 구조 class는 충돌을 줄이기 위해 `c-` prefix를 쓴다.

```text
.c-speechBubble
.c-keypad
.c-key
.c-ticketButton
.c-feedbackStamp
.c-debugPanel
```

상태 class에는 prefix를 붙이지 않는다.
`production/1-2/08`에서 그대로 가져온 이름을 유지하는 편이 이식 비용이 낮고,
상태 class는 항상 `c-` 루트와 함께 쓰이므로 충돌 위험이 크지 않다.

```text
.active
.leaving
.show
.current
```

JS가 DOM을 찾을 때는 **ID가 아니라 data 속성**을 쓴다.
ID로 찾으면 그 컴포넌트는 특정 페이지에서만 동작한다.

| 속성 | 용도 |
|---|---|
| `data-component` | 컴포넌트 루트 표시 |
| `data-slot` | 내용이 채워지는 자리 (`text`, `label`, `display`, `keys`) |
| `data-action` | 동작 버튼 (`close`) |
| `data-state` | 배타 상태 |

scene은 QA 계약상 `id`를 유지하되, 조회는 `data-qa-scene`으로도 되게 둔다.

```text
data-qa-scene / data-qa-order / data-qa-label
```

`behavior.js`는 전역 네임스페이스 하나만 노출한다.
번들러 없이 `<script>`로 순서대로 붙이는 방식이라 모듈 시스템을 쓰지 않는다.

```text
window.CommonSceneController = { scaleStage, createSceneController }
window.CommonSpeechBubble    = { setText, show, hide }
window.CommonTicketButton    = { setLabel }
window.CommonKeypad          = { build, displayTick, setEnabled, setConfirmOnly }
window.CommonFeedbackLayer   = { showStamp, hideStamp }
window.CommonDebugJumper     = { init }
```

이름은 `Common` + PascalCase 컴포넌트명이다.
컴포넌트 간 통신은 서로를 직접 호출하지 않고 이벤트로 한다.

```text
common:scenechange  → { sceneId, scene }
```

기존 output HTML을 바로 고칠 때는 무리하게 전부 rename하지 않는다.
새 source component부터 이 규칙을 따른다.

### 7.5 합성 방식

초기에는 자동 assembler를 만들지 않는다.
builder/refiner가 reference로 받은 컴포넌트 조각을 읽고 단일 HTML에 inline한다.

나중에 자동화가 필요하면 다음 흐름으로 확장한다.

```text
component template.html
component style.css
component behavior.js
component assets/
        ↓
assembler
        ↓
output/index.html
output/assets/...
```

합성 시 지켜야 할 규칙:

- 최종 HTML은 여전히 `common_html_contract.md`의 단일 파일 계약을 따른다.
- CSS는 `<style>` 안에 inline한다.
- JS는 `<script>` 안에 inline한다.
- asset은 `output/assets/`로 복사하고 HTML에서는 `assets/...` 상대 경로로 참조한다.
- 컴포넌트 source의 asset을 output에서 직접 참조하지 않는다.
- 외부 CDN, 외부 폰트, 원격 이미지를 추가하지 않는다. `example/index.html`의 폰트 link는 옮기지 않는다.

inline 순서는 고정한다. CSS는 소스 순서로 우선순위가 갈리므로 순서가 계약이다.

```text
<style>
  1. _shared/base.css
  2. 각 컴포넌트 style.css
  3. 콘텐츠 고유 CSS
</style>

<script>
  1. 각 컴포넌트 behavior.js   (window.Common* 등록)
  2. 콘텐츠 controller script  (scaleStage, createSceneController, 각 컴포넌트 init)
</script>
```

`template.html`의 asset 경로는 컴포넌트 기준 `assets/...`로 적혀 있다.
output으로 옮길 때 파일을 `output/assets/`로 복사하면 경로 문자열은 그대로 맞는다.

### 7.6 추출 현황

반복 빈도와 수정 비용이 큰 것부터 분리했다.

| # | Component | 범위 | 상태 |
|---|---|---|---|
| 1 | `debug-jumper` | `data-qa-*`에서 scene 목록 자동 구성, backquote 토글 | 추출됨 (`candidate`) |
| 2 | `scene-controller` | `data-qa-scene`, `__contentHarnessShowScene`, stage scale, active/leaving | 추출됨 (`candidate`) |
| 3 | `speech-bubble` | dialogue/feedback 짧은 대사, left/right/top speaker | 추출됨 (`candidate`) |
| 4 | `feedback-layer` | correct/wrong stamp, hold 옵션 | 추출됨 (`candidate`) |
| 5 | `keypad` | `[1..9][← 0 확인]`, enabled/disabled/confirm-only | 추출됨 (`candidate`) |
| 6 | `ticket-button` | CTA body asset, label slot, hover/press/disabled | 추출됨 (`candidate`) |
| 7 | `clock` | body asset, CSS hands, spin/glow/recheck states | 미추출 |

전부 `production/1-2/08/index.html`에서 뽑았고, 아직 `candidate`다.
다른 차시에 한 번 이상 실제로 붙여본 뒤 `approved`로 올린다.

미추출 항목 중 다음 후보는 `clock`, 그다음은 `certificate`다.
`feedback-layer`는 지금 stamp만 담당하고, pose swap과 center effect는 아직 콘텐츠 쪽에 남아 있다.

---

## 8. 파이프라인 연결 방식

초기에는 md를 자동 파싱하지 않는다.
작업자가 필요한 reference path를 input metadata나 user_request로 넘긴다.

이미 존재하는 `metadata.style_reference_set`은 다음 범주를 지원한다.

- `backgrounds`
- `characters`
- `props`
- `ctas`

따라서 teacher style reference는 이 계약으로 바로 연결할 수 있다.

```json
{
  "metadata": {
    "style_reference_set": {
      "id": "teacher-a-basic",
      "must_follow": true,
      "root": "source/teacher-a",
      "categories": {
        "backgrounds": [
          {
            "path": "assets/backgrounds/classroom-basic.png",
            "role": "classroom background",
            "use": "palette, lighting, background density",
            "avoid": "copying exact board text"
          }
        ],
        "characters": [
          {
            "path": "assets/characters/teacher-idle.png",
            "role": "teacher identity",
            "use": "line, proportions, expression language",
            "avoid": "changing face, hair, outfit"
          }
        ],
        "props": [],
        "ctas": []
      },
      "usage_policy": {
        "summary": "이미지를 직접 열어 확인하고 description보다 reference image를 우선한다."
      }
    }
  }
}
```

Common debug/html 패턴은 아직 `style_reference_set`보다 넓은 범위다.
초기에는 `user_request`나 작업 지시에서 md path를 직접 넘긴다.

```text
Use reusable references from:
- `source/common/assets.md#speech-bubble-basic`
- `source/common/assets.md#scene-debug-jumper`
```

나중에 자동화가 필요해지면 `source_index.json` 또는 `references.yaml`을 추가한다.
하지만 첫 단계에서는 md catalog만 유지한다.

### 8.1 현재 연결 상태

아직 연결된 것이 없다.
`prompts/`, `stages/`, `runner.py`, `schemas/` 어디에서도 `source/`를 참조하지 않는다.

따라서 지금 컴포넌트를 쓰는 유일한 경로는 사람이 작업 지시에 직접 경로를 적는 것이다.

```text
Use reusable components from:
- `source/common/components/AGENTS.md`
- `source/common/components/speech-bubble/component.md`
- `source/common/components/keypad/component.md`

조립 예시는 `source/common/components/example/index.html`을 참고한다.
inline 순서는 `docs/reusable-source-design.md` 7.5를 따른다.
```

컴포넌트를 실제로 한 번 재사용해본 뒤에 파이프라인 연결 방식을 정한다.
쓰이지 않는 상태에서 먼저 자동화하지 않는다.

---

## 9. 재사용 후보 초기 목록

이 목록은 **이미지 catalog 축**의 후보다. 7장의 컴포넌트 축과는 별개로 진행한다.
컴포넌트로 이미 다룬 항목이라도 이미지 asset 자체는 아직 catalog화되지 않았다.

현재 산출물에서 먼저 catalog화할 후보는 다음 순서가 좋다.

1. `speech_bubble`
   - `speech_bubble_blank`
   - `library_dialogue_plate`
   - `school-speech-bubble-body`
2. `feedback`
   - correct/wrong stamp
   - center effect
   - feedback bubble timing
3. `cta`
   - ticket button body
   - intro/activity/completion CTA body
4. `clock`
   - body asset
   - CSS hand overlay
   - spin/glow/recheck states
5. `keypad`
   - keycap body
   - numeric keypad layout
   - clear/backspace/confirm controls
6. `certificate`
   - certificate paper
   - safe zone text overlay
   - save button
7. `debug`
   - scene jumper
   - question seek list
   - `__contentHarnessShowScene`
8. `character`
   - teacher idle/explaining/praising
   - student idle/thinking/volunteer

---

## 10. 운영 절차

### 10.1 새 후보 추가

1. run 또는 production에서 재사용 후보를 찾는다.
2. 이미지를 `source/common/assets/...` 또는 `source/[teacher]/assets/...`로 복사한다.
3. md catalog에 항목을 추가한다.
4. `Status: candidate`로 시작한다.
5. 실제 작업에서 1~2회 재사용해 문제가 없으면 `approved`로 바꾼다.

### 10.2 새 작업에서 사용

1. 필요한 catalog 항목을 고른다.
2. reference path 또는 md anchor를 작업 지시에 넘긴다.
3. 이미지 asset은 반드시 실제로 열어 확인한다.
4. md의 `Use when`과 `Avoid`를 지킨다.
5. 새 run 결과가 더 좋은 기준이면 source candidate로 다시 올린다.

### 10.3 Deprecated 처리

다음 중 하나에 해당하면 `deprecated`로 바꾼다.

- 같은 역할의 더 좋은 approved reference가 생김
- 특정 선생님 정체성이 강해 common으로 쓰기 부적절함
- 텍스트가 굽혀져 있어 재사용 범위가 좁음
- CSS/SVG 패널처럼 보여 현재 asset 품질 기준과 맞지 않음

파일은 바로 삭제하지 않는다.
사용자 확인 없이 파일 삭제를 하지 않는 프로젝트 규칙을 따른다.

---

## 11. 나중에 자동화할 수 있는 것

초기에는 md catalog로 충분하다.
반복 사용이 늘어나면 다음을 고려한다.

- `source_index.json`: md를 읽지 않고도 전체 reference 목록을 기계적으로 조회
- `reference bundles`: `teacher-a-basic`, `common-feedback-v1`처럼 묶음 단위로 input에 연결
- `source lint`: md의 Path가 실제 파일인지 검사
- `asset promotion script`: run 산출물을 source candidate로 복사하고 md 템플릿 생성
- `visual contact sheet`: source 이미지를 한 화면에서 비교하는 HTML 생성

자동화는 catalog가 충분히 쌓인 뒤에 한다.
지금은 이미지와 짧은 사용 계약을 안정적으로 모으는 것이 우선이다.
