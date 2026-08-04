# 1-2/08 완료 항목 보관소

`todo.md`에서 완료된 항목을 잘라 옮긴 곳이다. 항목 번호는 `todo.md`에 있던 번호를 그대로 유지한다
(다른 항목과 `problem.md`가 번호로 참조한다). 과거 조치를 찾을 때는 `todo.md`와 이 파일을 **둘 다** 본다.

완료 날짜 순으로 뒤에 덧붙인다.

---

## 2026-07-31

## 1. header를 1-2/01 방식으로 수정

- 상태: 완료 (2026-07-31)
- 조치(1차, 시각 양식): 01 `topbar`의 CSS 값을 그대로 이식했다. `.topbar`(56px, 크림 유리 그라디언트 + 하단 보더) > `.topbar-left`(`.btn-home.course-menu-btn` 햄버거+목록 → `.header-voice-volume-button` 원형 스피커 SVG → `.step-label` 금색 세로 구분선) / 중앙 절대배치 `.lesson-header-title` + 금색 밑줄 / 우측 `.lesson-bar-reward`(track+fill+`%`). `sceneMeta`는 `title` → `stage`로 바꾸고 `progress`를 숫자로 통일했다. 제거: 08 자체 3단계 chip, `assets/global-hud-frame.png` 프레임(파일도 2026-07-31 삭제).
- 조치(2차, 코스 메뉴 — 2026-07-31 사용자 확정): 씬 이동 드로어(`#menuDrawer` + `unlockedMenuScenes` / `refreshMenuAccess` / `unlockMenuScene`)를 통째로 걷어내고 01의 `installCourseMenu` 드로어를 이식했다. 클래스명은 01 그대로 — `.course-menu-overlay` / `-panel` / `-head` / `-grade` / `-close` / `-list` / `-item` / `-no` / `-title` / `-now` / `-soon` / `-foot` / `-home`, 상태는 `.is-open` / `.is-current` / `.is-locked`. 데이터는 `lesson.json` 대신 index.html 내부 상수 **`COURSE_MENU`**. `path` / `id` 값은 01 `lesson.json`의 `ui.courseMenu` 원본 그대로다 — **1-2/01과 1-2/08은 디렉토리 깊이가 같아 `../../1-1/01/`·`../01/` 상대 경로가 그대로 맞는다.**
- 01의 CSS는 `clamp(..., cq*, ...)` 기반인데 08은 고정 캔버스라 container query를 안 쓴다. 1366에서 대부분 clamp 상한에 걸리므로 **상한값을 취해 × 1.4056** 했다(패널 400→562px, 항목 글자 18→25px, 번호 원 34→48px 등).
- 검증: headless Chrome 1920×1080에서 `#menuButton` 클릭 → 드로어 열림, 10개 항목 렌더, 8번 항목에 `지금` 태그 + `is-current` 강조, 5·7·9·10번 `is-locked` + `준비 중`, 닫기 버튼/배경 클릭으로 닫힘 확인. 런타임 오류 0.
- **주의 — 이 항목에 한때 "차시 목록 드로어는 08에서 하지 않는다(범위 제외)"는 메모가 있었다.** 2026-07-31 사용자 확인으로 뒤집혔고 위 구현을 유지하기로 확정했다. 되돌리려면 `COURSE_MENU` / `buildCourseMenu` / `.course-menu-*`를 제거하고 `#menuDrawer` + 씬 잠금 로직을 복원해야 한다.
- 나레이션 다시듣기(`#headerNarrationReplay`)는 08에 나레이션 오디오 자산이 없어 넣지 않았다. 08은 `speechSynthesis` TTS를 쓰므로 대응 기능이 필요하면 별도 항목으로 연다. 소리 버튼(`#soundButton`)과 진행률 바(`#lessonBar`)는 08 것을 유지했다.
- 차시 번호는 **`no:8`이 맞다**(2026-07-31 사용자 확정). 01의 원본이 1-2/01을 `no:6`으로 둔 것과는 규칙이 다르지만, 08은 8차시이므로 `no:8`로 간다.


## 2. 가장 첫 번째 페이지 삭제

- 상태: 완료 (2026-07-31)
- 확정: 삭제 대상은 `section_global_ui`(공통 UI + 활동 목표 3칸 overview). 사용자 확인 완료.
- 조치: `<section id="section_global_ui">` 블록과 `#section_global_ui`-스코프 CSS 7줄, `#goalButton{}` 규칙을 제거했다. `section_intro`가 `class="scene active"` + `data-qa-order="1"`이 되고 나머지 씬은 2~7로 재번호했다. `sceneMeta`에서 항목을 빼고 `section_intro.progress`를 12 → **4**로 내렸다(뒤 씬의 인라인 `setProgress()` 값은 그대로 두어도 단조 증가가 유지된다). `currentScene`·`exitButton` 폴백을 `section_intro`로 바꾸고, 부팅을 `updateHud(currentScene)` → **`showScene(currentScene)`** 으로 바꿔 첫 씬에서도 `resetIntro()`와 `title-mode`가 걸리게 했다.
- 검증: 7개 씬 전수 캡처, `.scene` 개수 7, `data-qa-order` 1~7 연속, 런타임 오류 0.
- **주의**: `assets/school-wall-wide.png`와 `assets/overview-mural-triptych-frame.png`는 참조가 없어져 **2026-07-31 삭제했다**(사용자 확정). `.hero-title` 기본 규칙은 `.title-banner .hero-title`이 아직 쓰므로 남겨 뒀다.


## 3. title을 CTA 이미지로 변경

- 상태: 완료 (2026-07-31)
- 해석 확정: (a) **타이틀 로고 에셋 교체**였다. (b) CTA 버튼의 이미지화가 아니다 — 그건 4번에서 CSS 버튼으로 이미 처리됐다.
- 조치: `assets/colorful-school-wall-title.png`를 01 `assets/ui/title-logo.png` 화풍으로 재생성했다. 금빛 그라데이션 + 두꺼운 갈색 외곽선/베벨 + 별 장식 + 2줄 구성까지 01과 같은 계열로 맞춰졌다. **파일명과 마크업(`#introTitleSurface` > `.intro-title-img`)은 그대로라 CSS·JS 변경은 없다.**
- 검증: 두 로고를 나란히 육안 비교 — 색감·외곽선 두께·베벨·별 장식이 같은 작가 결과물로 보인다. 이전 에셋의 "납작한 노랑" 문제 해소.
- **9번 오프셋 재계산 불필요.** 새 에셋 `1909×824`, 알파 bbox `(48, 100, 1848, 758)` — 이전 에셋의 y 범위(100~758 / 824)와 **동일**하다.


## 4. title "시작하기" 버튼을 1-2/01 방식으로 변경

- 상태: 완료 (2026-07-31)
- 조치: 01의 타이틀 화면을 통째로 이식했다. `#introStartWrap` > `.intro-title-copy` > `.intro-title-img` + `#introStart` 구조, `titleLogoDrop` / `ctapulse` / `shimmer` 애니메이션, `title-mode`(타이틀 화면에서 topbar 숨김)까지 01과 같은 이름으로 가져왔다.
- **주의 — 01의 CSS는 소스 순서로 읽으면 틀린다.** `#introStartWrap .intro-start-cta`(네이비 테두리 + 금색)는 뒤쪽 `#app .cta,#app #introStartWrap .intro-start-cta`(명시도가 더 높음)에 덮여 죽은 규칙이다. 실제 적용값은 `getComputedStyle`로 읽어야 한다. 실측값(1366 기준):
  - `547.19 × 63.86`, `min-height:58px`, `padding:13px 34px 15px`, `border:2px solid rgba(161,98,7,.52)`, `border-radius:999px`
  - 배경 `linear-gradient(180deg,#fef08a,#facc15 36%,#eab308 72%,#ca8a04)` + 흰 광택 레이어
  - 글자 `Jua` 27px/31.86 900, 색 `#713f12`
  - `box-shadow: inset 0 3px 0 rgba(255,255,255,.56), inset 0 -4px 0 rgba(120,53,15,.12), 0 4px 0 rgba(120,53,15,.28), 0 8px 22px rgba(66,32,6,.18)`
  - 08에는 위 값을 × 1.4056 (= 1920/1366) 해서 넣었다.
- **01의 서체는 Noto Sans KR이 아니라 `Jua`다.** 13번째 줄 `<style>`의 `font-family:"Noto Sans KR"...`를 15번째 줄 `html,body,button,...{font-family:"Jua",...}`가 덮는다.
- 2026-07-31 결정: **01처럼 전역 적용.** `--font-body`를 `"Jua","Noto Sans KR","Apple SD Gothic Neo",sans-serif`로 바꾸고, `--font-topbar`/`--font-title`은 `var(--font-body)` 별칭으로 정리했다. `button,input,textarea,select{font:inherit}`로 폼 요소까지 01과 동일하게 상속시켰다.
- **미검증 — 이 개발 PC에서는 Jua 렌더를 확인할 수 없다.** headless Chromium이 `fonts.googleapis.com`에 `net::ERR_SSL_PROTOCOL_ERROR`로 실패한다(TLS 가로채기 프록시 미신뢰. curl은 200). **1-2/01도 같은 이유로 이 PC에서는 폴백으로 렌더된다** — 08만의 문제가 아니라 환경 문제다. 실제 브라우저에서 육안 확인이 필요하다.
- 후속 후보: 오프라인 보장이 필요하면 Jua를 `assets/fonts/`에 self-host하고 `@font-face`로 건다(01은 안 하고 있어 지금은 01과 동일하게 CDN 의존).


## 5. 화면 전환 애니메이션 추가

- 상태: 완료 (2026-07-31)
- **이 항목의 "전환 효과가 없다"는 서술은 틀렸다.** 08에는 이미 `.scene.active` / `.scene.leaving` + `sceneIn` / `sceneOut` 키프레임과 `SCENE_OUT_MS` / `SCENE_OVERLAP_MS` 겹침 타이밍이 있었다. 문제는 "없음"이 아니라 **01과 값·이름이 달랐다는 것**(08: out .26s + `translateX(0→-28px)`, in .42s + `translateX(36px→0)`).
- 조치: 01의 이름·값으로 맞췄다. `stageFadeIn` / `stageFadeOut`(순수 opacity, in `.45s` / out `.42s`, easing `ease`)을 기본으로 하고, 01의 `#app[data-transition="slide"]`에 대응하는 **`#stage[data-transition="slide"]`** 옵트인으로 `stageSlideOutRight`(`translateX(0→100%)`) / `stageSlideInRight`(`translateX(-100%→0)`)를 추가했다. `--dur-scene-out` `.26s→.42s`, `--dur-scene-in` `.42s→.45s`, JS `SCENE_OUT_MS` `260→420`.
- 08은 정적 씬 구조라 01처럼 `#app`이 아니라 `.scene`에 건다. 키프레임 이름과 지속시간은 01과 같게 뒀다(나중에 같은 이름으로 검색되도록).
- 검증: 7개 씬 전수 전환 캡처, 런타임 오류 0.


## 6. 말풍선을 1-2/01과 동일하게 변경

- 상태: 완료 (2026-07-31)
- 조치: 배경 이미지(`school-speech-bubble-body.png`, 990×190 고정)를 걷어내고 CSS 말풍선으로 교체했다. 값은 01 `.speech`를 `getComputedStyle`로 실측한 뒤 × 1.4056: 배경 `#fffdf6`, 테두리 `6px solid #4c3428`, `border-radius:28px`, `box-shadow:0 10px 0 rgba(0,0,0,.18)`, 글자 `--fs-xs`(28px) / **weight 400** / line-height 1.4 / `#221914`, `word-break:keep-all` + `text-wrap:balance`. 꼬리는 01과 같은 2겹(`::before`=테두리색 17px, `::after`=배경색 14px)이고 `left-speaker` / `right-speaker`로 좌우를 미러링했다. 등장은 `speechPop`(`cubic-bezier(.36,.07,.19,.97)`) — 01의 키프레임 그대로.
- 토큰 `--bubble-bg` / `--bubble-line` / `--bubble-ink` / `--ease-speech-pop`을 추가했다(디자인 토큰 계약대로 raw hex를 흩뿌리지 않음).
- **주의 — 함께 지워야 했던 것**: `#shapeSpeech` / `#arithSpeech` / `#drawingSpeech`에 걸려 있던 비대칭 패딩(`28px 83px 66px 61px` 등)은 **배경 이미지 아트에 맞춘 보정값**이었다. CSS 말풍선에서는 그대로 두면 한 줄짜리 대사가 145px 높이로 렌더된다. 전부 제거했다(`#arithSpeech`의 `top:350px`만 남김).
- **01의 weight는 900이 아니라 400이다** — `#app .speech{text-align:left;font-weight:400}`가 뒤에서 덮는다. 이 항목 초안에 적혀 있던 `font-weight:900`은 소스 순서 오독이다.
- 검증: 7개 씬 캡처에서 좌/우 화자 꼬리 방향, 대사 길이에 따른 높이 자동 조정, 넘침 없음 확인. `school-speech-bubble-body.png` 참조 0개(preload 링크도 제거). **파일은 2026-07-31 삭제했다.**


## 7. "수리가 필요해요 1"의 모양 찾기 대폭 변경

- 상태: 완료 (2026-07-31)
- 사용자 결정: **교실 배경 + 개별 사물 에셋**.
- 조치: 배경을 `school-yard-shape-search.png`(학교 마당, 도형이 그림에 굳어 있음) → 신규 `classroom-shape-search.png`(교실)로 바꾸고, 찾을 도형 사물 6종을 **투명 PNG 개별 에셋**으로 얹었다. `hotspotDefs`(픽셀 하드코딩 6개)를 없애고 **`findObjects`** 테이블 하나로 통합했다 — `{src, alt, rect:[left,top,w,h]}`이고 `hotspotDefs`는 여기서 파생시킨다(`Object.fromEntries`). 이미지는 `renderFindObjects()`가 `#shapeObjects` 레이어에 그리며 `.find-object{pointer-events:none}`이라 클릭은 기존 `.hotspot` 버튼이 받는다. **이제 좌표 한 줄만 고치면 위치·난이도가 바뀐다.**
- 6종 / hotspot id: 원 `circle_wall_clock`(벽시계) · `circle_ball`(공) / 삼각 `triangle_ruler`(삼각자) · `triangle_pennant`(삼각 깃발) / 사각 `square_window`(창문) · `square_locker`(사물함). `searchQuestions`의 `answers`도 새 id로 교체했다.
- 배경 실측: 칠판은 stage `x 80~763 / y 241~660`, 화분은 `x 1722~1894`. 사물은 그 사이 벽면과 바닥에만 배치했다. **`.search-prompt`의 `top`을 160px → 90px로 올렸다** — 안 올리면 문제 배너가 시계·창문을 덮는다.
- 에셋 생성: codex `exec`를 asset 1장당 1프로세스로 병렬 실행. 프롬프트에는 `dfbc1027_planner.json`의 `art_direction` 전문 + 기존 08 에셋 2~3장의 절대경로(실제로 열어 대조하라는 지시) + `asset_generator_system.md`의 텍스트/투명/component 정책을 인라인했다.
- **주의 — 초판 3장을 폐기하고 재생성했다.** (a) 배경이 가구 없는 빈 방이라 교실로 안 읽혔다(프롬프트의 "비워 두라" 제약이 과했음) → 칠판·책상·형광등을 넣되 찾기 대상 6종과 **창문은 배경에 절대 금지**로 다시 지시. (b) 벽시계에 바늘이 없어 시계로 안 보였다 — 이 씬은 시각을 묻지 않으므로 바늘은 `component_rules`의 가변부가 아니다. (c) 사물함이 창문과 똑같은 파랑/하늘색이라 구별이 안 됐다 → 원목 갈색으로 재지시.
- 검증: 6개 사물 + 배너의 상호 겹침 0(경계 상자 전수 대조), 찾기 3문항 정답 클릭 → 세기 단계 진입까지 통과, 런타임 오류 0.
- **주의**: `school-yard-shape-search.png`는 참조가 없어져 **2026-07-31 삭제했다**.


## 8. 동그라미·세모·네모 에셋 배경 투명 처리

- 상태: 완료 (2026-07-31)
- **이 항목의 현황 서술은 틀렸다.** "도형은 에셋이 아니라 CSS로 그려져 있다"가 아니라, `assets/shape-tile-body.png`(1536×1024 RGBA, 3프레임 스프라이트, 알파 bbox `40,261~1490,730`)를 `background-size:300% 100%`로 잘라 쓰는 구조였고 **에셋 알파는 이미 정상**이었다(네 모서리 alpha=0 실측).
- 실제 문제(사용자 지적): **도형 채우기가 도형 바깥까지 새어 배경 사각형까지 칠해졌다.** 원인은 `background-color` + `background-blend-mode:multiply` 조합이다 — `background-color`는 padding-box 전체를 칠하고 blend는 그 위에서 이미지와 섞을 뿐이라, **이미지 알파가 0인 영역에는 섞을 대상이 없어 배경색이 그대로 남는다.** 스프라이트 세로 알파 점유율이 46%뿐이라 `height:150px` 요소에서 위아래로 각 ~38px씩 색 띠가 생겼다.
- 조치: 색칠을 `.paint-shape::before`로 옮기고 같은 스프라이트를 `mask-image`(`mask-size:300% 100%` + 도형별 `mask-position`)로 걸어 실루엣 밖을 잘라냈다. `filter`(그림자·글로우)는 요소에 남겨 마스크된 결과 위에 적용되게 했다. `.drawn-shape`에서 중복으로 깔던 `background-image`는 제거했다(항상 `.paint-shape`와 같이 붙으므로 `::before`가 담당).
- 함께 고친 것: `.paint-shape`에 `aspect-ratio:1;justify-self:center`를 넣어 **그리드 칸에 눌려 타원·직사각형으로 보이던 왜곡**을 없앴다(도형 차시에서 동그라미가 타원으로 보이는 문제). `.random-progress`(112×92→96×96)·`.drawing-summary`(118×108→112×112)도 정사각으로 맞췄다.
- 검증: 수정 전/후를 같은 페이지에서 렌더해 요소 모서리 픽셀 비교 — 수정 전 `triangle red` 네 모서리가 모두 틴트색 `(230,80,67)`, 수정 후 모두 페이지 배경 `(255,255,255)`. 도형 중심 색은 동일 유지. 7번에서 만든 사물 에셋 10장도 모서리 alpha=0 / fringe <1% 실측.
- 7번의 신규 도형 사물 에셋은 전부 투명 PNG로 생성됐다(원래 이 항목의 요구사항).


## 9. 도입 타이틀 이미지가 담장을 가리지 않도록 위로 이동

- 상태: 완료 (2026-07-31)
- 대상: `section_intro`의 `#introStartWrap` (타이틀 `#introTitleSurface` + `#introStart` 시작 버튼 컬럼)
- 배경 측정: `school-wall-damaged.png`(1672x941, cover 배율 1.148)의 담장 기둥 윗면이 stage 좌표 **y≈550**. 타이틀 에셋은 알파 bbox가 y 100~758/824라, 폭 1068px로 그리면 높이 461px 중 실제 그림은 박스 상단 **+56 ~ +424** 구간에만 있다.
- 조치: **`#section_intro #introStartWrap{translate:0 calc(-50% - 140px)}`** 로 140px 올려 그림이 y **165~533**, 담장 윗면 바로 위 하늘에 놓이게 했다. 01 규칙(`#introStartWrap{top:50%;translate:0 -50%}`)은 건드리지 않고 씬 스코프 오버라이드만 추가했다(명시도 id 2개 > id 1개라 `!important` 불필요).
- 검증: headless Chrome 1920x1080 캡처에서 담장 전체·무너진 구간·벽돌 더미·콘·바리케이드가 모두 드러나고 타이틀이 상단 헤더와 겹치지 않음을 확인.
- ~~주의: 3번에서 로고 에셋이 바뀌면 140px 오프셋을 다시 계산해야 한다.~~ → 3번 완료 시 재측정 결과 알파 bbox가 동일해 재계산 불필요. 로고를 또 바꾸면 이 확인은 다시 해야 한다.


## 10. 디버그 패널 (` 키) — 씬 자유 이동

- 상태: 완료 (2026-07-31)
- 요청: `` ` `` 를 누르면 우측에 디버그 모드가 나타나고, 거기서 각 씬으로 마음대로 이동할 수 있게 한다.
- 조치:
  - 패널을 `#stage` **밖**(`<body>` 직속, `position:fixed`)에 두었다. `#stage`는 `resizeStage()`에서 `scale()` + 세로 화면 `rotate(90deg)`가 걸리므로 안에 넣으면 패널도 같이 축소·회전된다.
  - 씬 목록은 하드코딩하지 않고 `.scene`의 `data-qa-order` / `data-qa-label`에서 생성한다(`buildDebugScenes`). 씬이 늘거나 순서가 바뀌면 자동 반영된다(2번의 씬 삭제도 자동 반영됐다).
  - 이동은 기존 `showScene(id)`를 그대로 쓴다. 씬별 `reset*()` 초기화가 `showScene` 안에 있어 어느 씬으로 건너뛰어도 상태가 깨지지 않는다.
  - 현재 씬은 초록 테두리로 표시하고 `showScene` 끝에서 `syncDebugPanel()`로 갱신한다. `Esc`로도 닫히고, `<input>` / `<textarea>` 포커스 중에는 토글하지 않으며 `Alt` / `Meta` 조합은 제외했다.
- **주의(2026-07-31 갱신)**: 원래 있던 "점프 시 `unlockedMenuScenes` 전부 해제" 로직은 1번에서 씬 이동 드로어를 차시 목록 드로어로 바꾸면서 **함께 제거**됐다(씬 잠금 개념 자체가 사라짐).
- 남은 결정: 지금은 **항상 활성**이다. `production/`은 학생에게 나가는 산출물이므로 `?debug=1` 같은 플래그 게이팅을 걸지 결정 필요.


## 11. section_intro — 담장 수리 망치 모션 + 수리 애니메이션

- 상태: 완료 (2026-07-31)
- 사용자 결정: **떠 있는 망치 아이콘**(작업자가 드는 캐릭터 컷 아님).
- 조치: 대사 0(무너진 담장) → 대사 1(수리 완료) 사이에 연출을 끼웠다. `introTap` 핸들러가 `introBeat===0`에서 `startIntroRepair()`를 부르고, 4회 타격(`HAMMER_SWING_MS=420` × `HAMMER_STRIKES=4`)마다 임팩트 스파크(`.repair-impact.hit`)와 정답음이 나면서 `#introBgRepaired` 오버레이 opacity를 `.25 → .5 → .75 → 1`로 올린다. 끝나면 `finishIntroRepair()`가 `introBeat=1`로 넘기고 오버레이를 0으로 되돌린다(이때 `#introBg`가 이미 repaired라 이음새가 없다).
- 에셋: `assets/repair-hammer.png`(1254×1254 투명 PNG, 손잡이 우상단·머리 좌하단 대각선, 손·팔·효과선 없음). codex 이미지 생성으로 제작.
- **주의 — damaged / repaired 두 배경은 담장 텍스처가 전체적으로 미묘하게 다르다**(diff 실측: 임계 120에서 `x 44~1832 / y 576~980` 전 구간). 그래서 `clip-path` 부분 와이프는 이음새가 보인다 → **전체 크로스페이드**로 갔다.
- 붕괴 구간 실측: `school-wall-damaged.png` 크롭 스캔으로 stage `x 1160~1550 / y 620~792`(벽돌 더미 포함). 망치는 `left:1250px;top:485px;width:300px`, `transform-origin:90% 12%`(손잡이 끝)이고 타격 포즈에서 머리가 `(1300, 655)`에 닿는다. 스파크는 그 지점에 맞춰 `left:1240px;top:595px`.
- **주의 — 회전 방향을 두 번 틀렸다.** 이 에셋은 손잡이가 우상단이라 `transform-origin`을 손잡이 끝에 두면 **양수 회전이 머리를 들어올린다.** 처음에 `rotate(-40deg)`를 "들어올린 포즈"로 잡았다가 머리가 오히려 내려갔다. 최종: `0%/100% rotate(50deg)`(들어올림) → `42% rotate(8deg)`(타격) → `56% rotate(16deg)`(반동).
- **연출 중 탭은 무시한다 — 끝까지 보게 한다**(2026-07-31 사용자 확정). `introRepairing`이 true인 동안 `introTap` 핸들러가 즉시 return한다.
- 마지막 타격 뒤 망치 레이어를 먼저 감추고, 고쳐진 담장을 **`HAMMER_HOLD_MS=1000`** 동안 그대로 보여 준 다음 대사 1로 넘어간다. 총 소요 = 타격 1.86s + 유지 1.0s.
- 검증: 들어올림/중간/타격 3포즈를 애니메이션 일시정지로 캡처해 머리가 붕괴 구간에 닿는지 확인. 연출 중 탭해도 대사가 안 넘어가고, 대사 1 도달까지 **2.90초**(기대 2.86초) 걸리며 유지 구간에는 망치가 숨겨져 있음을 실측. 런타임 오류 0.
- 5번(화면 전환)과 별개다. 이건 씬 **내부** 연출이다.


## 12. section_arithmetic_tutorial 입력기를 1-2/01 방식으로 변경

- 상태: 완료 (2026-07-31)
- 범위: **08의 모든 키패드**(`#countKeypad`, `#arithKeypad`, `#randomKeypad`). 셋 다 공통 `buildKeypad(id, handler)`를 쓰므로 한 번에 교체했다.
- 조치: 01 `.repair-count-key` 실측값(1366)을 × 1.4056 해서 `.key`에 넣었다 — `border:3px solid rgba(180,218,255,.95)`, `border-radius:17px`, `background:rgba(255,255,255,.92)`, `color:#12355f`, `font-weight:800`, `box-shadow:0 4px 0 rgba(143,173,211,.76), 0 11px 22px rgba(0,0,0,.15)`, 그리드 `gap:17px`. 지우기(`.key.del`)와 확인(`.key.enter`)도 01의 색 체계(`#e7c197`/`#a75f28`, `#e23b3b`/흰색) 그대로.
- **키 배치를 01의 `keypadControlsHtml`과 같게 바꿨다** — 1~9 다음 줄이 **`[←] [0] [확인]`**. 08에는 지우기 키가 아예 없어서 오입력하면 확인을 눌러 오답 처리되기를 기다려야 했다(problem.md `[content-refine-learning-flow-integrity]`에서 반복 지적된 "키패드 삭제" 결함과 같은 것). `.key.zero{grid-column:2}` 규칙은 마지막 줄이 꽉 차면서 필요 없어져 제거했다.
- 상호작용 이식: `keypadPress()`(pointerdown에 `.keypad-pressing` 부착, pointerup/leave/cancel에 해제) + `.key.keypad-pressing:not(:disabled){transform:translateY(4px) scale(.98);box-shadow:0 1px 0 #020810}`, `keypadDisplayTick()` + `@keyframes keypadDisplayTick{0%{transform:scale(.94);filter:brightness(1.85)}100%{...}}` — 둘 다 01의 이름·값 그대로. 세 핸들러(`countKeypad` / `arithKeypad` / `judgeRandomKey`)에 `del` 분기와 입력 시 tick 호출을 넣었다.
- `#randomInput`의 `wall-choice-plaque-body.png` 4겹 배경은 `gap:0`을 전제로 한 행 배경 흉내였다. 01 크롬을 쓰면 겹쳐 보여서 껐다(`#randomInput .keypad{gap:17px}`, `#randomInput .key{height:78px}`만 남김).
- **키 높이만 08의 78px을 유지했다.** 01은 `clamp(24px, 5.2cqh, 50px)`라 실측 33px이고, 그대로 × 1.4056 하면 46px로 오히려 작아진다(1학년 타깃에 부적합, problem.md `[content-scale-too-small]` 위험).
- 검증: `#randomKeypad` 키 12개(`1..9 ← 0 확인`), 숫자 2개 입력 후 `←` 클릭 시 `'72' → '7'` 확인, 캡처로 크롬 렌더 확인. 런타임 오류 0.
- 확인 키 글자는 **`확인`**(2026-07-31 사용자 확정). 원래 08은 `O`였는데 `0`과 혼동된다. `확인`은 planner에 없는 새 화면 문구지만 **입력기 컨트롤 라벨이라 학습 원문이 아니고**, 01이 이미 같은 문구를 쓰므로 원문 보존 계약의 대상이 아니라고 판단했다. 실측: 키 159×78px에 글자 57px(31px `--fs-sm`)로 넘침 없음.


## 13. section_random_problems — 문제 전에 도형 생성·감소 과정을 먼저 보여주기

- 상태: 완료 (2026-07-31)
- 조치: `#randomShapes` 레이어(`.work-area`)와 `#randomShapeSkip` 탭 층을 추가하고, `renderRandom`의 키패드 분기에서 문제 노출을 `revealQuestion` 클로저로 감싸 **도형 연출이 끝난 뒤에 식·입력기를 내보내게** 했다. 연출 중에는 `#section_random_problems.shape-intro`로 `#randomPanel`을 `visibility:hidden` 처리한다.
- 도형 개수는 무작위 생성기가 만든 수를 따른다(고정 3개가 아니다). `shapeStepsFor(type)`가 `randomBundle`에서 스크립트를 만든다 — type1 `10 - c`(10개 등장 후 c개 제거), type2 `a + b`, type3 `a + b + c`, type4 `a - b`, type5 `a - b - c`. **type 0은 보기 선택 문제라 대상이 아니다.**
- 표현은 `section_arithmetic_tutorial`의 `interaction_shape_add_remove`와 같은 것을 쓴다 — `.paint-shape`에 `pending`(미등장) / `removed`(소멸) 클래스를 스태거로 토글. 개당 `RANDOM_SHAPE_STAGGER_MS=120`, 단계 사이 `RANDOM_SHAPE_STEP_GAP_MS=420`.
- 재생 빈도: **매 문제마다 재생한다**(2026-07-31 사용자 확정). 초안의 `RANDOM_SHAPE_INTRO_COUNT` 게이팅은 제거했다. 재생 중 탭하면 건너뛸 수 있다(`#randomShapeSkip` → `finishRandomShapeIntro`) — 11번과 달리 여기는 문제마다 반복되므로 스킵을 남겼다.
- 검증: 3문제를 실제로 풀어 진행하며 **매 문제 연출이 재생**되고 도형 수가 생성된 수와 일치함을 확인(`10 - 8`→10개, `15 - 5`→15개, `15 - 5 - 8`→15개). 런타임 오류 0.
- 8번의 마스크·비율 수정이 여기 도형에도 그대로 적용된다(색이 새지 않고 정사각 비율).


## 14. 수리 이야기 표지판을 에셋으로 변경

- 상태: 완료 (2026-07-31)
- 사용자 결정: **픽토그램 + 글자 모두 이미지에 굽기.**
- 조치: 스프라이트 1장(`road-sign-body.png`, 가로 710px를 `overflow:hidden` + `left:0/-237px/-474px`로 잘라 씀)을 도형별 개별 에셋 3장으로 분리했다 — `road-sign-circle.png`(파란 원형 + 흰 자동차 픽토그램 + `자동차 전용도로`), `road-sign-square.png`(파란 사각 + `P` + `주차`), `road-sign-triangle.png`(노란 삼각 + 빨간 테두리 + 인부 픽토그램 + `공사`). 모두 1024×1024 투명 PNG, 기둥 포함, 기둥 높이·두께 통일.
- CSS: `overflow:hidden`과 픽셀 오프셋 3줄을 제거하고 `.sign img{position:absolute;left:50%;top:0;height:100%;width:auto;transform:translateX(-50%)}`로 바꿨다. **`object-fit:fill` + `width:710px` 강제가 사라져 원본 비율이 눌리지 않는다.** `.sign-label`과 `.sign.circle .sign-label` 보정 규칙도 제거했다(문구가 이미지에 있음).
- 문구는 planner 원문 그대로(`자동차 전용도로` / `주차` / `공사`) 이미지에 통합해 그렸다. `asset_generator_system.md`의 판단 기준("변하느냐 고정이냐")상 이 셋은 고정 문구라 굽는 것이 맞다.
- 검증: 세 표지판 렌더 크기 413×413 동일, 비율 왜곡 없음, 문구 오탈자 없음(육안), 도로 배경 위 배치 확인.
- **주의**: `road-sign-body.png`는 참조가 없어져 **2026-07-31 삭제했다**.


## 15. 말풍선 크기 자동 조정 + 01의 공통 UI(음소거·다음 버튼) 이식

- 상태: 완료 (2026-07-31)
- **음소거 버튼은 이식 대상이 아니었다.** 08 topbar에 이미 01과 같은 `.header-voice-volume-button`(`#soundButton`, `.volume-speaker` / `.volume-wave-1` / `.volume-wave-2` SVG까지 동일)이 있다. 중복 배치하지 않았다.
- 사용자 결정: 가져올 "다음 버튼"은 **01의 `.repair-narr-next`**(말풍선 안 `다음 ▸`)다. 씬 전환용 `#nextStepBtn`이 아니다.
- 조치(자동 크기): `.speech`의 `width:990px` → **`width:max-content` + `max-width:990px`**, 높이는 auto. `#arithContext`의 `min-width:780px`·`min-height:120px`와 `.feedback-speech`의 `min-height:140px`를 제거했다 — 남긴 씬별 값은 앵커 좌표(`left`/`right`/`top`)뿐이다.
- 조치(다음 버튼): 01의 `.repair-bubble-nav` + `.repair-narr-next` + `@keyframes repairNarrNextPulse`를 **클래스명·구조·애니메이션 이름 그대로** 옮겼다. 진행 신호였던 `.dialogue-advance`(깜빡이는 점)는 전부 이 버튼으로 대체했고 CSS 규칙도 지웠다(`#shapeSpeech`·`#arithSpeech`·`#drawingSpeech`·`#introSpeech`·`#feedbackSpeech`·`#helpCard`·`#storyCard`). 상수 `ADVANCE_NAV_HTML` 하나와 `ensureAdvanceNav(el)`가 담당한다.
- **01의 값은 px로 환산하지 않는다.** 01이 `cqw`/`cqh`(컨테이너 단위)로 적혀 있고 08의 `#stage`도 `container-type:size`라 **선언을 그대로 옮기면 1366→1920 환산(×1.4056)이 자동으로 일어난다.** 실측으로 확인: `font-size:1.5cqw`가 01에서 20.48px, 08에서 28.8px.
- 01의 `.repair-narr-replay`(나레이션 다시듣기)는 08에 오디오 자산이 없어 제외했다.
- 검증: 7개 씬 전수 캡처 + 실제 클릭 흐름. 대사 길이가 다른 말풍선이 각각 다른 폭으로 렌더되고 넘침 0, `stage` 밖으로 나가는 요소 0, 런타임 오류 0.
- **주의**: 씬별 폭·패딩 보정을 다시 넣으면 자동 조정이 깨진다. 6번에서 한 번 겪은 것과 같은 함정이다.


## 16. 대사·글자 크기 전반 확대

