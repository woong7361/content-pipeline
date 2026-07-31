# 1-2/08 수정 목록

기준 참고 차시: `production/1-2/01` (같은 선생님 스토리보드). 공통 규칙은 같은 폴더의 `CLAUDE.md` 참조.

상태 표기: `열림` / `진행중` / `완료` / `보류`

## 씬 순서 (현재 index.html)

| # | id | stage 라벨 | 비고 |
| --- | --- | --- | --- |
| 1 | `section_global_ui` | 수리력 + | 공통 UI + 활동 목표(overview 3칸) |
| 2 | `section_intro` | 수리력 + | 타이틀 로고 + 시작하기 + 작업자 대화 |
| 3 | `section_shape_find` | 수리가 필요해요 1 | 모양 찾기와 세기 |
| 4 | `section_arithmetic_tutorial` | 수리가 필요해요 2 | 세 수의 덧셈과 뺄셈 |
| 5 | `section_random_problems` | 수리로 해결해요 | 무작위 계산 문제 |
| 6 | `section_free_drawing` | 수리로 해결해요 | 모양으로 자유 그리기 |
| 7 | `section_math_story` | 수리 이야기 | |
| 8 | `section_completion` | 수리 이야기 | |

---

## 1. header를 1-2/01 방식으로 수정

- 상태: 진행중 (시각 양식 이식 완료 / 코스 메뉴 드로어·나레이션 다시듣기 미결)
- 완료(2026-07-31): 01 `topbar`의 CSS 값을 그대로 이식했다. `.topbar`(56px, 크림 유리 그라디언트 + 하단 보더) > `.topbar-left`(`.btn-home.course-menu-btn` 햄버거+목록 → `.header-voice-volume-button` 원형 스피커 SVG → `.step-label` 금색 세로 구분선) / 중앙 절대배치 `.lesson-header-title` + 금색 밑줄 / 우측 `.lesson-bar-reward`(track+fill+`%`). 클래스명·구조는 01에서 그대로 가져왔다. `sceneMeta`는 `title` → `stage`(01의 stageLabels 사다리)로 바꾸고 `progress`를 숫자로 통일해 기존 `setProgress()` 호출을 lesson-bar에 연결했다. 서체는 01과 같은 Noto Sans KR을 `--font-topbar`로 topbar에만 적용(폴백 `--font-body`). 제거: 08 자체 3단계 chip, `assets/global-hud-frame.png` 프레임(파일은 남겨 둠). 검증: 01(title-mode topbar 숨김만 해제한 사본)과 08을 로컬 HTTP + headless Chrome 1920x1080으로 캡처해 상단 60px를 나란히 비교, 위치·크기·서체 일치 확인.
- 남은 것: 01의 `installCourseMenu()` 드로어(`ui.courseMenu` 데이터로 차시 이동)와 `#headerNarrationReplay`(나레이션 다시듣기). 08의 `menuButton`은 아직 차시 목록이 아니라 씬 이동 드로어(`#menuDrawer`)를 연다. 아래 "확인 필요"가 정해져야 착수 가능.
- 목표: 1-2/01의 헤더 구조·동작에 맞춘다.
  - 01은 `installCourseMenu()`가 `#btnHome`을 햄버거 + "목록" 버튼으로 바꾸고, `lesson.json`의 `ui.courseMenu`(번호/제목/`id` 또는 `path`) 데이터로 좌측 드로어를 띄운다. `current`와 일치하는 항목은 활성 + "지금" 태그.
  - 01 헤더 요소: `.topbar-left`(`#btnHome`, `#headerNarrationReplay`), `#probGauge`, `#pReward` pill.
- 확인 필요: 08에는 `lesson.json`이 없다. 코스 메뉴 데이터를 (a) `lesson.json`을 새로 만들어 넣을지, (b) index.html 내부 상수로 둘지 결정 필요.
- 확인 필요: 08의 소리 조절 버튼(`soundButton`)과 진행률 바(`lessonBar`)를 유지할지, 01의 나레이션 다시듣기 + pill 구성으로 교체할지.

## 2. 가장 첫 번째 페이지 삭제

