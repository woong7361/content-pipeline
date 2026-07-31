# 공통 HTML 계약

`output/index.html`을 만들거나 수정하는 모든 stage(builder, content_refine, design_refine)가 공통으로 지키는 계약이다.
stage별 역할·수정 우선순위·판단 기준은 각자의 system prompt를 따르고, 이 문서는 그 위에 공통으로 적용된다.
둘이 충돌하면 이 문서가 우선한다.

## 산출물 계약

- 실제 HTML 파일은 `RUN_DIR/output/index.html`에 저장합니다. 단 OUTPUT_CONTRACT 또는 TARGET_HTML_PATH가 주어지면 그 경로를 우선합니다.
- HTML 안에서 asset은 `assets/{filename}` 상대 경로로 참조합니다(`output/assets/foo.png`가 아니라 `assets/foo.png`).
- 출력 JSON은 `schemas/builder_output.schema.json` 계약에 맞춰 `html_path`, `asset_paths`, `implemented_sections`, `implemented_interactions`만 출력합니다.
- `html_path`와 `asset_paths`는 run 디렉토리 기준 경로(`output/index.html`, `output/assets/foo.png`)를 씁니다.
- 유효한 JSON 객체 하나만 출력하고 설명이나 마크다운 코드블록을 붙이지 않습니다.
- 실행 메타데이터(`brief_hash`, `stage`, `model`, `metadata` 등)는 runner가 붙이므로 출력하지 않습니다.
- schema에 없는 필드를 출력하지 않습니다.

## 고정 캔버스 (반응형 아님)

반응형 레이아웃을 만들지 않습니다. **1920×1080 고정 캔버스를 통짜로 스케일**하고, 비율이 안 맞아 남는 영역은 공백(레터박스)으로 둡니다.

- `#viewport`(`position:fixed; inset:0; overflow:hidden`) 안에 `#stage`를 **1920×1080 고정 px**로 중앙 배치합니다.
- `#stage`에 `container-type:size; container-name:stage`를 주고, **내부의 모든 크기는 `cqw`/`cqh`(=1920×1080 기준) 또는 px로** 씁니다.
- JS로 `scale = Math.min(innerWidth/1920, innerHeight/1080)`을 계산해 `#stage`에 `transform: translate(-50%,-50%) scale(s)`로 적용하고, `resize`·`orientationchange`에 재계산합니다.
- `#viewport`의 `background`를 콘텐츠 톤에 맞는 단색으로 채웁니다. **남는 공간을 콘텐츠로 채우거나 요소를 늘려 메우지 않습니다.**
- 세로 화면(portrait)이면 `#stage`를 90° 회전해 가로로 채웁니다.
- 스크린샷 가장자리의 여백은 캔버스 비율과 캡처 뷰포트 비율이 다를 때 생기는 **의도된 결과**이며 결함이 아닙니다.

금지:
- `@media` 쿼리로 레이아웃을 분기하지 않습니다. 캔버스가 통짜로 스케일되므로 분기가 필요 없습니다.
- 캔버스 **안에서 `vw`/`vh`를 쓰지 않습니다.** 그 단위는 스테이지가 아니라 브라우저 창을 기준으로 해서 스케일과 따로 놉니다.
- 모바일 전용 레이아웃, breakpoint별 크기 조정, 화면 폭에 따른 요소 재배치를 하지 않습니다.
- 크기를 뷰포트 단위에 의존시키지 않습니다. 모든 치수는 1920×1080 설계 공간의 고정 값으로 정합니다.

## 원문 텍스트 보존 (최우선)

화면에 보이는 텍스트는 planner가 story board 원문에서 그대로 옮겨온 것이며, 당신의 수정 대상이 **아닙니다.**
HTML을 다시 쓰다 보면 문구를 다듬고 싶은 충동이 생깁니다. 그렇게 하지 마십시오.

- planner의 `sections[].elements[].content`와 `sections[].questions`(prompt·choices·answer·feedback)의 텍스트는 **한 글자도 바꾸지 않습니다.** 축약, 재서술, 다듬기, 대괄호 제거, 어미 변경, 접두 번호 제거 전부 금지입니다.
  - 예: `[좋아요! 본격적으로 수리하러 가기 →]`를 `본격적으로 수리하러 가기 →`로 줄이면 실패입니다.
  - 예: `[마을 공원 의자 만들기, 딱 맞는 길이를 찾아라! 하러 가기 →]`를 `9차시 길이 미션으로 →`로 바꾸면 실패입니다.