- 상태: 완료 (2026-07-31)
- 조치: `:root`의 `--fs-*` 사다리 전체를 ×1.2로 올렸다. `2xs 24→29 · xs 28→34 · sm 31→37 · md 34→41 · lg 38→46 · xl 42→50 · 2xl 48→57 · hero 72→86`. 개별 선택자에 px를 흩뿌리지 않았다.
- **함께 고쳐야 했던 것**: 글자를 키우자 폭 510px인 `.keypad-wrap` 안 프롬프트가 단어 중간에서 끊겼다("7개에서 3개를 더 색 / 칠하면"). `.prompt`에 `word-break:keep-all` + `text-wrap:balance`를 넣고 `.keypad-wrap .prompt`만 사다리에서 한 단계 낮춰(`--fs-md`) 잡았다. 개별 px가 아니라 사다리 안에서 고른 것이다.
- 15번을 먼저 넣은 뒤 진행했다. 고정 폭 말풍선인 채로 글자를 키웠다면 전부 넘쳤다.
- 검증: 7개 씬 전수 캡처 + 상호작용 흐름 캡처에서 줄바꿈·넘침 확인. `scrollWidth > clientWidth` / `scrollHeight > clientHeight` 요소 0(닫힌 드로어 제외), stage 밖 요소 0.


## 17. 모양 찾기 — ■ 2개를 찾아도 다음 모양으로 진행되지 않음

- 상태: 완료 (2026-07-31)
- **가설이 틀렸다. 메커니즘은 살아 있었다.** Playwright 실제 클릭으로 재현한 결과 `#feedbackSpeech`는 렌더되고(`display:block`, `opacity:1`), `pointer-events:auto`이며, 중심점의 `elementFromPoint`가 자기 자신이라 **덮이지도 않았고**, 클릭하면 `completeFeedback → advanceSearch`가 정상으로 돌아 ●문항으로 넘어갔다.
- **진짜 원인은 어포던스다.** 이 말풍선만 (a) `left-speaker`/`right-speaker` 클래스가 없어 꼬리가 없고 (b) 다른 대사 말풍선에 다 붙어 있던 진행 표시(`.dialogue-advance`)도 없었다. 화자를 덮은 채 글상자로 떠 있어 "눌러야 넘어간다"는 신호가 0이었다.
- 조치: 15번에서 이식한 `.repair-narr-next`("다음 ▸")를 `showFeedback`의 말풍선에도 붙이고(`ensureAdvanceNav`), `left-speaker` 꼬리를 줬으며, 앵커를 `left:380px` → **`left:500px`**로 옮겨 피드백 캐릭터(x 80~440)를 덮지 않게 했다. 키보드 진행(`Enter`/`Space`)도 추가했다.
- **`#feedbackSpeech`를 `<button>`에서 `<div role="button" tabindex="0">`로 바꿨다.** `<button>` 안에 01의 `<button class="repair-narr-next">`를 넣을 수 없다(중첩 버튼은 브라우저가 DOM을 재배치한다). 다른 말풍선과 같은 구조가 됐다.
- 자동 전환을 되살리지 않았다 — `[content-flow-state-scaffolding-regression]`의 과거 조치를 되돌리지 않고, 사람이 볼 수 있는 표면 하나를 확실히 만드는 쪽으로 풀었다.
- 검증: 실제 클릭으로 ■ 2개 → `다음 ▸` 노출 확인 → 클릭 → `■모양 2개를…` → `●모양 2개를…` 전환 확인. ●·▲까지 이어서 세기 단계 진입까지 통과. 런타임 오류 0.


## 18. 모양 찾기 — 사물의 종류·위치를 개연성 있게 재배치 + 학생 상시 배치

- 상태: 완료 (2026-07-31)
- 사용자 결정: 네모 대상 2개를 **공책 + 도시락**으로 교체(창문·사물함 둘 다 폐기).
- 배경 실측(`classroom-shape-search.png`를 1920×1080 cover로 매핑해 스캔): 칠판 `x 80~768 / y 240~660`, 벽·바닥 경계 `y≈818`, 화분 `x 1720~1900 / y 570~850`, 책상 상판 `y 900~975`(왼쪽 `x 0~390` · 가운데 `x 528~1065` · 오른쪽 `x 1240~1680` · 끝 `x 1710~1920`).
- 조치(`findObjects` 좌표): 삼각자 `[830,240]`→**`[500,395,210,210]` 칠판 면 위**, 벽시계 `[1130,215]`→**`[880,215,190,190]` 교실 가운데 상단 벽**, 삼각깃발 `[1180,470]`→`[1490,220,180,180]`(벽에 걸린 위치), 공은 `[470,690,180,180]` **그대로 유지**(사용자 지시).
- 조치(교체): `square_window`/`square_locker` → **`square_notebook`(`classroom-notebook.png`, 책상 가운데 `[860,790,185,185]`) · `square_lunchbox`(`classroom-lunchbox.png`, 책상 오른쪽 `[1480,790,185,185]`)**. `searchQuestions[0].answers`도 새 id로 교체했다.
- 조치(학생): `#shapeSceneStudent`(`.classroom-student`, `student-idle.png`)를 칠판 오른쪽 빈 면 `left:1080px;bottom:-12px;340×560`에 상시 배치했다. **찾기 대상이 아니므로 핫스팟도 alt도 주지 않고** `z-index:var(--z-scenery)`로 찾기 사물보다 뒤에 둔다. `startPaintIntro`에서 배경이 담장으로 바뀔 때 함께 내린다.
- 에셋 생성: codex `exec`를 asset 1장당 1프로세스로 병렬 실행(7번과 같은 방식). 프롬프트에 `1-2/01/lesson.json`의 `artDirection` 전문 + `dfbc1027_planner.json`의 `art_direction` 전문 + 형제 에셋 3장(공·삼각자·벽시계)과 교실 배경의 절대경로(**실제로 열어 대조하라는 지시**)를 인라인했다. 둘 다 1254×1254 RGBA, 네 모서리 alpha=0, 이미지 내 글자 0.
- 검증: 6개 사물 + 배너 + 학생의 경계 상자 전수 대조 → **겹침 0**. ■/●/▲ 3문항을 실제 클릭으로 통과.
- **주의**: `classroom-window.png` / `classroom-locker.png`는 참조가 없어졌다(삭제 여부 미확정 — todo.md 확인 항목 참조).


## 19·21. 산술 튜토리얼 — 대사와 화면 상태 불일치

- 상태: 완료 (2026-07-31)
- 두 항목은 같은 씬의 같은 원인(`[narration-visual-mismatch]`)이라 함께 처리했다. **원문 대사는 한 글자도 바꾸지 않고 화면을 대사에 맞췄다.**
- 19 조치: `startArithmeticQuestion`의 도형 생성이 `i%3`으로 원/삼각/사각 × 초록/빨강/파랑을 돌리고 있었다. 대사가 `초록색부터 알려드릴게요`까지만 색을 소개하고 이후 어떤 대사도 다른 색을 소개하지 않으므로 **이 씬 전체를 `circle green` 하나로 통일**했다. 앞 씬 `#paintIntroVisual`이 세운 `초록=●` 매핑도 함께 지켜진다.
- 21 조치: `#arithPaintCans`(`.paint-can-row`) 컨테이너를 만들고 통을 `#arithPaintCan1` / `#arithPaintCan2`로 나눴다. `q_add_10_2`의 preBeats에 `cans` 필드를 달아 `페인트 1통을 다 썼어요` → **`first-empty`**(1통이 `.empty` — 회색조·기울임·반투명), `1통을 더 준비했어요.` → **`two`**(2통째 `pop` 등장)로 바뀐다. `setPaintCans(state)`가 상태를 적용하고 `resetArithmetic`이 `'one'`으로 되돌린다.
- 검증: 실제 클릭으로 해당 beat까지 진행해 `can1.empty=true` / `can2.hidden=false` 실측 + 캡처. 도형이 전 문항 초록 단색임을 캡처로 확인.
- **주의**: 씬4(`#randomShapes`)와 `.random-progress`는 여전히 3색 3모양이다. 그 씬의 대사는 색을 언급하지 않아 불일치가 아니므로 범위에 넣지 않았다.


## 20. 산술 튜토리얼 — 더하는 대상 표시 추가

- 상태: 완료 (2026-07-31)
- 조치: `animateArithmetic`의 `reveal(index, mark)`에 표시 인자를 넣고, 실제 "더하기"인 문항(`q_add_7_3`·`q_add_10_2`·`q_add_7_3_2`)에서만 `revealAdded`로 도형에 **`.added`**를 남긴다. 처음부터 전부 있는 `q_total_shapes_ten`은 더하기가 아니므로 표시하지 않는다.
- 표현: `.paint-shape.added{border-radius:12%;box-shadow:0 0 0 5px var(--mark-add),0 0 22px 8px var(--mark-add-glow)}` + `shapeAddIn` 등장. 요소 자신에 배경이 없어 `box-shadow`가 **도형을 감싸는 사각 테두리 + glow**로 보인다(사용자 제안 그대로). 빼기 쪽 `.removed`와 대칭이 되게 표시를 지속시킨다.
- 색: `--mark-add: var(--surface)`(파랑) / `--mark-add-glow: rgba(31,115,201,.45)`. **오답 피드백 빨강(`--danger`)과 겹치지 않는다.** 19번으로 도형이 초록 단색이 되어 파랑 테두리가 더 또렷하다.
- 검증: `q_add_7_3`에서 `.paint-shape.added` 개수 **3**(= 더한 3개) 실측 + 캡처.


## 22. 동그라미·세모·네모를 HTML/CSS로 다시 만들기

- 상태: 완료 (2026-07-31)
- 사용자 결정: 표지판 도형(`road-sign-*.png`)은 **범위 제외**(14번의 "픽토그램·글자 모두 굽기" 결정을 유지).
- 조치: `.paint-shape`에서 `shape-tile-body.png` 스프라이트 + `background-blend-mode:multiply` + `mask-image` 우회를 **전부 걷어냈다**. 8번이 넣은 마스크는 색이 도형 밖으로 새는 raster 전용 문제의 우회였으므로 raster가 사라지면서 함께 불필요해졌다.
- 새 구조: `::before`가 외곽선(`--shape-line`), `::after`가 채움(`--shape-fill`)이고 `::after`만 `inset:var(--shape-stroke)`만큼 안으로 들어간다. 원은 `border-radius:50%`, 사각은 `border-radius:9%`, **삼각은 `clip-path:polygon(50% 0%,100% 100%,0% 100%)`**.
- **삼각형은 `border`가 `clip-path`에 잘려 선을 만들 수 없다.** 안쪽 폴리곤을 내심 기준으로 축소해 선 두께를 냈다 — 내접원 반지름 `r=30.9%`, 4% 안쪽 → 배율 `0.8706` → `polygon(50% 8.94%,93.53% 96%,6.47% 96%)`.
- `--shape-stroke:4%`는 px가 아니라 **비율**이라 96px(`.random-progress`) / 112px(`.drawing-summary`) / 150px(`.work-area`) 어디서도 같은 굵기 비율로 보인다.
- 선 색 토큰 신설: `--leaf-line:#3f8a26` / `--surface-line:#12508f` / `--danger-line:#a8342a` / `--purple-line:#5f428f` / `--accent-line:#c9971a`.
- 요소 자신에는 배경이 없으므로 `filter`의 `drop-shadow`·glow가 **도형 실루엣을 그대로 따라간다**(과거에 요소에 마스크를 직접 걸어 그림자가 잘린 전례를 피했다). `.hint-step`의 `--filter-glow-lg`도 유지된다.
- 검증: 영향 범위 전수 확인 — `#paintIntroVisual`(3색 3모양) · `#countShapes` · `#arithShapes` · `#randomShapes` · `#randomWorkProgress` · `.drawn-shape`(자유 그리기 4개 실제 클릭 배치) · `.drawing-summary`(확인 팝업). 전부 외곽선·채움·그림자 정상, 런타임 오류 0.
- **주의**: `shape-tile-body.png`는 참조가 없어졌다(삭제 여부 미확정 — todo.md 확인 항목 참조).

## 23. `section_shape_find` 상시 배치 학생 — 등장 시점 · 발 위치 · 피드백 주체

- 상태: 완료 (2026-08-03)
- 대상: `index.html` `#shapeSceneStudent` / `.classroom-student` / `showWrongFeedback` / `showFeedback`
- 사용자 지적:
  1. 오프닝 대사 중에도 오른쪽 학생이 서 있어 **같은 아이가 2명**으로 보인다. 대사가 끝난 뒤에 나와야 한다.
  2. 그 학생이 **책상 위에 서 있는 것처럼** 보인다. 위로 올려 마루바닥에 서게 한다.
  3. **피드백의 pose 변화가 서 있는 그 아이에게서** 나와야 한다.
- 조치:
  - `#shapeSceneStudent` 제어를 `showSceneStudent()` / `hideSceneStudent()` / `setSceneStudentPose(pose, holdMs)` 세 함수로 모았다(`SCENE_STUDENT_POSE_SRC`, `SCENE_STUDENT_POSE_MS=700`). `resetShapeScene`·`startPaintIntro`가 직접 `classList`를 만지던 것을 이 함수 호출로 바꿨다.
  - 등장 시점: `resetShapeScene`에서 숨기고, `shapeDialogueTap`의 `opening` → 찾기 전환 지점에서 `showSceneStudent()`로 등장시킨다. 진입 모션은 `.classroom-student.student-enter`(기존 `characterEnter` 키프레임 재사용).
  - 발 위치: `.classroom-student`를 `bottom:-12px / 340x560` → `bottom:129px / 300x494`. `student-*.png`는 셋 다 1024x1536이고 알파 bbox 하단이 y≈1370이라 `object-fit:contain`에서 발끝이 요소 하단 71px 위 → 발끝 stage y≈880으로 벽·바닥 경계(818)와 책상 상판(900) 사이 마루면에 앉는다. 크기 축소는 그 깊이의 원근 보정이다(배경 화분 기준 1m≈310px).
  - 피드백 주체: `showWrongFeedback()`은 `sceneStudentVisible()`이면 `#feedbackCharacter` 오버레이를 띄우지 않고 서 있는 아이를 `student-thinking`으로 700ms 교체한다. 대칭으로 `showFeedback()`도 `student-volunteer`로 700ms 교체한다(칭찬 말풍선은 종전대로 선생님 `teacher-praising`). 무대에 학생이 없는 계산 단계·씬3·씬4는 기존 오버레이 경로를 그대로 탄다.
  - `student-thinking.png`를 `<link rel="preload">`에 추가했다(첫 오답에서 src 교체 시 한 프레임 비는 것 방지).
- 검증: Playwright 1920x1080 실주행. 대사 중 `hidden:true` → 찾기 진입 `hidden:false, bottom:951px`(= 1080-129) → 오답 직후 `student-thinking` → 700ms 후 `student-idle` 복귀 → paint-intro `hidden:true` → 세기 단계 오답은 오버레이 경로. 스크린샷으로 발이 마루면에 닿고 아이가 한 명만 보이는 것을 확인.
- 주의: 이 학생의 좌표·크기를 다시 만지면 `findObjects`(특히 `square_lunchbox` x1480~, `circle_wall_clock` x880~1070)와 `.search-prompt`(y 90~190) 겹침을 다시 본다. 현재 학생 실루엣은 stage x 1165~1296 / y 509~880으로 어느 것과도 겹치지 않는다.
- 미해결 아님(참고): 대사용 `#shapeCharacter`와 `#feedbackCharacter`는 여전히 `bottom:-12px`로 책상 앞에 선다. 이건 전 씬 공통의 "전경 화자" 규약이라 이번 범위에서 건드리지 않았다.

## 26. `section_shape_find` 정답 뒤 아무 데나 누르면 진행 경로가 사라지는 데드엔드

- 상태: 완료 (2026-08-03)
- 대상: `index.html` `registerSearchWrong` / `showWrongFeedback` / `selectHotspot` / `renderSearch`
- 사용자 지적: "동그라미 세모 네모 선택이 틀리면 다음으로 못 넘어가는 버그가 있어."
- 조치(원인이 둘이라 둘 다 넣었다):
  - (a) `searchSolved` 플래그 신설. `selectHotspot`에서 `found.size===2`가 되는 순간 `true`, `renderSearch`에서 `false`로 되돌린다. `registerSearchWrong`은 `if(searchSolved)return`으로 즉시 빠진다. 씬4의 `randomAwaitingContinue`와 같은 역할이다.
  - (b) `showWrongFeedback`에 `if(feedbackContinueAction)return` 가드. 정답이 확정돼 진행 경로가 armed된 뒤에는 오답 오버레이를 아예 띄우지 않는다. 예전에는 안에서 `resetFeedbackOverlay()`가 `feedbackContinueAction=null`로 만들고 말풍선을 지워 진행 표면이 0개가 됐다.
- 검증: headless Chrome에서 재현 시나리오 재실행 — 정답 2개 → 빈 곳 3회 클릭 → `#feedbackSpeech`가 `정답입니다.다음 ▸` / `hasOnclick:true`로 유지, 클릭 시 다음 문항(`●모양 2개를 찾아 봅시다.`)으로 진행 확인.
- 주의: `searchArea.onclick`(hotspot 밖 클릭도 오답으로 세는 17번 이후 요구)은 그대로 살려 뒀다. 핸들러를 떼지 않고 게이트만 걸었다.
- 주의: (b)는 전 씬 공통이다. 앞으로 **정답 확정 이후에도 살아 있는 오답 판정 표면**을 새로 만들면 이 가드 덕에 데드엔드가 안 나지만, 씬별 "해결됨" 플래그도 함께 두는 것이 원칙이다.

## 27. 피드백 말풍선이 캐릭터에서 너무 멀리 떨어져 있다

- 상태: 완료 (2026-08-03)
- 대상: `index.html` `.speech.feedback-speech`
- 사용자 지적: "피드백 시 캐릭터 옆에 `정답` 말풍선이 너무 멀리 떨어져 있다."
- 조치: `.speech.feedback-speech`의 앵커만 `left:500px;top:250px` → **`left:380px;top:470px`**. 꼬리(`left − 34`)가 x 346으로 `teacher-praising.png`의 실제 알파 bbox(stage x 236~356) 안에 들어가고, 꼬리 높이가 인물 머리(y 548)에 온다. 폭·패딩·`min-height`는 건드리지 않았다(15번의 자동 크기 조정 유지).
- 검증: headless 캡처. 말풍선 본체가 인물 오른쪽(x 380~)에 서고 꼬리가 얼굴 높이를 가리키는 것을 확인.
- 주의: **앵커는 요소 박스가 아니라 `object-fit:contain` 후의 알파 bbox 기준으로 잡는다.** 이 요소는 박스 폭 360px 중 실제로 그려지는 것이 120px뿐이라 박스(440)를 기준으로 피하면 인물에서 84px 더 밀려난다.

## 28. `section_arithmetic_tutorial` 도형이 3줄이면 담장 위로 삐져나온다

- 상태: 완료 (2026-08-03)
- 대상: `index.html` `.work-area`
- 사용자 지적: "모양이 3줄이 되면 담장 바깥으로 모양이 삐져나온다."
- 조치: `.work-area`의 `top:250px` → **`338px`** 한 줄. 담장 면(`school-wall-closeup.png` stage y 367~878) 중앙 622에 박스 중앙을 맞췄다. 도형 크기는 줄이지 않았다 — 3행 높이 486px < 면 높이 511px이라 좌표만 내리면 된다.
- 검증: headless 실측 — 12개(3행)가 stage y **380~866**으로 면(367~878) 안. 캡처로 1행이 담장 캡 아래에 있는 것을 눈으로 확인.
- 주의: 이 박스는 `#paintIntroVisual`·`#countShapes`·`#arithShapes`가 공유한다(전부 같은 `school-wall-closeup.png` 배경이라 함께 내려가는 게 맞다). `#randomShapes`는 배경 면이 달라 29번에서 좌표를 통째로 오버라이드했다.

## 29. `section_random_problems` — 유형 4종 전부 출제 + 그림과 문제를 같이 보여주기

- 상태: 완료 (2026-08-03)
- 대상: `index.html` `startRandomEngine` / `renderRandom` / `playRandomShapeIntro` / `finishRandomShapeIntro` / `clearRandomShapeIntro` / `randomProgressValue` / `#randomPanel` / `#randomShapes` / `#randomShapeSkip` / `#randomWorkProgress`
- 사용자 지적: "A·B·C·D 4개가 나와야 하는데 3개가 나오고 있고, 그림이 보여지고 사라진다. 같이 볼 수 있도록 해 달라. 생성 규칙은 input.json을 참조."
- 조치(29-a, 4유형 6문항):
  - `randomSequence`를 `Math.random()<.5?[0,2,3]:[1,4,5]` → **`[0,1,2,3,4,5]`**. 생성 규칙(`randomBundle`)은 원문과 이미 일치했으므로 건드리지 않았다 — 2026-07-31 조치가 지키려던 "단계 간 operand 공유"는 `randomBundle`이 그대로 유지한다(A·C는 `add`, B·D는 `subtract`를 함께 쓴다).
  - `#randomWorkProgress`의 하드코딩 도형을 3개 → **6개**로 늘렸다(3개면 4문항째부터 안 채워진다).
  - 진행률을 `setProgress(72+n*4)`(→96, 다음 씬 84보다 커서 역행) → **`randomProgressValue()` = `72+round(n*10/길이)`** 로 바꿔 씬4 구간을 72~82로 재배분했다.
- 조치(29-b, 그림·문제 동시 표시):
  - **좌표를 좌우로 나눴다.** `#randomShapes` `left 290/top 250/1340x560` → **`left 180/top 390/576x466`**(+ `gap:14px;padding:20px`, `#randomShapes .paint-shape{height:96px}`), `#randomPanel` `left 245/width 1040` → **`left 690/width 940`**. 도형 x 180~756, 패널 내용 x 800~1520이다. 오른쪽 한계는 `.help-character`(실제 인물 x≈1660~1900, 뻗은 손 x≈1560).
  - 도형 박스는 **최대 개수 19개**(D-2단계 `subtract.a`) 기준으로 잡았다 — 96px 도형 5열 × 4행 = 정확히 536×426.
  - `#section_random_problems.shape-intro #randomPanel{visibility:hidden}` 규칙과 `.shape-intro` 클래스 토글을 제거했다.
  - `renderRandom`이 **`revealQuestion()`을 먼저 부르고** 그 다음 `playRandomShapeIntro(script)`를 재생한다(예전에는 연출이 끝나야 문제가 열렸다). `playRandomShapeIntro`의 `done` 콜백 인자를 없앴다.
  - `finishRandomShapeIntro`는 이제 도형을 숨기지 않고 **남은 단계를 즉시 적용(`randomShapePending`)한 뒤 건너뛰기 레이어만 내린다.** `randomShapeDone` 변수는 `randomShapePending` 배열로 대체했다.
  - `#randomShapeSkip`을 전면(`inset:142px 0 0`) → 도형 박스와 같은 좌표로 좁혔다. 전면으로 두면 같이 떠 있는 키패드를 막는다.
  - 보기 선택 문제(type 0)만 도형을 숨긴다 — 식이 3개라 도형 하나로 무엇을 세는지 특정할 수 없다.
- 조치(덤, 같은 요소라 함께 고침): `#randomPanel .random-prompt` 높이 165 → **220px**, 패딩 `33px 40px`. 문항 최장인 3줄(`덧셈과 뺄셈 / 10에서 빼어 보세요. / 10 - 6=(   )`)은 41px × 1.2 × 3 = 148px이 필요한데 165px로는 모자라 **3번째 줄이 `overflow:hidden`에 잘려 있었다**(이번 수정 전부터 그랬다). `wall-choice-plaque-body.png`(780×100) 실측 크림 면 y 0.15~0.85 비율로 패딩을 잡았다. `#randomInput .choice`도 780×120 → 700×115로 함께 줄였다.
- 검증: headless 캡처 — 2문항째(`10 - 6=(   )`)에서 도형(왼쪽)과 식·키패드(오른쪽)가 한 화면에 함께 보이고, 프롬프트 3줄이 온전히 표시되며, 진행 표시 6칸 중 1칸이 채워지고 진행률 74%인 것을 확인. 런타임 오류 0.
- 주의: 원문 387행의 "`B + C = 10`·`A + C = 10`도 가능하면"은 **감사 요청(필수 아님)** 이라 이번 범위에서 제외했다(2026-08-03 결정).
- 주의: 씬4를 벗어난 뒤에도 연출 타이머는 남는다(재진입 시 `renderRandom`이 정리). 이전과 같은 동작이다.

## 30. `section_free_drawing` — 크기·기울기 조절 추가 + 그리기 영역을 담장 안쪽으로

- 상태: 완료 (2026-08-03)
- 대상: `index.html` `.paint-tools` / `.tool-slider` / `#drawingCanvas` / `#completedMuralPreview` / `drawingState` / `applyDrawnShapeStyle` / `drawnHalfExtent` / `renderCompletedMural` / `resetDrawingIntro`
- 사용자 지적: "그리기 툴에 도형 크기 변경 실린더와 기울이기 실린더가 있으면 좋겠다. 담장 바깥에 이미지가 짤리니 그리기 영역을 담장 안쪽으로 줄여 달라."
- 조치(30-a, 슬라이더 — "실린더"는 2026-08-03 사용자 확인으로 슬라이더 확정):
  - `.paint-tools`에 `<input type="range">` 두 개를 넣었다 — `#drawSizeRange`(80~220px, step 10, 기본 150) / `#drawTiltRange`(−30°~+30°, step 5, 기본 0). `.tool-slider` / `.tool-slider-label` / `.tool-slider-value` 스타일 신설(손잡이 34px).
  - 상태는 `drawSize` / `drawTilt`, 동기화는 `syncDrawSliders()`. 슬라이더는 **다음에 찍을 도형에만** 적용된다.
  - **저장·복원을 함께 고쳤다.** `drawingState()`가 `{shape,color,left,top,size,tilt}`를 저장하고 `renderCompletedMural()`이 같은 규칙으로 복원한다. 생성·복원이 어긋나지 않게 `applyDrawnShapeStyle(el,item)` 한 함수로 모았다(값은 `dataset.size`/`dataset.tilt`에도 남긴다).
  - 크기는 **가로세로 같은 배율**로만 건다 — 22번의 `.paint-shape.triangle` 안쪽 폴리곤이 정삼각형 비율 전제라 늘리면 선 두께가 어긋난다.
- 조치(30-b, 담장 밖 잘림):
  - `#drawingCanvas` `top:275px;width:1370px` → **`top:320px;width:1320px`**(x 390~1710 / y 320~860). 담장 면(x 172~1776 / y 308~877) 안이다. `#completedMuralPreview`도 **같은 값**으로 맞췄다(씬7 `school-wall-completed.png`의 면은 실측 y 304~876으로 씬5와 사실상 같아 같은 박스를 쓸 수 있다).
  - `drawingCanvas.onclick`에서 클릭 좌표를 도형 반폭만큼 clamp한다. 반폭은 `drawnHalfExtent()` — **회전을 반영해야 한다.** 한 변 s를 θ만큼 돌리면 축정렬 반폭이 `s/2`가 아니라 `(s/2)(|cosθ|+|sinθ|)`로 커진다(30°에서 1.37배). 원만 `s/2`. 처음에 `s/2`만 쓴 판을 캡처했더니 기울인 사각형·삼각형이 모서리에서 잘렸다.
- 검증: headless 실주행 — 네 모서리 극단 좌표에 크기 220/80/150/180 · 기울기 0/30/−30/15로 찍어 전부 잘림 없이 담장 면 안에 들어오는 것을 캡처로 확인. 씬7까지 진행해 크기·기울기가 그대로 복원되는 것도 확인.
- 주의: `#drawingCanvas`와 `#completedMuralPreview`는 여전히 **같은 값을 두 곳에 하드코딩**한다. 한쪽만 바꾸면 완성 그림이 다른 자리에 복원된다.
- 주의: 씬7 담장 면 실측값은 `todo.md`의 "배경 담장 면 실측값" 표에 추가했다.

## 31. `section_free_drawing` — 완료 버튼 라벨과 요약 도형 개수 제한

- 상태: 완료 (2026-08-03)
- 대상: `index.html` `#drawingDone` / `renderDrawingSummary` / `.drawing-summary .summary-more`
- 사용자 지적: "버튼 글을 `완성하기`로 바꾸고, `그림을 완성했나요?` 아래 도형이 6개 이상이면 넘치니 5개 이상이면 `...`으로 표시하자."
- 조치:
  - (31-a) `#drawingDone`의 보이는 글자를 `버튼` → **`완성하기`**. `aria-label="그림 완성하기"`는 그대로다. 원문 md 405~410행 UI 요소 표의 `| 3 | 버튼 | 버튼 |`을 라벨로 쓴 것이 원인이었는데, **사용자 지시가 원문 보존 계약보다 우선**한다는 판단으로 바꿨다(production 사본 한정).
  - (31-b) `renderDrawingSummary`에 `DRAWING_SUMMARY_MAX=4` 상한을 두고 초과분은 `.summary-more`(`…`) 한 칸으로 대신한다. 사용자 문구("5개 이상이면 `…`")를 그대로 따랐다. 조합은 3모양 × 4색 = 최대 12개까지 늘 수 있어 상한이 없던 것이 진짜 문제였다.
- 검증: headless에서 12조합을 모두 찍고 확인 팝업을 열어 도형 4개 + `…`로 패널 안에 들어가는 것을 캡처로 확인.

## 32. `section_math_story` 인트로 판에 ● ■ ▲ 가 없다

- 상태: 완료 (2026-08-03)
- 대상: `index.html` `#storyIntroBoard` / `.story-intro-board` / `.story-intro-shapes` / `storyBeats`
- 사용자 지적: "`모양을 길에서 본 적 있나요?` 위에 동그라미 세모 네모가 필요하다. 그 다음 화면에 나오는 게 아니라."
- 조치:
  - `#storyIntroBoard` 안을 `<div class="story-intro-shapes">`(●■▲) + `<span>`(문구) 두 줄로 바꾸고, `.story-intro-board`를 `place-items:center` → `grid-auto-flow:row;align-content:center;justify-items:center;gap:14px`로 바꿨다. 도형은 22번대로 raster가 아니라 `.paint-shape` CSS이며 색은 19번의 **초록=● / 파랑=■ / 빨강=▲** 매핑을 따랐다.
  - **판 높이(220px)는 늘리지 않았다.** 이 판은 `story-roadside-info-board.png`를 원본 비율 그대로 쓰는 유일한 곳이라 늘리면 `.story-card`와 같은 늘어짐이 생긴다. 가용 높이 220 − 33 − 59 = 128px에서 문구 한 줄이 62.5px이므로 도형은 `height:50px` + gap 14 = 64px로 맞췄다.
  - `● ■ ▲`가 인트로로 옮겨졌으므로 `storyBeats[0]`(`{text:'● ■ ▲',sign:-1}`)을 **제거**했다. 길이 7 → 6이 되어 `setProgress(94+storyIndex)`는 94~99가 되고 마지막 beat 분기는 자동으로 따라온다. 정적 마크업 `#storyCard`의 초기 텍스트도 `무슨 표지판일까요?`로 맞췄다.
- 검증: headless 캡처로 인트로 판 문구 위에 ●■▲ 세 개가 크림 면 안에 들어가는 것, 씬6 진행이 6 beat로 끝나 99% → 완료 화면 100%로 이어지는 것을 확인.

## 33. `section_math_story` 표지판 설명이 아래로 치우쳐 잘리고 글자가 작다

- 상태: 완료 (2026-08-03)
- 대상: `index.html` `.story-card`
- 사용자 지적: "표지판 설명이 그림 가운데 정렬이 아니라 아래로 치우쳐 잘리고 있고, 글자 크기도 더 키우면 좋겠다."
- 조치(**카드 크기도 `.sign-row`도 건드리지 않았다** — 2026-08-03 사용자 지시 "카드를 키우는 게 아니라 글씨를 키우면 된다"):
  - 패딩을 손으로 잡은 `282px 108px 118px` → **에셋 크림 면 비율로 계산한 `101px 64px 153px`**. `story-roadside-info-board.png`(1420×220) 실측 크림 면은 x 0.048~0.954 / y 0.168~0.745이고, 카드 1300×600 환산으로 가용 영역이 **1177 × 346px**(stage y 696~1042)이 된다.
  - `display:grid;grid-auto-flow:row;align-content:center` 추가 — 짧은 beat도 크림 면 세로 가운데에 온다.
  - 글자를 사다리 한 단계 올렸다: `--fs-sm`(37px) → **`--fs-md`(41px)**. 개별 px를 쓰지 않았다(16번 규칙).
- 검증: headless 실측 — 가장 긴 beat(▲ 표지판)의 글 영역이 **stage y 709~1036**으로 크림 면(696~1042)과 무대(1080) 안에 모두 들어간다. 캡처로 마지막 줄과 `다음 ▸` 버튼이 모두 보이는 것을 확인.
- 주의: 가로 패딩을 108 → 64로 줄인 것이 핵심이다. 글 폭이 1084 → 1172가 되면서 가장 긴 beat가 6줄 390px → **334px**로 줄어 346px 안에 들어갔다. 폭을 되돌리면 글자를 못 키운다.
- 주의: `.story-intro-board`는 같은 에셋을 **원본 비율 그대로** 쓴다. 이 카드 값을 그쪽에 복사하지 않는다.

## 34. `section_shape_find` 첫 대사의 화자를 선생님으로, 오른쪽에서 나오게

- 상태: 완료 (2026-08-03)
- 대상: `index.html` `shapeDialogues` / `#shapeDialogue` 정적 마크업
- 사용자 지적: "`여러 가지 모양으로 그리면 좋겠어요` 대사는 선생님이 할 거야. 오른쪽에서 나오게 해 줘."
- 조치(화자·방향 + **순서까지** — 2026-08-03 사용자 결정):
  - `shapeDialogues`의 앞 두 원소를 맞바꾸고 교사 대사의 에셋·방향을 바꿨다. 결과 순서는 원문 `…723 음성 스크립트.md` 씬2 그대로 — `1.주인공(좌) 벽화를 어떻게 그려야 되지? → 2.교사(우) 여러 가지 모양으로 그리면 좋겠어요. → 3.교사(우) → 4.주인공(좌)`. **문구는 하나도 바꾸지 않았다.**
  - 교사 alt는 같은 파일이 이미 쓰는 문구를 그대로 복사했다(`민트색 블라우스를 입고 밝게 미소 지으며 왼쪽 학습 대상을 열린 손으로 안내하는 여 교사`).
  - 정적 마크업(`#shapeDialogue`)도 함께 `student-thinking.png` / 주인공 alt / `벽화를 어떻게 그려야 되지?`로 바꿨다. **한쪽만 고치면 첫 프레임에 이전 인물이 번쩍인다.**
- 검증: headless 캡처로 씬2 진입 첫 화면이 주인공(왼쪽) + `벽화를 어떻게 그려야 되지?`인 것을 확인.
- 주의: 오프닝 동안 `#shapeSceneStudent`는 `hideSceneStudent()`로 숨어 있어 beat 1·3의 `student-*` 화자와 인물이 중복되지 않는다(23번 전제 유지).

