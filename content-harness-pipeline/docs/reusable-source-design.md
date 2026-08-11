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
| 컴포넌트 추출 (7개) | 완료, 전부 `candidate` | `source/common/components/` |
| 컴포넌트별 단독 확인 페이지 | 7개 모두 있음 | `source/common/components/[component]/preview.html` |
| 조립 확인 페이지 | 있음 | `source/common/components/example/index.html` |
| craft example (12장) | 2개, `approved`. 파이프라인 연결됨 | `source/common/craft-examples/` |
| teacher source (4장) | `baek-seungyong` 1명, 16항목. 파이프라인 연결됨 | `source/baek-seungyong/` |
| common 이미지 catalog (3장) | 미착수 | — |
| 파이프라인 연결 (8장) | 세 축 모두 스캔으로 연결됨 | `stages/scripts/` |

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

    craft-examples/      # 구현됨. 상세는 12장
      CLAUDE.md
      AGENTS.md
      [example]/
        example.md

    AGENTS.md            # 미구현
    assets.md            # 미구현
    assets/              # 미구현
      speech-bubble/
      feedback/
      cta/
      header/
      list/
      debug/

  baek-seungyong/        # 구현됨. 상세는 4장
    CLAUDE.md
    AGENTS.md
    characters.md        # `## 항목` + `- Path:`가 catalog 항목
    assets.md
    style.md             # 화풍 계약. catalog 항목은 없다
    assets/
      characters/
      backgrounds/
      props/
      ui/                # style_reference_set에 ui 범주가 없어 Category는 props
      cta/
```

항목이 많아지기 전까지는 `assets.md`, `characters.md`, `style.md` 정도만 둔다.
분량이 커지면 `feedback.md`, `speech-bubble.md`, `headers.md`처럼 나눈다.

디렉토리 설명은 `README.md`가 아니라 **`AGENTS.md`**로 둔다.
그 디렉토리에서 작업하는 AI가 자동으로 먼저 읽는 파일이기 때문이다.
사람용 소개가 따로 필요해지면 그때 `README.md`를 추가하고, 제약과 사용 절차는 `AGENTS.md`에 남긴다.

이 source에는 세 개의 축이 있다.

| 축 | 위치 | 다루는 것 | 참조와 결과의 관계 | 현재 상태 |
|---|---|---|---|---|
| common 이미지 catalog | `common/assets/` | 재사용 이미지와 사용 계약 (3장) | 그대로 쓴다 | 미착수 |
| teacher 화풍 | `[teacher]/` | 선생님별 화풍 기준 (4장) | **화풍은 따르고 소재는 안 가져온다** | 1명, 파이프라인 연결됨 |
| 컴포넌트 | `common/components/` | HTML/CSS/JS 재사용 원본 (7장) | 그대로 inline한다 | 7개 추출, 다음 후보는 7.7 |
| craft example | `common/craft-examples/` | 글자를 굽는 asset의 완성도 기준 (12장) | **베끼면 실패다** | 2개, 파이프라인 연결됨 |

네 축은 독립적으로 진행할 수 있다.

**축마다 "참조를 얼마나 그대로 가져오는가"가 다르다.** 이게 축을 나누는 기준이다.

| 축 | 가져오는 것 | 가져오면 안 되는 것 |
|---|---|---|
| 컴포넌트 · common 이미지 | 전부 | — |
| teacher 화풍 | 선·채도·명암·밀도·등신·재질 | **소재**(그 이미지에 찍힌 사물과 장소), 인물 정체성 |
| craft example | 완성도(구조와 재질 논리) | **색·모티프·세계관** — 그 run의 `art_direction`을 따라 새로 그린다 |

teacher 축과 craft example 축을 섞으면 이 경계가 사라진다. 상세는 4장과 12장.

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

현재 `source/baek-seungyong` 하나가 있고 `production/1-2/08`에서 뽑았다. 16항목이 catalog화됐다.

### 4.0 이름이 같으면 teacher가 common을 덮는다

**세부가 일반을 이긴다.** 같은 `keypad`가 common과 teacher 양쪽에 있으면
그 선생님 콘텐츠에서는 teacher 것만 쓴다. 캐릭터 design reference도 같다.

```text
source/common/components/keypad/          ← 무시됨
source/baek-seungyong/components/keypad/  ← 이것만 쓴다
```

**병합하지 않고 통째로 교체한다.** 둘을 섞으면 teacher가 일부러 뺀 규칙이 common에서 되살아나고,
무엇이 실제로 적용되는지 파일만 봐서는 알 수 없게 된다. 덮어쓸 거면 전부 책임진다.

`stages/scripts/source_resolve.py`의 `shadowed_dirs()`가 이 판정을 하고,
컴포넌트 축(`common_components`, `component_bundle`)과 craft example 축(`craft_examples`)이 함께 쓴다.
teacher가 누구인지는 `input.metadata.style_reference_set.root`가 정한다 — 그 키가 없으면 common만 쓴다.

`_shared`나 `example`처럼 부속 디렉토리는 `component.md`가 없어서 애초에 항목이 아니다.

### 4.0.0 소재가 아니라 화풍을 가져온다

**이 축에서 가장 자주 틀리는 지점이다.**

teacher source의 이미지는 어떤 차시에서 뽑혔으므로 그 차시의 소재가 찍혀 있다.
`baek-seungyong`의 배경에는 학교 담장이, 소품에는 페인트 통이 있다.

다른 차시가 가져올 것은 그 소재가 아니라 **선, 채도, 명암 단계, 밀도, 재질 표현, 등신, 표정 언어**다.
도서관 차시가 학교 담장을 그리면 실패다.

그래서 각 항목의 `Avoid`에는 **그 이미지의 소재 중 무엇을 가져오면 안 되는지**를 개별로 적는다.
`Avoid`를 비워 두면 모델은 참조를 "베껴도 되는 그림"으로 읽는다.

캐릭터도 같다. `characters.md`의 인물은 얼굴·헤어·의상·이름을 복제하라고 두는 것이 아니라,
**성인 여성 / 성인 남성 / 어린이를 각각 어떻게 그리는지** 보여주려고 둔다.

### 4.0.1 catalog 형식

`## 제목` 절에 `- Path:`가 달리면 catalog 항목이고, 없으면 산문이다.
`stages/scripts/teacher_source.py`가 이 규칙으로 스캔하므로 **사람이 읽는 설명과 기계가 읽는 항목이
한 파일에 공존할 수 있다.** 필드는 `Path` / `Category` / `Status` / `Role` / `Use` / `Avoid`다.

