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