## 24. `section_shape_find` 공책·도시락이 책상 위에 놓인 느낌이 안 난다

- 상태: 완료 (2026-08-03)
- 대상: `index.html` `findObjects`(`square_notebook` / `square_lunchbox`) / `.find-object.on-desk` / `assets/classroom-notebook.png`
- 사용자 지적: "책과 도시락이 책상 위에 놓여져 있는 분위기가 안 산다. 살짝 눕혀 달라."
- 진단(원인 셋, **비중이 큰 쪽은 기울기가 아니라 좌표였다**). `classroom-shape-search.png` stage 실측:
  - 가운데 책상 상판 x 580~1051, 뒷모서리 y≈901, 앞모서리 y≈985. 의자 등받이가 x 631~913을 y≈953부터 앞에서 가린다.
  - 오른쪽 책상 상판 x 1243~1636, 뒷모서리 y≈901, 앞모서리 y≈979. 의자 등받이가 x 1381~1616을 y≈956부터 가린다.
  - 예전 `square_notebook` `[860,790,185,185]`는 위쪽 111px가 상판보다 높은 허공, `square_lunchbox` `[1480,790,185,185]`는 오른쪽 끝 x=1665가 상판 오른쪽 끝 1636을 29px 넘어갔다.
  - 시점 불일치 — 상판의 깊이 압축비는 폭 470 : 깊이 84 ≈ **0.18**(하이앵글)인데 `classroom-notebook.png`가 완전 정면 정투영이라 "세워 둔 책"으로 읽혔다.
  - 접지 그림자 부재 — `.find-object{filter:var(--ds-sm)}`의 균일 드롭섀도뿐이었다.
- 조치:
  - 좌표를 상판 폴리곤 안으로 내렸다 — `square_notebook` `[910,866,150,150]`(핫스팟 `[906,890,150,102]`), `square_lunchbox` `[1430,829,150,150]`(핫스팟 `[1442,848,127,110]`). 좌표는 `findObjects` 한 곳에만 있고 핫스팟이 여기서 파생되지만, 그림과 클릭 영역을 따로 잡아야 해서 `hotspotRect`를 함께 줬다.
  - 접지 그림자 `.find-object.on-desk` 신설 — `drop-shadow(0 6px 5px rgba(76,52,40,.34)) drop-shadow(0 2px 1px rgba(76,52,40,.22))`. 상판이 하이앵글(0.18)이라 그림자도 낮고 옆으로 퍼지게 잡았다. **이 filter는 `.find-object`의 `var(--ds-sm)`를 덮어쓴다(같은 속성) — 의도된 것이다.**
  - 눕히기는 **B안(에셋 재생성)으로 확정.** `classroom-notebook.png`를 3/4 하이앵글(세로/가로 0.60)로 다시 그렸다(1254×1254 유지).
- **A안(CSS `rotateX`)은 시도했다가 폐기했다.** `rotateX(62deg)`로 눕힌 판을 보고 사용자가 "노트가 너무 눕혀져 있다"고 판정했다. 62°는 배경 상판의 실제 압축비(0.18 ≈ 80°)보다도 오히려 완만한 값이었는데도 과하게 느껴졌다 — **저학년 학습 콘텐츠에서는 원근 정합보다 "■ 모양이 읽히는가"가 우선**이라 물리적으로 맞는 각도가 정답이 아니다. 부수적으로 상판 깊이(84px)에 맞추느라 공책이 120px까지 작아져 다른 사물(150~210)보다 눈에 띄게 작아진 것도 작용했다. `.find-object.lay-flat` 규칙은 제거했고, 그 자리에 **다시 CSS로 눕히지 말라**는 주석을 남겼다.
- 검증: headless Chrome 1920×1080 캡처 — 공책·도시락이 상판 면 위에 접지 그림자와 함께 놓이고, ■로 읽히며, `#shapeSceneStudent` 실루엣(x 1165~1296)과 겹치지 않는 것을 확인.
- 주의: 도시락은 이미 약간 하이앵글로 그려져 있어 에셋을 건드리지 않고 좌표만 옮겼다. 입체라 `rotateX`를 걸면 몸통이 뭉개진다.
- 주의: 배경 `classroom-shape-search.png`의 책상 상판 실측값은 이 항목 본문에 있다. 이 씬에 사물을 더 놓거나 옮길 때 다시 재지 말고 위 값을 쓴다.

## 25. `section_shape_find`의 삼각 깃발을 다른 삼각형 오브젝트로 교체

- 상태: 완료 (2026-08-03, 커밋 `02b3ca0`)
- 대상: `index.html` `findObjects.triangle_party_hat` / `HAT_POSE_RECT` / `positionPartyHat` / `searchQuestions.q_triangle_find_two` / `assets/classroom-party-hat.png`
- 사용자 지적: 깃발이 어색하다. 다른 삼각형 오브젝트가 좋겠다.
- 진단: 문제는 삼각형 자체가 아니라 **교실 실재성**이었다. 벽에 짧은 막대 삼각 깃발이 홀로 박혀 있는 교실은 없어서 "사물"이 아니라 "붙여 놓은 도형 스티커"로 보였고, 삼각자와 나란히 떠 있어 둘이 같은 인상을 줬다.
- 조치: **고깔모자(`triangle_party_hat`)로 교체.** 후보 비교에서 1순위였던 트라이앵글(악기)이 아니라 고깔모자를 골랐다 — 저학년 ▲ 인지를 최우선으로 두면 면이 크고 알록달록한 쪽이 낫고, "벽에 걸린 물건"을 또 하나 더하면 삼각자와 같은 인상 문제가 반복되기 때문이다.
  - 벽이 아니라 **`#shapeSceneStudent`의 머리 위**에 얹었다. 아이가 쓰고 있는 모자라서 교실 실재성이 확보된다.
  - `HAT_POSE_RECT`(`idle:[1145,400,171,171]` / `thinking:[1114,397,171,171]` / `volunteer:[1154,401,171,171]`) — 학생 에셋 3종은 머리 위치가 서로 달라(가로로 최대 40px = 머리 폭의 1/3) 한 자리에 고정하면 `thinking`에서 눈에 띄게 미끄러진다. `positionPartyHat(pose)`가 `renderFindObjects`와 `setSceneStudentPose`에서 불려 그림을 따라 옮긴다.
  - **핫스팟은 세 포즈의 머리를 모두 덮는 고정 박스** `hotspotRect:[1136,405,170,178]`이다. 그림은 움직여도 클릭 영역은 고정된다 — `renderSearch`가 다시 만들어도 어긋나지 않는다.
  - `searchQuestions.q_triangle_find_two.answers`를 `['triangle_ruler','triangle_party_hat']`으로, `alt`를 `교실 아이가 머리에 쓴 하늘색 줄무늬 고깔모자`로 바꿨다. 에셋은 `1-2/01/lesson.json`의 `artDirection`을 읽어 프롬프트에 반영해 생성했다.
- 검증: headless 캡처 — 모자가 학생 머리에 자연스럽게 얹히고 삼각자와 재질·색이 확실히 갈리는 것을 확인.
- 영향 없음 확인: 카운트 씬(`countQuestions`의 `q_count_triangle`, 답 2)은 CSS `.paint-shape`로 그리므로 찾기 씬 오브젝트 교체와 무관하다.
- 주의: **`.classroom-student`의 `left`/`bottom`/`width`/`height`를 바꾸면 `HAT_POSE_RECT` 세 값과 `hotspotRect`를 다시 재야 한다.** rect는 1254 정사각 에셋 기준이고 그 안에서 모자 실물은 좌 23.6 / 상 17.2 / 폭 124 / 바닥 152.6 지점에 있다.

## 35. 챕터 이동 CTA가 보일 때 말풍선의 `다음 ▸`를 빼기

- 상태: 완료 (2026-08-03)
- 대상: `index.html` `clearAdvanceNav` / `#introTap`·`#shapeDialogueTap`·`#arithIntroTap`의 마지막 beat 분기
- 사용자 지적: "다음 챕터 버튼이 나올 때는 말풍선에 `다음`을 넣지 말기."
- 조치: `ensureAdvanceNav` 옆에 `clearAdvanceNav(el)`(`.repair-bubble-nav`를 찾아 `remove()`)을 만들고, **CTA를 여는 세 지점에서만** 불렀다 — 씬1 `introTap`의 마지막 beat, 씬2 `outro`의 두 번째 beat, 씬3 `outro`의 두 번째 beat. 대사 문구는 건드리지 않았다.
- 검증: headless 캡처 — 씬1 마지막 beat에서 `#introNext`가 뜨고 `#introSpeech .repair-bubble-nav` 개수가 0인 것을 확인.
- 주의: **지우는 조건은 "같은 화면에 CTA가 보인다" 하나뿐이다.** 진행 버튼이 유일한 진행 수단인 beat에서 지우면 15·17번이 고친 데드엔드가 재발한다. `#drawingDone`(완성하기)은 그 시점에 `#drawingDialogue`를 통째로 숨기므로 해당 없다.

## 36. `section_shape_find` 호버 테두리를 사물 이미지 모양에 맞추기

- 상태: 완료 (2026-08-03) — **B안(실루엣 글로우)으로 확정**, 사용자 선택
- 대상: `index.html` `.find-object` / `.hotspot` / `setObjectGlow`·`clearObjectGlow` / `renderSearch` / `revealSearchAnswers` / `selectHotspot`
- 사용자 지적: "아이템 호버 시 노란색 테두리가 나오는데 테두리를 이미지에 맞추기."
- 조치:
  - `.hotspot`에서 `border-color`·`filter` 상태 규칙을 전부 걷고 `border:0`으로 바꿔 **클릭 영역 전용**으로 만들었다.
  - 보이는 표시는 `.find-object`의 `filter` drop-shadow 4방향 겹침이 낸다(체이닝이라 링이 닫힌다) + 바깥 글로우 한 겹. 알파를 따라가므로 삼각자·고깔모자처럼 실루엣이 사각형과 다른 사물에서도 어긋나지 않는다.
  - **filter 선언 충돌 회피**: `.find-object.on-desk`의 접지 그림자와 같은 속성이라 `--obj-outline` / `--obj-shadow` 두 변수로 나누고 `filter:var(--obj-outline,) var(--obj-shadow)` 한 선언에서 합쳤다. 새 그림자를 넣을 때도 `--obj-shadow`만 바꾼다.
  - 상태 3종을 그림으로 옮기는 `setObjectGlow(id,cls,on)`을 만들어 hover(`glow-hover`, `--accent`)·3회 오답 공개(`glow-hint`, `--accent`)·정답(`glow-found`, `--leaf`)에 연결했다. `.find-object`는 `pointer-events:none`이고 `#shapeObjects`와 `#hotspots`는 부모가 달라 형제 선택자가 닿지 않아 JS로 전달한다. `renderSearch`가 문항마다 `clearObjectGlow()`로 초기화한다.
  - 사각 테두리가 사라진 만큼 키보드 포커스에도 같은 글로우를 걸었다(`onfocus`/`onblur`).
- 검증: headless 캡처 — 공책·삼각자 호버 시 글로우가 실루엣을 따라가고, `.on-desk` 사물의 접지 그림자가 사라지지 않는 것(computed filter에 두 값이 모두 있음)을 확인.
- 주의: `.hotspot`에 `border-color`를 다시 넣으면 사각 테두리가 되살아난다. `triangle_party_hat`은 포즈마다 그림이 움직이는데 글로우도 그림에 붙으므로 자연히 따라간다(고정 핫스팟 박스와 어긋나던 25번의 예외가 풀렸다).

## 37. `section_shape_find` 삼각자를 칠판 위에 세우고 약간 왼쪽으로

- 상태: 완료 (2026-08-03) — **"칠판 상단 테두리 위에 세워 기대기"로 확정**, 사용자 선택
- 대상: `index.html` `findObjects.triangle_ruler`
- 사용자 지적: "삼각자를 칠판의 위에 서 있도록 하고 그리고 약간 왼쪽으로 옮기기."
- 조치: `rect:[500,395,210,210]` → `rect:[300,95,170,170]`, `hotspotRect:[323,114,131,128]`(알파 bbox) 신설.
  - 배경 실측: 칠판 프레임 윗면 stage y **242**, 그 위 벽 띠는 천장 몰딩(y 130)까지 **112px뿐**이다. 천장 형광등은 stage y 25~78.
  - 에셋 알파 bbox 비율 x 0.1356~0.9035 / y 0.110~0.8652 → 170px 박스에서 실물은 x +23~+154 / y +19~+147. `top:95`면 밑변이 y 242(프레임 윗면)에 정확히 닿고 꼭짓점만 몰딩 선을 살짝 넘는다.
- **210 → 170으로 줄인 것은 이 면의 높이 제약 때문이다.** 210을 유지하면 꼭짓점이 y 32까지 올라가 천장 형광등과 겹친다. 왼쪽으로 옮길수록 형광등(x 132~614)에 더 가까워지므로 크기를 줄이는 것 외에 선택지가 없었다.
- 검증: headless 캡처 — 삼각자가 칠판 상단 테두리에 밑변을 대고 서 있고, `.search-prompt`(x 570~1350)와 겹치지 않는 것을 확인.
- 주의: CSS로 눕히거나 세우지 않았다(24번 규칙). 36번의 글로우 대상도 이 좌표를 따라 함께 옮겨졌다.

## 38. 아이 캐릭터를 어른 캐릭터의 70% 크기로 축소

- 상태: 완료 (2026-08-03)
- 대상: `index.html` `.character` / `.character[src*="student-"]` / `.feedback-character` / `.character[src*="student-"].left + .speech.left-speaker`
- 사용자 지적: "아이 캐릭터와 어른 캐릭터의 크기가 같아 인지 부조화 → 아이를 어른의 70% 정도로 축소."
- 조치:
  - `.character{--char-scale:1}` + `.character[src*="student-"]{--char-scale:.7}`, 그리고 `.left`/`.right`/`.small`/`.feedback-character`의 width·height를 `calc(<원래 px> * var(--char-scale))`로 바꿨다. `bottom`은 그대로 두어 발끝이 같은 바닥선에 남는다.
  - **클래스 토글이 아니라 `src` 속성 선택자를 썼다.** 렌더 지점 12곳이 `ch.className='character left'`로 클래스를 통째로 갈아 끼우므로 JS로 붙인 `.child`는 그때마다 지워진다. `src`는 그 지점들이 반드시 바꾸는 값이라 자동으로 따라온다.
  - **말풍선 꼬리 보정(27번과 같은 결함).** 아이가 70%가 되면 알파 bbox도 줄어 꼬리가 인물 밖(하늘)을 가리켰다. 대사 말풍선은 전부 캐릭터 `<img>`의 **바로 다음 형제**라 인접 형제 선택자로 앵커만 옮겼다 — `.left`는 `left:390 → 280`, `.right`는 `right:390 → 250`. 실측(폭 440 → 308): `.left` thinking x 124~268 · idle x 149~284 → 꼬리 끝 246, `.right` volunteer x 1612~1785 · idle x 1647~1785 → 꼬리 끝 1704.
- 검증: headless 캡처 — 씬1 마지막 beat(아이, right)와 씬2 오프닝 beat 0(아이, left)에서 꼬리가 인물 위에 오고, beat 1(교사)에서는 앵커가 390으로 되돌아오는 것을 확인.
- 주의: 15번 규칙대로 **바꾼 것은 앵커 좌표뿐**이다. 폭·패딩을 건드리면 자동 크기 조정이 깨진다. `#feedbackSpeech`는 `.left` 클래스가 없어 이 보정을 받지 않는데, 오답(student-thinking) 때는 `showWrongFeedback`이 말풍선을 숨기므로 문제되지 않는다. 씬2의 `.classroom-student`(300×494)는 `.character`가 아니라 영향 없다.

## 39. 페인트 통 에셋에 색을 표시하기

- 상태: 완료 (2026-08-03) — **CSS 오버레이로 확정**, 사용자 선택
- 대상: `index.html` `.paint-can` / `.paint-can-img` / `.paint-can::after` / `#paintCan`·`#arithPaintCan1`·`#arithPaintCan2` / `renderCount`
- 사용자 지적: "페인트 통에 색깔 모양 넣어주기 — 페인트 가운데에 색깔을 칠해서, 대신 페인트 손잡이와 겹치지 않게."
- 조치:
  - `.paint-can`을 `<img>`에서 `<span>` 래퍼로 바꾸고(`.paint-can-img`가 안에 들어간다) `::after`로 색 면을 얹었다. `data-color="green|blue|red"`가 `--can-fill`/`--can-line`을 정하고 값은 `--leaf`/`--surface`/`--danger`와 그 `-line` 변형이다(도형과 같은 토큰).
  - **색 면 좌표는 에셋 실측이다**(1254×1254): 손잡이 아치 윗선이 x 380~860 구간에서 y 835 아래로만 지나가고, 뚜껑 테두리 아래 첫 평면이 y 470 → 안전면 **x 0.30~0.69 / y 0.38~0.65**. `todo.md`의 "크림 면 비율" 표에 기록했다.
  - 원통 곡면을 흉내내려고 색 면에 상단 하이라이트·하단 음영 `linear-gradient`를 한 겹 얹었다(색 자체는 raster가 아니다 — 22번).
  - `#paintCan`의 색은 세기 단계에서 문항 색을 따라간다(`renderCount`에서 `dataset.color`·`aria-label` 갱신). 씬3의 두 통은 그 씬 도형이 전부 초록이라 초록 고정이다(19번).
  - `.paint-can{left:1202px}` → **1000px**. 예전 값은 `.keypad-wrap`(x 1305~1815) 뒤에 통 절반이 깔려 있었는데 색 면이 생기면서 그 잘림이 눈에 띄게 됐다. 왼쪽 한계는 `#countShapes` 4번째 칸 도형의 오른쪽 끝 x≈943이다(이 씬 최대 개수 4).
- 검증: headless 캡처 — 씬2 세기에서 통 색이 ●초록 → ▲빨강으로 따라가고 손잡이와 겹치지 않는 것, 씬3에서 초록 통이 나오는 것을 확인.
- 주의: `.empty`/`.arriving`이 이제 **래퍼**에 붙는다(그림과 색 면이 함께 회색이 되고 함께 튀어 오른다). 통 크기를 바꿔도 색 면은 %라 따라오지만, **에셋을 다시 그리면 위 비율을 다시 재야 한다.**

## 40. `section_shape_find` 페인트 소개에서 색 페인트 통을 각 모양 아래에 배치

- 상태: 완료 (2026-08-03)
- 대상: `index.html` `#paintIntroVisual` / `.paint-pair` / `startPaintIntro`
- 사용자 지적: "`페인트 색깔마다 모양이 달라요` 할 때 색깔 모양이 있는 페인트 통을 모양 아래에 배치해 주기."
- 조치: `#paintIntroVisual`의 도형 3개 가로 배치를 `.paint-pair`(도형 위 / 같은 색 통 아래) 세로 짝 **3벌**로 바꾸고, `startPaintIntro`에서 오른쪽 단일 `#paintCan`을 `remove('hidden')` → `add('hidden')`으로 뒤집었다. 색 매핑은 19번(초록 ● / 파랑 ■ / 빨강 ▲).
  - 좌표는 **`#paintIntroVisual`에만 오버라이드**했다(`left:360px;top:390px;height:440px;grid-template-columns:repeat(3,1fr)`). 공유 `.work-area{top:338px;height:570px}`는 `#countShapes`·`#arithShapes`가 함께 쓰므로 건드리지 않았다.
  - 담장 면(`school-wall-closeup.png` stage y 367~878, 높이 511) 안에 도형 150 + gap 16 + 통 200 = 366이 들어간다(박스 y 390~830 → 내용 y 427~793). 단일 통이 사라진 만큼 가로를 오른쪽으로 옮겨 무대 가운데에 맞추되 `.character.right`(x 1428~)를 넘지 않게 했다.
- 검증: headless 캡처 — 세 짝이 담장 면 안에 들어가고 교사·말풍선과 겹치지 않는 것을 확인.
- 주의: 통 크기 200px은 담장 면 높이에서 역산한 값이다. 도형을 키우면 통을 줄여야 한다.

## 41. `section_random_problems` 담장 도형을 항별로 색 구분 + 중앙 면으로 + 키패드 축소

- 상태: 완료 (2026-08-03)
- 대상: `index.html` `RANDOM_OPERAND_CLASS` / `shapeStepsFor` / `playRandomShapeIntro` / `#randomShapes` / `#randomShapeSkip` / `#randomPanel` / `.random-prompt` / `#randomInput .choice`·`.keypad-wrap`·`.key`·`.answer-display` / `.random-progress`
- 사용자 지적: "`2+8=10`이라면 2개와 8개가 다른 색깔로 담장에 있어야지. 담장은 가운데쪽 큰 비어 있는 곳에만 모양을 두고 키패드는 약간 작게 해서 공간을 나오게 하고."
- 조치:
  - **(a) 항별 색 구분.** `shapeStepsFor`가 내던 `{base, steps}`를 `{groups:[{n,cls}], steps}`로 바꿨다. 예전에는 `i%3`으로 색·모양을 돌려 써서 색이 피연산자 경계와 무관하게 섞였고, 등장 애니메이션이 끝나면 단서가 완전히 사라졌다. 이제 항 순서에 19번 매핑을 그대로 얹는다 — **1번째 항 = 초록 ● / 2번째 = 파랑 ■ / 3번째 = 빨강 ▲**(`RANDOM_OPERAND_CLASS`). 색과 모양이 함께 묶여 두 규칙이 충돌하지 않는다. 뺄셈은 한 덩어리에서 빼는 것이라 그룹이 하나이고 `.removed` 표시는 그대로다.
  - **(b) 중앙 면으로.** `#randomShapes{left:180 → 374, width:576 → 610, height:466 → 500, gap:14 → 12, padding:20 → 16}`, 도형 96 → 104px. 예전 x 180~756은 왼쪽 194px이 배경의 낮은 대비 추상 벽화(x 253~374) 위에 걸쳐 있었다. 이제 x 374~984 · y 390~890으로 깨끗한 중앙 면(x 374~1522 / y 380~946) 안이다. 최대 19개 → 5열 × 4행. `#randomShapeSkip`도 같은 박스로 맞췄다.
  - **(c) 패널·키패드 축소.** `#randomPanel{left:690 → 990, width:940 → 570, min-height:700 → 640}`, `.random-prompt{720 → 540, padding 40 → 30}`, `.choice{700×115 → 540×110}`, `#randomInput .keypad-wrap{width 510 → 440}`, `.key{78 → 68}`, `.answer-display{100 → 88}`, `.keypad{gap 17 → 14}`. 내용 x 990~1560이고 오른쪽 한계는 `.help-character` 알파 실측의 뻗은 손 x≈1569다.
  - `.random-progress`를 `left:360px` → `left:50%;transform:translateX(-50%)`로 바꿔 칸 수가 달라져도 가운데 정렬이 유지되게 했다(43번과 함께).
- 검증(16번 재실측 포함): headless에서 5개 문항 문구를 `#randomPromptText`에 직접 넣어 측정 — 최장인 3줄 문항이 148px로 `wall-choice-plaque-body.png` 크림 면 154px 안에 들어간다(전부 `fits:true`). 4문항 연속 진행 캡처로 `1 + 9 + 5`가 초록 원 1 · 파랑 사각 9 · 빨강 삼각 5로 나뉘는 것을 확인.
- 주의: 폭 540에서는 유형 A의 `10이 되는 덧셈식을 찾아 보세요.`가 2줄로 접혀 문항 전체가 3줄이 된다(예전 720에서는 2줄). 크림 면 안에는 들어가지만 **여유가 6px뿐**이므로 사다리를 또 올리거나 패딩을 키우면 넘친다.
- 주의: 패널 폭을 다시 키우면 도형과 겹친다. 도형 박스를 키우면 패널이 밀려 위 3줄 판정이 깨진다.

## 42. `section_random_problems` 손가락 힌트를 매 문제 + 선생님을 가리키게 + 힌트를 선생님 말풍선으로

- 상태: 완료 (2026-08-03)
- 대상: `index.html` `.speech.top-speaker` / `.speech.help-speech`(`#helpCard`) / `.finger-hint`(`#fingerHint`) / `@keyframes fingerHintTap` / `renderRandom` / `startRandomEngine`
- 사용자 지적: "손가락 반짝이는 효과는 모든 문제에 해 주고 해당 손가락이 선생님을 가리키게 해 줘. 선생님을 클릭하면 말풍선으로 힌트를 주고, 말풍선은 선생님이 말하는 식으로 배치."
- 조치:
  - **(a) 매 문제 재생.** `startRandomEngine`에서 한 번만 띄우던 것을 `renderRandom`으로 옮기고 `style.animation`을 껐다 켜서 탭 애니메이션도 재시작한다. 예전에는 선생님을 한 번 누르면 `hidden`이 붙어 2번째 문제부터 힌트 존재를 알 길이 없었다.
  - **(b) 선생님을 가리키게.** 에셋이 왼쪽 위를 가리키므로 `--finger-base:scaleX(-1)`로 뒤집었다. 뒤집은 뒤 손끝은 박스의 (0.833, 0.152) → 180px 박스에서 (+150, +27). `right:330;bottom:300` + `rotate(70deg)` → `right:200;bottom:207`이면 박스 x 1540~1720 · y 693~873, 손끝 (1690, 720)이 선생님 몸통에 닿는다. **회전·반전을 `--finger-base` 하나로 모아** 키프레임과 어긋나지 않게 했다(예전에는 `rotate(70deg)`가 base와 keyframes 두 군데에 박혀 있었다).
  - **(c) 말풍선으로.** `.help-card`(크림 사각 패널)를 없애고 `#helpCard`를 `.speech top-speaker help-speech`로 바꿨다. 여닫이는 `display:none ↔ block`이라 열 때마다 `speechPop`이 재생된다.
  - **`.speech.top-speaker` 변형을 새로 만들었다** — 인물 위에서 아래로 꼬리를 내리는 2겹 구조(1-2/01의 하단 변형과 같다). 처음엔 얼굴 높이에 `.right-speaker`로 붙였는데 말풍선이 보기 버튼(y 437~791)을 덮어 **정답이 가려졌다.** 인물(x 1569~1820) 왼쪽은 전부 문제 패널이라 옆으로 붙일 자리가 없다.
  - 앵커는 `teacher-explaining.png`의 `object-fit:contain` 후 알파 bbox 기준이다 — 인물 x 1569~1820 / y 481~1066, 머리 x 1697~1805 · 꼭대기 y 481. `right:60` → 꼬리 중심 x 1783이 머리 안이고 말풍선은 x 1602~1860이라 패널(x 990~1560)과 겹치지 않는다. `bottom:620` → 꼬리 끝 y 460. **`top`이 아니라 `bottom`으로 잡아야** 힌트 줄 수가 달라져도 꼬리가 머리에 붙어 있는다.
- 검증: headless 캡처 — 4문항 모두에서 손가락이 다시 뜨고, 힌트 말풍선이 선생님 머리 위에서 열리며 보기 3개를 가리지 않는 것을 확인. 정답 후 `#helpCard`에 `다음 ▸`가 붙고 클릭으로 다음 문항으로 넘어가는 것(26번 데드엔드 없음)도 확인.
- 주의: `armRandomContinue`가 `#helpCard`를 **진행 표면으로 쓴다**(`ADVANCE_NAV_HTML` + `role="button"` + `onclick=nextRandom`). 표면을 또 바꾸면 이 경로를 함께 옮겨야 한다. 15번 규칙대로 폭·패딩은 손대지 않았다 — 옮긴 것은 앵커 좌표뿐이다.

## 43. `section_random_problems` 문항을 6개 → 4개로

- 상태: 완료 (2026-08-03)
- 대상: `index.html` `startRandomEngine`(`randomSequence`) / `#randomWorkProgress`
- 사용자 지적: "6문제가 아니라 4문제야. `8+2+6`이면 `8+2` 한 문제 `8+2+6`이 아니라 바로 `8+2+6`을 해 주는 거야."
- 조치: `randomSequence=[0,1,2,3,4,5]` → **`[0,1,3,5]`**(A: 10이 되는 덧셈 보기 선택 / B: `10 - c` / C: `a+b+c` / D: `a-b-c`). `#randomWorkProgress`의 하드코딩 도형을 6개 → **4개**로 줄이고 색 순서를 19번 매핑(● ■ ▲ ●)에 맞췄다.
- 검증: 4문항 연속 진행 캡처 — 문항이 A → `10-6` → `1+9+5` → `13-3-6` 순으로 나오고 준비운동 단계가 없다. 진행률 72 → 75 → 77 → 80 → (씬5) 84%로 역행 없이 이어진다.
- 주의: 29번이 남긴 "문항 수에 묶인 세 곳" 중 `randomProgressValue()`와 `armRandomContinue`의 마지막 문항 분기는 `randomSequence.length` 의존이라 자동으로 따라왔다. **손으로 고친 것은 `randomSequence`와 `#randomWorkProgress` 둘뿐이다.**
- 미해결(범위 밖): type 2·4가 미사용이 되어 `shapeStepsFor`의 `type===2`·`type===4`와 `staticExamples`의 `q_random_c_step1`·`q_random_d_step1`이 죽은 코드다. **되돌릴 여지를 두고 남겨 뒀다.** `<template id="staticQuestionContract">`도 6문항 기준 문구를 그대로 갖고 있다 — `todo.md`의 "확인이 필요한 항목" 참조.

## 44. `section_math_story` ●■▲를 인트로 판 밖 화면 가운데로

- 상태: 완료 (2026-08-03) — **"제목 배너 ↔ 인트로 판 사이"로 확정**, 사용자 선택
- 대상: `index.html` `.story-intro-shapes`(`#storyIntroShapes`) / `#storyIntroBoard` / `resetStory` / `openStorySigns`
- 사용자 지적: "`모양을 길에서 본 적이 있나요?` 위에 모양이 있는데 그게 아니라 두 카드 사이에 놔줘. 카드 내부가 아니라 배경화면 앞에 화면 가운데쪽."
- 조치: `.story-intro-shapes`를 `#storyIntroBoard` 밖으로 빼 배경 앞 절대 배치로 옮기고 `id="storyIntroShapes"`를 줬다. 빈 면은 제목 배너(y 205~355)와 인트로 판(y 825~1045) 사이의 **y 355~825 · 470px**, 화면 가로 가운데다. 판 안의 128px 제약이 풀려 도형을 **50px → 180px**로 키웠다. 색 매핑은 19번 유지.
  - 판과 함께 여닫히지 않게 되었으므로 `resetStory`에서 열고 `openStorySigns`에서 닫는 코드를 각각 넣었다.
- 검증: headless 캡처 — 도형이 두 판 사이에 180px로 놓이고, 표지판 단계로 넘어가면 사라지는 것을 확인.
- 주의: `.sign-row`(y 275~665)와 **같은 영역**이다. `#signRow`가 인트로 단계에서 `hidden`이라 겹치지 않을 뿐이므로, 이 도형을 인트로 이후에도 남기려면 표지판 좌표를 다시 잡아야 한다. 인트로 판(`.story-intro-board`)은 이제 한 줄짜리라 `gap:14px`이 무의미하지만 그대로 뒀다.

## 45. 녹음 대사 오디오(52본) 적용 + `speak()`를 TTS에서 wav 재생기로 교체

- 상태: 완료 (2026-08-03)
- 대상: `index.html` `speak`/`playVoice`/`stopVoice`/`showFeedback` · `assets/audio/script/` 52개 파일명
- 사용자 지시: 원문 `…723 음성 스크립트.md`에 따라 녹음을 물린다. **다음으로 넘기면 재생 중인 음성은 자른다.** 파일명은 안정 키로 바꾼다. `모양을 찾아 봅시다`는 세 문항이 같은 본을 돌려 쓴다.
- 조치:
  - **파일명 리네임 52개.** 납품 원본 `Take{n}-1_{대사 전문}_2026-08-03.wav` → 코드가 쓰는 키 그대로(`intro-1-apology.wav` 등). 재녹음은 **같은 키 이름으로 덮어쓰면 코드 수정이 필요 없다.** 대조표는 아래.
  - `speak(text)`(speechSynthesis) → **`speak(text, voice)`**. `voice`가 있으면 `playVoice`로 wav를 재생하고, 없으면 무음이다(`VOICE_TTS_FALLBACK=false` 한 줄로 TTS 폴백을 되살릴 수 있다). 사람 목소리 사이에 TTS가 끼면 톤이 튀어 무음을 기본으로 뒀다.
  - `playVoice(key)`는 **문자열 또는 배열**을 받는다. 배열이면 `onended`로 이어 재생한다 — 한 말풍선이 녹음 2~3본으로 나뉜 자리가 4곳 있다(`arith-outro` 2본, 표지판 카드 3장이 각각 2·2·3본).
  - **끊기**: `speak`/`playVoice`가 항상 `stopVoice()`로 시작하고, 대사 없이 UI만 열리는 전환을 위해 `introTap`·`shapeDialogueTap`·`arithIntroTap`·`storyIntroTap`·`storyCard`·`drawingTap`·`drawingNo`·`completeFeedback`·`nextRandom`·`showScene`에 `stopVoice()`를 직접 넣었다. 음소거 버튼도 `speechSynthesis.cancel()` → `stopVoice()`.
  - 대사 데이터에 `voice` 필드를 추가했다(`introBeats`/`shapeDialogues`[5번째 원소]/`searchQuestions`/`countQuestions`/`arithmeticQuestions`+`preBeats`/`staticExamples`/`storyBeats`). `arithmeticIntroBeats`는 문자열 배열 → `{text,voice}` 객체 배열로 바꿨다(참조 3곳 동반 수정).
  - `showFeedback(el,text,onContinue)`에 **4번째 인자 `voice`** 추가. `정답입니다` 3본은 원문 위치를 따라 배분했다 — `correct-2`는 씬7-1(=`7+3+2` 정답 직후), `correct-3`은 씬8-3(=`10-3` 정답 직후), 나머지는 `correct-1`.
  - `drawingDone` 확인 패널에 `drawing-3-finished-question` 재생을 새로 걸었다. 원문 씬10-3에 있는데 기존 코드엔 `speak()` 호출 자체가 없었다.
- 검증: 계측 사본(`Audio`를 스텁으로 갈아 끼워 재생 순서를 기록)으로 **씬1~6 전 구간을 클릭 주파**했다. 52본이 전부 예상 순서대로 발화하고, 큐 4곳이 이어 재생되며, 넘기기 시 이전 음성이 잘리고(망치 연출 진입·CTA 노출·`● ■ ▲ 모양`·`무슨 표지판일까요?`에서 로그가 비어 있음), 콘솔 에러가 없다. 계측 사본은 검증 후 삭제했다.
- 주의:
  - 파일이 **wav 13MB**다. 웹 배포 시 mp3/ogg 변환을 별도로 검토해야 한다.
  - 첫 재생이 `시작하기` 클릭 이후라 자동재생 정책에 걸리지 않는다. `play()` 실패는 `catch(()=>{})`로 삼키고 진행은 탭으로 하므로 막히지 않는다.
  - `assets/audio/script/`의 파일명이 곧 코드의 키다. **파일명을 바꾸면 소리가 조용히 사라진다**(예외가 안 난다).