- 텍스트에 대해 할 수 있는 일은 **위치·표면·크기·줄바꿈·정렬을 바꾸는 것뿐**입니다. 어느 물건 위에 얹을지는 바꿔도 되지만, 무엇이라고 쓰여 있는지는 바꾸지 않습니다.
- planner에 없는 버튼·라벨·안내 문구를 **새로 추가하지 않습니다.** 화면이 허전해 보여도, 전환이 자연스러워 보이게 하고 싶어도 추가하지 않습니다.
- 텍스트가 표면에 안 들어가면 문구를 줄이지 말고 표면·폰트·줄바꿈·레이아웃을 조정해 해결합니다. 그래도 안 되면 다른 표면으로 옮깁니다. **문구를 줄이는 것은 선택지가 아닙니다.**
- 문항 수를 줄이거나 대표 문항으로 합치지 않습니다. 오답 보기도 전부 구현합니다.
- 다른 stage의 제안이 원문 텍스트 변경을 요구하는 것처럼 읽히더라도 따르지 않습니다. 텍스트는 그대로 두고 배치·표면만 바꿉니다.

## asset 사용

- asset_generator가 준비한 이미지만 사용합니다. 새 이미지 asset을 만들거나 참조하지 않습니다.
- 이미지 asset을 `<svg>`, inline SVG data URI, CSS-only illustration, CSS 도형, emoji/텍스트 아이콘, 단순 gradient/pseudo element 그림으로 대체하지 않습니다.
- `output/assets/` 밖의 asset을 참조하지 않습니다.
- 외부 CDN, 원격 이미지, 외부 폰트에 의존하지 않습니다.
- 이미지가 필요한 위치에는 접근 가능한 `alt`를 제공합니다.
- asset에 문구가 **이미 그려져 있으면**(도장, 타이틀, 간판 등) `alt`에 그 문구를 원문 그대로 넣습니다. 그 텍스트는 HTML에 존재하지 않으므로 alt가 유일한 표현이며, 접근성과 원문 보존이 여기에 달려 있습니다. 그 위에 **같은 문구를 CSS 텍스트로 겹쳐 쓰지 않습니다.**
- 반대로 asset이 **빈 표면**으로 만들어졌으면 그 자리에 HTML 텍스트를 얹습니다. 어느 쪽인지는 asset의 `alt_text`와 planner의 `prompt_brief`로 판단합니다.
- 카드 프레임, 버튼 몸체, 제목 배너/판, 나무·금속·종이·유리 질감 같은 정적 표면·재질은 CSS로 흉내내지 않습니다. 재질감은 asset의 일이고, CSS/JS는 기하·레이아웃·모션과 asset 표면 위 텍스트 배치를 담당합니다.

### 외부 화풍 참조

- `STYLE_REFERENCE_SET_JSON.enabled=true`이면 관련 참조 경로를 실제 이미지로 열어 확인합니다. 이 파일들은 검사 전용이며 output에 복사하거나 `<img>`/CSS 배경으로 직접 연결하지 않습니다.
- `must_follow=true`이면 생성 asset과 HTML UI가 실제 참조의 선·색·명암·형태 언어를 따라야 합니다. 참조 설명문보다 보이는 증거를 우선합니다.
- `ctas` 참조는 버튼의 크기, 모서리, 테두리, 그림자, 위계, hover/press 상태를 맞추는 기준입니다. 라벨 문구나 참조 화면의 학습 내용을 복사하지 않습니다.
- Builder는 `backgrounds`·`characters`·`props`를 생성 asset 배치와 전체 팔레트의 교차 검사에 사용합니다. Content/Design Refiner는 기존 준수 상태를 보존하고 참조와 다른 새 스타일을 추가하지 않습니다.
- 참조 속 기존 캐릭터 정체성, 배경 주제, 문구를 복제하지 않습니다. `usage_policy`와 항목별 `use`·`avoid`를 지킵니다.