`Category`는 `style_reference_set`이 지원하는 네 범주(`backgrounds`/`characters`/`props`/`ctas`)만 쓴다.
UI 표면처럼 범주가 없는 것은 디렉토리만 `ui/`로 두고 `Category`는 `props`로 적는다.
한 케이스 때문에 공용 범주 목록을 넓히지 않는다.

캐릭터는 **계열당 한둘만** 항목으로 만든다. 같은 인물의 모든 pose를 항목으로 만들면
그 계열이 참조 묶음을 다 차지해 배경·소품이 밀린다. pose 목록은 표로 두고 스캔되지 않게 한다.

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

  topbar/
    component.md
    template.html        # .c-topbar + .c-courseMenu 두 블록
    preview.html
    style.css
    behavior.js

  speech-bubble/
    component.md
    template.html
    preview.html         # 이 컴포넌트만 띄우는 확인 페이지
    style.css
    behavior.js

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
- 한 컴포넌트가 서로 떨어진 두 블록을 요구하면 `template.html`에 둘 다 담고
  어디에 놓아야 하는지를 주석에 적는다(`topbar`의 상단 바와 목록 드로어).

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
| `topbar` | `data-state` + class + 네이티브 | 바 `hidden`/`visible`, 드로어 `is-open`, 항목 `is-current`/`is-locked`+`disabled`, 소리 `aria-pressed` |
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
window.CommonTopbar          = { init, setTitle, setStep, setProgress, setSoundOn, setHidden, openMenu, closeMenu }
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

지금 이 이벤트를 듣는 쪽은 `debug-jumper`(현재 항목 표시)와 `topbar`(단계 라벨, 진행률)다.
`scene-controller`는 누가 듣는지 모른다. 새 컴포넌트도 controller를 직접 부르지 않고 이 이벤트를 듣는다.

기존 output HTML을 바로 고칠 때는 무리하게 전부 rename하지 않는다.
새 source component부터 이 규칙을 따른다.

### 7.5 합성 방식

초기에는 자동 assembler를 만들지 않는다.
builder/refiner가 reference로 받은 컴포넌트 조각을 읽고 단일 HTML에 inline한다.

나중에 자동화가 필요하면 다음 흐름으로 확장한다.