- 원본 테이크 ↔ 키 대조표:

| Take | 키 | Take | 키 |
| --- | --- | --- | --- |
| 1~4 | `intro-1-apology` / `intro-2-wall-fixed` / `intro-3-need-help` / `intro-4-volunteer` | 27~31 | `correct-2` / `arith-beat-thanks` / `arith-beat-yes-2` / `arith-beat-erase-2` / `arith-q-subtract-12-2` |
| 5~8 | `shape-open-1-how-to-draw` / `-2-various-shapes` / `-3-find-together` / `-4-yes` | 32~34 | `arith-beat-erase-3-more` / `arith-q-subtract-10-3` / `correct-3` |
| 9~11 | `search-prompt` / `correct-1` / `praise-well-found` | 35~37 | `arith-outro-1-well-done` / `-2-more-walls` / `-3-yes` |
| 12~15 | `paint-color-shape` / `count-circle` / `count-triangle` / `count-square` | 38~41 | `random-a-find-ten` / `random-b-subtract-from-ten` / `random-c-add-three` / `random-d-subtract-three` |
| 16~17 | `shape-outro-1-praise` / `shape-outro-2-request` | 42~44 | `drawing-1-almost-done` / `-2-free-draw` / `-3-finished-question` |
| 18~21 | `arith-intro-1-we-will` / `-2-this-is-paint` / `-3-ten-per-can` / `arith-q-total-ten` | 45~48 | `story-intro-seen-shapes` / `story-circle-question` / `story-circle-answer` / `story-square-question` |
| 22~26 | `arith-q-add-7-3` / `arith-beat-can-empty` / `-can-ready` / `-paint-2-more` / `arith-beat-yes` | 49~52 | `story-square-answer` / `story-triangle-question` / `story-triangle-answer` / `story-outro-safe` |

## 52. 추가 녹음 7본 적용 + `● ■ ▲ 모양`을 세 대사 단계 공개로 분리

- 상태: 완료 (2026-08-03)
- 대상: `index.html` `searchQuestions[].voice` / `PAINT_INTRO_SHAPES`·`renderPaintIntroShape`·`revealPaintPairs` / `.paint-pair` CSS / `storyBeats[0/2/4].voice` · `assets/add_audio/` → `assets/audio/script/`
- 사용자 지시: "`add_audio`에 새로운 음성을 추가해뒀다. `■/●/▲모양 2개를 찾아봅시다`는 알아서 넣고, `● ■ ▲ 모양`은 애니메이션으로 각각 모양 음성이 나올 때 말풍선과 함께 페인트 통과 모양을 하나씩 보여준다 — **대사도 3개로 나뉘는 것**. `무슨 표지판일까요?`는 음성 추가해놨다."
- 조치:
  - `assets/add_audio/`의 7본을 45번 규칙대로 키 이름으로 바꿔 `assets/audio/script/`로 옮겼다(총 52 → **59본**). `add_audio/`는 빈 디렉토리로 남겨 뒀다.
    - Take57/58/59 → `search-circle` / `search-square` / `search-triangle`
    - Take13/14/15 → `paint-shape-circle` / `paint-shape-square` / `paint-shape-triangle`
    - Take46 → `story-what-sign`
  - **찾기 3문항**이 모양별 녹음을 각각 쓴다(`search-square` → `search-circle` → `search-triangle`, 화면 순서 그대로).
  - **페인트 소개를 대사 1개 → 4개로.** `페인트 색깔마다 모양이 달라요`(짝 0개) → `● 모양`(1개) → `■ 모양`(2개) → `▲ 모양`(3개) → 세기 단계. `PAINT_INTRO_SHAPES` 배열 + `renderPaintIntroShape(index)` + `revealPaintPairs(count)`로 갈랐고, 탭 핸들러는 `shapeDialogueIndex`를 인덱스로 그대로 쓴다.
  - `.paint-pair`를 기본 `visibility:hidden` → `.revealed`에서 `visibility:visible` + `paintPairPop`. **`display:none`을 쓰지 않았다** — grid 칸이 무너져 먼저 열린 짝이 가운데로 밀린다. 자리는 처음부터 세 칸을 잡아 둬야 "다음은 여기"가 읽힌다.
  - `무슨 표지판일까요?` 카드 3장이 `story-what-sign`을 돌려 쓴다.
- 검증: 계측 사본으로 씬2·씬6 주파 — 발화 순서가 `search-square → search-circle → search-triangle → paint-color-shape(짝 0) → paint-shape-circle(1) → -square(2) → -triangle(3) → count-*`, 표지판은 `story-what-sign → 설명 2본 → story-what-sign → …`로 나온다. headless 캡처로 1짝·3짝 상태를 확인 — 첫 짝이 왼쪽 칸에 고정되고 2·3번째가 열려도 밀리지 않는다.
- 주의:
  - **`search-prompt`(옛 `모양을 찾아 봅시다`, 원문 씬2-5)는 참조가 0이 됐다.** 파일은 남겨 뒀다.
  - 새 찾기 녹음에도 **"2개"는 없다**(`동그라미 모양을 찾아봅시다`). 개수는 여전히 화면 배너로만 전달된다.
  - `PAINT_INTRO_SHAPES`의 순서 = `#paintIntroVisual`의 DOM 순서 = 19번 색 매핑(초록 ● / 파랑 ■ / 빨강 ▲)이다. **셋 중 하나만 바꾸면 색·모양·음성이 어긋난다.**

## 46. `section_arithmetic_tutorial` 도형이 3줄일 때도 시작점(세로)이 2줄일 때와 같아야 한다

- 상태: 완료 (2026-08-03) — **(a) 위 정렬로 확정**, 사용자 선택("권장 방향으로")
- 대상: `index.html` `.work-area` / `#paintIntroVisual`
- 사용자 지적: "3줄일 때도 도형의 시작점을 2줄일 때와 똑같이 하자. 시작점은 **세로 위치**를 말하는 거야."
- 조치: `.work-area{align-content:center → start}` + `top:338 → 354px`. 28번이 3행을 담장 면 안에 넣었지만 `align-content:center`가 남아 **행 수가 바뀔 때마다 첫 줄 y가 움직였다**(3행 380 / 2행 463). top을 3행 시작점 380에서 패딩 26을 뺀 354로 내리고 위 정렬로 바꾸니 몇 줄이든 첫 줄이 380이다.
  - `#paintIntroVisual`에는 `align-content:center`를 **다시 넣어 되돌렸다** — 이 씬만 한 줄짜리 짝(도형+통) 배치라 개수가 변하지 않고, 40번이 잡은 세로 중앙이 유효하다.
- 검증: headless 계측 — `#arithShapes`에 10개(2행)·12개(3행)를 넣어 첫 도형 rect를 쟀더니 **둘 다 y=380**, 3행 하단은 866으로 28번과 같다(담장 면 367~878 안).
- 주의: `#randomShapes`(씬4)는 좌표만 오버라이드하고 정렬은 상속하므로 함께 위 정렬이 됐다. 최대 19개(4행)가 y 406~858로 면(380~946) 안이다.

## 47. `section_random_problems` 정답인데 힌트가 떠서 정답처럼 안 보인다

- 상태: 완료 (2026-08-03)
- 대상: `index.html` `#randomSolved`(신규) / `armRandomContinue` / `completeRandomProblem` / `showRandomSolution`(제거) / `#randomPanel[data-solved]`
- 사용자 지적: "정답을 맞췄는데도 힌트가 나오느라 정답 처리가 안 되고 있어. **힌트는 오답일 때와 누를 때만** 나오는 거야."
- 조치:
  - **표면을 갈랐다.** `#helpCard`(선생님 힌트 말풍선)는 이제 힌트 전용이고, 정답 결과(중간식)와 진행 버튼은 문제 패널 안에 새로 만든 **`#randomSolved`**가 맡는다. `showRandomSolution()`은 없앴고 `armRandomContinue()`가 `closeRandomHint()` → 결과 판 열기 → `focus()`까지 한다.
  - 정답 뒤 입력기는 내린다 — `#randomPanel[data-solved="1"]`에서 `.keypad`(입력값 표시 `#randomDisplay`는 남긴다)와 `.choices`를 감춘다. **보기를 남겨 두면 결과 판이 네 번째 보기처럼 보인다**(같은 `wall-choice-plaque-body.png`를 쓰기 때문).
  - 유형 A는 48번의 물음표 칸이 정답을 받아 닫힌다(`.paint-slot.filled`, `8 + ? = 10` → `8 + 2 = 10`).
- 자리 선정(실측으로 걸렀다): `.bottom-cta`(y 870~1010)는 `#randomWorkProgress`(y 956~1052)와 겹치고, `#randomPrompt` 작업표는 41-c 기준 여유가 6px뿐이며, 공용 `#feedbackSpeech`(left 380/top 470)는 도형 박스를 덮고 `#feedbackCharacter`가 오른쪽 `.help-character`와 같은 선생님을 둘로 만든다. 남는 면은 패널 안 입력기 아래뿐이었다.
- 검증: headless로 4문항을 실제 클릭으로 주파 — 모든 정답 시점에서 `#helpCard`가 닫혀 있고(`helpOpen:false`) `#randomSolved`가 열린다. 판 위치는 유형 A y 437~587 / 키패드 유형 y 545~745로 진행 표시 막대(956) 위에서 끝난다.
- 주의(**26번 데드엔드**): 진행 경로가 `#helpCard` → `#randomSolved`로 **통째로** 옮겨졌다(`ADVANCE_NAV_HTML` + `role="button"` + `onclick=nextRandom` + `focus()`). 이 표면을 또 옮길 때는 네 가지를 함께 옮긴다. `.speech.help-speech.continue-ready` CSS는 이 이동으로 죽어 주석으로 대체했다.

## 48. `section_random_problems` 첫 문제에만 모양이 안 나온다

- 상태: 완료 (2026-08-03)
- 대상: `index.html` `shapeStepsFor`(`type 0` 신설) / `renderRandom`의 `randomType===0` 분기 / `.paint-op`·`.paint-slot`(신규 CSS)
- 사용자 지적: "가장 첫 문제에는 모양이 안 나오고 있어." / 지시: "8+2면 왼쪽 항은 문양으로 보여주고 나머지는 `+` 후 점선 사각형, 사각형 내부에 물음표."
- 조치: `shapeStepsFor(0)`이 `{groups:[{n:a,cls:'circle green'}],steps:[],extras:[{kind:'paint-op',text:'+'},{kind:'paint-slot',text:'?'}]}`를 낸다. 화면은 `● … ● + [?]`가 되어 `a + ? = 10`을 그림으로 읽는다. 연출(steps)이 없는 정지 화면이라 `#randomShapeSkip`도 띄우지 않는다.
  - **점선 칸은 개수와 무관하게 하나**다. 정답 개수(`10-a`)만큼 두면 그림이 답을 먼저 알려 준다.
  - `.paint-op`·`.paint-slot`은 `.paint-shape`가 아니므로 22번의 `::before/::after` 도형 그리기를 타지 않는다. 크기는 `#randomShapes` 안에서 104px로 도형과 맞췄다.
- 검증: headless 캡처 — `8 + 2 = 10` 문항에서 초록 ● 8개 + `+` + 점선 `?` = 10칸이 5열 2행으로 떨어진다. `a`가 4일 때도 정상(4칸 + 2칸).
- 주의: 예전 주석("보기 선택은 식이 3개라 도형으로 특정할 수 없다")은 **"그릴 수 없다"가 빈 자리를 정당화하지 못한다**는 판정으로 뒤집혔다. 나머지 문항이 전부 그림을 갖고 있으면 빈 자리는 누락으로 읽힌다.

## 49. `section_random_problems` 뺄셈도 덧셈처럼 항별 모양·색 구분

- 상태: 완료 (2026-08-03)
- 대상: `index.html` `shapeStepsFor`(`type 1`·`4`·`5`) / `playRandomShapeIntro`
- 사용자 지적: "덧셈과 같이 빼기도 모양과 색깔이 다르면 좋겠어."
- 조치: 뺄셈을 **[남는 것 / 첫 번째로 빼는 것 / 두 번째로 빼는 것]** 그룹으로 갈라 41-a와 같은 매핑(초록 ● / 파랑 ■ / 빨강 ▲)을 얹었다. `a - b - c` → `[{a-b-c, ●}, {b, ■}, {c, ▲}]`, `10 - c` → `[{10-c, ●}, {c, ■}]`.
  - `playRandomShapeIntro`를 함께 고쳤다. **(1) 초기 가시성을 `mode`로 가른다** — 덧셈은 첫 그룹만 보이고 나머지가 `pending`이지만 뺄셈은 처음부터 전부 보여야 한다(`a`개가 있다가 줄어드는 것이므로). **(2) 제거 대상을 그룹 번호로 지정한다** — 예전 `shapes[--cursorRemove]`는 배열 뒤에서부터 지워서 그룹 순서와 제거 순서가 맞물려야만 맞았다. 이제 `steps:[{op,group}]`이다.
- 검증: headless 캡처 — `15 - 5 - 5`가 초록 ● 5 + 파랑 ■ 5(지워짐) + 빨강 ▲ 5(지워짐)로, `10 - 8`이 초록 ● 2 + 파랑 ■ 8(지워짐)로 나온다.
- 주의: 이 비대칭은 **방향만 바꿔 두 번째로 나온 것**이다(2026-07-31에는 뺄셈에만 표시가 있고 덧셈에 없었다 — 20번). 한쪽을 고칠 때 짝을 함께 보지 않으면 비대칭이 자리만 옮긴다.

## 50. 페인트통 위에 얹은 2D 면이 통 그림과 안 어울린다

- 상태: 완료 (2026-08-03) — **`.paint-can::after` 색 면으로 확정**, 사용자 확인
- 대상: `index.html` `.paint-can::before`(신규)·`.paint-can::after` / `--can-face-clip`
- 사용자 지적: "페인트통에 모양을 둔 건 좋은데 이미지에 2D 모양을 올려두니 안 어울려. 좀 더 기울이거나 접어야 하지 않을까?"
- 조치: 39번의 정면 직사각형을 **원통에 감긴 띠**로 바꿨다.
  - **모양** — 위·아래 가장자리를 통 림과 같은 방향(가운데가 내려앉는 아치)으로 깎았다. `border-radius`로는 이 초승달을 만들 수 없어 %기반 `polygon`(`--can-face-clip`)으로 두 아치를 샘플링했다. %라서 통 크기 276/250/200에 전부 따라온다.
  - **테두리** — `clip-path`가 `border`를 잘라 없애므로 22번 `.paint-shape`와 같은 **2겹 기법**으로 바꿨다. `::before`가 선 색, `::after`가 채움이고 같은 clip을 쓰되 `::after`만 1% 안쪽이다.
  - **자리·명암** — 띠를 통 실루엣 가까이 넓히고(x 0.30~0.69 → **0.245~0.755**) 손잡이 고리 아래로 내렸다(y 0.38~0.65 → **0.43~0.68**). 가로 그라데이션으로 좌우 끝을 눌러 면이 말려 들어가게 하고 에셋 하이라이트 위치(왼쪽 1/3·오른쪽 3/4)에 밝은 띠를 맞췄다. `perspective(300px) rotateX(5deg)`.
- 검증: headless 캡처로 초록·빨강 통을 나란히 확인 — 띠가 통 실루엣에 닿고 위아래 아치와 좌우 명암으로 감긴 것으로 읽힌다.
- 주의: **아치의 처짐(띠 높이의 10%)은 에셋 림 타원 실측에서 나온 값**이다. 통 폭의 84%를 덮는 띠의 기하학적 처짐이 림 전체 처짐(≈캔 높이의 0.035)의 0.46배라, 이보다 키우면 오히려 어색해진다. "원통 위"라는 인상은 아치가 아니라 **가로 명암**이 만든다.
- 주의: 24번 교훈(정면 정투영 raster를 `rotateX`로 눕히지 않는다)과 충돌하지 않는다 — 이번 대상은 raster 사물이 아니라 통 **위에 그리는 CSS 면**이다. 각도는 5°로 최소화했다.

## 53. `section_random_problems` 힌트가 문제를 그대로 다시 보여주는 수준이다

- 상태: 완료 (2026-08-03)
- 대상: `index.html` `randomHintSteps`·`randomHintIndex` / `openRandomHint`·`closeRandomHint`·`flashRandomShapes` / `helpCharacter.onclick` / `judgeRandomChoice`·`judgeRandomKey` 오답 분기
- 사용자 지적: "힌트가 나가고 있는데 **문제를 그대로 보여주는 식**이야. 힌트를 어떻게 보여줄지도 생각해야 해."
- 조치: 힌트를 문자열 하나(`randomHint`)에서 **단계 배열**(`randomHintSteps=[{text,focus}]`)로 바꿨다. 예전에는 유형 B가 `10 - c = (   )`로 문제와 글자까지 같았고 유형 C·D는 첫 줄이 `a + b = 10`이라 답의 절반을 바로 공개해 **재진술 아니면 정답 공개** 둘뿐이었다.
  - **1단계는 시선 유도만** — 글은 무엇을 먼저 볼지만 말하고, `flashRandomShapes(focus)`가 해당 항의 도형을 `hint-step`으로 차례로 깜빡인다(씬2·3의 `hintCountShapes`·`hintArithmetic`과 같은 방식). 저학년이라 글보다 그림 강조가 먼저다.
  - **2단계에서만 중간식**(`a + b = 10`). 3단계는 두지 않았다 — 3회 오답의 정답 공개(`revealRandomAnswer`)가 그 역할이다.
  - 선생님을 누를 때마다 한 단계씩 열리고 마지막 단계에서 한 번 더 누르면 닫힌다(예전에는 `open` 토글뿐이라 몇 번을 눌러도 같은 글이었다). 오답 1회·2회에도 각각 1·2단계가 자동으로 열린다.
- 단계 문구: A `초록 ●를 세어 봐요.` → `${a}개에서 10까지 몇 개가 더 필요할까요?` / B·D-준비 `지워질 것을 세어 봐요.` → `남은 것을 세어 봐요.` / C `앞의 두 수를 먼저 더해 10을 만들어 봐요.` → `${a} + ${b} = 10` / D `앞에서부터 차례로 지워 봐요.` → `${a} - ${b} = 10`
- 검증: headless로 4문항을 오답 2회씩 내며 주파 — 1·2단계 문구가 위 표대로 나오고, 도형에 `hint-step`이 해당 그룹에만 붙는다(예: C의 1단계는 초록·파랑에만).
- 주의: 1단계 문구는 **원문(planner)에 없는 새 문구**다. 31·34번과 같이 production 사본에서는 사용자 지시가 원문 보존 계약보다 우선한다는 판단이다. 녹음이 없으므로 `speak()`를 걸지 않아 무음이다.
- 주의: 도형 강조는 49번이 항별 그룹을 만든 뒤라야 가능하다(`randomShapeGroups`). **49 → 53 순서 의존**이다.

## 54. 효과음(SFX) 적용 — `…723 효과음 스크립트.md`

- 상태: 완료 (2026-08-03)
- 조치: `tone(ok)`를 WebAudio 오실레이터 비프에서 **mp3 재생기로 교체**했다. `SFX_DIR='assets/audio/sfx/'` + `playSfx(name)`(호출마다 `new Audio`, `soundOn` 게이트, `.play().catch(()=>{})`)를 새로 두고 `tone(ok)={playSfx(ok?'answer-correct':'answer-wrong')}`으로 줄였다. 호출부 7곳은 손대지 않았다.
  `startIntroRepair`는 루프 안 `tone(true)`를 빼고 `hammer-hit`을 **연출당 한 번만** 예약한다(`HAMMER_HIT_OFFSET_MS-HAMMER_SFX_ONSET_MS` = 145ms 지연). 씬7은 `showScene`의 `section_completion` 분기에서 `SCENE_OVERLAP_MS` 뒤 `lesson-complete`을 낸다.
- 음원 4종 (Pixabay Content License — 저작자 표시 불필요·상업적 이용 가능. 재배포 자체가 목적인 사용만 금지라 콘텐츠 삽입은 문제없다)

  | 파일 | 쓰는 자리 | 원제 · 작가 | 길이 | 출처 |
  | --- | --- | --- | --- | --- |
  | `hammer-hit.mp3` | 씬1 담장 수리 | Hammer · freesound_community | 1.61s | <https://pixabay.com/sound-effects/household-hammer-37506/> |
  | `answer-wrong.mp3` | 오답 전부(`tone(false)`) | Marimba Game Over · Universfield | 2.83s | <https://pixabay.com/sound-effects/film-special-effects-marimba-game-over-250960/> |
  | `answer-correct.mp3` | 정답 전부(`tone(true)`) | Doorbell Ding Dong · DRAGON-STUDIO | 3.24s | <https://pixabay.com/sound-effects/household-doorbell-ding-dong-482879/> |
  | `lesson-complete.mp3` | 씬7 완료 | Level Complete · Universfield | 1.96s | <https://pixabay.com/sound-effects/film-special-effects-level-complete-143022/> |

- **원문의 `딩동`(씬2·3·7·8)과 `정답 효과음`(씬9)은 한 파일로 통일했다** — 사용자 결정 2026-08-03. 표현만 다른 같은 "맞았다" 신호이고, 나누면 저학년이 두 신호를 다른 것으로 읽을 위험이 있다.
- **`hammer-hit.mp3`는 파일 하나가 타격 4회를 담고 있다.** 실측 onset **35 / 490 / 910 / 1355ms**(간격 ≈420ms)로, 코드의 `HAMMER_STRIKES=4` × `HAMMER_SWING_MS=420`과 우연히 거의 같다. 그래서 타격마다 재생하는 A안(16번 울림)이 아니라 **통째로 1회 재생**으로 갔다. 145ms 지연을 걸면 화면 충돌(180 / 600 / 1020 / 1440ms)과의 오차가 **0 / +35 / +35 / +60ms**로 들어온다.
- 검증: headless Chrome에서 `HTMLMediaElement.prototype.play`를 가로채 실제 재생을 기록했다. 씬1 `hammer-hit` **1회**, 씬2 핫스팟 6개 클릭에 `answer-wrong` 3회 + `answer-correct` 2회, 씬7 `lesson-complete` 1회. 4개 파일 모두 200, JS 오류 0건.
- 주의: **`assets/audio/script/`(대사 녹음)와 폴더를 나눈 것은 45번 규칙 때문이다.** 그 폴더는 "파일명 = 대사 키"라 재녹음이 오면 같은 이름으로 덮어쓰는 자리다. 효과음을 섞으면 그 계약이 깨진다.
- 주의: **`HAMMER_STRIKES`나 `HAMMER_SWING_MS`를 바꾸면 `hammer-hit.mp3`의 박자와 어긋난다.** 코드만 고칠 수 없고 음원을 함께 갈아야 한다.
- 주의: Pixabay는 curl/WebFetch 기본 요청을 **403**으로 막는다. 다시 받으려면 브라우저 헤더 전체(`User-Agent` + `Accept` + `Accept-Language` + `Sec-Fetch-*` + `sec-ch-ua*`)를 붙여야 200이 온다.
- 미해결(사용자 판단 필요): `answer-correct.mp3`가 3.24초라 **정답 나레이션(`correct-1.wav` 등)과 겹친다.** 검증 로그에서 둘이 같은 순간(7869/7870ms)에 시작했다. 톤이 탁해 보이면 더 짧은 정답음으로 바꾸거나 나레이션을 늦춘다.

## 51. 각 씬 상단에 제목을 글자를 구운 이미지로 붙이기

- 상태: 완료 (2026-08-03) — **판까지 포함해 이미지 하나로 대체**, 사용자 결정("하나의 이미지로 가는거야")
- 대상: `index.html` `.title-image`(신규) / `#shapeTitleImage`·`#arithTitleSurface`·`#randomTitleImage`·`#drawingTitleImage`·`#storyTitleSurface` / 신규 에셋 5종 / `CLAUDE.md` 에셋 규칙
- 사용자 지적: "각 섹션에 제목을 이미지로 붙여 주면 좋겠어. 상단에 두고, **글과 이미지를 하나로 굽는** 형식으로."
- 조치:
  - **에셋 5장을 이미지 생성으로 만들었다**(`codex exec`). 문구는 `모양 찾기와 세기` / `세 수의 덧셈과 뺄셈` / `무작위 계산 문제` / `모양으로 그리기` / `수리 이야기`. 화풍 기준은 사용자가 준 `assets/reference/title-image-exemplar.png`(`100까지의 수`)와 `1-2/01/lesson.json`의 `artDirection`이고, 2장째부터는 **먼저 만든 타이틀을 참조로 함께 넣어** 세트로 보이게 했다.
  - 생성 캔버스의 여백이 장마다 달라 **알파 bbox까지 잘라 설치**했다(`tmp/titlegen/install_titles.py`). 자르지 않으면 `height`만 줬을 때 씬마다 글자 높이가 어긋난다. 설치 후 크기는 1068×258 ~ 1810×304, 비율 4.14~5.95다(글자 높이는 같고 글자 수만큼 가로가 길어진다). 씬3만 캔버스가 1860×320이고 나머지는 1240×300이다.
  - 마크업은 `.title-banner`(빈 판 `<img>` + `<h2 class="hero-title">`) → **`<img class="title-image">` 한 장**으로 바꿨다. 씬3·6은 **기존 id(`arithTitleSurface`·`storyTitleSurface`)를 그대로 유지**해 JS 여닫이(`arithIntroTap`·`resetStory`·`openStorySigns`)를 건드리지 않았다.
  - 씬2·4·5에는 제목 표면이 아예 없어 새로 넣었다.
- 자리(실측 기준, stage 좌표):

| 씬 | 요소 | 자리 | 근거 |
| --- | --- | --- | --- |
| 2 | `#shapeTitleImage` | x 122~727 / y **300~420** (칠판 위) | 상단 띠가 이미 꽉 찼다 — `.search-prompt`(y 90~215) · 삼각자(x 300~470 / y 95~265) · 벽시계(x 880~1070 / y 215~405). 비어 있는 면은 칠판(x 80~768 / y 240~660)뿐이고 공은 y 629~793이라 위쪽 절반이 완전히 빈다 |
| 3 | `#arithTitleSurface` | y **180~330** | 기존 배너 자리 그대로 |
| 4 | `#randomTitleImage` | y **58~198** | `#randomPanel`(top 205) 위 |
| 5 | `#drawingTitleImage` | y **63~202** | `#drawingSpeech`(y 220~377)·`#drawingCanvas`(top 320) 위 |
| 6 | `#storyTitleSurface` | y **205~355** | 기존 배너 자리. 44번의 빈 면(y 355~825)과 정확히 맞닿는다 |

- **씬2·4·5는 씬 내내 남고, 씬3·6은 도입에서만 보인다.** 후자는 기존 동작을 유지한 것이다 — 그 자리를 `.arith-context`(top 155)와 `.sign-row`(y 275~665)가 이어받기 때문에 남겨 두면 겹친다.
- 검증: headless 캡처 5장 + rect 실측. 다섯 자리 모두 위 표대로이고 다른 요소와 겹치지 않는다. 다섯 장이 같은 글자 높이·같은 화풍으로 보인다.
- 주의: **`세 수의 덧셈과 뺄셈`은 한 번 폐기하고 다시 만들었다.** 9자라 첫 시안이 글자를 캔버스 높이의 30%로 작게 그려 다른 넉 장과 크기가 어긋났다. 캔버스를 넓히고 "글자 높이 78% 이상 · 가로를 끝까지 쓴다 · 폐기 시안을 반례로 첨부"를 프롬프트에 넣어 해결했다. **글자 수가 많은 문구는 이 함정을 다시 만난다.** 또 하나 — codex는 실행 중 같은 경로에 **중간본을 먼저 쓰고 나중에 최종본으로 덮는다.** 파일이 생기자마자 설치했다가 2분 뒤 최종본(1860×320)이 따로 떨어져 다시 설치했다. **codex 프로세스가 끝난 뒤에 파일을 가져간다.**
- 주의: 씬7(`3차시 수리 완료!`)은 사용자 목록에 없어 **기존 `.title-banner`(빈 판 + HTML 텍스트) 구조를 유지**한다. `school-title-banner-body.png`는 이 한 곳에서만 쓰인다.
- 주의: 문구를 고치려면 **에셋을 다시 생성해야 한다.** 이 대가를 감수하는 예외임을 `CLAUDE.md` 에셋 규칙에 조항으로 넣었다("제목·로고류는 예외 — 가르는 기준은 텍스트냐가 아니라 변하느냐 고정이냐").

## 55. `section_random_problems` 제목·문제·보기가 너무 위에 있다

- 상태: 완료 (2026-08-03)
- 대상: `index.html` `#randomTitleImage`(top 58 → **118**) / `#randomPanel`(top 205 → **278**) / `shapeStepsFor`의 `type 0` extras
- 사용자 지적: "무작위 계산 문제에서는 title 이미지를 아래로 내리는데 **문제와 보기도 같이** 내려 줘. 너무 위에 있다."
- 원인: 배경 `school-wall-problem-scene.png`의 담장 면은 y **380~946**인데 제목(58~198)도 문제 작업표(205~425)도 그 **위 하늘 구간**에 떠 있었다. 도형(390~890)만 담장 위에 있어 좌우가 서로 다른 높이에서 시작했다.
- 조치: 제목 **+60**, 문제 판 **+73**. 제목 118~258 / 작업표 278~498 / 보기 510~864 / 키패드 518~932가 됐다.
  - **내릴 수 있는 한계는 키패드 유형이 정한다.** 입력기 바닥이 859였고 진행 막대(`#randomWorkProgress`)가 956에서 시작해 여유가 97px뿐이었다. 판을 담장 면 시작(390)까지 내리면 키패드가 1044까지 내려가 막대·무대 밖으로 나간다. 그래서 작업표가 하늘/담장 경계를 걸치는 자리가 최선이다(중심 388이 담장 윗선과 거의 같다).
  - 함께 고친 것(48번 후속): 5열 그리드라 `a`가 **4·9면 `+`가 줄 끝에 걸리고 `?` 칸만 다음 줄로 혼자 떨어져** 식이 끊겨 읽혔다. 그때만 빈 칸 하나를 앞세워 `+ ?`를 같은 줄로 민다.
- 검증: headless로 네 상태(보기·보기 정답·키패드·키패드 정답)를 실측 — 위 좌표대로이고 키패드 바닥 932가 진행 막대 956 위에서 끝난다. `a`를 1~9 전부 관측해 `+`와 `?`가 **9/9 같은 줄**임을 확인했다.
- 주의: 이 씬의 세로 여유는 이제 **24px**뿐이다(키패드 932 ↔ 막대 956). 작업표를 더 내리거나 키패드를 키우면 바로 부딪힌다. 41-c의 가로 제약(도형 x 374~984 / 패널 990~1560 / 인물 1569~)에 이어 세로도 포화 상태다.

## 56. `section_free_drawing` 제목 이미지도 아래로

- 상태: 완료 (2026-08-03)
- 대상: `index.html` `#drawingTitleImage`(top 62 → **110**) / `#drawingSpeech`(씬 전용 `top:270px` 신설)
- 사용자 지적: "모양으로 그리기 이미지도 약간 내려 줘."
- 조치: 제목 **+48**(y 110~250). 55번과 같은 이유다 — 담장 면이 y 308~877인데 제목만 상단 바 바로 아래(62~202)에 붙어 있었다.
  - **혼자서는 못 내렸다.** 도입 대사 말풍선(`#drawingSpeech`)이 공용 기본값 `.speech.right-speaker{top:220}`을 쓰고 x가 1158~1531이라 제목 오른쪽 끝(1280)과 겹친다. 말풍선의 z가 더 높아 제목만 내리면 **말풍선이 제목 끝글자를 덮는다.** 그래서 말풍선도 `#drawingSpeech{top:270px}`로 **이 씬만** 함께 내렸다(y 270~427, 제목과 20px 간격).
  - 씬별 오버라이드는 15번 규칙이 허용하는 범위다 — "씬별로 남겨도 되는 것은 **앵커 좌표와 꼬리 방향 변형**뿐". 폭·패딩은 건드리지 않았다.
  - 부수 효과로 앵커가 좋아졌다. 꼬리 중심이 298 → 348로 내려와 선생님 머리(알파 기준 y≈407~)에 더 가깝다. 예전에는 머리보다 한참 위를 가리켰다.
- 검증: headless로 **도입 대사 단계와 그리기 단계 둘 다** 실측 — 제목 110~250 / 말풍선 270~427(20px 간격), 그리기 단계에서는 도구판(x 38~349)·캔버스(y 320~860)와 겹치지 않는다. 두 단계는 애초에 같이 뜨지 않는다.
- 주의: `.speech.right-speaker{top:220}`은 `#introSpeech`·`#shapeSpeech`·`#arithSpeech` 등이 함께 쓰는 **공용 기본값**이다. 씬5만 내린 것이므로 다른 씬 말풍선을 옮길 때 이 값을 건드리면 안 된다.

## 59. 효과음 재선정 — 판정음을 단순한 것으로 + 시작하기 효과음 추가

- 상태: 완료 (2026-08-03)
- 조치: 54번이 고른 판정음 2종을 물리고 **실측 기준으로 다시 골랐다.** `playSfx`가 확장자를 조립하던 것을 `SFX_FILE` 맵으로 바꿔 **쓰는 효과음 5종이 한 표에 다 보이게** 했다. `시작하기` 버튼(`#introStart`)의 `onclick` 맨 앞에 `playSfx('intro-start')`를 붙였다.
- 음원 (Pixabay Content License — 저작자 표시 불필요·상업적 이용 가능)

  | 파일 | 쓰는 자리 | 원제 · 작가 | 파일 / 가청 | RMS | 출처 |
  | --- | --- | --- | --- | --- | --- |
  | `answer-correct.mp3` | 정답 전부(`tone(true)`) | Correct · DRAGON-STUDIO | 1.32s / 0.80s | −11.2dB | <https://pixabay.com/sound-effects/technology-correct-472358/> |
  | `answer-wrong.wav` | 오답 전부(`tone(false)`) | Training Program, Incorrect1 · freesound_community | 1.06s / 0.48s | −11.9dB | <https://pixabay.com/sound-effects/film-special-effects-training-program-incorrect1-88736/> |
  | `intro-start.mp3` | `시작하기` 클릭 | Sound Effect: Twinkle/Sparkle · ShidenBeatsMusic | 2.04s / 1.18s | −19.2dB | <https://pixabay.com/sound-effects/film-special-effects-sound-effect-twinklesparkle-115095/> |

  `hammer-hit.mp3`(씬1)·`lesson-complete.mp3`(씬7)는 54번 그대로다.