- 상태: 열림
- 요청 원문에 "(intro인가?)"로 적혀 있으나, 실제 **첫 화면은 `section_intro`가 아니라 `section_global_ui`**(공통 UI + 활동 목표 3칸 overview)다. `section_intro`는 두 번째 화면이다.
- 확인 필요: 삭제 대상이 `section_global_ui`인지 `section_intro`인지 확정할 것. (문맥상 `section_global_ui`로 추정)
- 삭제 시 함께 손봐야 할 것:
  - `SCENE_META`(index.html 442~449줄 부근)의 해당 항목 제거 및 나머지 `progress` 값 재배분.
  - 첫 씬의 `class="scene active"` 이동.
  - `data-qa-order` 재번호.
  - 삭제되는 씬에서만 쓰는 에셋 정리(`overview-mural-triptych-frame.png`, `school-wall-wide.png` 등).

## 3. title을 CTA 이미지로 변경

- 상태: 완료 (2026-07-31)
- 해석 확정: (a) **타이틀 로고 에셋 교체**였다. (b) CTA 버튼의 이미지화가 아니다 — 그건 4번에서 CSS 버튼으로 이미 처리됐다.
- 조치: `assets/colorful-school-wall-title.png`를 01 `assets/ui/title-logo.png` 화풍으로 재생성했다. 금빛 그라데이션 + 두꺼운 갈색 외곽선/베벨 + 별 장식 + 2줄 구성까지 01과 같은 계열로 맞춰졌다. **파일명과 마크업(`#introTitleSurface` > `.intro-title-img`)은 그대로라 CSS·JS 변경은 없다.**
- 검증: 두 로고를 나란히 육안 비교 — 색감·외곽선 두께·베벨·별 장식이 같은 작가 결과물로 보인다. 이전 에셋의 "납작한 노랑" 문제 해소.
- **9번 오프셋 재계산 불필요.** 새 에셋 `1909×824`, 알파 bbox `(48, 100, 1848, 758)` — 이전 에셋의 y 범위(100~758 / 824)와 **동일**하다. 따라서 `#section_intro #introStartWrap{translate:0 calc(-50% - 140px)}` 값을 그대로 둬도 담장 가림이 재발하지 않는다.
- 이 항목으로 "확인이 필요한 항목" 2번·7번이 함께 해소됐다.

## 4. title "시작하기" 버튼을 1-2/01 방식으로 변경

- 상태: 완료 (2026-07-31)
- 조치: 01의 타이틀 화면을 통째로 이식했다. `#introStartWrap` > `.intro-title-copy` > `.intro-title-img` + `#introStart` 구조, `titleLogoDrop` / `ctapulse` / `shimmer` 애니메이션, `title-mode`(타이틀 화면에서 topbar 숨김)까지 01과 같은 이름으로 가져왔다.
- **주의 — 01의 CSS는 소스 순서로 읽으면 틀린다.** `#introStartWrap .intro-start-cta`(네이비 테두리 + 금색)는 뒤쪽 `#app .cta,#app #introStartWrap .intro-start-cta`(명시도가 더 높음)에 덮여 죽은 규칙이다. 실제 적용값은 `getComputedStyle`로 읽어야 한다. 실측값(1366 기준):
  - `547.19 × 63.86`, `min-height:58px`, `padding:13px 34px 15px`, `border:2px solid rgba(161,98,7,.52)`, `border-radius:999px`
  - 배경 `linear-gradient(180deg,#fef08a,#facc15 36%,#eab308 72%,#ca8a04)` + 흰 광택 레이어
  - 글자 `Jua` 27px/31.86 900, 색 `#713f12`
  - `box-shadow: inset 0 3px 0 rgba(255,255,255,.56), inset 0 -4px 0 rgba(120,53,15,.12), 0 4px 0 rgba(120,53,15,.28), 0 8px 22px rgba(66,32,6,.18)`
  - 08에는 위 값을 × 1.4056 (= 1920/1366) 해서 넣었다.