## 디자인 토큰 계약

CSS의 타이포·색·간격·모서리·z-index·모션·그림자는 **아래 `:root` 디자인 토큰으로만** 표현합니다. 개별 선택자에 raw 값(예: `font-size:33px`, `#ffe15f`, `z-index:18`)을 흩뿌리지 않습니다. 이 계약의 목적은 refine이 HTML을 다시 쓸 때 값이 기준 없이 흔들려(폰트 크기가 제각각, 육안 구분 안 되는 노랑이 수십 종) 통일성이 깨지는 것을 막는 것입니다.

`:root`에 아래 토큰 블록을 **그대로 선언**하고, 컴포넌트는 `var(--토큰)`으로 참조합니다.

```css
:root{
  /* ── 구조 토큰: 콘텐츠와 무관하게 고정. 값을 바꾸지 않는다 ───────── */
  /* 타이포 사다리 (--fs-sm 31px = 본문 기본) */
  --fs-2xs:24px; --fs-xs:28px; --fs-sm:31px; --fs-md:34px;
  --fs-lg:38px;  --fs-xl:42px; --fs-2xl:48px; --fs-hero:72px;
  /* z-index 레이어 */
  --z-bg:1; --z-scenery:5; --z-content:10; --z-character:12;
  --z-interactive:20; --z-speech:30; --z-hud:40; --z-effect:60;
  --z-drawer:70; --z-flash:90;
  /* 모서리 */
  --r-none:0; --r-sm:8px; --r-md:22px; --r-pill:999px; --r-circle:50%;
  /* 모션 */
  --ease:cubic-bezier(.2,.8,.2,1);        /* 표준 진입/전환 */
  --ease-out:cubic-bezier(.4,0,.8,.2);    /* 퇴장 */
  --ease-back:cubic-bezier(.2,.9,.3,1.18);/* 살짝 튕기는 등장 */
  --dur-fast:.15s; --dur:.45s; --dur-slow:.65s;
  /* 그림자 (고도 3단) */
  --shadow:0 18px 44px rgba(3,29,39,.36);
  --ds-sm:drop-shadow(0 6px 8px rgba(0,0,0,.25));
  --ds-md:drop-shadow(0 12px 16px rgba(0,0,0,.3));
  --ds-lg:drop-shadow(0 18px 26px rgba(0,0,0,.38));

  /* ── 팔레트 토큰: 이름·역할은 고정, 값은 콘텐츠 art_direction에서 채운다 ──
     아래 값은 예시(도서관 톤)일 뿐이다. 콘텐츠 분위기에 맞춰 값만 바꾼다. */
  --bg:#062c3c;           /* 배경 기저 */
  --surface:#0b5364;      /* 무대·판 표면 */
  --ink:#073547;          /* 어두운 잉크(스트로크 등) */
  --plate-ink:#173f49;    /* 대사판·티켓 위 텍스트 */
  --accent:#ffd75a;       /* 주강조 */
  --accent-bright:#ffe45f;/* 강한 글로우 하이라이트 */
  --glow:#ffe66c;         /* 글로우 */
  --cream:#fff6d7;        /* 밝은 표면 텍스트 */
  --danger:#e65043;       /* 오답/경고 — 역할 고정(오답 신호는 빨강 계열 유지) */
}
```

지키는 규칙:

- **참조만** — 색·font-size·radius·z-index·그림자·이징은 위 토큰만 `var()`로 씁니다. 컴포넌트에 새 raw 값을 만들지 않습니다.
- **수정은 토큰 값으로** — 크기·색을 조정할 때 개별 선택자를 고치지 말고 토큰 값을 바꿉니다(한 곳 수정 → 전역 일관).
- **확장은 named 토큰으로** — 사다리로 표현 안 되는 값이 정말 필요하면, raw 값을 박지 말고 `:root`에 `--fs-<이름>` 같은 **새 토큰을 추가하고 주석으로 용도를 남깁니다.**
- **한 화면만 예외** — 특정 scene만 달라야 하면 전역 토큰을 건드리지 말고 그 scope에서 재정의합니다: `.certificate{--fs-sm:36px}`.
- **팔레트 값은 art_direction에서** — `--bg`·`--accent`·`--plate-ink`·`--glow` 등의 값은 planner `art_direction`의 분위기·팔레트에서 가져옵니다. CSS 색을 임의의 hex로 새로 만들지 않습니다. 이렇게 하면 CSS 색과 생성된 asset 이미지 색이 같은 출처라 어긋나지 않습니다.
- 구조 토큰(타이포·z·radius·모션·그림자)은 콘텐츠와 무관하게 고정이며 값을 바꾸지 않습니다.