- **`answer-wrong`만 wav인 이유**: 원본이 peak **−14.6dB** / RMS **−25.5dB**로 다른 효과음보다 14dB 작아 사용자가 "좀 작다"고 지적했다. **4.8배(+13.6dB)** 증폭해 다시 구웠는데 이 환경에 mp3 인코더(ffmpeg/lame)가 없어 16-bit PCM wav로 냈다. 결과 peak −1.0dB / RMS −11.9dB로 **클리핑 0샘플**, 정답음(−11.2dB)과 0.7dB 차다. 파일은 21KB → 182KB.
  - 증폭 방법: 헤드리스 Chrome의 `OfflineAudioContext.decodeAudioData`로 디코드 → 샘플에 게인 곱 → wav 헤더 직접 조립 → POST로 회수. 스크립트는 세션 scratchpad에 있었고 재현하려면 같은 방식을 다시 짜야 한다. **ffmpeg가 생기면 `ffmpeg -i in.mp3 -filter:a "volume=4.8" out.mp3` 한 줄로 끝난다.**
- 판정음 선택 기준(54번 실패에서 나온 것): **가청 1초 이하 · 단일 신호 · 서사 없음.** 54번의 `Doorbell Ding Dong`은 3.24초(가청 2.70초)에 초인종이라는 서사가 있어 한 문제에 여러 번 나는 자리에 과했다. 이번 정답음은 가청 **0.80초**로 **1/3.4**다.
- 삭제: `answer-wrong.mp3`(Marimba Game Over, 54번). 교체로 참조가 0이 됐다. **`assets/audio/sfx/`의 남은 5개는 전부 `SFX_FILE`에 물려 있다**(전수 감사 완료).
- 검증: headless Chrome에서 `HTMLMediaElement.prototype.play`를 가로채 실제 재생을 기록 — `시작하기` 클릭 0ms에 `intro-start.mp3`, 씬1 `hammer-hit.mp3` 1회, 씬2 핫스팟 6개에 `answer-wrong.wav` 3회 + `answer-correct.mp3` 2회, 씬7 `lesson-complete.mp3` 1회. 5개 파일 모두 200, JS 오류 0건. 레벨은 디코드해서 peak/RMS로 재검증했다.
- 주의: **효과음을 추가·교체하면 `SFX_FILE` 맵부터 고친다.** `playSfx`는 이제 맵에 없는 이름을 받으면 조용히 `null`을 낸다(무음). 오타가 나도 에러가 안 나므로 맵과 호출 이름을 함께 본다.
- 주의: **Pixabay 표시 길이(0:01 등)는 반올림이라 믿지 않는다.** 54번에서 "0:01" 파일이 실제 1.61초에 타격 4회였고, 이번에도 "0:01"짜리들이 실제 1.0~1.9초였다. 받아서 디코드해 재는 것이 유일하게 맞는 방법이다.
- 미해결: `assets/add_audio/`가 빈 폴더로 남아 있다(이번 작업 이전부터). 지울지는 확인이 필요하다.

## 57. 아이가 말할 때 말풍선이 너무 위에 있다

- 상태: 완료 (2026-08-03)
- 조치: `.speech`의 세로 앵커를 **씬 기준값 + 아이 보정** 두 항의 합으로 바꿨다 — `.speech{--speech-anchor-top:220px}`를 두고 `.speech.left-speaker`·`.right-speaker`의 `top`을 `calc(var(--speech-anchor-top) + var(--speech-child-drop,0px))`로 적었다. 38번이 만든 인접 형제 선택자 두 줄에 `--speech-child-drop:205px`를 더했다(가로 `left:280px`/`right:250px`는 그대로).
- 조치: 씬별 오버라이드 `#arithSpeech{top:350px}`·`#drawingSpeech{top:270px}`를 `--speech-anchor-top` 선언으로 바꿨다. **이게 이 항목의 핵심이다** — ID 선택자(1,0,0)가 형제 선택자(0,5,0)를 이겨, `top`으로 두면 씬3에서만 아이 보정이 통째로 죽는다. 기준값만 바꾸는 형태라 씬 오버라이드가 아이 보정을 모르고도 함께 동작한다.
- 205px의 근거: 애니메이션을 끈 상태에서 `object-fit:contain` 후 알파 bbox로 머리 꼭대기를 실측했다. 어른 `worker-explaining` 440 · `teacher-explaining` 434, 아이 `student-thinking` 646 · `student-volunteer` 643 · `student-idle` 640 → 차이 200~209px의 중간값.
- 검증: headless Chrome 1920×1080 실측. 보정 뒤 "꼬리 y − 머리 y"가 씬1·2에서 아이 −136~−142 / 어른 −135로 맞물리고, 씬3(기준값 350)에서도 아이 −9~−12 / 어른 −11로 맞물린다. 아이 beat 최장 대사에서도 말풍선 아래가 무대(1080)를 넘지 않는다(씬1·2 425~582, 씬3 555~712). 씬1·2·3 캡처 육안 확인.
- 주의: 앞으로 **씬별 말풍선 오버라이드에 `top`을 직접 쓰지 않는다.** `--speech-anchor-top`만 준다. `top`을 쓰면 아이 보정이 그 씬에서만 사라지고, 증상이 씬 하나에서만 나와 찾기 어렵다.
- 주의: 씬3의 아이 beat는 todo 57번이 적어 둔 세 자리 말고도 `q_add_10_2`의 `preBeats`(`페인트 1통을 다 썼어요` = `student-thinking`.left, `네` = `student-idle`.right)가 있다. 기준값 방식이라 함께 보정됐다.
- 주의: `#feedbackSpeech`도 `.left-speaker`를 갖지만 `.speech.feedback-speech{top:470px}`가 소스 순서로 뒤에 와서 이긴다 — 27번 좌표 그대로다. `#helpCard`(`top:auto`)·`#arithContext`(화자 클래스 없음)도 영향 없다.

## 58. 다음 섹션 CTA가 뜰 때 대화창이 화면에 그대로 남는다

- 상태: 완료 (2026-08-03)
- 조치: 세 자리에서 `clearAdvanceNav(대사표면)`을 **대사 표면을 통째로 `hidden`으로 내리는 것**으로 바꿨다. 씬1 `introTap.onclick` 마지막 분기는 `#introCharacter`·`#introSpeech`를, 씬3 `arithIntroTap.onclick`의 `arithPhase==='outro'`는 `#arithCharacter`·`#arithSpeech`를 각각 내린다(둘 다 인물과 말풍선이 형제로 흩어져 있다). 씬2 `shapeDialogueTap.onclick`의 `shapePhase==='outro'`는 래퍼 `#shapeDialogue` 하나만 내리면 된다. 탭 레이어는 종전대로 함께 내린다.
- 조치: 참조가 0이 된 `clearAdvanceNav`를 제거했다. 그 자리에 35번을 58번이 대체했다는 것과 새 규칙("단계가 끝나 다음 표면이 뜨면 이전 단계의 표면은 내린다")을 주석으로 남겼다. `ensureAdvanceNav`는 `bindDialogueSurface`가 계속 쓰므로 그대로다.
- 정본: 씬5 `drawingTap.onclick`(`#drawingDialogue`를 내리고 `#drawingDone`을 띄운다). 새 씬을 만들 때 이 형태를 따른다.
- 검증: headless Chrome으로 씬1·2·3을 실제 조작(대사 탭 · 핫스팟 클릭 · 키패드 입력)으로 CTA까지 진행해 확인 — 세 곳 모두 CTA만 보이고 인물·말풍선·탭 레이어는 전부 안 보인다. 씬5(정본)와 같은 상태다.
- 검증(재진입): 씬을 나갔다 다시 들어오면 대사가 되살아난다. `resetIntro`(`ch.className='character left hidden'` → `renderIntro`가 되돌림) · `resetShapeScene`(`#shapeDialogue` `hidden` 제거) · `resetArithmetic`(`ch.classList.remove('hidden')` + 지연 후 `sp`)이 각각 처리한다. 실측으로 세 씬 모두 확인했다.
- 주의: 35번은 이 항목으로 **대체됐다.** `다음 ▸`만 빼고 표면을 남기는 처리는 이제 이 문서 어디에도 없다.

## 60. `정답입니다`는 내레이션인데 캐릭터가 나와서 말한다

- 상태: 완료 (2026-08-03)
- 결정: **B안(도장 + 음성만)** — 2026-08-03 사용자 선택. 말풍선도 캐릭터도 없애고 진행 표면을 따로 옮겼다.
- 조치: `showFeedback(el,text,onContinue,voice)`에 다섯 번째 인자 `speaker`(기본 `'narration'`)를 더했다. `speaker==='teacher'`이고 텍스트가 있을 때만 `#feedbackCharacter`+`#feedbackSpeech`를 띄운다. 원문 `…723 음성 스크립트.md`에서 **교사** 대사인 씬2-3 `잘 찾았어요!`(`q_triangle_find_two`)만 `'teacher'`로 부르고, **내레이션**인 `정답입니다.` 3곳(씬2 찾기·씬2 세기·씬3 산술)은 기본값 그대로 둔다.
- 조치: 내레이션에서 말풍선을 없애면 17·26번이 세운 유일한 진행 표면이 사라지므로 **`#narrationAdvance`(`.narration-advance`)를 새로 만들어 진행을 옮겼다.** 배경·테두리·꼬리가 없고 `다음 ▸` 버튼만 담는다(꼬리를 두면 없는 화자를 가리킨다). 도장(`.feedback-mark`, y 398~638) 바로 아래 `top:652px` 중앙이다.
- 조치: `showStamp(el,type,hold)`에 `hold`를 더했다. 내레이션 정답은 도장이 화면에 남는 유일한 결과 신호라 0.7초 뒤 지우지 않고 **진행을 누를 때까지 띄워 둔다.** 띄워 둔 도장은 `heldStamp`로 들고 있다가 `resetFeedbackOverlay`가 걷는다.
- 조치: `resetFeedbackOverlay`가 `#narrationAdvance`(가시성·`innerHTML`·핸들러)와 `heldStamp`를 함께 되돌린다. `showScene`이 이 함수를 부르므로 씬을 옮겨도 남지 않는다.
- 조치: 씬4의 `showFeedback(#randomMark,'')` 2곳(`judgeRandomChoice`·`judgeRandomKey`)은 텍스트가 없어 자동으로 내레이션 경로를 타고, **대사도 없이 인물만 0.7초 번쩍이던 것이 사라졌다.** 이 씬의 진행은 47번이 만든 `#randomSolved`가 그대로 맡는다.
- 검증: headless Chrome 1920×1080에서 실제 조작으로 다섯 자리를 확인했다. 씬2 찾기 `정답입니다`·씬2 세기·씬3 산술 → 캐릭터 false / 말풍선 false / 진행바 true(x 928~992, 중앙 960) / 도장 유지 true. 씬2 삼각형 `잘 찾았어요!` → 캐릭터 true + 말풍선 true. 씬4 정답 → 캐릭터 false + `#randomSolved` true(진행 경로 유지). 캡처 4장 육안 확인.
- 주의: `.narration-advance`의 가운데 정렬에 **`transform:translateX(-50%)`를 쓰지 않는다.** `animation:speechPop`의 키프레임이 `transform:scale()`로 이를 덮어써 중심이 절반 폭만큼 오른쪽으로 밀린다(처음에 그렇게 짰다가 x 992~1055로 어긋났다). `left/right:0` + `width:max-content` + `margin:0 auto`로 잡는다.
- 주의: 23번의 `sceneStudentVisible()` → `setSceneStudentPose('volunteer')`는 **무대에 이미 서 있는 아이의 포즈 교체**라 "캐릭터를 새로 띄우는 것"이 아니다. 이 항목의 대상이 아니므로 그대로 뒀다.
- 미해결(규칙): 규칙화된 `[feedback-as-character-bubble]`(`prompts/builder_system.md`의 channel 렌더링 계약)에 **"원문이 내레이션으로 지정한 대사는 화자를 세우지 않는다"** 예외를 넣을지는 사용자 결정이 남았다. todo.md "확인이 필요한 항목 정리" 참조.

## 61. `section_arithmetic_tutorial` 제목을 문제 푸는 내내 유지

- 상태: 완료 (2026-08-03)
- 지시(2026-08-03): "세 수의 덧셈과 뺄셈 타이틀 … **문제 풀 때 계속 유지하기**" / (뺄셈 문항에 대해서도) "**+ 타이틀 유지**".
- 조치: `arithIntroTap.onclick`의 intro 마지막 분기에서 `#arithTitleSurface`에 `hidden`을 붙이던 한 줄을 뺐다. 인물·말풍선·탭 레이어를 내리는 것은 그대로다. `resetArithmetic`이 이미 `classList.remove('hidden')`을 하고 있어 재진입도 그대로 돈다.
- 조치: `#arithTitleSurface`를 `top:180px → 95px`로 **85px 올렸다.** 제목이 문항 내내 남으면 오른쪽 끝(x 1407)이 키패드 판(`.keypad-wrap`, x 1305~ · y 245~)과 겹쳐 **제목 끝글자 `셈`과 문제 문구 첫 글자 `모`가 서로를 가린다.** 바닥을 245로 맞춰 판 윗선과 맞닿게 하니 겹침이 0이 됐다. **가로(중심 960)와 height 150은 그대로** — 사용자가 "가로는 그대로"로 확정했다.
- 왜 예전엔 숨겼나: 51번이 "씬3·6은 도입에서만 보인다"로 잡은 이유는 학습 설계가 아니라 **그 자리(top 180)를 `.arith-context`(top 155, 풀이 말풍선)가 이어받기 때문**이었다. 62번으로 그 요소가 없어져 자리 다툼 자체가 사라졌다. 씬6은 `.sign-row`(y 275~665)가 실제로 그 자리를 쓰므로 **종전대로 도입에서만 보인다.**
- 검증: headless Chrome 1920×1080 실측. 인트로·덧셈 문항·뺄셈 문항·정답 직후 네 상태 모두 제목 y 95~245 / x 513~1407로 떠 있고 키패드(y 245~)와 겹침 0. 캡처 육안 확인.
- 주의: **제목 height를 키우면 다시 겹친다.** `#arithTitleSurface`의 세로는 키패드 판 `top:245`와 한 쌍으로 본다. z-index로는 풀 수 없다 — 어느 쪽을 올려도 반대쪽이 가려진다(실제로 `calc(var(--z-interactive) + 1)`을 넣어 봤다가 문제 문구가 가려져 되돌렸다).

## 62. `7 + 3 = 10 / 10 + 2 = 12` 풀이 말풍선 제거

- 상태: 완료 (2026-08-03)
- 지시(2026-08-03): "세 수의 덧셈에서 `7+3+2` 맞추면 나오는 `7+3=10`, `10+2=12` **말풍선 없애기**". 범위는 사용자 결정으로 **정답·오답 모두**(아예 제거).
- 조치: `showArithmeticReason` 함수와 호출 3곳(정답 분기 · `arithWrong===2` · `arithWrong>=3`)을 지웠다. `#arithContext` 요소와 `.arith-context` CSS, `arithmeticQuestions`의 `strategy` 필드 2개(`q_add_7_3_2` · `q_subtract_12_2_3`), `resetArithmetic`·`renderArithmetic`·`startArithmeticQuestion`·`finishArithmetic`의 `arithContext` 숨김 호출 4곳도 함께 걷었다.
- 원문 계약: `7 + 3 = 10` 등 `strategy` 문구는 `dfbc1027_planner.json`·`dfbc1027_input.json` 어디에도 없다(grep 0건). **원문에 없던 보조 문구**라 지워도 원문 보존 계약에 걸리지 않는다. todo의 "녹음 공백" 표에서도 `✗ 원문에 없음`으로 잡혀 있던 항목이다.
- 남는 오답 단서: `hintArithmetic`(해당 도형 깜빡임)과 3회 오답 시 정답 공개(`answer-reveal` + `setKeypadConfirmOnly`)가 그대로다. 즉 **단서가 0이 된 것이 아니라 텍스트 풀이만 빠졌다.**
- 검증: 7+3+2 정답 직후 `#arithContext` 부재, 화면에는 도장 + `다음 ▸`만. headless 실측 + 캡처 확인.
- 주의: `.speech`를 공유하는 요소가 7개 → **6개**가 됐다(`#introSpeech`·`#shapeSpeech`·`#arithSpeech`·`#drawingSpeech`·`#feedbackSpeech`·`#helpCard`). 60번의 `#narrationAdvance`는 `.speech`가 아니다.

## 63. 담장이 바뀐 뺄셈 문항에서 도형 위치를 아래로

- 상태: 완료 (2026-08-03)
- 지시(2026-08-03): "튜토리얼에서 **담장 바뀌었을 때 모양이 나오는 위치 약간 아래로** 내려주기".
- 조치: `renderArithmetic`이 배경을 바꿀 때 `#arithShapes`에 `data-wall`(`second` | `closeup`)을 함께 세우고, CSS에 `#arithShapes[data-wall="second"]{top:416px}`를 더했다(공용 `.work-area{top:354px}`에서 **+62**). 뺄셈 3문항(`q_subtract_12_2` · `q_subtract_10_3` · `q_subtract_12_2_3`)만 해당한다.
- 62px의 근거: 두 배경의 작업 면이 다르다 — `school-wall-closeup` y 367~878, `school-wall-second` y **364~990**으로 112px 더 길다. 최대 행수(12개 = 3행, 높이 ≈ 470)를 그 면 한가운데에 놓으면 y 442~912이고, 도형 시작 380 → 442라 +62다.
- 검증: 뺄셈 문항 실측 도형 y **442~928**(이전 380~850), 박스 `#arithShapes` y 416~986으로 담장 면(364~990) 안. 덧셈 문항은 y 380 그대로. 캡처 육안 확인.
- 주의: **개수로 다시 계산하지 않는다.** 46번대로 앵커는 고정이라 10개(2행)인 `q_subtract_10_3`도 첫 줄 y가 442로 같다. `align-content:center`로 되돌리면 46번이 재발한다.
- 주의: 공용 `.work-area{top:354px}`는 건드리지 않았다 — 씬2 `#countShapes`가 같이 쓴다.

## 2026-08-04

## 64. 씬2에서 담장으로 배경이 바뀌면 제목 이미지가 좌측으로 치우쳐 도형을 가린다

- 상태: 완료 (2026-08-04)
- 지시(2026-08-04): "모양 찾기와 세기에서 담장으로 배경이 넘어가면 `모양 찾기와 세기` 이미지 위치가 좌측으로 치우쳐져 있어 모양을 가려 — **배경을 넘어갔을 때만 중앙 위쪽**에 타이틀 이미지를 두자".
- 원인: 51번이 잡은 `#shapeTitleImage{left:424px;top:300px}`은 **교실 배경의 칠판 면(x 80~768 / y 240~660)에 맞춘 좌표**다. 씬2는 `startPaintIntro`에서 배경만 담장(`school-wall-closeup`)으로 바꾸고 제목 좌표는 그대로 둬, 담장 작업 면 위 도형과 자리가 겹쳤다. 수정 전 실측: 제목 x 121~727 · y 300~420, 세기 단계 도형 4칸(y 380~530) 중 **왼쪽 3칸이 40px씩 가려졌다**(x 겹침 150·150·127).
- 조치: CSS에 `#shapeTitleImage.on-wall{left:50%;top:80px}`을 더하고, 배경을 바꾸는 `startPaintIntro`에서 `.on-wall`을 붙이고 `resetShapeScene`(교실로 되돌리는 유일한 곳)에서 뗀다. **배경 전환과 같은 지점에서 좌표도 함께 바꾼다**는 것이 요점이다.
- 크기를 안 바꾼 이유: 씬3(`#arithTitleSurface`)처럼 `height:150`으로 맞춰 보니 폭이 605 → 756이 되어 교사 말풍선(x 1003~1530 / y 220~320)과 **335×25 겹쳤다**(실측). `height:120` · `max-width:620`(51번 값)을 그대로 두면 폭 605라 겹침이 사라지고, 배경만 바뀌는데 제목 크기까지 변하지도 않는다.
- top:80의 근거: 상단 바(바닥 56)와 24px, 교사 말풍선 윗선(220)과 20px 뜬다. 담장 면은 y 367부터라 제목은 하늘 영역에만 놓인다.
- 검증: headless Chrome 1920×1080에서 **실제 조작으로** 진행(대사 탭 → 핫스팟 2개 × 3문항 → 피드백 진행)해 배경이 바뀌는 순간 `.on-wall`이 붙고 제목이 x 657 · y 80으로 옮겨지는 것을 확인했다. 담장 두 단계(페인트 소개 · 세기) 모두에서 제목 ↔ 도형 / 말풍선 / 키패드 판 겹침 **0**, 다른 씬으로 나갔다 재진입하면 교실 좌표(x 121 · y 300)로 복귀. JS 오류 0.
- 주의: 담장 배경을 쓰는 지점이 늘어나면(`school-wall-second` 등) `.on-wall`을 붙이는 곳도 함께 본다. 지금 담장 전환은 `startPaintIntro` 한 곳뿐이고, 되돌리는 곳은 `resetShapeScene` 한 곳뿐이다.
- 주의: 교실 좌표(`#shapeTitleImage`)와 담장 좌표(`.on-wall`)는 **각각 다른 배경에 맞춰 잰 값**이다. 한쪽을 옮길 때 다른 쪽을 따라 옮기지 않는다.

## 65. 무작위 계산 문제에서 다이얼(키패드) 버튼 일부가 안 눌린다

- 상태: 완료 (2026-08-04)
- 지시(2026-08-04): "무작위 계산 문제에서 가리키는 손가락 모양 때문인지 다이얼 버튼 일부가 안눌리는 문제 발생".
- 원인: **손가락이 아니라 선생님 이미지다.** `.finger-hint`는 `pointer-events:none`이고 박스도 x 1541~1721로 키패드 밖이라 무관하다. `.help-character`(`right:10;width:500` → 박스 x **1411~1911**, `--z-character`=12)가 `#randomPanel`(`.panel`, `--z-content`=10)보다 위에 있어 **키패드 3열(`3`·`6`·`9`·`확인`, x 1358~1496)의 오른쪽 절반**을 덮었다. 그 면은 인물 알파가 0(실제 알파 bbox x **1570**~1821)이라 화면에는 안 보이지만, `<img>`의 히트 영역은 알파가 아니라 **요소 박스**라 클릭을 그대로 먹는다. 증상은 두 가지로 나타난다 — 오른쪽 절반을 누르면 아무 반응이 없거나(키가 안 먹음), 힌트 말풍선이 열린다(선생님이 눌림).
- 조치: `.help-character`에 `clip-path:inset(0 0 0 30%)`. `clip-path`는 그리기와 히트 영역을 함께 자르므로 **보이는 그림은 그대로 두고 판정만** 인물 위로 좁힌다. 30%(= x 1561)는 알파 왼쪽 경계 31.8%보다 바깥이라 그림이 안 잘리고, 키패드 오른쪽 끝 1496보다 안쪽이라 겹침이 사라진다. 알파 bbox는 `teacher-explaining.webp`(1024×1536)를 500×650 박스에 `object-fit:contain`한 기준으로 실측했다(박스 비율 x 0.318~0.819 / y 0.047~0.947).
- 검증: `tmp/hit-s4.js`·`tmp/verify65-67.js` — headless Chrome 1920×1080에서 키 12개의 **좌·중·우 세 점에 `document.elementFromPoint`** 를 찍었다. 수정 전 3열 4키의 중앙·오른쪽이 전부 `img#helpCharacter`, 수정 후 12키 36점 전부 자기 자신(`button.key`). 선생님은 x 1700에서 여전히 눌린다(힌트 정상 동작 확인).
- 주의: 이 결함은 **캡처로는 절대 안 잡힌다** — 화면에 아무 이상이 없다. 인터랙티브 요소 위에 투명 여백이 큰 이미지가 겹치면 `elementFromPoint` 히트 테스트로 확인한다.
- 주의: todo.md "캐릭터 알파 bbox" 표는 이제 **정렬용이자 히트 영역용**이다. 인물 좌표·크기를 바꾸면 `clip-path`의 30%도 함께 다시 잰다.

## 66. 무작위 계산 문제 힌트에 `힌트` 글자 추가

- 상태: 완료 (2026-08-04)
- 지시(2026-08-04): "무작위 계산 문제에서 가리키는 이미지만 있으니 힌트인지 모르겠다. 힌트라고 글자가 필요할듯".
- 원인: 42-a·b의 `.finger-hint`는 **어디를 누르라**까지만 말하고 **누르면 무엇이 나오는지**는 말하지 않는다. 탭 애니메이션까지 있어도 아이콘만으로는 기능이 안 읽힌다.
- 조치: `#fingerHintLabel`(`힌트` 필 라벨)을 손가락의 **형제 요소**로 추가했다. 자식으로 넣지 않은 이유는 `.finger-hint`가 `--finger-base:scaleX(-1)`로 뒤집혀 있어 글자까지 뒤집히기 때문이고, `::after`를 못 쓴 이유는 `<img>`라서다. 스타일은 말풍선 토큰을 그대로 쓴다(`--bubble-bg` / `--bubble-line` 5px / `--r-pill` / `--fs-sm`).
- 자리: `right:200px;bottom:125px;width:180px` → stage **x 1541~1721 · y 888~955**. 손가락 박스(x 1541~1721 · y 693~873) 바로 아래 같은 세로축이고, 키패드(오른쪽 끝 1496)·진행 막대(x 732~1188 / y 956~)와 겹치지 않는다.
- 여닫이: `showFingerHint()` / `hideFingerHint()` 한 쌍으로 묶었다. 여닫는 곳이 `renderRandom`(매 문제 다시 띄움 + 탭 애니메이션 재시작) · `armRandomContinue`(정답) · `helpCharacter.onclick`(힌트 열기) **세 곳**이라, 한 곳만 고치면 손가락은 사라지고 라벨만 남는다.
- 검증: headless Chrome 1920×1080 — 문제1(보기)·문제2(키패드) 진입 시 손가락·라벨이 함께 뜨고, 선생님을 누르면 **둘 다 함께** 사라지며 힌트 말풍선이 열리는 것을 확인했다. 라벨 박스 실측 x 1541~1721 / y 888~955로 겹침 0.

## 67. 무작위 계산 문제 모양 위치를 약간 아래로

- 상태: 완료 (2026-08-04)
- 지시(2026-08-04): "무작위 계산 문제에서 모양 위치 약간 아래로 내리기".
- 원인: `#randomShapes{top:390px}`는 담장 면(y **380~946**) 안에는 있었지만, 패딩 16을 더한 첫 줄이 y 406이라 **상단 캡에 붙어** 있었다. 아래는 최대 개수에서도 남았다 — 55·63번이 "면 안에 넣는 것"까지만 보고 **면 안에서의 여백 배분**을 안 본 자리다.
- 조치: `#randomShapes{top:390px → 420px}`. 짝인 `#randomShapeSkip`(건너뛰기 레이어)도 같은 값으로 함께 옮겼다 — 29번대로 이 둘은 **항상 같은 좌표**다.
- 폭의 근거: 최대 개수는 D 유형의 `subtract.a`= 19개(5열 4행)다. 행 간격이 116px(도형 104 + gap 12)이므로 첫 줄 y 436 → 4행 바닥 **888**로 면(946)까지 58px 남는다. 46번대로 앵커는 위 고정(`align-content:start`)이라 개수가 줄어도 첫 줄은 y 436 그대로다.
- 검증: `tmp/verify67-max.js` — headless Chrome 1920×1080에서 `Math.random` 첫 3회를 고정해 **최악의 경우(19개)** 를 만들고 4문항을 실제로 풀어 통과했다. 문항별 실측: 9개·10개(2행) 436~656, 19개(4행) 436~**888**. 전부 면 안이고 첫 줄 y는 네 문항 모두 436으로 동일.

## 68. 인증서를 1-2/01과 같은 형태로 교체 + 버튼 2단계화

- 상태: 완료 (2026-08-04)
- 지시(2026-08-04): "인증서 다운로드를 `production/1-2/01`과 똑같은 형태의 인증서로 받고 싶다. 버튼을 `인증서 보기` → `인증서 다운로드` 2단계로 나누고, 문구는 해당 차시 이름으로 바꿔라. **효과음은 필요 없다**."
- 종전: `#certificateButton`이 `<h1>3차시 수리 완료!</h1>` 한 줄짜리 HTML blob을 내려주는 임시 구현이었다.
- 조치: 01의 `repairCertConfig` / `openRepairCertificate` / `popRepairCertStar` / `downloadRepairCertificate`(01 `index.html:4531~4659`)와 `.repair-cert-*` CSS를 이식했다. 08 이름은 `CERT` / `openCertificate` / `popCertStar` / `downloadCertificate`이고 클래스명은 01 그대로 뒀다(두 차시를 같은 이름으로 찾을 수 있어야 한다). 캔버스에 상장 바탕 webp를 깔고 제목·부제·이름·본문 3줄·날짜·푸터를 그려 PNG로 내려준다.
- 버튼 2단계: 완료 씬 `#certificateButton`을 **`인증서 보기`**로 바꾸고(라벨만 변경, `data-interaction-id`의 `interaction_certificate_download`는 계약이라 유지), 실제 저장은 오버레이 안 `#repairCertDl`(**`인증서 다운로드`**)이 한다. 이름 입력에서 Enter로도 저장된다.
- 문구: 01의 `lesson.json` → `L.reward.certificate` 경로가 08엔 없으므로 `COURSE_MENU`처럼 **index.html 내부 상수 `CERT`** 로 박았다. 8차시 이름으로 `subtitle:'학교 담장 편'`, `body`의 2번째 줄 `학교 담장 곳곳의 수를 척척 수리하였기에`, `footer:'수리력 웹콘텐츠 · 알록달록, 학교 담장 색칠하기'`. **차시 번호는 인증서 어디에도 넣지 않았다** — 완료 배너는 원문 보존으로 `3차시 수리 완료!`인데 폴더·`COURSE_MENU`는 8차시라 숫자를 쓰면 어느 쪽을 써도 어긋난다.
- 효과음: 01은 `button-select`·`confetti`를 냈지만 지시대로 **전부 뺐다**(08 `SFX_FILE`에 그 키도 없다). 별 튀는 연출(`popCertStar`)은 시각 효과만 남겼다.
- 01 코드를 그대로 못 쓴 4곳: ① `esc` → `escapeHtml`, ② `later(fn,ms)` → `setTimeout`, ③ 마운트가 `#app` → **`#stage`**, ④ 저장 버튼의 `.cta clear-next-cta`. ④가 특히 조용한 함정이다 — 08의 `.cta`는 **완료 씬 전용 이미지 버튼**(380×150 · `completion-cta-body.webp` 배경)이라 그대로 얹으면 카드 안 버튼이 담장 그림으로 바뀐다. `.repair-cert-dl`을 01 `.cta`+`.clear-next-cta` 실효값(1366 기준)에서 자립시켰다.
- 치수: cqw/cqh 선언은 그대로 두고(15번 규칙 — `#stage`가 `container-type:size`라 자동 환산) **px 리터럴만 ×1.4056** 했다. 01의 `@media (max-height:480px)` 축소 보정은 뺐다 — 08은 `#viewport`가 무대째 축소되므로 뷰포트 높이로 카드만 따로 줄이면 무대 안에서 크기가 튄다.
- 상장 바탕은 01과 같은 webp를 **`CERT_BASE` data: URI로 인라인**했다(82,011자, index.html 236KB → 301KB). `assets/` 파일로 빼면 `file://`에서 캔버스가 tainted 되어 `toDataURL`이 SecurityError를 던지고 저장이 통째로 실패한다. 바탕에 글자가 굽혀 있지 않아 문구를 바꿔도 에셋 재생성은 필요 없다.
- 검증: `tmp/verify68.js` — headless Chrome 1920×1080에서 씬7 진입 → `인증서 보기` 클릭 → 오버레이 열림 확인 → 이름 `홍길동` 입력 → `인증서 다운로드` 클릭까지 실제로 돌렸다. 카드 실측 x 566~1353 / y 244~696으로 무대 안, 저장 버튼 661×107이 카드 안에 들어가고 `elementFromPoint` 중심이 `button#repairCertDl`(막힘 0). 내려받은 파일명 `수리인증서_홍길동.png`, PNG 727KB를 실제로 열어 문구·이름·날짜·푸터가 Jua로 제대로 구워진 것을 눈으로 확인했다. `tmp/smoke-all.js`로 7씬 전수 재확인 — 런타임 오류 0건 / 중복 id 0건.
- 주의: 캔버스는 CSS를 안 타므로 서체를 `FONT` 문자열로 따로 준다. 웹폰트가 늦으면 폴백으로 굳어 버려 `document.fonts.load('700 80px "Jua"')`를 기다린 뒤 그린다. 서체를 바꾸면 `--font-body`와 이 상수 **둘 다** 고쳐야 한다.

## 69. 모양 찾기 첫 문항에 "한 번 눌러 보기" 튜토리얼

- 상태: 완료 (2026-08-04)
- 지적: "모양 찾기와 세기에서 처음에 `네모 모양을 찾아봅시다`로 시작하면 1학년이 클릭을 이해 못할 수도 있을 것 같다. 처음에는 프롬프트가 나오고 클릭 한 번 해보라고 튜토리얼을 주는 게 어떤가." → 손가락으로 가리키되 **손가락이 움직여서 돋보이게** (2026-08-04 사용자 지시).
- 진단: 씬1~씬2 오프닝까지 `.tap-layer`(`inset:142px 0 0`)가 화면 전체를 덮어 **"아무 데나 탭 = 진행"** 을 6~7회 학습시킨다. 찾기 단계에서 이 규칙이 처음으로 **"정확한 대상 탭 = 정답 / 그 외 = 오답"** 으로 뒤집히는데 전환을 알리는 신호가 없다. `.hotspot`은 투명이고 `glow-hover`는 `pointerenter`라 터치에서는 누른 뒤에나 켜진다. 결과적으로 **아이의 첫 탐색 탭이 곧 첫 오답**(`registerSearchWrong`)이다. 기존 스캐폴딩(오답 2회 → `glow-hint`, 3회 → 번호 + 나머지 `disabled`)은 전부 실패 후행이라 "어떻게 하는지"를 "틀렸다" 두 번 뒤에 알려준다.
- 결정 사항: **튜토리얼 대상은 첫 문항의 정답 중 하나(`square_notebook`)로 하고, 그 탭을 정답 2개 중 1개로 인정한다.** 연습용 더미를 따로 둘 수 없어서다 — 네모 사물은 `square_notebook`·`square_lunchbox` 둘뿐이고 둘 다 정답이다. 미참조 에셋 `classroom-window.webp`(네모)를 연습 대상으로 쓰는 안은 **버렸다**: 배경(`classroom-shape-search.webp`)에 창문이 그려져 있지 않아 새로 얹어야 하는데, 얹으면 `■모양 2개를 찾아 봅시다`에서 정답이 아닌 세 번째 네모가 화면에 남아 문항 자체가 틀린 문제가 된다.
- 원문 이탈: 원문 `…723 요청.md` 씬2 UI 표에는 `내레이션 "모양을 찾아 봅시다"` → `입력창 클릭 방식` → `3번 오답 시 숫자` 만 있고 튜토리얼 단계가 없다. **31-a·25번과 같이 사용자 지시가 원문 계약보다 우선한 경우다.**
- 조치: `SEARCH_TUTORIAL` 상수 + `startSearchTutorial()` / `endSearchTutorial()` / `nudgeSearchTutorial()`를 넣고 `renderSearch`가 `q.id==='q_square_find_two'`일 때만 연다. 씬 안에 `#searchFinger`(`.finger-hint.search-finger`) + `#searchFingerLabel`(`네모 모양을 클릭해보세요`)를 두고 공책에 `glow-hint`를 건다.
  - **오답 판정 차단**: `registerSearchWrong` 첫 줄에 `if(searchTutorial)return void nudgeSearchTutorial()`. 빗나간 탭은 도장·효과음 대신 손가락 애니메이션 재시작으로만 반응한다.
  - **종료**: `selectHotspot`에서 **정답이면 어느 것을 눌렀든** `endSearchTutorial()`. 즉 튜토리얼 탭이 정답 2개 중 1개다. `resetShapeScene`에도 걸어 재진입 시 잔상이 없다.
  - **손가락 모션**(사용자 요청): 씬4 `fingerHintTap`(제자리 펄스 ×3)이 아니라 `searchFingerTap` — 오른쪽 아래(+30,+38)에서 대상으로 다가왔다 물러나는 왕복 + 누름 축소를 1.4s 무한 반복. 멈추는 조건은 시간이 아니라 `endSearchTutorial()`이다. 에셋이 원래 왼쪽 위를 가리켜 뒤집지 않는다(`--finger-base:none`).