```text
component template.html      → 모델이 마크업으로 넣는다
component style.css   ┐
component behavior.js ┴→ emit_common() → output/common.css · common.js
        ↓
output/index.html
```

**컴포넌트는 이미지를 소유하지 않는다.** `output/assets/`에 들어가는 것은 그 run이 생성한 asset뿐이다.

합성 시 지켜야 할 규칙:

- CSS와 JS는 코드가 `output/common.css` · `output/common.js`로 내보낸다. 모델이 옮겨 적지 않는다.
- HTML에는 `<link>` · `<script src>` 두 줄만 둔다. 그 뒤의 콘텐츠 `<style>`에서 오버라이드한다.
- **컴포넌트는 이미지를 소유하지 않는다.** `source/`의 어떤 파일도 `output/assets/`로 복사하지 않는다.
  `output/assets/`에 들어가는 것은 그 run이 생성한 asset뿐이다.
- art가 필요한 컴포넌트는 생성된 asset 경로를 밖에서 받는다 (`--cta-body`, `data-*-src`).
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
| 7 | `topbar` | 제목·단계 라벨·진행률·소리 토글, 차시 목록 드로어 | 추출됨 (`candidate`) |
| 8 | `clock` | body asset, CSS hands, spin/glow/recheck states | 미추출 |

전부 `production/1-2/08/index.html`에서 뽑았고, 아직 `candidate`다.
다른 차시에 한 번 이상 실제로 붙여본 뒤 `approved`로 올린다.

`topbar`는 08이 `1-2/01`에서 이미 한 번 이식한 조각이라 다른 차시에서 성립한다는 근거가 있다.
`feedback-layer`는 지금 stamp만 담당하고, pose swap과 center effect는 아직 콘텐츠 쪽에 남아 있다.

### 7.7 다음 추출 후보

기준은 `source/common/components/CLAUDE.md`의 질문 그대로다 — **"다음 차시에서 이걸 그대로 쓸까?"**
08에서 뽑되 08의 학습 내용에 묶이지 않은 것만 올린다.

| 우선 | 후보 | 08의 근거 | 왜 common인가 | 주의 |
|---|---|---|---|---|
| 1 | `dialogue-advance` | `.tap-layer`, `.narration-advance`, `.repair-bubble-nav`, `.repair-narr-next` | 대사를 넘기는 방식(전면 탭 + `다음 ▸`)은 대사가 있는 모든 콘텐츠에 있다 | `speech-bubble` 안에 들어가는 배치와 화면 중앙 단독 배치 둘 다 있다. 두 배치를 모두 지원해야 한다 |
| 2 | `choice-list` | `.choices`, `.choice`, `.choice.reveal` | 3.1의 `list` 범주 그대로. 보기 카드 없는 문항형 콘텐츠가 드물다 | 08은 `#randomInput .choice`에서 CSS surface를 배경 asset(plaque)으로 갈아끼운다. 기본형은 CSS, asset은 옵션으로 둔다 |
| 3 | `confirm-dialog` | `.confirmation`, `.confirm-panel`, `.confirm-btn` | 되돌릴 수 없는 조작 앞의 확인 모달 | `topbar` 드로어와 같은 `--z-drawer`를 쓴다. 둘이 동시에 열리지 않게 하는 책임은 콘텐츠에 있다 |
| 4 | `hint-finger` | `.finger-hint`, `.finger-hint-label`, `searchFingerTap` | 어디를 눌러야 하는지 알려주는 손가락 + 라벨. 저학년 콘텐츠 공통 | 위치는 콘텐츠가 준다. asset이 필요하므로 이미지 catalog 축과 함께 간다 |
| 5 | `audio` (runtime) | `playSfx`/`SFX_FILE`, `ensureSynthCtx`/`synthTone`/`SFX_SYNTH.tick`, `playVoice`/`stopVoice`/`playVoiceQueue`, `speak` | `topbar`의 소리 토글이 이미 이걸 전제한다. 자동재생 차단 폴백과 TTS 폴백 정책이 콘텐츠마다 다시 쓰이고 있다 | 시각 컴포넌트가 아니다. `template.html`이 없는 runtime 모듈로 둔다 |
| 6 | `help-toggle` | `.help-character`, `.speech.help-speech` | 화면 구석 도우미를 눌러 도움말 대사를 여는 패턴 | 캐릭터 이미지는 teacher source다. 컴포넌트는 토글과 배치만 가진다 |
| 7 | `certificate` | `.repair-cert-*` (overlay, 이름 입력, 저장 버튼) | 9장 목록에도 이미 있다. 완료 보상은 차시마다 반복된다 | 이름 입력과 저장은 브라우저 API에 닿는다. 저장 방식은 콘텐츠가 주입한다 |
| 8 | `cursor` | `#cursor`, `.cursor-image`, `@media (pointer:coarse)` | 커스텀 커서와 터치 기기 방어는 차시와 무관하다 | stage 밖 `position:fixed`라 stage 배율을 곱하지 않는다 |
| 9 | `title-banner` | `.title-banner`, `.hero-title`, `.title-image` | 씬 제목판의 자리·크기 계약 | 문구를 구운 asset은 차시별이다. 컴포넌트는 자리와 크기만 갖는다 |
| 10 | `question-panel` | `.panel`, `.question-panel`, `.prompt` | 문항을 얹는 기본 surface | 08은 `.panel`을 여러 씬에서 조금씩 덮어쓴다. 기본형만 올리고 변형은 콘텐츠에 남긴다 |

