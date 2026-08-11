# Common Components

## 이 디렉토리의 성격

**선생님·차시·콘텐츠 세계관과 무관하게 재사용하는 공용 UI 컴포넌트 모음이다.**

여기 있는 조각은 누가 만든 콘텐츠든, 어떤 학년·과목이든 그대로 가져다 쓸 수 있어야 한다.
특정 선생님의 얼굴, 의상, 말투, 브랜드 색이 들어간 것은 여기 두지 않는다.
그런 것은 `source/[teacher]/`에 둔다.

`production/1-2/08`에서 1차 추출했지만, **08 전용이라는 뜻이 아니다.**
08은 출처일 뿐이고, 여기 올라온 이상 다른 차시에서도 성립해야 한다.

### 여기 두는 것

- 어떤 콘텐츠에나 있는 기능: scene 전환, 숫자 입력, 정답/오답 판정 표시, CTA, debug
- 형태가 아니라 **역할**로 이름 붙일 수 있는 것 (`keypad`, `speech-bubble`)
- 색과 크기가 토큰(`_shared/base.css`)으로 갈리는 것

### 여기 두지 않는 것

- 특정 선생님 캐릭터가 들어간 말풍선·CTA·피드백
- 한 차시의 학습 내용에 묶인 UI (시계 읽기 전용 판, 특정 문제 유형 전용 보드)
- 그 콘텐츠에서 한 번만 쓰는 레이아웃

판단이 애매하면 **"다음 차시에서 이걸 그대로 쓸까?"** 를 묻는다.
아니라면 콘텐츠 쪽에 두고, 두 번째 콘텐츠에서 같은 게 또 필요해질 때 올린다.

## 최종 산출물과의 관계

최종 산출물은 여전히 `runs/.../output/index.html` **단일 파일**이다.

여기 있는 `template.html`, `style.css`, `behavior.js`, `assets/`는 그 단일 파일을 만들기 전
**수정하기 쉬운 원본**이다. builder/refiner 또는 나중의 assembler가 이 조각들을 최종 HTML에 inline한다.

따라서 `template.html`은 그 자체로 실행되는 페이지가 아니라 **마크업 조각**이다.
브라우저에서 직접 열면 스타일도 동작도 없는 게 정상이다.
실제로 동작하는 것을 보려면 그 컴포넌트의 `preview.html`이나 `example/index.html`을 연다.

## 구성

| Component | Source | Notes |
|---|---|---|
| `scene-controller` | `production/1-2/08/index.html` scene 전환 | `data-qa-scene`, `active/leaving` 계약 |
| `speech-bubble` | 08 `.speech` | 1-2/01에서 이식된 크림 말풍선 |
| `ticket-button` | 08 `.cta.activity-cta` | `activity-cta-body.webp` sprite 기반 CTA |
| `keypad` | 08 `buildKeypad` | `[1..9][← 0 확인]` 숫자 키패드 |
| `feedback-layer` | 08 `showStamp`/feedback overlay | 정답/오답 도장 |
| `debug-jumper` | 08 debug panel | `data-qa-*`에서 scene 목록 자동 구성 |

전부 `Status: candidate`다. 다른 차시에 한 번 이상 이식해본 뒤 `approved`로 올린다.

| 경로 | 역할 |
|---|---|
| `_shared/base.css` | 토큰, `#stage` 1920x1080, `.scene` 기본 계약. 컴포넌트 CSS가 이걸 전제한다 |
| `_shared/preview.css`, `_shared/preview.js` | preview 전용 harness (HUD, 컨트롤 버튼, stage 스케일) |
| `[component]/preview.html` | **그 컴포넌트 하나만** 띄우고 상태를 버튼으로 바꿔보는 페이지 |
| `example/index.html` | 전 컴포넌트를 한 흐름으로 조립한 페이지 |
| `[component]/component.md` | 그 컴포넌트의 사용 계약. 먼저 읽는다 |

**컴포넌트를 고쳤으면 `preview.html` → `example/index.html` 순서로 확인한다.**
`preview.html`은 그 컴포넌트가 혼자서도 성립하는지 보고, `example/`은 다른 컴포넌트와 함께 놓였을 때
겹치거나 깨지지 않는지 본다. 둘은 대체재가 아니다.

`preview.html`과 `example/`에서만 외부 폰트 CDN을 쓴다. 최종 output에는 옮기지 않는다.
`_shared/preview.*`도 preview 전용이므로 최종 output에 inline하지 않는다.

파일명이 `CLAUDE.md`인 이유: Claude Code는 `CLAUDE.md`만 자동으로 읽는다(`AGENTS.md`는 안 읽는다).
같은 디렉토리의 `AGENTS.md`는 이 파일을 가리키는 심링크다. 내용은 하나다.

## 쓰는 법

1. 필요한 컴포넌트의 `component.md`를 읽고 `Use when` / `Avoid`를 확인한다.
2. `template.html`을 마크업에 넣고, `data-slot` / `data-action` 계약을 유지한다.
3. CSS는 `_shared/base.css` → 컴포넌트 `style.css` → 콘텐츠 CSS 순서로 inline한다.
4. JS는 컴포넌트 `behavior.js`(전역 `window.Common*` 등록) → 콘텐츠 controller 순서로 inline한다.
5. asset은 `output/assets/`로 복사한다. `template.html`의 경로는 이미 `assets/...` 기준이다.

순서가 계약이다. CSS는 소스 순서로 우선순위가 갈리고, `behavior.js`는 전역을 등록만 하므로
controller보다 먼저 실행돼야 한다.

## 규칙

- **DOM 조회는 ID가 아니라 `data-component` / `data-slot` / `data-action`을 쓴다.**
  ID로 찾으면 그 컴포넌트는 특정 페이지에서만 동작한다.
- 컴포넌트 class는 `c-` prefix를 쓴다. 상태 class(`active`, `leaving`, `show`)에는 prefix를 붙이지 않는다.
- 상태 표현은 배타적이면 `data-state`, 전환 중 겹치면 class, 브라우저가 의미를 가지면 네이티브 속성(`disabled`, `hidden`)을 쓴다.
- 컴포넌트끼리 직접 호출하지 않는다. 필요하면 이벤트로 알린다 (`common:scenechange`).
- 컴포넌트를 고쳤으면 `preview.html` → `example/index.html`을 열어 확인하고, `component.md`의 `Runtime API`를 함께 갱신한다.
- 새 컴포넌트를 추가하면 `preview.html`도 함께 만든다. 상태가 있으면 그 상태를 바꿔볼 버튼을 넣는다.
- 외부 CDN·원격 이미지를 추가하지 않는다.

상세 설계는 `docs/reusable-source-design.md` 7장을 따른다.