- 검증: `tmp/verify69.js`(headless 1920×1080). q1에서 손가락·라벨 노출 / 손끝이 왕복 양 끝 모두 공책 핫스팟(x 907~1057 · y 890~992) 안 / 손가락 아래 `elementFromPoint`가 `#shapeSearch`라 클릭을 안 먹음 / **빈 배경 3회 + 시계 1회 탭에도 오답 도장 0 · `.hint` 0 · `.hotspot-number` 0**(튜토리얼이 없으면 3회에서 번호가 떴어야 함) / 공책 탭 → 손가락·라벨 사라지고 `glow-found` · found 1 / 도시락 탭 → 정답 도장 / q2에서 손가락 미노출 + 배경 탭이 정상 오답. `tmp/smoke-all.js` 7씬 런타임 오류 0.
- 주의: 라벨 y를 처음 946으로 잡았다가 **같은 문항의 나머지 정답인 도시락**(그림 y 829~979) 아랫단을 덮어 992로 내렸다. `pointer-events:none`이라 클릭은 안 먹지만 **찾아야 할 사물을 가리면 안 된다.**
- 미해결(사용자 결정): `search-tutorial-square` 녹음이 없어 **이 대사만 무음**이다. 키는 미리 물려 뒀으므로 `assets/audio/script/search-tutorial-square.mp3`를 넣기만 하면 코드 수정 없이 붙는다. 아래 "녹음 공백" 표에 추가했다.


## 70. 모양을 하나 맞힐 때마다 정답 도장을 낸다

- 상태: 완료 (2026-08-04)
- 지적: "튜토리얼로 뜬 거 눌러도 상호작용이 **초록색 테두리밖에 없어서 알기 힘들다**. 각각의 모양을 올바르게 클릭했을 때 정답 도장이 나오고, 2개를 모두 클릭 완료했을 때 도장+다음 버튼이 나오는 게 좋겠다." (2026-08-04)
- 진단: `selectHotspot`이 사물 하나를 맞혔을 때 내는 신호가 `glow-found`(초록 외곽선) + 딩동뿐이었다. **판정을 상태 변화(색)로만 전달**했고, 도장(`showFeedback`)은 `found.size===2`가 되어야 나왔다. 아이가 판정을 받는 단위는 **클릭 한 번**인데 연출 단위는 문항이었다. 초록 외곽선은 `glow-hover`(같은 굵기·`--accent` 색)와 굵기가 같아 **호버 표시와도 구분이 약하다.**
- 조치: `selectHotspot`에 `if(found.size<q.answers.length){showStamp(shapeMark,'correct');…;return}` 분기를 넣었다. 사물 하나를 맞힐 때마다 **0.7초 정답 도장 + 딩동**이 나고 무대의 아이가 `volunteer` 포즈를 잡는다(오답의 `thinking` 포즈와 대칭). 진행 표면(`다음 ▸`)은 열지 않는다 — 문항이 안 끝났고, 여기서 표면을 열면 26번 데드엔드 계열이 재발한다.
  - 마지막 하나는 이 분기를 타지 않고 종전대로 `showFeedback`(도장 **유지** + `다음 ▸`)으로 간다. 판정 조건도 `found.size===2` → `found.size<q.answers.length`로 바꿔 문항 데이터에 묶었다.
  - **타이머 충돌 수정**: `showStamp`의 0.7초 해제 타이머를 `stampHideTimer`에 잡고 호출 첫 줄에서 `clearTimeout`한다. 안 잡으면 **0.7초 안에 두 개를 연달아 맞혔을 때 앞 낱개 도장의 타이머가 뒤의 `hold` 도장을 걷어 간다**(문항 완료인데 도장이 사라지고 `다음 ▸`만 남는다).
- 검증: `tmp/verify70.js`(headless 1920×1080). 첫 사물 탭 +150ms → 도장 `show` · `다음 ▸` 닫힘 · 아이 `volunteer` / +1050ms → 도장 걷힘 · 진행 표면 여전히 닫힘 / 두 번째 탭 → 도장 + `다음 ▸`, **1.4초 뒤에도 도장 유지** / q2에서 **120ms 간격 연타**로 두 개를 맞혀도 1.5초 뒤 도장 유지 + `다음 ▸`(타이머 충돌 회귀 테스트). `tmp/verify69.js` 69번 회귀 전항목 통과, `tmp/smoke-all.js` 7씬 오류 0.
- 주의: 낱개 도장은 화면 중앙(`.feedback-mark` left 50% / top 48% → stage x 840~1080 · y 398~638)에 뜬다. **찾기 사물과는 겹치지 않는다**(공책 y 890~992 · 도시락 y 829~979 · 벽시계 y 215~405 — 시계와 7px 스침). `.feedback-mark` 좌표나 크기를 바꾸면 이 겹침을 다시 본다.
- 주의: 헤드리스 캡처로는 **0.7초 도장을 그림으로 못 잡는다**(스크린샷이 스크립트 종료 뒤에 찍혀 이미 걷힌 뒤다). 낱개 도장은 DOM 상태(`show` 클래스)로 검증했고, 도장의 실제 모양은 `tmp/shots/v70-done.png`(문항 완료 시 유지되는 같은 요소)로 확인했다.


## 72. 무작위 계산 문제에서 오답일 때 힌트를 자동으로 열지 않는다

- 상태: 완료 (2026-08-04)
- 지시(2026-08-04): "무작위 계산 문제에서 틀렸을때 바로 힌트를 말해주지 말아줘".
- 원인: `judgeRandomChoice`·`judgeRandomKey`의 오답 분기가 `openRandomHint(randomWrong-1)`을 불러 **학습자가 요청하지 않았는데** 말풍선이 열렸다(1회 오답 → 1단계, 2회 → 2단계). 53번이 힌트 **내용**을 단계화하면서 그 단계를 오답 횟수에 자동으로 매단 형태다. 42-a·b가 "선생님을 눌러 힌트를 받는다"는 요청 경로를 세워 놨는데 오답 경로가 그 앞을 질러가 **스스로 다시 풀어 볼 구간**을 없앴다.
- 조치: 두 판정 함수의 오답 분기에서 `openRandomHint(...)` 호출을 뺐다. 힌트를 여는 곳은 이제 `helpCharacter.onclick` **한 곳뿐**이다.
- 도형 깜빡임도 함께 뺐다(2026-08-04 사용자 결정). `openRandomHint` 안의 `flashRandomShapes`가 같이 딸려 나가므로, 오답에는 판정만 남는다 — `tone(false)` · `showWrongFeedback()`(X 도장 + 학생 thinking 포즈) · `shake()`. **씬2(`hintCountShapes`)·씬3(`hintArithmetic`)은 종전대로 오답에 도형을 깜빡인다** — 씬4만 다르다는 것을 알고 둔 것이다.
- 3회 오답 정답 공개(`revealRandomAnswer`)는 힌트가 아니라 씬2·3과 같은 안전망이라 그대로 뒀다.
- 검증: headless Chrome — 보기 유형 오답 1회 후 `#helpCard.open` false / `.hint-step` 0개, 키패드 유형 오답 1회 후에도 동일. 선생님을 누르면 종전대로 1단계부터 열린다.

## 73. 힌트를 연속으로 누르면 도형 글로우가 켜진 채 멈춘다

- 상태: 완료 (2026-08-04)
- 지시(2026-08-04): "힌트를 연속으로 누르면 도형에 글로우를 연속적으로 주는 효과가 중간에 멈춰서 일부가 빛나는 형태로 멈춰있어".
- 원인: `flashRandomShapes`가 진입할 때 `randomHintTimers.forEach(clearTimeout)`로 이전 예약을 전부 지우는데, 그 예약 안에 **"450ms 뒤 `hint-step`을 뗀다"는 되돌리기**가 들어 있었다. 켜기는 이미 실행됐고 끄기만 취소되므로 그 도형은 영구히 빛난 채 남는다. 힌트 단계마다 focus 그룹이 달라(1단계 `[0]` → 2단계 `slot`) 새 호출이 그 노드를 다시 건드리지도 않고, `closeRandomHint()`도 클래스를 안 걷었다.
- 조치: `clearRandomShapeFlash()`(타이머 취소 + `#randomShapes .hint-step` **전부** 제거)를 만들어 `flashRandomShapes` 진입 · `closeRandomHint` · `clearRandomShapeIntro` 세 곳에서 부른다. **대상 노드만 걷으면 안 된다** — 잔류하는 노드는 새 focus 그룹 밖에 있다.
- 검증: headless Chrome에서 선생님을 200ms 간격 3회 탭 → 2초 뒤 `.hint-step` 잔류 **수정 전 1개 → 수정 후 0개**. 천천히 1회 탭도 0개(정상 동작 유지).
- 주의: 씬2·3의 같은 패턴(`hintCountShapes`·`hintArithmetic`)은 호출 시 타이머를 안 지워 이 증상이 없다. 그쪽에 "겹침 방지" `clearTimeout`을 넣게 되면 **같은 함정에 빠진다** — 취소와 클래스 원복을 반드시 한 함수로 묶는다.

## 74. 힌트 손가락 글로우 제거

- 상태: 완료 (2026-08-04)
- 지시(2026-08-04): "힌트 손가락에 글로우 뺴줘".
- 조치: `.finger-hint`의 `filter:var(--ds-sm) var(--filter-glow-md)` → `filter:var(--ds-sm)`. 그림자는 남기고 노란 소프트 광만 뺐다. 실측 확인: 계산된 filter가 `drop-shadow(rgba(0,0,0,.25) 0 6px 8px)` 하나만 남는다(수정 전에는 `drop-shadow(rgb(255,232,106) 0 0 18px)`가 더 있었다).
- **손끝의 또렷한 금색 링은 남는다.** 그것은 CSS가 아니라 `tap-hint-hand.webp`에 구워진 탭 파문이다(에셋 x 0.071~0.272 · y 0.068~0.270, 채도 높은 금색 12,010px). **2026-08-04 사용자 결정: CSS 헤일로만 제거하고 링은 유지.** 링까지 지우려면 에셋을 고쳐야 한다.
- 교훈: "글로우를 빼 달라"는 요청에는 **CSS인지 에셋에 구워진 것인지 먼저 가른다.** 안 가르면 절반만 사라진 채 "뺐다"고 보고하게 된다.

## 75. 무작위 계산 문제 정답 화면을 씬2·3과 같은 도장 + 다음 버튼으로 통일

- 상태: 완료 (2026-08-04)
- 지시(2026-08-04): "무작위 계산 문제에서도 정답이 되었을때 다른 문제들과 똑같이 도장 + 다음 버튼으로 가자. 정답 보기와 다음 버튼을 만드는게 아니라".
- 원인: 씬2·3은 전부 `showFeedback(mark,'정답입니다.',advance,'correct-1')` 한 줄(도장 유지 + `#narrationAdvance`의 `다음 ▸`)인데, 씬4만 `showFeedback(mark,'')`(도장 700ms 뒤 사라짐) + `armRandomContinue`가 `#randomSolved` 판에 풀이식과 버튼을 그리는 **별도 경로**였다. **47번의 부작용**이다 — `#helpCard` 겸직을 풀려고 새 표면을 만들면서 이미 있는 표준 표면을 쓰는 선택지를 보지 않았다.
- 조치: `armRandomContinue`가 `showFeedback(randomMark,'정답입니다.',nextRandom,'correct-1')`을 부른다. 47번이 지키려던 것(힌트와 결과 분리)은 그 앞의 `closeRandomHint()`가, 26번 데드엔드는 `showFeedback`의 진행 경로가 막는다. 정답 음성도 씬2·3과 같은 `correct-1`이 난다(종전 씬4는 무음이었다).
- 함께 지운 것: `#randomSolved`의 마크업·CSS·`renderRandom`의 초기화 블록, 그리고 그 판에만 쓰이던 `randomSolution` **전부**(선언 1 + 대입 4). 중간식 풀이는 화면에서 사라진다 — 힌트 2단계가 이미 같은 식을 맡는다.
- 그대로 둔 것: 진행률·완료 칸 갱신, `hideFingerHint()`, `data-solved`로 키패드·보기 감추기, 유형 A의 `?` 칸 채우기, `randomAwaitingContinue` 가드.
- ~~`다음 ▸` 자리: 씬4만 `.on-random`으로 문제 패널 가운데(x 1212~1340)로 옮겼다.~~ → **78번으로 되돌렸다**(2026-08-04). 도형 겹침을 피하려고 씬4 전용 좌표를 준 것이었는데, 사용자가 "다음 버튼이 다른 곳들과 같이 **도장 아래**에 있어야지"라고 교정했다. 지금은 공용 기본값(가로 중앙 `top:652`)뿐이고 씬별 좌표는 없다.
- 검증: headless Chrome — 정답 시 도장 유지(`show` 유지) · `다음 ▸` 표시 · 보기/키패드 내려감 · `?` 칸 채워짐 · 힌트 닫힘, `다음 ▸` 클릭으로 다음 문항 진입(도장·`on-random` 모두 걷힘), 마지막 문항 라벨은 `모양으로 자유 그리기`. 전 씬 스모크 런타임 오류 0건·중복 id 0건.
- 주의: 헤드리스는 `speechPop`·`stamp` 같은 `both` fill 애니메이션이 **프레임을 안 돌려 from 상태(opacity 0)로 멈춘다.** 캡처로 확인할 때는 두 요소의 keyframe 끝 상태를 인라인으로 고정해야 실제 화면과 같아진다(`tmp/shot-75b.js`). 이걸 모르면 "다음 버튼이 안 뜬다"고 오판한다.

## 76. 무작위 계산 문제 3회 오답에서 X 도장 뒤에 O 도장까지 나온다

- 상태: 완료 (2026-08-04)
- 지적: "무작위 계산 문제에서 다른 문제들과 다르게 **3번 오답이 나오면 X 도장만 나오는 게 아니라 X 도장 후 O 도장까지 나온다**."
- 진단: `revealRandomAnswer`가 `answer-reveal`/`reveal` 클래스를 걸고 끝나지 않고 `setTimeout(()=>showStamp(randomMark,'correct'),ANSWER_STAMP_DELAY_MS)`(160ms)로 **정답 도장을 함께 냈다.** `showStamp`은 씬당 `.feedback-mark` 한 장(`#randomMark`)의 `src`를 갈아 끼우므로, 직전 `showWrongFeedback`이 낸 X 도장을 0.16초 뒤 O 도장이 덮어 "틀렸다 → 맞았다"로 읽힌다. 씬2·3의 같은 분기(`countWrong>=3`·`arithWrong>=3`)는 클래스만 걸고 도장을 안 낸다 — **씬4만 달랐다.** 3회 오답 공개는 판정이 아니라 안전망인데 정답 판정 신호가 붙어 있었다.
- 조치: `revealRandomAnswer`에서 `setTimeout(...showStamp...'correct')` 한 줄을 제거하고, 이 함수의 유일한 사용처였던 상수 `ANSWER_STAMP_DELAY_MS`(=160)도 함께 지웠다. 이제 X 도장이 `showStamp`의 기본 수명(700ms)대로 걷히고 그 사이 `answer-reveal`(`#randomDisplay`) 또는 `reveal`(정답 보기 버튼)만 정답을 공개한다. 보기형(`judgeRandomChoice`)·키패드형(`judgeRandomKey`) 두 경로가 같은 함수를 쓰므로 한 곳 수정으로 둘 다 잡힌다.
- 검증: `tmp/verify76-77.js`(headless Chrome 1920×1080). q1(보기형)·q2(키패드형) 각각 3회 오답을 낸 뒤 `#randomMark`를 80ms 간격으로 560ms까지 샘플링 — **수정 후 전 구간 `wrong:show`**, 정답 공개는 `.choice.reveal` / `.answer-display.answer-reveal`로 확인. 같은 스크립트를 수정 전 코드로 되돌려 돌린 `tmp/verify76-77-before.js`에서는 **160ms 지점부터 `correct:show`로 뒤집힌다**(A/B 대조). 정상 정답 경로는 그대로 O 도장 유지(`afterCorrect=correct:show`).
- 주의: `showStamp(el,type,hold)`은 씬마다 한 장을 공유한다. **오답 뒤 0.7초 안에 정답 도장을 내면 무조건 X를 덮는다** — 안전망·힌트 계열에서 도장을 낼 일이 생기면 이 수명을 먼저 확인한다(70번의 `stampHideTimer` 메모와 같은 뿌리).

## 77. 무작위 계산 문제 키패드에서 확인 버튼에 호버하면 글자가 안 보인다

- 상태: 완료 (2026-08-04)
- 지적: "무작위 계산 문제에서 키패드 **확인 버튼에 호버하면 흰색으로 색이 바뀌어서 글자가 안 보이게 된다.** 호버했을 때 색 바뀜은 없애 달라."
- 진단: `.key.enter`는 `color:#fff` on `background:#e23b3b`(빨강)인데, `#randomInput .key:hover{background:var(--veil)}`(= `rgba(255,255,255,.92)`)가 **id 명시도로 그 위를 덮어** 흰 판 위 흰 글자가 됐다. 이 hover 규칙은 씬4 전용이라 씬2·3 키패드(`countKeypad`·`arithKeypad`)에는 같은 증상이 없다.
- 조치: `#randomInput .key:hover`에서 `background` 선언만 빼고 `transform:translateY(-2px)`(들림)는 남겼다. 공통 규칙 `.key:hover{filter:var(--filter-hover)}`(= `brightness(1.06)`)만 적용되어 씬2·3 키패드와 호버 반응이 같아진다.
- 검증: `tmp/verify76-77.js`. 확인 키에 **실제로 걸리는** `:hover` 규칙만 CSSOM에서 골라(`:hover`를 뗀 선택자로 `element.matches`) 배경/글자색 선언을 검사 — 수정 후 `enterHoverChangesColor:false`(남은 선언은 `filter`·`transform`뿐), 확인 키 색은 `rgb(255,255,255)` on `rgb(226,59,59)` 유지. 수정 전 대조본에서는 `#randomInput .key:hover`의 `bg:var(--veil)`가 잡힌다.
- 주의: 헤드리스에서는 실제 마우스 호버를 걸 수 없어 **적용될 규칙 집합으로 검증**했다. `:hover`에서 배경을 바꾸는 규칙을 다시 넣는다면 `.key.enter`처럼 반전 배색인 변형의 글자색까지 함께 정해야 한다.

## 78. `다음 ▸`는 씬4에서도 도장 바로 아래에 둔다

- 상태: 완료 (2026-08-04)
- 지시(2026-08-04): "다음 버튼이 다른곳들과 같이 도장 아래에 있어야지". 75번 조치에 대한 교정이다.
- 원인: 75번에서 씬4 정답 표면을 표준 경로로 옮기면서, **자리만 씬4 전용(`.narration-advance.on-random`, 문제 패널 가운데)** 으로 줬다. 기본 좌표가 도형 박스와 56×23 겹치는 것을 피하려던 것인데, **표준 표면을 쓰는 의미가 "도장 바로 아래"라는 같은 관계에 있다**는 것을 놓쳤다. 도구는 통일하고 위치는 안 통일한 셈이다.
- 조치: `.on-random` 규칙과 그 클래스를 붙였다 떼던 두 줄(`armRandomContinue`·`resetFeedbackOverlay`)을 전부 제거했다. 이제 씬4도 `.narration-advance` 기본값(가로 중앙 · `top:652`)만 쓴다 — 도장(240px, 중앙 y 518 → 바닥 638) **14px 아래**로 씬2·3과 같은 관계다. 마지막 문항 라벨(`모양으로 자유 그리기`)만 씬4에서 덮어쓴다.
- 실측: `다음 ▸` x **897~1024** · y **652~699**(가로 중심 960 = 도장 중심과 같다).
- **알고 남긴 겹침**: 최대 개수(D 유형 19개 = 4행)에서 5열의 2·3행 도형 두 칸(x 864~968 · y 552~656 / 668~772)과 겹친다. 버튼이 `--z-speech`(30), 도형이 `--z-content`(10)이라 버튼이 위에 그려진다. **도장(x 825~1096)이 이미 같은 방식으로 도형을 덮고 있고 씬2·3도 마찬가지**라, 정답 순간의 오버레이로 일관된다고 보고 그대로 뒀다. 겹치는 두 칸은 뺄셈에서 이미 `.removed`(흐린 회색)라 정보 손실도 없다.
- 검증: headless Chrome — 문항 4개를 실제로 풀어 마지막 D 유형(19개)까지 가서 좌표·겹침을 실측하고 캡처했다(`tmp/shot-78-max.js` · `tmp/shots/v78-max.png`). 전 씬 스모크 런타임 오류 0건.

## 81. 유형 A 정답을 숫자가 아니라 도형으로 닫는다

- 상태: 완료 (2026-08-04)
- 지시(2026-08-04): "무작위 계산 문제에서 첫번째 유형의 `10이 되는 덧셈식을 찾아 보세요` 문제에서 정답을 맞췄을 시 **물음표 박스에 숫자를 넣는 게 아니라 10개를 맞추러 도형을 추가**해 주는 식이 좋을 것 같아. `+` 이후에 도형을".
- 원인: 48번이 유형 A의 빈 담장을 `● … ● + [?]`로 채웠지만 **정답 표현은 숫자로 남았다**(`randomSlotNode.textContent=b` + `.filled`). 이 씬의 다른 세 유형은 전부 개수를 도형으로 세는데 유형 A만 답이 숫자로 닫혀, "10을 채웠다"가 그림에서 안 보였다.
- 조치: `fillRandomSlotWithShapes()`를 만들어 `armRandomContinue`에서 부른다. 물음표 칸 **자리에** 모자란 개수(`randomBundle.add.b`)만큼 도형을 끼워 넣고 칸 자체는 제거한다 → 화면의 도형이 정확히 **10개**가 된다.
  - 색·모양은 41-a의 항별 매핑을 따른다 — 첫째 항이 초록 ●이므로 둘째 항은 **파랑 ■**다. 같은 초록 ●로 채우면 항 경계가 사라져 41-a가 세운 규칙과 부딪힌다.
  - 등장은 유형 C·D의 add 단계와 같은 연출(`.pending` 해제 스태거, `RANDOM_SHAPE_LEAD_MS` + `index*RANDOM_SHAPE_STAGGER_MS`)이다. 타이머는 **`randomShapeTimers`에 넣어야** 다음 문항에서 `clearRandomShapeIntro`가 함께 걷는다.
  - `.paint-slot.filled` CSS는 참조가 0이 되어 제거했다.
- 검증: headless Chrome에서 `Math.random` 첫 호출을 고정해 **a=1·4·8·9 네 경우**를 실제로 풀었다. 전부 `초록 a + 파랑 (10-a) = 10`, 물음표 칸 제거됨, `pending` 잔여 0. 최대 셀 수(a=9 → 도형 10 + 빈칸 + `+` = 12칸)에서도 3행으로 담장 면(y 380~946) 안이다. 전 씬 스모크 런타임 오류 0건.
- **남은 겹침(사용자 판단 필요)**: 정답 도장(x 825~1096)과 `다음 ▸`(x 897~1024)가 도형 5열(x 856~960)을 덮는다. 이 유형은 "10개를 세는 것"이 요점인데 **도장이 한 칸을 가린다.** 78번에서 정한 대로 도장·버튼 자리는 씬 공통이라 이 씬만 옮기지 않았다. 고치려면 (a) 그대로 두기, (b) 씬4 도장만 위로 올리기(78번의 일관성과 부딪힘), (c) 도형 박스를 좁혀 5열을 x 825 왼쪽에 몰기(도형이 104 → 78px로 작아져 `[content-scale-too-small]` 13회와 부딪힘) 중 선택이 필요하다.
- 주의: 이 함수는 **정답 경로에서만** 불린다. 3회 오답 뒤 정답을 눌러 들어와도 같은 경로(`judgeRandomChoice` → `completeRandomProblem`)라 그대로 동작한다.

## 79. 무작위 계산 문제 힌트가 유형마다 골격이 달라 중구난방이다

- 상태: 완료 (2026-08-04)
- 지시(2026-08-04): "무작위 계산 문제에서 힌트가 너무 중구난방이야. **10이 되는 덧셈식은 괜찮아 이어지잖아** — 2개 세고 10개까지 몇 개? 근데 **세 수의 덧셈**은 `두 수를 더해 10을 만들고` 그다음 힌트가 `2+8=10`이면 이상하잖아. 차라리 `두 수를 더해 10을 만들어보세요` → `10에 나머지 수를 더해보세요`가 낫지. 각 유형 4개에 힌트를 어떻게 줄지 고민해봐."
- 원인: 53번이 힌트를 2단계로 쪼갤 때 **단계의 "형식"만 정하고 단계 사이의 "관계"는 정하지 않았다.** 결과적으로 골격이 유형마다 달랐다 — A `세기 → 질문` / B `세기 → 세기` / C·D `지시 → 완성된 식`. C·D의 2단계 `${a} + ${b} = 10`은 결함이 셋이다.
  1. 1단계가 시킨 일(`두 수를 더해 10을 만들어 봐요`)의 **답을 되풀이할 뿐 앞으로 못 간다.**
  2. 남은 `+ c`(또는 `- c`)는 **두 단계 어디에서도 말하지 않는다.** 정작 못 푸는 지점이 거기다.
  3. 반짝이는 도형은 `c`(빨강 ▲)인데 글자는 `a+b` 얘기라 **글자와 그림이 서로 다른 항을 가리킨다.**
- 정한 골격(사용자가 "괜찮다"고 한 유형 A에서 뽑았다): **1단계 = 재료 만들기(답을 담지 않는다) / 2단계 = 그 재료를 받아 남은 한 걸음.** 2단계는 1단계 결과(`10` 또는 센 개수)를 주어로 받아 `이제 ~해 봐요`로 다음 **동작**을 말한다. **완성된 식은 힌트에 쓰지 않는다** — 답의 절반이고, 앞 단계의 되풀이라 사슬이 끊긴다. 글자가 말하는 항과 `focus`로 반짝이는 도형은 반드시 같은 것을 가리킨다.
- 조치 (`renderRandom`의 `randomHintSteps`):

  | 유형 | 1단계 (재료) | focus | 2단계 (남은 한 걸음) | focus |
  | --- | --- | --- | --- | --- |
  | A `a + ? = 10` | `초록 ●를 세어 봐요.` (변경 없음) | `[0]` | `{a}개에서 10까지\n몇 개가 더 필요할까요?` (변경 없음) | `slot` |
  | B `10 - c` | `지워진 파랑 ■를 세어 봐요.` | `[1]` | `이제 남은 초록 ●를\n세어 봐요.` | `[0]` |
  | C `a + b + c` | `앞의 두 수를 먼저 더해\n10을 만들어 봐요.` (변경 없음) | `[0,1]` | `이제 10에 빨강 ▲를\n더해 봐요.` | `[2]` |
  | D `a - b - c` | `앞의 두 수를 먼저 빼서\n10을 만들어 봐요.` | `[1]` | `이제 10에서 빨강 ▲를\n빼 봐요.` | `[2]` |

  - B의 1단계는 `지워질 것을` → `지워진 파랑 ■를`로 바꿨다. 연출이 이미 지운 뒤라 **시제가 틀렸고**, 색을 안 말해 어느 도형을 보라는 건지 글자만으로는 알 수 없었다.
  - B의 2단계 `남은 것을 세어 봐요`는 1단계 없이도 성립하는 독립 지시라 사슬이 아니었다. `이제`를 붙여 앞 단계를 받게 했다.
  - D의 1단계 `앞에서부터 차례로 지워 봐요`는 **목표(10 만들기)를 말하지 않아** C와 골격이 달랐다. C와 대칭인 문장으로 바꿨다.
  - **미사용 유형 2·4**(43번이 시퀀스에서 뺐지만 되돌릴 여지로 남긴 분기)도 같은 골격으로 함께 고쳤다. 골격이 규칙인 이상 한 곳만 남겨 두면 되살릴 때 다시 어긋난다.
- 검증: headless Chromium(1920×1080)에서 4유형을 실제로 렌더해 **문제식 · 담장 도형 개수 · 힌트 두 단계의 글 · 각 단계에서 실제 `hint-step`이 붙은 도형 클래스**를 전수 대조했다. 예: D `19 - 9 - 1`(초록 9 · 파랑 9 · 빨강 1) → 1단계 글 `앞의 두 수를…` + 파랑 반짝 / 2단계 글 `이제 10에서 빨강 ▲를…` + 빨강 반짝. 4유형 전부 글자와 반짝이는 항이 일치했고 page/console 오류 0건.
- 주의: 힌트 문구는 **녹음이 없다**(원문에 없는 화면 추가 문구 — `todo.md`의 "녹음 공백" 표 참조). 문구를 또 바꿔도 음성은 따라오지 않는다.

## 80. 힌트 말풍선에 `다음 ▸`가 없어 단계가 하나뿐인 줄 안다

- 상태: 완료 (2026-08-04)
- 지시(2026-08-04): "힌트가 2개로 나뉘어지는데 **다음 버튼이 없어서 힌트가 하나만 나오는 줄 알 듯해.** 힌트에 다음 버튼을 추가해주는거 어때?"
- 원인: 53번이 힌트를 2단계로 쪼개면서 **다음 단계를 여는 조작을 `#helpCharacter`(선생님) 재탭 하나에만** 걸어 뒀다. `#helpCard` 안에는 이 문서의 표준 진행 신호인 `.repair-bubble-nav`가 없어 **더 있다는 신호가 0개**였다. 게다가 `.speech.help-speech`에는 `cursor:pointer`만 있고 **클릭 핸들러가 없어** 눌러도 되는 것처럼 보이는 죽은 표면이었다.
- 조치:
  - `openRandomHint`가 글을 넣은 뒤 nav를 덧붙인다. 다음 단계가 있으면 `다음 ▸`, 마지막 단계면 `닫기`(`HINT_NEXT_HTML` / `HINT_CLOSE_HTML`). **마지막에 버튼을 아예 없애지 않은 이유**는 "끝"인지 "고장"인지 구분이 안 되기 때문이다.
  - 글은 `textContent`로 넣고 nav만 `insertAdjacentHTML('beforeend', …)`로 붙인다. `.speech`가 `white-space:pre-line`이라 **`innerHTML`로 통째로 쓰면 힌트 글의 `\n`을 `<br>`로 바꿔 써야 하고, 그러면 글 데이터에 마크업이 섞인다.**
  - 단계 진행 로직을 `stepRandomHint()`로 묶고 `#helpCharacter.onclick`과 새로 단 `#helpCard.onclick`이 **같은 함수**를 쓴다. 66번처럼 여닫이가 여러 곳에 흩어지면 한쪽만 고쳐 상태가 어긋난다.
  - 버튼은 다른 씬과 같이 `tabindex="-1"`이라 클릭이 말풍선으로 버블링된다 — 버튼에 따로 핸들러를 달지 않는다.
  - `closeRandomHint`·`renderRandom`이 이미 `textContent=''`로 비우므로 nav도 함께 사라진다(추가 정리 불필요).
- 검증: headless Chromium에서 4유형 각각 `선생님 탭 → 말풍선 탭 → 말풍선 탭` 3회를 눌러 `open` 상태 · nav 개수(항상 1개, 중복 삽입 없음) · 버튼 라벨(`다음 ▸` → `닫기` → 없음/닫힘)을 전수 확인했다. 정답 처리 뒤 힌트가 닫히는 것(`armRandomContinue`)도 4유형 전부 확인. page/console 오류 0건. 캡처: 1·2단계 각각 1920×1080.
- **알고 남긴 겹침(사용자 판단 필요)**: nav 한 줄이 붙어 말풍선이 약 40px 높아졌다. 말풍선은 꼬리를 선생님 머리에 붙이느라 `bottom:620px`로 **아래가 고정**이라 높아진 만큼 위로 자란다. 그래서 문제 판(`#randomPanel .random-prompt`, x 1020~1530 · y 305~480)의 오른쪽 끝을 덮는 정도가 조금 늘었다(2줄 힌트에서는 **이전에도 이미 덮고 있었다** — 새로 생긴 겹침이 아니라 커진 겹침이다). 위로 올리면 꼬리가 선생님 머리에서 떨어지므로 이 씬만의 좌표 조정으로는 못 푼다. 필요하면 (a) 그대로 두기, (b) 문제 판을 왼쪽으로 좁히기, (c) nav를 글 끝에 인라인으로 붙여 줄을 안 늘리기(다른 씬의 표준 형태와 달라진다) 중 선택이 필요하다.

## 82. "이것을 페인트라고 해요" 대사에 맞춰 페인트 통이 등장하고 하이라이트된다

