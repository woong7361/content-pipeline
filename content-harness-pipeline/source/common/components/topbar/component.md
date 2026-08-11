# Topbar

- Type: `ui_component`
- Status: `candidate`
- Source: `production/1-2/08/index.html` `.topbar` + `.course-menu-*` (원본은 `1-2/01`의 `installCourseMenu`)
- Final output: inline into `output/index.html`
- Blocks:
  - `.c-topbar` — 상단 HUD
  - `.c-courseMenu` — 차시 목록 드로어. **`#stage`의 직계 자식**으로 둔다
- Slots:
  - `title` 차시 제목
  - `step` 현재 단계 라벨 (빈 문자열이면 구분선까지 감춘다)
  - `bar` / `fill` / `pct` 진행률
  - `grade` / `list` 드로어 머리말과 차시 목록
- Actions:
  - `menu` 목록 열기/닫기
  - `sound` 소리 on/off 토글
  - `close` / `home` 드로어 닫기, "처음으로"
- States:
  - topbar: `data-state="visible | hidden"` (`hidden`은 타이틀 화면용)
  - 드로어: class `is-open`
  - 목록 항목: class `is-current`, `is-locked` (+ 네이티브 `disabled`)
  - 소리 버튼: 네이티브 `aria-pressed`
- Runtime API:
  - `CommonTopbar.init(root, options)` → `{ setTitle, setStep, setProgress, setSoundOn, isSoundOn, setHidden, open, close }`
  - `CommonTopbar.setProgress(root, 0..100)`
  - `CommonTopbar.setStep(root, text)` / `CommonTopbar.setTitle(root, text)`
  - `CommonTopbar.setSoundOn(root, on)` / `CommonTopbar.isSoundOn(root)`
  - `CommonTopbar.setHidden(root, hidden)`
- Required DOM: `#stage` (드로어의 `inset:0`과 `cqw/cqh` 단위가 stage container를 전제한다)
- Use when:
  - 차시 전체에 걸리는 상단 HUD — 제목, 현재 단계, 진행률, 소리 토글
  - 같은 학년/시리즈의 다른 차시로 이동하는 목록 드로어
- Avoid:
  - 한 scene 안에서만 쓰는 지역 진행 표시 (문항 진행 dot 같은 것)
  - 선생님 얼굴·브랜드 로고를 넣은 헤더 (그건 teacher source다)
  - 드로어를 일반 모달 대용으로 쓰기 (좌측 슬라이드 차시 목록 전용이다)

## `init` options

```js
CommonTopbar.init(document.querySelector("[data-component='topbar']"), {
  menu: document.querySelector("[data-component='course-menu']"), // 생략하면 문서에서 찾는다
  title: "알록달록, 학교 담장 색칠하기",
  step: "수리력 +",
  progress: 4,
  soundOn: true,
  course: {
    gradeLabel: "1학년 차시 목록",
    current: "08",
    lessons: [
      { no: 6, id: "01", title: "와글와글, 운동회를 도와요!" },
      { no: 8, id: "08", title: "알록달록, 학교 담장 색칠하기" },
      { no: 9, title: "준비 중" }
    ]
  },
  onSoundChange: on => { if (!on) stopVoice(); },
  onHome: () => scenes.showScene("section_intro"),
  onNavigate: href => location.assign(href),  // 기본값
  followScenes: true                          // 기본값
});
```

- `lessons[].path`가 있으면 그 경로, 없고 `id`만 있으면 형제 디렉토리(`../{id}/`)로 간다.
  둘 다 없는 항목은 `준비 중`으로 잠긴다. `current`와 같은 `id`인 항목이 `지금` 배지를 단다.
- `onHome`은 콘텐츠가 채운다. 컴포넌트가 scene-controller를 직접 부르지 않는다.
- `followScenes`가 켜져 있으면 `common:scenechange`를 듣고
  scene의 `data-qa-label`을 단계 라벨로, `data-progress`가 있으면 진행률로 반영한다.
  scene 중간에 진행률이 오르는 콘텐츠는 그때그때 `setProgress`를 직접 부른다.

## Integration notes

- 최종 HTML에서는 CSS/JS를 inline한다. asset은 없다 (소리 아이콘은 인라인 SVG다).
- 드로어는 `.c-topbar` 안에 넣지 않는다. `.c-topbar`가 `position:absolute`라 오버레이가 56px 헤더에 갇힌다.
- 08은 타이틀 화면에서 `#stage.title-mode .topbar`로 HUD를 감췄다.
  이 컴포넌트에서는 같은 동작을 `setHidden(root, true)`가 맡는다. stage class를 쓰지 않는다.
- 소리 버튼은 **표시 상태만** 바꾼다. 실제 음소거·정지는 `onSoundChange`를 받은 콘텐츠가 한다.
- 08 대비 추가된 동작: Escape로 드로어 닫기. 포커스 트랩은 아직 없다.