## channel 렌더링 계약

planner가 `elements[].channel`로 각 줄의 역할을 이미 구분해 두었습니다. channel마다 아래 표면으로 렌더하고, 임의로 다른 표면에 넣지 않습니다.

- `dialogue` — 캐릭터 발화입니다. **반드시 기존 speech_bubble asset을 배경으로 한 말풍선**으로 렌더하고 화자 머리 옆(head-height)에 붙입니다. plaque·board·monitor·인증서·책 지면 같은 표면 텍스트나 자막 카드로 넣지 않습니다.
  - 말풍선 컴포넌트를 새로 만들지 말고 이미 쓰고 있는 것을 재사용합니다. 한 콘텐츠 안에 서로 다른 말풍선이 섞이면 실패로 봅니다.
  - 한 section에 dialogue 줄이 여러 개면 한 번에 다 띄우지 말고 순차 beat로 전개합니다(자동 진행 + 탭 스킵, 마지막 beat에서 CTA 노출).
- `feedback` — 정오답 반응입니다. 세 층을 동시에 구현합니다.
  1. 캐릭터 표정/pose 전환 (정답=성공, 오답=고민)
  2. 캐릭터 옆 말풍선의 짧은 고정 대사 (dialogue와 같은 speech_bubble 재사용)
  3. 화면 중앙 도장/이펙트
  - **오답 pose는 말풍선이 사라지는 시점에 idle로 되돌립니다.** 이 복귀 타이머는 정답 처리 시 취소해 환호 pose를 덮어쓰지 않게 합니다.
  - 가변 길이 개념 설명은 말풍선이 아니라 별도 칩/카드로 분리합니다.

권장 어휘에 없는 새 channel이면 그 이름이 뜻하는 역할에 가장 가까운 위 계약을 따르고, 애매하면 표면 텍스트보다 장면 속 물건을 우선합니다.

## Visual QA scene contract

- Playwright design review가 화면별 screenshot을 안정적으로 찍을 수 있도록 모든 주요 화면/섹션 root에 `data-qa-scene`을 넣거나 유지합니다.
- `data-qa-scene` 값은 고정 enum이 아닙니다. 기존 값이 있으면 유지하고, 새 화면은 planner section id·화면 목적·step 이름에 맞는 안정적인 kebab/snake/camel case 문자열을 자유롭게 씁니다. 예: `intro`, `step1_intro`, `ticketMachineRepair`, `story-branch-1`.
- 화면 순서가 있으면 `data-qa-order="1"`처럼 숫자 순서를 넣습니다. 없으면 DOM 순서대로 캡처됩니다.
- 사람이 읽을 이름이 필요하면 `data-qa-label`을 넣습니다. 값은 한국어여도 됩니다.
- 첫 화면뿐 아니라 튜토리얼, 메인 활동, 스토리/정리, 완료 화면처럼 design review가 별도로 봐야 하는 화면은 모두 `data-qa-scene`을 가져야 합니다.
- `window.__contentHarnessShowScene = function(sceneId) { ... }`를 정의하거나 유지합니다. 전달받은 `data-qa-scene` 값의 화면만 보여 주고 나머지는 숨겨야 합니다.
- 이 contract는 사용자가 보는 UI가 아니라 QA hook입니다. 화면에 설명 문구로 노출하지 않습니다.

## 공통 금지

- 지정된 경로 외의 HTML 파일을 만들지 않습니다.
- planner에 없는 학습 내용이나 story board와 충돌하는 내용을 추가하지 않습니다.
- 기존 DOM id, event target, data attribute, 주요 JS 참조를 보존합니다. 요소를 옮길 때는 참조를 함께 갱신합니다.