- **01의 서체는 Noto Sans KR이 아니라 `Jua`다.** 13번째 줄 `<style>`의 `font-family:"Noto Sans KR"...`를 15번째 줄 `html,body,button,...{font-family:"Jua",...}`가 덮는다. 01의 topbar·본문·버튼 전부 computed font가 `Jua`임을 실측 확인했다.
- 2026-07-31 결정: **01처럼 전역 적용.** `--font-body`를 `"Jua","Noto Sans KR","Apple SD Gothic Neo",sans-serif`로 바꾸고, `--font-topbar`/`--font-title`은 `var(--font-body)` 별칭으로 정리했다(이전에 topbar에만 Noto Sans KR을 걸어 둔 것은 위 소스순서 오해에서 나온 값이라 폐기). `button,input,textarea,select{font:inherit}`로 폼 요소까지 01과 동일하게 상속시켰다. 웹폰트 링크도 01과 같은 `family=Jua&family=Noto+Sans+KR:wght@400;700;900`으로 맞췄다.
- **미검증 — 이 개발 PC에서는 Jua 렌더를 확인할 수 없다.** headless Chromium이 `fonts.googleapis.com`에 `net::ERR_SSL_PROTOCOL_ERROR`로 실패한다(TLS 가로채기 프록시를 크로미움이 신뢰하지 않음. curl은 200). **1-2/01도 같은 이유로 이 PC에서는 Jua가 아니라 폴백으로 렌더된다** — 즉 08만의 문제가 아니라 환경 문제다. 실제 브라우저에서 육안 확인이 필요하다.
- 폴백 경로(Jua 미로드 시 Noto Sans KR)로 8개 씬을 전수 캡처해 넘침을 점검했고 회귀 없음. Noto Sans KR이 Malgun Gothic보다 좁아서(100px 기준 672 vs 735) 오히려 여유가 늘었다.
- 후속 후보: 오프라인에서도 서체가 보장돼야 하면 Jua를 `assets/fonts/`에 self-host하고 `@font-face`로 거는 방법이 있다(01은 안 하고 있어서 지금은 01과 동일하게 CDN 의존 상태로 뒀다).

## 5. 화면 전환 애니메이션 추가

- 상태: 열림
- 현재: 08은 `.scene`에 `active` 클래스를 토글할 뿐 전환 효과가 없다.
- 목표: 01과 동일한 전환을 적용한다.
  - `#app.stage-fade-out` → `opacity:0; transition:.42s ease`
  - `#app.stage-fade-in` → `@keyframes stageFadeIn .45s ease both`
  - `#app[data-transition="slide"]` → `stageSlideOutRight` / `stageSlideInRight` (`translateX(0 → 100%)`, `-100% → 0`)
- 씬 전환 지점(모든 `.cta` 다음 씬 이동 핸들러)에 fade-out → 씬 교체 → fade-in 순서로 연결한다.

## 6. 말풍선을 1-2/01과 동일하게 변경

- 상태: 열림
- 현재(08): `.speech`가 배경 이미지 `assets/school-speech-bubble-body.png` 기반, 고정 크기 990×190px, `background-size:1980px 190px`. 크기 고정이라 대사 길이에 따라 넘치거나 남는다.
- 목표(01): CSS로 그린 말풍선으로 교체.
  - `background:#fffdf6`, `border:4px solid #4c3428`, `border-radius:20px`, `box-shadow:0 7px 0 rgba(0,0,0,.18)`
  - 꼬리는 `::before`(테두리색) / `::after`(배경색) 삼각형 2겹
  - `font-size:clamp(14px,1.4cqw,19px)`, `font-weight:900`, `word-break:keep-all`, `text-wrap:balance`
  - 등장 애니메이션 `.speech-pop` (`speechPop .4s cubic-bezier(.36,.07,.19,.97)`)
  - 좌/우/하단 화자 위치 변형 유지 (08의 `left-speaker` / `right-speaker`에 매핑)
- 교체 후 `school-speech-bubble-body.png` 사용처가 없으면 에셋 정리.

## 7. "수리가 필요해요 1"의 모양 찾기 대폭 변경

- 상태: 열림
- 대상: `section_shape_find` (모양 찾기와 세기)
- 현재: 배경 `assets/school-yard-shape-search.png`(학교 마당) 위에 `hotspotDefs`로 정의한 좌표 핫스팟을 눌러 동그라미·세모·네모를 찾는 방식. 찾을 대상이 배경 그림에 굳어 있어 위치·난이도 조정이 불가능하다.
- 목표:
  - 배경에 굳힌 그림 대신 **개별 에셋(도형이 들어간 사물)을 배치**하는 방식으로 전환 검토.
  - 장소를 **학교 마당 → 교실 안**으로 변경.