- 상태: 완료 (2026-08-04)
- 지시(2026-08-04): "세 수의 덧셈과 뺄셈 섹션에서 `이것을 페인트라고 해요`라는 말이 나오는데 **이미 나와 있어**. 이때 대사를 치면서 페인트 나타나면서 하이라이트 진행하면 더 좋을 것 같아. 초등학생이니까 이해하기 쉽도록."
- 원인: `section_arithmetic_tutorial`은 씬이 열리는 순간부터 `#arithPaintCan1`이 화면에 있었다(`resetArithmetic`이 곧바로 `setPaintCans('one')`). 소개 대사가 **무엇을 가리키는지 시선을 끌어 줄 액션이 0개**라 대사가 화면과 따로 놀았다. 앞 씬(`startPaintIntro`)은 52번으로 이미 "대사 1개 ↔ 짝 1벌 공개"가 물려 있어, 이 씬만 그 규칙에서 빠져 있던 자리다.
- 조치:
  - `arithmeticIntroBeats`에 `cans`(+`spotlight`)를 얹어 **등장 시점을 대사 데이터가 정한다** — `preBeats[].cans`와 같은 방식이다. beat0 `'none'` → beat1(`이것을 페인트라고 해요`) `'one'`+`spotlight` → beat2 `'one'`. `#arithIntroTap`의 intro 분기와 `resetArithmetic`이 이 값을 읽는다(재진입해도 통은 다시 없어진다).
  - `setPaintCans`에 `'none'` 상태를 추가하고, `'one'`으로 올 때 **숨어 있었을 때만** `arriving`(pop)을 재생한다(`wasHidden`). 이미 보이는데 대사마다 튀면 소개 순간의 신호가 묽어진다. `empty` 토글 조건도 `state!=='one'` → `'first-empty'||'two'`로 명시화했다(`'none'`이 회색 통을 켜지 않게).
  - 하이라이트는 `.paint-can.spotlight` + `@keyframes canSpotlight`(글로우 `--filter-glow-lg` + `scale(1.07)`, `--dur-slow` × 3회). `spotlightPaintCan(on)`이 붙였다 뗀다.
- 주의(다음 사람에게 필요한 것):
  - **투명 raster에 사각 링(box-shadow)을 두르면 통이 아니라 빈 박스가 그려진다.** 알파를 따라가는 `drop-shadow` 글로우여야 한다.
  - **`.arriving`과 `.spotlight`를 각각 별도 규칙으로 두면 하나만 재생된다** — 같은 요소의 `animation` 속성을 통째로 덮기 때문이다. `.paint-can.arriving.spotlight`에 두 애니메이션을 한 줄로 쓰고 글로우에 `var(--dur)` 지연을 줘 "등장 → 강조" 순서로 읽히게 했다.
  - **글로우만으로는 크림색 담장 위에서 거의 안 보인다**(정점 프레임을 `Animation.currentTime`으로 고정해 실측). 그래서 같은 박자의 크기 펄스를 얹었다. `transform-origin:bottom center`인 것은 통이 땅에 놓여 있어서다 — 가운데 기준으로 키우면 통이 떠오른다.
- 검증: headless Chromium 1920×1080. (1) beat0 `display:none` → beat1 `pop + canSpotlight`(계산된 filter가 정점에서 `rgb(255,232,106) 22px` + `scale(1.07)`) → beat2 글로우만 해제 → 문항 중 통 유지 → 씬 재진입 시 다시 숨김을 상태·캡처로 확인. (2) 회귀: q1·q2를 실제로 풀어 `q_add_10_2`의 preBeats까지 진행해 `통 소진`에서 can1 `empty`, `1통을 더 준비했어요`에서 can2 등장(21번 연출)이 그대로임을 확인.

## 84. 모양 찾기와 세기의 오프닝 대화 인물이 책상을 밟고 서 있다

- 상태: 완료 (2026-08-04)
- 지시(2026-08-04): "모양 찾기와 세기에서 **선생님과 학생 위치 책상 밟지 말고 바닥을 밟고 있을 수 있도록** 해 줘. 다른 곳에 영향 주지 말고 여기서만. **서 있는 학생 말고 대화할 때 나오는 선생님과 학생**을 말하는 것."
- 원인: 공용 `.character.left/.right{bottom:-12px}`는 **무대 바닥** 기준이라 발끝이 stage y **1022(아이)·1027(교사)** 에 온다. `classroom-shape-search.webp`에서 그 높이는 **책상 상판·의자 구간**(뒷모서리 901 · 앞모서리 979~985)이다. 이 배경에서 사람이 설 수 있는 면은 벽·바닥 경계(818)와 책상 뒷모서리(901) 사이의 통로뿐이고, **같은 씬의 `#shapeSceneStudent`는 23번에서 이미 그 통로(발끝 y≈880)에 앉혀 놨다** — 대화 인물만 공용 규칙에 남아 있었다.
- 조치:
  - `#shapeCharacter.on-floor{bottom:129px}` / `#shapeCharacter.on-floor[src*="teacher-"]{bottom:135px}` 두 줄. 값이 두 벌인 것은 알파 bbox 하단 비율이 달라서다(아이 0.892~0.896 / 교사 0.947). 계산은 `contain` 여백을 빼고 발끝 = `1009 - bottom`(아이 박스 308×504) / `1015 - bottom`(교사 박스 440×720)이며, 아이 값 129px은 `.classroom-student`와 우연이 아니라 같은 값이다(같은 에셋·같은 발끝 목표).
  - `.on-floor`는 `renderShapeDialogue()`가 붙인다(`ch.className='character on-floor '+b[3]`). **이 씬은 `#shapeCharacter` 한 요소가 배경을 갈아 끼우며 세 단계를 다 쓴다** — 오프닝만 교실이고 `startPaintIntro`·`finishShape`는 담장(`school-wall-closeup`)이라 지면이 무대 바닥이다. 그 둘은 `ch.className='character right'`로 클래스를 지우므로 공용 `bottom:-12px`가 그대로 남는다(64번의 제목 `.on-wall`과 같은 짝 구조).
- 검증: headless Chrome 1920×1080.
  - 발끝: 씬2를 오프닝 4 beat → 찾기 3문항 → paint-intro → 세기 3문항 → 아웃트로까지 실제 클릭으로 통과시키며 실측(`tmp/verify-83.js` — 파일명은 개명 전 번호다). 오프닝 **880·880·880·882**(목표 880), paint-intro·아웃트로 **1027**(변경 전과 동일).
  - 말풍선: 오프닝 4 beat에서 말풍선 세로 중심 − 얼굴 중심 = **0·0·0·−1px**(`tmp/verify-84.js`).
  - 캡처로 네 beat 모두 마루면에 서 있고 담장 단계는 잔디에 그대로 서 있는 것을 확인.
- 주의:
  - **공용 `.character`의 `bottom`은 안 건드렸다.** 38번 주석("bottom은 건드리지 않는다 — 발끝이 같은 바닥선에 남아야 크기 차이가 키 차이로 읽힌다")은 무대 바닥을 지면으로 쓰는 씬(1·3·5)에서 유효하고, 지면이 그려진 교실 배경에서만 예외다.
  - **인물이 올라가면 말풍선도 같은 폭으로 올라가야 한다.** 같은 시각 다른 세션의 83번이 말풍선 세로 앵커를 `--speech-face-y`(얼굴 중심 절대 y — 어른 492 / 아이 707)로 바꿨는데, 그 값은 **`bottom:-12`(무대 바닥)를 전제로 계산된 것**이라 발끝을 옮긴 이 씬에서는 말풍선만 제자리에 남는다. 83번과 같은 공식에 옮긴 bottom을 넣어 다시 재고(교사 345 / 아이 566) `.on-floor`가 붙은 beat에만 걸었다. 이 두 값은 `#shapeCharacter`의 `bottom`과 **한 몸**이다.
  - 인물 크기는 그대로다. 이 깊이(발끝 880)의 원근 축척은 23번 실측으로 1m ≈ 310px이라 교사(알파 높이 625px ≈ 2m)는 규격보다 크다. **크기는 `--char-scale`이 전 씬 공통(어른 1.0 / 아이 0.7)이라 이 씬만 줄이면 38번 규칙이 깨진다** — 필요해지면 별도 항목으로 연다.

## 83. 대사 말풍선 세로 위치를 캐릭터 얼굴 높이에 맞춘다

- 상태: 완료 (2026-08-04)
- 지시(2026-08-04): "대사 말풍선 위치의 **y축이 캐릭터의 얼굴 위치**에 올 수 있도록 해 줘. 지금은 너무 높거나 낮아."
- 원인은 둘이고 **둘 다 57번이 남긴 것**이다.
  - (a) **기준점이 얼굴이 아니라 머리 꼭대기였다.** 57번은 "꼬리 y − 머리 꼭대기 y"를 어른·아이가 같게 맞췄을 뿐, 그 간격이 얼굴에 오는지는 보지 않았다. 실측하니 어른 beat의 꼬리는 얼굴 중심(y 492)보다 **194px 위**, 머리 꼭대기(433)보다도 위여서 말풍선이 **머리 위 하늘**에 떠 있었다.
  - (b) **앵커가 상자 윗변(`top`)인데 꼬리는 상자 세로 중심(`::before{top:50%}`)이었다.** 대사 줄 수가 늘면 상자가 아래로만 자라 꼬리가 그만큼 내려간다 → 같은 씬 안에서도 beat마다 높이가 달라진다. 사용자가 "너무 높거나 **낮아**"라고 한 것이 이 둘이 섞인 결과다.
- 조치:
  - `.speech`의 세로 앵커를 `--speech-face-y`(**얼굴 중심 y** 절대 좌표) 하나로 바꾸고 `.left-speaker`·`.right-speaker`에 `top:var(--speech-face-y);translate:0 -50%`를 줬다. 상자가 위아래로 **같이** 자라므로 대사 길이와 무관하게 **상자 세로 중심 = 꼬리 = 얼굴**이 유지된다.
  - **`transform:translateY(-50%)`가 아니라 `translate` 속성을 쓴 것이 핵심이다.** `speechPop`이 `transform:scale()`을 애니메이션하므로 `transform`으로 적으면 등장할 때 보정이 통째로 날아간다(377행 `.narration-advance` 주석이 적어 둔 것과 같은 함정). `translate`는 독립 속성이라 `transform`과 합성된다.
  - 아이 보정은 `--speech-child-drop:205px`(머리 차이) → `--speech-face-y:707px`(아이 얼굴 절대값)로 바꿨다. 가로(`left:280`/`right:250`)는 38번 실측 그대로다.
  - 씬 오버라이드 `#arithSpeech{--speech-anchor-top:350px}`·`#drawingSpeech{--speech-anchor-top:270px}`는 **삭제**했다. 상자 윗변 기준값이라 남겨 두면 얼굴 정렬을 이긴다. 씬5는 얼굴 앵커(492)가 제목 아래(250)보다 한참 낮아 56번이 내려 뒀던 이유 자체가 사라졌다(제목 좌표는 그대로).
  - `.speech.feedback-speech`도 `top:470px` → `--speech-face-y:598px`. 이 슬롯(`.feedback-character` 360×590 / bottom −10)은 인물 크기가 달라 얼굴 y가 따로다.
- 얼굴 중심 실측(`tmp/measure-face.js`): 에셋 알파의 **행 폭 프로파일**에서 머리 꼭대기 → 목(국소 최소)을 찾고 그 중점을 얼굴 중심으로 잡았다. 원본 1024×1536 높이 대비 비율은 어른 6종 **0.132~0.146**, 아이 3종 **0.212~0.214**로 갈린다(값은 `todo.md`의 "캐릭터 얼굴 중심 비율" 표).
  - `.character.left/.right`(440×720 / bottom −12) 환산 → **어른 492 / 아이(--char-scale .7) 707**. `.feedback-character` → **598**.
- 검증: headless Chrome 1920×1080, 애니메이션 정지 후 14개 beat 실측(`tmp/verify-83b.js`). "꼬리 y − 얼굴 중심 y"가 **−6 ~ +1px**(worker-explaining만 −6 — 안전모까지 얼굴로 잡혀 비율이 .146으로 혼자 높다). 상단바(56)·무대(1080) 침범 0. 대사를 4줄로 늘려 상자가 100 → 242px로 커져도 꼬리는 707에 그대로 남는 것을 따로 확인했다. 캡처 8장(`tmp/shots/s83-*.png`) 육안 확인.
- 주의: **씬별 오버라이드에 `top`을 직접 쓰지 않는다**(57번 주의사항 유지). 이제 줄 수 있는 것은 `--speech-face-y` 하나뿐이고, 그 값은 **인물 발끝(`bottom`)이 바뀌면 같은 폭으로 함께 움직여야 한다** — 84번의 `.on-floor`(씬2 오프닝, 교사 345 / 아이 566)가 그 사례다.
- 주의: `#helpCard`(`.top-speaker`, `top:auto;bottom:620px`)는 인물 **머리 위** 변형이라 `translate` 대상이 아니다. `.left-speaker`·`.right-speaker`에만 걸었으므로 영향이 없다.

## 85. 말풍선을 인물 바로 옆에 붙이지 않는다 (포즈를 가림)

- 상태: 완료 (2026-08-04)
- 지시(2026-08-04): "**머리 바로 옆에 붙이지 마.** 인트로에서 보면 꼬마 옆에 바로 붙여서 **꼬마 포즈가 가려졌잖아.**"
- 원인: 38번이 아이 가로 앵커를 `right:390` → `250`으로 당길 때 기준이 "**꼬리 끝이 전신 알파 bbox 안에 들어오는가**"뿐이었다. **상자 자체가 인물을 덮는지는 보지 않았다.** 실측하니 `student-volunteer`.right는 말풍선 오른쪽 끝 1670이 실루엣 시작 1612를 **58px 파고들어**, 자원하며 든 팔을 그대로 덮고 있었다(`student-thinking`.right 48 · `student-idle`.right 22 · `student-idle`.left 4 · `student-volunteer`.left 7px도 같은 방향).
- **전신 알파 bbox로는 이 결함이 안 보인다.** 전신 bbox는 들어올린 팔·벌린 발까지 포함한 좌우 끝이라, 말풍선이 실제로 걸리는 **얼굴 높이 밴드**의 실루엣과 다르다. 그래서 밴드(얼굴 중심 ± 말풍선 최대 반높이 **121px** = 4줄 242px의 절반) 안으로 좁혀 다시 쟀다(`tmp/measure-side.js`).
- 조치:
  - 가로 앵커를 `--speech-side-x`로 빼고 `.left-speaker{left:var(--speech-side-x)}` / `.right-speaker{right:var(--speech-side-x)}`로 바꿨다. **값 = 밴드 안 실루엣 가장자리 ∓ 60px.** 꼬리가 34px이므로 실루엣까지 26px을 남기고 멈춘다 — 가리키되 덮지 않는다.
  - **에셋·방향별로 준다.** 밴드 안 실루엣이 에셋마다 최대 75px까지 차이 나기 때문이다(`worker-apologizing` 301 ↔ `worker-explaining` 376). 묶어서 한 값을 주면 좁은 인물에서 꼬리가 100px 넘게 떠 "누가 말하는지" 신호가 끊긴다. 38번이 남긴 `.character[src*="student-"]` 두 줄은 세로(`--speech-face-y`) 전용으로 줄이고 가로는 이 표로 옮겼다.

    | 선택자 | 밴드 안 실루엣 | `--speech-side-x` |
    | --- | --- | --- |
    | `worker-apologizing`.left | …301 | 361 |
    | `worker-explaining`.left | …376 | 436 |
    | `student-thinking`.left | …259 | 319 |
    | `student-idle`.left | …284 | 344 |
    | `teacher-explaining`.right | 1556… | 424 |
    | `teacher-praising`.right | 1624… | 356 |
    | `student-volunteer`.right | 1612… | 368 |
    | `student-idle`.right | 1648… | 332 |

  - `.speech.feedback-speech`도 `left:380px` → `--speech-side-x:416px`. 이 슬롯(360×590 / left 80)에서 `teacher-praising`의 밴드 안 실루엣 오른쪽 끝은 **356**이라 같은 +60 규칙이다(27번이 잡아 둔 380은 꼬리가 인물 안으로 파고드는 값이었다).
  - `left`/`right`를 직접 쓰지 않고 **변수로 준 것**이 57번 교훈의 적용이다 — 인접 형제 선택자와 ID 선택자 사이에 명시도 싸움이 생기지 않는다.
- 검증: headless Chrome 1920×1080, 13개 beat 실측(`tmp/verify-85.js`). 말풍선 상자 ↔ 실루엣 여백이 전부 **59~60px**, 꼬리 끝은 실루엣까지 **25~26px**. 세로(83번)는 그대로 −6 ~ +1px. 캡처 8장(`tmp/shots/s83-*.png`)에서 인트로 꼬마의 든 팔·씬2 아이의 턱 괸 손·작업자의 숙인 자세가 모두 안 가리는 것을 확인했다.
- 주의: **인물 에셋을 교체하거나 `--char-scale`·슬롯 크기를 바꾸면 이 표를 다시 잰다.** 재는 대상은 전신 bbox가 아니라 **말풍선이 걸리는 y 밴드 안의 실루엣**이다(`tmp/measure-side.js`를 다시 돌리면 된다).
- 주의: 새 인물·새 방향 조합을 추가하면 표에 줄을 더한다. 빠뜨리면 공용 기본값(`--speech-side-x:390px`)으로 떨어지는데, 그 값은 **어떤 인물 기준도 아니다** — 겹치거나 뜬다.

## 86. 페인트 통 하이라이트의 노란 글로우를 뺀다

- 상태: 완료 (2026-08-04)
- 지시(2026-08-04): "**노란색 하이라이트 너무 촌스럽다.** 어떻게 하는게 좋을까? 그냥 글로우만 뺄까?" → 검토 후 **A안(글로우 제거, 모션만) 사용자 확정.**
- 대상: 82번이 넣은 `@keyframes canSpotlight`(`section_arithmetic_tutorial`의 `#arithPaintCan1` 지목 연출).
- 원인: 강조를 `--filter-glow-lg`(= `drop-shadow(0 0 22px #ffe86a) drop-shadow(0 0 38px #fff080)`)로 낸 것. (a) 배경이 크림색 담장(`school-wall-closeup.webp`)이라 노랑은 대비가 거의 없어 **색으로 안 읽히고 뿌연 번짐만 남는다.** (b) 화풍이 "굵고 깔끔한 외곽선 + 플랫 셰이딩"이라 soft bloom이 이질적이다. **82번 검증 메모에 이미 "글로우만으로는 크림색 담장 위에서 거의 안 보인다 → 크기 펄스를 얹었다"고 적혀 있었다 — 실제로 일하던 신호는 처음부터 펄스였고, 글로우는 촌스러움만 얹고 있었다.**
- 조치:
  - `@keyframes canSpotlight`를 `{0%,100%{transform:scale(1)}50%{transform:scale(1.10)}}`로 바꿨다. `filter` 선언을 통째로 뺐고, 빠진 글로우 몫은 펄스를 **1.07 → 1.10**으로 키워 메웠다. `.paint-can.spotlight` / `.paint-can.arriving.spotlight`의 타이밍(pop 450ms → 강조 650ms × 3, `transform-origin:bottom center`)은 그대로다.
  - **`--filter-glow-lg` 토큰 자체는 건드리지 않았다.** 그 토큰은 `@keyframes glowOnce`(201) · `.paint-shape.hint-step`(439) · `.paint-slot.hint-step`(730)이 함께 쓴다 — 토큰 값을 고쳤으면 씬2·씬4 힌트까지 조용히 바뀐다.
- 검증: headless Chrome 1920×1080 (`tmp/verify-86.js`). `Animation.currentTime`을 정점(delay 450 + 325ms)에 고정해 실측 — 계산된 `filter`가 기본 그림자 `drop-shadow(rgba(0,0,0,.3) 0 12px 16px)` **하나뿐**(노란 drop-shadow 0개), `transform`이 `matrix(1.1,0,0,1.1,0,0)`, `transform-origin` `125px 250px`(= bottom center). 끝(100%)에서 `scale(1)` 복귀. beat0 `display:none` → beat1 `pop`+`canSpotlight` 등장 회귀도 함께 확인. 캡처 `tmp/shots/86-peak.png`.
- 주의(다음 사람에게 필요한 것):
  - **keyframe에서 `filter`가 빠진 것은 부수 효과가 아니라 이득이다.** `drop-shadow` 애니메이션은 매 프레임 리페인트를 부르는데 이제 `transform`만 남아 컴포지팅으로 돈다. 예전 0%/50% 양쪽에 있던 `var(--ds-md)`는 keyframe이 `filter`를 건드리는 동안 기본 그림자를 잃지 않으려던 것이라, `filter`를 안 쓰면 필요 없다(`.paint-can`이 상시로 갖고 있다).
  - **`transform-origin:bottom center`는 유지해야 한다** — 가운데 기준으로 키우면 통이 땅에서 떠오른다. 펄스를 더 키우고 싶어도 이 값을 함께 바꾸지 않는다.
  - **headless 캡처에서 말풍선이 안 보이면 회귀가 아니다.** 가상시간(`--virtual-time-budget`)에서는 rAF가 굶어 `speechPop` 같은 진입 애니메이션이 첫 프레임(`opacity:0`)에 멈춘다. `tmp/verify-86.js`처럼 캡처 직전 `document.getAnimations().forEach(a=>a.finish())`로 나머지를 끝까지 돌리고, 재고 싶은 애니메이션 하나만 `currentTime`으로 붙들어야 실제 화면과 같은 프레임이 나온다.

## 87. 정답 뒤 `다음 ▸`를 없애고 도장만 보여 준 뒤 자동으로 넘어간다

- 상태: 완료 (2026-08-04)
- 지시(2026-08-04): "문제를 맞추면 도장에 다음 버튼이 나오는데 이걸 다음버튼이 나오지 않고 **도장만 1초정도 보여주고 바로 넘어가도록**." → 검토 후 **지연은 1.5초(내레이션) / 2.5초(교사 말풍선)로 사용자 확정.**
- 대상: `showFeedback`(내레이션 도장 경로 + 교사 말풍선 경로), `armRandomContinue`(씬4), `#narrationAdvance`.
- 조치:
  - `showFeedback` 꼬리의 진행 표면 배선(`ensureAdvanceNav` + `surface.onclick=completeFeedback` + `nav.classList.remove('hidden')`)을 **타이머 한 줄로 대체**했다 — `feedbackAdvanceTimer=setTimeout(completeFeedback,useCharacter?FEEDBACK_ADVANCE_SPEECH_MS:FEEDBACK_ADVANCE_MS)`.
  - 상수 `FEEDBACK_ADVANCE_MS=1500` / `FEEDBACK_ADVANCE_SPEECH_MS=2500`를 `showFeedback` 바로 위에 뒀다. 1.5초는 **도장 애니(`--dur-slow` .65s)와 정답 음성이 둘 다 끝나는 시점**이다(`correct-1.mp3`는 64kbps·12KB ≈ 1.51초라 사용자가 말한 1초로는 끝을 못 맺는다). 교사 말풍선만 2.5초인 것은 **도장은 보는 즉시 읽히지만 글자는 읽어야 하기 때문**이다.
  - `feedbackAdvanceTimer`를 전역 타이머 목록(1033행)에 넣고 `resetFeedbackOverlay`에서 `clearTimeout` 한다. `showScene`이 그 함수를 타므로 씬 이탈 시 함께 걷힌다.
  - `feedbackContinueAction`은 **계속 세운다.** 26번의 오답 오버레이 가드(`showWrongFeedback` 첫 줄)가 이 값을 본다 — 안 세우면 정답 직후 들어온 오답 판정이 진행 경로를 지운다.
  - `armRandomContinue`에서 78번이 넣은 진행 버튼 라벨 분기(마지막 문항만 `모양으로 자유 그리기`)와 `nav.focus()`를 지웠다. 누를 것이 없으니 이름 붙일 대상도 포커스 옮길 대상도 없다.
  - `#narrationAdvance`(요소 + `.narration-advance` CSS)는 **참조 0이 됐지만 남겼다.** 되돌리기 여지도 있고, 그 CSS 주석이 `speechPop`의 `transform:scale()`과 `translateX(-50%)`가 부딪히는 함정을 적어 둔 유일한 자리라 292행이 그 주석을 참조한다.
- 검증: headless Chrome 1920×1080 (`tmp/verify-87.js` · `tmp/verify-87b.js`). 네 경로 전수 —
  - 씬2 찾기(내레이션): 정답 직후 도장 · `다음 ▸` 0개 → **+1.5초에 다음 문항**(`■모양…` → `●모양…`).
  - 씬2 삼각형(교사 `잘 찾았어요!`): 말풍선에 `다음 ▸` 없음, +1.2초 유지 → **+2.5초에 다음 단계**.
  - 씬3 산술: 도장 0~1200ms 유지 → **+1.6초에 입력칸이 비며 다음 문항**.
  - 씬4 무작위: 도장 0~1200ms 유지 → **+1.6초에 `#randomPanel[data-solved]`가 걷히며 다음 문항**.
  - 타이머 누수: 정답 직후 다른 씬으로 이탈시키고 3초를 기다려도 진행이 안 일어난다.
- 주의(다음 사람에게 필요한 것):
  - **오답도 도장을 낸다.** 자동화로 정답 순간을 잡을 때 `.feedback-mark.show`로 가르면 오답과 3회 오답 안전망(`setKeypadConfirmOnly`)까지 정답으로 오인한다 — `src`가 `feedback-stamp-correct`인지까지 봐야 한다. 검증 스크립트를 두 번 고친 이유가 이것이다.
  - **17·26번이 세운 데드엔드 위험은 사라졌지만 위험의 자리가 옮겨갔다.** 이제는 "진행 표면이 없다"가 아니라 **"타이머를 안 걷는다"**가 사고다. 도장을 띄우는 새 경로를 만들면 그 경로가 `resetFeedbackOverlay`를 타는지 반드시 확인한다(60번의 `heldStamp` 메모와 같은 이유).
  - **스크린리더 알림이 약해졌다.** 예전에는 `nav.focus()`가 `다음 문제` 버튼으로 포커스를 옮겨 정답을 읽어 줬는데 그 경로가 없어졌다. 지금은 정답 음성(`correct-1`)이 그 몫을 대신한다 — 음소거 상태의 스크린리더 사용자에게는 도장 이미지뿐이다. 필요해지면 `#narrationAdvance`를 시각적으로 숨긴 `aria-live` 영역으로 되살리는 것이 가장 싼 길이다.

## 88. 마우스 포인터를 1-2/01의 이미지 커서로 교체

- 상태: 완료 (2026-08-04)
- 지적: 08은 OS 기본 화살표를 쓰는데 01은 초등학생이 볼 수 있는 큰 이미지 커서를 쓴다. `CLAUDE.md:75` 표에 "커서 = 01의 `mouse-pointer.webp`"로 **기준이 이미 적혀 있었는데도** 이식이 빠져 있었다(problem.md `[cross-lesson-shell-inconsistency]` 4회차).
- 결정: **새로 그리지 않고 01 에셋을 그대로 복사한다.** 커서는 차시 고유 소재가 아니라 코스 공통 UI라 파일이 갈라지면 안 된다. `01/assets/ui/mouse-pointer.webp` → `08/assets/mouse-pointer.webp`(08은 평면 구조라 `ui/`를 만들지 않았다).
- 조치:
  - CSS에 `*{cursor:none !important}` + `#cursor` / `.cursor-image` / `.big` / `.readable-hover`를 **01과 같은 클래스명**으로 넣었다(`</style>` 직전). 08에 `cursor:pointer`가 20곳 넘게 흩어져 있어 명시도로는 못 이기고, "OS 커서는 무조건 숨긴다"는 원자적 강제라 `!important`를 썼다.
  - 마크업 `<div id="cursor" class="cursor-image">`는 **`#viewport`/`#stage` 밖**(디버그 패널 옆)에 뒀다. 안에 넣으면 transform 걸린 조상 때문에 `position:fixed`가 스테이지 기준으로 잡혀 포인터가 어긋난다(디버그 패널과 같은 이유).
  - JS는 스크립트 끝 `showScene(currentScene)` 직전 IIFE. `mousemove`로 `left`/`top`을 쓰고, 호버 판정은 `HOT`(누를 수 있는 것 → `.big`)과 `READ`(글 읽는 표면 → `.readable-hover`) 두 목록으로 갈랐다.
  - `assets/mouse-pointer.webp`에 `<link rel="preload">`를 걸었다. `*{cursor:none}`이 먼저 걸리므로 이미지가 늦으면 첫 마우스 이동에서 커서가 아예 없어 보인다.
- 값의 출처: **01의 CSS를 소스 순서로 읽지 않았다.** `tmp/probe-cursor-01.js`로 `getComputedStyle` 실측(4번·15번 교훈). 기본 `44×44` / `transform:translate(-5%,-4%)` / `opacity:.96` / 2겹 drop-shadow, `.big` `55×55` + 더 진한 그림자, `.readable-hover` `opacity:.94`.
- 검증: `tmp/verify-cursor-08.js`(headless Chrome, `getComputedStyle` 대조) — 08의 base/big/hover 세 상태가 01 실측값과 **전부 일치**. 그 외 확인한 것: 이미지 로드 성공, `#cursor`가 스테이지 밖(`insideStage:false`), `mousemove(640,400)` → `rect x638 y398`(translate 보정 반영), 호버 판정 `.cta`→`big` / `.speech`→`big readable-hover` / 배경→해제. 육안은 `tmp/shot-cursor-88.js`로 타이틀 화면 2컷 캡처(`tmp/cp-88/`).
- 주의:
  - **스테이지 배율 ×1.4056을 곱하지 않았다.** `#cursor`는 `position:fixed`라 `#stage`가 아니라 뷰포트 px이고, 01·08 모두 스테이지를 화면에 꽉 채우므로 44px 그대로가 화면상 같은 크기다. 15번의 "01 값은 그대로 옮기면 환산이 자동" 규칙과 결론은 같지만 **이유가 다르다**(그쪽은 `cqw`/`cqh`, 이쪽은 스테이지 밖이라서). 여기에 1.4056을 곱하면 01보다 커진다.
  - **조준선이 사라졌다.** `#drawingCanvas`(자유 그리기)·`#shapeSearch`(모양 찾기)의 `cursor:crosshair`가 `*{cursor:none}`에 덮인다. **2026-08-04 사용자 결정으로 그대로 뒀다.** 되살리려면 `*{cursor:none}`의 예외를 만들지 말고 그 두 곳에서 `#cursor`를 바꿔 끼우는 쪽이 맞다(OS 커서와 이미지 커서가 동시에 보이면 포인터가 두 개가 된다).
  - **01의 `.cspark`(클릭 반짝이 트레일)는 가져오지 않았다.** 01에서 이미 `.cspark{display:none!important}`로 꺼진 죽은 코드다. "01에 있는데 08에 없다"고 나중에 다시 이식하지 말 것.
  - `.speech`는 `role="button"`이라 `HOT`·`READ` 양쪽에 걸려 `big readable-hover`가 된다. 두 클래스가 겹치면 `.big` 크기(55px)가 이기므로 **`READ`가 실제로 보이는 곳은 `.prompt`뿐**이다. 01도 같은 구조다.
  - 터치 기기는 `@media (pointer:coarse){#cursor{display:none !important}}`로 막았다(01과 같은 방어). `*{cursor:none}`은 그대로 두는데, 터치에는 보일 커서가 없어 무해하다.

## 89. 세 수의 뺄셈은 뒤에서부터 지운다 (세모 → 네모)

- 상태: 완료 (2026-08-04)
- 요청: 씬4 마지막 문항(세 수의 뺄셈)이 화면에 `동그라미 네모 세모` 순으로 놓이는데 흐려지는(`.removed`) 순서가 `네모 → 세모`였다. **뒤에서부터, 즉 `세모 → 네모`** 로 지워야 하고, 힌트도 "세모를 빼서 10을 만들고 그다음에 네모를 빼라"가 되어야 한다.
- 조치:
  - `shapeStepsFor(5)`의 `groups`를 `[남는 것(a-b-c) 초록 ● / c 파랑 ■ / b 빨강 ▲]`으로 바꾸고 `steps`를 `[{op:'remove',group:2},{op:'remove',group:1}]`로 뒤집었다. **먼저 빠지는 b를 꼬리에 두는 것**이 핵심이다 — 지우기가 오른쪽 → 왼쪽 한 방향이 된다.
  - `renderRandom`의 `randomHintSteps`(type 5)를 같은 순서로 맞췄다. 1단계 `뒤의 빨강 ▲를 먼저 빼서\n10을 만들어 봐요.`(`focus:[2]`), 2단계 `이제 10에서 파랑 ■를\n빼 봐요.`(`focus:[1]`).
  - 49번이 남긴 "`[남는 것 / 빼는 b / 빼는 c]`" 주석을 새 배치로 고치고, 이유는 `shapeStepsFor` 안 89번 주석에 적었다.
- 검증: `tmp/verify-89-subtract-order.js` — `randomSequence`를 `[5]`로 줄인 사본을 headless Chrome 1920×1080으로 띄워 `.removed`가 붙는 순서를 100ms 폴링으로 기록. `16 - 6 - 1` 인스턴스에서 배치 `●×9 ■×1 ▲×6`, 제거 순서 index `15→14→13→12→11→10`(▲ 6개) 후 `9`(■ 1개)로 **오른쪽 → 왼쪽 단방향** 확인. 1단계 뒤 남는 도형 10개(`●9 + ■1`). 힌트 문구·`hint-step` 대상도 ▲ → ■ 순으로 확인.
- 주의:
  - **뺄셈만 그룹 배치가 항 순서와 다르다.** 41-a가 세운 "색·모양 매핑을 항 순서에 얹는다"는 규칙은 덧셈(type 3, 왼→오른쪽으로 쌓임)에서만 항 순서와 화면 방향이 일치한다. 뺄셈은 덜어내는 방향이 반대라 배치를 뒤집어야 방향이 맞는다. 나중에 "덧셈과 뺄셈이 비대칭"으로 보여 되돌리지 말 것 — 대칭인 것은 **배치**가 아니라 **진행 방향**이다.
  - 힌트 문구가 도형을 색·모양 이름(`빨강 ▲`)으로 부르므로, `groups` 배치를 바꾸면 `randomHintSteps`의 문구와 `focus` 번호를 **같은 자리에서** 함께 고쳐야 한다.
  - `type 1`·`type 4`(두 수의 뺄셈)는 제거 그룹이 꼬리 하나뿐이라 이미 뒤에서부터였다. 손대지 않았다.

## 90. 씬6 수리 이야기의 `다음 ▸`를 카드 우하단에 고정

- 상태: 완료 (2026-08-04)
- 요청: 표지판 설명 카드(`.story-card`)에서 `다음 ▸`가 beat마다 자리를 옮긴다. **한쪽에 고정한다 — 우하단으로.**
- 조치:
  - `.story-card .repair-bubble-nav`를 그리드 행에서 빼내 카드에 절대배치했다(`right:64px; bottom:153px; width:auto; margin-top:0`). 앵커는 크림 면의 오른쪽·아래 모서리(x 1236 = 1300−64 · y 447 = 600−153)다. 카드에 테두리가 없어 패딩 박스 = 1300×600이라 **아래 패딩을 늘려도 버튼은 안 움직인다.**
  - `.story-card`의 `padding-bottom`을 153 → **212px**(= 153 + 버튼 47 + 여백 12)로 늘려 버튼 자리만큼 글 영역을 줄였다. 안 줄이면 가장 긴 beat의 글이 버튼 위 22px까지 내려와 붙는다.
  - `renderStory`의 `insertAdjacentHTML('beforeend',ADVANCE_NAV_HTML)`는 그대로다. JS 변경 없음 — 버튼은 여전히 카드 안에 있어 `tabindex=-1` 클릭이 카드로 버블링된다.