컴포넌트가 아니라 `_shared/base.css`로 올릴 것:

- 08 `:root`에만 있는 토큰 — `--ds-sm`, `--ds-md`, `--shadow-press`, `--shadow-none`, `--r-none`,
  `--filter-glow-sm/md/lg`. 위 후보를 옮기면 바로 필요해진다.
- 여러 컴포넌트가 함께 쓰는 keyframes — `pop`, `stamp`, `shake`, `sparkle`.

common에 올리지 않을 것 (08의 학습 내용에 묶인다):

- `paint-shape` / `paint-can` / `paint-tools` / `#drawingCanvas` — 색칠·도형 그리기 전용
- `find-object` / `hotspot` / `glow-*` — 모양 찾기 상호작용. 다른 콘텐츠에서 또 필요해지면 그때 올린다
- `sign-row` / `story-card` / `#completedMuralPreview` / `.repair-fx` — 08의 서사 장치

이 목록은 한 번에 다 옮기는 계획이 아니다.
`topbar`처럼 **다른 차시에 실제로 붙일 일이 생겼을 때** 하나씩 올린다.

---

## 8. 파이프라인 연결 방식

`metadata.style_reference_set`이 teacher 축의 입구다. 지원 범주는 네 개다 —
`backgrounds` / `characters` / `props` / `ctas`.

**`categories`는 적지 않는다.** 생략하면 `teacher_source.load_catalog()`가 `root`의 md를 스캔해 채운다.

```json
{
  "metadata": {
    "style_reference_set": {
      "id": "teacher-a-basic",
      "must_follow": true,
      "root": "source/teacher-a",
      "usage_policy": {
        "summary": "이미지를 직접 열어 확인하고 description보다 reference image를 우선한다. 항목별 use/avoid는 catalog가 소유한다."
      }
    }
  }
}
```

`categories`를 명시하면 그대로 쓴다. catalog 밖의 이미지를 한 번만 끼워 넣을 때와,
기존 input이 계속 동작해야 하기 때문에 남겨 둔 경로다.

### 8.0 input 계약

`schemas/input.schema.json`이 `metadata.style_reference_set`의 모양을 강제한다.
`required`는 `id`와 `root`이고 `additionalProperties: false`라 오타 필드가 거절된다.

**on/off 플래그를 따로 두지 않는다.** `style_reference_set` 키의 유무가 곧 on/off다.
`teacher_reference: true`를 따로 두면 플래그와 내용이 어긋날 수 있고(true인데 `root`가 없는 상태),
그때 어느 쪽이 맞는지 판정할 근거가 없다. 강도는 `must_follow`가 이미 표현한다.

schema는 모양만 본다. 경로가 실제로 있는지는 `validate.py`가
`resolve_style_reference_set()`을 직접 불러 확인한다. **stage 안에서 처음 해석하면
run 디렉토리와 input 사본을 만든 뒤에야 실패하므로** 같은 검사를 입력 검증 단계로 당겼다.

`python -B ./validate.py ./input.json --artifact input`이 잡는 것:

| 잘못된 입력 | 잡는 층 |
|---|---|
| `root` 누락, 오타 필드, 타입 불일치 | schema |
| 없는 디렉토리, 없는 이미지, root 밖 경로, 지원 안 하는 확장자 | 해석 |
| `must_follow: true`인데 참조 0개 | 해석 |
| catalog에 `- Path:` 항목이 하나도 없음 | 해석 |