- 교실 안에서 찾을 도형 사물 후보 정리 필요 (예: 동그라미 — 시계/공, 세모 — 삼각자/깃발, 네모 — 창문/책상/사물함/칠판).
- 확인 필요: 새 교실 배경 에셋을 생성할지, 기존 담장 계열 톤과 어떻게 이어갈지.
- 에셋 생성 시 `1-2/01/lesson.json`의 `artDirection`을 그대로 반영할 것.

## 8. 동그라미·세모·네모 에셋 배경 투명 처리

- 상태: 열림
- 7번에서 만들 도형 에셋은 **배경 투명 PNG**로 만든다. 씬 배경 위에 얹히므로 흰 사각형이 보이면 안 된다.
- 현재 08의 도형은 에셋이 아니라 CSS(`.paint-shape.circle/.square/.triangle`)로 그려져 있다. 에셋으로 전환할 경우 `paintIntroVisual`, `countShapes`, `arithShapes`, `randomWorkProgress`에서 쓰는 도형 표현을 함께 바꿀지 결정 필요.
- 확인 필요: 도형을 전면 에셋화할지, 찾기 씬에서만 에셋을 쓰고 계산 씬은 CSS 도형을 유지할지.

## 9. 도입 타이틀 이미지가 담장을 가리지 않도록 위로 이동

- 상태: 완료 (2026-07-31)
- 대상: `section_intro`의 `#introStartWrap` (타이틀 `#introTitleSurface` + `#introStart` 시작 버튼 컬럼)
- 요청: 타이틀 이미지를 위로 올려 배경의 학교 담장을 가리지 않게 할 것.
- 배경 측정: `school-wall-damaged.png`(1672x941, cover 배율 1.148)의 담장 기둥 윗면이 stage 좌표 **y≈550** (캡처 픽셀 스캔). 타이틀 에셋은 알파 bbox가 y 100~758/824라, 폭 1068px로 그리면 높이 461px 중 실제 그림은 박스 상단 **+56 ~ +424** 구간에만 있다.
- 조치: 01과 같은 정중앙 배치(`top:50%` + `translate:0 -50%`)로는 컬럼 상단이 y≈249라 그림이 y 305~673을 차지해 담장을 덮었다. **`#section_intro #introStartWrap{translate:0 calc(-50% - 140px)}`** 로 140px 올려 그림이 y **165~533**, 담장 윗면 바로 위 하늘에 놓이게 했다.
- 01 규칙(`#introStartWrap{top:50%;translate:0 -50%}`)은 건드리지 않고 씬 스코프 오버라이드만 추가했다. 명시도는 id 2개 > id 1개라 `!important` 불필요.
- 시작 버튼도 컬럼째 함께 올라가 y 594~691, 담장의 깨끗한 면 위에 놓인다(이전에는 y 734~831로 바리케이드·콘과 겹쳤다).
- 검증: headless Chrome 1920x1080 캡처에서 담장 전체·무너진 구간·벽돌 더미·콘·바리케이드가 모두 드러나고 타이틀이 상단 헤더와 겹치지 않음을 확인. (실제 런타임에서는 `#stage.title-mode`로 topbar가 숨겨져 여유가 더 있다.)
- ~~주의: 3번(타이틀 CTA 이미지 교체)에서 로고 에셋이 바뀌면 알파 bbox가 달라지므로 140px 오프셋을 다시 계산해야 한다.~~ → 2026-07-31 3번 완료 시 재측정 결과 새 에셋의 알파 bbox가 `(48,100,1848,758)/824`로 **이전과 동일**해 재계산 불필요했다. 다만 앞으로 로고를 또 바꾸면 이 확인은 다시 해야 한다.

## 10. 디버그 패널 (` 키) — 씬 자유 이동

- 상태: 완료 (2026-07-31)
- 요청: `` ` `` 를 누르면 우측에 디버그 모드가 나타나고, 거기서 각 씬으로 마음대로 이동할 수 있게 한다. (처음엔 `` Ctrl+` `` 였으나 단독 `` ` `` 로 변경)
- 조치:
  - 패널을 `#stage` **밖**(`<body>` 직속, `position:fixed`)에 두었다. `#stage`는 `resizeStage()`에서 `scale()` + 세로 화면 `rotate(90deg)`가 걸리므로 안에 넣으면 패널도 같이 축소·회전된다.
  - 씬 목록은 하드코딩하지 않고 `.scene`의 `data-qa-order` / `data-qa-label`에서 생성한다(`buildDebugScenes`). 씬이 늘거나 순서가 바뀌면 자동 반영된다.
  - 이동은 기존 `showScene(id)`를 그대로 쓴다. 씬별 `reset*()` 초기화가 `showScene` 안에 있어 어느 씬으로 건너뛰어도 상태가 깨지지 않는다.
  - 점프할 때 `unlockedMenuScenes`를 전부 해제한다. 그러지 않으면 뒤 씬으로 건너뛴 뒤 상단 "목록" 드로어가 잠긴 채로 남는다.
  - 현재 씬은 초록 테두리로 표시하고 `showScene` 끝에서 `syncDebugPanel()`로 갱신한다(패널을 열어 둔 채 정상 진행해도 표시가 따라간다).
  - `Esc`로도 닫힌다. `<input>`/`<textarea>` 포커스 중에는 토글하지 않는다. `Alt`/`Meta` 조합은 제외해 브라우저 단축키와 겹치지 않게 했다.
- 남은 결정: 지금은 **항상 활성**이다. `production/`은 학생에게 나가는 산출물이므로 `?debug=1` 같은 플래그 게이팅을 걸지 결정 필요.
- 범위: 08 전용. 검증 후 `content-harness-pipeline/prompts/common_html_contract.md`로 승격할지는 별도 판단.

## 11. section_intro — 담장 수리 망치 모션 + 수리 애니메이션

- 상태: 열림
- 대상: `section_intro`의 `introBeats` 0 → 1 구간
- 현재: 대사 0(`공사 중에 실수로 담장을 무너뜨렸어요`, `bg:'school-wall-damaged.png'`)에서 대사 1(`휴, 담장은 다 고쳤어요`, `bg:'school-wall-repaired.png'`)로 넘어갈 때 **`introBg`의 `src`만 즉시 교체**된다. 고치는 과정이 전혀 보이지 않고 담장이 순간이동으로 붙는다.
- 목표:
  - 무너진 담장 구간 위에 **망치가 뚝딱뚝딱 내려치는 모션**을 보여준다.
  - 그에 맞춰 담장이 **점차 수리되는 애니메이션**으로 damaged → repaired 전환을 연출한다.
- 구현 후보:
  1. 망치 에셋(`hammer-*.png`) 1장 + CSS `@keyframes`로 회전 왕복(`rotate(-35deg) ↔ rotate(5deg)`) 3~4회 + 타격 순간 임팩트(작은 별/먼지 파티클, `translate` 흔들림).
  2. 담장 전환은 `damaged`/`repaired` 두 배경을 겹쳐 놓고 위층(damaged)을 `clip-path`로 왼쪽→오른쪽 벗겨내거나, 망치 타격 박자에 맞춰 단계별 `opacity` 전환.
  3. 무너진 구간 좌표를 알아야 망치를 정확히 올릴 수 있다. 9번에서 쓴 방식(캡처 픽셀 스캔)으로 `school-wall-damaged.png` 위 붕괴 구간의 stage 좌표를 먼저 측정할 것.
- 필요 에셋: 망치(투명 배경 PNG, `artDirection` 준수). 작업자가 직접 망치를 드는 포즈로 갈 경우 `worker-hammering.png` 캐릭터 컷이 추가로 필요하다.
- 확인 필요: 망치를 **떠 있는 아이콘**으로 둘지, **작업자 캐릭터가 드는 형태**로 갈지. 후자면 캐릭터 에셋이 늘어난다.
- 확인 필요: 애니메이션 동안 대사·탭 진행을 잠글지(연출 끝나야 다음 대사), 아니면 탭으로 스킵 가능하게 할지.
- 5번(화면 전환 애니메이션)과 별개다. 이건 씬 **내부** 연출이다.

## 12. section_arithmetic_tutorial 입력기를 1-2/01 방식으로 변경

- 상태: 열림
- 대상: `section_arithmetic_tutorial`의 `#arithKeypadWrap` / `#arithKeypad` / `#arithDisplay`
- 현재(08): `.keypad-wrap` + `.keypad`(3열 그리드) 뿐이다. 키 배경은 `wall-choice-plaque-body.png`를 4겹 `background-image`로 깔아 행 배경만 흉내 냈고, **누름 피드백·표시 틱 등 상호작용 연출이 없다.**
- 목표(01): 01의 키패드 구현을 그대로 가져온다.
  - `keypad-panel` (패널 껍데기)
  - `keypadInput()` / `keypadPress()` (입력·누름 처리)
  - `.keypad-pressing` (누르는 순간 키 상태 — 08에 없음)
  - `keypadDisplayTick` (답 표시 영역 갱신 시 틱 연출 — 08에 없음)
  - `keypadControlsHtml` / `keypadRight` (지우기·확인 등 컨트롤 배치)
- **01의 CSS는 소스 순서로 읽으면 틀린다.** 4번 항목에서 확인한 문제와 같다. 값은 반드시 `getComputedStyle` 실측으로 가져오고, 1366 → 1920 배율 **× 1.4056**을 적용한다.
- 08의 다른 키패드(`#countKeypad` in `section_shape_find`, `#randomInput` in `section_random_problems`)도 같은 스타일을 쓴다. **한 씬만 바꾸면 차시 안에서 입력기가 두 종류로 갈라진다.** 공통 컴포넌트로 한 번에 교체할 것.
- 확인 필요: 이번 작업 범위를 `section_arithmetic_tutorial`만으로 볼지, 08의 모든 키패드로 볼지. (권장: 전체 — 안 그러면 일관성이 깨진다)

## 13. section_random_problems — 문제 전에 도형 생성·감소 과정을 먼저 보여주기

- 상태: 열림
- 대상: `section_random_problems`
- 현재: `#randomPanel`에 계산식(`randomPromptText`)이 **글자로 바로 튀어나온다.** 우측 `#randomWorkProgress`의 도형 3개는 진행 표시용일 뿐(`complete` 클래스 토글), 문제의 수와 연결되어 있지 않다.
- 문제: **1학년 대상**인데 앞 씬(`section_shape_find`, `section_arithmetic_tutorial`)에서는 도형을 놓고 세고 더하고 빼는 걸 눈으로 보여주다가, 이 씬에서만 갑자기 추상 수식으로 건너뛴다. 흐름이 끊긴다.
- 목표: 문제를 내기 전에 **도형이 생기고(+) 줄어드는(−) 과정을 먼저 그려준다.** 그 뒤에 식과 입력기를 제시한다.
- 재사용할 것: `section_arithmetic_tutorial`의 `#arithShapes` + `interaction_shape_add_remove` 연출이 이미 이 동작을 한다. 새로 만들지 말고 그 구현을 공통화해서 가져온다.
- 구현 메모:
  - 무작위 생성기(`A + B = 10` 등)가 만든 수에 맞춰 도형 개수를 동적으로 그려야 한다. 고정 3개가 아니다.
  - 등장/소멸에 stagger를 주고(개당 ~120ms), 다 그린 뒤 식 → 입력기 순으로 노출한다.
  - 문제마다 매번 재생하면 지루해질 수 있다. 재생 속도나 반복 여부 조정 여지를 남겨 둘 것.
- 확인 필요: 매 문제마다 연출을 재생할지, 처음 1~2문제만 보여주고 이후엔 생략(또는 탭 스킵)할지.
- 8번(도형 에셋화 범위)과 직결된다. 여기서 쓰는 도형이 CSS `.paint-shape`인지 에셋인지 먼저 정해져야 한다.

## 14. 수리 이야기 표지판을 에셋으로 변경

- 상태: 열림
- 대상: `section_math_story`의 `#signRow` — `.sign.circle` / `.sign.square` / `.sign.triangle`
- 현재: 표지판 3개가 **모두 같은 `assets/road-sign-body.png` 한 장**을 쓴다. 이 파일은 가로 710px 스프라이트라, 각 `.sign`이 `width:230px;overflow:hidden`으로 잘라내고 `left:0 / -237px / -474px`로 밀어 원형·사각형·삼각형 부분만 보여주는 구조다. 표지판 안의 문구(`자동차 전용도로`, `주차`, `공사`)는 `<span class="sign-label">`로 위에 얹혀 있다.
- 문제:
  - 스프라이트 오프셋이 픽셀 하드코딩이라 에셋을 다시 그리면 전부 깨진다.
  - `object-fit:fill` + `width:710px` 강제라 원본 비율이 눌린다.
  - `.sign.circle .sign-label`처럼 도형별로 라벨 위치를 따로 보정하고 있어 유지보수가 나쁘다.
- 목표: **표지판을 개별 에셋으로 분리한다.** 도형별로 파일 1장씩.
  - 예: `road-sign-circle.png` / `road-sign-square.png` / `road-sign-triangle.png`
  - 배경 투명 PNG (8번 규칙과 동일)
  - `artDirection` 준수
- 확인 필요: 표지판 **문구를 이미지에 굽지 말 것** — `CLAUDE.md`의 에셋 규칙대로 빈 면을 남기고 HTML 텍스트(`.sign-label`)를 유지한다. 다만 실제 도로 표지판은 픽토그램이 핵심이라, 픽토그램은 이미지에 넣고 글자만 HTML로 두는 절충이 필요할 수 있다. 어디까지 이미지에 넣을지 확정 필요.
- 교체 후 `road-sign-body.png` 사용처가 없으면 에셋 정리. 스프라이트용 CSS(`left` 오프셋, `overflow:hidden`, `width:710px`)도 함께 제거한다.

---

## 확인이 필요한 항목 정리

작업 착수 전 사용자에게 확인할 것.

1. (2번) 삭제 대상이 `section_global_ui`인지 `section_intro`인지.
2. (1번) 08에 `lesson.json`을 새로 만들지 여부 / 소리 버튼·진행률 바 유지 여부.
3. (7번) 교실 배경 에셋 신규 생성 여부와 찾을 도형 사물 목록.
4. (8번) 도형 에셋화 범위 — 찾기 씬만인지 계산 씬까지인지.
5. (4번) 서체 `Jua`를 타이틀 화면에만 둘지, 01처럼 `html,body,button`에 전역 적용할지. 전역 적용하면 08의 모든 텍스트 폭이 바뀌어 기존에 맞춰 둔 레이아웃(말풍선 990×190, 키패드, overview 3칸 등)이 흔들릴 수 있다.
6. (11번) 망치를 떠 있는 아이콘으로 둘지, 작업자 캐릭터가 드는 형태로 갈지. 수리 연출 중 탭 스킵 허용 여부.
7. (12번) 키패드 교체 범위 — `section_arithmetic_tutorial`만인지 08의 모든 키패드(`countKeypad`, `randomInput`)까지인지. (권장: 전체)
8. (13번) 도형 생성·감소 연출을 매 문제마다 재생할지, 초반 몇 문제만인지.
9. (14번) 표지판 픽토그램을 이미지에 굽고 글자만 HTML로 둘지, 픽토그램도 HTML/CSS로 올릴지.

**해소됨**

- ~~(3번) "title CTA 이미지"가 타이틀 로고 교체인지 CTA 버튼의 이미지화인지.~~ → 로고 교체로 확정, 2026-07-31 완료.
- ~~(3번) 타이틀 이미지의 아트가 01 `title-logo.png`와 색감·글자 형태가 다르다.~~ → 01 화풍으로 재생성 완료, 2026-07-31.

## 항목 간 의존 관계

- 8번(도형 에셋화 범위) → 7번, 13번이 모두 여기에 걸려 있다. **먼저 정해야 할 항목이다.**
- 12번(키패드) → 08 전 씬의 입력기에 영향. 부분 교체하면 일관성이 깨진다.
- ~~3번(타이틀 로고 교체) → 9번의 140px 오프셋 재계산 필요.~~ → 재측정 결과 알파 bbox가 동일해 재계산 불필요했다(2026-07-31). 로고를 또 바꾸면 이 확인은 다시 해야 한다.
- 2번(첫 페이지 삭제) → 1번(헤더 진행률), `SCENE_META` progress 재배분, 10번 디버그 패널 목록에 