- 검증: `tmp/measure-story-nav.js` — headless Chrome 1920×1080으로 6개 beat를 순서대로 넘기며 버튼 rect를 측정. 수정 전 버튼 y가 짧은 beat **284~330** ↔ 긴 beat **366~413**으로 82px 튀던 것이, 수정 후 6 beat 전부 **y 400~447 / x 1120~1236**으로 동일. 가장 긴 beat의 글은 y 140~348에 머물러 버튼까지 52px 여유. 캡처는 `tmp/shot-90.js`(`shots/v90-short.png`, `shots/v90-long.png`).
- 주의:
  - **`padding-bottom`(212)과 `bottom:153`은 한 쌍이다.** 버튼 크기(`.repair-narr-next`의 cq 단위 폰트·패딩)를 바꾸면 두 값을 함께 다시 잡는다. 33번이 잡아 둔 크림 면 비율(y 0.168~0.745 → 카드 101~447)이 여전히 기준이고, 카드 크기와 `.sign-row`는 이번에도 건드리지 않았다.
  - 이 절대배치는 `.story-card`에만 걸었다. 다른 씬의 `.repair-bubble-nav`는 말풍선 안 글 아래에 흐름으로 붙는 종전 형태 그대로다 — 말풍선은 글 길이에 따라 상자 자체가 자라 버튼이 글에 붙어 따라오는 것이 맞고, 카드는 상자가 고정이라 안이 흔들린 것이다.

## 91. `section_shape_find` 정답 번호 배지를 삼각형 도형 중앙에, 고깔모자는 포즈를 따라가게

- 상태: 완료 (2026-08-04)
- 요청: 삼각형 모양에 붙는 번호가 가운데가 아니다. 캐릭터가 움직이면 고깔이 왼쪽으로 살짝 움직이니 번호도 그걸 따라가야 하고, 삼각자는 **자 에셋 중앙**에 숫자를 붙여라.
- 원인: `.hotspot-number`가 `left:50%;top:50%`로 **핫스팟 박스**(손으로 잡은 사각형)의 중심에 붙어 있었다. 둘이 겹쳤다 — (1) 삼각형은 박스를 절반만 채우므로 박스 중심이 도형 중심이 아니고(삼각자는 배지 중심이 빗변 **밖**이었다), (2) `triangle_party_hat`의 핫스팟은 25번이 **세 포즈의 머리를 모두 덮도록 일부러 고정**한 박스인데 모자 **그림**은 `HAT_POSE_RECT`로 포즈마다 옮겨간다 → 오답 피드백으로 학생이 `thinking`이 되면 모자만 31px 왼쪽으로 가고 배지는 제자리에 남았다.
- 조치:
  - `findObjects[].numberAnchor` 도입 — **그 사물 `rect` 안의 비율**이다. 기본값은 `[.5,.5]`(그림 박스 중심)이고 두 삼각형만 값을 준다. `triangle_ruler:[.358,.642]` / `triangle_party_hat:[.501,.674]`.
  - 값은 **도형 내접원의 중심**이다. 배지가 72px(r 36)이라 삼각형 안에 온전히 들어가는 자리가 사실상 거기뿐이다 — 삼각자 내접원 r 37.9(중심 박스 기준 (60.9,109.1)), 고깔 r 37.4(중심 (85.6,115.2)). **알파 bbox 중심을 쓰면 안 된다**(삼각자에서 빗변까지 30.5px밖에 안 남아 배지가 도형을 넘는다).
  - `objectRect(id)`가 사물 그림의 **현재** rect를 준다(모자만 `HAT_POSE_RECT[sceneStudentPose]`, 나머지는 `findObjects[].rect`). `positionHotspotNumber(hotspot)`이 그 rect + `numberAnchor`로 stage 좌표를 잡고 핫스팟 원점을 빼서 `left/top`을 px로 쓴다. `revealSearchAnswers`가 배지를 붙인 직후 호출한다.
  - `positionPartyHat`이 모자를 옮길 때마다 `refreshHotspotNumbers()`를 불러 배지가 함께 간다.
- 검증: `tmp/shot-91.js` — headless Chrome 1920×1080으로 씬2 찾기 ■ → ● 를 정답 처리하고 ▲ 문항에서 3회 오답으로 번호를 띄운 뒤 배지·그림 rect를 stage 좌표로 측정. 배지 중심 삼각자 **(360.9, 204.1)**, 고깔 **(1230.7, 515.3)** = 계산값과 일치. 배경 클릭으로 오답 피드백을 내 학생이 `student-thinking`이 되자 모자 그림 x 1145 → 1114와 함께 배지 중심도 **1199.7, 512.2**로 −31/−3 이동(고정이었을 때는 핫스팟 중심 1221, 494에 그대로 남았다). 캡처는 `tmp/shots/v91-numbers.png`.
- 주의:
  - **`numberAnchor`는 비율이라 `rect`를 옮기면 배지가 자동으로 따라가지만, 에셋을 다시 그리면 값을 다시 재야 한다.** 알파 bbox가 아니라 내접원이므로 재는 법도 다르다 — 도형 세 꼭짓점을 잡고 `r=(a+b−c)/2`(직각삼각형) 또는 `r=넓이/s`로 중심을 낸다.
  - 배지가 커지면(72px 초과) 두 삼각형 모두 내접원을 넘는다. 크기를 키울 거면 `.hotspot-number`의 `width/height`와 이 두 앵커를 함께 본다.
  - 25번이 핫스팟을 고정해 둔 결정은 **그대로 옳다**(클릭 영역은 세 포즈를 다 덮어야 한다). 이번 수정은 클릭 영역이 아니라 **표시**만 그림 쪽에 물린 것이다.

## 92. 차시 목록 드로어의 닫기 버튼 × 를 버튼 중앙에

- 상태: 완료 (2026-08-04)
- 요청: 왼쪽 햄버거 메뉴(차시 목록)를 열면 나오는 **닫기 버튼의 × 가 버튼 중앙에 있지 않다**.
- 원인: 둘이 겹쳤다. 실측(스테이지 좌표)으로 잉크 중심이 박스 중심에서 **가로 +2.0px(오른쪽) · 세로 −2.5px(위)** 어긋나 있었다.
  - **가로** — `.course-menu-close`에 `display`·`padding` 지정이 없어 UA 기본 `padding:1px 6px`가 살아 있었다. `box-sizing:border-box`라 42px 박스의 콘텐츠 폭이 `42 − 6(테두리) − 12(패딩) = 24px`인데 `×` 의 advance는 **28px**이다. **글자가 콘텐츠 박스보다 넓으면 `text-align:center`가 음수 오프셋을 못 내고 넘치는 쪽(오른쪽)으로 흘러버린다.**
  - **세로** — 버튼은 **라인박스**를 중앙에 놓을 뿐이고, Jua의 `×` 는 잉크가 `baseline−20 ~ baseline−1`이라 잉크 중심이 `baseline−10.5`다. 라인박스 중심은 `baseline−8`이므로 잉크가 2.5px 위에 뜬다. 서체가 그린 글리프의 시각 중심이 라인박스 중심이 아니다.
- 조치: `.course-menu-close`에 `display:grid;place-items:center;padding:5px 0 0` 셋을 넣었다(width/height/색/테두리는 그대로).
  - `padding` 좌우 0 + grid 중앙 정렬로 가로 압착을 없앤다. 같은 파일 `.debug-close`가 이미 쓰는 방식이라 새 관례가 아니다.
  - 상단 패딩 5px이 콘텐츠 중심을 `5/2 = 2.5px` 내려 세로 잉크 오프셋을 정확히 상쇄한다.
- 검증: `node tmp/measure-menu-close.js` — headless Chrome 1920×1080에서 메뉴를 연 뒤 잉크 bbox(canvas `measureText`의 `actualBoundingBox*`)와 박스 중심을 비교. **offsetX 0.00 / offsetY −0.0000009** (수정 전 +2.0 / −2.5). `node tmp/shot-menu-close.js` 로 버튼을 8배 확대하고 박스 중심 십자선을 얹은 캡처(`tmp/menu-close-before.png` ↔ `after.png`)로 눈으로도 확인했다.
- 주의:
  - **라인박스 `getBoundingClientRect`로는 글리프가 중앙인지 판정할 수 없다.** 라인박스는 advance 폭·line-height 높이라 잉크와 다르다. 반드시 `actualBoundingBox*`(또는 확대 캡처)로 잰다.
  - 실측 스크립트를 쓸 때 **`getBoundingClientRect`는 device px(#stage 축소 배율 0.912가 곱해진 값)이고 canvas 폰트 메트릭은 CSS px**이다. 섞어서 계산하면 오프셋이 절반쯤으로 나온다(처음에 −1.3으로 잘못 나왔던 이유다). `tmp/measure-menu-close.js`는 rect를 전부 `br.width/offsetWidth`로 나눠 스테이지 좌표로 되돌린다.
  - **상단 패딩 5px은 서체(Jua)·박스 크기(42px)·글자 크기(28px)에 묶인 실측값이다.** 셋 중 하나라도 바뀌면 다시 잰다. Jua가 CDN에서 안 오면 대체 서체 메트릭이 달라 이 보정도 어긋난다.
  - **`production/1-2/01/index.html`의 `.course-menu-close`(30px 박스 / 20px 글자 / 같은 UA 패딩)가 같은 결함을 그대로 갖고 있다.** 08은 01에서 이식한 것이라 원본에 남아 있다. 이번 요청 범위가 08이라 건드리지 않았다 — 01을 손볼 때 함께 고친다(값은 박스·글자 크기가 다르므로 다시 재야 한다).


## 93. 주인공 아이를 "벽화 페인터" 캐릭터로 교체

- 상태: 완료 (2026-08-04)
- 요청: 주인공이 **일반 어린아이**라 차시 주제(학교 담장 벽화 색칠하기)와 겉돈다. 페인트 롤러를 들고 멜빵에 페인트 얼룩이 묻은 모습으로 바꾸되 **포즈·인물·크기는 그대로** 둔다.
- 조치(에셋): `student-idle.webp` / `student-thinking.webp` / `student-volunteer.webp` 3종을 페인터 버전으로 교체했다(codex 이미지 생성, `assets/preview-painter/`에 시안 보관). 1024×1536 RGBA 투명·발바닥 y 동일이라 파일만 갈아끼우면 되는 형태다. 롤러는 3종 모두 **내린 손에 아래로** 들렸고, 얼룩은 청록 멜빵과 주황 티셔츠에 흩어져 있다.
- 조치(앵커): 85번 규칙("인물 에셋을 바꾸면 이 표를 다시 잰다")대로 `tmp/measure-face.js` · `tmp/measure-side.js`를 재실행해 `--speech-side-x` 3줄을 고쳤다 — `student-thinking`.left 319 → **318**, `student-idle`.left 344 → **347**, `student-idle`.right 332 → **328**. `student-volunteer`.right는 368 그대로다. 얼굴 중심은 `student-idle`만 .214 → .215(렌더 0.6px)라 `--speech-face-y:707px`은 두었다.
- 조치(문서·alt): todo.md의 "캐릭터 알파 bbox" · "얼굴 중심 비율" · "밴드 실루엣" 세 표에 페인터 행을 더했고, 아이를 묘사하는 `alt` 9곳(3문구 × 각 2~4회)에 롤러·얼룩을 반영했다.
- 검증: `tmp/verify-93.js`(85번 스크립트 재실행) — 말풍선·실루엣 여백이 13개 자리 전부 **59~60px**, 꼬리−얼굴 0~−6px. `tmp/shot-93.js`로 씬1 b3(volunteer) · 씬2 대화(thinking) · 씬2 찾기(서 있는 idle + 고깔모자) · 씬3 beat(thinking/volunteer)를 1920×1080 캡처해 육안 확인했다.
- 주의: **앵커가 1~4px밖에 안 움직인 것은 롤러를 내린 손에 아래로 들렸기 때문이다.** 말풍선 밴드는 얼굴 중심 ±402px(원본 기준)이라 롤러가 그 밖에 있다. 시안 1차처럼 롤러를 어깨 높이로 세우면 밴드 안으로 들어와 이 표가 크게 흔들린다 — 포즈를 다시 손볼 때 이 조건을 유지한다.
- 주의: 학생에게는 `clip-path` 히트 영역 보정이 걸려 있지 않다(65번의 `clip-path`는 씬4 `.help-character` 하나뿐). 그래서 x 실루엣이 넓어져도 클릭 판정에 영향이 없었다.
- 미해결 아님(기록): 코덱스가 "주황 티셔츠에 얼룩 없음"을 O로 자가보고했지만 실제로는 티셔츠에도 얼룩이 남아 있다. 육안으로 자연스러워 그대로 채택했다. **코덱스의 자가 QA 보고를 그대로 믿지 말고 산출물을 직접 열어 볼 것.**

## 94. 씬4 오답 피드백에서 캐릭터 오버레이 제거

- 상태: 완료 (2026-08-04)
- 요청: 무작위 계산 문제(`section_random_problems`)에서 틀렸을 때 캐릭터가 피드백으로 나오지 않게 한다.
- 조치: `showWrongFeedback()`에 씬 제외 목록 `NO_WRONG_CHARACTER_SCENES=['section_random_problems']`를 두고, 도장(`showStamp(currentFeedbackMark(),'wrong')`)을 찍은 **직후·포즈 분기 앞에서** 빠져나가게 했다. 씬4의 오답 신호는 X 도장 + 오답음(`tone(false)`) + 흔들림(`shake`)만 남는다. 호출부(`judgeRandomChoice`·`judgeRandomKey`)는 건드리지 않았다 — 26번의 `feedbackContinueAction` 가드와 도장 경로를 그대로 타야 한다.
- 검증: headless Chrome 1920×1080에서 씬4 첫 문항(3지선다)의 오답 보기를 눌러 `#feedbackCharacter`가 `hidden`·`display:none`이고 `#randomMark`는 `feedback-stamp-wrong.webp`로 떠 있음을 확인. 같은 실행에서 씬3(`section_arithmetic_tutorial`) 키패드 오답도 함께 확인해 그쪽 오버레이는 종전대로 `display:block`으로 뜨는 것(회귀 없음)을 대조했다.
- 주의: 씬 이름은 리스트 한 곳(`NO_WRONG_CHARACTER_SCENES`)에만 있다. 다른 씬에서도 같은 요청이 오면 함수를 고치지 말고 이 배열에 id를 더한다.
- 주의(검증 스크립트용): `sceneStudentVisible()`은 현재 씬과 무관하게 `#shapeSceneStudent`의 `hidden`만 본다. 씬2를 거치지 않고 씬3·4로 점프하면 이 요소가 마크업 그대로 노출 상태(`resetShapeScene`이 안 돌아 `hidden`이 없다)라 오답이 **오버레이 대신 포즈 교체**로 빠진다. 실사용 흐름에서는 씬2를 반드시 지나므로 화면 문제는 아니지만, 씬을 점프하는 검증 스크립트는 이 요소를 먼저 숨기고 재야 한다.

## 93. 차시 목록 드로어 크기를 01과 동일하게 (×1.4056 환산 철회)

- 상태: 완료 (2026-08-04)
- 요청: 목록(차시 드로어)이 `production/1-2/01`과 똑같아야 하는데 **너무 크다**. 크기를 똑같이 맞춰 달라.
- 원인: **이식할 때 배율을 곱하지 말았어야 할 값에 곱했다.** 08은 01의 드로어 수치를 전부 ×1.4056(1920/1366) 해서 넣었는데(패널 400 → 562px, 항목 글자 18 → 25px, 번호 배지 34 → 48px), 01의 드로어는 `width:min(400px,40cqw)`·`font-size:clamp(13px,2.7cqh,20px)`처럼 **절대 px 캡에 걸려 있어 스테이지가 커져도 400px/20px에서 더 자라지 않는다.** 08의 `#stage`는 1920×1080 고정 후 `transform:scale`로 화면에 맞추므로, 곱한 값이 화면에서는 **01의 1.28배**로 그려졌다.
  - 실측(같은 1904×985 창, device px) — 패널 **400 vs 512.6**, 헤드 높이 51.7 vs 72.1, 항목 높이 51.8 vs 73, 번호 배지 34 vs 43.8, `지금` 배지 40.2×22 vs 52.7×28.3.
- 조치: `.course-menu-panel` / `-head` / `-grade` / `-close` / `-list` / `-item` / `-no` / `-title` / `-now` / `-soon` / `-foot` / `-home`과 `.is-current` 그림자까지 **01의 선언을 그대로** 되돌렸다. 테두리(3 → 2px)·모서리(18 → 13px 등)·그림자(`20px 0 51px` → `14px 0 36px`)도 함께 01 값이다.
  - **01의 `clamp()`+컨테이너 단위 식을 그대로 복사했다.** 08의 `#stage`가 `1920px × 1080px` 고정 `container-type:size`라 `cqw`/`cqh`가 상수(19.2 / 10.8)로 풀리고, 01의 설계 해상도(1920×1080)에서와 같은 값이 된다.
  - **처음에는 clamp를 손으로 풀어 정수 px로 넣었다가 되돌렸다** — `clamp(3px,.7cqh,9px)`=7.56을 8로, `clamp(2px,.55cqh,7px)`=5.94를 6으로 반올림하니 항목 pitch가 01의 59px에서 60px이 되어 10항목에서 10px 밀렸다. 손으로 풀지 말 것.
  - `.course-menu-close`(92번)의 상단 패딩도 박스가 42 → 30px, 글자 28 → 20px으로 바뀌면서 **5px → 4px**로 다시 쟀다.
- 검증:
  - `node tmp/measure-drawer-01-vs-08.js` — 01과 08을 같은 1920×1080 창에서 각각 띄워 드로어 전 요소의 rect·computed font-size를 대조. 폰트 크기(20/20, 18/18, 14/14, 17/17)와 패딩·gap이 전부 일치.
  - `node tmp/shot-drawer.js` 캡처(`tmp/drawer-01.png` ↔ `drawer-08.png`)를 픽셀로 대조 — **패널 오른쪽 경계 x=397로 동일**, x=360 열의 밝기 전이 y 좌표열(항목 경계)이 동일. 남은 차이는 (a) 현재 차시가 01은 6번·08은 8번이라는 내용 차이, (b) 닫기 × 가 08에서 2px 아래 — **92번으로 중앙에 맞춘 결과라 의도된 것**이다.
- 주의:
  - **01의 드로어는 스테이지 배율을 타지 않고 08의 드로어는 탄다.** 두 차시가 픽셀 단위로 같아지는 것은 뷰포트가 1920×1080(08 스테이지 배율 1.0)일 때다. 창이 더 작으면 08의 드로어는 topbar를 포함한 08 화면 전체와 **같은 비율로** 함께 줄어든다(1904×985에서 0.912배). 08 안에서는 일관되므로 이 상태가 맞다.
  - **다음에 01에서 무언가를 이식할 때 ×1.4056을 반사적으로 곱하지 말 것.** 기준 차시에서 그 값이 (a) 스테이지 비율에 묶였으면 환산하고, (b) 절대 px 캡(`min()`/`clamp()`의 max)이나 `position:fixed`처럼 스테이지와 무관하게 고정이면 **그대로 옮긴다**. 88번(커서)이 (b)를 맞게 판정한 사례고 이 항목이 틀린 사례다. 판정은 두 차시를 같은 창에 띄워 렌더된 px을 재서 한다.

## 95. 01의 키 누름 효과음을 모든 키패드 입력에 적용

- 상태: 완료 (2026-08-04)
- 요청: 01에서 쓰는 **다이얼(키패드) 누르는 효과음**을 08에도 가져와 **모든 다이얼 입력에서** 나게 해 달라.
- 조사에서 나온 것: **01은 이 소리를 mp3로 내지 않는다.**
  - 01의 키 누름은 전부 `playButtonSelectSfx()` = `playSfx('button-select', 0.75)`를 거친다(숫자 키·`DEL`·`OK` 모두).
  - 01의 `playSfx`는 `playSynthSfx`를 **먼저** 부르고, `SFX_SYNTH_MAP`에 `'button-select':'tick'`이 있어 **Web Audio 합성음**이 나가고 파일 경로에는 도달하지 않는다.
  - 즉 `01/assets/audio/sfx/button-select.mp3`는 **Web Audio가 없을 때만 쓰이는 폴백**이다. **그 파일을 복사해 왔다면 01에서 실제로 들리는 소리와 다른 소리가 났을 것이다.** 그래서 에셋이 아니라 합성 코드를 옮겼다(새 파일 0개).
  - 참고: `01/assets/audio/sfx/keypad.mp3`(→ 합성 `blip`)는 이름과 달리 **키 누름 소리가 아니다.** 01에서 `playSfx('keypad')`가 불리는 곳은 세는 수 표시가 바뀔 때(`updateRepairNumber`)와 카드가 모이는 연출 두 곳뿐이다.
- 조치: 01의 `ensureSynthCtx` / `synthTone` / `SFX_SYNTH.tick` / `playButtonSelectSfx`를 **같은 이름으로** `index.html`의 SFX 구역(`playSfx`·`tone` 아래)에 이식했다.
  - 소리 정의는 01의 `tick` 프리셋 그대로다 — C5(523.25Hz) 사인파가 90ms 동안 E5(659.25Hz)로 글라이드, `attack .004` / `release .07`, `vol 0.2 × v`.
  - 음량도 01과 같다. 01은 `playSfx('button-select', 0.75)`로 부르고 내부에서 `v = volume/0.9`(= 0.8333)를 프리셋에 넘기므로, 08은 합성 경로만 쓰기에 `SFX_SYNTH.tick(0.75/0.9)`로 그 계산을 펼쳐 뒀다.
  - `synthTone`의 vibrato·glide 분기는 `tick`이 쓰지 않지만 **01 원형 그대로** 남겼다(다른 프리셋을 더 옮길 때 재이식하지 않기 위해서다).
  - 거는 자리는 **`buildKeypad`의 `onclick`** 이다: `b.onclick=()=>{playButtonSelectSfx();handler(...)}`. 세 키패드(`countKeypad`·`arithKeypad`·`randomKeypad`)가 이 함수 하나를 공유하므로 한 곳이면 전부 붙는다. 누름 연출(`keypadPress`, pointerdown)이 아니라 click에 건 이유는 **키보드(Enter/Space)로 눌러도 나야 하기 때문**이고, 01도 onclick에서 낸다.
  - 음소거는 08의 `playSfx`와 같은 자리에서 막는다(`if(!soundOn)return`). AudioContext는 첫 키 누름(사용자 제스처)에 만들어져 자동재생 정책에 걸리지 않는다.
- 검증: `node tmp/verify-keypad-sfx.js` — headless Chrome에서 `AudioContext.prototype.createOscillator`를 감싸 주파수 스케줄을 기록하고 씬3을 도입 대사부터 실제 클릭으로 풀어 키패드까지 간 뒤 **12개 키(1~9 · ← · 0 · 확인)를 전부 클릭**했다. 결과 — 무음 키 **0개**, 키당 정확히 **1회**, 모든 톤이 `523.25 → 659.25`(01의 tick), 도입 대사 탭에서는 톤 0회(키패드에만 붙었다는 뜻), 음소거 중 **0회**, 음소거 해제 후 다시 **1회**.
- 주의:
  - **`.key` 버튼을 만드는 곳은 `buildKeypad` 하나뿐이다**(파일 전체에서 `className='key'`는 1곳). 새 키패드를 추가할 때 `buildKeypad`를 쓰지 않고 직접 만들면 소리가 빠진다.
  - 씬2·씬4 키패드는 활동을 끝까지 풀어야 나타나서 클릭 전수 검증은 씬3으로 했다. **셋이 같은 `buildKeypad`를 지나므로 코드 경로는 동일하다** — 검증 스크립트도 이 근거를 주석에 적어 뒀다.
  - 08에 Web Audio 경로가 생긴 것은 이번이 처음이다. 앞으로 01의 다른 합성 효과음(`correct`/`wrong`/`levelup` 등)을 더 가져오려면 `SFX_SYNTH`에 프리셋만 더하면 된다. **다만 08의 정답·오답은 이미 파일(`answer-correct.mp3`/`answer-wrong.mp3`)로 나가고 있으므로**, 합성으로 바꾸면 59번(효과음 재선정)에서 고른 소리가 바뀐다. 섞기 전에 확인이 필요하다.

## 96. 씬 전환 버튼에 인트로 시작음, 진행(다음 ▸) 표면에 키 누름음

- 상태: 완료 (2026-08-04)
- 요청: (a) `다음 ▸` 버튼도 누를 때 효과음을 내는 게 좋은지 물었고, (b) **다음 씬으로 넘어가는 버튼에 효과음이 필요하다. 첫 인트로 `시작하기` 버튼과 같은 소리를 쓰자.**
- (a)에 대한 근거: **01은 이미 그렇게 한다.** `01/index.html`의 `.repair-narr-next` 핸들러가 `playButtonSelectSfx?.()`를 부른다(다시듣기 버튼도 같다). 95번으로 옮겨 온 것과 **같은 소리**라 새 자산도, 새 소리도 필요 없다. 그래서 넣었다.
- **소리를 역할로 나눴다.** 두 소리가 말하는 것이 다르다.
  - **`intro-start.mp3`** = "**장면이 바뀐다**". 씬을 넘기는 전환에서만 난다.
  - **Web Audio `tick`**(95번, `playButtonSelectSfx`) = "**눌렀다**". 대사·beat를 넘기는 진행 표면에서 난다.
- 조치 1 — 씬 전환: `function goScene(id){playSfx('intro-start');showScene(id)}`를 `showScene` 옆에 두고 앞으로 가는 전환 6곳을 바꿨다.
  - `#introNext`(씬1→2) · `#shapeNext`(2→3) · `#arithNext`(3→4) · `nextRandom()`의 마지막 분기(4→5) · `#drawingYes`(5→6) · `#storyCard` 마지막 beat(6→7).
  - **`showScene`이 아니라 래퍼에 걸었다** — `showScene`은 종료 폴백(`#exitButton`)·QA 훅(`__contentHarnessShowScene`)·최초 진입도 타므로 거기서 내면 차시를 진행하는 전환이 아닌 데서도 소리가 난다. **씬을 넘기는 새 버튼을 만들면 `showScene`이 아니라 `goScene`을 부른다.**
  - 씬4→씬5는 87번으로 **버튼 없이 자동 진행**이 된 자리인데 여기에도 `goScene`을 썼다. 이 소리는 "버튼을 눌렀다"가 아니라 "장면이 바뀐다"는 신호라 사람이 눌렀는지와 무관하게 낸다는 판단이다. **원치 않으면 이 한 곳만 `showScene`으로 되돌리면 된다.**
- 조치 2 — 진행 표면(`playButtonSelectSfx()` 삽입): `#introTap` · `#shapeDialogueTap` · `#arithIntroTap` · `#drawingTap` · `#storyIntroTap` · `#storyCard`(마지막 beat 제외) · `stepRandomHint`(씬4 힌트의 `다음 ▸`/`닫기`, `#helpCard`·`#helpCharacter`가 부른다).
  - **`.repair-narr-next` 버튼에는 걸지 않았다.** 08의 그 버튼은 `tabindex="-1"`이고 핸들러가 없어 **클릭이 바깥 표면으로 버블링**되는 구조다(17·80번). 버튼에 따로 걸면 표면 핸들러와 **두 번** 난다.
  - 소리를 **가드 뒤에** 넣은 곳 둘: `#introTap`은 `if(introRepairing)return`(수리 연출 중 탭 무시) 뒤, `stepRandomHint`는 `if(randomAwaitingContinue)return` 뒤다. 앞에 넣으면 **아무 일도 안 일어나는 클릭에서 소리만 난다.**
  - `#storyCard`는 한 표면이 beat 진행과 씬 전환을 겸한다. `playButtonSelectSfx()`를 **비-마지막 분기 안에** 넣어 마지막 클릭에서 두 소리가 겹치지 않게 했다.
- 검증: `node tmp/verify-advance-sfx.js` — `Audio` 생성자와 `AudioContext.prototype.createOscillator`를 감싸 클릭마다 무엇이 났는지 세고, 씬1을 시작하기부터 대사 끝까지 실제 클릭으로 풀어 씬2로 넘기고 씬3 대사·씬6 카드까지 눌렀다.

  | 조작 | intro-start | tick |
  | --- | --- | --- |
  | 씬1 `시작하기` | 1 | 0 |
  | 씬1 대사 탭(각) | 0 | 1 |
  | 씬1→2 `#introNext` | 1 | 0 |
  | 씬3 대사 탭 | 0 | 1 |
  | 씬6 카드 beat | 0 | 1 |
  | 씬6→7 마지막 카드 | 1 | 0 |

  수리 연출이 도는 동안의 탭은 **둘 다 0**이었다(`introRepairing` 가드가 먹는다는 뜻).
- 주의:
  - 클릭 전수 검증은 씬1·3·6으로 했다. `#shapeNext`·`#arithNext`·`#drawingYes`·`nextRandom`은 **같은 `goScene` 한 줄**이라 코드 경로가 같다(치환 시 각 문자열이 파일에 1곳뿐임을 확인했다).
  - `#exitButton`의 `showScene('section_intro')`는 **일부러 그대로 뒀다** — 앞으로 가는 진행이 아니라 나가기 폴백이다.
  - 씬7 완료의 `다음 차시` 버튼은 씬 전환이 아니라 **다른 차시로 나가는 것**이라 범위에서 뺐다. 여기에도 소리를 넣을지는 결정이 필요하다.

## 97. 작업자(worker) 대사 10본 재녹음 교체

- 상태: 완료 (2026-08-04)
- 대상: `assets/audio/script/` 작업자 키 10개 · 원본 `assets/add_audio/Take{1~10}-1_*_2026-08-04.wav`
- 사용자 지시: "`assets/add_audio`에 worker의 음성을 새로 추가해뒀다. 기존 worker의 음성을 전부 그 음성으로 바꿔라."
- 조치:
  - 45번 규칙대로 **같은 키 이름으로 덮어썼다. `index.html`은 한 줄도 건드리지 않았다.** 코드가 쓰는 배역별 키 목록은 `supertone-script-map.md`의 `01-worker.txt` 행이 기준이고, 작업자 대사는 정확히 10개라 새 테이크 10본과 1:1로 맞았다.
  - 납품이 wav인데 기존 자산은 mp3라 **`libmp3lame -b:a 64k -ac 1 -ar 44100`으로 변환**해 넣었다(기존 59본의 실측 인코딩과 같은 값). 시스템에 `ffmpeg`이 없어 `python -c "import imageio_ffmpeg"`가 주는 번들 바이너리를 썼다.
  - 원본 테이크 ↔ 키 대조표(2026-08-04 재녹음분):

| Take | 키 | Take | 키 |
| --- | --- | --- | --- |
| 1 | `intro-1-apology` | 6 | `arith-beat-thanks` |
| 2 | `intro-2-wall-fixed` | 7 | `arith-beat-erase-2` |
| 3 | `intro-3-need-help` | 8 | `arith-beat-erase-3-more` |
| 4 | `arith-beat-can-ready` | 9 | `arith-outro-1-well-done` |
| 5 | `arith-beat-paint-2-more` | 10 | `arith-outro-2-more-walls` |

- 검증: `git status`로 **정확히 그 10개만 `M`**임을 확인했다. 10본 모두 44100Hz mono 64kb/s로 다시 열리고 길이는 1.33~3.87초다. `volumedetect`로 새 3본(mean −24.3/−22.9/−20.4dB)과 손대지 않은 다른 배역 6본(−22.5~−24.1dB)을 비교해 **레벨이 같은 대역**임을 확인했다 — 작업자만 튀지 않는다.
- 주의:
  - 대사 문구가 화면 텍스트와 **글자만 다르고 읽는 소리는 같은 자리가 3곳**이다. `1통을 더 준비했어요`→녹음 `한통을`, `3개를 더 지우고 싶어요`→녹음 `세개를`, `휴,`→녹음 `휴~,`. 화면 텍스트는 그대로 뒀다(읽으면 같은 소리다).
  - 옛 mp3는 git에 남아 있다(전부 tracked였다). 되돌리려면 `git checkout -- assets/audio/script/`.
  - `assets/add_audio/`는 **납품 인박스라 다음 배치가 오면 비워진다.** 이 10본의 wav도 98번 배치가 들어오면서 사라졌다(mp3만 남는다). 원본 대조가 필요하면 이 항목의 대조표를 쓴다.

## 98. 씬3 도입 대사 4본 재녹음 교체

- 상태: 완료 (2026-08-04)
- 대상: `assets/audio/script/` 4개 키 · 원본 `assets/add_audio/Take{2~5}-1_*_2026-08-04.wav`
- 사용자 지시: "add_audio에 새로 오디오 추가했다. 이 음성으로 기존 걸 바꿔라."
- 조치: 97번과 같은 절차 — 같은 키 이름 mp3로 덮어쓰기(`libmp3lame -b:a 64k -ac 1 -ar 44100`), `index.html` 무수정.

| Take | 키 | 배역(스크립트 기준) | 길이 변화 |
| --- | --- | --- | --- |
| 2 | `arith-intro-1-we-will` | 주인공 | 2.72 → 2.04초 |
| 3 | `arith-intro-2-this-is-paint` | 주인공 | 4.55 → 4.36초 |
| 4 | `arith-intro-3-ten-per-can` | 주인공 | 3.24 → 2.85초 |
| 5 | `arith-q-add-7-3` | **내레이션** | 3.58 → 3.63초 |

- 검증: `git status`로 그 4개만 새로 `M`이 된 것을 확인(97번의 10개와 합쳐 14개). 4본 모두 44100Hz mono 64kb/s로 다시 열린다.
- 주의:
  - **레벨이 다른 배역보다 3dB 높다.** 납품 wav 4본이 전부 `mean_volume −20.0dB`로 **출력 시 라우드니스 정규화된 값**이다(97번 작업자 배치는 −20.4~−24.3으로 제각각이었다). 손대지 않은 다른 배역은 −22.5~−24.1dB다. 지금은 **납품 원본을 그대로 뒀다** — 맞추려면 `volume=-3dB`로 다시 굽는다.
  - **`Take1`이 배치에 없다.** 씬3 도입 순서상 앞줄인 `shape-outro-2-request`(교사 "페인트 소개를 부탁해요!")가 Take1 자리로 보이는데 오지 않았다. 다음 배치에서 오는지 확인이 필요하다.
  - **`arith-q-add-7-3`은 스크립트상 내레이션 자리다.** 이 배치가 주인공 목소리면 그 한 문항만 화자가 바뀐다(45번 원본은 Take22 `일곱 개에서…`였고 이번 파일명은 `7개에서…`라 읽기 교정본으로 보인다). 사용자 확인 대상.
  - 화면 텍스트와 녹음 문구가 글자만 다른 자리 1곳: 화면 `1통에 모양을 10개씩` → 녹음 `한통에`. 읽으면 같은 소리라 화면은 그대로 뒀다.