**차시마다 `use`·`avoid`를 input에 옮겨 적지 않는다.** 그 사본이 catalog와 갈라지고
어느 쪽이 맞는지 알 수 없게 된다. 이건 "컴포넌트 목록을 프롬프트에 손으로 적지 않는다"와
같은 규칙의 다른 입구다.

Common debug/html 패턴은 아직 `style_reference_set`보다 넓은 범위다.
common 이미지 catalog(3장)가 생기기 전까지는 `user_request`나 작업 지시에서 md path를 직접 넘긴다.

```text
Use reusable references from:
- `source/common/assets.md#speech-bubble-basic`
```

컴포넌트 축, craft example 축, teacher 축은 8.1처럼 이미 파이프라인에 연결됐다.

### 8.1 현재 연결 상태 (2026-08-11)

**컴포넌트 축과 craft example 축은 연결됐다. 이미지 catalog 축은 아직이다.**

두 축은 같은 패턴을 쓴다. 스캔 모듈이 **항상 싣는 규칙 블록** 하나와 **선택용 manifest** 하나를 만들고,
그 stage 프롬프트에 붙인다.

| 축 | 모듈 | 붙는 stage |
|---|---|---|
| 컴포넌트 | `stages/scripts/common_components.py` | `builder` · `design_refine` · `content_refine` |
| craft example | `stages/scripts/craft_examples.py` | `asset_generator` |
| teacher 화풍 | `stages/scripts/teacher_source.py` | `planner` · `asset_generator` |

**규칙 블록을 통째로 싣고 manifest는 경로만 넘기는 이유는 두 축이 같다.** 규칙 블록에 있는 것은
어긋나면 그 뒤 모든 판단이 함께 흔들리는 것(컴포넌트는 `:root` 토큰, craft example은 우선순위 규칙)이고,
개별 항목의 상세 계약은 stage가 고른 뒤 `component.md` / `example.md`를 직접 열어 읽는다.

`stages/scripts/common_components.py`가 `source/common/components`를 스캔해 두 블록을 만들고,
`builder` · `design_refine` · `content_refine` 세 stage 프롬프트에 같은 블록이 들어간다.

| 블록 | 내용 | 왜 이 방식인가 |
|---|---|---|
| `COMMON_BASE_CSS` | `_shared/base.css` 전문 | 토큰은 코드가 강제한다. builder가 `:root`를 처음 선언하는 주체이고, 여기서 어긋나면 이후 모든 stage의 `var()` 참조가 함께 흔들린다 |
| `COMMON_COMPONENTS_JSON` | 컴포넌트별 경로 + `type`/`status`/`final_output`/`use_when`/`avoid`/`runtime_api` | manifest의 일은 **고르게 하는 것**까지다. slot·state·DOM 계약은 stage가 고른 뒤 `component.md`를 직접 열어 읽는다 |

manifest는 파일 스캔으로 만든다. 목록을 프롬프트에 손으로 적지 않는다 —
컴포넌트가 늘어날 때 세 stage 프롬프트가 서로 어긋나는 것을 막는다.

사용 규칙(선택 기준, inline 순서, 계약 보존)은 `prompts/common_html_contract.md`의
"공용 컴포넌트 재사용" 한 곳에만 있다. stage별 system prompt에는 적지 않는다.

**계약 보존이 이 연결의 핵심 위험이다.** `design_refine`은 HTML을 통째로 다시 쓰므로,
`c-` prefix · `data-slot` · `window.Common*`를 보존하라는 규칙이 없으면 한 iteration 만에
컴포넌트가 풀어헤쳐진다. 그래서 계약 문서에 그 조항을 함께 넣었다.

craft example 축은 `stages/scripts/craft_examples.py`가 같은 방식으로 두 블록을 만든다.

| 블록 | 내용 | 왜 이 방식인가 |
|---|---|---|
| `CRAFT_EXAMPLES_RULES` | `craft-examples/CLAUDE.md` 전문 | 우선순위 규칙("`art_direction`이 예시를 이긴다")이 여기 있다. 이게 빠지면 모델이 `identity_context` 습관대로 예시의 팔레트와 모티프를 복제해 그 run의 `art_direction`을 덮어쓴다 |
| `CRAFT_EXAMPLES_JSON` | 예시별 경로 + `type`/`status`/`applies_to`/`take`/`do_not_take`/`images` | `applies_to`가 선택 기준이다. 만들려는 asset이 거기 해당하면 stage가 `example.md`와 이미지를 직접 연다 |

이 축은 `asset_generator` 한 stage에만 붙는다. 글자를 이미지에 굽는 주체가 거기뿐이기 때문이다.
굽느냐 마느냐를 정하는 것은 planner이고(`prompt_brief`에 문구를 명시하는지), 그 판정 기준은
`prompts/planner_system.md`의 "이미지 안의 텍스트(가변 vs 고정)" 절에 있다. **완성도 기준과 굽기 판정은
서로 다른 층이므로 한쪽에 몰아 적지 않는다.**

teacher 축은 입구가 다르다. **프롬프트가 아니라 `input.json`의 `metadata.style_reference_set`** 이
어느 선생님을 쓸지 고른다. run마다 다른 선생님을 쓸 수 있으므로 코드가 하나를 강제할 수 없다.

`categories`를 생략하면 `teacher_source.load_catalog()`가 `root`의 md를 스캔해 채운다.
명시하면 그대로 쓴다 — catalog 밖의 이미지를 한 번만 끼워 넣는 경우와 기존 input 호환을 위해 남겼다.

**항목별 `use`·`avoid`는 `source/[teacher]/*.md`가 소유한다. input.json에 다시 적지 않는다.**
차시마다 옮겨 적으면 그 사본이 catalog와 갈라지고 어느 쪽이 맞는지 알 수 없게 된다.
이 규칙은 "컴포넌트 목록을 프롬프트에 손으로 적지 않는다"와 같은 규칙의 다른 입구다.

아직 안 된 것:

- common 이미지 catalog(3장)는 아직 없다. 작업 지시로 사람이 경로를 넘긴다.
- 어떤 컴포넌트를 쓸지는 stage가 `use_when`/`avoid`를 보고 고른다. planner가 미리 지정하지 않는다.
- craft example은 `asset_generator`만 본다. `design_review`는 이 기준으로 판정하지 않는다 —
  구운 글자의 완성도가 낮아도 게이트에 걸리지 않는다.
- teacher catalog에는 **선택 기능이 없다.** `root`의 모든 항목이 참조 묶음에 들어가고,
  그중 2~3개를 고르는 일은 `asset_generator`가 `role`/`use`를 보고 한다.
  항목이 많아지면 subset 지정이 필요해질 수 있다.
- **참조가 실제로 쓰였는지 산출물에 남지 않는다.** codex는 `view_image`로 참조를 열어 볼 수 있고
  `image_gen__imagegen`의 `referenced_image_paths`로 참조를 이미지 생성에 넘길 수 있다.
  프롬프트가 양쪽을 지시하지만(`asset_generator_system.md`), `asset_generator_output.schema.json`에
  **어떤 참조를 넘겼는지 기록하는 필드가 없다.** 결과 이미지가 화풍을 벗어났을 때
  "참조를 안 봤는지" 대 "보고도 못 따라갔는지"를 구분할 수 없다.
  참조 축의 효과를 측정하려면 asset별 `style_references_used`를 기록하는 것이 다음 후보다.

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
  (컴포넌트 축과 craft example 축은 `common_components.py` / `craft_examples.py`가 이미 런타임에 만든다.
  파일로 굳힐 필요가 생기면 그때 한다)
- `reference bundles`: `teacher-a-basic`, `common-feedback-v1`처럼 묶음 단위로 input에 연결
- `source lint`: md의 Path가 실제 파일인지 검사
- `asset promotion script`: run 산출물을 source candidate로 복사하고 md 템플릿 생성
- `visual contact sheet`: source 이미지를 한 화면에서 비교하는 HTML 생성

자동화는 catalog가 충분히 쌓인 뒤에 한다.
지금은 이미지와 짧은 사용 계약을 안정적으로 모으는 것이 우선이다.

---

## 12. Craft Example

`source/common/craft-examples`는 **글자를 이미지에 굽는 asset의 완성도 기준**을 그림으로 둔다.
사용 계약은 `source/common/craft-examples/CLAUDE.md`에 있고, 이 장은 왜 이 축이 따로 있는지를 적는다.

### 12.1 왜 다른 두 축과 섞지 않는가

1.1에서 "이미지를 source of truth로 둔다"고 했지만, **이 축은 그 규칙이 뒤집힌다.**

| | 이미지 catalog · teacher source | craft example |
|---|---|---|
| 이미지가 말하는 것 | 어떤 그림이어야 하는가 | 얼마나 잘 만들어야 하는가 |
| description과 충돌하면 | 이미지가 이긴다 (1.1) | 그 run의 `art_direction`이 이긴다 |
| 그대로 재현하면 | 정답 | **실패** |
| run에 따라 | 달라진다 | 변하지 않는다 |

같은 `source/common/assets/` 아래 두면 이 구분이 사라진다.
디렉토리 이름이 `assets`가 아니라 `craft-examples`인 것도 같은 이유다 — 가져다 쓰는 asset이 아니다.

`identity_context`와 비교하면 더 분명하다. `identity_context`는 같은 인물을 재현해야 하므로
이미지가 텍스트를 이긴다. craft example은 반대다. **명시하지 않으면 모델이 `identity_context` 습관대로
예시의 팔레트와 모티프를 복제해, run마다 새로 정한 `art_direction`을 덮어쓴다.**

### 12.2 왜 규칙이 아니라 그림인가

굽기 규칙 자체는 이미 말로 있다 — `planner_system.md`의 "도장 글자는 도장 면 안에 새겨지고,
타이틀 글자는 장식과 얽힘". 예시는 **새 규칙이 아니라 그 규칙의 합격선**이다.
"한 덩어리로 통합한다"가 어느 정도를 뜻하는지는 문장으로 전달되지 않는다.

따라서 예시가 늘어나도 규칙이 늘어나는 것은 아니다.
새 예시를 넣는 기준은 "새 규칙이 필요한가"가 아니라 **"이 종류의 asset에서 합격선을 말로 못 전하고 있는가"** 다.

### 12.3 구조

한 디렉토리 = 하나의 **craft 주제**다. 이미지 한 장이 아니다.
같은 주제 안에서 서로 대비되는 이미지가 여러 장이면 한 디렉토리에 함께 둔다.

```text
source/common/craft-examples/
  CLAUDE.md              # 축 전체의 우선순위와 합격 판정. 프롬프트에 전문이 실린다
  AGENTS.md              # CLAUDE.md를 가리킨다

  title-lettering/
    example.md
    title-lettering-craft.png

  stamp-lettering/
    example.md
    stamp-lettering-correct.png
    stamp-lettering-wrong.png
```

`stamp-lettering`이 한 디렉토리에 두 장을 두는 이유는 그 둘이 형제여서가 아니라 **정반대다.**
`example.md`가 "이 두 장은 완전히 별개의 asset"이라고 적는 자리가 필요하기 때문이다.
정답/오답을 한 asset으로 만들고 CSS `filter`로 색만 바꾸는 실패가 실제로 있었다.

### 12.4 `example.md`의 필수 필드

| 필드 | 역할 |
|---|---|
| `Applies to` | **선택 기준.** 어떤 asset을 만들 때 이 예시를 열어야 하는지 |
| `Take` | 콘텐츠가 달라도 유지되는 구조·재질 논리 |
| `Do not take` | 그 예시에만 해당하는 색·모티프·소재 |

`Take`와 `Do not take`의 경계가 곧 12.1의 우선순위 표를 개별 예시에 적용한 결과다.
이 경계를 적지 않으면 예시는 "베껴도 되는 참조"로 읽힌다.

`## 상세` 이후는 manifest가 읽지 않는다. stage가 이 예시를 고른 뒤 직접 읽는다.

### 12.5 아직 없는 것

- **CTA 예시가 없다.** 굽기 판정 자체는 정해졌지만(2026-08-11, `planner_system.md`) 합격선을 보여줄
  기준 이미지가 없어서, CTA는 `CRAFT_EXAMPLES_RULES`의 일반 합격 판정만으로 만들어진다.
  구운 CTA가 나오면 그중 하나를 이 축의 세 번째 예시로 올린다.
- **`design_review`가 이 기준을 보지 않는다.** 구운 글자의 완성도가 낮아도 게이트에 걸리지 않는다.
  현재는 asset_generator가 한 번에 잘 만드는 데 의존한다.
- **구운 문구가 HTML에서 사라지는 것을 기계가 검사하지 않는다.** `alt_text` 경로
  (`planner_system.md`, `common_html_contract.md`)에 의존하고, 실제 대조는 `content_eval` LLM이 한다.
  구운 asset이 늘수록 이 지점이 커진다.
