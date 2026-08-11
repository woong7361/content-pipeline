# problem.md

`index.html`과 content-pipeline(`content-harness-pipeline/` 전반)에 대한 사용자 피드백을 누적 기록하는 대장이다. 운영 규칙은 최상단 `AGENTS.md`의 "피드백 → problem.md → rule 루프" 섹션을 따른다.

## 사용 규칙

- 사용자가 결과를 교정·지적할 때마다 아래 "문제 로그"에 항목을 추가한다.
- 같은 **분류 태그(category)** 의 항목이 이미 있으면 새로 만들지 말고 그 항목의 `발생 횟수`와 `최근 발생일`, `사례`를 갱신한다.
- 같은 분류 태그가 누적 **5회 이상**이 되면 다음 작업 전에 rule 승격을 제안한다.
- rule로 승격되면 해당 항목 `상태`를 `규칙화됨`으로 바꾸고 어느 AGENTS.md에 반영했는지 적는다.

### 보류(SKIP) 처리

- 기술적으로 불가능하거나 하지 않기로 결정한 항목은 상태를 `보류`로 둔다. **`보류`인 항목은 5회를 넘어도 rule 승격을 다시 제안하지 않는다.** (`열림`은 "아직 안 했다", `보류`는 "안 하기로 했다"로 구분한다.)
- 발생 횟수와 사례는 그대로 유지한다. 재발해도 횟수만 갱신하고 승격 제안은 하지 않는다.
- 보류로 바꿀 때는 **왜 불가능한지**와 **무엇이 바뀌면 다시 열 것인지(해제 조건)** 를 반드시 함께 적는다. 해제 조건이 충족되면 `열림`으로 되돌린다.

### 규칙화됨 항목 보관과 재발 처리

- 항목이 `규칙화됨`이 되면 사례·조치 **전문은 `solved-log.md`로 옮겨 보존**하고, `problem.md`에는 **스텁만** 남긴다. "어떤 문제였고 어떻게 해결했는가"라는 지식은 요약해 날리지 않는다.
- 스텁 형식: `- [태그] · 횟수 N · 규칙화됨 · solved-log#앵커 · 반영: (AGENTS.md 위치)` — 아래 "규칙화됨 아카이브 (스텁)" 섹션에 둔다.
- 스텁을 같은 파일에 남기는 이유: **중복 감지와 재발 카운트를 유지**하기 위해서다. 규칙화됨 항목을 통째로 딴 파일로 빼면 재발이 신규(횟수=1)로 잡혀 "rule이 있는데도 재발"이라는 신호를 놓친다.
- `규칙화됨` 이후 같은 태그 피드백이 다시 오면, 신규 항목을 만들지 말고 스텁 횟수를 **+1** 하고 재발 사례는 solved-log에 덧붙인 뒤, rule 재검토(문구 강화 / 적용 범위 확대 / 예외 정리)를 제안한다(상태: `제안됨(재검토)`).

## 항목 템플릿

```markdown
### [분류태그] 한 줄 요약

- 대상: content-harness-pipeline/... (구체 경로 또는 index.html)
- 분류 태그: <중복 감지 기준이 되는 짧은 카테고리>
- 상태: 열림 | 제안됨 | 규칙화됨 | 보류
- 발생 횟수: N
- 최초 발생일: YYYY-MM-DD
- 최근 발생일: YYYY-MM-DD
- 사례:
  - YYYY-MM-DD: <사용자가 지적한 내용 요약>
- 조치: <이번에 어떻게 수정했는지>
- 규칙화 메모: <제안한 rule 초안 / 반영 위치 / 승인 여부>
```

## 규칙화됨 아카이브 (스텁)

<!-- 규칙화된 항목은 여기 스텁 한 줄로 남긴다. 문제+해결 전문은 solved-log.md 참조. -->

- [dialogue-as-speech-bubble] · 횟수 8 · 규칙화됨 · solved-log.md#dialogue-as-speech-bubble-대사피드백을-표면-텍스트로-넣고-말풍선을-매번-새로-만듦-channel-렌더링-계약으로-통합 · 반영: prompts/builder_system.md "channel 렌더링 계약". feedback-as-character-bubble·sequential-scene-choreography와 하나의 규칙으로 통합(실질 16회).
- [feedback-as-character-bubble] · 횟수 5 · 규칙화됨 · solved-log.md#dialogue-as-speech-bubble-대사피드백을-표면-텍스트로-넣고-말풍선을-매번-새로-만듦-channel-렌더링-계약으로-통합 · 반영: prompts/builder_system.md "channel 렌더링 계약"의 `feedback` 절. **재검토 필요(2026-08-03)** — 사용자가 "내레이션(`정답입니다`)은 캐릭터를 세우지 말라"고 지시. 규칙에 "**원문 화자가 `내레이션`인 대사는 화자를 세우지 않는다**" 예외를 넣을지 승인 대기(상세: [dialogue-speaker-misassigned] 2번째 사례 · `production/1-2/08/todo.md` 60번).
- [sequential-scene-choreography] · 횟수 3 · 규칙화됨 · solved-log.md#dialogue-as-speech-bubble-대사피드백을-표면-텍스트로-넣고-말풍선을-매번-새로-만듦-channel-렌더링-계약으로-통합 · 반영: prompts/builder_system.md "channel 렌더링 계약"의 dialogue 순차 beat 조항. (5회 미만이나 dialogue 계열로 통합 승격.)
- [character-asset-identity-alpha] · 횟수 9 · 규칙화됨 · solved-log.md#character-asset-identity-alpha-캐릭터-에셋이-포즈마다-다른-인물로-생성됨-정체성-부분 · 반영: AGENTS.md 문서 규칙이 아니라 파이프라인 구조로 강제 (planner_output.schema.json characters 엔티티 · runner.py patch merge/identity_context · design_review.py allowlist · planner/design_review/asset_generator 프롬프트). 원 항목 17회 중 알파 8회는 [character-asset-alpha-fringe]로 분리되어 열린 상태.

## 문제 로그

<!-- 새 항목은 이 아래에 추가한다. -->

### [visual-qa-pixel-measure-cost] 정렬 판정을 LLM이 스크린샷 픽셀로 매번 재게 해서 토큰·시간 비용이 과도함

- 대상: content-harness-pipeline/prompts/design_review_system.md (STEP1 픽셀 전수 검사), schemas/design_review_model_output.schema.json (`alignment_offset`), stages/visual_qa.py, stages/design_review.py
- 분류 태그: visual-qa-pixel-measure-cost
- 상태: 열림 (조사 완료, 설계안 미적용)
- 발생 횟수: 1
- 최초 발생일: 2026-08-08
- 최근 발생일: 2026-08-08
- 사례:
  - 2026-08-08: 사용자가 "playwright로 화면을 보고 거기서 픽셀을 계산하고 있어서 token 소모가 너무 심하다"고 지적. 대표 사례로 "이미지 내부에 글자를 중앙에 넣는 것"을 듦. 좌표평면을 다루는 다른 도메인(도면/CAD 등)의 기법을 레퍼런스로 가져오고 싶다며 조사를 요청.
- 배경(왜 이 구조가 됐나): [design-review-no-image-input] 대응으로 2026-07-22에 "모델=측정기, 코드=임계값 판정기" 구조를 넣었다. 그 결정 자체가 비용을 명시적으로 기록해 두었다 — `alignment_offset` 필수화로 리뷰 생성 시간 **1.7~2배(cell9 642초)**. 즉 이번 지적은 그 조치의 **알려진 잔여 비용**이 임계에 달한 것이다. 두 항목은 같은 지점의 앞뒤 면이므로 태그를 합치지 말 것 — 그쪽은 "못 잡는다"(정확도), 이쪽은 "비싸다"(비용).
- 비용 구조 분석: 씬 N개 × 표면 M개마다 (1) 스크린샷 PNG를 이미지로 열고 (2) 두 중심의 오프셋을 눈으로 재고 (3) `alignment_offset{dx_px,dy_px,surface_w,surface_h}`를 채운다. **정보이론적으로 이 값은 이미 결정되어 있다** — 슬롯 중심은 asset 저작 시점에, DOM 박스 중심은 CSS에 있다. 매 iteration마다 렌더된 픽셀에서 역산하는 것은 이미 아는 값을 비싼 경로로 다시 구하는 것이다. 게다가 측정 결과가 흔들려(cell6/7/8에서 같은 ~12px를 high/none/low) 코드 임계값을 덧대야 했다.
- 조치: (조사만, 미조치) 좌표계 도메인 6종 레퍼런스 조사 완료. 공통 원리는 **"측정하지 말고 선언하라"** — 좌표를 산출물에서 역산하지 않고, 각 요소가 자기 기준계(anchor/pivot/safe zone)를 **입력 데이터로 신고**하고 배치는 solver/레이아웃 엔진이 푼다.
  - 핵심 후보 ①: **Android 9-patch / Aseprite slice 방식** — 에셋이 자기 content rect(=safe zone)를 메타데이터로 들고 다닌다. asset_generator가 `composition_notes`에 산문으로 적는 safe zone을 정규화 좌표 JSON(`{x,y,w,h}` 0~1)으로 승격하면, builder는 그 값을 CSS로 옮기기만 하면 되고 측정이 사라진다.
  - 핵심 후보 ②: **CAD 구속(constraint) + GD&T 공차** — "중앙에 놓아라"를 `concentric(text_box, slot)` 같은 관계로 선언하고, 검증은 공차 위반만 보고. `visual_qa.py`가 `getBoundingClientRect()`로 결정적 계산 → 위반 건만 출력하면 토큰은 위반 수에 비례(정상이면 0).
  - 나머지: TeX box-glue(중앙정렬은 glue가 푼다), Cassowary/Auto Layout(선언적 제약 + priority), Unity RectTransform(정규화 anchor/pivot), Mapbox 라벨 배치(anchor+offset+collision index).
- 규칙화 메모: 아직 1회. 설계안을 실제 적용해 효과가 확인되면 "**정렬은 산출물 픽셀에서 역산하지 않는다. 에셋은 자기 safe zone을 정규화 좌표로 신고하고, 정렬 검증은 결정적 기하 계산으로 위반만 보고한다**"를 `content-harness-pipeline/AGENTS.md` 또는 `prompts/common_html_contract.md`에 승격 제안. 연관: [design-review-no-image-input](정확도 면), [bg-anchor-alignment]·[content-overflows-fixed-surface](배경 면 좌표를 눈대중으로 잡아 생긴 결함 — safe zone 메타데이터화의 직접 수혜자).

### [debug-panel-missing-from-run-output] run 산출물에서 백틱으로 여는 씬 이동 디버그 패널이 누락됨

- 대상: content-harness-pipeline/runs/2026-07-31_dfbc1027/output/index.html, runs/2026-08-11_dfbc1027/output/index.html
- 분류 태그: debug-panel-missing-from-run-output
- 상태: 열림 (2회 재발, 2026-08-11 원인 제거)
- 발생 횟수: 2
- 최초 발생일: 2026-08-04
- 최근 발생일: 2026-08-11
- 사례:
  - 2026-08-04: 사용자가 `production/1-2/08`과 똑같이 백틱(`) 키를 누르면 디버그 모드가 열리도록 요청. 기준 파일에는 스테이지 밖 고정 패널, 씬 목록 자동 생성, 현재 씬 동기화, 백틱 토글과 Esc 닫기가 있으나 해당 run 산출물에는 전체 구현이 누락되어 있었다.
  - 2026-08-11: "그리고 debugger도 안넣어줬어". **이번 누락은 우연이 아니라 내가 규칙으로 막은 것이다.** 공용 컴포넌트를 파이프라인에 연결하면서 `debug-jumper/component.md`에 `Final output: inline only for preview/debug builds`를 적고, `common_html_contract.md`에 "그 값인 컴포넌트는 학습자용 산출물에 넣지 않는다"를 넣었다. builder는 그 지시를 정확히 지켜 6/7 컴포넌트만 넣었다. 판단 자체가 틀렸다 — 패널은 기본 `hidden`이고 백틱으로만 열리므로 학습자 화면을 침범하지 않고, 사용자는 이 패널로 QA를 한다. 2회차이므로 이제 "산출물에 항상 포함"으로 뒤집는다.
- 조치(2026-08-11): `debug-jumper/component.md`의 `Final output`을 `inline into output/index.html`로 바꾸고, `common_html_contract.md`의 제외 조항을 **"scene이 둘 이상이면 debug-jumper를 함께 inline한다(기본 hidden)"** 요구 조항으로 교체했다. 상세는 아래 조치(2026-08-04)와 함께 본다.
- 조치(2026-08-04): **수정 완료.** `production/1-2/08/index.html`과 같은 구조로 스테이지 밖 고정 디버그 패널을 이식했다. `.scene`의 `data-qa-order`·`data-qa-label`에서 8개 씬 버튼을 자동 생성하고, 버튼 클릭은 기존 `showScene()`을 사용해 씬별 초기화 경로를 유지한다. 씬 전환 때 현재 버튼·씬 정보를 동기화하며, 백틱/Backquote로 열고 닫고 Esc 또는 닫기 버튼으로 닫는다. 입력 필드에서는 백틱 토글을 무시한다. 검증: 인라인 JavaScript 문법 파싱 통과, 8개 씬 및 필수 패널 DOM·키 핸들러 계약 자동 검사 통과. 현재 세션의 인앱 브라우저 목록이 비어 있어 실제 키 입력 화면 검증은 수행하지 못했다.
- 규칙화 메모: 2회. 5회 승격 대상이지만, 이번 원인이 "내가 넣은 제외 규칙"이라 규칙 승격이 아니라 **잘못된 규칙 철회**로 처리했다. 3회째가 나오면 그때는 "개발용 도구는 산출물에 항상 포함하되 기본 숨김" 형태로 `content-harness-pipeline/CLAUDE.md` 승격을 제안한다.

### [blend-tint-bleeds-outside-alpha] background-color + blend-mode로 투명 스프라이트를 색칠해 도형 바깥 사각형까지 색이 새어 나감

- 대상: production/1-2/08/index.html (`.paint-shape`, `.drawn-shape`)
- 분류 태그: blend-tint-bleeds-outside-alpha
- 상태: 조치 (2026-07-31 수정 완료, 규칙 승격은 미제안 — 1회)
- 발생 횟수: 1
- 최초 발생일: 2026-07-31
- 최근 발생일: 2026-07-31
- 사례:
  - 2026-07-31: 사용자가 "도형 채우기가 도형 바깥까지 새어 배경까지 색이 칠해진다"고 지적. 원인은 에셋 알파가 아니라 CSS 색칠 기법이다. `.paint-shape`는 `background-image:url('assets/shape-tile-body.png')`(1536×1024 RGBA, 3프레임 스프라이트, 알파 bbox `40,261~1490,730`) 위에 `.green/.blue/.red/.purple/.yellow`가 `background-color:var(--leaf)` + `background-blend-mode:multiply`를 얹는 구조다. **`background-color`는 요소 padding-box 전체를 칠하고, `background-blend-mode`는 그 위에서 이미지와 블렌드할 뿐이라 이미지 알파가 0인 영역에는 블렌드 대상이 없어 배경색이 그대로 남는다.** 스프라이트 세로 알파 점유율이 (730-261)/1024 = 46%뿐이라, `height:150px` 요소에서 도형 위아래로 각각 ~38px의 색칠된 빈 띠가 생긴다. 영향 범위: `#paintIntroVisual`(394행), `#countShapes`, `#arithShapes`(407행), `#randomWorkProgress`(419행), 자유 그리기 `.drawn-shape`(690행)와 완성 벽화 미리보기(686행) — 도형이 등장하는 08의 모든 씬.
  - 참고: 에셋 자체는 정상이다. `shape-tile-body.png`·`road-sign-body.png` 모두 네 모서리 alpha=0인 투명 PNG임을 실측 확인했다. `production/1-2/08/todo.md` 8번의 "현재 08의 도형은 에셋이 아니라 CSS로 그려져 있다"는 서술도 이 조사에서 오류로 확인되어 정정했다.
- 조치: **2026-07-31 수정 완료.** 색칠을 `.paint-shape::before`로 옮기고 같은 스프라이트를 `mask-image`(`mask-size:300% 100%` + 도형별 `mask-position`)로 걸어 실루엣 밖을 잘라냈다. `filter`(그림자·글로우)는 요소에 남겨 마스크된 결과 위에 적용되게 했다(요소에 마스크를 직접 걸면 drop-shadow가 잘린다). `.drawn-shape`가 중복으로 깔던 `background-image`는 제거했다. 색상별 에셋 15장(3도형×5색) 생성이나 스프라이트 분리는 불필요했다. 함께 고친 것: `.paint-shape`에 `aspect-ratio:1;justify-self:center`를 넣어 그리드 칸에 눌려 동그라미가 타원으로 보이던 왜곡을 없앴다(`.random-progress`·`.drawing-summary`도 정사각으로). 검증: 수정 전/후를 같은 페이지에서 렌더해 요소 모서리 픽셀 비교 — 수정 전 `triangle red` 네 모서리가 전부 틴트색 `(230,80,67)`, 수정 후 전부 페이지 배경 `(255,255,255)`, 도형 중심 색은 동일 유지.
- 규칙화 메모: 아직 1회. 반복되면 "투명 raster를 색상 변형해 쓸 때 `background-color`+`background-blend-mode`로 틴트하지 않는다 — 배경색이 알파 0 영역에 그대로 남는다. `mask-image`로 실루엣을 잘라낸 뒤 색을 얹는다"를 `prompts/common_html_contract.md`에 제안 후보. 알파 계열([transparent-asset-alpha-not-validated]·[decorative-asset-background-alpha]·[character-asset-alpha-fringe])과 증상이 닮았으나 **원인 층위가 다르다** — 그쪽은 에셋 생성/후처리 문제라 `보류`지만 이건 순수 CSS라 결정적으로 고칠 수 있다. 같은 태그로 묶지 말 것.

### [refine-css-drift-no-tokens] refine이 CSS를 통째로 다시 쓸 때 폰트 크기·색이 기준 없이 흔들려 통일성이 깨짐

- 대상: content-harness-pipeline/prompts/design_refine_system.md, prompts/common_html_contract.md, prompts/builder_system.md (관측: runs/2026-07-22_ch8c0719/output/index.html)
- 분류 태그: refine-css-drift-no-tokens
- 상태: 열림
- 발생 횟수: 1
- 최초 발생일: 2026-07-22
- 최근 발생일: 2026-07-22
- 사례:
  - 2026-07-22: 사용자가 "refine 시 의도치 않은 사이드이펙트가 크다 — 폰트 크기가 달라진다거나 통일성 없는 css"라고 지적. 최신 index.html의 `<style>` 블록(218줄) 실측 결과, 근본 원인은 **디자인 토큰/타이포 스케일 부재**로 확인됨. 구체 수치: (1) `font-size` 선언 45개에 **고유 값이 20종**(22·23·25·26·27·28·29·30·31·32·33·34·36·37·38·40·42·44·48·72px)으로, 26~31px 구간은 거의 모든 정수가 한 번씩 쓰여 스케일이 아니라 잡음 상태. (2) 대사판 텍스트색 `#173f49`가 토큰 없이 **6번 하드코딩**. (3) 골드/크림 계열 hex가 **25종**(#ffe14c·#ffe15f·#ffe26d·#ffe44d·#ffe45f·#ffe462·#ffe562·#ffe566… 육안 구분 불가한 노랑 난립) 흩어져 있고, `:root`에는 `--gold:#ffd75a`·`--cream:#fff6d7`만 있고 거의 안 쓰임. (4) `:root` 토큰이 **색 7개뿐**이고 font-size·spacing·radius 스케일은 아예 없음. → refine이 HTML을 통째로 재작성할 때(design_refiner) 앵커할 스케일/토큰이 없어 요소마다 국소적으로만 그럴듯한 새 px 값을 찍고, 그 불일치가 소스에 드러나지 않아 누적됨.
- 조치: **2026-07-22 ①+② 프롬프트 계약 반영 완료.** 사용자 원 질문("js/css/html 파일 분리하면 AI가 더 잘 고치나")은 분리가 이 문제를 못 고침을 확인 — 원인은 파일이 합쳐져서가 아니라 CSS에 단일 진실원(토큰)이 없어서고, 이 output은 빌드물이 아니라 builder LLM이 한 방에 생성+refine이 통째 재작성하는 산출물이라 파일 경계가 무의미. 대신 **디자인 토큰을 common 층에 넣고 세 스테이지가 참조**하도록 함. 실제 편집(4파일):
  - `prompts/common_html_contract.md`: "## 디자인 토큰 계약" 신설. **구조 토큰(고정값)** = 타이포 사다리 8단(실측 20종→24/28/31/34/38/42/48/72px, 스냅오차 ≤2px)·z-index 10층·radius 5단·이징 3종(`.2,.8,.2,1` 등)·지속 3단·그림자 고도 3단. **팔레트 토큰(이름·역할 고정, 값은 콘텐츠별)** = `--bg`·`--surface`·`--ink`·`--plate-ink`·`--accent`·`--accent-bright`·`--glow`·`--cream`·`--danger`. 규칙: 토큰만 `var()` 참조·raw 신규 금지·수정은 토큰 값으로·확장은 named 토큰+주석·scene 예외는 scope 재정의·**팔레트 값은 planner art_direction에서**(오답=빨강 역할 고정). common은 이미 builder·design_refine·content_refine 3곳에 주입되므로 한 번 편집으로 전파.
  - 세 스테이지 프롬프트는 **규칙을 재서술하지 않고 스테이지 고유 역할만** 남김(사용자 지적으로 DRY 정리 — common이 이미 3곳에 주입되고 문서 첫 줄에서 세 스테이지를 명시하므로 규칙 재서술은 중복). `builder_system.md`: "토큰 블록을 :root에 **최초 선언**하고 팔레트 값을 art_direction에서 정하는 **원천**" 한 줄. `design_refine_system.md`: "통째 재작성이라 **드리프트 주범** — 재작성 시 토큰을 raw 값으로 풀어헤치지 마라" salience 한 줄. `content_refine_system.md`: 원래부터 팔레트 등 안 건드리므로 **고유 추가 없음**(초안의 보강을 되돌림).
  색을 구조 토큰과 뭉뚱그렸던 초기 초안을 사용자 지적으로 정정 — **색=분위기라 콘텐츠별 생성이 맞고, 파이프라인엔 이미 art_direction이 그 주인**(planner_system.md:106). 25종 노랑의 원인은 "색이 콘텐츠별이라서"가 아니라 "raw hex가 흩어져서"였으므로, 값은 art_direction에서 생성하되 named 토큰 세트로 고정하는 것으로 해결. **미적용(후속)**: ③ validate.py 토큰-밖-raw-값 게이트 미구현. 또한 프롬프트 계약이라 실제로 지켜지는지는 다음 run 산출물의 font-size 고유값 수·raw hex 수로 검증 필요(계약만으로 100% 강제되진 않음 — [refine-alters-spec-text]에서 계약 후에도 잔여 누수 있었던 전례).
- 규칙화 메모: 아직 1회이나 [refine-alters-spec-text]와 같은 **refine 재작성 부작용 계열**(그쪽은 원문 텍스트, 이쪽은 시각 토큰). 두 개가 합쳐지면 "refine이 돌수록 원문도 스타일도 흐트러진다"가 되어 루프가 순손실. 반복되면 "refine/builder는 타이포·색·간격을 `:root` 디자인 토큰으로만 표현하고 raw 값을 새로 만들지 않는다"를 프롬프트 계약으로 승격 제안. 연관: [content-scale-too-small]·[typeA-prompt-text-small-terse]·[cta-text-offcenter-padding](개별 크기/정렬 결함 — 토큰화가 상위 해법), [[codex-strict-output-schema]].

### [design-review-no-image-input] design_review가 tutorial의 정렬·부분덮음 결함을 놓치고 "중앙 정렬됨"으로 오판함 (근본원인: blind 아님 — 11씬 일괄 리뷰 satisficing, 실측으로 정정)

- 대상: content-harness-pipeline/stages/design_review.py, stages/scripts/codex_client.py, prompts/design_review_system.md (관측: runs/2026-07-21_ch8c0718/iter_005)
- 분류 태그: design-review-no-image-input
- 상태: 열림
- 발생 횟수: 1
- 최초 발생일: 2026-07-21
- 최근 발생일: 2026-07-21
- 사례:
  - 2026-07-21: 사용자가 ch8c0718 `output/index.html`의 활동1 튜토리얼 화면(시계 1개 + `[?]` 카드 + `[3시][4시][5시]` 티켓)에서 (1) 시계 에셋이 그림판(수리 트레이) 원형 홈의 일부만 덮고, (2) 티켓 문구와 `[?]`가 각 카드/빈칸 중앙에 정렬되지 않았다고 지적하며, "critique에서도 문제가 제기됐어야 하는데 왜 안 잡혔나"를 물음. 실제 iter_005 design_review는 이 씬(`02_activity1_tutorial`)에 대해 `overall_assessment`에 "선택 문구와 `[?]`도 각 빈 표면 **중앙에 안정적으로 배치**되어 있으며"라고 **정반대로 판정**하고, `refine_suggestions`에 "선택 티켓의 **중심 정렬**과 캐릭터 safe zone을 **유지하라**"고 적었으며, `text_review`·`checks`·`priority_findings`를 **전부 빈 배열**로 두고 status=PASS를 냈다. 활동2 시계 선택 씬(`05_activity2_type_a`)도 "세 시계와 라벨이 일관된 축으로 정렬"이라 칭찬하며 findings 0.
- 초기 가설('blind' — **아래 "검증" 실측으로 반증·정정됨**). 아래 1·2·5·6의 코드 사실은 맞지만, 그로부터 "모델이 픽셀을 못 본다"고 내린 결론은 틀렸다:
  1. `design_review.py:build_prompt`(141~156행)는 스크린샷을 **파일 경로 문자열 목록(`SCREENSHOT_FILES`)** 으로만 프롬프트에 넣는다. 이미지 자체를 첨부하지 않는다. (사실이나, codex는 그 경로를 받아 파일을 스스로 열어 본다 — 검증 참고.)
  2. `codex_client.py:run_prompt`(57~64행)는 프롬프트를 **stdin 텍스트로만** 전달하고(`input=prompt`), `build_command`(82~115행)에 `-i/--image`·base64·image_url 등 **이미지 첨부 경로가 없다.** (사실이나 → 첨부가 없어도 codex가 스스로 파일을 열어 픽셀을 봄이 실측으로 확인됨. "픽셀 미보장 = 못 봄"은 틀린 추론.)
  3. `design_review_system.md:16`은 이 상황을 이미 전제한다 — "직접 이미지를 볼 수 없는 환경이면 HTML/CSS 구조와 asset 요약을 근거로 판단한다." 프롬프트 자체가 blind fallback을 허용한다.
  4. 그 결과 리뷰는 코드(HTML/CSS + planner/asset JSON)만으로 추론한다. CSS가 `text-align:center`/flex 중앙정렬을 선언하고 있으면 "중앙 정렬됨"으로 결론내지만, 실제 어긋남은 **에셋의 시각 중심과 DOM 박스 중심 불일치·object-fit/background-size로 인한 부분 덮음** 같은 렌더 산물이라 소스에는 드러나지 않는다. iter_005 findings의 evidence가 전부 CSS 속성 인용(`height:440px과 overflow:hidden`, `left:28px/right:145px`)이고 "스크린샷 x,y에서 보인다"는 픽셀 근거가 하나도 없는 점이 blind 추론의 서명.
  5. 보조 신호도 닫혀 있다: `visual_qa.py`는 기하 검사를 하지만 `horizontalOverflow`·`textClipping`(박스를 넘침)만 계산해 **"박스 안에서 중심 어긋남"·"에셋이 슬롯 일부만 덮음"은 애초에 못 잡고**, 게다가 `design_review.py:compact_desktop_screenshot_summary`가 render_checks를 모델에 **넘기지도 않는다**(screenshots 목록만 전달).
  6. 참고: `runner.py:133` 주석은 "design_review도 같은 HTML 전문과 **asset 이미지를 모두 읽으므로** 무겁다"고 적혀 있어, 저자의 멘탈 모델(이미지를 읽는다)과 실제 구현(경로 텍스트만) 사이에 괴리가 있다.
- ①/② 판정(critique가 못 잡은 문제인가, refine이 받고도 못 고친 문제인가 — 사용자 요청으로 실측): **①(critique 문제)로 확정.** tutorial 씬 iter별 추적 결과 — iter_001은 design_review가 tutorial을 **잡긴 했으나**(4 findings + top-level PF 1건), 지적 성격이 "조작물이 일반 CSS 카드/dashed drop zone이다 → **수리 트레이 asset 도입** 후 safe zone에 넣고 텍스트 **중앙 정렬로 유지**하라"는 **구조/재질 지적**이었다(정렬 어긋남·시계 덮음을 버그로 관측한 게 아니라 목표로 지시). refine은 이 지시를 **실제로 이행**했다 — `tutorial_clock_repair_tray.png`를 도입하고 시계·슬롯·티켓을 트레이 위로 옮겨 `place-items:center`를 적용(iter_001 스크린샷=맨 시계+dashed 박스+민 카드 / iter_005=나무 트레이 통합으로 before/after 확인). **그 asset 통합이 새 결함을 유발** — DOM 오버레이는 자기 박스 기준 중앙이나 asset에 그려진 슬롯 중심과 어긋나고 시계가 홈 일부만 덮음. 이 렌더 전용 결함은 **한 번도 보고되지 않았고**(iter_002~005 tutorial findings 매번 0건, iter_005는 "중앙에 안정적으로 배치/중심 정렬 유지하라"고 오히려 칭찬), 따라서 ②(refine이 correct 지시를 무시)가 **아니다**. refine은 받은 지시(중앙 정렬)를 CSS로 만족시켰고 그 코드 결과가 픽셀에서 어긋났는데 critique도 refine의 선택적 preview도 픽셀을 보지 않았다. `design_refiner.py:build_prompt`도 스크린샷을 `reviewed_screenshots` **경로 문자열**로만 받는다. (당초 여기서 "refine도 blind"라 결론냈으나, 아래 검증에서 뒤집힘.)
- 검증 (2026-07-21, 실측 테스트 — **근본원인 정정**): codex/claude에 이미지 경로만 주고 픽셀 전용 사실을 물어 실증. 스크립트: scratchpad `test_vision.py`(cell1~3), `test_vision2.py`(cell4~5).
  - **'blind' 가설은 반증됨.** cell1(codex, 경로 텍스트만 = 파이프라인과 동일 명령형태): `can_see=true`, 말풍선 원문("다행이다!…줄래?")·시계 3시·돋보기·노란 조끼 **전부 정답**, 접근 방식="파일을 이미지 뷰어로 직접 열었음", 심지어 `cv2.imread`로 픽셀 좌표 측정까지 시도(cv2 미설치로 실패). **codex는 -i 첨부 없이도 경로만으로 파일을 열어 픽셀을 본다.** claude(cell3)도 Read 툴로 봄.
  - cell1의 정렬 판정: "[3시] 약 16px 왼쪽, [5시] 약 20px 오른쪽, [?] 14px 왼쪽·13px 위, 시계는 원형 홈 일부만 덮고 오른쪽·아래 여백" → **초점을 맞추면 사용자 지적 두 결함을 정확히 잡음.**
  - 모델 confound 제거: cell4(설정 모델 `gpt-5.6-sol` + 초점 프롬프트)도 정렬 어긋남을 잡음(can_see=true).
  - **실제 프롬프트 재현(cell5, 결정적)**: 진짜 `build_prompt`로 만든 **136KB·11씬 전문** 프롬프트 + `gpt-5.6-sol` + 실제 schema로 돌리자, status=REJECT지만 **tutorial 씬은 findings 0 + "정확히 결합·통합 우수"로 칭찬** — 실제 iter_005 결과를 **그대로 재현**. 동시에 같은 응답이 다른 씬의 픽셀 결함은 정밀 포착(성공 트레이 `y≈775 잘림`, 갤러리 nav 버튼 "책 밖에 떠 있음"). 즉 모델은 픽셀을 보고 있었다.
  - **정정된 근본원인**: capability(blind) 아님. **11씬을 한 136KB 패스에서 리뷰할 때의 per-scene satisficing** — 모델이 더 눈에 띄는 결함(CSS 도장 계약 위반, 명백히 잘린 성공 트레이, HUD 재질)에 주의를 몰고, tutorial의 미묘한 ~15px 오버레이 오프셋·부분 시계 덮음은 주의 임계값 아래로 흘려 "정렬 잘 됨"으로 러버스탬프. 부추기는 요인: (a) 시스템 프롬프트의 면죄부 조항(`design_review_system.md:16` "이미지 못 보면 HTML/CSS로 판단")이 CSS `place-items:center`에 기대게 함, (b) center-offset·fill-ratio 같은 결정적 정렬 신호 부재(visual_qa는 overflow/clipping만 계산, 그나마 모델에 미전달 — 모델이 cv2를 손수 시도한 이유). **교훈: 코드 경로+출력 스타일만 보고 'blind'로 단정했으나 직접 프로브로 반증됨. 능력 판정은 지표(코드/출력)가 아니라 직접 실측해야 한다.** 연관 [[verify-artifact-predates-fix]].
- 조치: (진단만, 미조치) 원인 규명 완료 — 근본은 blind 아닌 **일괄 리뷰 satisficing**이므로 해결 방향도 정정됨. ⚠️ **`-i` 첨부는 효과 없음**(cell2에서 오히려 시계 판정이 더 약해짐, cell1=경로텍스트가 최고 성능) → 당초 후보 ①(이미지 첨부)은 폐기. 유효 후보: **② 결정적 기하 검사(최우선)** — `visual_qa.py`에 각 slot/card/asset 표면 중심 vs 내부 텍스트 bbox 중심 오프셋(px), 에셋 이미지 실제 채움영역 vs 슬롯 경계 비율을 계산해 render_checks로 넣고 design_review 프롬프트에 전달(모델이 cv2로 스스로 재려던 그 값을 대신 제공). **③ per-scene 리뷰 분할** — 11씬 1패스 대신 씬별 호출(cell4는 잡고 cell5는 놓침 → 분할이 satisficing을 줄임, 대신 호출 비용 ~11×). **④ 프롬프트 강화** — `design_review_system.md:16`의 면죄부 조항 제거 + "STEP1: 각 스샷을 열어 interaction surface의 텍스트 중심 vs 슬롯 중심 오프셋을 px로 측정 → STEP2: 그 다음 소스" 강제. 권장 조합: ②+④.
  - 실측(2026-07-21, cell5~7으로 후보 검증; scratchpad `test_vision3.py`/`test_vision4.py`):
    - **④ 단독으로 유효 입증**: cell6(④ 지시 + 면죄부 제거, HTML 인라인 유지)은 tutorial을 **0건→4건(high)**, `[?]` -11px·티켓 (-10,-7)(-5,-7)(+14,-7)px·시계 홈 여백까지 픽셀 좌표로 잡고 "#tutorialDrop을 ~11px 이동" 등 실행 가능한 refine까지 냄. → cell5 대비 결정적 개선.
    - **HTML 경로화(사용자 제안)는 이 판정 문제의 지렛대 아님**: cell7(④ + HTML을 인라인 대신 절대경로로, 프롬프트 136KB→56KB)은 오프셋을 **재긴 했으나**([?] -14px, 티켓 -15/-2/+7px를 overall에 적음) severity를 "허용범위·현재 유지"로 판정해 **findings 0**. cell6은 잡고 cell7은 놓침 → 갈림은 "~15px가 결함이냐"라는 **경계선 판단**이고 **n=1이라 노이즈일 수 있음**(단정 불가). 게다가 경로화해도 모델은 motion/selector 때문에 결국 HTML을 열어야 함. → ④가 핵심, 경로화는 중립~미확정(지금 불필요).
    - **② 필요성 재확인**: cell7이 "재고도 안 잡은" 것이 ~15px 경계 severity를 LLM 판단에 맡기면 안 된다는 증거. visual_qa가 오프셋을 결정적으로 계산해 임계값(예: >8px=flag)으로 강제해야 견고.
  - 결론 권장: **④(STEP1 픽셀먼저+면죄부 제거) 즉시 적용 + ② 결정적 오프셋 검사**. -i 첨부·HTML 경로화는 채택 안 함. (판정 확신 필요 시 cell6/cell7 각 3~5회 반복.)
  - **2026-07-22 ④ 소스 적용 완료**: `prompts/design_review_system.md`에 (1) 16행 면죄부 조항 → "반드시 스샷을 열어 픽셀로 판정, CSS 선언으로 정렬 결론 금지"로 교체, (2) "리뷰 순서" 상단에 STEP1(씬별 픽셀 전수 검사, 4축) → STEP2(소스 보조) 절차 삽입, (3) 축3 정렬 항목에 "표면중심 대비 오프셋을 px로 측정해 evidence에 수치로 남겨라" 추가. 검증 근거: cell8(일반 4축 STEP1)이 tutorial [?] 오프셋을 (-10,-13)px로 잡음(cell5는 "정확히 결합"으로 칭찬했던 것 대비 반전). **⚠️ 남은 과제 = severity 일관성**: cell6/7/8에서 같은 ~12px를 high/none/low로 판정이 흔들림 → 측정은 A로 확보됐으나 "결함 확정"은 다음 단계 ②(B)의 결정적 임계값(사용자 제안: 표면대비 2~4%=mid, >4%=high)이 못 박아야 함. B는 프로토타입으로 오프셋 분포 실측 후 임계값 확정 → 재검증 → 반영 예정.
  - **2026-07-22 ② B 방향 전환·검증 완료 (LLM측정 + 코드임계값)**: 처음엔 "코드가 픽셀 분석해 슬롯 검출"로 잡았으나 과함 — 크림 centroid가 검색창을 테스트 박스에 앵커해 오프셋을 0쪽으로 편향(scratchpad `test_offset.py`/`offset_viz.png` 오버레이로 확인: CSS 박스가 트레이 아트 슬롯과 명백히 어긋나 있는데 centroid는 -0~+7px만 잡음). 사용자 지적("어차피 px는 LLM이 재는 것") 반영해 **"모델=측정기, 코드=임계값 판정기"로 단순화**: `schemas/design_review_model_output.schema.json`의 `designFinding`에 `alignment_offset{measured,dx_px,dy_px,surface_w,surface_h}` 추가(전 필드 required·정렬무관 finding은 measured=false·0 — [[codex-strict-output-schema]]), `prompts/design_review_system.md` 축3·출력절에 "px를 이 필드에 채워라, severity는 코드가 파생" 지시 추가. **검증(cell9, `test_vision6.py`, 실제 프롬프트+수정 스키마+gpt-5.6-sol)**: 전 씬 34개 finding이 measured=true로 px 채움; tutorial `[?]` dx-13/dy-18 on 394×280 → 코드 6.4% → **HIGH**(모델은 medium), 티켓 3개 3.6~3.9% → **MEDIUM**(모델은 low), CSS 도장은 measured=false로 코드가 건너뜀. **cell7의 severity 흔들림(측정하고도 0건)이 제거됨 — 같은 px면 코드가 항상 같은 severity.** 모델 측정(-13,-18)이 크림-centroid(~0,+7)보다 오버레이 실제 결함과 더 일치 → 모델 측정 신뢰 정당. ⚠️ 비용: alignment_offset 필수화로 리뷰 생성 시간 ↑(600초 초과, 1200초로 완료; 실제 파이프라인 timeout 2400초라 무방). **남은 통합**: (1) `schemas/design_review_output.schema.json`(최종 검증 스키마)에도 alignment_offset 추가, (2) `stages/design_review.py`에 px→severity 재계산 후처리(현재 코드는 값을 안 읽음, 테스트 하네스가 대행).
  - **2026-07-22 깨짐 수정 (통합 1단계 완료)**: 모델출력 스키마만 고치고 최종출력 스키마를 안 고쳐 파이프라인이 깨진 상태였음(design_review.py가 scene_reviews를 통째 복사 → 최종 validation이 `additionalProperties:false` + 미지의 alignment_offset에서 실패). `schemas/design_review_output.schema.json`의 designFinding에 동일 필드 추가로 수정. 검증(`verify_pipeline.py`): 두 스키마 유효 + cell9 모델출력이 model_output 통과 + 재구성 final_output이 output 스키마 통과 → run 안전. **단 통합 2단계(design_review.py severity 재계산)는 의도적 미배선** — 켜면 과잉플래그 위험(티켓 3.6~3.9%가 MEDIUM 무더기)이 발동하므로, 임계값 완화(예: 3% mid/6% high) 후 재검증하고 켤 것. 현재는 A(측정·보고)만 활성, B는 px 데이터 수집만(게이팅 영향 0). **잔여 비용**: alignment_offset required로 리뷰 생성 ~1.7~2배 지연(cell9 642초). 지연까지 없애려면 B를 세 파일에서 되돌리고 A만 유지하는 선택지 있음.
- 규칙화 메모: 아직 1회이나 **파이프라인 설계 차원의 문제**라 임팩트가 큼 — 모델이 픽셀을 보긴 하지만 11씬 일괄 리뷰에서 미묘한 정렬 결함을 satisficing으로 흘리면, 시각 품질 게이트가 "명백한 것만 잡고 미묘한 것은 통과"시키는 편향을 갖고, 오히려 "정렬 유지하라"는 refine 지시로 결함을 고착시킨다. 연관: [asset-native-ui-design-reject](같은 정렬·표면 미정합 defect를 다루나 그쪽은 design_review가 REJECT로 **잡은** 사례들 — 이번엔 반대로 **놓치고 PASS**), [bg-anchor-alignment]·[content-scale-too-small]-계열(픽셀 실측이 필요한 판정), [content-refine-never-runs](critique를 내지만 아무도 안 읽음 — 이번은 critique가 냈어도 미묘한 건 놓침). 교훈 연관 [[verify-artifact-predates-fix]](진단을 지표로 단정 말고 산출물/실측으로 확인).

### [content-refine-learning-flow-integrity] 문항 상태·피드백·수리 보상 순서가 학습 수행과 일치하지 않음

- 대상: content-harness-pipeline/runs/2026-07-21_ch8c0718/output/index.html, content-harness-pipeline/runs/2026-07-22_ch8c0719/output/index.html, production/1-2/08/index.html
- 분류 태그: content-refine-learning-flow-integrity
- 상태: 열림
- 발생 횟수: 10
- 최초 발생일: 2026-07-21
- 최근 발생일: 2026-08-03
- 사례:
  - 2026-07-21: content critique에서 (1) 수리 완료 장면의 대사→전광판→시계→책→복구 배경→CTA 순서 누락, (2) 3회 오답 강제 진행을 정답으로 집계하고 인증서에 13/13을 고정 표시, (3) q_b6·q_b7의 끝 시계가 판정 전에 정답 시각을 노출, (4) 유형 C·마무리 퀴즈를 포함한 문항별 정답 설명·오답 힌트 부족, (5) 유형 C가 개별 빈칸 대신 전체 영역의 입력 순서로 숫자를 채움, (6) 유형 C 완료 피드백이 끝나기 전에 다음 문항이 렌더되는 문제를 지적함. 문제 발생 장면의 수동 다음 진행과 인증서 대사·버튼의 planner 순서 활성화도 함께 요구함.
  - 2026-07-21: 후속 content critique에서 키패드 삭제·전체 지우기와 오답 후 재입력 복구, q1~q13의 계산 근거·구체적 힌트, 유형 A 세 번째 오답 분기, q10 두 슬롯 자동 판정, 오전·오후 1~12 타임라인, q6 끝 시각 상태, 드래그 완료 조건 안내, 검증 가능한 9차시 라우팅, 현재 차시가 드러나는 메뉴 동작을 요구함.
  - 2026-07-21: content refine packet에서 (1) q6·q10의 두 칸 입력 뒤 q8·q12 단일 키패드로 넘어갈 때 `activeSlot=1`이 남아 첫 숫자 입력이 런타임 오류를 낼 수 있는 문제, (2) 튜토리얼·q1~q12의 설명형 피드백 부족, (3) 실제 화면에서 누락된 `[STEP 2. 수리로 해결해요]` 전환 상태, (4) 독립 HTML에서 9차시 이동 결과가 보장되지 않는 문제, (5) 유형별 도입 대사 중 첫 문항 조작이 활성화되는 순서 문제, (6) 인증서·저장·감사 대사·다음 차시 CTA가 한꺼번에 노출되는 문제를 지적함.
  - 2026-07-21: 최신 content refine packet에서 (1) 차시 메뉴·9차시 CTA의 hash-only fallback, (2) 튜토리얼과 q1~q13의 이유·교정 단서 부족, (3) 유형 A 강제 전환을 에너지·인증 성취로 집계하는 문제, (4) 튜토리얼·q10 드래그 조작과 완료 조건 불명확, (5) q10의 `[시스템 재부팅 완료!]` 뒤 q11·q12가 이어지는 전환 모순, (6) 문항 진행도·키패드 지우기·갤러리 마지막 화살표 결과 안내 부족을 지적함.
  - 2026-07-21: 이번 content refine packet에서 (1) 8차시 재선택·새 시작 시 런타임/DOM 상태가 초기화되지 않는 문제, (2) 차시 메뉴와 9차시 CTA의 실제 route 부재, (3) 유형 A 세 번째 오답 뒤 정답을 다시 눌러야 진행되는 문제, (4) 전 문항의 계산 근거·단계형 힌트 부족, (5) 튜토리얼·q10 드래그 조작 발견성 부족, (6) 대사·정답 피드백의 시간 기반 자동 전환을 지적함.
  - 2026-07-22: ch8c0719 content refine packet에서 (1) 유형 B 키패드에 삭제·전체 지우기가 없어 오입력 시 진행이 막힘, (2) 유형 B·C·q13 정답 처리가 중복 실행되어 문항/점수가 건너뛸 수 있음, (3) 다음 차시 CTA가 hash만 바꿔 실제 이동하지 않음, (4) 유형 A 도움 공개 정답을 사용자 정답으로 집계하고 인증서 수치를 자름, (5) q1~q13의 계산 근거·재시도 단서 부족, (6) 튜토리얼 조작과 긴 대사의 수동 확인이 부족하고, (7) 메뉴 현재 차시가 1차시로 잘못 표시됨을 지적함.
  - 2026-07-22: ch8c0719 후속 content refine packet에서 (1) 실제 9차시 경로가 없을 때 최종 CTA가 비활성화되어 완료 흐름이 막힘, (2) 대사·정답 피드백판이 별도 진행 안내 없이 수동 제어로 사용됨, (3) q1~q13의 개념 이유·단계형 힌트가 부족함, (4) 유형 A 정답 자동 전환과 3회 오답 강제 전환이 planner와 다름, (5) 유형 B·C에서 시간 이동 및 `12+12=24시간=1일` 관계를 조작 과정에서 확인하기 어려움, (6) 도움 완료 문항이 인증서 문제 수에서 제외되어 완료 상태와 기록이 어긋남을 지적함.
  - 2026-07-22: ch8c0719 iter_003 content refine packet에서 (1) 독립 실행 환경의 9차시 실제 route 부재, (2) 도움으로 완료한 유형 A 문항이 인증서 정답 수에 포함되는 문제, (3) q1~q12의 계산 근거·단계형 힌트 부족, (4) 튜토리얼과 q6의 조작 전환 불명확, (5) q10 두 슬롯과 오전·오후 12시간 구간의 연결 부족을 지적함.
  - 2026-07-22: ch8c0719 후속 content refine packet에서 (1) route가 없을 때 최종 9차시 CTA가 비활성화됨, (2) q6 오답 초기화 후 두 번째 분 입력칸이 활성 상태로 남음, (3) q1~q12가 계산·시간 관계의 이유를 설명하지 못함, (4) 대사·피드백의 짧은 자동 진행과 화면 전체 탭 스킵, (5) q5·q8 시간 간격 및 유형 C의 `12+12=24시간=1일` 관계 시각화 부족, (6) 튜토리얼·키패드·숫자 블록 첫 조작 순서의 가시적 안내 부족을 지적함.
- 조치: 문항별 `correct`·`attempts`·`forced`·`completed` 상태를 도입해 실제 정답만 인증서에 집계하고, 유형 A 3회 오답 강제 진행은 `forced=true`, `correct=false`로 기록했다. q_b6·q_b7의 끝 시계는 판정 전 바늘을 숨기고 정답 뒤에만 표시하도록 수정했다. 유형 C는 각 빈칸을 독립 드롭 대상으로 바꾸고 해당 자리의 정답 숫자만 고정되게 했으며, `[시스템 재부팅 완료!]` 피드백의 2초 표시가 끝난 뒤 다음 문항을 렌더하도록 전환 수명을 분리했다. 수리 완료는 두 대사→전광판 정상화→시계 정상 작동→책 정리→복구 배경→CTA 순으로, 인증서는 사서 대사→꼬마 사서 대사→저장→다음 차시 순으로 활성화했다. 문제 발생 장면은 새 문구를 추가하지 않고 기존 대사 말풍선 자체를 직접 누르는 진행 버튼으로 바꿔 원문 보존 계약과 수동 진행을 함께 지켰다. 정답 설명·오답 힌트는 planner에 없는 화면 문구를 새로 만들 수 없으므로 기존 feedback 원문과 캐릭터 pose·도장·흔들림·재시도 상태만 보강했다. 후속 수정에서는 입력 슬롯 탭 삭제·더블 탭 전체 초기화·Backspace/Delete 키 지원과 오답 자동 초기화를 추가하고, q6 정답 후 12시 시계 표시, 오전·오후 각 1~12 타임라인, q10 두 슬롯 자동 판정과 중복 입력 잠금, 유형 A 세 번째 오답 정답 강조, 현재 8차시 메뉴 표시, 상위 라우터 함수·이벤트·postMessage 기반 차시 이동을 구현했다. 이번 content refine에서는 키패드별 활성 슬롯을 함수 지역 상태로 격리하고 첫 슬롯을 매번 0으로 초기화했으며, 실제 `[STEP 2. 수리로 해결해요]` 전환 scene, 유형별 도입 대사 동안의 `inert` 입력 잠금, 정답 피드백 표시 시간 확보, 인증서→저장→두 감사 대사→다음 차시 CTA의 순차 활성화, 외부 라우터가 없을 때 `#lesson-9-length`로 이동하는 fallback을 추가했다. 검증: planner 필수 문자열 79개 누락 0, asset 누락 0, JS 구문 정상, Playwright에서 12개 QA scene 전환·도입 입력 잠금/해제·q8/q12 첫 키 입력·q10 자동 완료·인증 보상 순서·9차시 fallback 라우팅을 확인했고 런타임 오류는 0건이었다.
  - 2026-07-21 최신 조치: 유형 A는 세 번째 오답 뒤 자동 진행·에너지 상승을 제거하고 정답 보기를 공개한 뒤 학습자가 직접 보충 확인해야만 `correct`·에너지·인증 점수에 반영되게 했다. 튜토리얼은 카드 선택→목표 슬롯 확인 또는 실제 드롭의 2단계 조작으로 바꾸고, q10은 활성 드롭 슬롯 강조·독립 드롭·자동 완료를 유지했다. 유형별 4단계 문항 진행 상태, 화면 텍스트를 추가하지 않는 지우기 컨트롤, 정답 원문을 기존 작업 티켓에 보여 주는 개념 피드백, q10 완료 메시지의 별도 수명과 q11 전환 지연, 갤러리 마지막 화살표의 접근성 전환 예고를 추가했다. 차시 이동은 동작하지 않는 hash fallback을 제거하고 호스트 콜백·취소 가능한 이벤트·부모 프레임·route map/meta/link/query 기반 실제 URL을 해석하며, 연결 경로가 없으면 버튼 흔들림과 aria-live 실패 상태를 남긴다. 새 힌트 문장은 공통 HTML 계약의 planner 외 화면 문구 추가 금지 때문에 만들지 않고, 기존 오답 피드백·정답·시계·타임라인·선택 강조로 교정 단서를 보강했다. 검증: `grep -cF` 방식 planner 체크리스트 93개 누락 0, 전체 107개(피드백 포함) 누락 0, JS 구문·asset 19개·고정 캔버스 계약 정상. Playwright에서 유형 A 3회 오답 후 에너지 동결→보충 확인 뒤 상승, q10 두 슬롯 드래그→완료 상태 유지→q11 전환, 튜토리얼 목표 슬롯 확인, 차시 이동 실패 상태와 설정 URL 이동을 확인했고 콘솔·페이지 오류는 0건이었다.
  - 2026-07-21 이번 조치: `resetLessonState`가 진행도·점수·문항 상태·유형 인덱스·갤러리 인덱스·튜토리얼 선택/완료·입력 DOM·비활성화 상태·캐릭터 pose·복구/인증 상태·타이머를 모두 초기화하도록 구현하고, 새 시작과 메뉴의 8차시 재선택 전에 호출했다. 문제 발생·튜토리얼·유형별 도입 대사는 시간 경과나 화면 전체 클릭이 아니라 원문 말풍선을 직접 확인해야 다음 상태가 열리게 했으며, q1~q12 정답은 원문 문항과 정답을 함께 담은 기존 티켓을 확인해야 다음 문항으로 진행한다. 유형 A 세 번째 오답은 원문 문항·정답을 보여 준 뒤 오답 완료로 기록하고 자동 전환한다. 오답은 첫 시도에 원문 `다시 생각해보세요`, 두 번째부터 현재 원문 문항을 다시 보여 주어 단서를 단계화했다. q13도 원문 정답 말풍선을 확인해야 인증서로 이동한다. 차시 URL은 runtime route map/meta/link/query 또는 호스트 callback으로만 활성화하고, 경로가 없는 메뉴·9차시 CTA는 disabled 상태로 표시하며 `__contentHarnessRefreshRoutes`로 런타임 연결 후 재활성화할 수 있게 했다. planner 밖의 새 화면 문장은 공통 원문 보존 계약 때문에 추가하지 않았다. 검증: planner 필수 문자열 79개 누락 0, asset 누락 0, JS 구문 정상, QA scene 12개 전환 및 콘솔 오류 0, Playwright에서 수동 대사 진행·유형 A 3회 오답 자동 전환·정답 피드백 확인 후 전환·8차시 상태 초기화·route 유무에 따른 CTA disabled/활성화를 확인했다.
  - 2026-07-22 이번 조치(ch8c0719): 유형 B 키패드에 화면 문구를 추가하지 않는 아이콘형 한 자리 삭제·전체 지우기, 키보드 Backspace/Delete, 오답 후 입력 초기화·재활성화를 넣었다. 유형 A/B/C와 q13에 단일 실행 잠금을 적용하고, 정답 뒤에는 planner 원문 문항·정답 또는 완료 피드백을 직접 확인해야 다음 문항으로 넘어가도록 바꿨다. q1~q13 상태를 `completed`·`userCorrect`·`assisted`·`attempts`로 분리해 유형 A의 3회 오답 뒤 공개된 정답 확인은 완료·에너지에는 반영하되 인증서 정답 수에는 반영하지 않으며, 인증서 화면과 저장 이미지가 같은 실제 사용자 정답 수를 사용한다. 문제 발생·튜토리얼·유형 도입·수리 완료·인증 대사는 자동 타이머 대신 해당 원문 말풍선 확인으로 진행하고, 튜토리얼 조작부에는 드래그/클릭 접근성 라벨과 비언어적 유도 모션을 추가했다. 갤러리 마지막 화살표는 접근성 라벨과 상태 모션으로 퀴즈 전환을 예고하고, 차시 메뉴 현재 항목을 8차시로 바로잡았다. 9차시는 hash-only 이동을 제거하고 runtime route map·meta·link·query·호스트 callback·iframe postMessage 계약을 통해 실제 URL/호스트 이동이 있을 때만 CTA를 활성화한다. 원문 보존 계약 때문에 새 설명 문장을 만들지 않고 기존 문항·정답·피드백 원문을 조합해 교정 단서를 보강했다. 검증: planner 노출/정답/피드백 문자열 87개 누락 0, JS 구문 정상, asset 25개 누락 0, 12개 QA scene screenshot 렌더 및 콘솔 오류 0. Playwright에서 키패드 삭제·전체 지우기, 유형 B/C/q13 중복 입력 잠금, 유형 A 보조 완료의 비정답 집계, 메뉴 8차시 표시, route 유무에 따른 다음 차시 CTA 비활성/활성을 확인했다.
  - 2026-07-22 후속 조치(ch8c0719): planner에 없는 진행 문구를 추가하지 않고 모든 dialogue beat와 정답 피드백에 자동 진행·화면 탭 스킵을 적용해 말풍선 클릭을 몰라도 흐름이 이어지게 했다. 유형 A는 정답 피드백·게이지 갱신 뒤 자동으로 다음 문항으로 넘어가며, 오답은 `다시 생각해보세요`→원문 문항→원문 문항+정답 순으로 기존 텍스트만 단계화하고 세 번째에는 정답 시계를 강조한 뒤 assisted 완료로 자동 전환한다. 유형 B·C·q13도 반복 오답 시 원문 문항과 정답을 함께 보여 주고 입력을 초기화하며, 캐릭터 고민 pose는 피드백 종료 뒤 idle로 복귀한다. 인증서 `맞힌 문제 수`는 도움 여부와 무관한 완료 문항 수로 집계해 완료 상태와 13/13 보상이 일치하도록 했다. 차시 메뉴에는 planner의 1~10 목록 숫자를 노출하고 모든 항목을 호스트 라우팅 요청으로 활성화했으며, 실제 URL·콜백이 없는 독립 실행에서는 비활성화 대신 `content-harness-navigation-missing` 이벤트와 `data-route-missing` 상태를 남긴다. 검증: JS 구문 정상, asset 29개 누락 0, QA scene 12개·고정 캔버스 계약 정상. Playwright에서 12개 QA hook, 대사 자동 전환, 유형 A 3회 오답 assisted 자동 전환, 유형 A/B/C·q13 정답 자동 전환, 메뉴 숫자, route-missing 이벤트를 확인했고 예기치 않은 콘솔·페이지 오류는 0건이었다.
  - 2026-07-22 iter_003 조치(ch8c0719): 인증서 화면과 저장 이미지가 공유하는 `scoreRecord`를 `completedCount`가 아니라 `userCorrectCount`로 갱신해 assisted 완료를 정답 수에서 제외했다. q6은 시 입력 길이가 채워지는 즉시 분 입력칸을 자동 선택하고 정답 뒤 빈 도착 시계에 12시 바늘을 표시한다. q10 입력을 원문에 있는 `오전 [12]시간`·`오후 [12]시간` 구조로 직접 묶고 두 슬롯 완료 시 오전·오후 타임라인을 함께 강조한다. 확인 가능한 9차시 파일은 프로젝트에 없으므로 경로를 지어내지 않고, runtime route map/meta/link/query 또는 확인 가능한 호스트 콜백이 있을 때만 최종 CTA와 메뉴를 활성화하도록 수정했다. 새 계산 설명·힌트 문장은 공통 원문 보존 계약 때문에 추가하지 않고 기존 문항·정답·`다시 생각해보세요`·시계·타임라인으로 단계형 피드백을 유지했다. 검증: planner 원문/문항/보기/정답/피드백 140개 누락 0, JS 구문 정상, asset 30개 누락 0, Playwright에서 q6 자동 슬롯 이동·12시 시계 공개, q10 오전/오후 슬롯·자동 완료, route 부재 시 disabled 및 route 주입 후 활성화, 런타임 오류 0건을 확인했다.
  - 2026-07-22 후속 조치(ch8c0719): 대사·정답·오답 피드백의 시간 기반 자동 진행과 화면 전체 탭 스킵을 제거하고, 현재 보이는 원문 말풍선·피드백판·완료판 자체에서만 다음 상태로 진행하게 했다. q6 오답 초기화에서는 잠금을 먼저 해제한 뒤 값을 지우고 첫 번째 `시` 입력칸으로 active 상태를 되돌렸으며, 입력이 모두 채워지기 전 `[확인하기]`를 disabled로 유지한다. q5·q8에는 원문에 이미 있는 시작 시각·끝 시각을 잇는 HTML 시간 간격 표시를 추가하고 정답 판정 뒤에만 `[1]시간`·`[30]분` 관계를 공개한다. 튜토리얼 오답은 시침·분침을 순차 강조하고, 유형 C 모든 정답은 오전·오후 타임라인을 함께 강조해 `24시간=1일` 관계를 비언어적으로 보강했다. 보이지 않는 말풍선이 조작을 가로막지 않도록 `pointer-events`를 차단했다. 실제 9차시 파일/URL은 저장소에 없어 임의 경로를 만들지 않고, 임베드 호스트에서 `content-harness-navigate-lesson` postMessage를 수신하는 라우팅 계약을 추가해 최종 CTA를 활성화했다. 검증: JS 구문 정상, planner 필수 텍스트 140개 누락 0, asset 30개 누락 0, QA scene 12개·고정 캔버스 계약 정상. Playwright에서 q6 오답 피드백이 3초 뒤에도 유지됨·피드백 확인 후 첫 입력칸 복귀·빈 입력 `[확인하기]` 비활성, 배경 클릭이 대사를 진행하지 않음, q10 완료가 명시적 완료판 확인 전 유지됨, iframe 호스트가 9차시 postMessage를 수신함, 런타임 오류 0건을 확인했다.
  - 2026-08-03: **(실사용 관측)** `production/1-2/08/index.html` `section_random_problems`에서 "초등학생이 알 수 있도록 그림이 같이 보여져야 하는데 그림이 보여지고 사라진다"고 지적. `playRandomShapeIntro()`가 도형 연출을 재생한 뒤 `finishRandomShapeIntro()→clearRandomShapeIntro()`로 `#randomShapes`를 숨기고 나서야 `revealQuestion()`이 식·키패드를 연다. 즉 **계산의 근거가 되는 그림과 문제가 한 화면에 절대 공존하지 않는다.** 구조적 원인은 `#randomShapes`(left 290/top 250/1340×560)와 `#randomPanel`(left 245/top 205/1040×700)이 완전히 겹쳐 있어 `.shape-intro` 동안 `#randomPanel{visibility:hidden}`으로 가릴 수밖에 없는 배치다. (**조치 완료 2026-08-03** — `production/1-2/08/complete.md` 29번: `#randomShapes`를 왼쪽(x 180~756), `#randomPanel`을 오른쪽(내용 x 800~1520)으로 좌우 분리하고 `.shape-intro{visibility:hidden}` 규칙을 제거했다. `renderRandom`이 `revealQuestion()`을 먼저 부르고 도형 연출을 그 옆에서 재생하며, `finishRandomShapeIntro`는 도형을 남기고 건너뛰기 레이어만 내린다. `randomSequence`도 `[0,1,2,3,4,5]`로 되돌려 4유형 6문항을 전부 낸다.)
- 규칙화 메모: 8회 도달로 rule 승격 제안 대상. 초안: "학습 문항은 판정 전 정답 단서를 노출하지 않고 문항별 수행 상태·재시작 초기화·피드백 수명·강제 보충 완료를 명시적으로 관리하며, 대사·문항·보상 장면은 planner의 사건·대사·CTA 순서를 사용자 제어 가능한 상태 머신으로 보존한다." 반영 후보: `content-harness-pipeline/AGENTS.md`의 AI 행동 원칙 아래. 사용자 승인 전이므로 아직 미반영.

### [certificate-paper-transparency-safe-zone] 인증서 종이와 동적 기록 영역이 비쳐 보이고 기록 safe zone이 불명확함

- 대상: content-harness-pipeline/runs/2026-07-21_ch8c0718/output/assets/library_repair_certificate.png
- 분류 태그: certificate-paper-transparency-safe-zone
- 상태: 열림
- 발생 횟수: 1
- 최초 발생일: 2026-07-21
- 최근 발생일: 2026-07-21
- 사례:
  - 2026-07-21: 현재 인증서의 크림색 종이 본체를 완전히 불투명하게 만들고, 중앙 하단에서 맞힌 문제 수와 클리어 소요 시간을 HTML로 올릴 기록 영역을 깨끗하게 비워 달라고 요청. 고정 제목·수여 문구·장식 체계는 유지해야 함.
- 조치: 기존 인증서와 글자 통합 예시를 기준으로 불투명 크림 종이, 원문 고정 문구, 26px 이상 동적 기록 두 줄을 수용하는 빈 고대비 safe zone을 갖도록 인증서 asset을 재생성했다. 최종 PNG는 1024×1536, `Format24bppRgb`이며 safe zone 표본을 포함한 검사 지점의 alpha가 모두 255라 배경이 비치지 않음을 확인했고, 제목·수여 문구 원문과 빈 기록 영역을 실제 이미지로 검수했다.
- 규칙화 메모: 아직 1회. 반복되면 "동적 기록을 HTML로 얹는 인증서 asset은 종이와 기록 영역을 완전 불투명하게 만들고, 고정 문구만 이미지에 통합하며, 동적 값 두 줄용 고대비 safe zone을 명시적으로 비운다"를 asset_generator_system.md 규칙 후보로 제안한다.

### [content-refine-never-runs] design_review가 REJECT인 한 content_refine이 영원히 실행되지 않아 content critique가 통째로 버려짐

- 대상: content-harness-pipeline/runner.py (`run_content_pipeline` 품질 루프 분기, 2785~2816행)
- 분류 태그: content-refine-never-runs
- 상태: 열림
- 발생 횟수: 1
- 최초 발생일: 2026-07-16
- 최근 발생일: 2026-07-16
- 사례:
  - 2026-07-16: 사용자가 "runs에 추가된 애들 eval이 계속 낮아진다"고 지적해 ch8c0716·ch8c0717의 critique/eval 로그를 추적한 결과 발견. 루프 분기가 `if asset_change_needed: … elif design_status != "PASS": design_refine … else: content_refine` 구조라, **content_refine은 design_review가 PASS일 때만 도달 가능한 3순위 분기**다. 두 run 10 iteration 전부 design_review=REJECT였고(asset_change_needed도 8/10에서 True), 실제 실행 분기는 asset_revision 8회 + design_refine 2회 = **content_refine 0회**. asset_revision(`run_asset_revision_stage`)도 내부에서 `run_design_refine_stage`를 호출하므로 결국 **HTML을 고친 stage는 10/10 전부 design_refine**. 그런데 design_refine의 프롬프트(`stages/design_refiner.py:build_prompt`)에는 design_review packet만 들어가고 **content_critique·content_eval이 없다**. 그 결과 content_critique는 매 iter 생성·저장되지만(무거운 모델 호출 1회) 아무도 읽지 않고 버려진다. 증거: 두 run의 critique `priority_issues`가 iter 001~005 내내 **같은 항목을 그대로 반복** — 제출 잠금 없음(중복 클릭), 9차시 CTA가 실제 라우팅 없이 hash만 변경, 피드백이 결과 통보형, 복구 장면 순서 미구현, 유형 C 자동 채점 누락. 5번 지적됐지만 5번 다 아무도 받지 않았다.
- 조치: **2026-07-16 수정 완료.** 후보 ①을 채택 — `if/elif/else` 한 덩어리를 축별 독립 분기로 쪼갰다. `if asset_change_needed:` asset 재생성 → `if asset_change_needed or design_status != "PASS":` design_refine → `if eval_status != "PASS":` content_refine. 각 축이 자기 게이트에만 반응하므로 design이 REJECT여도 content_refine이 돈다. 함께 고친 것: `run_asset_revision_stage`가 내부에서 `run_design_refine_stage`를 부르던 것을 제거했다(안 그러면 새 분기에서 한 iteration에 design_refine이 두 번 돈다). asset 변경을 rebuild가 아니라 refine으로 잇는다는 [asset-revision-refine-routing]의 결정은 유지되며, 이제 호출자의 design 축이 그 일을 맡는다. 실행 순서는 design → content — content_refine이 CSS·레이아웃을 안 건드리는 보수적 stage라 마지막이 안전하고, 반대로 두면 design_refine의 통짜 재작성이 content 수정을 지운다. **비용**: 두 축이 다 REJECT면 한 iteration에 HTML 전체 재작성이 2회(각 최대 2400초)라 iteration당 최악 80분.
- 규칙화 메모: 아직 1회이나 [refine-alters-spec-text]와 마찬가지로 **파이프라인 설계 차원의 문제**. 두 항목이 합쳐지면 "critique는 내지만 아무도 안 읽는" + "유일한 수정자가 원문을 훼손한다"가 되어 루프가 개선이 아니라 랜덤 워크가 된다. 연관: [asset-revision-refine-routing](asset 변경 후 design_refine으로 잇기로 한 사용자 결정이 이 분기의 1순위를 만든 원인 — 그 결정 자체는 유효하나 content 축을 막는 부작용이 검토되지 않았음).

### [refine-alters-spec-text] design_refine이 시각 수정 중 원문 텍스트를 축약·변경·추가해 content_fidelity를 훼손함

- 대상: content-harness-pipeline/prompts/design_refine_system.md, prompts/design_review_system.md (관측: runs/2026-07-15_ch8a0715)
- 분류 태그: refine-alters-spec-text
- 상태: 열림
- 발생 횟수: 2
- 최초 발생일: 2026-07-15
- 최근 발생일: 2026-07-16
- 사례:
  - 2026-07-16: (재발하되 **정도는 크게 경미해짐**) run ch8c0717에서 노출 채널 원문 위반 **2건** 확인 — ①`transition_label` `[STEP 2. 수리로 해결해요]`가 HTML에 **아예 없음**, ②`cta` `[확인하기]`가 **대괄호가 벗겨진 `확인하기`로 표시**됨. ②는 `common_html_contract.md`가 "대괄호 제거 전부 금지"로 **명시적으로 금지한 바로 그 항목**이라 규칙이 있어도 새는 구간이 있다는 뜻. 다만 ch8a0715의 문장 축약·재서술(`[마을 공원 의자 만들기, 딱 맞는 길이를 찾아라! 하러 가기 →]` → `9차시 길이 미션으로 →`) 같은 **중대 훼손은 사라졌다** → 규칙이 대부분 작동 중이고 잔여 누수만 남은 상태.
- 검증 기록:
  - 2026-07-16: planner ↔ `output/index.html` 결정적 대조(normalize: markdown·화자 접두어·따옴표·공백·HTML entity) 실측 결과.
    - **ch8c0716: 노출 채널 원문 위반 0건.** `questions[].prompt`+`choices` **38/38**, `dialogue` 14/14, `cta` 5/5, `certificate_text` 1/1 전부 원문 그대로. eval이 센 "누락 6개"는 **전부 오탐**이었다(→ [content-eval-scoring-too-lenient]).
    - **ch8c0717: 위반 2건**(위 사례). 나머지 `dialogue` 15/15, `title` 3/3, `certificate_text` 1/1은 보존.
    - 공통: HTML은 planner 텍스트를 `**` markdown까지 문자 그대로 JS에 담고(`/* Question data (verbatim from planner) */`) `formatRich()`가 `**…**`→`<strong>`으로 변환해 렌더한다. 원문 보존과 표시가 양립하는 올바른 구현.
  - **주의(자기 교정):** 최초 기록 때 "eval content_fidelity=1이 계속 나오니 원문이 훼손되고 있다"고 횟수 2로 올렸으나, 그 근거는 **틀렸다**. 0716의 6건은 전부 eval 오탐이었고, 재발의 실제 근거는 뒤늦게 0717에서 따로 확인한 2건이다. 결론(횟수 2)은 우연히 같아도 **근거가 달랐다**. 교훈: **eval 점수를 1차 증거로 쓰지 말 것.** 원문 판정은 산출물을 직접 대조해야 하며, 그게 곧 이 판정을 LLM에서 결정적 검증기로 옮겨야 하는 이유다.
  - 2026-07-15: full run(ch8a0715)에서 **content 품질 루프가 순손실**로 관측됨. content_eval 총점이 iter를 거치며 **4.2 → 3.08 → 2.9**로 하락했고 weak_axes는 1개 → 2개 → 3개로 늘었다. 특히 `content_fidelity`가 **5 → 1**로 추락. iter 001은 총점 4.2로 min_total(4.2)을 이미 만족했고 `feedback_scaffolding`(3<4.0) 하나 때문에 REJECT였는데, 그것을 고치려 돌린 refine이 나머지를 무너뜨렸다. eval이 지목한 근거:
    - planner에 없는 전환 버튼 `도와주러 가기`가 **추가됨**
    - `[좋아요! 본격적으로 수리하러 가기 →]` → `본격적으로 수리하러 가기 →` **축약**
    - `[3. 수리 이야기 보러 가기 →]` → `수리 이야기 보러 가기 →` **축약**
    - `[내 사진첩에 저장하기]` → `사진첩에 저장하기` **축약**
    - `[마을 공원 의자 만들기, 딱 맞는 길이를 찾아라! 하러 가기 →]` → `9차시 길이 미션으로 →` **변경**
    - 문항·보기·정답 데이터 자체는 살아 있으나 "필수 노출 라벨과 전환 텍스트 불일치가 누적"되어 원문 충실도 조건을 만족하지 못함.
- 조치: (기록 시점 미조치) 근본 원인 후보 — `design_refine_system.md`는 텍스트를 "장면 속 물건으로 흡수합니다"라고 **옮기라고만** 하고, **원문 내용을 바꾸지 말라는 제약이 어디에도 없다.** design_refine이 HTML을 통째로 다시 쓰는 stage이므로, 재작성 과정에서 라벨을 자연스럽게 다듬어 버린다. planner의 `elements[].content`가 원문 보존 대상이라는 사실이 builder_system.md에는 있으나 design_refine_system.md에는 없다. design_review 역시 원문 변경을 제안하지 말라는 제약이 없다.
- 규칙화 메모: 아직 1회이나 **파이프라인 설계 차원의 문제**라 즉시 대응 가치가 큼(루프를 돌릴수록 나빠지므로 refine 자체가 순손실). 반복되면 "design_refine과 design_review는 시각·레이아웃만 다루고 planner `elements[].content`/`questions`의 원문 텍스트는 한 글자도 바꾸지 않는다. 텍스트는 위치만 옮길 수 있다"를 두 프롬프트에 고정. 상류 [planner-storyboard-detail-loss]·[typeB-problem-text-mismatch-spec]과 같은 '원문 보존' 계열이나 **범인이 다름**(planner도 builder도 아닌 design_refine).

### [asset-native-ui-design-reject] design_review가 웹 패널형 학습 UI와 asset 표면 미정합을 REJECT함

- 대상: content-harness-pipeline/runs/2026-07-15_ch8a0715/output/index.html, content-harness-pipeline/runs/2026-07-21_ch8c0718/output/index.html, content-harness-pipeline/runs/2026-07-22_ch8c0719/output/index.html, content-harness-pipeline/runs/2026-07-31_dfbc1027/output/index.html
- 분류 태그: asset-native-ui-design-reject
- 상태: 제안됨(재검토)
- 발생 횟수: 15
- 최초 발생일: 2026-07-15
- 최근 발생일: 2026-07-31
- 사례:
  - 2026-07-15: design_review가 desktop 기준 REJECT. 튜토리얼, 활동2 유형 A/B/C, 팝업 퀴즈, 최종 인증서에서 핵심 학습 UI가 장면 속 asset 표면에 흡수되지 않고 흰 웹 패널/카드/키패드/모달처럼 떠 있으며, 최종 장면에서는 말풍선과 CTA가 겹친다고 지적.
  - 2026-07-15: design_review iter_002가 desktop 기준 REJECT. Type B/C 키패드와 확인 버튼이 콘솔 밖으로 돌출되고, 팝업 퀴즈 질문·선택지가 종이 카드 밖에 떠 있으며, 팝업북 asset이 배경을 포함해 restored lobby 위에 다른 장면처럼 겹친다고 지적. 반복 CTA도 일반 CSS 버튼처럼 보인다고 지적.
  - 2026-07-15: design_review iter_003가 desktop 기준 REJECT. 튜토리얼 작업대의 안내문·카드 라벨이 asset surface 경계에 걸치고, 활동2 Type A/B/C 콘솔의 시계 라벨·키패드·확인 CTA가 버튼/슬롯 중심에 맞지 않으며, 에너지 게이지와 scene title도 웹 UI처럼 보인다고 지적.
  - 2026-07-21: run ch8c0718 iter_001 design_review가 REJECT. 시작·전환 CTA, 튜토리얼 태그/슬롯, 유형 A 선택 카드, 유형 B 키패드/입력 슬롯, 유형 C 숫자 블록, 최종 퀴즈가 일반 웹 컴포넌트로 보이고, 대사·타임라인·인증서 기록이 asset safe zone을 침범하거나 분리된다고 지적. 이미 재생성된 투명 장치 asset과 공용 티켓/선택 표면을 HTML이 충분히 사용하지 않은 사례다.
  - 2026-07-21: run ch8c0718 iter_002 design_review가 REJECT. 튜토리얼 성공 값과 시계가 수리 트레이에서 분리되고, 대출 단말기 숫자·확인 문구가 물리 슬롯 경계를 벗어나며, 복구 보상판의 빈 메시지 면 대신 별도 말풍선이 표면을 덮고, 최종 인증서가 준비된 래스터 프레임을 사용하지 않은 평면 CSS 패널로 남았다고 지적. 유형 A 라벨·유형 B 입력 focus·퀴즈 왼쪽 페이지도 asset surface 중심과 어긋난 반복 사례다.
  - 2026-07-21: run ch8c0718 iter_003 design_review가 REJECT. 유형 B의 `[확인하기]`가 코르크 게시판 confirm bay 하단 테두리에 걸리고, 복구 완료 문장이 보상판 중앙 크림 safe zone을 벗어나 좌우 기어 장식과 겹쳤다. 유형 C 타임라인은 단말기 내장 표시보다 두꺼운 둥근 CSS 패널처럼 보였고 공통 HUD도 장면 재질과 분리되었다.
  - 2026-07-21: run ch8c0718 iter_004 design_review가 REJECT. 유형 C의 오전·오후 1~12 타임라인을 모니터 반쪽 폭에 각각 배치해 14px 숫자와 9~12가 붙어 보이는 high severity 판독 결함이 발생했다. 성공 장면에는 사용이 끝난 트레이 하단 빈 티켓이 선택지처럼 남았고, 유형 B의 빈 answer-slot은 asset의 recessed 입력 행 안에서 경계와 활성 상태가 드러나지 않았다. 문제·튜토리얼 진입 stagger와 유형별 오답 장치 반응도 추가 보완 대상으로 지적되었다.
  - 2026-07-22: run ch8c0719 iter_001 design_review가 REJECT. 시작·성공·복구 CTA, 튜토리얼 드롭 슬롯과 선택 카드, 유형 A 라벨, 유형 B 입력/키패드, 유형 C 슬롯/숫자 블록, 갤러리와 마무리 퀴즈가 준비된 raster interaction surface를 사용하지 않거나 safe zone 밖에 놓여 일반 웹 UI처럼 보였다. 특히 STEP 2 제목의 중앙 원형 표면 미사용, 유형 B 키패드의 게시판·캐릭터 침범, 유형 C 슬롯의 단말기 프레임 침범, 팝업북 위 단색 CSS 패널이 high severity로 재발했다.
  - 2026-07-22: run ch8c0719 iter_002 design_review가 REJECT. 유형 C 숫자 블록이 대출 단말기 하단 키덱 safe zone 밖 바닥에 놓이고 일반 CSS 사각 버튼으로 남았으며, 갤러리 삽화와 대화판이 팝업북 좌우 페이지·중앙 제본선을 덮었다. 준비된 keycap·page tab·step medallion asset을 실제 interaction surface에 결합하고, Type B focus와 퀴즈 중심 정렬도 함께 보정해야 한다고 지적했다.
  - 2026-07-22: run ch8c0719 iter_003 design_review가 REJECT. 문제 발생 대화문이 대화판 상단 프레임에 걸리고, 유형 B의 11:30 캡션이 시계 중심에서 벗어났으며 키패드가 전용 키캡 대신 압축된 답안 티켓을 사용했다. 유형 C 숫자 행은 카드 투입구를 침범하고 입력 홈은 준비된 전용 슬롯 asset을 쓰지 않았다. 코르크 게시판·대출 단말기·팝업북에는 불투명 사각 캔버스가 남아 장면 속 소품 대신 삽입 이미지처럼 보였고, 튜토리얼 entrance와 갤러리 페이지 전환 모션도 동기화가 부족했다.
  - 2026-07-22: run ch8c0719 iter_004 design_review가 REJECT. 유형 C 대출 단말기가 공통 HUD와 좌우 캐릭터 gutter를 모두 가리고, 팝업 퀴즈의 질문과 중앙 선택지 티켓이 마법책 제본 홈을 가로질렀다. 도입·성공·갤러리 대화판의 글자 크기와 여백, 유형 B 확인 티켓의 압축, 선택 target과 무관한 중앙 고정 정오답 도장, 활동 2 진입 stagger 부재도 함께 지적되었다.
  - 2026-07-31: run dfbc1027 iter_001 design_review가 REJECT. 시작 화면의 개요·HUD, 무작위 문제의 거대 흰 패널·선택 pill, 수리 이야기의 흰 설명판이 준비된 담장 작업표·HUD frame·선택 명패·도로변 안내판 asset 대신 일반 웹 UI로 남았다. 정오답 표시는 생성된 도장 asset 대신 CSS 원/O를 사용했고, disabled CTA는 활성 secondary와 같은 상태로 보였다. 장면 전환 퇴장·도입/free-drawing stagger·세 번째 오답 정답 reveal 모션도 부족했다.
  - 2026-07-31: run dfbc1027 iter_002 design_review가 REJECT. 초기 3칸 계획표 문구가 asset safe zone 중심보다 약 67px 아래에 반복 배치됐고, intro·산술·수리 이야기·완료 제목이 배경 위에 직접 떠 있었다. 시작·활동 전환·완료 CTA는 일반 CSS pill로 남았으며, 전역 HUD·계획표·선택 명패는 must_follow style2보다 광택과 베벨이 강했다. shape·arithmetic·completion 진입 stagger도 부족했다.
  - 2026-07-31: run dfbc1027 iter_003 design_review가 REJECT. 전 장면의 HUD가 asset 좌우 홈을 비운 채 목록·소리·단계 라벨을 중앙 면에 몰아 배치했고, 목표·완료 CTA와 반복 말풍선이 새로 준비된 raster 상태 surface를 사용하지 않아 일반 CSS pill로 남았다. 무작위 문제의 탭 힌트도 `tap-hint-hand.png` 대신 CSS 원으로 표시됐으며, 수리 이야기 표지판 stagger와 완료 준공식 CTA stagger가 부족했다.
  - 2026-07-31: run dfbc1027 iter_004 design_review가 REJECT. 전 장면 HUD에 남은 `clip-path`가 좌우 프레임과 마지막 단계 칸을 절단하고 단계 라벨을 실제 safe zone에서 벗어나게 했다. 무작위 문제 키패드는 전용 raster surface가 아직 없는 상태에서 CSS 테두리·흰 입력창·둥근 버튼으로 남아 일반 웹 폼처럼 보였고, 말풍선 텍스트·탭 힌트 손·페인트통 표시 위치도 asset 시각중심과 어긋났다. 교사·작업자 asset 비율 문제는 design_refine의 HTML 수정 범위를 넘어 asset 재생성 대상으로 분리됐다.
- 조치: ch8a0715에서는 기존 생성 asset을 활용해 HTML/CSS/JS 배치를 수정하고 preview로 확인했다. ch8c0718에서는 재생성된 투명 전광판·게시판·단말기와 공용 티켓·선택 surface를 실제 DOM 조작물에 적용하고, 대사/타임라인/기록을 asset 내부 safe zone으로 재배치했다. 최종 퀴즈는 마법책 양쪽 페이지 구조로 재작성했고, 완료 장면의 restored 배경·중앙 시계를 고정했으며, scene 퇴장·퀴즈 stagger·강제 정답 공개·드래그 상태 모션을 보강했다. iter_002 후속 refine에서는 성공 장면에 기존 수리 트레이를 복원해 시계와 `[3시]`를 홈 안에 결합하고, 대출 단말기의 5×2 keypad와 confirm bay를 DOM/CSS에서 분리해 실제 홈 중심에 정렬했다. 복구 대사는 보상판 크림 면의 투명 overlay로 바꾸고, 최종 인증서는 `library_repair_certificate_frame.png`를 실제 표면으로 사용했다. 유형 A 라벨·유형 B focus·퀴즈 왼쪽 페이지와 갤러리 page-out/page-in 모션도 보정했다. iter_003 후속 refine에서는 유형 B 확인 CTA를 별도 `.confirm-bay` DOM으로 분리해 실제 청록 bay 중앙에 정렬하고, 유형 C 타임라인을 모니터 안쪽 폭·얇은 청록 경계·작은 radius로 제한했으며, 복구 보상판 문장을 350px 중앙 safe zone 안에 22px/1.42 행간으로 재배치했다. 성공 트레이와 CTA의 물리적 간격 및 STEP 2 티켓 착지 모션도 보정했다. HTML의 12개 scene root와 QA hook을 정적 검증했고, `design_refine_preview` desktop 캡처에서 대상 표면 경계 포함 여부를 2회 확인했다. planner 원문 문자열 79개 누락 0, asset 21개 누락 0, 중복 DOM id 0, 깨진 이미지·console/page error 0건을 확인했다.
- 조치 (iter_004): 유형 C 타임라인을 오전·오후 세로 2행으로 바꾸고 각 행 전체 폭에 21px 숫자와 4px gap을 확보했다. 유형 B 입력 행은 빈 상태에도 보이는 청록 inset 슬롯·금색 active glow와 슬롯/단위/지우기 3영역 정렬로 재구성했다. 성공 장면은 전용 overflow crop으로 사용이 끝난 하단 티켓 행을 완전히 제외했다. 문제 시계의 벽면 축·접촉 그림자를 보정하고, 문제·튜토리얼 등장 stagger와 유형 A 바늘 역회전·유형 B 지우개 sweep·유형 C 붉은 scan/keypad recoil 오답 반응을 분기했다. 갤러리 disabled 손잡이는 낮은 채도와 눌린 깊이로 구분했다. desktop preview를 2회 캡처해 high finding의 1~12 판독성, 입력 슬롯 경계 포함, 성공 트레이 crop과 텍스트 비겹침을 확인했으며 console/page/image 오류는 없었다.
- 조치 (ch8c0719 iter_001): 기존 대화판·황금 CTA 티켓·시간 답안 티켓·수리 포트·정오답 도장을 실제 title/CTA/대사/선택지/드롭/피드백 표면으로 연결했다. STEP 2 원문을 중앙 원형 홈 안 3줄로 재배치하고, 유형 B 질문·입력·키패드를 코르크 게시판 safe zone 안으로 이동했으며, 유형 C 슬롯을 단말기 화면 위로 올렸다. 갤러리 초기 pageTurn과 book-mask를 제거해 삽화를 실제 페이지에 크게 고정하고, 마무리 퀴즈의 CSS 패널을 제거해 질문과 세 시간 티켓을 팝업북 페이지에 직접 배치했다. 정오답 도장 reveal, 유형 B 오답 캐릭터 pose, hover/press 상태, 첫 장면 stagger를 보강했다. desktop preview를 2회 캡처해 high target을 확인했으며 console/page/request/broken-image 오류 0, asset 누락 0, QA scene 12개, 중복 id 0을 확인했다.
- 조치 (ch8c0719 iter_002): 유형 C의 0~9 숫자 행을 단말기 하단 데크 경계 안으로 옮기고 `library_keycap_body.png`를 각 키의 실제 표면으로 연결했다. 갤러리는 삽화를 팝업북 왼쪽 페이지에 crop하고 대화판을 오른쪽 페이지로 분리해 중앙 제본선을 비웠으며, 좌우 화살표에는 `popup_book_page_tab_body.png`를 적용했다. STEP 2는 `step_title_medallion_body.png` 위 두 줄로 정돈했고, Type B 게시판 축소·캐릭터 안전 영역·focus glow, 팝업 퀴즈 중심축, scene2/tutorial 초기 대화판, scene2와 활동2 문항 stagger를 보정했다. `system_complete_plate_body.png`도 완료 문구 표면으로 연결했다. desktop preview를 2회 캡처해 high target의 장치/페이지 경계 포함을 확인했으며 console/page/request/broken-image 오류가 없었다.
- 조치 (ch8c0719 iter_003): asset_generator가 같은 파일명으로 준비한 투명 코르크 게시판·대출 단말기·팝업북을 기존 참조에 그대로 적용했다. 문제 발생 대화판은 높이·inset·font-size를 함께 조정해 세 줄 전체를 크림색 안전 영역 안에 넣었다. 유형 B는 첫 시계와 `11:30`을 세로 그룹으로 묶고 숫자·유틸리티 키를 `library_keycap_body.png`로 교체했다. 유형 C는 `checkout_digit_slot_body.png`를 실제 입력 홈으로 사용하고 숫자 행을 새 단말기의 카드 투입구 오른쪽으로 이동했다. 갤러리는 삽화에 페이지 clip/perspective를 적용하고 삽화·대사를 하나의 wrapper로 묶어 out→교체→in 전환을 구현했다. 튜토리얼은 시계→꼬마 사서→사서→첫 대사 순으로 stagger를 추가했다. desktop preview를 2회 확인했고 대상 high finding은 모두 asset 표면 경계 안에 들어갔으며 console/page/request/broken-image 오류가 없었다.
- 조치 (ch8c0719 iter_004): 대출 단말기와 질문·타임라인·슬롯·숫자 행·완료판을 `.terminal-shell`로 묶어 85%로 함께 축소하고 중앙 y≈161..858에 배치해 상단 HUD와 좌우 캐릭터를 복원했다. 팝업 퀴즈는 질문과 세 답안 티켓을 오른쪽 페이지 안에 세로 배열하고 피드백 말풍선을 scene root로 분리했다. 도입·성공·갤러리 대화판의 surface 크기와 텍스트 inset을 확대했으며 유형 B 확인 티켓은 280×112px로 비율과 위계를 회복했다. `effect(kind,targetElement)`가 실제 선택 카드·시계·슬롯 중심을 stage 좌표로 계산하도록 바꾸고 정답 stamp-down과 오답 recoil을 분리했으며, 활동 2 메달리온→제목→꼬마 사서 stagger와 메뉴/차시 버튼 미세 반응을 추가했다. desktop preview를 2회 확인했고 단말기/퀴즈 high target은 각 장치와 오른쪽 페이지 safe zone 안에 들어갔다. Playwright 실측에서 선택 티켓 중심과 도장 중심이 정확히 (1240,598)로 일치했고 page error는 0건이었다.
- 조치 (dfbc1027 iter_001): 전역 HUD를 `global-hud-frame.png`, 시작 개요를 `overview-mural-triptych-frame.png`, 무작위 문제 헤더·보기 3개를 `wall-choice-plaque-body.png`, 도로 설명을 `story-roadside-info-board.png`의 실제 safe zone에 결합했다. 정오답 CSS 원/O를 `feedback-stamp-correct.png`·`feedback-stamp-wrong.png`로 교체하고 세 채점 scene이 공통 판정 함수로 두 asset을 사용하게 했다. disabled 다음 차시는 채도·깊이·cursor를 낮춰 활성 나가기와 분리했으며, sceneOut→overlap→sceneIn 전환, intro/free-drawing stagger, 세 번째 오답의 answerReveal+지연 도장을 추가했다. desktop preview를 2회 캡처했고 텍스트 clipping·겹침·broken image·console/page/request 오류는 0건이었다. QA scene 8개는 전환 종료 후 항상 대상 하나만 보이며 중복 DOM id와 `!important`도 0건임을 확인했다.
- 조치 (dfbc1027 iter_002): 교체된 style2 HUD·3칸 계획표·선택 작업표를 실제 파일 비율에 다시 맞추고, 계획표 문구 중심을 67px 위로 옮겼다. intro·산술·수리 이야기·완료 제목은 `school-title-banner-body.png` safe zone에 넣고 수리 이야기의 첫 질문은 초기부터 도로변 안내판에 분리했다. `introStart`는 3상태 CTA sprite에 연결했으며, 미생성 활동·완료 CTA asset 대상은 크림·청색의 중립 표면과 명확한 disabled 상태로 정돈했다. shape·arithmetic·completion 진입 stagger와 완료 반짝임 burst를 추가했다. desktop preview를 2회 확인해 3칸 문구, 네 제목판, 도로변 질문, 선택 작업표 문구가 모두 각 asset 경계 안에 들어갔고 console/page/request/broken-image·text clipping·overlap 오류가 없음을 확인했다.
- 조치 (dfbc1027 iter_003): `activity-cta-body.png`·`completion-cta-body.png`·`school-speech-bubble-body.png`·`tap-hint-hand.png`를 목표/활동 CTA, 완료 CTA, 좌우 화자 대사, 교사 도움말 target의 실제 raster surface로 연결했다. HUD 외곽의 사용 불가능한 작은 홈은 clip하고 남은 asset의 실제 좌측 2칸·중앙 제목·우측 3칸 중심에 DOM grid를 맞췄으며 진행 fill도 asset 하단 track 전체 좌표에 정렬했다. 수리 이야기 표지판은 120ms 간격으로 진입시키고 완료 제목·반짝임·CTA는 0~660ms 준공식 sequence로 늘렸다. 산술 말풍선은 16px 아래, 선택식은 3px 위, 도로변 안내문은 13px 위로 보정했다. `design_refine_preview` desktop을 확인해 CTA·말풍선·탭 힌트·HUD 텍스트가 각 asset 경계 안에 들어간 것을 확인했고 horizontal overflow·text clipping·overlap·broken image·console/page/request 오류는 0건이었다. 고정 캔버스 계약의 `#viewport`를 자동 검사기가 fixed-overlay로 잡는 기존 false positive만 남았다.
- 조치 (dfbc1027 iter_004): HUD의 `clip-path`를 제거하고 목록·소리·중앙 제목·세 단계·진행률을 `global-hud-frame.png`의 실제 6개 safe zone과 하단 트랙 중심에 절대 좌표로 다시 결합했다. 초기 3번째 계획 문구와 목표 CTA, 도입 CTA, shape/arithmetic 말풍선 텍스트, 완료 나가기 문구를 review 측정값만큼 보정하고 페인트통은 접지점을 유지한 채 1.15배 확대했다. 전용 키패드 asset은 아직 생성되지 않았고 새 asset 참조가 금지된 refine 경계이므로, 무작위 키패드는 새 CSS 재질을 만들지 않고 기존 `wall-choice-plaque-body.png`를 표시창과 4개 입력 행의 실제 표면으로 재사용해 숫자·O만 투명 hit target으로 올렸다. 탭 힌트는 교사 손 실루엣 밖으로 이동하고 방향을 캐릭터 쪽으로 돌렸다. `.hidden` 상태가 더 구체적인 컴포넌트 `display`에 패배하던 문제는 허용된 상태 유틸리티 예외로 `display:none !important`를 적용해 장면 시작 전 CTA/키패드가 노출되지 않게 했다. desktop preview를 2회 캡처했으며 두 번째 결과에서 horizontal overflow·overlap·broken image·console/page/request 오류는 0건이고, HUD 전체 외곽과 각 오버레이가 asset 표면 안에 들어갔다. `#viewport` fixed-overlay는 고정 캔버스 계약에 따른 기존 false positive다.
- 규칙화 메모: 15회로 재발해 rule 승격 재검토를 제안한다. 반복 패턴은 "interaction surface asset이 준비되어도 builder/refine이 동적 텍스트·조작물을 asset의 실제 safe zone/slot 중심에 결합하지 않고 별도 웹 패널 또는 어긋난 overlay로 남김"이다. 초안: "planner/asset_generator가 장면 소품의 interaction surface와 safe zone을 제공한 경우, builder와 design_refine은 동적 텍스트·입력·버튼을 해당 표면 경계 안의 실제 슬롯 중심에 배치한다. 별도 CSS 카드·패널로 대체하거나 asset 표면을 덮지 않으며, preview에서 high finding target의 경계 포함 여부를 확인한다. 필요한 interaction surface asset이 아직 없으면 CSS 재질로 가장하지 말고 중립 기하만 사용하며, 미해결 상태를 asset 요청으로 넘긴다." 반영 위치 제안: `content-harness-pipeline/AGENTS.md`의 CSS/Visual QA 규칙. 사용자 승인 전에는 자동 반영하지 않는다.

### [planner-storyboard-detail-loss] planner.json이 storyboard 세부(문제 보기·대사·오디오·모션·효과)를 압축/누락함

- 대상: content-harness-pipeline/stages/planner.py, schemas/planner_output.schema.json, prompts/planner_system.md (산출: runs/2026-07-08_ch802d08/ch802d08_planner.json)
- 분류 태그: planner-storyboard-detail-loss
- 상태: 열림
- 발생 횟수: 2
- 최초 발생일: 2026-07-13
- 최근 발생일: 2026-07-31
- 사례:
  - 2026-07-13: `2학년_8차시(시간)_임상현.md`(storyboard)와 `ch802d08_planner.json`을 비교하니 차이가 큼. storyboard가 요구한 요소(이미지, 대사, 문제 문구, 보기(distractor), 캐릭터 포즈, 효과, 애니메이션, 오디오/SFX)가 요약되거나 생략됨. 특히 활동2 12문제의 정확한 문제 문구·보기 3개·정답이 planner에서는 content_outline 한 줄로 압축되어 정답만 남고 오답 보기가 사라짐. 사용자가 schema가 너무 정적이거나 prompt 문제로 추정하고, storyboard를 온전히 담을 수정 방향을 요청.
  - 2026-07-31: `runs/2026-07-31_dfbc1027/dfbc1027_planner.json` 검토 후 전체 수정 요청. schema는 PASS하지만 도형 세기 문항 2개의 `answer`가 비어 있고, 도형 찾기 정답 대상이 기계적으로 판정할 수 없는 자연어로만 표현됨. 원문의 `다음 차시 이동`이 완료 섹션에서 누락되고, 무작위 문제 생성 규칙과 고정 예시 문항의 역할이 모호하며, 동일 asset이 두 batch group에 중복되어 runner의 first-consume 로직상 뒤 그룹의 일관성 목적이 무효화됨. 사용자는 전체 보정 후 planner schema 통과를 요구.
- 조치: 2026-07-13 분석 결과를 반영해 현재 schema/prompt에 `sections[].elements`, `questions`, `rendered_text` 구조가 도입됨. 2026-07-31 산출 planner에서 잔존한 의미적 누락을 수정함: 도형별 정답·클릭 target ID·다음 차시 interaction을 명시하고, 무작위 template/예시의 역할을 interaction에 고정하며, asset group 중복과 사용 참조 불일치를 정리함. 공식 planner schema PASS, 중복 ID·누락 참조·빈 정답·group 중복 검사도 PASS.
- 규칙화 메모: 아직 2회. 이 항목은 상위 원인(메타)에 가까움 — 하류 [typeB-problem-text-mismatch-spec], [typeA-prompt-text-small-terse], [spec-success-feedback-missing], [type-per-problem-answer-format] 계열이 "builder가 spec대로 안 만든다"로 반복되는데, 실은 planner가 spec을 온전히 안 넘긴 것이 상류 원인. 5회 이상 반복되면 "planner는 storyboard의 문제 문구·보기·정답·대사·전환/성공 메시지를 원문 그대로 보존하고, 자유문자열로 압축하지 말고 typed 슬롯(questions/dialogue/audio/feedback)에 담는다" 규칙을 planner_system.md에 제안 후보.

### [typeB-correct-note-card-unwanted] 유형 B 정답 시 스탬프와 함께 뜨는 초록 정답 카드 제거

- 대상: content-harness-pipeline/runs/2026-07-08_ch802d08/output/index.html (`#s-b` submitB의 `showStamp(true, q.done, ...)`), production/1-2/08/index.html (`#arithContext` ← `showArithmeticReason`)
- 분류 태그: typeB-correct-note-card-unwanted
- 상태: 열림
- 발생 횟수: 2
- 최초 발생일: 2026-07-13
- 최근 발생일: 2026-08-03
- 사례:
  - 2026-07-13: 유형 B 정답 시 "정답!" 스탬프와 함께 하단에 초록색 카드('1시간', =`q.done`)가 같이 떠서, 스탬프만 나오게 카드를 없애달라고 요청.
  - 2026-08-03: **(다른 차시에서 같은 형태가 재발)** `production/1-2/08` `section_arithmetic_tutorial`에서 "**세 수의 덧셈에서 `7+3+2` 맞추면 나오는 `7+3=10`, `10+2=12` 말풍선 없애기**"라고 지적. `startArithmeticQuestion`의 정답 분기가 `showArithmeticReason(q)` → `showFeedback(...)` 순으로 불러, 도장·정답 신호와 함께 **풀이 설명 말풍선(`#arithContext`, `q.strategy`)이 같이 뜬다.** 1회차 메모("유형 A는 정답 시 `q.note`(풀이 설명)를 카드로 보여줌 — 필요 시 동일하게 뺄지 별도 확인")가 **확인되지 않은 채 남아 있다가 그대로 재발한 것**이다. 사용자 결정으로 이번엔 정답뿐 아니라 **오답 2회·3회 경로까지 통째로 제거**한다. (**조치 완료 2026-08-03** — `production/1-2/08/complete.md` 62번)
- 조치: submitB 정답 분기의 `showStamp(true, q.done, 1300)`을 `showStamp(true, null, 1300)`으로 변경. `.stamp-fx-note:empty{display:none}` 규칙 덕에 note가 비면 카드가 렌더되지 않아 스탬프만 표시됨. (오답 안내 문구·타 유형은 유지)
- 규칙화 메모: 2회. 교훈 후보: **정답 순간에는 "맞았다"는 신호 하나만 낸다 — 풀이·해설·근거는 오답 경로나 사용자가 요청했을 때만 연다.** 정답과 동시에 해설이 뜨면 학습자가 자기 답이 맞았는지 흐리게 읽는다(47번 `#helpCard` 겸직과 같은 증상, 원인은 다르다). 1회차의 "필요 시 별도 확인" 메모를 닫지 않아 다른 차시에서 그대로 재발했으므로, **미확인 메모는 다음 차시 착수 전에 닫는다**도 함께 남긴다. 연관 [content-flow-state-scaffolding-regression].

### [cta-text-offcenter-padding] 티켓 버튼 텍스트가 비대칭 패딩 때문에 한쪽으로 치우침

- 대상: content-harness-pipeline/runs/2026-07-08_ch802d08/output/index.html (`#s-cert #btnNextLesson.wide`)
- 분류 태그: cta-text-offcenter-padding
- 상태: 열림
- 발생 횟수: 1
- 최초 발생일: 2026-07-13
- 최근 발생일: 2026-07-13
- 사례:
  - 2026-07-13: 인증서 씬 오른쪽 CTA(`딱 맞는 길이를 찾아라! 하러 가기 ▶`)가 너무 오른쪽으로 치우쳐 보인다고 지적. 원인: `#s-cert #btnNextLesson.wide{padding:11% 15% 11% 24%}`의 왼쪽 패딩(24%)이 오른쪽(15%)보다 커서, flex `justify-content:center` 텍스트가 오른쪽으로 밀림. 옆의 저장 티켓(`padding:12% 12%` 대칭)은 균형 있게 보임.
- 조치: 왼쪽 24% 비대칭 패딩을 제거하고 대칭(`11% 15%`)으로 맞춰 티켓 중앙에 정렬.
- 규칙화 메모: 아직 1회. 반복되면 "티켓/버튼 표면 텍스트는 좌우 장식(리본/자·책 등)이 대칭인 asset에서는 패딩도 대칭으로 두어 중앙 정렬을 유지한다(한쪽 패딩만 키워 텍스트를 밀지 않는다)" 규칙을 builder_system.md에 제안 후보.

### [fact-list-nonparallel-ending] 알아두기 팩트 리스트 어미가 병렬 안 맞고 일부가 애매함

- 대상: content-harness-pipeline/runs/2026-07-08_ch802d08/output/index.html (`#s-story` 페이지3 STORY facts)
- 분류 태그: fact-list-nonparallel-ending
- 상태: 열림
- 발생 횟수: 3
- 최초 발생일: 2026-07-13
- 최근 발생일: 2026-07-13
- 사례:
  - 2026-07-13: 페이지3 알아두기 3개 중 2번째 "시계 긴바늘이 반 바퀴 돌면 30분"만 명사로 끝나 다른 항목(`~이에요`/`~꺼내요`)과 어미 불일치, "반 바퀴"도 추상적이라 애매하다고 지적. 어떻게 바꿀지 문의.
  - 2026-07-13: (후속) 3번째 "타이머가 울리면 빵을 꺼내요"가 시간 '알아두기'가 아니라 빵 굽기 지시라 결이 안 맞고 이상하다고 지적. 시간 관련 일반 사실로 교체 요청.
  - 2026-07-13: (재발) 교체본 3번째 "타이머는 시간이 다 되면 알려줘요"도 이상하다고 지적 — 정작 퀴즈 문제에는 타이머가 등장하지 않아, 문제 풀이용 시간 지식이어야 할 팩트가 문제에 없는 도구(타이머)를 설명함.
- 조치: 2번째 팩트를 구체적+`~요` 어미로 교체("긴바늘이 6을 가리키면 30분이에요"). 3번째는 (1차)빵 지시→(2차)"타이머는 시간이 다 되면 알려줘요"→(3차)"짧은바늘은 두 숫자 사이 한가운데에 있어요"까지 시도했으나 모두 반려. 시침 팩트는 사실은 맞지만(반일 때 시침은 두 숫자 정중앙) 지속시간 주제 페이지에서 시각 읽기 개념이라 결이 다르고 초급 아이에게 혼란. **최종: 사용자가 팩트 2개만 유지 선택** → ①(분량:1시간의 반) + ②(분침:긴바늘 6)만 남기고 3번째 제거.
- 규칙화 메모: 아직 1회. 반복되면 "불릿/팩트 리스트는 항목 어미를 병렬(모두 ~요 등)로 맞추고, 추상 표현(반 바퀴 등) 대신 아이가 화면에서 확인 가능한 구체 표현을 쓴다" 규칙 후보. ([story-right-page-sparse-content]와 같은 팩트 리스트 대상.)

### [cert-cta-button-two-lines] 인증서 다음차시 CTA 버튼 글자가 두 줄로 나옴

- 대상: content-harness-pipeline/runs/2026-07-08_ch802d08/output/index.html (`#s-cert` `#btnNextLesson`)
- 분류 태그: cert-cta-button-two-lines
- 상태: 열림
- 발생 횟수: 1
- 최초 발생일: 2026-07-13
- 최근 발생일: 2026-07-13
- 사례:
  - 2026-07-13: 인증서 화면의 "딱 맞는 길이를 찾아라! 하러 가기 ▶" 버튼이 두 줄로 줄바꿈됨. 한 줄로 나오게 요청. 원인: `.ticket-btn.wide span{white-space:normal}`(긴 CTA 줄바꿈 허용)이 이 버튼에도 적용 + 대칭 15% 패딩으로 텍스트 안전영역이 289px로 좁음.
- 조치: `#s-cert #btnNextLesson span{white-space:nowrap}` + 이 버튼 폰트 축소, 좌측 장식(리본/책) 피하도록 비대칭 패딩(좌 크게/우 작게)으로 한 줄에 담기게. Playwright로 렌더 검증.
- 규칙화 메모: 아직 1회. 반복되면 "장식이 한쪽에 몰린 티켓 버튼은 텍스트 안전영역을 비대칭 패딩으로 잡고, 한 줄 CTA는 nowrap+영역폭에 맞춘 폰트로" 규칙 후보.

### [transparent-asset-alpha-not-validated] 투명 에셋을 체크무늬 이미지로 교체하고 실제 알파값을 검증하지 않음

- 대상: content-harness-pipeline/runs/2026-07-08_*/output/assets/intro_title_time_repair_v1.png
- 분류 태그: transparent-asset-alpha-not-validated
- 상태: 보류
- 발생 횟수: 7
- 최초 발생일: 2026-07-13
- 최근 발생일: 2026-07-13
- 사례:
  - 2026-07-13: 가운데 흰 배경을 투명하게 요청했으나, 투명 미리보기용 체크무늬가 픽셀에 포함된 생성 이미지를 실제 투명 PNG로 오판해 교체함. 사용자가 실제 알파값이 투명해야 한다고 지적.
  - 2026-07-13: 실제 알파 투명화 후에도 흰색·연한 하늘색 외곽 테두리가 남아 있어 더 깨끗하게 제거해 달라고 요청.
  - 2026-07-13: 외곽 테두리 제거 범위를 과도하게 확장하여 시계판과 스패너의 흰색·밝은 금속 영역까지 투명해졌다고 지적.
  - 2026-07-13: 제한적 외곽 프린지 보정본도 만족스럽지 않아 투명 부분을 다시 처리해 달라고 요청.
  - 2026-07-13: 재처리 결과에 대해 "조금 더 신경 써 달라"며 정밀도와 검수 품질 개선을 재요청.
  - 2026-07-13: 느낌표 오른쪽과 스패너 바깥 사이에 남은 흰색만 제거하고 스패너 내부는 보존해 달라고 이미지로 위치를 지정.
  - 2026-07-13: 위쪽 `박` 글자 아래, 두 줄 사이에 남은 흰색 조각을 이미지로 지정해 제거 요청.
- 조치: 실제 재작업 전 rule 승격 제안 완료. 지정된 흰색 연결 성분만 투명화하고 주변 글자 테두리·별 장식은 보존·검증.
- 규칙화 메모: **2026-07-15 보류(SKIP) 결정.** 사용자 판단: "기술적으로 안 되더라, prompt 처리를 해도." 프롬프트·스키마 수준으로는 해결되지 않는 문제라 rule 승격을 하지 않는다. 근거: 누적 사례가 전부 프롬프트 지시가 아니라 **수동 픽셀 보정**(flood-fill, despill, alpha 마스크 수축, 크로마키 색 교체)으로만 해결됐다. 이미지 생성이 애초에 진짜 alpha를 안 내고 체크무늬를 RGB로 그려주는 것이 근본이며, 이건 프롬프트로 교정할 수 있는 층위가 아니다.
  - 해제 조건: (1) 진짜 alpha 채널을 내는 이미지 생성 도구/MCP가 실행 환경에 생기거나, (2) LLM이 아닌 **결정적 후처리 코드**(캔버스 외곽 연결 성분 flood-fill → despill → 마스크 수축 → alpha 수치 검증)를 파이프라인 단계로 넣기로 하면 다시 `열림`으로 되돌린다. ([asset-generation-method-mismatch]에 기록된 "codex에 이미지 생성 도구 없음"이 (1)의 선행 조건.)
  - 폐기하지 않고 남겨둔 기존 초안: "투명 PNG 수정은 원본을 보존한 채 작업하고, 배경·프린지와 내부의 밝은 소재를 별도 마스크로 분리한다. 교체 전 흰색·검정·고채도 단색 배경에서 외곽 프린지와 내부 손상을 시각 검수하고, RGBA/alpha 범위·투명 픽셀 수·보호 영역 표본을 수치 검증한다. 검수 이미지를 확인하기 전 대상 파일을 덮어쓰지 않는다." — 해제 시 (2)의 코드 사양으로 재활용 가능.

### [story-cert-button-behind-tickets] 마무리 퀴즈 정답 후 인증서 버튼이 답안 티켓 뒤에 가려짐

- 대상: content-harness-pipeline/runs/2026-07-08_ch802d08/output/index.html (`#storyQuizPop` `.sqp-cert` `#btnStoryCert`)
- 분류 태그: story-cert-button-behind-tickets
- 상태: 열림
- 발생 횟수: 1
- 최초 발생일: 2026-07-13
- 최근 발생일: 2026-07-13
- 사례:
  - 2026-07-13: 마무리 퀴즈 정답 후 나타나는 "인증서 받으러 가기" 버튼(금색 배너)이 답안 티켓 3개 뒤에 깔려 텍스트가 안 보임. 원인: `.sqp-cert`(z auto=0)가 `.center-col`(z:10, 티켓 포함)의 형제라 티켓이 위에 렌더됨. 사용자가 버튼이 "가장 위로 오도록" 요청.
- 조치: `.story-quiz-pop .sqp-cert`에 `z-index`를 center-col(10)보다 높게 부여해 버튼이 티켓 위로 올라오게. (필요시 위치도 겹치지 않게 조정)
- 규칙화 메모: 아직 1회. 반복되면 "오버레이 팝업에서 뒤늦게 나타나는 CTA는 기존 콘텐츠(선택지 등)보다 z-index를 높여 가려지지 않게 한다" 규칙 후보.

### [typeC-question-longer-monitor-overflow] 유형 C 문제 문구를 길게 바꾸면 모니터 화면을 벗어남

- 대상: content-harness-pipeline/runs/2026-07-08_ch802d08/output/index.html (`#s-c` `.mon-screen` `.mon-q`/`.timeline-bar`, C_DATA)
- 분류 태그: typeC-question-longer-monitor-overflow
- 상태: 열림
- 발생 횟수: 1
- 최초 발생일: 2026-07-13
- 최근 발생일: 2026-07-13
- 사례:
  - 2026-07-13: 유형 C 4문제(9~12)를 더 친절한 완성형 문장으로 바꾸려는데, 문구가 길어 모니터 유리(`.mon-screen` 47%×32.5%, overflow:hidden)를 벗어남. 어떻게 배치할지 문의 → 3안(서술은 말풍선/다 모니터/하이브리드) 제시. 사용자가 **"다 모니터에 넣기"** 선택.
- 조치: C_DATA `q`를 새 문장으로 교체(9:"도서관 대출 시스템을 켜려면 암호가 필요해요. 24시간은 며칠과 같을까요?", 10:"하루는 오전과 오후로 이루어져 있어요. 빈칸에 알맞은 수를 넣으세요.", 11:"오늘 오후 3시에 책을 빌렸어요. 하루(1일)가 지나면 내일 언제일까요?", 12:"이 마법 책은 딱 1일 동안만 빌릴 수 있어요. 1일은 모두 몇 시간인가요?"). 공간 확보: 처음엔 `#s-c .timeline-bar` 높이를 줄였으나 `object-fit:cover`라 시간대 이미지가 잘려서 사용자가 "시간대 막대는 자르지 말아줘" → 타임라인은 원본 크기 유지하고 `.mon-screen` gap·`.mon-q` 폰트/행간 축소만으로 2~3줄 문장이 유리(430×336px, 여유 있음) 안에 들어가게. Playwright로 각 문제 렌더 검증.
- 규칙화 메모: 아직 1회. 참고: 문제11은 명세상 보기(객관식)이나 현재 키패드-채우기와 입력 방식이 달라, 사용자가 "그대로 두자 일단"으로 **(a) 채우기 유지** 결정(객관식 전환 보류). 반복되면 "고정 아트 화면(모니터 유리 등)에 넣는 텍스트는 화면 실측 용량에 맞춰 길이/폰트/부속요소를 조절하되 아트 이미지(타임라인 등)는 object-fit로 잘리지 않게 원본 비율 유지, 넘치면 서술은 말풍선으로 분리한다" 규칙 후보.

### [typeB-problem-text-mismatch-spec] 유형 B 문제 문자열이 원본 요구사항(기획) 문구와 어긋남

- 대상: content-harness-pipeline/runs/2026-07-08_ch802d08/output/index.html (`B_DATA[*].title`)
- 분류 태그: typeB-problem-text-mismatch-spec
- 상태: 열림
- 발생 횟수: 1
- 최초 발생일: 2026-07-13
- 최근 발생일: 2026-07-13
- 사례:
  - 2026-07-13: 유형 B 4문제의 `title`이 요구사항(기획서 이미지, 문제 5~8)의 완성형 문장과 다르게 축약·재서술되어 있음. 사용자가 이미지에 적힌 문제 문구 그대로 문자열을 바꿔달라고 요청. 예: `독서 교실이 8시에 시작해 9시에 끝났어요. 걸린 시간은?` → `첫 번째 독서 교실은 8시에 시작해서 9시에 끝났어요. 걸린 시간은 얼마인가요?`; Q3은 `독서`가 아니라 `책 정리 봉사활동` 소재로 교체.
- 조치: `B_DATA` 4개 `title`을 이미지의 문제 5~8 문장으로 교체(정답·클록·입력 blank 구조는 유지). Q3 소재를 독서→책 정리 봉사활동으로 반영.
- 규칙화 메모: 아직 1회. 반복되면 "문제 텍스트는 원본 기획(spec)의 완성형 문장을 그대로 쓰고 임의로 축약·재서술하지 않는다" 규칙을 builder_system.md에 제안 후보. ([typeA-prompt-text-small-terse]와 '문제 문구를 아이 대상 완성형 문장으로' 계열.)

### [typeA-prompt-text-small-terse] 유형 A 전광판(글자 제시) 프롬프트가 글자가 작고 문구가 단적임

- 대상: content-harness-pipeline/runs/2026-07-08_ch802d08/output/index.html (`#s-a` clock 모드 `#aPrompt` `.q-time`/`.q-sub`)
- 분류 태그: typeA-prompt-text-small-terse
- 상태: 열림
- 발생 횟수: 1
- 최초 발생일: 2026-07-13
- 최근 발생일: 2026-07-13
- 사례:
  - 2026-07-13: 유형 A에서 전광판에 시계 이미지 대신 글자만 나오는 clock 모드("3시 5분 전 / 같은 시각의 시계는?")의 글자가 더 커도 되고, 문구를 `3시 5분전`(강조) + `그리고 같은 시각의 시계를 찾아주세요!`처럼 바꾸면 좋겠다고 요청.
  - 2026-07-13: (재요청) 일반 문구가 아니라 **4문제 각각 고유 질문 문장**을 지정. 대괄호로 핵심 값 강조: 문제1 "전광판에 [3시 5분 전]이라고 적혀 있어요. 알맞은 시계를 찾아주세요!", 문제2 "멈춰버린 시계가 [11시 50분]을 가리키고 있어요. 다른 말로 어떻게 읽을까요?", 문제3 "다음 중 [8시 15분 전]을 가리키는 시계는 어느 것인가요?", 문제4 "시계가 [4시 55분]에 멈췄어요. 바르게 읽은 것을 고르세요." 보기도 명시(문제1·3 오답 보기 조정: 2시45분→3시55분, 7시15분→8시45분).
- 조치: A_DATA 각 문제에 `q`(고유 질문 문장, `[값]` 강조 마크업) 필드 추가. loadA의 clock/text 두 모드 모두 `.a-question`(대괄호 부분 `.q-hi`로 강조) 렌더로 통일. 문제1·3 choices를 사용자 보기대로 조정(정답 위치는 비균일 유지). CSS `#s-a .a-question`/`.q-hi` 추가, 이전 `.q-time`/`.q-sub` 확대 규칙 대체.
- 규칙화 메모: 아직 1회. 반복되면 "핵심 제시값(전광판 시각 등)은 화면에서 충분히 크게, 질문 문구는 아이 대상 완성형 문장으로" 규칙을 builder_system.md에 제안 후보.

### [aspect-element-stretched-by-fullscreen-flex] 전체화면 flex 오버레이가 내부 aspect-ratio 요소(퀴즈 plaque·티켓)를 세로로 늘려 화면을 꽉 채움

- 대상: content-harness-pipeline/runs/2026-07-08_ch802d08/output/index.html (`#storyQuizPop .plaque`, `.choice-ticket`)
- 분류 태그: aspect-element-stretched-by-fullscreen-flex
- 상태: 열림
- 발생 횟수: 1
- 최초 발생일: 2026-07-13
- 최근 발생일: 2026-07-13
- 사례:
  - 2026-07-13: 이야기 마무리 팝업 퀴즈(`#storyQuizPop`)가 화면 비율에 꽉 차게 너무 크게 나옴. 원인 2개: (1) `.story-quiz-pop{position:absolute;inset:0}`(높이 960 정의)의 flex column에 plaque를 직접 넣어 aspect(1790/900→425)를 무시하고 582로 신장. (2) 답안 행 `#storyQuizChoices`가 base `.row`의 `display:flex`라 티켓이 215×173(aspect 1417/1140)이 아니라 277×375로 신장(글자 세로로 쌓임). 반면 일반 `#s-quiz`는 plaque가 `.center-col`(width:min(900px,94vw)) 안 + 답안행 `#quizChoices`가 `display:grid`(repeat(3,minmax(0,168px)))라 정상.
- 조치: (1) `#storyQuizPop`의 plaque+row를 `#s-quiz`처럼 `.center-col` 래퍼로 감싸고 `#s-story .story-quiz-pop .center-col{width:min(900px,94vw)}`로 폭 고정(#s-story .center-col=1160 오버라이드 회피). (2) grid 규칙 셀렉터에 `#storyQuizChoices`를 추가해 `#quizChoices`와 동일 grid 적용. → plaque 845×425, 티켓 173로 #s-quiz와 동일.
- 규칙화 메모: 아직 1회. 반복되면 "aspect-ratio 기반 asset 요소(plaque/티켓/카드)는 높이가 정의된 전체화면 flex 컨테이너에 직접 넣지 말고, 폭이 정의되고 높이 auto인 래퍼(`.center-col` 패턴) 안에 배치한다(전체화면 flex는 aspect 요소를 세로로 늘림)" 규칙을 builder_system.md에 제안 후보. ([bg-anchor-alignment]의 'aspect 일치' 계열.)

### [text-color-emoji-restraint] 장식성 이모지·빨간 강조 텍스트를 빼고 검은색으로

- 대상: content-harness-pipeline/runs/2026-07-08_ch802d08/output/index.html (`#s-story .bp-right`: `.fact-head` 이모지, `.key-badge`/`.pt`/`.fact-head`/불릿 빨간·코랄 색)
- 분류 태그: text-color-emoji-restraint
- 상태: 열림
- 발생 횟수: 1
- 최초 발생일: 2026-07-13
- 최근 발생일: 2026-07-13
- 사례:
  - 2026-07-13: 방금 추가한 오른쪽 지면에서 `✨` 이모지를 삭제하고, 빨간 폰트(예: `24시간 = 1일`)를 없애고 검은색으로 바꿔달라고 요청.
  - 2026-07-13: (후속) 검정으로 바꾼 뒤 `알아두기` 제목이 "너무 까만색"이라며 색을 약간 바꿔달라고 요청.
  - 2026-07-13: 이야기 3페이지 오븐 이미지의 `30분` 오버레이(`.timer-30`)가 빨간색(#c0392b)이라 검정으로 바꿔달라고 요청.
- 조치: `.fact-head`의 `✨` 제거. `#s-story`의 `.key-badge`(#e0562f)·`.pt`(#c76a3a)·`.fact-head`(#c76a3a)·불릿 `::before`(#e0562f)를 검정 `#1a1a1a`로, `.key-badge` 흰색 text-shadow 제거. (후속) `.fact-head`만 `#1a1a1a`→`var(--ink-soft)`(#7c5a34)로 약간 소프트하게.
- 규칙화 메모: 아직 1회. 반복되면 "본문/지면 텍스트는 장식 이모지와 빨간 강조색을 기본으로 쓰지 않고 검은색을 우선한다(강조는 굵기·크기로)" 규칙을 builder_system.md에 제안 후보. ([redundant-surface-label-text]와 함께 '텍스트 절제' 계열.)

### [story-right-page-sparse-content] 이야기 책 오른쪽 지면이 짧은 문구 하나만 있어 허전함

- 대상: content-harness-pipeline/runs/2026-07-08_ch802d08/output/index.html (`#s-story .bp-right`: `.pt` 페이지 라벨 + `.key-badge` 단문)
- 분류 태그: story-right-page-sparse-content
- 상태: 열림
- 발생 횟수: 1
- 최초 발생일: 2026-07-13
- 최근 발생일: 2026-07-13
- 사례:
  - 2026-07-13: 이야기 씬 오른쪽 지면에 `페이지 N · 라벨` + 굵은 단문(`24시간 = 1일`/`해 그림자로 시간 읽기`/`30분 뒤에 꺼내기`)만 있어 큰 지면 대비 내용이 너무 단적이고 허전하다고 지적. 어떤 형식을 채우면 좋을지 아이디어 요청.
- 조치: 4개 형식 후보 제시 → 사용자가 **미니 팩트 리스트** 선택. STORY 각 페이지에 `facts` 3개 추가(핵심어 badge/말풍선 cap과 중복 없는 보충 정보), `renderStory`에 `✨ 알아두기` 제목 + `.fact-list` 렌더, `#s-story .fact-head`/`.fact-list` CSS 추가하고 `.key-badge`를 헤드라인 크기로 축소해 라벨→핵심어→팩트 위계 구성. Playwright로 3페이지 렌더 검증(지면 안에 다 들어가고 넘침 없음).
- 규칙화 메모: 아직 1회. 반복되면 "책/문서형 지면 레이아웃은 빈 지면을 단문 하나로 두지 말고 제목→핵심개념→보충(1~2줄)→시각요소의 위계로 채우되, 다른 표면(말풍선 등)과 내용 중복을 피한다" 규칙을 builder_system.md에 제안 후보.

### [overlay-plane-perspective-mismatch] 아트 면 위에 얹은 오버레이가 그려진 면의 원근/기울기와 안 맞음

- 대상: content-harness-pipeline/runs/2026-07-08_ch802d08/output/index.html (`#s-story` `.book-page img.ill` vs `.book` 아트) / production/1-2/08/index.html (`section_shape_find`의 `.find-object`)
- 분류 태그: overlay-plane-perspective-mismatch
- 상태: 열림
- 발생 횟수: 3
- 최초 발생일: 2026-07-13
- 최근 발생일: 2026-08-03
- 사례:
  - 2026-07-13: 이야기 씬에서 책 아트(`storybook_base.png`)는 살짝 눕혀진 원근으로 그려져 있는데, 그 위에 얹은 삽화 사진(`.book-page img.ill`)이 정면으로 반듯이 선 사각형이라 책 지면 위에 붕 떠 보임("책은 눕혀져 있는데 사진은 서 있어서 안 맞아"). 사진을 눕히거나 책을 세우는 두 방향 중 어느 쪽이 나은지 문의.
  - 2026-07-13: (후속) 적용한 `rotate(-1.5deg)`(왼쪽 기울기) 때문에 사진 좌상단이 지면 금색 테두리 밖으로 나감. 오른쪽(시계방향)으로 3도 정도 기울여 달라고 요청 → `rotate(-1.5deg)`→`rotate(3deg)`로 변경해 좌상단을 지면 안으로 들임.
  - 2026-08-03: (후속) A안을 실제로 적용했더니 **반대 방향으로 과했다.** `rotateX(62deg)`로 눕힌 공책을 보고 사용자가 "노트가 너무 눕혀져 있다"며 B안(에셋 재생성)으로 전환을 지시. 62°는 배경 책상 상판의 실제 압축비(0.18 ≈ 80°)보다도 오히려 완만한 값이었는데도 과하게 느껴졌다 — **저학년 학습 콘텐츠에서는 원근 정합보다 "■ 모양이 읽히는가"가 우선**이라 물리적으로 맞는 각도가 정답이 아니다. 부수 효과로 상판 깊이(84px)에 맞추느라 공책이 120px까지 작아져 다른 사물(150~210)보다 눈에 띄게 작아진 것도 함께 작용했다.
  - 2026-08-03: `production/1-2/08` `section_shape_find`에서 "책과 도시락이 책상 위에 놓여진 분위기가 안 산다, 살짝 눕혀 달라"는 지적. 실측 결과 원인이 둘이었다. (1) **원근 불일치** — 배경 `classroom-shape-search.png`의 책상 상판은 하이앵글로 그려져 깊이 압축비가 약 0.18(폭 470 : 깊이 84, stage 좌표)인데 `classroom-notebook.png`는 완전 정면 정투영이라 "책상 위에 선 책"으로 읽힘. (2) **좌표 이탈** — `findObjects`의 `square_notebook` `[860,790,185,185]`·`square_lunchbox` `[1480,790,185,185]`가 상판(back edge y≈901, front edge y≈979~985) 위쪽 허공에서 시작하고, 도시락은 오른쪽 끝 x=1665가 책상 back-right corner x≈1636을 넘어간다. 접지 그림자도 없어(`.find-object{filter:var(--ds-sm)}` 균일 드롭섀도만) 부유감이 강화된다. 07-13 사례와 달리 이번은 오버레이가 raster 캐릭터/사물이라 CSS `rotateX`만으로는 두께·측면이 뭉개진다.
  - 2026-08-03: 같은 차시에서 "**페인트통에 모양을 둔 건 좋은데 이미지에 2D 모양을 올려두니 안 어울린다 — 좀 더 기울이거나 접어야 하지 않을까**"라고 지적. 39번이 통 앞면 색을 CSS로 얹으면서 `.paint-can::after`를 `left:30%;top:38%;width:39%;height:27%;border-radius:10%/14%`인 **정면 직사각형**으로 그렸는데, `paint-can-body.png`는 원통이라 앞면이 좌우로 휘고 뚜껑 타원도 기울어 있다. 평평한 사각 면이 곡면 위에 정면으로 붙어 스티커처럼 읽힌다. **앞의 두 사례(얇은 판을 눕히기 / 두꺼운 사물을 재생성)와 또 다른 세 번째 형태 — 곡면 위의 평면**이라 remedy가 회전이 아니라 곡률 정합(`clip-path` 배럴 · 세로 타원 반경 확대 · 색상별 에셋 3종)이다. (**조치 완료 2026-08-03** — complete.md 50번: 대상은 `::after` 색 면으로 확인됐다. `::before`(선)+`::after`(채움) 2겹에 %기반 `clip-path` 아치를 걸고, 띠를 통 실루엣 가까이 넓혀 손잡이 아래로 내렸다. **인상을 만드는 것은 아치가 아니라 가로 명암**이었다.)
- 조치(2026-08-03, 08차시 24번 — `production/1-2/08/complete.md` 24번): **B안(에셋 재생성)으로 확정.** `classroom-notebook.png`를 3/4 하이앵글(세로/가로 0.60)로 다시 그리고, `.find-object.lay-flat`(CSS `rotateX(62deg)`)은 제거했다. 좌표는 상판 폴리곤 안으로 내렸고(`square_notebook` `[910,866,150,150]` / `square_lunchbox` `[1430,829,150,150]`, 핫스팟은 `hotspotRect`로 따로) 접지 그림자 `.find-object.on-desk`를 신설했다. **핵심 교훈 — 저학년 콘텐츠에서는 원근 정합보다 "도형이 읽히는가"가 우선이라 물리적으로 맞는 각도가 정답이 아니다.** 코드에 "다시 CSS로 눕히지 말 것" 주석을 남겼다.
- 조치(2026-07-13): 책은 raster 아트 에셋이라 세우려면 재생성+연쇄 재정렬 비용이 큼 → 대신 사진+오버레이를 함께 감싼 `#s-story .bp-left .ill-wrap`에 `transform:perspective(900px) rotateX(8deg) rotate(-1.5deg);transform-origin:center 68%`를 얹어 지면 면에 눕히고, `img.ill` 드롭섀도를 `0 6px 14px`→`0 3px 7px`로 줄여 '떠 있는 카드' 인상 제거. Playwright로 3페이지 렌더 검증(오버레이 `24`/`30분`도 사진과 함께 눕음, 오른쪽 지면 텍스트는 그대로 유지). 각도는 아트 지면 원근 실측 기반 시작값이라 ±3° 미세조정 여지 있음.
- 규칙화 메모: 2회. [bg-anchor-alignment]와 같은 '아트에 요소 맞추기' 계열이나 remedy가 다름(위치 정렬이 아니라 오버레이 면의 원근/기울기 정합). 반복되면 "아트 표면(책 지면·모니터 유리·책상 상판 등) 위에 얹는 오버레이는 그 표면이 그려진 원근/기울기에 맞춘다. **얇은 판(사진·종이)은 CSS transform으로 눕히고, 두께가 있는 사물(공책·상자)은 에셋을 그 시점으로 생성한다** — 정면 정투영 raster에 `rotateX`를 걸면 측면이 사라져 종이 한 장이 된다. 함께 표면의 실제 폴리곤 좌표(back/front edge, 좌우 corner)를 실측해 배치 rect가 그 안에 들어가는지 확인한다" 규칙을 builder_system.md에 제안 후보.

### [numeric-answer-leading-zero-rejected] 숫자 정답의 선행 0 표기를 오답 처리함

- 대상: content-harness-pipeline/runs/2026-07-08_ch802d08/output/index.html (유형 B 키패드 정답 판정)
- 분류 태그: numeric-answer-leading-zero-rejected
- 상태: 열림
- 발생 횟수: 1
- 최초 발생일: 2026-07-13
- 최근 발생일: 2026-07-13
- 사례:
  - 2026-07-13: `11시 30분부터 30분 후에 끝나요. 끝나는 시각은?` 문제에서 `12시 0분`은 정답이지만 같은 시각인 `12시 00분`은 문자열 불일치로 오답 처리됨. `00분`도 정답으로 인정하도록 요청.
- 조치: 유형 B의 숫자 답안을 비교할 때 빈 입력은 배제하고 선행 0을 제거한 숫자값을 비교하도록 정규화해 `0`과 `00`을 모두 정답으로 인정.
- 규칙화 메모: 아직 1회. 반복되면 "숫자 키패드 답안은 표시 문자열이 아니라 의미상 숫자값으로 비교하며, 선행 0처럼 동치인 표기를 허용한다" 규칙을 builder_system.md에 제안 후보.

### [generated-keypad-assets-not-integrated] 생성한 키패드 에셋이 유형 B 실제 UI에 반영되지 않음

- 대상: content-harness-pipeline/runs/2026-07-08_ch802d08/output/index.html (`#keypad`)
- 분류 태그: generated-keypad-assets-not-integrated
- 상태: 열림
- 발생 횟수: 1
- 최초 발생일: 2026-07-10
- 최근 발생일: 2026-07-13
- 사례:
  - 2026-07-10: 유형 B용 나무 시계문양 바탕판과 빈 버튼 에셋을 생성한 뒤에도 실제 키패드는 기존 크림색 CSS 패널·그라디언트 버튼을 사용하고 있어, 사용자가 새 에셋으로 교체하도록 요청.
- 조치: `#keypad` 배경을 `wood_clock_keypad_base_v1.png`로, 반복 숫자·삭제·닫기 키 표면을 `wood_keypad_button_blank_v1.png`로 교체하고 기존 입력 이벤트와 CSS 텍스트를 유지.
- 규칙화 메모: 아직 1회. 반복되면 "UI용 생성 에셋이 최종 승인되면 임시 CSS 표면을 실제 에셋으로 교체하고 동작·상태 스타일을 회귀 검증한다" 규칙을 builder workflow에 제안 후보.

### [number-board-composition-mismatch] 숫자 나무판 시안의 표면/소품 구성이 요청과 다름

- 대상: content-harness-pipeline/runs/2026-07-08_ch802d08/asset-revisions/number-board/final/number_block_board.png
- 분류 태그: number-board-composition-mismatch
- 상태: 열림
- 발생 횟수: 1
- 최초 발생일: 2026-07-10
- 최근 발생일: 2026-07-10
- 사례:
  - 2026-07-10: 생성된 숫자 나무판 시안에 청록색 판과 숫자 카드가 남아 있음. 사용자는 초록/청록색 표면과 위 숫자 카드를 제거하고 나무판만 남기며, 소품은 오른쪽에 마우스, 왼쪽에 시계들을 배치하길 요청.
- 조치: 이미지 생성으로 청록 판/숫자 카드 없는 단일 나무판 시안을 재생성하고, 오른쪽 마우스·왼쪽 시계 소품 배치로 수정.
- 규칙화 메모: 아직 1회. 반복되면 "reference 기반 asset 생성 후 사용자가 구성 변경을 요청하면 색/표면/소품/텍스트/배치 항목별로 명시해 재생성 prompt에 반영한다" 규칙을 asset generation workflow에 제안 후보.

### [asset-generation-method-mismatch] 이미지 생성 요청을 로컬 렌더링으로 처리함

- 대상: content-harness-pipeline/runs/2026-07-08_ch802d08/asset-revisions/keypad/time_number_keypad.png
- 분류 태그: asset-generation-method-mismatch
- 상태: 열림
- 발생 횟수: 3
- 최초 발생일: 2026-07-10
- 최근 발생일: 2026-07-10
- 사례:
  - 2026-07-10: 사용자가 수 입력 자판 이미지를 만들어달라고 했고, `index.html`에는 붙이지 말고 이미지만 만들라고 요청했는데, 이미지 생성이 아니라 로컬 PIL 렌더링으로 제작함. 사용자가 "이미지 gen으로 해야지"라고 지적.
    - 조치: 로컬 렌더링 시안은 참고용으로만 두고, 이미지 생성 경로로 단일 자판 이미지를 다시 생성한다.
  - 2026-07-10: 복구 완료 "복구가 완료되었어요!" 축하 타이틀을 생성하려고 `codex exec --model gpt-5.5`(파이프라인과 동일 방식)를 돌렸더니, codex(gpt-5.5)가 이미지 생성 도구가 아니라 **로컬 PIL 코드로 타이틀을 그려서** 저장함(로그에 `draw.ellipse`/`star()`/gears 등 PIL 코드). intro 타이틀 같은 퍼피 3D 광택 스타일이 안 나오고 첫 글자 "복"이 시계 아이콘과 겹침. **근본 원인: 현재 codex 설정(`~/.codex/config.toml`)에 이미지 생성 MCP/도구가 없어(등록된 MCP는 db/open-design뿐) 모델이 조용히 PIL 폴백함.** → 현재 환경 codex로는 진짜 이미지 생성 불가.
    - 조치: PIL 산출물 삭제. 사용자에게 (a)이미지gen 경로 제공 (b)기존 plaque 배너 전환 (c)PIL 다듬기 중 선택 요청 → **기존 plaque(`library_dialogue_plaque_blank.png`) 배너 재사용**으로 전환. `#repairDone`에 '복구가 완료되었어요!' `.title`을 얹어 시계 settle 순간 중앙 pop-in(top:64%, goldBurst 동반) 후 CTA 노출.
  - 2026-07-10: 이미지 생성 도구로 만든 투명 `repair_title_complete_v1.png`가 준비된 뒤에도 복구 완료 화면에는 임시 plaque 텍스트 카드가 남아 있어, 사용자가 카드를 빼고 생성 이미지를 화면 가운데에 넣도록 요청.
    - 조치: `#repairDone`을 plaque/text 구조에서 투명 PNG `<img>`로 교체하고, 화면 정중앙에 pop-in되도록 CSS를 수정.
- 규칙화 메모: **3회.** 교훈: (1) 사용자가 이미지 gen을 요구하면 로컬 코드 렌더링으로 대체하지 않는다. (2) 생성 에셋이 준비되면 임시 대체 UI를 남기지 말고 실제 에셋으로 교체한다. 반영 위치: content-harness-pipeline/AGENTS.md 또는 asset generation workflow. 사용자 승인 대기.
  - **⚠️ 2026-07-15 정정 — 이 항목의 "근본 원인" 서술은 더 이상 유효하지 않다.** 위 7/10 사례에 *"codex 설정에 이미지 생성 MCP/도구가 없어 현재 환경 codex로는 진짜 이미지 생성 불가"* 라고 적혀 있으나, 확인 결과 **이미지 생성은 정상 동작한다.** 근거: `runs/2026-07-14_ch802d14`의 asset 21개가 전부 `status: generated`이고 800KB~2.2MB 알파 PNG 일러스트이며, 2026-07-15 full run(ch8a0715)도 asset 28개를 정상 생성했다. `~/.codex/config.toml`의 MCP 목록에 image-gen이 없는 것은 사실이나, 그것이 이미지 생성 불가를 뜻하지 않는다(codex가 다른 경로로 생성함 — `codex-runtime-home/generated_images/`에 산출물이 쌓임).
  - **이 기록이 실제로 해를 끼쳤다.** 2026-07-15 세션에서 이 항목을 근거로 "전체 run은 돌리면 안 된다"고 반복 판단해 version0.3의 end-to-end 검증을 미뤘고, docs/version_log.md와 solved-log.md에 틀린 한계 서술을 커밋했다. 교훈 추가: **problem.md의 과거 환경 진단은 시간이 지나면 낡는다. 이를 근거로 판단하기 전에 실제 산출물로 재확인한다.**
  - 7/10 당시 PIL 폴백이 실제로 있었는지, 아니면 그때도 오진이었는지는 확실치 않다. 어느 쪽이든 현재는 정상이다.

### [ornate-asset-wrong-function] 장식성 강한 에셋(인증서/상장 등)을 기능 UI 표면으로 재사용해 주제와 안 어울림

- 대상: content-harness-pipeline/runs/2026-07-08_ch802d08/output/index.html (`#s-c` 숫자 트레이 `assets/certificate_library_repair.png`; `#s-b` 키패드 `assets/wood_clock_keypad_base_v1.png`+`wood_keypad_button_blank_v1.png`)
- 분류 태그: ornate-asset-wrong-function
- 상태: 열림
- 발생 횟수: 2
- 최초 발생일: 2026-07-10
- 최근 발생일: 2026-07-10
- 사례:
  - 2026-07-10: 유형 C 숫자 블록 트레이 배경으로 `certificate_library_repair.png`(화려한 금색 인증서/상장 액자)를 얹었더니 "너무 안 어울린다"고 지적. 상장 느낌 액자를 기능적 숫자 키패드 표면으로 쓰니 주제(도서관 컴퓨터 재부팅)와 톤이 안 맞고, 좌우로 늘리며 프레임 장식(시계·책)까지 찌그러져 더 어색했음.
    - 조치: 액자 제거. 숫자 블록을 모니터 키보드 위(측정 중심 ~69%)에 직접 배치(단순 트레이), 라벨만 크림색 알약 배경으로 가독 확보. 사용자에게 3가지 방향 제시 후 "액자 제거" 선택. certificate 에셋 파일은 마무리 인증서용으로 보존.
  - 2026-07-10: 유형 B 키패드를 에셋 중심(나무 베이스 `wood_clock_keypad_base_v1.png` + 나무 버튼 `wood_keypad_button_blank_v1.png`)으로 바꿨더니 "너무 어색"하다고 지적. 원인 진단: (1) 나무-위-나무라 버튼/트레이 대비가 거의 없어 버튼이 안 읽힘, (2) 베이스 중앙에 새겨진 시계 음각이 숫자 격자 뒤로 비쳐 지저분·맥락 불일치, (3) 세로형(0.899) 에셋을 `background:100% 100%`로 격자 높이에 늘려 나무결·시계 왜곡, (4) 11개 나무버튼과 달리 '확인하기'만 CSS 금색 글로시라 시각 언어 혼재. 사용자에게 3방향(우드 트레이+밝은 키/예전 심플 복원/에셋 재생성) 제시 → **"우드 트레이 + 밝은 키(CSS)"** 선택.
    - 조치: 우선 CSS로 오목한 나무톤 트레이 + 밝은 크림 베벨 키(진한 갈색 숫자로 고대비) 구성. 삭제/닫기는 같은 크림 타일에 글자색으로만 역할 구분, 확인하기는 같은 타일 실루엣에 금색 강조로 통일.
    - 조치(후속): 사용자가 트레이는 **나무 판 에셋을 쓰되 CSS 효과를 얹길** 원함. 트레이 배경을 `wood_clock_keypad_base_v1.png`로 복귀시키되 CSS로 깊이감 부여 — `filter:drop-shadow`로 리프트, `.keypad::before` inset 그림자 + 중앙 비네트로 오목한 트레이 느낌 + 새겨진 시계 음각을 눌러 완화(밝은 키가 중앙을 덮어 거의 안 보임). 밝은 크림 키는 유지.
    - 조치(최종): 사용자가 참고 이미지(클린 모바일 숫자패드)를 주며 **"이미지 쓰지 말고 CSS로, 색감·디자인은 콘텐츠에 맞게"**로 정리. 나무 판 에셋을 완전히 제거하고 CSS-only 클린 키패드로 재구성 — 크림 패널 + '✓ 정답 입력' 금색 알약 헤더 + 빨강 원형 ✕ 닫기 + 3열 크림 숫자 키(초록 숫자, 보드 정답색과 통일) + 금색 유틸 키(←=백스페이스, 지우기=전체삭제) + 하단 풀폭 금색 '확인'. 숫자 배열도 참고처럼 7-8-9 상단. JS는 `del`을 한 글자 백스페이스로, `clear`(지우기) 추가. 최종 교훈 재확인: **기능적 입력 컨트롤(키패드)은 사진 에셋이 아니라 CSS로 만들고, 팔레트만 콘텐츠 톤에 맞춘다**(이미지 우회는 폐기).
- 규칙화 메모: 2회. 반복되면 "에셋의 장식 강도를 기능에 맞춘다 — 인증서/상장/트로피/시계음각 등 장식 톤 에셋은 기능적 입력/트레이/키패드 표면으로 재사용하지 말고, 입력 표면엔 단순·중립·고대비 표면(나무 트레이/코르크/CSS 타일)을 쓴다. 표면과 그 위 컨트롤은 색/톤을 다르게 해 대비를 확보하고, 장식 asset을 aspect 왜곡(늘림)하지 않는다" 규칙을 builder_system.md에 제안 후보. ([flat-ui-lacks-tactility]와 같은 `#s-b` 키패드 대상 — 기능 UI는 CSS 고대비 탱타일로.)
### [decorative-asset-background-alpha] 모니터 내부 장식 이미지에 불필요한 불투명 배경이 포함됨

- 대상: content-harness-pipeline/runs/2026-07-08_ch802d08/output/index.html (`assets/morning_evening_time_bar.png`)
- 분류 태그: decorative-asset-background-alpha
- 상태: 보류
- 발생 횟수: 1
- 최초 발생일: 2026-07-10
- 최근 발생일: 2026-07-10
- 사례:
  - 2026-07-10: 유형 C 모니터 안에 추가한 아침→저녁 시간대 막대 이미지의 크림색 배경이 화면과 겹쳐 보여, 배경을 투명하게 해야 한다고 지적.
- 조치: 기존 구도를 마젠타 크로마키 배경으로 편집한 뒤 alpha PNG로 추출했다. 보라색 저녁 영역이 디스필에 손상되는 것을 검수에서 발견해 디스필을 끄고 edge-contract 1로 테두리를 정리한 final asset으로 HTML 참조를 교체했다.
- 규칙화 메모: **2026-07-15 보류(SKIP) 결정.** [transparent-asset-alpha-not-validated]·[character-asset-alpha-fringe]와 같은 알파 계열이라 동일 사유로 함께 보류한다 — 프롬프트로는 해결되지 않는 층위. 이 사례도 결국 크로마키 편집·디스필 조정·edge-contract 같은 수동 픽셀 작업으로 해결됐다. 해제 조건은 그 항목들과 같다.
  - 해제 시 살릴 초안: "기존 UI 표면 위에 얹는 장식용 raster asset은 생성 전에 투명 배경 필요 여부를 확인하고 alpha PNG로 검수한다."

### [feedback-stamp-visual-overload] 피드백 도장 이미지가 과밀하고 컨셉 전달이 약함

- 대상: content-harness-pipeline/runs/2026-07-08_ch802d08/{stamp_correct_time,stamp_fail_time}.png · runs/2026-07-15_ch8c0716/output/assets/feedback_stamp_body.png · **runs/2026-07-21_ch8c0718 (planner가 도장을 아예 기획 안 함 → CSS 폴백)**
- 분류 태그: feedback-stamp-visual-overload
- 상태: 조치 (2026-07-21 규칙 추가 + **탐지 A/B 검증 완료**; asset 생성→builder 사용 full-chain은 미검증)
- 발생 횟수: 5 (ch8c0718이 진짜 post-exemplar 재발; 아래 07-21 두 번째 항목)
- 최초 발생일: 2026-07-09
- 최근 발생일: 2026-07-21
- 사례:
  - 2026-07-09: 정답/실패 도장 시안이 시계 눈금, 바늘, 체크/X, 깨짐선, 큰 글자가 겹쳐 너무 이상하게 보임. 사용자가 원형 시계 배경 위에 `정답!`/`실패!` 글자를 단순히 얹는 방식이 낫다고 지적.
  - 2026-07-09: 재생성한 시계 배경까지 초록/빨강으로 물들어 `index.html`의 애니메이션풍 도서관 시계 톤과 맞지 않음. 사용자가 시계는 상태색이 아니라 index.html 느낌의 애니메이션풍 시계로 두고, 글자만 초록/빨강으로 하라고 지적.
  - 2026-07-09: 기존 시계 asset을 결합하는 방식이 아니라, 도장 자체를 단일 이미지로 생성해야 한다고 지적.
  - 2026-07-16: asset_generator 예시(exemplar) 도입 검증 중 관측. leak test(심해 정거장, 보라·라임 art_direction)에서 오답 도장이 연보라 잉크 on 보라 패널로 나와 "오답"이 안 읽힘. 정답=코랄, 오답=슬레이트로 만든 예시도 한국 관습(빨간펜=오답)과 반대였음. 사용자가 "오답이 빨간색이면 좋겠다, 문자열이라도"라고 교정. **결정**(질문 확인): 오답 신호는 **글자·심볼만 빨강**, 도장 몸체는 그 run의 세계관 팔레트 유지. 예시 재생성은 안 함(예시 색은 어차피 art_direction이 덮어씀). 2026-07-09 두 번째 사례("몸체는 세계관색, 글자만 상태색")와 **같은 원칙의 재발**이며, 이번엔 index.html이 아니라 asset_generator/exemplar 층에서 발생.
  - 2026-07-21: (초기 기록 후 정정) ch8c0716 `output/assets/feedback_stamp_body.png`를 직접 열어 확인 → **도장이 아니라 가로 ~2.4:1 장식 명패/현판**(책·시계 아이콘 박힌 빈 배너). `.stamp{aspect-ratio:1960/820}`로 배경 삼아 정답("와, 정답이야!")·오답("띠익")을 얹고, **정답/오답이 같은 asset 한 장**을 공유하며 색만 CSS `filter`로 바꿈(`index.html:790-811`, `showFeedback`). ch8c0717(`repair_feedback_stamp_surface.png`)도 동일하게 단일 asset 색 필터 방식. **⚠️ 정정: 이 둘을 "미해결 신규 facet(5회째)"으로 적었으나 틀렸다.** 생성 시각이 ch8c0716=07-15 19:37, ch8c0717=07-15 18:50으로 **exemplar 도입(07-16 14:12)보다 앞선다.** 즉 fix 이전 산출물이라 "규칙 미비의 증거"가 아니다. 그리고 형태·정답오답 구분·글자 굽기 facet은 이미 `asset_examples/stamp_lettering_craft_{correct,wrong}.png` + `asset_examples.md:16-19`가 정확히 겨냥하고 있다(원형 씰 + 손잡이 = 장면 속 물건, correct/wrong 완전 별개 asset, 문구를 도장 면 안쪽 밴드에 구움). 사실확인 결과: 이 exemplar들은 asset_generator 프롬프트에 본문(`load_asset_examples()`) + `ASSET_EXAMPLES_DIR` 경로로 **실제 주입되고 있다**(`stages/asset_generator.py:44-52`). 미해결이 아니라 **검증 대기** — 07-16 이후 stamp를 생성하는 run이 아직 없다(ch8c0718 07-21은 stamp asset 없음).
  - 2026-07-21 (검증 결과 — 위 "검증 대기"의 실측): 07-16 이후 유일한 full run **ch8c0718(07-21)에서 재발 확인.** 체인을 끝까지 추적: (1) **planner가 도장을 아예 기획 안 함** — `ch8c0718_planner.json`에 "도장/스탬프/stamp" 등장 0회. (2) 따라서 asset_generator도 피드백 도장을 안 만듦(`library_restoration_badge.png` 하나뿐, 이건 outro 보상판). (3) builder가 stamp asset이 없으니 **정답 도장을 순수 CSS로 그림** — `.status-stamp`(노란 이중 원 border + `::before`/`::after` 체크, `index.html:25`). 공통계약의 "정적 표면·재질은 CSS로 흉내내지 않는다"를 정면 위반. (4) design_review는 iter_001에서 **이미 짚음**("정답·오답 피드백을 CSS 원·사각형에서 도서관 수리 도장으로 바꾸면 물성↑", design_review.json:1100) — 그런데 그건 `why_beneficial` 서술로만 남고, iter_004 asset_review가 "신규 asset 불필요"(:629)로 닫아 **도장 asset 요청으로 승격되지 않음.** design_refine은 asset을 못 만드니(경계상 asset 요청은 asset_review 담당) 끝까지 CSS 도장으로 남음. → **결론: exemplar(=asset_generator가 도장을 어떻게 그리나)는 정상이지만, 그 위에서 "피드백 도장을 asset으로 기획/요청하는가"를 아무도 보장 안 한다.** 실패 지점이 asset_generator가 아니라 planner(기획 누락) + asset_review(CSS→도장 승격 거부)다.
- 조치: **2026-07-21 design_review_system.md 두 편집(덮어쓰기 아님, 정리+추가).** owner를 asset_review로 확정하되 REJECT(과함) 대신 "필수 통합 컴포넌트"로 강제. (1) 47행 재작성 — "고정 문구가 구워진 asset은 결함 아님" 예외를 **실제 asset에 한정**하고, "같은 표면을 `background-image` 없이 CSS 도형으로 그리면 결함"을 명시(예외의 CSS-가짜 오독 차단). (2) 41행 뒤 추가 — "정오답 피드백 도장은 **필수 통합 컴포넌트**. `background-image` asset 없이 CSS 도형이면 결함, 정답·오답 별개 asset을 `asset_review.new_asset_requests`에 priority=1·deferred 금지로 요청." planner는 안 건드림(과부하 회피), builder도 안 건드림(생성 권한 없음). asset 생성 권한이 있는 두 stage(planner/asset_review) 중 reactive한 asset_review에 owner를 둠. 남은 약점: design_review는 LLM이라 100% 아님 + 마지막 iter에서 발견 시 다음 iter 없어 미생성 가능(REJECT도 동일). 결정적 backstop(validator에서 "피드백 표면이 asset 없이 CSS면 REJECT")은 미착수(별건). **탐지 A/B 검증(2026-07-21, ch8c0718 iter_006 design-review-only)**: 같은 HTML에서 옛 프롬프트(iter_005)는 `PASS`·도장 asset 요청 0·`#statusStamp` 지적 0이던 것이, 새 프롬프트는 `REJECT` + 정답(priority=1)·오답(priority=2) **별개 도장 asset 요청(deferred 0)** + `#statusStamp` high-severity 결함으로 뒤집힘. 프롬프트만 바꾼 통제 대조라 규칙 효과가 확인됨. 미검증: asset 생성→builder 사용 full-chain(full run 필요).
- 규칙화 메모: **조치 방향 확정·검증됨(별도 rule 승격 불필요).** 상류 갭을 planner(기획 강제)가 아니라 **asset_review(design_review)** 소유로 해결 — planner 과부하를 안 늘리고, asset 생성 권한이 있는 두 stage 중 reactive한 쪽에 owner를 둠. REJECT 대신 "필수 통합 컴포넌트"로 강제(사용자 판단: REJECT는 과함). design_review_system.md 두 편집 후 A/B로 효과 확인(위 조치 참고). **⚠️ 진단 교훈(이번에 두 번 틀림): (1) fix 이전 artifact(ch8c0716)를 보고 "미해결 5회"라 과잉 판정 → [[verify-artifact-predates-fix]]. (2) 정정하며 "exemplar로 조치됨, 검증만 하면 됨"이라 과소 판정 → post-fix run(ch8c0718)을 안 열어보고 단정. 교훈: '조치됨'으로 닫기 전에 fix 이후 실제 산출물을 끝까지(planner→asset→builder→review 체인) 열어 확인한다.** 연관 [ornate-asset-wrong-function](형태-기능 미스매치), [spec-fx-color-mismatch](오답색), [asset-generation-method-mismatch]("CSS로 asset 대체" 계열).

### [character-asset-alpha-fringe] 캐릭터 에셋의 알파/프린지 후처리가 반복 실패함

- 대상: content-harness-pipeline/runs/2026-07-08_ch802d08/output/assets/ (`teacher_*.png`, `kid_librarian_*.png`)
- 분류 태그: character-asset-alpha-fringe
- 상태: 보류
- 발생 횟수: 8
- 최초 발생일: 2026-07-09
- 최근 발생일: 2026-07-13
- 사례:
  - 2026-07-09: 사서 선생님 치마가 투명하게 비쳐 보임(반투명 픽셀 잔존).
  - 2026-07-09: raw 크로마키 결과라 배경이 투명하지 않은 상태로 산출됨.
  - 2026-07-10: output/assets의 teacher 3종이 예전 버전이라 치마 비침이 남아 있음 → asset-revisions final(반투명 0%)로 교체.
  - 2026-07-10: 재생성한 `teacher_happy` 외곽에 보라색 크로마키 프린지 잔존. 원인: 마젠타가 캐릭터의 코랄 의상·피부 가장자리와 충돌 → 초록 크로마키로 재생성해 해결.
  - 2026-07-13: 생성 결과에 체크무늬 배경이 실제 RGB로 포함돼 있어 알파로 오판할 뻔함(캔버스 외곽 연결 영역만 flood-fill로 제거).
  - 2026-07-13: `teacher_happy` 머리 뒤 닫힌 공간에 흰 체크 배경 조각 잔존.
  - 2026-07-13: 얼굴·머리 외곽 전체에 흰 배경 프린지 잔존 → 색상 기준이 아니라 alpha 마스크 3px 수축으로 제거.
  - 2026-07-13: 머리 상단·번 주변에 흰 부분이 조금 남음 → 해당 ROI만 추가 2px 수축.
- 조치: (개별 사례는 그때그때 수동 보정으로 해결. 구조적 대응은 아직 없음.)
- 규칙화 메모: 원래 [character-asset-identity-alpha](17회)에 정체성 문제와 함께 묶여 있었으나, 2026-07-15에 정체성 부분(9회)이 파이프라인 구조로 해소되면서 알파/프린지 8회를 이 태그로 분리했다. **이 항목은 [transparent-asset-alpha-not-validated](7회)와 사실상 같은 문제**(투명 PNG 알파 검증 부재)이므로, 해제 시 두 항목을 하나로 병합해 실질 15회로 다루는 것을 권장한다.
  - **2026-07-15 보류(SKIP) 결정.** [transparent-asset-alpha-not-validated]와 동일 사유 — 프롬프트로는 해결되지 않는 층위의 문제. 해제 조건도 그 항목과 같다(진짜 alpha를 내는 생성 도구, 또는 결정적 후처리 코드 도입).
  - 해제 시 살릴 교훈: 크로마키 색은 대상 팔레트와 충돌하지 않는 색으로 고른다(마젠타가 코랄 의상·피부 경계와 충돌해 보라 프린지가 남았고, 초록으로 바꿔 해결한 사례). 검수 이미지를 확인하기 전 대상 파일을 덮어쓰지 않는다.

### [asset-batch-incomplete-execution] 캐릭터 에셋 배치를 일부만 생성하고 전체 세트를 완료하지 않음

- 대상: content-harness-pipeline/runs/2026-07-08_ch802d08/asset-revisions/characters/generated/
- 분류 태그: asset-batch-incomplete-execution
- 상태: 열림
- 발생 횟수: 1
- 최초 발생일: 2026-07-09
- 최근 발생일: 2026-07-09
- 사례:
  - 2026-07-09: 사용자가 "이미지를 만들어줘"라고 전체 캐릭터 세트 생성을 요청했는데, `teacher_worried.png`와 `kid_librarian_explaining.png` 2개만 생성/검증하고 멈춤. 전체 포즈 세트를 끝까지 생성해야 한다고 지적.
- 조치: 남은 포즈 전체(`teacher_pointing`, `teacher_happy`, `kid_librarian_idle`, `kid_librarian_success`, `kid_librarian_confused`, `kid_librarian_proud`)를 sub-agent 병렬 배치로 생성하고 final alpha PNG 검증까지 진행.
- 규칙화 메모: 아직 1회. 반복되면 "asset batch 요청은 대표 샘플 성공으로 종료하지 말고, poses.md의 전체 required/optional 범위를 명시적으로 완료/보류 판정한다" 규칙을 asset generation workflow에 제안 후보.

### [character-pose-direction-mismatch] 캐릭터가 요구된 방향이 아닌 반대 방향을 가리킴

- 대상: content-harness-pipeline/runs/2026-07-08_ch802d08/asset-revisions/characters/generated/final/kid_librarian_explaining.png
- 분류 태그: character-pose-direction-mismatch
- 상태: 열림
- 발생 횟수: 1
- 최초 발생일: 2026-07-09
- 최근 발생일: 2026-07-09
- 사례:
  - 2026-07-09: `kid_librarian_explaining.png`가 오른쪽 상단을 가리키고 있는데, 의도는 왼쪽 상단을 가리키는 포즈라고 지적.
- 조치: `kid-librarian/poses.md`와 `prompts/batch-01.md`를 viewer 기준 왼쪽 상단을 가리키도록 명시하고, 해당 이미지를 재생성. final alpha PNG 검증 후 `output/assets/kid_librarian_explaining.png`에도 교체 반영.
- 규칙화 메모: 아직 1회. 반복되면 "포즈 방향은 left/right 대신 viewer 기준/화면 기준/캐릭터 기준을 함께 명시하고, 생성 후 시각 QA에서 방향을 확인" 규칙을 asset generation workflow에 제안 후보.

### [bg-anchor-alignment] 배경 아트에 그려진 자리(거치대/프레임)에 요소가 안 맞고 다른 곳에 배치됨

- 대상: content-harness-pipeline/runs/2026-07-08_ch802d08/output/index.html (`#bigClock`, `#s-tut .wb-clock`, `#repairClock`), production/1-2/08/index.html (`.work-area`, `#drawingCanvas`, `.story-card`, `.hotspot`, `.hotspot-number`, `#randomShapes`, `.story-intro-shapes`)
- 분류 태그: bg-anchor-alignment
- 상태: 제안됨(재검토 — 19회)
- 발생 횟수: 19
- 최초 발생일: 2026-07-09
- 최근 발생일: 2026-08-04
- 사례:
  - 2026-07-09: 배경(bg_library_messy_lobby.png)에 시계가 들어갈 원형 거치대가 그려져 있는데, 벽시계가 그 원 밖 다른 위치에 정적 %로 배치되어 있었음. 원의 중심·크기에 맞춰 시계를 앉혀야 함. `background-size:cover`라 뷰포트 종횡비마다 원의 화면 좌표가 달라져 정적 %로는 정렬 불가.
    - 조치: 배경 아트에서 원의 중심선(중심 (862,292), 반지름 155)을 픽셀 측정 → 런타임에서 cover 스케일·크롭을 계산해 시계 중심/지름을 원에 맞추는 JS(`__placeBigClock`, resize 대응) 추가. 시계 PNG의 외곽 rim 채움비(0.859)까지 반영해 rim이 원과 일치하도록 크기 산정.
  - 2026-07-09: 튜토리얼 작업대 매트(repair_workbench_mat_blank.png) 위 시계가 좌하단에 치우쳐 매트에 그려진 연필과 겹침. 매트(푸른 영역) 상하 가운데로 올리고 오른쪽으로 살짝 이동해 연필과 분리 필요.
    - 조치: `#s-tut .wb-clock`을 `top:50%;transform:translateY(-50%);left:14%;width:24%`로 매트 세로 중앙+우측 이동. (workbench는 object-fit:contain이라 asset 좌표가 안정적이라 % 배치로 충분)
  - 2026-07-09: 유형 C 모니터 화면(`.mon-screen`) 텍스트가 모니터 유리 밖으로 삐져나옴("글자가 모니터 안에 안 들어감"). 원인: `library_monitor_body.png`는 세로형(1182×1330)인데 `.monitor-stage` aspect가 `1.5/1`(가로)이라 `object-fit:contain`으로 이미지가 레터박스(좌우 여백)되고, `.mon-screen`은 스테이지(박스) 기준 %라 실제 이미지의 화면 유리 위치와 어긋남. 게다가 height:50%로 유리(측정 34%)보다 큼.
    - 조치: 화면 유리를 픽셀 측정(flood-fill: left25.2/top14.4/w49.1/h34%). `.monitor-stage` aspect를 이미지에 맞춰 `1182/1330`으로 바꿔 레터박스 제거(박스=이미지). `.mon-screen`을 유리에 정렬(left26/top15.5/w47/h32.5, 약 1% inset). 세로형이라 `#s-c .monitor-stage` 폭 760→600px로 축소, 좁아진 유리에 맞게 mon-status/timeline/mon-q/eq-line/cblank 글자·gap 축소. 상단 상태문구(C_INTRO) 중복 꼬리 제거(안내는 새 선생님 말풍선이 담당). 오버레이 사각형을 아트에 그려 유리 안 정렬 시각 검증.
  - 2026-07-09: 이야기(s-story) 책 이미지가 너무 작고 텍스트가 책 지면 밖으로 넘침. 원인: `storybook_base.png`(1536×1024, aspect 1.5)인데 `.book-stage` aspect가 `1.4/1`이라 레터박스 발생 + `#s-story .book-page` 영역(top14/height64 → 하단 78%)이 실제 크림 지면(측정 하단 73.6%)보다 아래까지 내려가 글자가 페이지 밖으로 새어나감.
    - 조치: 크림 지면 픽셀 측정(left11.8/top8.3/w76.4/h65.3%). `.book-stage` aspect를 `1536/1024`로 맞춰 레터박스 제거하고 폭 860→1000px로 확대. `#s-story .book-page`를 금색 테두리 안(left13/top11/w74/h60%)으로 재정렬해 좌:삽화 우:글이 양 지면에 담기도록. 오버레이 사각형+접힘선 렌더로 정렬 시각 검증.
  - 2026-07-10: 복구(`#s-repair`) 씬 배경(bg_library_clean_lobby.png)에도 시계용 원형 거치대가 그려져 있는데, `#repairClock`이 intro처럼 원에 앉지 않고 정적 %(`.wall-clock` left:41%/top:15%)로 벽 원 밖에 떠 있었음. 사용자가 "intro처럼 가운데 동그라미에 넣어라" 지적.
    - 조치: clean lobby bg의 원을 Hough식 밴드 탐색으로 측정(중심 (850,281), 반지름 146, IMG 1672×941), intro와 동일한 cover-scale 배치 JS(`__placeRepairClock`, resize 대응) 추가. 시계 PNG rim 채움비(0.859) 반영해 box=2R/0.859로 산정. 배경에 시계 PNG 합성해 원 안에 정확히 안착 시각 검증(임시 검증 파일은 삭제). (후속: 시계가 회전→감속하며 정상 복귀하는 효과는 다음 단계)
  - 2026-07-13: 이야기 3페이지 오븐 이미지 위 `30분` 오버레이(`.timer-30`)가 이미지 중앙(left50/top50)에 있어 오븐 위에 떠 있음. 이미지 오른쪽에 그려진 둥근 타이머(시계) 면 안에 넣어야 한다고 지적. → 타이머 크림색 면 중심을 이미지 기준 픽셀 측정(약 left71/top66%)해 `.timer-30`을 그 위치로 이동. (`.timer-30`은 `.ill-wrap`(contain, 안정 좌표) 안이라 정적 %로 충분하고 사진 tilt도 함께 따라감)
  - 2026-08-03: `production/1-2/08` `section_arithmetic_tutorial`에서 "모양이 3줄이 되면 담장 바깥으로 모양이 삐져나온다"고 지적. `.work-area`(top:250 / height:570 / `align-content:center`)는 12개일 때 5열×3행 = 292~778(stage)로 자라는데, 배경 `school-wall-closeup.png`의 벽돌 면은 실측 stage y **367~878**이라 1행이 담장 위 캡·하늘로 **75px** 올라간다. 10개(2행)일 때만 우연히 면 안에 들어와 있어 그동안 안 보였다. (**조치 완료 2026-08-03** — complete.md 28번: `.work-area{top:250px→338px}`로 담장 면 중앙 622에 맞춰 12개(3행)가 stage y 380~866으로 면 안에 들어온다.)
  - 2026-08-03: 같은 차시 `section_free_drawing`에서 "담장 바깥에 이미지가 짤리기도 한다"고 지적. `#drawingCanvas`(390,275,1370×540 → x 390~1760 / y 275~815)가 배경 `school-wall-drawing.png`의 담장 면(실측 stage x **172~1776** / y **308~877**)보다 위로 33px 튀어나와 있고, `.drawn-shape`는 150px를 `translate(-50%,-50%)`로 클릭점에 놓으므로 가장자리에서 최대 75px가 캔버스 밖으로 나가 `overflow:hidden`에 잘린다. (**조치 완료 2026-08-03** — complete.md 30번: `#drawingCanvas`를 `top:320px;width:1320px`로 담장 면 안에 넣고, 클릭 좌표를 `drawnHalfExtent()`(회전 반영 `(s/2)(|cosθ|+|sinθ|)`)만큼 clamp한다. `#completedMuralPreview`도 같은 박스로 맞췄다.)
  - 2026-08-03: 같은 차시 `section_math_story`에서 "표지판 설명이 그림 가운데 정렬이 아니라 아래로 치우쳐져 잘린다"고 지적. `.story-card`는 안내판 에셋(`story-roadside-info-board.png`, 원본 1420×220)을 1300×600으로 늘려 쓰면서 패딩을 `282px 108px 118px`로 손으로 맞춰 놨는데, 에셋의 크림 면은 비율 y **0.168~0.736**이라 카드 기준 y 101~442(stage 696~1037)다. 현재 글 영역은 stage 877~1077로 크림 면 하단에 걸쳐 있고, 카드 자체가 `bottom:-115px`로 무대 밖에 걸쳐 있어 긴 대사의 마지막 줄과 `다음 ▸` 버튼이 화면 아래로 잘린다. (**조치 완료 2026-08-03** — complete.md 33번: 패딩을 에셋 크림 면 비율 `101px 64px 153px`로 다시 잡고 `align-content:center` 추가. 가로 패딩을 줄여 글 폭이 1084→1172가 되면서 `--fs-md`로 올려도 가장 긴 beat가 334px로 크림 면 346px 안에 들어간다. **카드 크기·`.sign-row`·에셋은 그대로**.)
  - 2026-08-03: 같은 차시 `section_shape_find`에서 "아이템 호버 시 노란색 테두리가 나오는데 **테두리를 이미지에 맞추라**"고 지적. `.hotspot`은 `border:5px solid`를 요소 박스에 그리는데, 박스는 `hotspotDefs`(= `findObjects`의 `hotspotRect`‖`rect`)로 **손으로 잡은 사각형**이고 사물 그림(`.find-object`, `object-fit:contain`)의 실제 알파 bbox와 크기·중심이 다르다. 예: `triangle_ruler`는 그림 `rect:[500,395,210,210]`과 핫스팟이 같은 값이지만 삼각자 알파는 그 정사각형의 일부만 채우고, `square_notebook`은 그림 `[910,866,150,150]` vs 핫스팟 `[906,890,150,102]`로 아예 따로 논다. 그래서 노란 테두리가 사물보다 크거나 어긋난 자리에 뜬다.
  - 2026-08-03: 같은 차시 `section_random_problems`에서 "담장은 **가운데쪽 큰 비어 있는 곳에만** 모양을 두고 키패드는 약간 작게 해서 공간을 내라"고 지적. 29-b에서 `#randomShapes`를 `left:180px`(x 180~756)로 옮겼는데, 배경 `school-wall-problem-scene.png`의 **깨끗한 중앙은 x 374~1522**이고 x 253~374는 낮은 대비 추상 벽화 구간이다(todo.md 실측표). 즉 도형 박스 왼쪽 194px이 벽화 위에 걸쳐 있다. 오른쪽 `#randomPanel`(left 690, width 940)이 중앙을 다 차지해 도형을 중앙으로 옮길 여유가 없는 것이 원인이라, 키패드·패널 폭을 줄여 중앙 면을 비워야 한다.
  - 2026-08-03: 같은 차시 `section_math_story`에서 "`모양을 길에서 본 적이 있나요?` 위에 모양이 있는데 그게 아니라 **두 카드 사이**, 카드 내부가 아니라 **배경화면 앞 화면 가운데쪽**에 두라"고 지적. 32번이 원문 md 449~451행대로 `.story-intro-shapes`를 인트로 판(`#storyIntroBoard`) **안**에 넣었는데, 판의 크림 면 가용 높이가 128px뿐이라 도형이 `height:50px`로 눌려 있다. 사용자는 판 안이 아니라 제목 배너와 인트로 판 **사이의 빈 배경 면**을 쓰라는 것이다. **원문 배치를 사용자 지시가 덮는 사례**다(34번과 같은 성격).
  - 2026-08-03: 같은 차시 `section_arithmetic_tutorial`에서 "**3줄일 때도 도형의 시작점(세로 위치)을 2줄일 때와 똑같이** 하자"고 지적. 28번이 `.work-area{top:250 → 338}`로 3행을 담장 면 안에 넣어 **면 이탈은 해결했지만**, `align-content:center`가 그대로라 행 수가 바뀌면 블록이 위아래로 함께 자라 첫 줄 y가 **3행 380 / 2행 463으로 83px 흔들린다.** 튜토리얼은 한 화면에서 10개 → 12개로 늘어나므로 이미 놓여 있던 도형까지 통째로 밀려 올라간다. **앞선 사례들이 "면 안에 들어가는가"를 봤다면 이번은 "개수가 변할 때 앵커가 고정되어 있는가"다** — 면 안이더라도 중앙 정렬이면 앵커는 고정이 아니다. (**조치 완료 2026-08-03** — complete.md 46번: `.work-area{align-content:center → start}` + `top:338 → 354`. 행 수와 무관하게 첫 줄이 y 380이다. `#paintIntroVisual`만 한 줄 고정 배치라 `center`를 되돌렸다.)
  - 2026-08-03: 같은 차시 `section_random_problems`에서 "제목 이미지를 아래로 내리는데 **문제와 보기도 같이** 내려 줘, 너무 위에 있다"고 지적. 배경 담장 면은 y **380~946**인데 제목(58~198)도 문제 작업표(205~425)도 **그 위 하늘 구간**에 떠 있었다. 도형(390~890)만 면 위에 있어 좌우가 서로 다른 높이에서 시작했다. **41-b가 가로(x)를 면 안으로 넣을 때 세로(y)는 같이 보지 않은 것**이 남아 있었던 셈이다. 내릴 수 있는 폭은 키패드 바닥(859)과 진행 막대(956) 사이 97px로 이미 정해져 있었다. (**조치 완료 2026-08-03** — complete.md 55번: 제목 +60 / 판 +73. 작업표가 하늘·담장 경계를 걸치는 자리가 최선이고 남은 여유는 24px다.)
  - 2026-08-03: 같은 차시 `section_free_drawing`에서 "모양으로 그리기 이미지도 약간 내려 달라"고 지적. 55번과 같은 형태다 — 담장 면이 y 308~877인데 제목만 상단 바 바로 아래(62~202)에 붙어 있었다. **51번에서 다섯 씬에 제목을 새로 넣을 때 "상단"을 무대 위쪽으로만 읽고 배경의 작업 면 기준으로 잡지 않은 것**이 씬4·5에서 연달아 지적된 것이다. (**조치 완료 2026-08-03** — complete.md 56번: 제목 +48. 도입 대사 말풍선이 공용 기본값 top:220이라 제목과 x가 겹쳐, 말풍선도 씬 전용 top:270으로 함께 내렸다.)
  - 2026-08-03: 같은 차시 `section_arithmetic_tutorial`에서 "**담장 바뀌었을 때 모양이 나오는 위치 약간 아래로 내려주기**"라고 지적. 뺄셈 3문항(`q_subtract_12_2`·`q_subtract_10_3`·`q_subtract_12_2_3`)은 배경이 `school-wall-second`로 바뀌는데 **도형 박스(`.work-area{top:354px}`)는 덧셈과 같은 좌표를 그대로 쓴다.** 두 배경의 작업 면이 다르다 — `school-wall-closeup`은 y 367~878인데 `school-wall-second`는 y **364~990**으로 112px 더 길다. 그래서 같은 좌표를 쓰면 도형이 면 위쪽(실측 y 380~850)에 몰리고 **아래 140px이 빈 담장으로 남는다.** 앞선 사례들이 "면 밖으로 나갔다"였다면 이번은 **"면이 바뀌었는데 좌표가 안 따라갔다"**로, 같은 씬 안에서 배경이 교체되는 경우를 실측표가 배경별로 갖고 있으면서도 코드는 한 값만 쓴 것이다. (**조치 완료 2026-08-03** — `production/1-2/08/complete.md` 63번)
  - 2026-08-04: 같은 차시 `section_random_problems`에서 "**모양 위치 약간 아래로 내리기**"라고 지적. `#randomShapes{top:390px}`는 담장 면(y **380~946**) **안에는 있지만** 패딩 16을 더해도 첫 줄이 y 406이라 담장 상단 캡 바로 아래에 붙어 있었다. 아래로는 여유가 남아 있었다 — 최대 4행(D 유형 19개) 콘텐츠가 y 406~874로 끝나 면 하단까지 72px이 비어 있다. **앞선 사례들이 "면 밖으로 나갔다"·"면이 바뀌었는데 좌표가 안 따라갔다"였다면 이번은 "면 안이지만 한쪽 모서리에 붙어 있다"**로, 실측 좌표를 경계선으로만 쓰고 **면 안에서의 여백 배분은 보지 않은** 경우다. (**조치 완료 2026-08-04** — `production/1-2/08/complete.md` 67번)
  - 2026-08-04: 같은 차시 `section_shape_find`에서 "**모양 찾기와 세기에서 선생님과 학생 위치 책상 밟지 말고 바닥을 밟고 있게** 해 달라"고 지적(오프닝 대화 인물 `#shapeCharacter` 한정, 서 있는 학생은 대상 아님). 공용 `.character.left/.right{bottom:-12px}`는 **무대 바닥** 기준이라 발끝이 stage y 1040(아이)·1054(교사)에 오는데, 교실 배경에서 그 높이는 **책상 상판·의자 구간**(뒷모서리 901 · 앞모서리 979~985)이다. 사람이 설 수 있는 면은 벽·바닥 경계(y≈818)와 책상 뒷모서리(901) 사이의 통로뿐이고, **같은 씬의 `#shapeSceneStudent`는 이미 그 통로(발끝 y≈880)에 서 있었다.** 앞선 사례가 전부 **콘텐츠 박스 대 배경 면**이었다면 이번은 **인물의 접지선 대 배경의 지면**이다 — 인물은 씬 공용 규칙(`bottom`)으로 놓여 있어서 "배경 면에 맞출 대상"으로 아예 세지 않았다. 게다가 그 공용 규칙에는 *"bottom은 건드리지 않는다 — 발끝이 같은 바닥선에 남아야 크기 차이가 키 차이로 읽힌다"*(38번)는 **정당한 반대 근거가 주석으로 달려 있어**, 규칙을 지킨 결과가 이 씬에서만 틀린 그림이 됐다. (**조치 완료 2026-08-04** — `production/1-2/08/complete.md` 84번: 씬 전용 `#shapeCharacter` 오버라이드로 발끝을 통로 바닥에 맞추고, 공용 값과 다른 씬은 그대로 뒀다.)
  - 2026-08-04: 같은 차시 `section_shape_find`에서 "**삼각형 모양에 번호를 붙여 주는 게 가운데가 아니다. 캐릭터가 움직이면 고깔이 왼쪽으로 살짝 움직이니 그것도 맞춰야 하고, 삼각자는 자 에셋 중앙에 숫자를 붙여라**"고 지적. 3회 오답 뒤 뜨는 번호 배지(`.hotspot-number`)가 `left:50%;top:50%`로 **핫스팟 박스의 중심**에 붙어 있었다. 두 가지가 겹쳤다 — (1) 핫스팟 박스는 손으로 잡은 사각형이라 그 중심이 삼각형 도형의 중심이 아니다(삼각자는 박스 중심이 빗변 밖 27px, 배지 절반이 도형 밖에 걸린다), (2) `triangle_party_hat`의 핫스팟은 **세 포즈의 머리를 모두 덮는 고정 박스**(25번이 의도적으로 고정)인데 모자 **그림**은 포즈마다 `HAT_POSE_RECT`로 31px 좌우 이동한다 → 오답 피드백으로 학생이 `thinking`이 되면 모자만 왼쪽으로 가고 배지는 제자리에 남는다. 앞선 사례(a)가 "**정지한** 그림의 알파 bbox에 맞춰라"였다면 이번은 **"그림이 움직이면 그 위 오버레이도 같은 좌표계를 따라가야 한다"** 이고, 게다가 **삼각형은 알파 bbox 중심조차 정답이 아니다**(내접원 중심을 써야 원형 배지가 도형 안에 들어간다). (**조치 완료 2026-08-04** — `production/1-2/08/complete.md` 91번: `findObjects[].numberAnchor`(사물 rect 안 비율, 내접원 중심)를 도입하고 `positionHotspotNumber()`가 사물 그림의 **현재** rect 기준으로 배지를 놓는다. `positionPartyHat`이 포즈를 옮길 때마다 `refreshHotspotNumbers()`로 함께 옮긴다.)
- 규칙화 메모: **19회 → rule 재검토 제안(2026-08-04).** 새 1건은 초안에 **(h) 그림 위에 얹는 오버레이(번호·뱃지·표시)는 클릭 영역이 아니라 그림의 좌표를 따른다 — 클릭 영역을 일부러 고정해 둔 요소(포즈마다 움직이는 그림의 핫스팟)라면 오버레이는 그 고정 박스가 아니라 그림 쪽에 물린다. 그리고 삼각형처럼 박스를 다 채우지 않는 도형에는 bbox 중심이 아니라 내접원 중심을 쓴다**를 더한다.
- 규칙화 메모(18회 시점): **18회 → rule 재검토 제안(2026-08-04).** 새 1건은 초안에 **(g) 배경 면에 맞출 대상에는 콘텐츠 박스뿐 아니라 인물의 접지선도 포함된다 — 지면이 그려진 배경(원근이 있는 실내·야외)에서 인물을 무대 바닥(`bottom:0`) 기준으로 두면 배경의 지면과 어긋난다. 씬 공용 인물 규칙이 있어도 배경마다 접지선은 다시 잡는다**를 더한다. 함께 적을 것: **같은 씬에 이미 올바르게 앉은 요소가 있으면 그 요소의 접지선을 기준값으로 쓴다**(여기서는 `#shapeSceneStudent`).
- 규칙화 메모(17회 시점): **17회 → rule 재검토 제안(2026-08-04).** 새 1건은 초안에 **(f) 면 좌표는 합격선이 아니라 배치 기준이다 — 박스를 면 안에 넣은 뒤 위·아래 여백이 한쪽으로 몰려 있지 않은지 확인한다**를 더한다. (a)~(e)는 전부 "면을 벗어났는가"를 묻는데, 면 안이어도 모서리에 붙어 있으면 지적이 온다.
- 규칙화 메모(16회 시점): **16회 → rule 재검토 제안(2026-08-03).** 새 1건은 초안에 **(e) 한 씬에서 배경이 교체되면 그 배경의 면 좌표로 콘텐츠 박스를 다시 잡는다**를 더한다 — 배경별 실측표는 있는데 코드가 한 좌표만 쓰면 표가 있어도 소용이 없다.
- 규칙화 메모(15회 시점): **15회 → rule 재검토 제안(2026-08-03).** 새 요소를 여러 씬에 한 번에 넣을 때는 **씬마다 배경 면 좌표로 자리를 잡는다** — 51번처럼 한 좌표를 여러 씬에 복사하면 배경이 다른 만큼 그대로 어긋난다(55·56번이 그 뒤처리였다).
- 규칙화 메모(14회 시점): **14회 → rule 재검토 제안(2026-08-03).** 새 1건은 초안에 **(d) 면 안으로 넣을 때 x와 y를 같이 본다**를 더한다 — 41-b는 가로만 면 안으로 넣고 세로는 하늘에 남겨 뒀다가 55번에서 다시 지적받았다.
- 규칙화 메모(13회 시점): **13회 → rule 재검토 제안(2026-08-03).** 새 1건은 초안에 **(c) 개수가 변하는 콘텐츠 박스는 정렬 기준을 면의 고정 모서리(위 또는 아래)에 둔다 — `align-content:center`는 개수가 바뀔 때마다 앵커가 움직인다**를 추가한다. 9회 시점의 "최대 개수 기준으로 면 안에 들어가는지 확인한다"만으로는 이 증상이 안 잡힌다(최대 개수에서는 면 안이었다).
- 규칙화 메모(12회 시점): **12회 → rule 재검토 제안(2026-08-03).** 새 3건은 앞의 "면 좌표 실측" 계열에 더해 **(a) 요소 박스가 아니라 그림의 알파 bbox에 맞춰야 하는 경우**(핫스팟 테두리)와 **(b) 배경의 "쓸 수 있는 면"과 "쓰면 안 되는 면(벽화·저대비 구간)"을 구분해야 하는 경우**를 추가한다. 27번([speech-bubble-anchor-detached])의 교훈("앵커는 박스가 아니라 알파 bbox")과 같은 원인이 다른 요소에서 재발한 것이므로 승격 초안에 함께 넣는다.
- 규칙화 메모(9회 시점): **9회 → rule 재검토 제안(2026-08-03).** 08차시 3건은 "asset 비율/레터박스" 문제가 아니라 **배경 아트가 정한 작업 면(담장·크림 패널)의 stage 좌표를 재지 않고 요소 박스를 눈대중으로 잡은** 경우다. 초안에 다음을 추가 제안: "배경 위에 콘텐츠 박스를 놓기 전에 그 면의 stage 좌표를 픽셀로 실측해 주석으로 남기고, 박스 크기가 콘텐츠 개수에 따라 자라면 **최대 개수 기준으로** 면 안에 들어가는지 확인한다." 실측값은 `production/1-2/08/todo.md`의 "배경 담장 면 실측값" 표에 모아 둔다.
- 규칙화 메모(기존): **6회 → rule 승격 제안.** 교훈: **asset을 얹는 컨테이너는 `aspect-ratio`를 asset 원본 비율에 맞춰라 — 안 맞으면 `object-fit:contain`이 레터박스를 만들어 %좌표 오버레이가 어긋난다. 또 `background-size:cover` 배경의 앵커(원형 거치대 등)는 정적 %로 못 맞추므로, 원 지오메트리를 픽셀 측정해 런타임에서 cover 스케일·크롭을 계산하는 JS로 앉히고 resize에 재적용한다(intro의 `__placeBigClock`/복구의 `__placeRepairClock` 패턴 재사용).** 반영 위치: builder_system.md. 사용자 승인 대기.

### [motion-supporting-narration] 나레이션이 말하는 상황을 뒷받침하는 시각 액션이 없고 등장 애니메이션이 밋밋함

- 대상: content-harness-pipeline/runs/2026-07-08_ch802d08/output/index.html (`#s-problem` `#bigClock`, `.dlg-actor`) · production/1-2/08/index.html (`section_arithmetic_tutorial` — `arithmeticIntroBeats`, `#arithPaintCans`)
- 분류 태그: motion-supporting-narration
- 상태: 열림
- 발생 횟수: 2
- 최초 발생일: 2026-07-10
- 최근 발생일: 2026-08-04
- 사례:
  - 2026-07-10: 인트로에서 선생님이 "큰일 났어! 시계가 고장 나서 시간이 뒤죽박죽이야!"라고 말하는데 **무엇이 큰일인지 보여주는 시각 액션이 없음**. 시계가 (CSS `.spin`으로) 처음부터 일정하게만 돌아, '정상이던 시계가 점점 빨라지며 고장 나는' 서사가 안 보임. 또 꼬마 사서 등장이 `.pop`(단순 튀어오름)이라 "그냥 생성되는" 느낌. 사용자가 (a)시계 정상→점점 빨라짐 표현 + 하이라이트, (b)등장 애니메이션 개선을 요청.
    - 조치: (a) `#bigClock`에서 CSS `spin` 제거하고 JS 컨트롤러(`__introClock`) 추가 — `startNormal`(느긋, 6s/바퀴) → beat0에서 `runaway`로 ease-in 가속(2.6s)해 폭주(0.24s/바퀴). 하이라이트는 경고 글로우(`clockPanicGlow` 펄스) + 진입 흔들림(`clockShake`, 배치 transform 유지). (b) `.pop` → `hero-in`(오른쪽에서 슬라이드+오버슈트 안착) + 착지 반짝임(`sparkOnEl`). __playProblemIntro/beat 컨트롤러에 연결.
  - 2026-08-04: 세 수의 덧셈과 뺄셈 씬에서 **"이것을 페인트라고 해요"라고 소개하는 순간에 페인트 통은 이미 화면에 나와 있다.** 씬이 열릴 때부터 `#arithPaintCan1`이 그려져 있어, 소개 대사가 가리키는 대상이 무엇인지 시선을 끌어 줄 등장·강조 액션이 하나도 없다. 사용자 지시: "대사를 치면서 페인트가 나타나고 하이라이트가 진행되게 — 초등학생이니까 이해하기 쉽게". `production/1-2/08/todo.md` 82번. 앞 씬(`section_shape_find`)은 52번으로 이미 대사 1개 ↔ 짝 1벌 공개가 물려 있어, 이 씬만 규칙에서 빠져 있던 자리다.
    - 조치(2026-08-04 완료): `arithmeticIntroBeats`에 `cans`·`spotlight`를 얹어 **등장 시점을 대사 데이터가 정하게** 했다(`preBeats[].cans`와 같은 방식). `setPaintCans`에 `'none'` 상태 추가 — 소개 대사 전에는 통이 없고, 대사 순간에 `pop`으로 등장하며 `.paint-can.spotlight`(`canSpotlight` = 글로우 + `scale(1.07)`, 3회)로 지목된다. 두 애니메이션은 `.arriving.spotlight` 한 줄로 묶고 글로우를 pop 길이만큼 미뤘다(별도 규칙이면 `animation` 속성이 통째로 덮여 하나만 재생된다). 글로우만으로는 크림색 담장 위에서 안 읽혀 크기 펄스를 함께 넣은 것은 정점 프레임 실측 결과다.
- 규칙화 메모: 아직 2회. 반복되면 "대사가 상황·감정을 말하거나(예: 위기·고장·성공) **화면의 대상을 처음 소개·지시하면**, 그 순간에 대상이 등장하거나 하이라이트되는 시각 액션을 동반한다(정적 나레이션 금지 — 이미 떠 있는 대상을 말로만 가리키지 않는다). 캐릭터 등장은 단순 pop/opacity가 아니라 방향성 있는 등장(슬라이드+오버슈트+착지 이펙트)으로" 규칙을 builder_system.md에 제안 후보. 연관 [narration-visual-mismatch](그쪽은 대사와 화면의 **속성**(색·개수)이 어긋난 것, 이쪽은 속성은 맞는데 **타이밍·강조**가 없는 것 — 같은 태그로 묶지 말 것).

### [beat-timing-vs-audio] 순차 beat의 자동전환 지연이 실제 음성 길이보다 짧아 말풍선이 대사 도중 사라짐

- 대상: content-harness-pipeline/runs/2026-07-08_ch802d08/output/index.html (`#s-repair` 대사 beat `delays`)
- 분류 태그: beat-timing-vs-audio
- 상태: 열림
- 발생 횟수: 1
- 최초 발생일: 2026-07-10
- 최근 발생일: 2026-07-10
- 사례:
  - 2026-07-10: 복구 씬 선생님 대사(take10) 말풍선이 대사가 끝나기 전에 사라짐. 원인: beat 자동전환 지연 `delays[2]=7000ms`가 실제 음성 길이(take10=10.56s)보다 3.5s 짧아, 다음 beat의 `hideAll()`이 대사 도중 말풍선을 숨김. (delays[n]은 'beat n-1이 뜬 뒤 beat n까지의 대기'라 곧 말풍선 표시 시간)
- 조치: 음성 wav 길이를 실측(take09=3.96s, take10=10.56s) 후 `delays`를 `[500,4200,7000]`→`[500,4500,11100]`로 상향(각 대사 길이+여유). 주석에 실측값과 delays 의미 명시.
- 규칙화 메모: 아직 1회. 반복되면 "beat 순차 대사의 자동전환 지연은 임의값이 아니라 대응 음성(wav) 길이를 실측해 (길이+여유)로 잡는다. 재녹음 시 지연도 함께 갱신" 규칙을 builder_system.md에 제안 후보. ([sequential-scene-choreography]의 하위 타이밍 이슈)

### [element-reveal-vs-bg-transition] 새 배경에 속한 요소가 배경 전환보다 먼저 나타나 이전 배경 위에 떠 보임

- 대상: content-harness-pipeline/runs/2026-07-08_ch802d08/output/index.html (`#s-repair` `#repairClock`, `repairMessy` 전환)
- 분류 태그: element-reveal-vs-bg-transition
- 상태: 열림
- 발생 횟수: 1
- 최초 발생일: 2026-07-10
- 최근 발생일: 2026-07-10
- 사례:
  - 2026-07-10: 유형 C 종료 후 복구 씬에서, 시계가 배경 전환(messy→clean fade)보다 먼저 떠 있음. 원인: `#repairClock`(z-index 8)은 씬 진입 즉시 보이는데, 시계가 앉는 원(ring)은 clean 배경에 있어 `repairMessy` 오버레이(z-index 1)가 700ms 뒤부터 1.4s 걸쳐 fade-out 될 때까지 가려짐. 그래서 시계가 이전(messy) 배경 위에 붕 떠 보임. 사용자가 "배경 전환과 동시에 시계를 보여달라" 요청.
- 조치: `nextC`에서 복구 씬 진입 시 시계를 `opacity:0`으로 숨겼다가, `repairMessy`가 fade-out을 시작하는 시점(700ms)에 `transition:opacity 1.4s`로 clean 배경과 같은 속도로 fade-in. `spin()` 시작에 `opacity:1` 기본 표시를 넣어 메뉴 직접 진입/재진입에도 안전.
- 규칙화 메모: 아직 1회. 반복되면 "배경이 fade로 전환되는 씬에서 '새 배경의 앵커(거치대/원 등)에 앉는 요소'는 이전 배경 위에 미리 띄우지 말고, 배경 전환과 동기화해 같은 타이밍·속도로 함께 fade-in 한다" 규칙을 builder_system.md에 제안 후보. ([bg-anchor-alignment]의 시간축 버전)

### [redundant-surface-label-text] 에셋/대사로 이미 표현된 정보를 텍스트 라벨·접두어로 중복

- 대상: content-harness-pipeline (builder_system.md / design_review_system.md), 예: runs/2026-07-08_ch802d08/output/index.html
- 분류 태그: redundant-surface-label-text
- 상태: 열림
- 발생 횟수: 4
- 최초 발생일: 2026-07-09
- 최근 발생일: 2026-08-03
- 사례:
  - 2026-07-09: 말풍선 위 `.who` 요약 라벨(`📢 도서관 고장 알림`, `🕑 깨진 전광판 안내`)이 바로 아래 대사와 같은 내용을 중복. 전광판 asset 위에 얹힌 문제 문구를 JS가 `전광판: … — 같은 시각의 시계는?`로 감싸, 이미 전광판 이미지로 표현된 맥락을 텍스트로 다시 명명함. 한 번의 피드백에 같은 성격의 사례 3건.
  - 2026-07-09: (재발/실적용) 사용자가 유형 A 화면의 `🕑 깨진 전광판 안내` 라벨과 `aPrompt`의 `전광판:` 접두어를 "AI가 자주 하는 의미 없는 설명"이라며 삭제 요청. 실제로 제거함.
  - 2026-08-03: `production/1-2/08` — "다음 챕터 버튼이 나올 때는 말풍선에 `다음`을 넣지 말기." 각 씬 아웃트로의 마지막 beat에서 챕터 이동 CTA(`#introNext`·`#shapeNext`·`#arithNext`)가 나타나는데도 말풍선 안의 진행 버튼(`ADVANCE_NAV_HTML` = `다음 ▸`)이 그대로 남아, **한 화면에 진행 표면이 둘**이 된다. 게다가 그 시점에는 대사 탭 레이어(`introTap`·`shapeDialogueTap`)가 이미 `hidden`이라 `다음 ▸`는 **눌러도 아무 일도 하지 않는 죽은 버튼**이다(index.html:823 / 903 outro 분기 / 956 outro 분기). 앞의 세 사례가 "텍스트 라벨 중복"이었다면 이건 "**진행 컨트롤 중복**"이다. (미조치 — `production/1-2/08/todo.md` 35번)
  - 2026-07-13: 이야기 오른쪽 지면 `.pt`의 `페이지 1 · 24시간` 등에서 `페이지 N ·` 접두어 삭제 요청. 페이지 번호는 이미 하단 `.book-dots` 인디케이터가 표현하므로 텍스트 접두어와 중복. 접두어 제거하고 주제어(`24시간`/`해시계`/`30분 타이머`)만 남김. → (후속) 남은 주제어 라벨도 큰 핵심 문구(`24시간 = 1일` 등 `.key-badge`)와 중복이라 `.pt` 라벨 자체를 렌더에서 제거.
- 조치: 유형 A(`#s-a`)에서 `.who`(🕑 깨진 전광판 안내) 라벨 제거, `aPrompt.innerHTML`에서 `전광판:` 접두어 제거. (검토 단계) builder에 중복 라벨/표면명 접두어 금지 제약 + design_review text_review에 "텍스트↔시각 중복" 판정 축 추가 제안은 사용자 승인 대기.
- 규칙화 메모: 최초 피드백 3사례 + 재발 1건(발생 횟수 2로 집계). 승격 임계값 5회 미도달. 도달 시 builder_system.md와 design_review_system.md 양쪽에 반영 제안.

### [asset-revision-refine-routing] asset 재생성 후 builder 재빌드 대신 refine으로 반영

- 대상: content-harness-pipeline/runner.py
- 분류 태그: asset-revision-refine-routing
- 상태: 열림
- 발생 횟수: 1
- 최초 발생일: 2026-07-08
- 최근 발생일: 2026-07-08
- 사례:
  - 2026-07-08: 사용자가 design_review가 asset 생성 또는 수정을 요구했을 때 builder를 다시 돌리면 기존 refine 결과를 잃을 수 있으므로, asset 변경 후에는 refine으로 이어져야 한다고 지적했다.
- 조치: asset revision 흐름이 asset generator 이후 `builder_only`가 아니라 기존 HTML을 기준으로 `design_refine`을 실행하도록 수정한다.
- 규칙화 메모: 아직 발생 1회로 rule 승격 대상이 아니다.

### [intro-title-raster-image] 인트로 타이틀을 게임형 이미지 타이틀로 교체

- 대상: content-harness-pipeline/runs/2026-07-08_2d08c0de/output/index.html, runs/2026-07-31_dfbc1027 (planner `asset_school_title_banner_body`)
- 분류 태그: intro-title-raster-image
- 상태: 열림
- 발생 횟수: 4
- 최초 발생일: 2026-07-08
- 최근 발생일: 2026-08-03
- 사례:
  - 2026-07-08: 사용자가 인트로의 `시간이 뒤죽박죽! / 수학의 힘으로 도서관 시계를 수리하라!` 문구를 예시처럼 이미지 생성 타이틀로 만들고, 1번 후보를 인트로에 삽입하길 요청했다.
  - 2026-07-08: 사용자가 삽입된 생성 이미지를 화면 가운데에 오게 하고, 주변 화면을 어둡게 만들어 아직 시작하기 전이라는 느낌을 주길 요청했다.
  - 2026-07-31: run dfbc1027 인트로 제목이 다시 빈 제목판(`school-title-banner-body.png`) + HTML `<h2>` 오버레이로 나갔다. 사용자가 "글자까지 title 이미지로 제작하기로 하지 않았나"라고 지적. planner가 하나의 제목판 몸체를 intro·arithmetic·story·completion 4개 씬에 공용으로 계획하면서 문구를 가변으로 취급해 `negative_prompt`에 텍스트 금지를 넣었고, planner_system.md:124-129의 "고정 문구 = 이미지에 굽는다(인트로·완료 타이틀 명시)" 조항을 우회했다.
  - 2026-08-03: `production/1-2/08`에서 "**각 섹션에 제목을 이미지로 붙여 달라 — 글과 이미지를 하나로 굽는 형식**"이라고 지적하며 `100까지의 수` 타이틀(두꺼운 크림 외곽선 + 노란 입체 글자)을 예시로 첨부했다. 대상 5종: `모양 찾기와 세기`·`세수의 덧셈과 뺄셈`·`무작위 계산 문제`·`모양으로 그리기`·`수리 이야기`. **07-31 지적 이후에도 production 사본이 여전히 빈 제목판(`school-title-banner-body.png`) + HTML `<h2>` 구조**이고, 그나마 씬3·6·7에만 있고 씬2·4·5에는 제목 표면 자체가 없다. 이번 건은 `production/1-2/08/CLAUDE.md`의 "텍스트가 필요한 이미지는 글자를 굽지 말고 빈 면 + HTML 텍스트" 규칙과 **정면으로 부딪히는데**, 07-31 사례에서 드러났듯 pipeline 쪽 planner_system.md는 반대로 "고정 문구는 굽는다"를 요구한다 — **두 문서가 서로 다른 방향을 지시하고 있는 것이 재발의 구조적 원인**이다. (**조치 완료 2026-08-03** — complete.md 51번: 제목 5종을 `codex exec` 이미지 생성으로 만들어 씬2~6에 `<img class="title-image">`로 붙였다. 빈 판 + HTML 텍스트 구조는 씬7만 남았다. **문서 충돌은 `production/1-2/08/CLAUDE.md`에 "제목·로고류는 예외" 조항을 넣어 정리했다** — 가르는 기준은 "텍스트냐"가 아니라 "변하느냐 고정이냐"로, pipeline planner_system.md와 같은 축이다. 예시 이미지는 `assets/reference/title-image-exemplar.png`로 보존.)
- 조치: 2026-07-08 건은 이미지 생성 후보 1번을 `output/assets/intro_title_time_repair_v1.png`로 삽입·중앙 정렬. 2026-07-31 건은 미조치(아래 규칙화 메모 참조).
- 규칙화 메모: **4회. 하나 더 나오면 승격 기준(5회)에 닿는다.** 승격안에는 pipeline `planner_system.md`("고정 문구는 굽는다")와 `production/1-2/08/CLAUDE.md`("글자를 굽지 말고 HTML 텍스트를 얹는다")의 **충돌을 먼저 정리**하는 항을 넣는다 — 어느 한쪽만 고치면 다른 경로로 재발한다. 갈라야 할 축은 "**고정 문구(제목·로고)는 굽고, 가변 문구(대사·문항·라벨)는 빈 면 + HTML**"로 보인다.
- 규칙화 메모(3회 시점): 3회. 규칙 문구 자체는 planner_system.md:122-134에 이미 있으나 "몸체 하나를 여러 씬에 재사용"이라는 경로로 우회되고 있다. 반복되면 planner_system.md에 "제목판은 씬마다 문구를 구운 개별 asset으로 계획하고, 몸체 공용화를 이유로 고정 제목을 오버레이로 내리지 않는다" 조항을 추가하는 안을 제안 후보로 둔다.

### [backdrop-filter-render-artifact] dim/blur 오버레이의 backdrop-filter가 검은 선·깜빡임 유발

- 대상: content-harness-pipeline/runs/2026-07-08_ch802d08/output/index.html (`#s-title::after`)
- 분류 태그: backdrop-filter-render-artifact
- 상태: 열림
- 발생 횟수: 1
- 최초 발생일: 2026-07-09
- 최근 발생일: 2026-07-09
- 사례:
  - 2026-07-09: 인트로 배경을 어둡게/흐릿하게 하려고 `#s-title::after`에 `backdrop-filter:blur(2.5px)`를 추가했더니, 타이틀 이미지 위에 특정 조건(합성 프레임)에서 검은색 선이 나타나고 dim 처리가 프레임마다 불안정하게(어두웠다 밝았다) 렌더됨. 헤드리스 스크린샷 두 컷에서 dim/blur 적용이 서로 달라 재현됨.
- 조치: `backdrop-filter`(및 `-webkit-` 접두어)를 제거하고 dim은 radial-gradient + rgba 오버레이만으로 처리. 흐림이 꼭 필요하면 backdrop-filter 대신 별도 블러 배경 레이어로 구현.
- 규칙화 메모: 아직 발생 1회. 반복되면 "오버레이 dim은 backdrop-filter 대신 gradient/rgba로" 규칙을 content-harness-pipeline/AGENTS.md에 제안 후보.

### [content-scale-too-small] 초등생용인데 이미지·글자가 너무 작음

- 대상: content-harness-pipeline (builder 산출물 전반), 예: runs/2026-07-08_ch802d08/output/index.html
- 분류 태그: content-scale-too-small
- 상태: 제안됨
- 발생 횟수: 13
- 최초 발생일: 2026-07-09
- 최근 발생일: 2026-08-03
- 사례:
  - 2026-07-09: 콘텐츠가 초등학생용인데 이미지와 글자가 너무 작다. 지금보다 훨씬 크게 요청. 화면은 full-viewport stage에 clamp(min,vw,max) 기반 스케일이라 큰 화면에서 max 천장에 걸려 작게 보임.
    - 조치: clamp() 상단(vw 계수·max)을 ~1.28배로 올려 큰 화면에서 확대(작은 화면 min은 유지). 표면 박스와 그 안 텍스트를 같은 배율로 키워 art 안에 글자가 유지되도록 함. 튜토리얼 씬 오버플로는 티켓 tray를 한 줄(`flex-wrap:nowrap`)로 고정해 해결.
  - 2026-07-09: 전역 확대 후에도 캐릭터가 작다고 판단, 캐릭터(`.char`)만 현재 크기에서 추가 1.3배 요청.
    - 조치: `.char` height 3개 규칙(기본/`#s-problem`/모바일)의 vh 계수·max를 ×1.3, min 유지. 대사·티켓·작업대와 겹침 없음 확인.
  - 2026-07-09: 튜토리얼 씬의 설명글·질문·힌트 텍스트가 전체적으로 작음(초등 대상). `.wb-note`(clamp .6~1.05rem), `.wb-slot .qhint`(clamp .72~1.254rem) 등이 낮은 max 천장에 걸림.
    - 조치: 튜토리얼 스코프에서 질문/힌트/카드 글자 clamp를 상향(질문 max 1.254→1.72rem 등).
  - 2026-07-09: 튜토리얼 가운데 테이블(작업대)과 탁상시계가 전체적으로 작다며 키워달라고 요청. (같은 대상 반복 요청 — 한 번 키운 뒤에도 더 키워달라 함)
    - 조치: `#s-tut .workbench` 폭 780→860→**1118px(≈1.3배 추가)**, `.wb-clock` 24%→27%(판 확대로 시계도 비례 확대). 넓어진 보드가 우측 말풍선을 가리지 않도록 `.wb-slot`을 안쪽(right:11%, width:40%)으로 이동. 위로 올려달라는 요청에 `center-col` top 61%→54%. (같은 대상 반복 튜닝이라 발생 횟수는 증분하지 않고 이 사례에 통합.)
  - 2026-07-09: CTA 버튼 폰트가 너무 작음 — 인트로 `#btnStart`("시작하기"), 문제 씬 `#btnToTutorial`("시계의 힘으로 수리하러 가기"). 티켓 asset 위 텍스트가 asset 대비 작게 보임(`.ticket-btn` font clamp max 1.485~1.613rem).
    - 조치: `#btnStart` font clamp max 1.613→2.05rem, `#btnToTutorial` 1.485→1.74rem으로 상향(nowrap/keep-all 유지).
  - 2026-07-09: 유형 B(코르크 시간표 보드)의 미니 시계가 작아서 안 보임. `loadB`의 `miniclock` size가 데스크톱 78/모바일 62로 낮음. (같은 대상 반복 튜닝: 120→150으로 한 번 더 확대 요청)
    - 조치: `loadB`에서 clock size를 데스크톱 78→120→150→**175**/모바일 62→92→112→**130**로 확대, 빈 시계 placeholder도 동일 size로 맞춤. 확인 버튼을 보드 밖으로 빼 세로 여백 확보. `bContent`를 `justify-content:space-between`으로 바꿔 제목을 위, "걸린 시간=" 식을 아래로 벌리고 시계를 가운데에 크게 배치(영역은 top:12%/height:76% → 위·아래 2%씩 안쪽으로 top:14%/height:72% 조정). 시계 아래 라벨(시작/끝, `.qhint` .72rem/ink-soft)이 흐려 잘 안 보이던 것을 clamp(.86~1.15rem)·`font-weight:800`·`color:#4a2b0e`로 키우고 진하게. (발생 횟수는 같은 대상 반복이라 증분하지 않고 통합)
  - 2026-07-10: 유형 A(시계 고르기) 보기 시계가 작아 보임. `loadA` 클록 모드 보기 size가 데스크톱 146/모바일 108로 낮음. 보기는 3개뿐이라 확대 여유 있음.
    - 조치: `loadA` 보기 clock size를 데스크톱 146→**200**/모바일 108→**150**으로 확대(약 1.37x). 3개가 ≥768px에서 한 줄에 들어가고(row3≈703 ≤ col900) 좁은 화면은 flex-wrap로 줄바꿈 확인.
  - 2026-07-10: 유형 A text 모드 티켓 보기(`.choice.choice-text`)도 작음. width clamp(165,27vw,250)/font clamp(.88,2.5,1.3rem).
    - 조치: width→clamp(210px,29vw,300px), font→clamp(1.05rem,3vw,1.7rem)로 확대. 3개 한 줄 유지 위해 `#s-a .center-col` 폭을 min(1100px,96vw)로 넓힘(≥768px 한 줄, 계산 검증).
  - 2026-07-10: 유형 A text 모드 전광판이 넓은데(aspect 1790/920) 시계·질문을 세로로 쌓아 작고 폭을 낭비함. 사용자가 "시계 왼쪽·글 오른쪽 가로 배치 + 시계/글자 더 크게, 단 전광판(크림) 벗어나지 말 것" 요청.
    - 조치: text 모드 `aPrompt`에 `.prompt-row` 클래스 부여 → `display:flex;row;align-items:center`로 시계 좌·질문 우 가로 배치(clock-mode는 `notice`로 세로 복귀). 시계 size를 뷰포트 상수(min 190)에서 **전광판 폭 비례(`plaqueW*0.30`, ~252@840)** 로 바꿔 크림 안에서 확대. 질문 font clamp(.8,2.4,1.2rem)→clamp(1.05rem,3vw,1.66rem), `max-width:48%`+keep-all로 우측에서 한 줄. plaque padding(9/5/12%) 기준 콘텐츠 영역 안에 들어감을 합성으로 검증(FIT).
  - 2026-07-10: 튜토리얼 질문 "지금 멈춰있는 이 시계는 몇 시일까?"(`#s-tut .wb-slot .qhint`)를 조금 위로 + 더 크게 요청. → 1.9rem으로 키웠더니 2줄이 됨 → 다시 "1줄로 해줘".
    - 조치: font를 1.9rem으로 키웠다가, 2줄 방지 위해 `white-space:nowrap`+한 줄에 들어가는 최대치 clamp(1.05rem,3.2vw,1.7rem)로 재조정. 슬롯 폭 40%→46%(작업대 시계 오른쪽 공간 활용)로 넓혀 데스크톱(≥1280)에서 슬롯 안 1줄. 질문만 위로: 드롭 슬롯(`#tutBlank`)은 두고 `position:relative;top:-.55rem`. 교훈: 텍스트를 키울 때 컨테이너 폭 대비 줄바꿈을 함께 확인(키움과 nowrap/폭 확보는 세트).
  - 2026-07-10: 유형 C 모니터 안 시간대 막대(`.timeline-bar` 이미지)와 라벨("오전 1~12시 · 오후 1~12시", `.timeline-labels`)이 작아 조금씩 키워달라고 요청.
    - 조치: `.timeline-bar` 폭 min(100%,430px)→490px·height clamp(52,8.2vw,72)→clamp(60,9.4vw,82)로 확대, `.timeline-labels` font clamp(.5,1.6vw,.8rem)→clamp(.58,1.9vw,.94rem)로 상향(`.tl-sep`은 1.15em 상대라 자동 확대). 모니터 유리(mon-screen) 안에 유지되도록 "약간" 수준으로만 키움.
  - 2026-07-31: `production/1-2/08/index.html`에서 "대사의 크기와 글자 크기를 전반적으로 키워야 한다"고 지적. 08은 파이프라인 산출물을 손으로 다듬은 차시본인데, 1920×1080 고정 stage로 옮긴 뒤에도 `--fs-*` 토큰 사다리가 파이프라인 기본값 그대로라 대사(`.speech`)와 본문이 초등 저학년 기준으로 작다. (미조치 — `production/1-2/08/todo.md` 16번으로 등록)
  - 2026-08-03: `production/1-2/08` `section_math_story`의 표지판 설명(`.story-card`) 글자 크기를 "더 키우면 좋겠다"고 지적. 16번에서 사다리 전체를 ×1.2 올렸지만 `.story-card`는 본문 기본인 `--fs-sm`(37px)에 머물러 있고, 카드가 1300×600으로 큰 탓에 상대적으로 더 작아 보인다. **글자를 키우면 안 그래도 잘리는 텍스트(위 bg-anchor-alignment 사례)가 더 넘치므로 카드 높이·표지판 행 좌표와 함께 봐야 한다.** (**조치 완료 2026-08-03** — complete.md 33번: 패딩을 에셋 크림 면 비율 `101px 64px 153px`로 다시 잡고 `align-content:center` 추가. 가로 패딩을 줄여 글 폭이 1084→1172가 되면서 `--fs-md`로 올려도 가장 긴 beat가 334px로 크림 면 346px 안에 들어간다. **카드 크기·`.sign-row`·에셋은 그대로**.)
- 규칙화 메모: **발생 13회 → rule 승격 제안.** 초안: "초등(저학년) 대상 콘텐츠는 본문/질문/힌트/**버튼(CTA)** 글자 clamp의 max와 vw 계수를 성인 기준보다 크게 잡는다(예: 본문 max ≥ 1.6rem, 주요 CTA max ≥ 1.8rem). 표면 박스/티켓 asset 위 텍스트도 동일 배율." 반영 위치: content-harness-pipeline/builder_system.md. 사용자 승인 대기.

### [label-text-wrapping] 짧은 라벨(숫자+한글 토큰)이 좁은 표면에서 글자 단위로 줄바꿈됨

- 대상: content-harness-pipeline/runs/2026-07-08_ch802d08/output/index.html (`.card`, 튜토리얼 드래그 카드)
- 분류 태그: label-text-wrapping
- 상태: 열림
- 발생 횟수: 3
- 최초 발생일: 2026-07-09
- 최근 발생일: 2026-07-10
- 사례:
  - 2026-07-09: 튜토리얼 씬의 드래그 카드가 "3시"인데 좁은 카드 폭에서 "3 / 시"로 두 줄로 쪼개져 보임. `.card`에 `white-space`/`word-break` 지정이 없어 브라우저 기본값이 숫자(3)와 한글(시) 경계에서 줄바꿈을 허용함.
    - 조치: `.card`에 `white-space:nowrap`을 추가해 짧은 토큰이 한 줄로 유지되도록 함(!important 미사용).
  - 2026-07-09: 유형 C 모니터 화면의 질문/식이 한글 음절 단위로 줄바꿈됨("내일 오/후", "지나/면?"). `#s-c .mon-q`/`.eq-line`에 word-break 지정이 없어 좁은 화면 유리에서 단어 중간이 깨져 어색함.
    - 조치: `#s-c .mon-screen .mon-q`/`.eq-line`에 `word-break:keep-all` 추가(단어 경계에서만 줄바꿈). 모니터도 10%(640→704px) 확대해 줄바꿈 자체를 줄임.
  - 2026-07-10: 유형 C 두 번째 문제 식 `하루 = 오전 ㅁㅁ 시간 + 오후 ㅁㅁ 시간`이 `.eq-line`(flex-wrap)에서 "오후" 그룹 중간이 임의로 쪼개져 `… + 오후 [1]` / `[?] 시간`처럼 줄바꿈됨. 사용자가 "오후 ㅁㅁ 시간"을 한 덩어리로 다음 줄에 넣으라고 요청.
    - 조치: 템플릿에 의도적 줄바꿈 토큰 `[br]`을 도입(`loadC` 파싱에서 `flex-basis:100%`인 `.eq-br` span으로 치환 → flex 강제 개행)하고, 해당 문제 tpl을 `하루 = 오전 [b:1][b:2] 시간 +[br]오후 [b:1][b:2] 시간`으로 수정. 오후 그룹이 통째로 둘째 줄로 감.
- 규칙화 메모: 2회 이상. 반복되면 "짧은 라벨/버튼 토큰은 글자 단위 줄바꿈 방지(white-space:nowrap 또는 word-break:keep-all)하고, 여러 항으로 된 식은 항(그룹) 중간에서 쪼개지지 않게 명시적 줄바꿈 토큰/nowrap 그룹으로 항 단위 개행" 규칙을 builder_system.md에 제안 후보.

### [fixed-pos-transformed-ancestor] position:fixed 드래그가 transform 조상 때문에 잡는 순간 우측 하단으로 점프

- 대상: content-harness-pipeline/runs/2026-07-08_ch802d08/output/index.html (`enableDrag`, `.card`/`.num-block`, 조상 `.center-col`)
- 분류 태그: fixed-pos-transformed-ancestor
- 상태: 열림
- 발생 횟수: 1
- 최초 발생일: 2026-07-09
- 최근 발생일: 2026-07-09
- 사례:
  - 2026-07-09: 튜토리얼("지금 멈춰있는 이 시계는 몇 시일까?")에서 3시/4시/5시 카드를 잡으면 마우스 포인터를 따라오지 않고 우측 하단으로 일정하게 튀고, 나머지 카드가 작아진다고 지적. `enableDrag`가 드래그 시 `el.style.position='fixed'`로 바꾸고 `left=origRect.left`(getBoundingClientRect=뷰포트 좌표)를 넣는데, 카드의 조상 `.center-col`에 `transform:translate(-50%,-50%)`가 있어 position:fixed의 컨테이닝 블록이 뷰포트가 아니라 그 조상이 됨. 그래서 뷰포트 좌표를 그대로 넣으면 조상의 뷰포트 offset만큼(측정값 +342,+228) 우측 하단으로 점프. Playwright 헤드리스로 pointerdown 즉시 카드 중심 (519,708)→(861,936) 점프 재현 확인. "카드 작아짐"은 카드를 position:fixed+margin:0로 flex 흐름에서 빼면서 tray가 재배치된 부수효과.
- 조치: `enableDrag`를 position:fixed+left/top 방식에서 **`transform:translate(dx,dy)` 델타 이동** 방식으로 교체(요소를 흐름에 유지, 컨테이닝 블록과 무관하게 포인터 델타만큼 이동). 드래그 중 `transition:none`으로 지연 제거. CSS/`!important` 미사용. 드롭 판정(`hitBlank`, clientX/Y 기반)은 그대로.
- 규칙화 메모: 아직 1회. 반복되면 "드래그로 요소를 움직일 때 position:fixed+뷰포트좌표 대신 transform:translate 델타를 쓴다(transform 조상 컨테이닝블록 문제 회피)" 규칙을 builder_system.md에 제안 후보.

### [weak-drag-affordance] 드래그 상호작용의 유도가 약함(정적 힌트만)

- 대상: content-harness-pipeline/runs/2026-07-08_ch802d08/output/index.html (`#s-tut` 튜토리얼 카드/슬롯)
- 분류 태그: weak-drag-affordance
- 상태: 열림
- 발생 횟수: 1
- 최초 발생일: 2026-07-09
- 최근 발생일: 2026-07-09
- 사례:
  - 2026-07-09: "아래 시간 티켓을 여기로 드래그!" 정적 텍스트만으로는 행동 유도가 약함. 카드 아래에 반짝이는 큐, 카드 자체의 grab 유도(글로우), 그리고 카드를 잡고 있는 동안 놓을 슬롯을 강하게 하이라이트하는 피드백이 필요.
- 조치: 빈 슬롯 pulse 애니메이션(`slotPulse`) + 카드 grab 유도 글로우(`cardInvite`) + tray 아래 sparkle 큐(`.tut-drag-cue`, `cueBounce`) 추가. `enableDrag`에 잡는 순간 대상 blank에 `.armed`(강조) 부여/해제 로직 추가(전 미션 공통 이점).
- 규칙화 메모: 아직 1회. 반복되면 "드래그 학습 상호작용은 (a)소스 grab 유도, (b)잡는 동안 타깃 하이라이트, (c)타깃 상시 pulse 큐를 기본 제공" 규칙을 builder_system.md에 제안 후보.

### [drag-drop-snap-fit] 드롭 시 카드가 슬롯에 물려야 하는데 텍스트만 기록되고 카드/슬롯 크기 불일치

- 대상: content-harness-pipeline/runs/2026-07-08_ch802d08/output/index.html (`#s-tut #tutBlank`, `.card`)
- 분류 태그: drag-drop-snap-fit
- 상태: 열림
- 발생 횟수: 2
- 최초 발생일: 2026-07-09
- 최근 발생일: 2026-07-10
- 사례:
  - 2026-07-09: 정답 카드를 드롭하면 작은 `.blank`(82x66)에 "3시" 텍스트만 써지고 실제 카드는 tray에 opacity로 남아, 카드가 슬롯에 물려 들어가는 물리적 UX가 아님. 슬롯을 카드 크기에 맞추고, 카드가 그대로 슬롯에 스냅되어야 함.
    - 조치: `#tutBlank`을 티켓 카드 크기(aspect 1417/1140)로 확대. 정답 onDrop에서 텍스트 기록 대신 실제 카드 엘리먼트를 슬롯에 `appendChild`하여 스냅(`.placed`), 슬롯은 `.filled`로 카드 프레이밍.
  - 2026-07-10: 튜토리얼에서 정답을 맞히면 카드 크기가 변해 보임. 원인: 슬롯(`#tutBlank` `clamp(142px,24.5vw,206px)`)을 카드(`clamp(134px,23vw,196px)`)보다 크게 "프레임"으로 잡아서, 196 카드가 206 슬롯 안에 스냅되며 더 작아 보임.
    - 조치: 슬롯 폭을 카드와 동일한 `clamp(134px,23vw,196px)`로 맞춤 → 빈 슬롯·트레이 카드·스냅된 카드가 모두 같은 폭이라 크기 변화 없음.
- 규칙화 메모: 2회. 교훈: "드롭 타깃은 소스와 **정확히 동일 크기**로(프레임 여백을 주지 말 것), 드롭 성공 시 소스를 타깃에 물리적으로 스냅(텍스트 대체 금지)" 규칙을 builder_system.md에 제안 후보.

### [clock-hand-overflow] 아날로그 시계 바늘 길이가 문자판을 벗어남

- 대상: content-harness-pipeline/runs/2026-07-08_ch802d08/output/index.html (`.clock .hand.minute/.hour`, `#tutClock`)
- 분류 태그: clock-hand-overflow
- 상태: 열림
- 발생 횟수: 2
- 최초 발생일: 2026-07-09
- 최근 발생일: 2026-07-10
- 사례:
  - 2026-07-09: 시계 분침(`height:37%`)/시침(`height:26%`)이 너무 길어 문자판(숫자 12 근처)을 뚫고 삐져나옴.
  - 2026-07-10: 튜토리얼 씬 탁상시계(`#tutClock`)만 분침이 문자판을 벗어남. 원인: `table_clock_body.png`는 하단에 받침대가 있어 문자판이 벽시계(`wall_clock_body.png`)보다 작고 위쪽(`--cy:45%`)에 있는데, 바늘 길이는 벽시계 기준 전역값(분침 30%·시침 21%)을 그대로 써서, 3시(분침 12시 방향)일 때 분침 끝이 숫자 링을 지나 나무 테두리까지 뚫고 나감.
    - 조치: `#tutClock` 스코프로 바늘 길이만 축소(분침 30%→23%, 시침 21%→16%). 벽시계 기반 다른 시계(`#bigClock`, `buildClock`의 퀴즈/선택 시계)는 `--cy:50%`·꽉 찬 문자판이라 전역값 유지.
- 조치: (2026-07-09) `.hand.minute` 37%→30%, `.hand.hour` 26%→21%로 전역 축소. (2026-07-10) 받침대로 문자판이 작은 탁상시계는 `#tutClock` 스코프로 분침 23%·시침 16%로 재조정.
- 규칙화 메모: 2회. 반복되면 "div로 그린 시계 바늘 길이는 문자판 반지름(숫자 링) 안쪽으로 제한하되, 시계 몸체 asset마다 문자판 반지름(=중심 `--cy`와 dial 크기)이 다르므로 **asset별로 바늘 길이를 보정**한다(전역 한 값으로 통일하지 말 것)" 규칙을 builder_system.md에 제안 후보.

### [card-aspect-stretch] flex 트레이의 align-items:stretch가 카드 aspect-ratio를 덮어 세로로 늘림

- 대상: content-harness-pipeline/runs/2026-07-08_ch802d08/output/index.html (`#s-tut .card-tray`, `.card`)
- 분류 태그: card-aspect-stretch
- 상태: 열림
- 발생 횟수: 1
- 최초 발생일: 2026-07-09
- 최근 발생일: 2026-07-09
- 사례:
  - 2026-07-09: 3시/4시/5시 티켓 카드가 위아래로 늘어나 보임(세로로 큼). 1차 원인은 부모 `.card-tray`(display:flex)의 기본 `align-items:stretch`가 카드 `aspect-ratio`를 덮어써 세로로 늘림.
  - 2026-07-09: (명확화) 요구의 핵심은 "카드 세로 높이를 줄여라"였음. stretch를 꺼 티켓 원본 비율(1417/1140)로 되돌렸어도 여전히 세로가 있었음 → 원본보다 더 납작하게 만들어야 함.
- 조치: `#s-tut .card-tray{align-items:center;}` + `#s-tut .card{flex:0 0 auto;height:auto}`로 stretch 제거. 그 위에 `aspect-ratio`를 원본(1417/1140)보다 납작한 **1417/820**으로 설정해 가로 유지·세로 축소. 드롭 슬롯(`#tutBlank`)도 동일 비율로 맞춰 스냅 시 일치. 카드가 납작해진 만큼 상하 padding도 축소(14%/15%→9%/10%).
- 규칙화 메모: 아직 1회. 반복되면 "aspect-ratio를 쓰는 카드/타일을 flex 컨테이너에 넣을 때는 `align-items:stretch`(기본)를 끄고(center 등) `flex:0 0 auto`로 비율을 보존" 규칙을 builder_system.md에 제안 후보.

### [flex-child-wider-than-container-misalign] flex 자식이 컨테이너보다 넓으면 auto마진이 flex-start로 정렬돼 한쪽으로 쏠림

- 대상: content-harness-pipeline/runs/2026-07-08_ch802d08/output/index.html (`#s-tut .center-col` / `.workbench`)
- 분류 태그: flex-child-wider-than-container-misalign
- 상태: 열림
- 발생 횟수: 2
- 최초 발생일: 2026-07-09
- 최근 발생일: 2026-07-09
- 사례:
  - 2026-07-09: 튜토리얼 판(작업대)을 1118px로 키웠더니 화면 중앙이 아니라 오른쪽으로 치우침. `.center-col`(flex column, `width:min(900px,94vw)`=900px)보다 `.workbench`(1118px)가 넓은데, workbench의 `margin:0 auto`가 교차축 여백이 음수가 되며 auto→0으로 처리되어 align-items:center가 무시되고 flex-start(왼쪽)로 붙어 오른쪽으로 오버플로.
    - 조치: `#s-tut .center-col{width:min(1180px,96vw)}`로 컨테이너를 판보다 넓게 잡아 중앙 정렬 복구.
  - 2026-07-09: (재발) 이야기(s-story) 책을 1120px로 키웠더니 가운데 정렬이 깨져 한쪽으로 쏠림. `.book-stage`(1120px)가 `.center-col`(min(900px,94vw)=900px)보다 넓어 동일 증상.
    - 조치: `#s-story .center-col{width:min(1160px,98vw)}`로 컨테이너를 책보다 넓게 잡아 중앙 정렬 복구.
- 규칙화 메모: 2회. 반복되면 "flex 컨테이너 안의 요소(작업대/책/모니터 등 asset 스테이지)를 키울 때 컨테이너 폭을 자식보다 크게 유지 — 자식이 컨테이너보다 넓으면 `margin:0 auto`+align-items:center가 무너져 한쪽으로 쏠린다" 규칙을 builder_system.md에 제안 후보.

### [low-contrast-cue] 유도 문구가 배경색과 대비 부족으로 잘 안 보임

- 대상: content-harness-pipeline/runs/2026-07-08_ch802d08/output/index.html (`#s-tut .tut-drag-cue`)
- 분류 태그: low-contrast-cue
- 상태: 열림
- 발생 횟수: 4
- 최초 발생일: 2026-07-09
- 최근 발생일: 2026-08-11
- 사례:
  - 2026-07-09: 유형 B 보드의 문제 제목(`독서 교실이 8시에 시작해 9시에 끝났어요…`)이 코르크 배경 위에서 진갈색(`color:#5a3b1b`)이라 잘 안 보임. 다른 색으로 요청.
    - 조치: 제목을 크림색 라벨 칩(`#s-b .b-qtitle`, `background:rgba(255,248,232,.94)` + 진한 적갈색 글자 `#7a1f10`)으로 감싸 코르크 배경과 무관하게 고대비 확보.
  - 2026-07-09: "✨ 카드를 끌어서 놓아요 ✨" 큐가 갈색 계열(`color:#b5791b`)이라 나무 바닥/러그 배경 위에서 잘 안 보임. 더 하이라이트 필요.
    - 조치: 큐를 어두운 알약 배경(갈색 그라디언트)+금색 글자(`#ffe89a`)+내부 금테/글로우 box-shadow로 변경하고 bounce에 글로우 맥동 추가. 배경과 무관하게 대비 확보.
  - 2026-07-09: (후속) 큐가 실제 화면에서 아예 안 보인다고 지적. 원인은 대비가 아니라 **CSS 애니메이션 override로 인한 opacity 미해제**: 큐 엘리먼트에 `enter d3`가 있어 `.scene .enter{opacity:0}`로 시작하는데, opacity를 1로 올리는 `enterUp` 애니메이션이 내가 큐에 준 `cueBounce`(명시도 `#s-tut ...`가 더 높음)에 덮여 실행되지 않음 → opacity 0 고정. (검증 스크린샷은 opacity를 강제로 켜서 버그가 가려져 있었음.)
    - 조치: `#s-tut .tut-drag-cue`에 `opacity:1` 명시. opacity 강제 없이(실제 CSS만) virtual-time 렌더로 큐 표시 확인.
  - 2026-08-04: **(상태 규칙이 변형의 색 계약을 덮음)** `production/1-2/08` `section_random_problems` 키패드에서 "**확인 버튼에 호버하면 흰색으로 바뀌어 글자가 안 보인다**"고 지적. `.key.enter`는 `color:#fff` on `background:#e23b3b`(빨강)인데, `#randomInput .key:hover{background:var(--veil)}`(= `rgba(255,255,255,.92)`)가 **id 명시도로 그 위를 덮어** 흰 판 위 흰 글자가 됐다. 앞 두 사례가 **정적인 색 선택**의 대비 문제였다면 이번은 **상태(:hover) 규칙이 변형(.key.enter)의 색 계약을 모른 채 배경만 갈아 끼운 것**이라 층위가 다르다 — 평상시에는 멀쩡하고 호버에서만 사라진다. 씬2·3 키패드에는 이 규칙이 없어 **씬4에서만** 났다. (**조치 완료 2026-08-04** — `production/1-2/08/complete.md` 77번: 호버 배경 교체를 빼고 들림만 남겼다.)
  - 2026-08-11: **(표면을 안 쓰고 배경 위에 직접 얹음)** `tmp/runs-fresh/2026-08-11_dfbc1027` 완료 화면의 `3차시 수리 완료!`가 `.heroTitle{color:#fff}` + text-shadow로 **밝은 하늘·크림 담장 위에 그대로** 얹혀 거의 안 읽힌다. 앞 사례들이 색 선택이나 상태 규칙 문제였다면 이번은 **쓸 수 있는 표면 asset이 있는데 안 쓴 것**이다 — `school-title-banner-body.png`가 준비돼 있고 `.banner-school` 규칙까지 만들어 놓고 완료 제목에는 붙이지 않았다. 대비를 색으로 풀려다 실패한 게 아니라, 텍스트를 얹을 표면을 아예 고르지 않은 결과다. (builder 1회 산출물이며 design_refine 미실행 상태에서 관찰)
- 규칙화 메모: 4회(가독 1 + 상태 대비 1 + 가시성 버그 1 + 표면 미선택 1). 반복되면 (a) "유도 큐/힌트는 고대비 칩으로", (b) "`.enter`(entrance opacity:0)를 가진 엘리먼트에 별도 `animation`을 주면 `enterUp` 리빌이 덮여 안 보일 수 있으니 opacity를 명시하거나 `.enter`를 빼거나 애니메이션을 합성" 규칙을 builder_system.md에 제안 후보. (c) **상태 규칙(`:hover`/`:focus`)은 색 계약이 다른 변형이 그 선택자에 걸리는지 먼저 확인한다** — 공통 hover가 배경만 갈아 끼우면 반전 배색 변형(흰 글자 버튼)에서 글자가 사라진다. 배경을 바꿔야 하면 글자색도 함께 바꾸거나, 변형을 뺀 선택자로 좁힌다.

### [ambient-effect-hover-only] 상시로 요구된 이펙트(글로우)를 호버 상태에만 구현

- 대상: content-harness-pipeline/runs/2026-07-08_ch802d08/output/index.html (`#btnStart`, `#btnToTutorial`, `.ticket-btn`)
- 분류 태그: ambient-effect-hover-only
- 상태: 열림
- 발생 횟수: 1
- 최초 발생일: 2026-07-09
- 최근 발생일: 2026-07-09
- 사례:
  - 2026-07-09: CTA 버튼에 글로우가 필요하다고 했는데 `.ticket-btn`의 글로우/샤인이 `:hover`(및 `::before` 샤인 hover)에만 있어 평상시엔 글로우가 없음. 상시 글로우 필요.
    - 조치(1차): `z-index:-1` 헤일로 `::after` 레이어(금색 radial+blur)를 상시 맥동으로 추가.
  - 2026-07-09: (후속) 1차 글로우가 "너무 이상하다/부자연스럽다"고 지적. 원인은 `::after` radial 블롭이 **버튼(티켓) 실루엣을 안 따르고** 사각/타원 형태로 버튼 뒤·아래에 떠 보였기 때문.
    - 조치(2차): `::after` 블롭 제거. 대신 버튼에 **`filter:drop-shadow` 다중 레이어**를 적용 — drop-shadow는 티켓 PNG의 alpha(실루엣)를 따라 halo를 그려 자연스러움. filter는 등장(enterUp)/펄스(theartbeat)가 안 건드리는 속성이라 상시 유지됨(btnStart는 `.enter`가 `.blink`를 덮어 tblink가 애초에 실행 안 됨도 확인). hover엔 조금 더 강한 glow.
  - 2026-07-09: (후속) "조금 움직이는 효과를 줘" — 정적 글로우에 은은한 모션 요청.
    - 조치(3차): `ctaFloat` 애니메이션(transform translateY/scale + filter glow 맥동) 추가로 부드럽게 떠오르며 글로우가 숨쉬는 모션. **주의:** 처음엔 `animation:enterUp(opacity 0→1)+ctaFloat`로 합쳤더니 버튼이 아예 사라짐(opacity 애니메이션 조합 문제) → **opacity는 정적 1로 두고 ctaFloat은 transform/filter만** 애니메이션하도록 수정(등장 슬라이드는 포기, 가시성·모션 확보). `#btnToTutorial`은 `.dlg-cta.on`의 opacity:1 정적값 유지 + ctaFloat.
- 규칙화 메모: 아직 1회(+ 후속 자연스러움 교정). 반복되면 "(a) 글로우 등 분위기 이펙트는 `:hover`가 아니라 상시로. (b) **alpha 실루엣 asset(티켓/캐릭터 등) 위 글로우는 `::after` 사각/radial 블롭이 아니라 `filter:drop-shadow`로 실루엣을 따라 그린다.**" 규칙을 builder_system.md에 제안 후보.

### [spec-fx-color-mismatch] 스펙이 지정한 오답 강조 색/연출을 임의 색으로 바꿔 구현

- 대상: content-harness-pipeline/runs/2026-07-08_ch802d08/output/index.html (`#s-a` `.choice.correct-reveal`, `#s-b` 오답 로직)
- 분류 태그: spec-fx-color-mismatch
- 상태: 열림
- 발생 횟수: 2
- 최초 발생일: 2026-07-09
- 최근 발생일: 2026-07-10
- 사례:
  - 2026-07-09: 스펙(활동 2 Scene 1)은 "3회 오답 시 정답 시계가 붉은색으로 깜박인 후 강제 전환"인데, 유형 A 구현이 의도적으로 금색(`goldReveal`, 주석 "gold reveal, not red")으로 바꿔 스펙과 어긋남. 유형 B는 3회 오답 강제 전환/붉은 깜박 자체가 없었음.
    - 조치: 유형 A 3회 오답 리빌을 금색 → `wrong-reveal`(붉은 깜박, `redReveal`)로 변경. 유형 B에 `bWrong` 카운터 + 3회 오답 시 정답 리빌(붉은 깜박 `.kb-blank.reveal`) 후 강제 전환 추가(유형 A와 동일 로직).
  - 2026-07-10: 튜토리얼(#s-tut) 오답 시 (a)꼬마 사서가 슬퍼하지 않고(캐릭터 표정 미변경) (b)빈칸 카드 피드백(흔들림/빨강)도 안 나옴. 원인: `.blank.bad`(흔들림+빨강)이 있지만 더 높은 명시도의 `#s-tut #tutBlank:not(.filled)`(slotPulse 애니메이션 + border-color:wood-deep)이 덮어 shake/빨강이 죽음. 캐릭터는 유형 A와 달리 오답 시 `kid_librarian_confused` 교체 로직이 없었음.
    - 조치: `#s-tut #tutBlank.bad` 규칙(shake .4s + 빨강 border/box-shadow + 연분홍 배경)을 slotPulse 뒤에 배치해 명시도·소스순서로 이기게 함. 튜토리얼 꼬마 사서에 `id="tutKid"` 부여 후 오답 시 `kid_librarian_confused.png`(+tilt)→1.3초 뒤 explaining 복귀, 정답 시 `kid_librarian_success.png`(+cheer) 반응 추가.
- 규칙화 메모: 2회. 교훈: 스펙 오답 연출을 임의 색으로 바꾸지 말 것 + **정답/오답 피드백은 씬마다 일관되게(카드 흔들림·빨강 + 캐릭터 표정 변화)**. 또 **더 높은 명시도의 scoped 규칙(`#s-x #id:not(...)`)이 범용 `.bad` 상태 피드백을 조용히 덮을 수 있으니, 상태 피드백은 동일 명시도+소스순서 뒤 또는 더 높은 명시도로 보장**한다. builder_system.md에 제안 후보.

### [spec-mixed-answer-format-flattening] 스펙의 문제별 혼합 정답 형식을 유형별 단일 형식으로 획일화

- 대상: content-harness-pipeline/runs/2026-07-08_ch802d08/output/index.html (`#s-a` `A_DATA`, `loadA`/`pickA`)
- 분류 태그: spec-mixed-answer-format-flattening
- 상태: 열림
- 발생 횟수: 1
- 최초 발생일: 2026-07-09
- 최근 발생일: 2026-07-09
- 사례:
  - 2026-07-09: 원본 스펙(`_no_img.md` 활동 2)은 유형 A 안에서도 문제 1·3은 "몇 분 전 텍스트 → 시계 고르기", 문제 2·4는 "시계 제시 → 문자열 보기 고르기"로 혼합 형식이었는데, 빌드는 4문제 모두 시계 고르기로 획일화했음. (초기엔 사용자도 단일 형식으로 가자고 했다가) 사용자가 2·4번을 스펙대로 "전광판에 시계 + 문자열 보기 카드"로 되돌리도록 요청.
- 조치: `A_DATA`에 `mode`('clock'|'text') 도입. 2·4번을 `mode:'text'`(`clock:[h,m]` 제시 + 문자열 `choices`/`answer`)로 변경. `loadA`가 mode별로 렌더(text 모드: 전광판 plaque에 `buildClock` + '이 시계와 같은 시각은?' + 문자열 보기는 넓은 티켓 카드 `.choice.choice-text`). `aIsCorrect(ch,q)`로 정오답 판정 통합, 3회 오답 리빌도 mode 무관 동작.
- 규칙화 메모: 아직 1회. 반복되면 "스토리보드가 문제별로 정답 형식(객관식 시계/문자열/키패드/드래그)을 다르게 지정하면 유형 단위로 획일화하지 말고 문제 단위 형식을 보존" 규칙을 builder_system.md에 제안 후보.

### [action-control-on-art-surface] 조작 버튼(확인/제출)이 아트 표면 안에 박혀 있어 밖으로 빼야 함

- 대상: content-harness-pipeline/runs/2026-07-08_ch802d08/output/index.html (`#s-b #bSubmit`)
- 분류 태그: action-control-on-art-surface
- 상태: 열림
- 발생 횟수: 1
- 최초 발생일: 2026-07-09
- 최근 발생일: 2026-07-09
- 사례:
  - 2026-07-09: 유형 B의 "확인하기" 버튼이 코르크 보드(`bContent`) 안에 status-tag 이미지 표면으로 박혀 있어 답답함. 보드 아래로 빼달라고 요청.
- 조치: `bSubmit`을 `bContent`의 innerHTML(동적 생성)에서 분리해 `.center-col` 안 보드-스테이지 아래 정적 버튼(`.btn`)으로 이동. per-load로 붙던 click 리스너를 1회 바인딩으로 변경. `#s-b #bSubmit` 이미지(status-tag) 오버라이드 CSS 제거.
- 규칙화 메모: 아직 1회. 반복되면 "학습 조작 버튼(확인/제출/다음)은 문제 아트 표면 안이 아니라 표면 밖(아래) 표준 버튼으로 배치" 규칙을 builder_system.md에 제안 후보. (표면에 텍스트/컨트롤을 억지로 넣지 말라는 `[dialogue-as-speech-bubble]`·`[redundant-surface-label-text]`와 같은 계열)

### [weak-input-affordance] 탭 입력 칸(?박스)이 선택 가능함을 알리는 상시 어포던스가 없음

- 대상: content-harness-pipeline/runs/2026-07-08_ch802d08/output/index.html (`#s-b .kb-blank`), production/1-2/08/index.html (`.finger-hint`)
- 분류 태그: weak-input-affordance
- 상태: 열림
- 발생 횟수: 4
- 최초 발생일: 2026-07-09
- 최근 발생일: 2026-08-04
- 사례:
  - 2026-07-09: 유형 B의 정답 입력 `?`칸(`.kb-blank`)이 눌러서 선택하는 요소인데, 활성(`.active`) 전에는 아무 시각 신호가 없어 선택 가능한지 알기 어려움. 글로우/하이라이트로 선택 가능함을 알려야 함.
    - 조치: `#s-b .kb-blank:not(.filled):not(.active)`에 상시 골드 글로우 펄스(`kbInvite`) 추가. 활성/입력완료 시에는 애니메이션이 멈추고 각각 `.active` 글로우/`.filled` 상태로 전환. (튜토리얼 빈 슬롯 `slotPulse`와 같은 상시 pulse 어포던스 계열)
  - 2026-08-04: `production/1-2/08` `section_random_problems`에서 "**가리키는 이미지만 있으니 힌트인지 모르겠다. 힌트라고 글자가 필요할듯**"이라고 지적. 42-a·b가 넣은 `.finger-hint`(선생님을 가리키는 손가락 + 탭 애니메이션 3회)는 **"여기를 눌러라"까지만 말하고 "누르면 무엇이 나오는가"는 말하지 않는다.** 앞 사례가 **큐의 부재**(신호가 아예 없음)였다면 이번은 **큐의 의미 부재**다 — 상시 애니메이션까지 갖췄는데도 아이콘만으로는 기능이 안 읽힌다.
    - 경계 주의: `[redundant-surface-label-text]`(에셋·대사로 이미 표현된 정보를 라벨로 중복하지 말 것)와 **반대 방향**이라 헷갈리기 쉽다. 가르는 기준은 "글자가 있느냐"가 아니라 **그 정보가 그림만으로 전달되느냐**다. 손가락은 방향은 전달하지만 기능(힌트)은 전달하지 못한다.
    - 조치: `#fingerHintLabel`(`힌트` 필 라벨)을 손가락 아래에 함께 띄운다. 상세는 `production/1-2/08/complete.md` 66번.
  - 2026-08-04: `production/1-2/08` `section_shape_find`의 모양 찾기에서 "**처음에 `네모 모양을 찾아봅시다`로 시작하면 1학년이 클릭을 이해 못할 수도 있다**"고 지적. 앞 두 사례가 **한 요소의 큐 부재/의미 부재**였다면 이번은 **상호작용 규칙이 바뀌는 지점에 안내가 없는 것**이다 — 씬1~씬2 오프닝까지는 `.tap-layer`가 화면 전체를 덮어 "아무 데나 탭 = 진행"이었는데, 찾기 단계에서 처음으로 "정확한 대상 탭 = 정답 / 그 외 = 오답"으로 뒤집히면서 그 전환을 알리는 신호가 하나도 없었다. `.hotspot`은 투명이고 `glow-hover`는 `pointerenter`라 터치에서는 누른 뒤에나 켜진다. **결과적으로 아이의 첫 탐색 탭이 곧 첫 오답이 된다**(`registerSearchWrong`). 기존 스캐폴딩(오답 2회 → 글로우, 3회 → 번호)은 전부 실패 후행이라 "어떻게 하는지"를 "너 틀렸다" 두 번 뒤에 알려준다.
    - 조치: 첫 문항(`q_square_find_two`)에 한해 손가락 큐 + `네모 모양을 클릭해보세요` 라벨로 한 번 눌러 보게 하는 튜토리얼 단계를 넣고, 그동안 오답 판정을 끈다. 상세는 `production/1-2/08/todo.md` 69번.
    - 교훈: 어포던스는 요소 단위만이 아니라 **"조작 규칙이 바뀌는 첫 지점"** 단위로도 필요하다. 앞 화면에서 학습시킨 규칙을 뒤집는 자리가 곧 안내가 필요한 자리다.
  - 2026-08-04: `production/1-2/08` `section_random_problems`에서 "**힌트가 2개로 나뉘어지는데 다음 버튼이 없어서 힌트가 하나만 나오는 줄 알 듯하다. 힌트에 다음 버튼을 추가하자**"고 지적. 53번이 힌트를 2단계로 쪼개면서 **다음 단계를 여는 조작을 `#helpCharacter`(선생님) 재탭 하나에만** 걸어 뒀다. 힌트 말풍선(`#helpCard`)에는 `.repair-bubble-nav`가 없어 **더 있다는 신호가 0개**다 — `.help-speech`에 `cursor:pointer`는 걸려 있지만 클릭 핸들러조차 없는 죽은 표면이었다. 같은 문서의 다른 모든 말풍선(도입·모양·산술·자유 그리기)은 `ADVANCE_NAV_HTML`(`다음 ▸`)로 다음 대사가 있음을 알린다 — **힌트 말풍선만 그 표준에서 빠져 있었다.** 앞 세 사례가 "조작 가능함/무엇이 일어나는가/규칙이 바뀜"을 안 알린 것이라면, 이번은 **콘텐츠가 더 남아 있음**을 안 알린 것이다. (**조치 완료 2026-08-04** — `production/1-2/08/complete.md` 80번: `#helpCard`에 표준 `.repair-bubble-nav`를 붙이고 말풍선 자체를 클릭 대상으로 만들었다. 마지막 단계는 `닫기`.)
- 규칙화 메모: **4회 → `[weak-drag-affordance]`와 묶으면 5회라 rule 승격 제안 대상이다(2026-08-04).** 4번째 사례로 **"여러 단계로 나뉜 표면(단계형 힌트·연속 대사)은 다음 단계가 있다는 것을 표면 안에서 `다음 ▸`로 알린다. 다음 단계를 여는 조작을 표면 밖(캐릭터 재탭 등)에만 두면 학습자는 단계가 하나뿐인 줄 안다"**를 초안에 넣는다. "탭·드래그 등 상호작용 대상은 유휴 상태에서도 상시 pulse/glow로 조작 가능함을 알린다"에 더해 **"아이콘·손가락 같은 지시 큐는 대상만 가리키지 말고 무엇이 일어나는지 짧은 글자로 함께 말한다"**를 초안에 넣는다. 3번째 사례로 **"조작 규칙이 앞 화면과 달라지는 첫 지점에는 실패 후행 힌트가 아니라 선행 시연(한 번 눌러 보게 하기)을 두고, 그 구간에서는 오답 판정을 끈다"**를 함께 넣는다. 반복되면 builder_system.md에 제안 후보.

### [flat-ui-lacks-tactility] 기능적 UI(키패드 등)가 납작하고 누름 반응이 없어 밋밋함

- 대상: content-harness-pipeline/runs/2026-07-08_ch802d08/output/index.html (`#s-b` `.keypad .key`)
- 분류 태그: flat-ui-lacks-tactility
- 상태: 열림
- 발생 횟수: 1
- 최초 발생일: 2026-07-10
- 최근 발생일: 2026-07-10
- 사례:
  - 2026-07-10: 유형 B 입력 키패드가 납작한 흰색 키(그라데이션·입체감·누름 반응 없음)라 밋밋함. 사용자가 "이미지 생성 vs CSS 효과 중 뭐가 낫냐" 문의. (이미지 생성은 현 codex 환경에서 PIL 폴백이라 불가 → CSS가 정답, 기능적 입력은 [ornate-asset-wrong-function]상 이미지보다 CSS가 맞음)
- 조치: CSS로 입체 탱타일 버튼화 — 위 광택 그라데이션 + `box-shadow`의 `0 4px 0 <lip색>`으로 하단 립(물리 버튼), `:active`/`.pressed`에서 `translateY(4px)`+립 축소로 눌리는 press 애니메이션. 숫자/확인(금색)/del(코랄)/닫기(나무톤) 팔레트 구분, 상단 그립 핸들. 터치 확실성 위해 `pointerdown/up`으로 `.pressed` 토글(:active 보완).
- 규칙화 메모: 아직 1회. 반복되면 "기능적 인터랙티브 UI(버튼/키패드/토글)는 납작한 단색 대신 입체 어포던스(광택+하단 립+누름 애니메이션)를 기본 제공하고, 이미지 생성 대신 CSS로 처리한다" 규칙을 builder_system.md에 제안 후보.

### [spec-success-feedback-missing] 스펙이 지정한 성공 연출/메시지를 누락하거나 축소해 구현

- 대상: content-harness-pipeline/runs/2026-07-08_ch802d08/output/index.html (`#s-c` `checkC`/`loadC`)
- 분류 태그: spec-success-feedback-missing
- 상태: 열림
- 발생 횟수: 2
- 최초 발생일: 2026-07-09
- 최근 발생일: 2026-08-04
- 사례:
  - 2026-07-09: 유형 C 정답 완료 시 스펙(md Scene 3 항목 5)은 "모니터 화면이 밝아지며 [시스템 재부팅 완료!] 메시지 출력"인데, 구현은 mon-status 한 줄 텍스트만 `q.done`으로 바꾸고 문제를 그대로 둔 채 넘어감. 또 진행중 표시(재부팅 중 `…`)가 정적이라 진행감이 없음.
    - 조치: `checkC`를 "화면(`.mon-screen.rebooted` glow)이 밝아지며 문제/트레이를 지우고 `✅ 시스템 재부팅 완료!` 메시지만 2초 출력 후 다음 문제"로 변경. 마지막 문제는 `nextC`에서 중복 메시지 제거하고 곧장 수리 아웃트로로. 상태문구 끝 점을 `. / .. / ...` 반복(`startMonLoading`/`stopMonLoading` + `.mon-status .dots` 고정폭)으로 진행중 연출 추가.
  - 2026-08-04: `production/1-2/08` 씬2 모양 찾기에서 "**눌러도 상호작용이 초록색 테두리밖에 없어서 알기 힘들다. 각각의 모양을 올바르게 클릭했을 때 정답 도장이 나오고, 2개를 모두 클릭 완료했을 때 도장+다음 버튼이 나오는 게 좋겠다**"고 지적. 정답 사물을 하나 맞혔을 때의 신호가 `glow-found`(초록 외곽선)와 딩동뿐이었다 — **상태 변화(색)만으로 판정을 전달**했고, 도장은 문항 2개를 다 맞힌 뒤에야 나왔다.
    - 경계 주의: 앞 사례가 **스펙이 지정한 연출을 축소**한 것이라면 이번은 **연출의 단위가 학습 단위보다 큰 것**이다. 원문(`…723 요청.md` 씬2 항목 7)의 정답 효과는 문항 단위(딩동+`정답입니다`+O 표기)로만 적혀 있고 사물 단위 피드백은 없다. 아이가 판정을 받는 단위는 **클릭 한 번**인데 연출은 문항 단위였다. 이 태그의 뜻을 "스펙 대비 축소"에서 **"학습자가 판정을 받는 단위마다 확실한 성공 신호가 있는가"**로 넓힌다.
    - 조치: `selectHotspot`에서 사물 하나를 맞힐 때마다 `showStamp(...,'correct')`(0.7초 도장)를 내고, 마지막 하나에서 기존 `showFeedback`(도장 유지 + `다음 ▸`)으로 넘긴다. 상세는 `production/1-2/08/complete.md` 70번.
- 규칙화 메모: 2회. 초안 — **"정답/오답 판정은 요소의 상태 변화(테두리·색)만으로 전달하지 않는다. 학습자가 판정을 받는 단위(클릭 한 번·입력 한 번)마다 상태와 독립된 신호(도장·소리)를 내고, 문항이 끝나는 지점에서만 진행 표면을 연다."** 반복되면 `prompts/builder_system.md`의 channel 렌더링 계약 `feedback` 절에 제안 후보.

### [rapid-answer-no-cooldown] 객관식 보기 선택에 연타 방지 대기시간이 없음

- 대상: content-harness-pipeline/runs/2026-07-08_ch802d08/output/index.html (`pickA`, `.quiz-op` 클릭 핸들러)
- 분류 태그: rapid-answer-no-cooldown
- 상태: 열림
- 발생 횟수: 1
- 최초 발생일: 2026-07-10
- 최근 발생일: 2026-07-10
- 사례:
  - 2026-07-10: 객관식 보기 선택 시 대기시간이 없어 "우다다다" 연타 선택이 가능함. 오답을 눌러도 즉시 다시 누를 수 있어 연출/피드백이 겹치고 무의미한 연타가 됨. 드롭다운(키패드 입력·드래그)이 아닌 클릭형 객관식(유형 A, 마무리 퀴즈)에 1초 대기시간을 요청. 정답 분기는 이미 보기를 잠그고 다음으로 넘어가므로, 문제는 오답 분기의 무제한 재클릭.
- 조치: 유형 A `pickA`와 퀴즈 `.quiz-op` 핸들러에 선택 직후 1초 잠금(busy 플래그) 추가 — 클릭 시 즉시 잠그고 오답이면 1000ms 후 해제, 정답/강제진행이면 그대로 잠금 유지(다음 문제 로드 시 해제). 키패드(유형 B)·드래그(유형 C)는 객관식이 아니므로 제외.
- 규칙화 메모: 아직 1회. 반복되면 "클릭형 객관식 보기 선택은 선택 직후 짧은 잠금(≈1s)으로 연타를 막고, 오답 피드백 애니메이션이 끝난 뒤 재시도를 허용한다" 규칙을 builder_system.md에 제안 후보.
- 규칙화 메모: 아직 1회. 반복되면 "스토리보드가 정답/성공 시 화면 상태 변화(밝아짐·메시지·문제 제거 등)를 명시하면 텍스트 한 줄 치환으로 축소하지 말고 명시된 연출을 그대로 구현" 규칙을 builder_system.md에 제안 후보. (`[spec-fx-color-mismatch]`와 같은 '스펙 연출 임의 축소/변경' 계열)

### [cta-reveal-reflow-shift] 정답 후 나타나는 CTA가 중앙 정렬 콘텐츠를 밀어 올림

- 대상: content-harness-pipeline/runs/2026-07-08_ch802d08/output/index.html (`#s-quiz #btnToCert`), production/1-2/08/index.html (`.story-card`의 `.repair-bubble-nav`)
- 분류 태그: cta-reveal-reflow-shift
- 상태: 열림
- 발생 횟수: 2
- 최초 발생일: 2026-07-10
- 최근 발생일: 2026-08-04
- 사례:
  - 2026-07-10: 마무리 퀴즈에서 정답을 맞히면 하단 `인증서 받으러 가기` 버튼(`#btnToCert`)이 `.hidden` 해제되며 나타나는데, 이 버튼이 `.center-col`(transform으로 세로 중앙정렬된 flex 컬럼)의 flex 자식이라 나타나는 순간 컬럼 높이가 커져 퀴즈(문제 plaque+보기)가 위로 밀려 올라감. 사용자가 "밀어 올리지 말고 CTA를 오버레이로 위에 덮으라"고 지적.
  - 2026-08-04: 08차시 씬6(수리 이야기) 표지판 설명 카드에서 사용자가 "**다음 버튼이 계속 움직여 한쪽으로 고정하자 우하단으로**"라고 지적. **같은 뿌리의 역방향 사례다** — 7-10은 진행 컨트롤이 나타나며 콘텐츠를 밀었고, 이번은 콘텐츠 길이가 진행 컨트롤을 밀었다. `.story-card`가 `display:grid; align-content:center`라 글 + `다음 ▸`가 한 덩어리로 세로 중앙에 오는데, beat가 1줄(`무슨 표지판일까요?`)과 4줄(설명)로 번갈아 나와 버튼 y가 **284~330 ↔ 366~413(82px)** 로 튀었다(headless 실측, stage 1920×1080 환산). 공통 원인은 **진행 컨트롤을 콘텐츠 흐름 안에 둔 것**이다.
- 조치: (2026-07-10) `#btnToCert`를 `.center-col` flex 흐름에서 빼내 다른 씬 전환 CTA와 동일한 절대배치 `.bottom-bar`(position:absolute; bottom:3.5%; z-index:16) 오버레이로 이동. 나타나도 컬럼 높이가 변하지 않아 퀴즈가 그대로 유지되고 버튼은 위(z-index)로 떠서 덮음. `hidden` 토글은 버튼 자체에 유지되어 JS 변경 불필요. / (2026-08-04) `.story-card .repair-bubble-nav`를 그리드 행에서 빼내 카드 크림 면 우하단에 절대배치(`right:64px; bottom:153px`)하고, 글이 버튼과 겹치지 않도록 `padding-bottom`을 153 → 212px로 늘려 버튼 자리를 비웠다. 가로 앵커(x 1236)는 종전과 같다.
- 규칙화 메모: 2회. 반복되면 "**진행 컨트롤(`다음`·CTA)은 콘텐츠 흐름에 넣지 않는다** — 나중에 나타나든 콘텐츠 길이가 바뀌든 한쪽이 다른 쪽을 밀어 자리가 튄다. 표면의 고정 모서리에 절대배치하고 그만큼 콘텐츠 영역을 줄여 겹침을 막는다"를 builder_system.md에 제안 후보. (`[action-control-on-art-surface]`의 'CTA 배치' 계열, `[bg-anchor-alignment]`의 "개수가 변하는 박스는 정렬 기준을 면의 고정 모서리에 둔다"와 같은 축)

### [unwanted-celebration-fx] 특정 씬에서 원치 않는 축하 이펙트 제거 요청

- 대상: content-harness-pipeline/runs/2026-07-08_ch802d08/output/index.html (`goldBurst`, `#s-cert` 진입)
- 분류 태그: unwanted-celebration-fx
- 상태: 제안됨
- 발생 횟수: 5
- 최초 발생일: 2026-07-10
- 최근 발생일: 2026-08-04
- 사례:
  - 2026-07-10: 인증서(`#s-cert`) 진입 시 화면 아래에서 위로 ✨🌟💫 아이콘이 쏟아져 올라가는 효과(`goldBurst`, `.particle floatUp`)를 지워달라고 요청. (fireworks 방사형 스파크·fanfare 사운드는 별개로 유지)
  - 2026-07-10: (후속) 같은 효과를 마무리 퀴즈(`#s-quiz`) 정답 시에도 지워달라고 요청.
  - 2026-07-10: (후속) 유형 C에서 복구 씬으로 넘어갈 때(`checkC`→`showSceneById('s-repair')` 진입, `goldBurst(20)`)의 효과도 지워달라고 요청.
  - 2026-08-04: **(축하 이펙트가 아닌 첫 사례 — 태그를 "장식 이펙트 일반"으로 넓힌다)** `production/1-2/08` `section_random_problems`에서 "**힌트 손가락에 글로우 빼 달라**"고 지적. `.finger-hint{filter:var(--ds-sm) var(--filter-glow-md)}`의 노란 소프트 광이다. 손가락은 **기능 큐**(선생님을 누르라)라 장식 광이 정보를 더하지 않고 화면만 시끄럽게 한다. 조사에서 갈래가 하나 더 나왔다 — 손끝의 또렷한 **금색 링은 CSS가 아니라 `tap-hint-hand.webp`에 구워진 탭 파문**이라(에셋 x 0.071~0.272 / y 0.068~0.270) CSS를 빼도 남는다. **사용자 결정: CSS 헤일로만 제거, 에셋 링은 유지**(2026-08-04). (**조치 완료 2026-08-04** — `production/1-2/08/complete.md` 70번)
  - 2026-08-04: **(5회차 — 같은 토큰이 다른 자리에서 또 걸렸다)** `production/1-2/08` `section_arithmetic_tutorial`에서 82번으로 넣은 페인트 통 하이라이트를 두고 "**노란색 하이라이트 너무 촌스럽다. 그냥 글로우만 뺄까?**"라고 지적. `@keyframes canSpotlight`의 `--filter-glow-lg`(= `drop-shadow(0 0 22px #ffe86a) drop-shadow(0 0 38px #fff080)`)다. 크림색 담장 위에서 노랑은 대비가 거의 없어 색으로 안 읽히고 뿌연 번짐만 남고, "굵은 외곽선 + 플랫 셰이딩" 화풍에 soft bloom이 이질적이다. **82번 검증 메모에 이미 "글로우만으로는 안 보여 크기 펄스를 얹었다"고 적혀 있어, 실제로 일하던 신호는 펄스였고 글로우는 촌스러움만 얹고 있었다.** 사용자 결정: A안(글로우 제거, 모션만). (**조치 완료 2026-08-04** — `production/1-2/08/complete.md` 84번)
- 조치: 인증서 진입(btnToCert)·퀴즈 정답 분기(`.quiz-op`)·유형 C→복구 씬 진입에서 `goldBurst()` 호출 제거(fanfare·fireworks·sparkOnEl 등은 유지). goldBurst는 아직 복구 씬 2곳(messy→clean 배경 전환 `goldBurst(16)`·복구 완료 celebrate `goldBurst(16)`)에 남아 있음 — 추가 제거는 확인 후 진행.
- 규칙화 메모: **5회 → rule 승격 제안(2026-08-04). 사용자 승인 대기.** 4·5회차가 모두 `--filter-glow-*` **같은 토큰**이고 자리만 달랐다(손가락 힌트 → 페인트 통). 초안: "공용 축하 이펙트(goldBurst/fireworks 등)와 **장식 글로우 토큰**은 씬별로 on/off를 명시적으로 관리하고, 특정 자리에서 빼달라는 요청 시 **같은 토큰을 쓰는 다른 호출부까지 함께 점검**한다. **기능 큐(어포던스 표시)에는 장식 광을 얹지 않는다** — 정보를 더하지 않으면서 시선만 뺏는다. **강조가 필요하면 광이 아니라 모션(크기 펄스·방향성 있는 등장)이나 알파를 따라가는 단색 외곽선으로 낸다** — 굵은 외곽선 + 플랫 셰이딩 화풍에 soft bloom은 이질적이고, 크림·파스텔 배경 위에서 노란 광은 대비가 나오지 않아 신호 역할도 못 한다."
  - 반영 위치 제안: 최상단 `AGENTS.md`의 "CSS 규칙" 아래 새 절(`강조 표현`). 파이프라인 산출물뿐 아니라 `production/` 손수정에서도 반복되고 있어 `content-harness-pipeline/AGENTS.md`보다 최상단이 맞다.
  - 함께 볼 것: **효과가 CSS인지 에셋에 구워진 것인지 먼저 가른다.** 08차시 손가락은 둘이 겹쳐 있어 CSS만 빼면 절반만 사라진다. 이 확인 없이 "뺐다"고 보고하면 사용자 화면에서는 그대로 남아 있다.
  - 경계: `[ambient-effect-hover-only]`(상시로 요구된 글로우를 호버에만 구현)와 **반대 방향**이다. 가르는 기준은 "글로우가 있느냐"가 아니라 **그 광이 상태를 알리느냐(기능) 분위기를 내느냐(장식)** 다.

### [spec-interaction-flow-mismatch] 원본 기획의 화면 흐름/상호작용을 임의로 다르게 구현

- 대상: content-harness-pipeline/runs/2026-07-08_ch802d08/output/index.html (`#s-story` 마무리 퀴즈 흐름), production/1-2/08/index.html (`randomSequence`, `#storyIntroBoard`)
- 분류 태그: spec-interaction-flow-mismatch
- 상태: 열림
- 발생 횟수: 4
- 최초 발생일: 2026-07-10
- 최근 발생일: 2026-08-03
- 사례:
  - 2026-08-03: 같은 씬에 대해 이번엔 **반대 방향**의 지적 — "**6문제가 아니라 4문제**다. 세 수의 덧셈·뺄셈을 각각 2개로 나누지 말고 바로 가라. `8+2+6`이면 `8+2` 한 문제 다음 `8+2+6`이 아니라 **바로 `8+2+6`**을 하는 것이다." 바로 위 사례(4유형 전부 출제)를 29-a에서 `randomSequence=[0,1,2,3,4,5]`로 반영했는데, 유형 C·D를 각각 **2단계(type 2=`a+b` → type 3=`a+b+c`, type 4=`a-b` → type 5=`a-b-c`)로 쪼개** 6문항으로 만든 것이 문제였다. 원문의 "4유형"은 **문항 4개**이지 유형당 준비운동 문항을 붙이라는 뜻이 아니다. 즉 앞 사례가 "스펙 범위를 임의로 **좁힘**"이었다면 이건 "스펙 단위를 임의로 **쪼개 늘림**"이다. (미조치 — `production/1-2/08/todo.md` 43번)
  - 2026-07-10: 원본 기획(`2학년_8차시(시간)_임상현_no_img.md` 활동3 Scene2)의 마무리 퀴즈는 "갤러리를 **모두 넘겨보면** 꼬마 사서가 톡 튀어나오며 **돌발 팝업 퀴즈**를 그 자리에 띄우고, 맞히면 게이지 100%+인증서 유도" 구조인데, 구현본은 `[마무리 퀴즈 풀러 가기]` 버튼으로 **별도 s-quiz 씬 이동**이었음. 사용자가 원본대로 책 위 팝업 퀴즈(이미지 겹침 허용)로 바꾸고 맞히면 `[인증서 받으러 가기]`가 나오도록 요청.
  - 2026-08-03: `production/1-2/08` `section_random_problems`에서 "A: 10이 되는 덧셈, B: 10에서 뺄셈, C: 세 수의 덧셈, D: 세 수의 뺄셈 이렇게 4개가 나와야 하는데 3개가 나오고 있다. 생성 규칙은 원문(input.json)을 참조해야 한다"고 지적. 원문 md(`수리력 1차_1학년 2학기 8차시 (백승용) 723 요청.md` 325~394행)는 4유형을 모두 요구하는데, 구현은 `randomSequence=Math.random()<.5?[0,2,3]:[1,4,5]`로 **A+C 묶음 또는 B+D 묶음 중 하나만** 골라 3문항만 낸다. 이건 실수가 아니라 2026-07-31 조치(`content-flow-state-scaffolding-regression`)에서 "A→같은 operand를 쓰는 C 또는 B→D 묶음 하나를 선택"하도록 의도적으로 넣은 것이라, **파이프라인이 스스로 스펙 범위를 좁혔다는 점**이 이 태그의 재발이다. (미조치 — todo 29번)
  - 2026-08-03: 같은 차시 `section_math_story`에서 "`모양을 길에서 본 적 있나요?` 위에 동그라미·세모·네모가 필요한데 아무 모양도 안 나온다. 그 다음 화면에 나오는 게 아니다"라고 지적. 원문 md 449~451행의 예시화면 문구는 `수리 이야기 / 모양을 길에서 본 적이 있나요?` → `● ■ ▲` → `무슨 표지판일까요?` 순인데, 구현은 `● ■ ▲`를 인트로 판(`#storyIntroBoard`)이 아니라 **다음 화면의 `storyBeats[0]`(`.story-card`)** 으로 미뤄 놨다. (**조치 완료 2026-08-03** — complete.md 32번: `#storyIntroBoard` 문구 위에 `.paint-shape` ●■▲를 넣고 `storyBeats[0]`을 제거했다. 판 높이(220px)는 원본 비율 유지를 위해 늘리지 않았다.)
- 조치: (1차) `#s-story`에 책 위 겹침 팝업 퀴즈를 인라인 구현했으나, 사용자가 "그게 아니라 기존 s-quiz 화면(플라크 문제판+티켓 보기)처럼 보여달라. 퀴즈를 별도 단계로 만들지 말고 이야기→(내부에서)퀴즈→인증서로 흐르게"라고 재지적. (2차·최종) 책 위 겹침 팝업(`storyQuiz`/`.sq-op`/`storyKidSay`/`btnStoryCert`)과 CSS(`.story-quiz`) 전부 제거. 이야기 마지막 페이지에서 `❯` → `showSceneById('s-quiz')`로 원본 기획의 팝업 퀴즈 화면(꼬마 사서 등장+플라크 문제판+보기 티켓, SCENE_INTRO가 take14 재생)으로 전환 → 정답 시 `[인증서 받으러 가기]`(기존 btnToCert)→s-cert. `[마무리 퀴즈 풀러 가기]` 버튼은 제거되어 별도 클릭 단계 없음. `#s-quiz`는 이제 이야기 흐름에서만 도달(메뉴 항목은 존치). (3차·최종) 사용자가 "화면(씬)을 바꾸지 말고 해당 화면에서 띄우라"고 재지적 → 씬 전환(`showSceneById('s-quiz')`) 제거. 대신 `#s-story` 안에 s-quiz와 동일한 **플라크 문제판+티켓 팝업**(`.story-quiz-pop`, `.plaque`+`.row .choice-ticket .sq-op`)을 인라인 추가하고, 책 다 넘기면 `startStoryQuiz()`로 그 화면에서 팝업을 띄운다(`#s-story.story-quizzing .center-col{display:none}`로 책만 숨기고 배경·캐릭터 유지 → 보내준 이미지와 동일). 정답→게이지 100%·take15·`#btnStoryCert`→s-cert. (4차) 팝업이 책을 숨기고 티켓이 줄바꿈돼 흩어짐 → 사용자가 "화면 바꾸지 말고 위로 겹쳐라(올리라는 게 아님)"고 지적. 책 숨김 제거하고 `.story-quiz-pop`을 `inset:0` 전체 오버레이+flex 중앙정렬(z-30), `.row{flex-wrap:nowrap}`로 티켓 한 줄 고정. 인증서 버튼은 오버레이(z-30) 뒤에 깔려 안 보여 `.sqp-cert` 래퍼로 오버레이 내부 하단에 이동(클릭 가능).
- 규칙화 메모: 아직 1회. 반복되면 "구현 전 원본 기획 md의 씬별 상호작용/흐름(팝업·자동전환·트리거)을 그대로 반영하고 별도 화면 이동으로 대체하지 않는다" 규칙을 builder_system.md에 제안 후보.

### [generated-v2-assets-not-integrated] 새로 생성한 V2 캐릭터가 화면에 연결되지 않음

- 대상: content-harness-pipeline/runs/2026-07-08_ch802d08/output/index.html (`teacher_pointing.png`, `teacher_happy.png` 참조)
- 분류 태그: generated-v2-assets-not-integrated
- 상태: 열림
- 발생 횟수: 1
- 최초 발생일: 2026-07-13
- 최근 발생일: 2026-07-13
- 사례:
  - 2026-07-13: `teacher_worried.png` 그림체에 맞춰 `teacher_pointing_v2.png`, `teacher_happy_v2.png`를 생성한 뒤 실제 화면의 기존 캐릭터 이미지를 V2로 바꿔달라고 요청.
- 조치: `index.html`의 정적 이미지 참조와 런타임 교체 경로를 V2 파일명으로 변경하고, 새 happy 포즈에 맞게 박수 표현의 대체 텍스트도 수정. 기존 PNG 파일은 보존.
- 규칙화 메모: 아직 1회. 반복되면 "기존 화면용 대체 에셋을 생성한 작업은 파일 생성에서 끝내지 말고, 대상 HTML/CSS/JS 참조 교체와 미사용 구버전 참조 검색까지 통합 검증한다" 규칙을 content-harness-pipeline/AGENTS.md에 제안 후보.

### [content-eval-scoring-too-lenient] content-eval 점수체계가 널널해 storyboard/스펙 미준수를 못 걸러냄

- 대상: content-harness-pipeline/content_rubric.yaml, prompts/content_eval_system.md, schemas/content_eval_output.schema.json
- 분류 태그: content-eval-scoring-too-lenient
- 상태: 열림
- 발생 횟수: 2
- 최초 발생일: 2026-07-13
- 최근 발생일: 2026-07-16
- 사례:
  - 2026-07-16: **(핵심) eval이 "제작 지시"를 "필수 노출 원문"으로 오분류해 없는 누락을 세고 있음.** ch8c0716의 content_fidelity=1(누락 6개)을 planner와 직접 대조해 분해한 결과, 6개 전부가 **오탐**이었다. 내역: ①`channel=question_display` ×3 — 이건 문항이 아니라 **storyboard의 예시 화면 문구**다. 해당 section에는 `questions[]`에 실제 문항 4개(a1~a4)가 이미 있고 builder가 그 4개를 원문 그대로 렌더했는데, eval은 예시 문구까지 화면에 나와야 한다고 셌다(그대로 따르면 5번째 가짜 문항이 생긴다). ②`channel=interaction_instruction` ×3 — "3개의 시계 중 하나를 직접 터치하여 선택." 같은 **조작 방법 제작 지시**이지 화면에 띄울 문장이 아니다. 근본 원인: planner `elements[].content`가 **(a)실제 노출 문구·(b)제작 지시 산문·(c)예시 mockup을 한 필드에 섞어** 담고 있고, rubric의 counting_rule (d)는 "사용자에게 노출되는 필수 content"라고만 해서 **셋을 가르는 판단을 LLM 재량에 맡긴다.** `channel` 필드가 이미 그 구분을 할 수 있는데 rubric이 안 쓴다. 판정이 매 iter 흔들리는 이유도 이것 — 점수가 산출물이 아니라 **judge의 그때그때 분류 변덕**을 측정한다(ch8c0717: 5→2→4→?→1개). 실제 원문 보존율은 questions 38/38, dialogue 14/14로 **사실상 만점**인데 축 점수는 1점이다.
  - 2026-07-16: (같은 대상의 **반대 극** — 결정적 채점 전환 후) 인플레는 잡혔으나 이번엔 **척도 포화로 신호가 사라짐**. `content-html:v4`의 content_fidelity는 "누락·불일치 **4개 이상 = 1점**"이라 ch8c0716의 6→5→7개 변동이 전부 같은 1점으로 뭉개진다. 3개를 고쳐도 점수가 그대로라 refine에 **개선 gradient가 없다**. functional_integrity도 값이 1/3/5 세 개뿐(2개 이상=1, 1개=3, 0개=5)이라 5→2개 개선이 0점 변화, 2→1개가 +2점 점프를 만들어 총점이 계단식으로 튄다. feedback_scaffolding은 `count_capped`로 "피드백 없는 문항 1개라도 있으면 3점 초과 불가"라 사실상 3에 고정. 게다가 eval은 **stateless** — `stages/content_evaluator.py`가 이전 eval을 안 넘기므로 매 iter 10만 자 HTML에서 위반을 새로 세고, 그 개수 자체가 표본 노이즈(ch8c0717: 5→2→4→?→1). 결과적으로 총점은 개선 신호가 아니라 **판정 분산**을 측정한다(ch8c0716: 3.06→2.64→2.88→2.88→2.88 / ch8c0717: 2.64→3.38→2.42→2.24→3.66). 부수 관측: 루프에 **best-so-far 보존이 없어** `output/index.html`을 매번 덮어쓰므로, ch8c0717 iter002(3.38)처럼 더 좋았던 산출물이 남지 않고 최종은 마지막 iter가 된다.
  - 2026-07-13: 그동안 파이프라인을 돌려보니 content-eval 점수체계가 너무 널널해서 산출 HTML이 storyboard(planner spec)를 잘 안 따르는데도 PASS가 남. 원인 진단: (1) storyboard_fidelity가 weight 0.20으로 최고인데 min_axis는 3.8로 최저(가장 널널). (2) weighted_total 4.0이 6축 가중평균이라 약한 storyboard가 다른 축으로 상쇄됨. (3) rubric의 hard_gates(핵심 장면 누락 등)와 모델 verdict 필드가 runner(get_content_eval_status)에서 실제로는 무시되고 숫자 threshold만 봄. (4) anchor가 1/3/5만 정의돼 모델이 4.2~4.6 소수점에 몰려 채점(인플레). 사용자가 축과 점수체계를 결정적(deterministic) 채점으로 재설계하기로 함.
- 조치: **2026-07-16 1차 수정 완료 — 실측으로 검증됨.**
  - (1) `planner_output.schema.json`의 `elements[]`에 `rendered_text: string[]` 추가(required, `[]`=노출 없음 — Codex strict 제약상 optional 불가). 판정 기준은 **"학습자가 화면에서 이 문자열을 읽는가" 하나**. 원문 서술은 `content`에 그대로 남으므로 지시를 잃지 않는다.
  - (2) `content_eval_system.md`·`content_critique_system.md`·`content_rubric.yaml`의 체크리스트를 `elements[].content` → `elements[].rendered_text`(비어 있지 않은 것만)로 교체. 대조는 `grep -cF` 강제 — `-F` 없이 `grep -c "[확인하기]"`를 하면 대괄호가 정규식 문자클래스로 읽혀 **62곳에 매치**되어 진짜 누락을 놓친다(실측). 그 근거를 프롬프트에 함께 적었다.
  - (3) `content_evaluator.py`에서 `input.json`을 입력에서 제거. 거기엔 story board 본문이 없고 `md_path` 경로만 있어 "story board를 보라"는 착각만 만들었다. eval의 기준 원문은 planner임을 명시.
  - (4) `--content-eval-only`에 planner schema 검증 추가 — 없으면 구형 planner(rendered_text 없음)로 채점할 때 체크리스트가 통째로 비어 "누락 0개 = 5점" 거짓 PASS가 난다.
  - **검증(같은 입력 planner 2회 독립 실행)**: 두 표본 모두 `예:` 예시 누출 0건, v1이 과다 포함하던 `90%`/`1~12(오전)`/`[?]`/`착!` 0건, v2가 잃던 `[확인하기]`/`[내 사진첩에 저장하기]`/`[3. 수리 이야기 보러 가기 →]` 전부 포착. **content_fidelity 1점 → 3점, 두 표본 동일.** 남은 누락 2건은 전부 진짜(`[확인하기]` 대괄호 벗김, `[STEP 2. 수리로 해결해요]`는 노출 여부 미정). 체크리스트 크기는 40 vs 47로 흔들렸지만 **점수는 동일** — 흔들린 항목(키패드 숫자 0~9, `오전`/`오후`)이 전부 HTML에 실재해 누락으로 안 잡히기 때문. **드리프트가 점수에 영향을 주지 않는다.**
  - 부수 효과: min_axis 5.0 게이트가 **만족 가능해졌다.** 예전엔 eval이 제작 지시를 세는 한 누락 0개가 원리적으로 불가능했다.
  - 남은 것: 척도 포화(4개 이상=1)와 stateless 판정은 그대로. 결정적 검증기(C)로 축을 옮기는 것은 미착수.
- 규칙화 메모: 이 항목은 상위 원인(메타). 하위 증상 계열 — [spec-interaction-flow-mismatch], [spec-success-feedback-missing], [sequential-scene-choreography], [typeB-problem-text-mismatch-spec] 등 "builder가 planner spec을 안 따른다"가 반복되는데 eval이 이를 REJECT로 못 잡은 결과. eval 채점을 결정적으로 만들면 이 계열의 재발을 상류에서 차단하는 것이 목표.

### [codex-bin-resolution-mismatch] Python subprocess가 shell과 다른(낡은) codex 바이너리를 실행함

- 대상: content-harness-pipeline/runner.py (`--codex-bin` 기본값 `"codex"`), stages/scripts/codex_client.py
- 분류 태그: codex-bin-resolution-mismatch
- 상태: 열림
- 발생 횟수: 1
- 최초 발생일: 2026-07-15
- 최근 발생일: 2026-07-15
- 사례:
  - 2026-07-15: `gpt-5.6-sol` 전환 후 planner가 62.94초 만에 RuntimeError. API 400 `"The 'gpt-5.6-sol' model requires a newer version of Codex."` + stderr `codex_models_manager::cache: failed to load models cache: unknown variant 'max'`. **모델·스키마·코드 문제가 아니라 실행 바이너리 문제였음.** 이 머신에 codex가 둘 설치돼 있고(`AppData/Roaming/npm/codex.CMD` = 0.144.3, `~/.codex/bin/codex.exe` = 0.133.0-alpha.1), bash `codex`는 0.144.3을 타는데 **Python `subprocess.run(['codex',...])`은 0.133.0-alpha.1을 탐**. 원인: Windows `CreateProcess`가 확장자 없는 이름에 `.exe`만 붙여 탐색하므로 npm의 `codex.CMD`를 건너뛰고 PATH 뒤쪽 `codex.exe`(구버전)를 잡음. `shutil.which('codex')`는 `npm\codex.CMD`를 답해서 **which로 확인하면 정상처럼 보이는 함정**이 있음(실제 실행 경로와 불일치). 구버전이라 gpt-5.5는 통과했고 gpt-5.6-sol만 400으로 거절돼, 모델을 바꾸기 전까지 증상이 드러나지 않았음. `unknown variant 'max'` 캐시 에러는 신버전이 쓴 models 캐시를 구버전이 못 읽는 같은 원인의 곁가지.
- 조치: `default_claude_bin()`과 같은 패턴으로 `default_codex_bin()` 추가 — win32에서 `shutil.which("codex")`로 shell과 동일한 해석을 쓰고, `--codex-bin` 기본값을 `DEFAULT_CODEX_BIN`으로 교체. 검증: 수정 전 `CodexClient(codex_bin='codex')` + gpt-5.6-sol → FAIL(400), 수정 후 `DEFAULT_CODEX_BIN` = `...\npm\codex.CMD`(0.144.3)로 해석되고 planner schema 실호출 PASS. 구버전 `~/.codex/bin/codex.exe`(0.133.0-alpha.1)는 다른 도구가 의존할 수 있어 사용자 결정으로 **그대로 둠** — 해석 함수가 npm 쪽을 타므로 파이프라인은 영향 없음.
- 규칙화 메모: 아직 1회. `default_claude_bin()`이 이미 같은 계열의 Windows 바이너리 해석 문제를 claude 쪽에서만 해결해둔 상태라(codex는 `"codex"` 문자열 그대로), 이 항목은 그 비대칭이 드러난 것. 반복되면 "외부 CLI를 subprocess로 부를 때는 이름 문자열을 그대로 넘기지 말고 플랫폼별 해석 함수를 거쳐 실제 실행 경로를 확정하고, 그 경로와 버전을 run config에 기록한다"를 content-harness-pipeline/AGENTS.md에 제안 후보. 진단 비용이 컸던 이유가 **config에 `codex_bin: "codex"`라는 문자열만 남고 실제 실행된 바이너리·버전이 안 남아서**이므로, 규칙화 시 `config`에 resolved path + `--version` 기록을 포함할 것.

### [stage-timeout-underprovisioned] HTML 전문을 다루는 무거운 stage가 전역 timeout에 걸려 run 전체가 죽음

- 대상: content-harness-pipeline/runner.py (run_design_review_stage, resolve_design_refine_timeout, DEFAULT_TIMEOUT_SECONDS)
- 분류 태그: stage-timeout-underprovisioned
- 상태: 열림
- 발생 횟수: 2
- 최초 발생일: 2026-07-15
- 최근 발생일: 2026-07-15
- 사례:
  - 2026-07-15: (선행 사례) design_refine이 10만 자 규모 HTML을 통째로 재작성하다 1200초에서 TimeoutError (run ch8a0715 iter003). `DEFAULT_DESIGN_REFINE_TIMEOUT_SECONDS=2400` 특례를 추가해 해결했으나, 조치가 코드 주석(runner.py:111-113)에만 남고 problem.md에는 기록되지 않아 같은 패턴의 재발 신호로 축적되지 못함. **횟수는 이 주석 기록을 근거로 소급 집계한 것이므로, 사용자 피드백 기준으로만 세려면 1로 조정.**
  - 2026-07-15: design_review가 iter 002에서 1211초 만에 TimeoutError로 죽어 run ch8c0717 전체가 종료(`--timeout-seconds` 기본값 1200). design_refine과 동일한 원인 — HTML 전문 + asset 이미지를 모두 읽는 무거운 stage인데, design_refine만 전용 timeout 특례를 받고 design_review는 `args.timeout_seconds`를 그대로 받고 있었음. 30분 넘게 돌린 run이 통째로 날아감.
- 조치: (1) 전역 `DEFAULT_TIMEOUT_SECONDS`를 1200 → **2400**으로 상향(사용자 결정). 이제 planner/asset_generator/builder/content_critique/content_eval/content_refine 등 모든 stage가 기본 2400초를 받음. (2) design_refine과 같은 패턴으로 design_review 전용 timeout 추가 — `DEFAULT_DESIGN_REVIEW_TIMEOUT_SECONDS=2400`, `resolve_design_review_timeout()`, `--design-review-timeout-seconds`. 전역이 2400이 된 지금은 `max()` 결과가 같아 겹치지만, `--timeout-seconds`를 낮춰 돌릴 때 무거운 stage의 하한선으로 남음(검증: `--timeout 600`에서도 design_review/design_refine은 2400 유지). `run_design_review_only`도 같은 stage 함수를 거치므로 함께 적용됨.
- 규칙화 메모: 2회. 같은 패턴이 3번째 나오면(content_refine, builder가 후보 — 둘 다 HTML 전문을 쓰는데 전역 timeout을 씀) "HTML 전문을 읽거나 쓰는 stage는 전역 timeout이 아니라 stage 전용 timeout을 갖는다"를 content-harness-pipeline/AGENTS.md에 rule로 제안 후보. 다만 stage마다 `resolve_*_timeout` 함수를 복제하는 현재 방식은 3번째부터 중복이 커지므로, rule 승격 시 `AGENT_MODELS`처럼 stage별 timeout 테이블(`AGENT_TIMEOUTS`)로 일반화하는 편이 나음. 별도 관찰: content 루프에는 `write_failed` 래퍼가 없어 이렇게 죽으면 `{hash}_failed.json`이 안 남음(사용자 선택으로 이번 범위에서 제외).

### [entrance-anim-clobbers-centering-transform] 등장 애니메이션 keyframe이 `transform: none`으로 요소의 `translateX(-50%)` 중앙정렬을 덮어써 텍스트가 표면 밖으로 밀림

- 대상: content-harness-pipeline/runs/2026-07-15_ch8c0716/output/index.html (`.surface-text`/`#typeAPrompt`, `@keyframes beatIn`, `.scene.beats-in`)
- 분류 태그: entrance-anim-clobbers-centering-transform
- 상태: 보류 (최신 run은 멀쩡 — 간헐적 builder 이슈. 해제 조건: 새 run에서 중앙정렬 transform이 애니메이션/상태로 덮여 밀리는 게 재발하면 재개)
- 발생 횟수: 1
- 최초 발생일: 2026-07-21
- 최근 발생일: 2026-07-21
- 사례:
  - 2026-07-21: 유형 A(전광판) 문제를 **정상 진행**으로 들어가면 프롬프트 텍스트가 전광판 이미지 밖 오른쪽으로 밀려 잘리고, **백틱(`) 디버그 점프**로 같은 씬에 들어가면 정확히 전광판 안에 들어감. 근본 원인: `.surface-text`는 `left:45.5%` + `transform: translateX(-50%)`로 가로 중앙정렬하는데, 정상 진입 경로(`showScene`)만 `beats-in` 클래스를 1250ms 붙인다. 그 사이 `@keyframes beatIn`(`from{transform:translateY(22px)} to{transform:none}`)이 `animation-fill-mode:both`로 요소 `transform`을 통째로 덮어써 **`translateX(-50%)`가 사라지고 블록이 폭의 절반(≈410px)만큼 오른쪽으로 이동**한다. 디버그 점프(`__contentHarnessShowScene`)는 `beats-in`을 안 붙이므로 중앙정렬이 유지돼 정상. 같은 구조를 공유하는 `#typeBPrompt`·`#typeCPrompt`·`.visual-aid`(모두 `translateX(-50%)` + `beatIn`)도 동일 취약점.
  - **실측 검증(2026-07-21, chrome-headless-shell + CDP, stage 1920px 좌표계)**: `output/index.html`을 그대로 띄워 `__contentHarnessShowScene('scene-type-a')`로 렌더 후, 디버그 경로 vs `beats-in` 추가(정상 경로 재현)를 `getBoundingClientRect`로 계측. 디버그: `transform=matrix(…,-410,0)`, 박스 left=464 right=**1284**(중앙, 정상). 정상(beats-in): 애니 초반 `matrix(…,0,22)`·종료 후 `matrix(…,0,0)` 둘 다 left=874 right=**1694**(우측 +410px, 전광판 밖). beats-in 제거 시 `matrix(…,-410,0)`으로 **스냅백**. → 기전 100% 확정. **정정: 처음 추정한 "잠깐/일시적 flash"는 부정확**. 어긋남은 애니 `from`뿐 아니라 애니 종료 후에도 `beats-in`이 붙어있는 **1.25초 내내 지속**(both fill이 `transform:none` 유지)되며, 학습자가 첫 프롬프트를 읽는 인트로 구간 전체가 깨져 보인 뒤 스냅백한다. 2번째 문제부터는 `beats-in` 미부착이라 정상. 스크린샷의 첫 문제(3시5분전)가 right=1694 상태와 일치.
- 조치: **보류(2026-07-21).** 최신 run **ch8c0718 실측 결과 이 버그 없음** — 중앙정렬 요소의 등장 keyframe(`centerBubble`·`rewardCopyIn`·`titleNoticeIn`·`stamp`·`step2TicketLand`)이 전부 `to`에서 `translateX(-50%)`/`translate(-50%,…)`를 보존하고, `.cta:active`까지 `translateX(-50%) translateY(6px)`로 정렬 유지. `repairPartIn`(to:transform:none)의 대상(`.board`·`.mission-body` 등)은 base transform이 없어 덮을 게 없음. → ch8c0716 builder만 `beatIn`에서 정렬 transform을 빠뜨린 **간헐적 builder 이슈**이지 매 run 고정 버그가 아님. 사용자 결정: 지금은 안 넣고(최신 멀쩡) 재발 시 재개. 넣을 경우 후보 = `common_html_contract.md`에 "비파괴 애니메이션" 규칙(등장·전환·강조 애니메이션은 요소의 정착 위치·크기·정렬을 바꾸지 않는다)으로 회귀 봉인. 3안(A margin/inset로 정렬 이전, B 정렬 보존 keyframe, C inner 래퍼)은 개별 픽스용으로 보존.
- 규칙화 메모: 아직 1회. 기존 [fixed-pos-transformed-ancestor]와 계열(“transform과 다른 목적이 한 요소에서 충돌”)이나 기전이 다름(조상 transform이 아니라 keyframe이 base transform을 덮어씀). 반복되면 “`translateX(-50%)` 등 base transform으로 정렬한 요소에는 그 정렬을 보존하는 keyframe만 적용하거나, 정렬을 margin/inset으로 옮겨 transform을 애니메이션 전용으로 비운다”를 content-harness-pipeline/AGENTS.md의 CSS 규칙에 제안 후보.

### [content-flow-state-scaffolding-regression] 콘텐츠 흐름의 상태 공유·재진입 초기화·학습 피드백이 서로 어긋남

- 대상: content-harness-pipeline/runs/2026-07-31_dfbc1027/output/index.html
- 분류 태그: content-flow-state-scaffolding-regression
- 상태: 제안됨 (5회 도달, 2026-07-31 rule 승격 제안 — 사용자 판단 대기 / 2026-08-03 10회 · 2026-08-04 15회로 재발)
- 발생 횟수: 15
- 최초 발생일: 2026-07-31
- 최근 발생일: 2026-08-04
- 사례:
  - 2026-07-31: content critique에서 무작위 C·D의 step1/step2가 서로 다른 operands를 생성하고, 도입·모양 찾기 재진입 초기화가 불완전하며, 수리 이야기 도입 질문이 즉시 숨는 문제를 지적했다. 또한 페인트 색·모양 대응 설명의 순서가 세기 문항 뒤로 밀렸고, 산술 도형의 추가·삭제가 최종 상태로만 보이며, 오답·도움말·3회 오답 이후 진행이 학습자의 다음 행동을 충분히 안내하지 못했다. 고정 진행률과 `O` 제출 라벨, 자유 그리기 `버튼` CTA도 현재 상태와 조작 의미를 명확히 전달하지 못했다.
  - 2026-07-31: 후속 content critique에서 다음 차시 대상이 주입되어도 버튼이 항상 disabled인 문제, 대부분 문항의 개념 설명·재시도 안내 부족, ①·② 대사와 페인트 추가·삭제 사건의 합침, 보수 확인과 세 수 계산이 고정 A→D 순회로 분리된 문제, 세 번째 오답 뒤 정답 위치 번호·후속 행동 부족, 목록으로 미완료 단계를 건너뛰는 문제를 지적했다. 키패드 `O`, 자유 그리기 `버튼` 라벨도 조작 의미가 불명확하다고 재차 지적했다.
  - 2026-07-31: 이번 content refine packet에서 독립 실행 환경의 `나가기` 비활성, 문항별 근거·단계형 힌트 부족과 자동 전환, 자유 그리기 완료 CTA의 의미 없는 `버튼` 라벨, 표지판별 예측 질문 단계 축약, 계산 성공과 담장 작업 진행·자유 그리기 해금의 연결 부족을 지적했다.
  - 2026-07-31: **(실사용 관측)** `production/1-2/08/index.html` 모양 찾기에서 `■모양 2개`를 다 찾았는데 다음 모양(`●`)으로 넘어가지 않고 진행이 멈춘다고 지적. 위 네 사례가 "자동 전환 제거 → 원문 표면을 직접 눌러 진행"으로 여러 번 방향을 튼 결과, `selectHotspot`이 `found.size===2`에서 `showFeedback(..., advanceSearch)`를 부르고 `showFeedback`은 `feedbackSpeech`를 눌러야만 `completeFeedback→advanceSearch`가 돌게 되어 있다(index.html:732·909). 즉 진행 조건이 "보이지 않거나 누를 수 있는지 알 수 없는 말풍선 클릭" 하나에 묶여 있어 실제로는 데드엔드로 보인다. 앞선 조치들이 만든 **수동 진행 게이트가 검증(Playwright hook)에서는 통과하지만 사람 조작에서는 막히는** 형태의 회귀다. (미조치 — `production/1-2/08/todo.md` 17번으로 등록)
  - 2026-07-31: 후속 content refine packet에서 무작위 문제 풀이 뒤 가시적인 다음 조작 부재, 모양 찾기 hotspot 밖 클릭 무반응, 세 번째 오답 자동 공개를 직접 정답처럼 처리하는 상태 혼동, 자유 그리기 최소 참여 조건·완료 장면 결과 보존 부족, 문항별 계산·관찰 근거 피드백 부족을 지적했다. `다음 문제`·`자유 그리기로 이동`·`그림 완성하기` 같은 새 가시 문구 제안은 planner 외 문구 추가 금지와 충돌하므로 기능·상태·기존 원문 표면으로 해결해야 한다.
  - 2026-08-03: **(실사용 관측 · 17번과 같은 씬에서 데드엔드 재발)** `production/1-2/08` `section_shape_find`에서 "동그라미 세모 네모 선택이 틀리면 다음으로 못 넘어간다"고 지적. headless Chrome CDP로 재현했다. 정답 2개를 다 찾으면 `selectHotspot`이 `setHotspotsEnabled(false)` 후 `showFeedback(..., advanceSearch)`로 진행 표면을 `#feedbackSpeech` **하나에만** 걸어 둔다. 그런데 `renderSearch`가 건 `searchArea.onclick`(장면 전체 오답 판정, 2026-07-31 후속 조치로 추가된 것)은 정답 이후에도 살아 있어, 사용자가 말풍선이 아닌 아무 데나 한 번 누르면 `registerSearchWrong → showWrongFeedback → resetFeedbackOverlay()`가 `feedbackContinueAction=null`로 만들고 말풍선을 지운다. 이 시점에 hotspot 6개는 전부 `disabled`라 **진행 경로가 0개인 완전한 데드엔드**가 된다(새로고침·디버그 패널 외 탈출 불가). 17번이 만든 "수동 진행 게이트"와 그 뒤 추가된 "장면 전체 오답 판정"이 서로를 무효화하는 구조다. (**조치 완료 2026-08-03** — complete.md 26번: 씬2에 `searchSolved` 가드, 전 씬 공통으로 `showWrongFeedback`에 `if(feedbackContinueAction)return` 가드. `searchArea.onclick`은 떼지 않고 게이트만 걸었다.)
  - 2026-08-03: 같은 차시 `section_free_drawing` 완료 CTA 라벨이 아직 `버튼`이라 "글이 `버튼`이 아니라 `완성하기`로 바꿔 달라"고 지적. critique가 2026-07-31에만 네 번 지적했으나 **planner 원문 보존 계약** 때문에 매번 `aria-label`만 붙이고 보이는 문구는 `버튼`으로 유지했다. 이번에 사용자가 직접 변경을 지시했으므로 production 사본에서는 원문 계약보다 사용자 지시가 우선한다. 교훈: **원문 표의 "UI 요소" 칸 값(`버튼`)을 그대로 라벨로 쓰면 원문 보존 계약이 오히려 의미 없는 라벨을 고착시킨다** — 원문의 "문구"와 "UI 요소 이름"을 구분해야 한다. (**조치 완료 2026-08-03** — complete.md 31번: 보이는 글자를 `완성하기`로 바꿨다. 사용자 지시가 원문 보존 계약보다 우선한다는 판단.)
  - 2026-08-03: **(실사용 관측)** `production/1-2/08` `section_random_problems`에서 "**정답을 맞췄는데도 힌트가 나오느라 정답 처리가 안 된다** — 힌트는 오답일 때와 누를 때만 나오는 것"이라고 지적. `#helpCard` **하나가 힌트·풀이·진행 버튼 세 역할을 겸하는** 것이 원인이다. 정답이면 `completeRandomProblem()` → `showRandomSolution()`이 같은 카드에 중간식을 넣고 `open`을 붙이고, 이어 `armRandomContinue()`가 그 카드에 `다음 ▸`를 붙인다. 오답 경로(`judgeRandomChoice`·`judgeRandomKey`)도 같은 카드를 연다. 그래서 **정답 순간 화면이 오답 때와 똑같이 보인다.** 이 겸직은 42번(힌트를 선생님 말풍선으로)과 26번(데드엔드 방지용 진행 표면 확보)이 각각 정당한 이유로 같은 요소를 고른 결과 생겼다 — **개별 조치는 옳았는데 표면이 겹쳐 상태 신호가 무너진 형태**다. 힌트를 정답 때 닫으려면 진행 표면을 함께 옮겨야 하며, 옮기지 않으면 26번 데드엔드가 재발한다. (**조치 완료 2026-08-03** — complete.md 47번: 결과·진행을 새 표면 `#randomSolved`(문제 패널 안)로 옮기고 `#helpCard`는 힌트 전용으로 남겼다. 정답 뒤 `.keypad`·`.choices`도 내린다. 진행 경로 4가지를 통째로 옮겨 26번 데드엔드는 나지 않는다.)
  - 2026-08-03: **(같은 씬 · 힌트 내용)** "힌트가 나가고 있는데 **문제를 그대로 보여주는 식**이야. 힌트를 어떻게 보여줄지도 생각해야 해"라고 지적. `renderRandom`이 만드는 `randomHint`는 유형 B가 `10 - ${c} = (   )`로 **문제와 글자까지 같고**, 유형 C·D는 첫 줄이 `${a} + ${b} = 10`이라 **10 만들기라는 답의 절반을 바로 공개**한다. 즉 힌트가 **재진술 아니면 정답 공개** 둘뿐이고 중간이 없다. 2026-07-31 critique의 "**문항별 근거·단계형 힌트 부족**" 지적이 그때는 "힌트 표면을 만들라"로만 해소되고 **내용의 단계화는 안 된 채 남아 있었다** — 표면(42번)과 진행 게이트(26번)는 여러 번 손봤는데 정작 그 안에 무엇을 담을지는 한 번도 설계되지 않았다. (**조치 완료 2026-08-03** — complete.md 53번: 힌트를 `randomHintSteps=[{text,focus}]` 단계 배열로 바꿨다. 1단계는 시선 유도(해당 항 도형만 `hint-step`), 2단계에서만 중간식. 선생님을 누를 때마다 한 단계씩 열린다.)
  - 2026-08-03: **(실사용 관측 · 씬 전환 표면)** `section_intro` 마지막 대사 `저희가 도와드릴게요!`에서 "**다음 버튼을 누르면 대화창이 사라지고 다음 섹션으로 가는 버튼이 나오는 것**이지, 다음 버튼이 사라지는 게 아니다. 다음 섹션 버튼이 나오는 다른 화면도 동일하게"라고 지적. 현재는 세 곳(`introTap.onclick` 마지막 분기 / `shapeDialogueTap.onclick`의 `shapePhase==='outro'` / `arithIntroTap.onclick`의 `arithPhase==='outro'`)이 전부 `clearAdvanceNav(대사표면)`으로 **말풍선 안의 `다음 ▸`만** 지우고 말풍선·캐릭터는 그대로 남긴 채 CTA를 띄운다. 그래서 화면에는 "끝난 대사"와 "다음 섹션 버튼"이 함께 떠 있고, 대사 표면은 이제 눌러도 아무 일이 없는 죽은 표면이 된다. **35번 조치가 만든 형태다** — 그때 "CTA가 보이면 `다음 ▸`를 뺀다"로 좁게 해결하면서 표면 자체의 생사를 정하지 않았다. 같은 차시 씬5(`drawingTap.onclick`)는 `#drawingDialogue`를 통째로 `hidden`으로 내리고 CTA를 띄워 **이미 올바른 형태**라, 같은 문서 안에서 두 방식이 공존한다. (**조치 완료 2026-08-03** — complete.md 58번: 세 자리 모두 `clearAdvanceNav` 대신 대사 표면을 통째로 `hidden`으로 내린다. 씬5 형태를 정본으로 삼았고, 참조가 0이 된 `clearAdvanceNav`는 제거했다.)
  - 2026-08-04: **(같은 씬 · 힌트 타이밍)** "무작위 계산 문제에서 **틀렸을 때 바로 힌트를 말해주지 말아 달라**"고 지적. `judgeRandomChoice`·`judgeRandomKey`의 오답 분기가 `openRandomHint(randomWrong-1)`을 불러 **학습자가 요청하지 않았는데** 말풍선이 열린다(1회 오답 → 1단계, 2회 → 2단계). 53번이 힌트 **내용**을 단계화하면서 그 단계를 오답 횟수에 자동으로 매단 것이 원인이다 — 42-a·b가 "선생님을 눌러 힌트를 받는다"는 요청형 경로를 세워 놓고, 오답 경로가 그 앞을 질러가 **스스로 다시 풀어 볼 구간을 없앴다.** 표면(42)·게이트(26)·내용(53)을 차례로 고쳤는데 **언제 여는가**는 한 번도 정하지 않은 채 남아 있었다. (**조치 완료 2026-08-04** — `production/1-2/08/complete.md` 68번: 오답 분기에서 `openRandomHint` 호출 제거. 사용자 결정으로 도형 깜빡임도 함께 뺐다 — 힌트는 선생님을 눌렀을 때만 나온다. 3회 오답 정답 공개는 씬2·3과 같은 안전망이라 유지.)
  - 2026-08-04: **(같은 씬 · 정답 표면)** "무작위 계산 문제에서도 정답이 되었을 때 **다른 문제들과 똑같이 도장 + 다음 버튼**으로 가자. 정답 보기와 다음 버튼을 만드는 게 아니라"고 지적. 씬2·3은 전부 `showFeedback(mark,'정답입니다.',advance,'correct-1')` 한 줄로 **도장 유지 + `#narrationAdvance`의 `다음 ▸`** 인데, 씬4만 `showFeedback(mark,'')`(도장 700ms 뒤 사라짐) + `armRandomContinue`가 `#randomSolved` 판에 풀이식과 버튼을 그리는 **별도 경로**였다. **47번 조치의 부작용**이다 — `#helpCard` 겸직을 풀려고 새 표면을 만들면서 "이미 있는 표준 표면(`#narrationAdvance`)을 쓴다"는 선택지를 보지 않았다. 같은 역할(정답 신호 + 진행)에 표면이 두 벌 생겨 씬마다 정답 화면이 다르게 보인다. (**조치 완료 2026-08-04** — `production/1-2/08/complete.md` 75번: 씬4도 표준 경로로 통일하고 `#randomSolved`를 제거했다.)
  - 2026-08-04: **(바로 위 조치에 대한 교정 — 표면은 통일했는데 자리를 안 통일함)** "**다음 버튼이 다른 곳들과 같이 도장 아래에 있어야지**"라고 지적. 75번에서 표준 표면(`#narrationAdvance`)으로 옮기면서 **자리만 씬4 전용**(`.on-random`, 문제 패널 가운데)으로 줬다. 기본 좌표가 도형 박스와 56×23 겹치는 것을 피하려던 판단이었는데, **"표준 표면을 쓴다"의 알맹이는 학습자가 보는 관계(도장 바로 아래)** 이지 요소 이름이 아니다. 도구만 통일하고 관계는 안 통일하면 사용자에게는 여전히 "씬마다 다른 화면"이다. **겹침 회피가 일관성보다 앞선 것**이 판단 착오다 — 도장은 이미 같은 방식으로 도형을 덮고 있었고 씬2·3도 그랬으므로, 겹침은 애초에 이 씬만의 문제가 아니었다. (**조치 완료 2026-08-04** — `production/1-2/08/complete.md` 78번: `.on-random`을 규칙·클래스 부착·제거까지 통째로 걷고 공용 기본값만 쓴다. 남는 겹침은 알고 남겼다.)
  - 2026-08-04: **(같은 씬 · 3회 오답 안전망)** "무작위 계산 문제에서 다른 문제들과 다르게 **3번 오답이 나오면 X 도장 뒤에 O 도장까지 나온다**"고 지적. `revealRandomAnswer`가 `answer-reveal`를 걸고 `setTimeout(()=>showStamp(randomMark,'correct'),ANSWER_STAMP_DELAY_MS=160)`으로 **정답 도장을 함께 냈다.** `showStamp`은 씬마다 `.feedback-mark` 한 장(`#randomMark`)의 `src`를 갈아 끼우므로, 방금 `showWrongFeedback`이 낸 X 도장을 0.16초 뒤 O 도장이 덮어 **"틀렸다 → 맞았다"로 읽힌다.** 씬2·3의 같은 분기(`countWrong>=3`·`arithWrong>=3`)는 `answer-reveal` 클래스만 걸고 도장을 내지 않는다 — **씬4만 다르다.** 바로 위 사례(정답 표면 통일)와 같은 뿌리다: 씬4의 판정·공개 경로가 표준 경로에서 갈라져 있고, 이번에는 그 차이가 **판정 신호 자체를 뒤집는** 데까지 갔다. 3회 오답 공개는 **판정이 아니라 안전망**인데 정답 판정 신호를 붙였다. (**조치 완료 2026-08-04** — `production/1-2/08/complete.md` 76번)
  - 2026-08-04: **(같은 씬 · 힌트 내용 — 53번 조치에 대한 교정)** "무작위 계산 문제에서 **힌트가 너무 중구난방**이다. 10이 되는 덧셈식(A)은 이어지니까 괜찮은데, 세 수의 덧셈(C)은 `두 수를 더해 10을 만들어 보세요` 다음 힌트가 `2+8=10`이면 이상하다. 차라리 `10에 나머지 수를 더해 보세요`가 낫다"고 지적. 53번이 힌트를 2단계로 쪼개면서 **단계의 형식을 유형마다 다르게** 만든 것이 원인이다 — A는 `세기 → 질문`, B는 `세기 → 세기`, C·D는 `지시 → 완성된 식`이다. C·D의 2단계 `{a} + {b} = 10`은 (a) 1단계가 시킨 일의 **답을 되풀이할 뿐 앞으로 못 가고**, (b) 남은 `+ c`는 두 단계 어디에서도 말하지 않으며, (c) 반짝이는 도형은 `c`(빨강 ▲)인데 글자는 `a+b` 얘기라 **글자와 그림이 서로 다른 항을 가리킨다.** 53번은 "재진술 아니면 정답 공개"라는 **양 끝**은 고쳤지만 **단계 사이의 관계(1단계가 2단계의 재료가 되는가)** 는 정하지 않은 채 남겨 뒀다. (**조치 완료 2026-08-04** — `production/1-2/08/complete.md` 79번: 4유형 전부를 `1단계=재료 만들기(답 없음) → 2단계=그 재료로 남은 한 걸음`이라는 같은 골격으로 다시 씀. 완성된 식은 힌트에 쓰지 않고, 글자가 말하는 항과 반짝이는 도형을 일치시켰다.)
- 조치: **2026-07-31 수정·검증 완료.** 무작위 C·D는 문제 묶음별 operand 객체를 만들어 step1/step2가 같은 수를 공유하게 했고, 도입·모양 찾기는 재진입 때 배경·캐릭터 위치/pose·대사 index·숨김 상태·CTA·입력·타이머를 초기화한다. 모양 찾기 뒤 `페인트 색깔마다 모양이 달라요`→`● ■ ▲ 모양`을 먼저 순차 노출한 다음 세기 문항을 시작하도록 storyboard 순서를 복원했다. 산술 튜토리얼은 10개 등장, 7→3 추가, 10→2 추가, 12→2 삭제→3 삭제를 DOM 상태 변화로 순차 실행하고 애니메이션이 끝날 때까지 키패드를 disabled로 둔다. 세기·산술·무작위 문항은 오답 때 현재 도형/operand를 강조하고, 3회 오답 뒤 정답을 표시하되 기존 `O` 조작으로 직접 확인해야 다음 문항으로 넘어가게 했다. 제작자용 생성 규칙 도움말은 현재 operands의 중간식으로 교체했고, 상단 게이지를 문항마다 갱신한다. 자유 그리기는 도형이 1개 이상 놓이기 전 완료 CTA를 disabled로 유지하며, 수리 이야기는 제목·`모양을 길에서 본 적이 있나요?`를 첫 beat로 실제 노출한 뒤 표지판을 연다. 원문 보존 계약 때문에 critique가 제안한 `확인`·`그림 완성하기` 같은 새 라벨은 적용하지 않고 기존 `O`·`버튼` 원문을 유지했다. 검증: planner rendered_text·문항·보기 100개 누락 0, JS 구문·중복 DOM id·asset·QA scene·고정 캔버스 계약 정상. Playwright에서 intro/shape 재진입 reset, 페인트 설명 선행, 산술 입력 잠금·순차 변화, C·D operand 공유, 세 종류 3회 오답→정답 확인, 빈 그리기 완료 차단, 수리 이야기 첫 beat를 확인했고 console/page 오류는 0건이었다. Visual QA 캡처 8장도 broken image·overflow·text clipping·overlap 0건이며, 자동 REJECT 한 건은 공통 계약상 필수인 `#viewport {position:fixed; inset:0}`를 100% fixed overlay로 오인한 기존 휴리스틱 false positive다.
  - 2026-07-31 후속 조치: 다음 차시 버튼은 `nextLessonUrl`·`onNextLesson` 존재를 초기화·완료 진입·호스트 갱신 이벤트·주기 동기화에서 다시 검사해 활성화하고, 종료 수단이 없으면 나가기 버튼을 비활성화한 채 완료 화면을 유지한다. 목록은 실제로 해제된 단계만 이동 가능하게 했다. 도입과 산술의 ①·② 대사, 페인트 추가·담장 이동·삭제 사건을 독립 beat로 분리해 각 확인 뒤에만 도형 모션과 문항을 연다. 무작위 문제는 런타임에서 A→같은 A·B를 쓰는 C 또는 B→같은 C를 쓰는 D 묶음 하나를 선택하고, 정답·세 번째 오답 뒤에는 중간값 10 식을 보여 준 뒤 자동 진행한다. 모양 찾기 세 번째 오답에는 두 정답 위치 번호를 표시하며, 키패드 강제 공개도 자동 진행으로 통일했다. 보이는 `O`·`버튼`은 공통 원문 계약 때문에 그대로 두고 각각 `확인`·`그림 완성하기` 접근성 라벨을 추가했으며, 자유 그리기 도형·색 `aria-pressed`를 상태와 동기화했다. 효과음과 대사·문항·안전 이야기 내레이션은 모두 소리 조절 상태를 따른다. 검증: planner 텍스트 127개(고유 102개) 누락 0, JS 구문·중복 DOM id·asset·8개 QA scene·고정 캔버스 계약 정상. Playwright에서 host route 활성화, 메뉴 잠금, 산술 독립 beat, 모양 정답 번호, 연결된 무작위 A→C operands를 확인했고 page error는 없었다.
  - 2026-07-31 이번 조치: `나가기`는 호스트 callback·부모 frame·opener를 우선 사용하고 독립 실행에서는 차시 시작 화면으로 돌아가는 fallback을 연결해 항상 활성화했다. 모양 찾기는 오답 2회에 정답 윤곽, 3회에 위치 번호와 정답 피드백을 공개하고, 모양 찾기·세기·산술·무작위 문제는 정답/자동 정답 뒤 원문 피드백 또는 중간식을 직접 눌러야 다음 문항으로 진행하도록 자동 전환을 제거했다. 무작위 문제 하단에는 기존 도형 asset 3개로 담장 작업 진행을 표시해 계산 성공과 자유 그리기 해금을 연결했다. 수리 이야기는 원·사각형·삼각형마다 `무슨 표지판일까요?` 예측 beat를 거친 뒤 설명을 공개한다. 자유 그리기 확인에는 사용한 도형·색 조합을 텍스트 추가 없이 asset 표본으로 요약한다. critique의 보이는 `그림 완성하기` 라벨은 planner에 없는 문구를 새로 노출하지 못하는 공통 원문 계약이 우선하므로 기존 `버튼`을 유지하고 이미 있던 `aria-label="그림 완성하기"`를 보존했다. 검증: planner rendered_text·문항·보기·정답·피드백 고유 102개 누락 0, JS 구문·중복 DOM id·asset 34개·8개 QA scene 정상. Playwright에서 대사 표면 진행, 피드백 수동 진행, 무작위 3단계 담장 진행과 수동 전환, 자유 그리기 요약, 표지판 예측 3회, 독립 실행 나가기 fallback을 확인했고 console/page 오류는 0건이었다. Visual QA는 broken image·overflow·text clipping·overlap 0건이며, REJECT는 고정 캔버스 계약의 필수 `#viewport`를 fixed overlay로 오인한 기존 false positive 한 건뿐이다.
  - 2026-07-31 후속 content refine 조치: 모양 찾기 장면 전체를 오답 판정 영역으로 연결하고 hotspot 밖 클릭도 기존 오답 횟수·도장·힌트에 반영했다. 세 번째 오답은 정답으로 완료시키지 않고 정답 위치·숫자 또는 입력값만 공개한 뒤 학습자가 정답 hotspot을 직접 선택하거나 기존 `O`를 눌러 확인해야 진행하도록 모양 찾기·세기·산술·무작위 문항을 통일했다. 무작위 풀이 표면에는 원문 밖 문구를 추가하지 않고 기존 풀이를 유지한 채 진행점을 표시하고 초점을 이동해 다음 조작 affordance를 보강했다. 자유 그리기는 도형 3개 이상·도형 종류 2개 이상·색 2개 이상의 명시적 완료 검사로 바꾸고, 배치 상태를 완료 장면의 담장 위에 그대로 복원했다. planner 밖 가시 문구를 추가할 수 없어 `다음 문제`·`자유 그리기로 이동`·`그림 완성하기` 제안은 적용하지 않았고 기존 `aria-label`과 원문 `버튼`을 유지했다. 검증: planner 원문·문항·보기·정답·피드백 고유 102개 누락 0, JS 구문·중복 DOM id·asset 참조 정상. Playwright에서 배경 오답 3회→정답 직접 선택, 세기·산술·무작위 자동 공개→기존 확인 조작, 자유 그리기 최소 조건과 완료 장면 3개 결과 복원을 확인했고 page error는 없었다.
- 규칙화 메모: **15회 → rule 재검토 제안(2026-08-04).** 새 1건은 초안에 다음을 더한다. **단계형 힌트는 단계마다 형식이 아니라 관계를 맞춘다** — `1단계 = 재료 만들기(답을 담지 않음)`, `2단계 = 그 재료를 받아 남은 한 걸음`. 완성된 식(`2+8=10`)은 힌트가 아니라 답의 절반이고, 앞 단계가 시킨 일의 되풀이라 사슬이 끊긴다. 같은 씬의 유형들은 **같은 골격**을 쓴다(유형마다 사고 단계가 달라지면 학습자가 "누르면 무엇이 나오는지"를 예측할 수 없다). 글자가 말하는 항과 강조하는 그림은 반드시 같은 것을 가리킨다.
- 규칙화 메모(14회 시점): **14회 → rule 재검토 제안(2026-08-04).** 아래 "같은 역할의 표면은 표준을 쓴다" 조항에 **자리까지 표준이어야 한다**를 덧붙인다 — 표준 표면을 골라 놓고 씬별 좌표를 주면 학습자에게는 여전히 씬마다 다른 화면이다. **겹침 회피는 일관성보다 뒤에 둔다**(정답 오버레이는 원래 콘텐츠를 덮는 물건이다).
- 규칙화 메모(12회 시점): **12회 → rule 재검토 제안(2026-08-04).** 새 2건은 초안에 다음 둘을 더한다.
  - **힌트는 학습자가 요청할 때만 연다.** 오답은 판정(도장·소리·흔들림)까지만 내고, 힌트 표면을 자동으로 열지 않는다. 요청형 힌트 경로를 만들어 놓고 오답 경로가 그 앞을 질러가면 요청 경로는 있으나 마나가 된다. 안전망(3회 오답 정답 공개)은 별개로 둔다.
  - **같은 역할의 표면은 씬마다 새로 만들지 말고 이미 있는 표준 표면을 쓴다.** 47번처럼 겸직을 푸는 과정에서 새 표면을 만들면 역할이 같은 표면이 두 벌 생기고, 학습자에게는 "같은 정답인데 씬마다 다른 화면"으로 보인다. 새 표면을 만들기 전에 **기존 표준 경로(`showFeedback` + `#narrationAdvance`)로 되는지 먼저 확인**한다.
- 규칙화 메모(5회 시점): **5회 도달 → rule 승격 제안(2026-07-31, 사용자 승인 대기).** 초안: “다단계 문항은 operands를 문제 묶음 상태로 공유하고, 모든 scene 재진입 시 DOM·배경·캐릭터·입력·타이머를 초기화한다. **문항에서 다음 단계로 넘어가는 경로는 항상 하나 이상 사람이 볼 수 있는 표면(가시·활성·포커스 가능)이어야 하며, 자동 전환을 제거할 때는 그 자리를 대신할 표면이 실제로 보이고 눌리는지 사람 조작 기준으로 확인한다.** Playwright hook 통과는 진행 가능의 근거가 아니다.” 반영 위치: `content-harness-pipeline/AGENTS.md`. 5회 중 4회는 파이프라인 critique, 5번째는 실사용 데드엔드 관측이라 **critique 루프가 못 잡는 층위**임이 드러났다.


### [cross-lesson-shell-inconsistency] 같은 학기 차시인데 공통 화면(상단 헤더·타이틀 화면) 양식이 차시마다 달라짐

- 대상: production/1-2/08/index.html (기준: production/1-2/01/index.html)
- 분류 태그: cross-lesson-shell-inconsistency
- 상태: 제안됨 (6회 — rule 승격 제안, 승인 대기)
- 발생 횟수: 6
- 최초 발생일: 2026-07-31
- 최근 발생일: 2026-08-04
- 사례:
  - 2026-07-31: 1-2/08의 헤더가 1-2/01과 전혀 다른 양식(이미지 프레임 HUD, 164x68 목록/소리 버튼, 3단계 chip, 전폭 progress track, 146px 높이)이라 1-2/01의 topbar 양식과 똑같이 맞추라고 지적했다. 파이프라인이 차시마다 공통 shell을 새로 설계해 차시 간 UI 연속성이 깨진다.
  - 2026-07-31: 타이틀 화면도 같은 일이 반복됐다. "01을 참고해서" 타이틀 로고를 가운데 이미지로 두라는 요청에 대해, 01의 `#introStartWrap` 구조를 가져오지 않고 08 기존 좌표계로 비슷하게만 만들었다. 사용자가 "css도 그렇고 크기도 그렇고 색감도 그렇고 글꼴도" 다르다고 지적. 실측 차이 — (a) 01은 `#app.title-mode .topbar{opacity:0}`으로 타이틀 화면에서 헤더를 숨기는데 08은 노출, (b) 01은 로고+시작버튼을 `#introStartWrap` 한 덩어리로 `top:50%` 중앙 배치하는데 08은 로고 `top:297px` / 버튼 `bottom:70px`로 분리, (c) 시작 버튼 폭이 01은 화면폭 28.6%(390/1366)·28px인데 08은 21.9%(420/1920)·34px, (d) 버튼 색이 01은 `#fff46d→#ffc72f→#ff8f18` 금색 그라데이션 + `#113d78` 테두리/글자인데 08은 흰/크림 스프라이트(`cta-intro-body.png`), (e) 서체가 01 `Noto Sans KR` vs 08 `Malgun Gothic`, (f) 01의 `titleLogoDrop` 로고 낙하 애니메이션 누락.
  - 2026-07-31: 세 번째 반복. (a) 08의 말풍선(`.speech`)이 씬마다 고정 좌표·고정 크기라 대사 길이가 달라도 박스가 그대로여서 글자 수에 따라 크기가 늘고 줄어야 한다는 지적, (b) 01에는 음소거 버튼과 다음(진행) 버튼이 공통 UI로 있는데 08에는 없으니 **01에서 가져와 쓰라**는 지시. 앞선 두 사례(헤더·타이틀 화면)와 같은 패턴이 조작 UI 층위에서 또 나왔다 — 차시별로 진행/소리 조작을 각자 만들어 두면 같은 코스인데 조작법이 차시마다 달라진다.
  - 2026-08-04: 네 번째 반복. **마우스 포인터**다. 08은 OS 기본 화살표를 그대로 쓰는데 01에는 초등학생이 볼 수 있는 큰 이미지 커서(`#cursor` + `assets/ui/mouse-pointer.webp`, `*{cursor:none}`)가 있다. 사용자가 "이렇게 바꿀 건데 새로 만들까 가져올까"라고 물어 왔다. `production/1-2/08/CLAUDE.md:75` 표에 이미 "커서 = 01의 `mouse-pointer.webp`"로 기준이 적혀 있었는데도 08에 없던 항목이다 — **표에 기준을 적어 두는 것만으로는 이식이 일어나지 않는다**는 것이 이번 사례의 새 정보다. 앞선 3회(헤더·타이틀·조작 UI)는 "비슷하게 새로 만들었다"였고 이번은 "아예 없다"에 해당한다.
  - 2026-08-04: 다섯 번째 반복. **차시 목록 드로어가 01보다 크다**고 지적("목록이 01과 똑같아야 하는데 너무 큰 것 같다"). 앞선 4회와 층위가 다르다 — **이식은 했는데 배율을 잘못 곱한 것**이다. 08은 01의 드로어 값을 전부 ×1.4056(1920/1366) 해서 넣었는데(패널 400 → 562px 등), 01의 드로어는 `min(400px,40cqw)`·`clamp(...,20px)`처럼 **절대 px 캡에 걸려 있어 스테이지 크기와 무관하게 400px로 고정**된다. 반면 08의 `#stage`는 1920×1080 고정 후 `transform:scale`로 화면에 맞춘다. 그래서 ×1.4056을 곱한 값이 화면에서는 01의 **1.28배**로 그려졌다(실측: 패널 400 vs 512.6, 항목 높이 51.8 vs 73, 번호 배지 34 vs 43.8). **88번(커서)이 "스테이지 밖 요소라 배율을 곱하지 않는다"고 정확히 판단했던 것과 같은 함정을, 스테이지 *안*에 있지만 값이 절대 px로 캡된 요소에서 반대로 틀린 것이다.**
  - 2026-08-04: 여섯 번째 반복. **키 누름 효과음**이다. 01은 키패드를 누를 때마다 `playButtonSelectSfx()`로 소리를 내는데 08은 무음이라, 사용자가 "01에서 사용되는 다이얼 누르는 효과음도 가져와서 08에 사용해 달라"고 요청했다. 4회차(커서)와 같은 "**기준 차시에만 있고 대상 차시에 없다**"이고, 이번에 새로 나온 정보는 **그 공통 UI가 에셋 파일이 아니라 코드에 있을 수 있다**는 것이다 — 01의 `playSfx`는 `playSynthSfx`를 먼저 부르고 `SFX_SYNTH_MAP`에 `'button-select':'tick'`이 있어 **Web Audio 합성음**이 나간다. `01/assets/audio/sfx/button-select.mp3`는 Web Audio가 없을 때만 쓰이는 폴백이라 **에셋만 복사했으면 01에서 실제로 들리는 소리와 다른 소리가 났다.** (`keypad.mp3`도 이름과 달리 키 누름 소리가 아니라 수 표시 틱이다 — 파일명으로 고르면 틀린다.)
- 조치(1회차): 1-2/01 topbar의 실제 CSS/DOM 값을 그대로 이식했다. 구조는 `.topbar`(56px, 크림 유리 그라디언트, 하단 보더) > `.topbar-left`(`.btn-home` + `.header-voice-volume-button` + `.step-label`) / 중앙 절대배치 `.lesson-header-title`(금색 밑줄) / 우측 `.lesson-bar-reward`(track+fill+`%`)로 통일했다. 내용은 planner/input에서 가져왔다 — 제목은 `알록달록, 학교 담장 색칠하기`, step-label은 1-2/01의 stageLabels 사다리에 맞춰 `수리력 +`·`수리가 필요해요 1`·`수리가 필요해요 2`·`수리로 해결해요`·`수리 이야기`로 sceneMeta에 매핑, 진행률은 기존 `setProgress()` 호출을 그대로 lesson-bar에 연결했다. 좌상단 버튼은 1-2/01의 실제 런타임 형태인 햄버거 아이콘 + `목록` 라벨(`.course-menu-btn`)로 맞췄고, 글자 서체도 1-2/01과 같은 Noto Sans KR을 `--font-topbar`로 topbar에만 적용했다(로드 실패 시 기존 `--font-body`로 폴백). 1-2/01에 없는 3단계 chip과 `assets/global-hud-frame.png` 프레임은 제거했다(파일은 삭제하지 않고 남겨 둠). 검증: node --check로 inline JS 구문 정상. 1-2/01(title-mode topbar 숨김만 해제한 사본)과 1-2/08을 각각 로컬 HTTP로 띄워 headless Chrome 1920x1080으로 캡처하고 상단 60px를 나란히 비교해 버튼·구분선·중앙 제목·금색 밑줄·우측 진행 pill이 같은 위치·크기·서체로 렌더되는 것을 확인했다.
- 조치(2회차): 01의 `#introStartWrap` / `.intro-title-copy` / `.intro-start-cta` / `titleLogoDrop` / `ctapulse` / `shimmer` / `title-mode`를 같은 이름으로 이식하고 값은 1920 배율(×1.4056)로 환산했다. **여기서 한 번 더 틀렸다 — 01의 CSS를 소스 순서로 읽어 `#introStartWrap .intro-start-cta`(네이비+금색)를 이식했는데, 이는 뒤쪽 `#app .cta,#app #introStartWrap .intro-start-cta`에 덮인 죽은 규칙이었다.** `getComputedStyle` 실측으로 실제 값(앰버 pill `#fef08a→#ca8a04`, `border-radius:999px`, 글자 `Jua` 27px `#713f12`)을 다시 읽어 교정했다. 서체도 같은 함정 — 01은 Noto Sans KR을 선언한 뒤 아래에서 `html,body,button{font-family:"Jua",...}`로 덮는다. 사용자 승인으로 08도 `--font-body`를 Jua 스택으로 전역 교체했다. 타이틀 이미지 아트 자체(색감·글자 형태)가 01 로고와 다른 건 CSS로 불가 — 사용자가 현재 이미지 유지 결정.
- 조치(4회차): 01의 `#cursor` / `.cursor-image` / `.big` / `.readable-hover`를 같은 이름으로 이식했다. 값은 `tmp/probe-cursor-01.js`의 `getComputedStyle` 실측(44px / `.big` 55px / `translate(-5%,-4%)` / opacity .96·hover .94 / 2겹 drop-shadow)이고, **스테이지 배율 ×1.4056을 곱하지 않았다** — `#cursor`는 `position:fixed`라 스테이지가 아니라 뷰포트 px이고, 01·08 모두 스테이지를 화면에 꽉 채우므로 실제 화면상 크기가 이미 같다. 에셋은 새로 만들지 않고 `01/assets/ui/mouse-pointer.webp`를 그대로 복사했다(08은 평면 구조라 `08/assets/mouse-pointer.webp`). 안 가져온 것 둘: `.cspark`(클릭 반짝이)는 01에서 이미 `display:none!important`로 꺼져 있어 죽은 코드고, `#drawingCanvas`·`#shapeSearch`의 `cursor:crosshair`는 `*{cursor:none}`에 덮여 사라지는데 **사용자가 조준선은 없어도 된다고 결정**(2026-08-04)해 그대로 뒀다. 상세는 `production/1-2/08/todo.md`·`complete.md` 88번.
- 조치(5회차): 08의 `.course-menu-*` 치수를 **01의 선언을 그대로**(clamp+컨테이너 단위 식까지 그대로) 되돌렸다. 08의 `#stage`가 `1920px × 1080px` 고정 `container-type:size`라 `cqw`/`cqh`가 상수(19.2 / 10.8)로 풀리므로, 01의 `clamp()` 식이 01의 설계 해상도(1920×1080)에서와 **같은 값**으로 resolve된다. 처음에 clamp를 정수 px로 반올림했더니 항목 pitch가 59 → 60px으로 1px씩 밀려(캡처 픽셀 비교로 발견) 식을 그대로 쓰는 쪽으로 바꿨다. 검증: `tmp/measure-drawer-01-vs-08.js`(rect 실측) + `tmp/shot-drawer.js` 캡처의 픽셀 대조 — 패널 오른쪽 경계 x=397 동일, 항목 전이 y 좌표열 동일. 상세는 `production/1-2/08/complete.md` 93번.
- 조치(6회차): 에셋을 복사하지 않고 01의 `ensureSynthCtx` / `synthTone` / `SFX_SYNTH.tick` / `playButtonSelectSfx`를 같은 이름으로 이식하고 `buildKeypad`의 `onclick`에 걸어 세 키패드 전부에 붙였다. 상세는 `production/1-2/08/complete.md` 95번.
  - 같은 대화에서 범위가 **진행 표면까지** 넓어졌다(횟수는 올리지 않는다 — 같은 피드백 줄기다). 01의 `.repair-narr-next`도 `playButtonSelectSfx()`를 부르므로 08의 대사·beat 진행 표면 7곳에 같은 소리를 넣었고, 사용자 지시로 **씬 전환에는 인트로 `시작하기`와 같은 `intro-start.mp3`** 를 내는 `goScene()` 래퍼를 뒀다. 상세는 `production/1-2/08/complete.md` 96번.
- 규칙화 메모: **6회 — rule 승격 제안(승인 대기).** 반복되면 `content-harness-pipeline/AGENTS.md`에 "차시 공통 화면(상단 헤더/타이틀 화면/진행 표시/목록·소리 조작/대사 진행 버튼)은 차시마다 새로 설계하지 않고, 기준 차시의 클래스명·수치를 `getComputedStyle` 실측으로 읽어 스테이지 배율만 환산해 그대로 이식한다"는 rule 승격을 제안한다. 2회차 관찰로 범위를 '상단 헤더'에서 '공통 화면 전반'으로, 3회차 관찰로 '조작 UI(소리·다음)'까지 넓혔다 — 근본 패턴은 "기준 차시를 참고하라고 했을 때 실제 값을 읽지 않고 비슷하게 새로 만들거나, 아예 안 만드는 것"이다. 4회차로 '포인터·커서 같은 입력 표시 층'까지 넓히고, rule 초안에 **"기준 차시에만 있고 대상 차시에 없는 공통 UI를 목록으로 만들어 착수 전에 확인한다"** 는 조항을 더한다 — 4회차는 08/CLAUDE.md 표에 기준이 이미 적혀 있었는데도 이식이 누락된 사례라, 값 이식 방법만 규정해서는 못 막는다. 연관 [[port-styles-via-computed-style]].
  - **5회차로 초안에 배율 조항을 더한다.** 지금 초안의 "스테이지 배율만 환산해 그대로 이식한다"는 문구가 이번 실패를 직접 유발했다 — 배율은 **무조건 곱하는 것이 아니라 기준 차시에서 그 값이 무엇에 묶여 있는지에 따라 갈린다**. (a) 기준 차시에서 스테이지 비율(%, vw, 무대 좌표)로 잡힌 값 → 배율 환산한다. (b) **절대 px 캡(`min(400px,...)`, `clamp()`의 max)이나 뷰포트 px(`position:fixed`)로 잡혀 스테이지 크기와 무관하게 고정되는 값 → 곱하지 않고 그대로 옮긴다.** 판정은 기억이 아니라 **두 차시를 같은 창 크기로 띄워 렌더된 px을 나란히 재서** 한다(88번은 이 판정을 맞게, 이번은 틀리게 했다).
  - **6회차로 초안에 "무엇을 옮길 것인가" 조항을 더한다.** 공통 UI를 이식할 때 **기준 차시에서 그 효과가 실제로 어느 경로로 나오는지 호출부에서 역추적한다** — 에셋 폴더에 그럴듯한 이름의 파일이 있어도 런타임이 그 파일을 안 쓸 수 있다(01의 키 누름 소리는 mp3가 아니라 Web Audio 합성음이고, `button-select.mp3`는 폴백·`keypad.mp3`는 아예 다른 용도다). **파일명으로 고르지 않는다.**
  - 08처럼 스테이지가 고정 크기 컨테이너(`container-type:size`)이면 **기준 차시의 `clamp()`·컨테이너 단위 식을 그대로 복사하는 것이 가장 안전하다.** 손으로 푼 뒤 반올림하면 1px씩 어긋난다.

### [overlay-occludes-bg-subject] 오버레이(타이틀 이미지)가 배경 아트의 핵심 피사체를 가림

- 대상: production/1-2/08/index.html `#introTitleSurface` (`assets/colorful-school-wall-title.png`), `#shapeTitleImage` (`assets/title-shape-find.webp`)
- 분류 태그: overlay-occludes-bg-subject
- 상태: 열림
- 발생 횟수: 2
- 최초 발생일: 2026-07-31
- 최근 발생일: 2026-08-04
- 사례:
  - 2026-07-31: 도입 장면 타이틀 이미지가 배경의 학교 담장(무너진 구간 포함) 위에 겹쳐 얹혀 있어, 이 차시의 핵심 피사체인 담장을 가린다고 지적했다. 위로 올려 담장을 가리지 않게 요청.
  - 2026-08-04: 씬2에서 배경이 교실 → 담장으로 넘어가면 `모양 찾기와 세기` 제목 이미지가 좌측으로 치우쳐 있어 도형을 가린다고 지적. 배경이 넘어갔을 때만 중앙 위쪽에 두라고 요청. **1번째 사례와 원인 층위가 다르다** — 그쪽은 처음부터 잘못 놓은 좌표였고, 이번은 **한 씬 안에서 배경이 바뀌는데 오버레이 좌표는 첫 배경에 맞춰 굳어 있는 것**이다. 상세·조치는 `production/1-2/08/complete.md` 64번.
- 조치: 배경 `school-wall-damaged.png`(1672x941, cover 배율 1.148)에서 담장 기둥 윗면이 stage 좌표 y≈550인 것을 캡처 픽셀 스캔으로 확인했다. 타이틀 에셋은 알파 bbox가 y 100~758/824라 폭 1068px로 그리면 높이 461px 중 실제 그림이 박스 상단 +56~+424에만 있다. 도입 화면은 작업 도중 01의 `#introStartWrap`(타이틀+시작 버튼 세로 컬럼, `top:50%`+`translate:0 -50%`) 구조로 교체되었고, 그 정중앙 배치에서는 그림이 y 305~673을 차지해 담장을 덮었다. 01 규칙은 그대로 두고 씬 스코프 오버라이드 `#section_intro #introStartWrap{translate:0 calc(-50% - 140px)}`만 더해 그림을 y 165~533으로 올렸다(명시도 id 2개 > id 1개라 `!important` 불필요). 시작 버튼도 컬럼째 올라가 바리케이드·콘과 겹치던 위치에서 담장의 깨끗한 면 위로 옮겨졌다. 검증: headless Chrome 1920x1080에서 도입 장면을 캡처해 담장 전체·무너진 구간·벽돌 더미·콘·바리케이드가 모두 드러나고 타이틀이 상단 헤더와 겹치지 않는 것을 확인했다.
- 규칙화 메모: 2회. 5회에 못 미쳐 승격은 아직 제안하지 않는다. 반복되면 `content-harness-pipeline/AGENTS.md`에 "장면 오버레이(타이틀/배너/패널)는 배경 아트의 학습 주제 피사체 위에 얹지 않고 하늘·여백 등 빈 영역에 배치하며, 배치 전 배경의 피사체 경계를 확인한다. **한 씬 안에서 배경이 바뀌면 그 배경에 맞춘 오버레이 좌표를 배경과 같은 시점에 함께 바꾼다**"는 rule 승격을 제안한다. 연관 [bg-anchor-alignment](배경 아트 자리와 요소가 안 맞음 — 같은 "배경 기준 좌표" 계열), [element-reveal-vs-bg-transition](배경 전환 시점과 요소 상태가 어긋남 — 이번 2번째 사례와 **같은 전환 시점 누락** 구조다).

### [speech-bubble-fixed-box-not-content-sized] 말풍선이 고정 좌표·고정 크기라 대사 길이에 맞춰 늘고 줄지 않음

- 대상: production/1-2/08/index.html (`.speech` — `#introSpeech`·`#shapeSpeech`·`#arithSpeech`·`#arithContext`·`#drawingSpeech`·`#feedbackSpeech` 공유)
- 분류 태그: speech-bubble-fixed-box-not-content-sized
- 상태: 열림
- 발생 횟수: 1
- 최초 발생일: 2026-07-31
- 최근 발생일: 2026-07-31
- 사례:
  - 2026-07-31: "말풍선의 위치가 고정되어 있고 글자 수에 따라 크기를 조정해 주면 좋겠다"고 지적. 대사 길이가 씬마다 크게 다른데(한 줄짜리 피드백 ~ 세 줄짜리 도입 대사) 박스 크기가 같아, 짧은 대사에서는 빈 공간이 남고 긴 대사에서는 빽빽해진다.
- 조치: (미조치 — `production/1-2/08/todo.md` 15번으로 등록)
- 규칙화 메모: 아직 1회. `production/1-2/08/todo.md`의 "항목 간 의존 관계"에 이미 "씬별 패딩 보정을 다시 넣으면 높이 자동 조정이 깨진다"고 적혀 있어, **씬별 하드코딩이 자동 크기를 죽이는 구조**가 알려진 상태다. 반복되면 "대사·피드백 표면은 폭/높이를 고정하지 말고 내용 기준(`width:max-content`+`max-width`, 높이 auto)으로 잡고, 위치는 앵커(캐릭터 기준 꼬리)로만 고정한다"를 `prompts/common_html_contract.md`에 제안 후보. 연관 [label-text-wrapping](같은 "텍스트 길이 변화를 표면이 못 따라감" 계열), [cross-lesson-shell-inconsistency](이번 피드백에 함께 온 공통 UI 이식 요구).

### [object-placement-implausible] 찾기·탐색 장면의 사물이 현실에 없을 법한 위치·종류로 배치됨

- 대상: production/1-2/08/index.html (`findObjects` — `classroom-shape-search.png` 위 6종 사물, `.classroom-student`)
- 분류 태그: object-placement-implausible
- 상태: 열림
- 발생 횟수: 3
- 최초 발생일: 2026-07-31
- 최근 발생일: 2026-08-03
- 사례:
  - 2026-07-31: 모양 찾기에서 "너무 뜬금없는 물건들이 뜬금없는 위치에 나온다"고 지적. 사용자가 제시한 기준은 **사물의 실제 소속 위치** — 공은 바닥에 붙어 있으면 좋다(현재 OK), 삼각자는 칠판 위, 시계는 교실 가운데 상단, 네모는 사물함·창문 말고 책상 위에 있을 법한 다른 에셋을 다시 생각할 것. 더불어 칠판 오른쪽이 비어 있으니 학생을 상시 배치해 교실처럼 보이게 하라고 요청. 현재 좌표는 배경 아트와 무관하게 stage 좌표로만 흩어 놓아(`rect:[830,240,215,215]` 등) 사물이 공중에 떠 있거나 맥락 없는 면에 얹힌다.
  - 2026-08-03: 위 요청으로 넣은 그 학생(`#shapeSceneStudent`)이 이번엔 **"책상 위에 서 있는 것처럼 보인다, 마루바닥에 서 있게 위로 올려라"**고 지적. `bottom:-12px`로 스테이지 바닥에 붙여 놓아 발이 y≈1004에 닿는데, 배경의 책상 상판은 y 900~975라 학생이 책상보다 앞·아래에 서게 된다. 사물과 똑같이 **인물도 배경에 그려진 바닥면에 발을 앵커**해야 한다는 지적이다.
  - 2026-08-03: 같은 장면에서 "**삼각자를 칠판의 위에 서 있도록** 하고 약간 왼쪽으로 옮기라"고 지적. 2026-07-31 요청("삼각자는 칠판 위")을 `rect:[500,395,210,210]`로 반영해 뒀는데, 이 좌표는 칠판 면(x 80~768 / y 240~660)의 **한가운데에 그림처럼 얹혀** 있어 벽에 붙인 도형 스티커로 읽힌다. 사용자가 말한 "위"는 **칠판 상단 테두리 위에 세워 둔(기대어 놓은) 상태**다. 같은 지적의 3번째 사례이자, **"어느 면에 놓느냐"에 더해 "그 면 위에 어떤 자세로 놓이느냐"까지 개연성의 일부**임을 보여준다.
- 조치(2026-08-03, 08차시 25번 — `production/1-2/08/complete.md` 25번): 벽에 홀로 박힌 삼각 깃발(`triangle_pennant`)을 **학생 머리 위의 고깔모자(`triangle_party_hat`)** 로 교체했다. 후보 1순위였던 트라이앵글(악기)이 아니라 고깔모자를 고른 이유는 (a) 저학년 ▲ 인지가 최우선이고 (b) **벽에 거는 물건을 또 더하면 삼각자와 같은 "도형 스티커" 인상이 반복**되기 때문이다. 학생 에셋 3종의 머리 위치가 서로 달라 `HAT_POSE_RECT` + `positionPartyHat(pose)`로 그림을 포즈마다 옮기고, 핫스팟은 세 포즈를 모두 덮는 고정 박스로 뒀다. **교훈: "찾을 사물"이 현실에 있을 법한지는 종류만이 아니라 그 종류가 그 장소에 홀로 있을 법한지까지 본다.**
- 조치: 1번은 `todo.md` 18번으로 완료. 2번은 `todo.md` 23번 — `.classroom-student`를 `bottom:129px`(발 y≈880, 벽·바닥 경계 818과 책상 상판 900 사이)로 올리고 원근에 맞춰 340×560 → 300×494로 축소.
- 규칙화 메모: 2회. 반복되면 "탐색·찾기 장면의 사물은 도형 난이도만 보고 배치하지 말고 그 사물이 실제로 놓이는 표면(바닥/책상/벽/칠판)에 앵커를 두고, 배경 아트의 빈 면은 장면 맥락(인물·소품)으로 채운다"를 `prompts/builder_system.md`에 제안 후보. **[bg-anchor-alignment]와 구분할 것** — 그쪽은 "배경에 그려진 자리에 못 맞춤"(기하 정합), 이쪽은 "자리 자체가 개연성이 없음"(장면 의미). 같은 태그로 묶지 말 것.

### [narration-visual-mismatch] 대사가 말하는 것과 화면에 보이는 것이 다름(색·개수)

- 대상: production/1-2/08/index.html (`section_arithmetic_tutorial` — `#arithSpeech` 대사 vs `.paint-shape` 색, 페인트 통 에셋)
- 분류 태그: narration-visual-mismatch
- 상태: 열림
- 발생 횟수: 4
- 최초 발생일: 2026-07-31
- 최근 발생일: 2026-08-03
- 사례:
  - 2026-07-31: 세 수의 덧셈·뺄셈 튜토리얼에서 대사는 `초록색부터 알려드릴게요`(index.html:452·764)라고 하는데 화면의 도형은 여러 색으로 나온다.
  - 2026-07-31: 같은 튜토리얼에서 "페인트 통이 하나 더 필요하다"는 대사가 나오는데 화면에는 페인트 통이 한 통만 그려져 있다. 대사가 요구하는 수량 변화가 화면에 반영되지 않는다.
  - 2026-08-03: "**페인트 통에 색깔 모양 넣어주기** — 페인트 가운데에 색깔을 칠하되 페인트 손잡이와 겹치지 않게"(참고 이미지 3장: 초록·파랑·빨강 페인트통). `paint-can-body.png`는 색 표시를 덧씌우라고 앞면을 비워 둔 회청색 통 **1종뿐**이라, 화면에 페인트가 몇 통 있어도 **어느 색인지 알 수 없다.**
  - 2026-08-03: `section_shape_find`의 페인트 소개 단계에서 "**페인트마다 색깔이 달라요** 할 때 색깔 모양이 있는 페인트 통을 **모양 아래에 배치**하라"고 지적. `startPaintIntro()`의 대사는 `페인트 색깔마다 모양이 달라요`인데, 화면은 `#paintIntroVisual`의 ●(초록)■(파랑)▲(빨강)과 **색이 없는 통 하나**(`#paintCan`, `left:1202px`)가 따로 떨어져 있어 **"색↔모양" 대응이 화면에 전혀 그려지지 않는다.** 대사가 말하는 대응 관계를 통-도형 세로 짝으로 보여야 한다. 위 사례와 한 쌍(에셋 → 배치)이다.
- 조치: (미조치 — `production/1-2/08/todo.md` 19·21번, 2026-08-03분은 39·40번으로 등록)
- 규칙화 메모: 아직 2회지만 둘 다 같은 씬에서 나왔다. 반복되면 "대사 원문이 색·개수·방향 같은 관찰 가능한 속성을 말하면 그 속성이 화면 상태와 일치하는지 씬 단위로 대조한다(원문은 못 바꾸므로 화면을 원문에 맞춘다)"를 `prompts/content_refine_system.md`에 제안 후보. 연관 [spec-fx-color-mismatch](스펙 지정 색을 임의로 바꿈 — 그쪽은 구현이 스펙을 어긴 것, 이쪽은 구현이 **원문 대사**와 어긋난 것), [refine-alters-spec-text].

### [arith-operand-not-highlighted] 더하는 대상은 표시가 없고 빼는 대상만 표시돼 연산 방향이 안 읽힘

- 대상: production/1-2/08/index.html (`section_arithmetic_tutorial` — `#arithShapes` 추가/삭제 연출)
- 분류 태그: arith-operand-not-highlighted
- 상태: 제안됨 (5회 도달, 2026-08-04 rule 승격 제안 — 사용자 판단 대기. 태그 이름보다 넓은 패턴을 담고 있다. 실제 성격은 "**같은 화면 안에서 짝을 이루는 것들의 시각 처리가 비대칭**"이다)
- 발생 횟수: 5
- 최초 발생일: 2026-07-31
- 최근 발생일: 2026-08-04
- 사례:
  - 2026-07-31: "7개에서 3개를 색칠"에서 **빼기는 빼는 표시가 잘 되어 있는데 더하기는 어떤 게 더해지는 것인지 표시가 없다**고 지적. 사용자가 제안한 해법은 네모로 묶어 glow를 주거나 그에 준하는 다른 표시. 짝을 이루는 두 연산에 시각 처리가 비대칭이라 덧셈 쪽만 관찰 근거가 사라진다.
  - 2026-08-03: `section_random_problems`에서 "**2+8=10이라면 2개와 8개가 다른 색깔로** 담장에 모양을 두어야 한다"고 지적. `playRandomShapeIntro()`는 도형 색·모양을 `i%3`(초록●/빨강▲/파랑■)로 **인덱스에 따라 돌려 쓰기** 때문에, 색이 피연산자 경계와 무관하게 섞인다. 예: `2 + 8`이면 앞 2개와 뒤 8개가 색으로 구분돼야 하는데 지금은 10개가 3색으로 번갈아 나와 **어디까지가 첫째 항인지 셀 수 없다.** 등장 애니메이션(`pending` 해제)이 끝나 정지 화면이 되면 단서가 완전히 사라진다. 위 사례가 "더해지는 대상 표시 없음"이었다면 이건 "**항의 경계 표시 없음**"이다.
  - 2026-08-03: (41번 조치 이후 후속) 같은 씬에서 "**덧셈과 같이 빼기도 모양과 색깔이 다르면 좋겠다**"고 지적. 41-a가 덧셈(`type 3`)만 `groups`를 항별로 쪼개 초록●/파랑■/빨강▲를 얹었고, 뺄셈(`type 1`·`type 5`)은 `shapeStepsFor`에서 `groups:[{n, cls:G[0]}]` **한 덩어리 초록 ●**로 남아 빠지는 것만 `.removed`로 흐려진다. **2026-07-31 사례와 정확히 같은 비대칭이 방향만 반대로 재발했다** — 그때는 뺄셈에만 표시가 있고 덧셈에 없었고, 이번엔 덧셈에만 항별 색이 있고 뺄셈에 없다. 한쪽을 고칠 때 짝을 함께 보지 않으면 비대칭이 자리만 옮긴다. (**조치 완료 2026-08-03** — complete.md 49번: 뺄셈을 [남는 것 / 빼는 b / 빼는 c] 그룹으로 갈라 같은 색 매핑을 얹었다. `shapeStepsFor` 계약이 `{mode, groups, steps:[{op,group}]}`로 바뀌었다.)
  - 2026-08-03: 같은 씬 `section_random_problems`에서 "**가장 첫 문제에는 모양이 안 나온다**"고 지적. 4문항 중 유형 A(10이 되는 덧셈 보기 선택)만 `renderRandom`이 `#randomShapes`에 `hidden`을 붙이고 `shapeStepsFor(0)`이 `null`을 낸다. **의도된 동작이었다** — 코드 주석대로 "보기 선택은 식이 3개라 도형 하나로 무엇을 세는지 특정할 수 없다". 그러나 사용자에게는 같은 씬 4문항 중 하나만 담장이 비어 있는 **문항 간 비대칭**으로 읽힌다. 교훈: **"논리적으로 그릴 수 없다"는 판단은 그 자리를 비워 두는 근거가 못 된다** — 나머지 문항이 전부 그림을 갖고 있으면 빈 자리는 누락으로 읽힌다. (**조치 완료 2026-08-03** — complete.md 48번: 사용자 지시대로 `● … ● + [?]`(왼쪽 항 도형 + `+` + 점선 물음표 칸)로 그렸다. 점선 칸은 개수와 무관하게 하나여서 답을 미리 알려 주지 않는다.)
  - 2026-08-04: **(48번의 직계 후속)** 같은 씬 유형 A에서 "정답을 맞췄을 때 **물음표 박스에 숫자를 넣는 게 아니라 10개를 맞추러 도형을 추가**해 주는 식이 좋겠다. `+` 이후에 도형을"이라고 지적. 48번이 빈 담장을 `● … ● + [?]`로 채웠지만 **정답 표현은 여전히 숫자**였다(`8 + [2] = 10`). 이 씬의 다른 세 유형은 전부 개수를 도형으로 세는데 유형 A만 답이 숫자로 닫혀, "10을 채웠다"가 그림에서 안 보인다. **48번과 같은 비대칭이 한 칸 안쪽에서 재발한 것**이다 — 그때는 "문항 하나만 그림이 없다", 이번은 "문항 하나만 답이 그림이 아니다". 그림을 주는 것만으로는 부족하고 **문항의 처음부터 끝까지 같은 표현 체계**여야 한다. (**조치 완료 2026-08-04** — `production/1-2/08/complete.md` 81번: `fillRandomSlotWithShapes()`가 `+` 뒤에 모자란 개수만큼 도형을 채워 화면의 도형이 정확히 10개가 되게 한다. 색·모양은 41-a의 항별 매핑대로 파랑 ■.)
- 조치: (미조치 — `production/1-2/08/todo.md` 20번, 2026-08-03분은 41·48·49번으로 등록)
- 규칙화 메모: **5회 도달 → rule 승격 제안(2026-08-04, 사용자 승인 대기).** 초안: "**같은 씬 안에서 짝을 이루는 것들은 시각 처리를 대칭으로 만든다.** 대칭 대상은 셋이다 — (a) 짝을 이루는 조작(추가/삭제, 정답/오답), (b) **같은 씬의 문항들**(한 문항만 그림이 없으면 누락으로 읽힌다), (c) **한 문항의 처음과 끝**(문제를 그림으로 냈으면 정답도 그림으로 닫는다). '논리적으로 그릴 수 없다'는 판단은 빈 자리나 다른 표현 체계를 정당화하지 못한다." 반영 위치: `content-harness-pipeline/prompts/builder_system.md`.
- 규칙화 메모(1회 시점): 아직 1회. 반복되면 "짝을 이루는 조작(추가/삭제, 정답/오답, 이전/다음)은 시각 처리를 대칭으로 만든다 — 한쪽에만 강조·모션을 주면 다른 쪽은 관찰 근거가 없는 상태가 된다"를 `prompts/builder_system.md`에 제안 후보. 연관 [motion-supporting-narration](나레이션이 말하는 사건에 시각 액션이 없음 — 이쪽은 **한쪽에만 있음**).

### [primitive-shape-raster-instead-of-css] 원·삼각형·사각형 같은 순수 기하 도형을 raster 에셋으로 만들어 낡아 보임

- 대상: production/1-2/08/index.html (`.paint-shape` — `assets/shape-tile-body.png` 3프레임 스프라이트), `road-sign-{circle,square,triangle}.png`
- 분류 태그: primitive-shape-raster-instead-of-css
- 상태: 열림
- 발생 횟수: 1
- 최초 발생일: 2026-07-31
- 최근 발생일: 2026-07-31
- 사례:
  - 2026-07-31: "동그라미 세모 네모 에셋이 너무 낡아 보인다, 다시 만들기 — 이건 이미지가 아니어도 될 것 같다, 한번 HTML로 해 보기"라고 지적. 순수 기하 도형이라 raster로 둘 이유가 없는데 스프라이트로 만들어 두어 (a) 아트가 낡아 보이고 (b) 색칠을 위해 `mask-image` 우회가 필요했다([blend-tint-bleeds-outside-alpha] 참조).
- 조치: (미조치 — `production/1-2/08/todo.md` 22번으로 등록)
- 규칙화 메모: 아직 1회. 반복되면 "원·삼각형·사각형 등 파라미터로 정의되는 기하 도형과 기능적 입력 컨트롤은 raster 에셋으로 만들지 않고 CSS/SVG로 그린다. 색·크기 변형이 필요한 요소일수록 그렇다"를 `prompts/asset_generator_system.md`+`builder_system.md`에 제안 후보. 연관 [ornate-asset-wrong-function](최종 교훈이 "기능적 입력 컨트롤은 사진 에셋이 아니라 CSS로" — 같은 결론에 도달한 선례), [blend-tint-bleeds-outside-alpha](raster로 둔 탓에 생긴 색칠 우회).

### [same-character-duplicated-on-screen] 상시 배치 인물과 대사·피드백용 인물이 겹쳐 같은 캐릭터가 한 화면에 둘 보임

- 대상: production/1-2/08/index.html (`section_shape_find` — `#shapeSceneStudent` vs `#shapeCharacter` / `#feedbackCharacter`)
- 분류 태그: same-character-duplicated-on-screen
- 상태: 열림
- 발생 횟수: 1
- 최초 발생일: 2026-08-03
- 최근 발생일: 2026-08-03
- 사례:
  - 2026-08-03: "아이가 대화가 끝나고 나와야 해. 지금은 대화 중에도 계속 서 있어서 아이가 2명 보이잖아." 오프닝 대사의 2·4번째 beat가 `student-thinking`/`student-idle`로 말하는 동안 배경 상시 배치 학생(`#shapeSceneStudent`, `student-idle`)이 그대로 서 있어 **같은 인물이 동시에 둘** 나온다.
  - 2026-08-03: 같은 지적의 연장 — "피드백이 서 있는 아이에게서 나와야 해, pose 변화가." 오답 피드백이 화면 밖에서 `#feedbackCharacter`(`student-thinking`)를 새로 띄우는 방식이라 서 있는 아이 옆에 **또 하나의 같은 아이**가 생긴다. 이미 무대에 있는 인물이 있으면 그 인물의 포즈를 바꿔야 한다.
- 조치: `todo.md` 23번 — (a) `#shapeSceneStudent`를 오프닝 대사 동안 숨기고 찾기 단계 진입 시 등장, (b) `setSceneStudentPose()`를 만들어 서 있는 학생이 화면에 있을 때는 오답=`student-thinking` / 정답=`student-volunteer`로 **그 인물의 src를 교체**하고 `#feedbackCharacter` 오버레이는 띄우지 않음.
- 규칙화 메모: 아직 1회. 반복되면 "한 씬에 같은 캐릭터를 두 요소로 두지 않는다. 무대에 상시 배치된 인물이 있으면 대사·피드백은 **그 인물의 src/포즈 교체**로 표현하고, 별도 오버레이 캐릭터는 무대에 그 인물이 없을 때만 띄운다"를 `prompts/builder_system.md`의 "channel 렌더링 계약"에 절로 추가 제안. 연관 [feedback-as-character-bubble](규칙화됨 — 피드백은 캐릭터+말풍선으로. 이 항목은 그 규칙을 지키다 **인물이 중복**되는 후속 실패), [object-placement-implausible](같은 학생 요소의 발 위치 문제 — 그쪽은 좌표, 이쪽은 존재).

### [speech-bubble-anchor-detached] 말풍선이 말하는 캐릭터에서 멀리 떨어져 누가 말하는지 안 붙어 보임

- 대상: production/1-2/08/index.html (`.speech.feedback-speech` ↔ `.feedback-character`, `.help-card` ↔ `.help-character`)
- 분류 태그: speech-bubble-anchor-detached
- 상태: 제안됨 (5회 도달 — rule 승격 제안, 승인 대기)
- 발생 횟수: 5
- 최초 발생일: 2026-08-03
- 최근 발생일: 2026-08-04
- 사례:
  - 2026-08-03: "피드백 시 캐릭터 옆에 `정답` 말풍선이 너무 멀리 떨어져 있다"고 지적. 실측: `.feedback-character{left:80px;bottom:-10px;width:360px;height:590px}`는 `object-fit:contain`이라 실제 그림은 360×540(y 525~1065)로 들어가고, `teacher-praising.png`의 알파 bbox(1024×1536 중 x 444~786 / y 66~1456)를 적용하면 **눈에 보이는 인물은 stage x 236~356 / y 548~1037**뿐이다. 말풍선은 `.speech.feedback-speech{left:500px;top:250px}`라 꼬리 끝이 (466, ~300) → 인물 오른쪽 끝에서 **110px 밖**, 머리 위로 **약 260px** 떨어진다. 같은 무대의 정상 조합(`.character.left` + `.speech.left-speaker{left:390px;top:220px}`)은 꼬리가 인물의 x 범위 **안**(356 vs 253~400)에 들어가 붙어 보인다.
  - 2026-08-03: `section_random_problems`의 힌트에 대해 "**선생님을 클릭하면 선생님이 말풍선으로 힌트를 주는 것**이고, 말풍선은 **선생님이 말하는 식으로 배치**해 달라"고 지적. 힌트는 `.help-card`(`right:430px;top:180px`, 크림 사각 카드)라 (a) 말풍선이 아니라 **패널**이고 (b) 화자인 `.help-character`(`#helpCharacter`, `right:10px;bottom:-20px;500×650`)의 머리 높이·꼬리 방향과 무관하게 화면 오른쪽 위에 떠 있다. 27번이 `.feedback-speech`에서 고친 것과 **같은 결함이 다른 요소에서 반복**된 것이다 — 그때는 앵커만 옮기면 됐지만 이번엔 **표면 종류 자체가 말풍선이 아니다.** 함께 지적된 것: 손가락 힌트(`.finger-hint`)를 **모든 문제**에 띄우고 그 손가락이 **선생님을 가리키게** 할 것(지금은 `#helpCharacter`를 한 번 누르면 `hidden`이 되고 다시 안 나온다 — index.html:1026·1046).
  - 2026-08-03: **(38번 조치의 세로 축 누락)** "아이의 크기는 작아졌는데 말풍선은 너무 위에 있어. 어른일 때는 그게 맞는데 아이일 때는 좀 더 아래에 있어야 해." 38번이 `--char-scale:.7`로 아이를 줄이면서 앵커는 **가로만** 보정했다(`.character[src*="student-"].left + .speech.left-speaker{left:280px}` / `.right{right:250px}`). 세로 `.speech.left-speaker`·`.right-speaker{top:220px}`은 어른·아이가 공유한다. 실측: `.character.left`(440×720, bottom −12)는 `object-fit:contain`으로 그림이 y 402~1062에 들어가 `teacher-explaining` 알파 y 0.048~0.947 → **머리 꼭대기 y ≈ 434**, 아이는 ×0.7(308×504)이라 그림이 y 609~1071이고 `student-thinking` 알파 y 0.080~0.896 → **머리 꼭대기 y ≈ 646**. **차이 212px**만큼 아이 말풍선이 머리 위로 떠 있다. (**조치 완료 2026-08-03** — complete.md 57번: 세로 앵커를 `--speech-anchor-top`(씬 기준값) + `--speech-child-drop`(아이 보정 205px) 두 항의 합으로 바꿨다. 씬별 `top` 오버라이드가 ID 명시도로 아이 보정을 이기던 구조가 원인이라, `#arithSpeech`·`#drawingSpeech`도 `top` 대신 기준값 변수를 쓰게 고쳤다.)
  - 2026-08-04: **(57번 조치의 기준점 자체가 틀림)** "대사 말풍선의 **y축이 캐릭터의 얼굴 위치**에 오게 해 달라. 지금은 너무 높거나 낮다." 57번은 세로 앵커를 **머리 꼭대기 기준**으로 맞췄는데("꼬리 y − 머리 y"를 어른·아이가 같게), 사람이 보는 기준은 **얼굴**이다. 실측하니 어른 beat의 꼬리는 얼굴 중심(stage y **492**)보다 **194px 위**, 즉 머리 꼭대기(433)보다도 위여서 말풍선이 인물 **머리 위 하늘**에 떠 있었다. 더 큰 문제는 앵커가 **상자 윗변**(`top`)인데 꼬리는 **상자 세로 중심**(`::before{top:50%}`)이라는 것이다 — 대사 줄 수가 늘면 상자가 아래로 자라 꼬리가 그만큼 내려가서, **같은 씬 안에서도 beat마다 높이가 달라진다.** 사용자가 "너무 높거나 낮아"라고 한 것이 바로 이 둘이 섞인 결과다.
    - 얼굴 중심 실측(에셋 알파 행 폭 프로파일에서 머리 꼭대기 → 목 국소 최소를 잡고 중점, `tmp/measure-face.js`): 어른 6종 이미지 높이의 **0.135~0.146**, 아이 3종 **0.212~0.214**. `.character.left/.right` 슬롯 환산 → 어른 **y 492** / 아이(`--char-scale:.7`) **y 707**, `.feedback-character` 슬롯(teacher-praising) → **y 598**.
    - 조치: 앵커를 `--speech-face-y`(얼굴 중심 y) 하나로 바꾸고 `top:var(--speech-face-y);translate:0 -50%`로 **상자 세로 중심 = 꼬리 = 얼굴**을 만들었다. `transform`이 아니라 **`translate` 속성**을 쓴 것이 핵심이다 — `speechPop`이 `transform:scale()`을 애니메이션하므로 `transform:translateY(-50%)`로 적으면 애니메이션이 덮어쓴다(377행 주석의 `.narration-advance` 사례와 같은 함정). 상세는 `production/1-2/08/complete.md` 83번.
  - 2026-08-04: **(반대 방향 — 너무 붙어서 인물을 가림)** "**머리 바로 옆에 붙이지 마.** 인트로에서 보면 꼬마 옆에 바로 붙여서 **꼬마 포즈가 가려졌잖아.**" 38번이 아이 가로 앵커를 `right:390` → `250`으로 당긴 것이 원인이다. 그때 기준은 "**꼬리 끝이 전신 알파 bbox 안에 들어오는가**"뿐이었고 **상자 자체가 인물을 덮는지**는 보지 않았다. 실측: `student-volunteer`가 `.right`일 때 말풍선 오른쪽 끝은 1670인데 인물 실루엣은 **1612**부터라 **58px이 인물 위로 올라탄다** — 그 58px이 자원하며 든 팔이다. `student-thinking`.right 48px · `student-idle`.right 22px · `student-idle`.left 4px · `student-volunteer`.left 7px도 같은 방향으로 겹쳐 있었다.
    - **전신 알파 bbox로 재면 이 결함이 안 보인다.** 들어올린 팔·벌린 발까지 포함한 좌우 끝이라 말풍선이 실제로 걸리는 **얼굴 높이 밴드**의 실루엣과 다르다. 85번에서 밴드(얼굴 중심 ± 말풍선 최대 반높이 121px) 안으로 좁혀 다시 쟀다(`tmp/measure-side.js`).
    - 조치: 가로 앵커를 `--speech-side-x`(= **밴드 안 실루엣 가장자리 + 60px**)로 바꾸고 **에셋·방향별로** 값을 줬다. 상세는 `production/1-2/08/complete.md` 85번.
- 조치: **완료 2026-08-03** — `production/1-2/08/complete.md` 27번. `.speech.feedback-speech`의 앵커만 `left:500px;top:250px` → `left:380px;top:470px`. 꼬리(x 346)가 `teacher-praising.png`의 실제 알파 bbox(x 236~356) 안에 들어간다. 폭·패딩은 건드리지 않았다. 세 번째 사례(아이 말풍선 세로 앵커)도 **완료 2026-08-03** — complete.md 57번. 네 번째 사례(얼굴 높이 정렬)도 **완료 2026-08-04** — complete.md 83번. 앵커를 `--speech-face-y`(얼굴 중심 절대 y) + `translate:0 -50%`로 바꿔 **대사 길이와 무관하게** 꼬리가 얼굴에 남는다. 얼굴 중심 비율표는 `production/1-2/08/todo.md`에 실었다.
- 규칙화 메모: **4회 — 1회만 더 나오면 승격 대상이다.** 교훈 후보: **말풍선 앵커는 캐릭터 요소의 박스가 아니라 `object-fit:contain` 후의 실제 알파 bbox 기준으로 잡는다.** 4회째가 더한 것: **(1) 세로 기준점은 머리 꼭대기가 아니라 얼굴 중심이다. (2) 크기가 변하는 표면은 "윗변"이 아니라 "꼬리가 붙는 점"을 앵커로 잡는다** — 상자가 한 방향으로만 자라면 콘텐츠 길이가 정렬을 깬다. 3회째 사례가 더한 것: **캐릭터 크기를 바꾸면 앵커는 가로·세로를 함께 다시 잡는다** — 한 축만 고치면 나머지 축에서 같은 결함이 남는다. 연관 [character-relative-scale-mismatch](그 조치가 이 결함을 만들었다). 박스 폭(360px)과 보이는 폭(120px)이 3배 차이 나면 박스 오른쪽에 붙인 말풍선은 인물에서 떠 보인다. 연관 [speech-bubble-fixed-box-not-content-sized](그쪽은 상자 크기, 이쪽은 앵커 위치), [bg-anchor-alignment](같은 "실측 없이 눈대중 좌표" 계열).

### [content-overflows-fixed-surface] 개수·길이가 가변인 콘텐츠가 고정 크기 표면을 넘쳐 잘림

- 대상: production/1-2/08/index.html (`.drawing-summary`, `.story-card`)
- 분류 태그: content-overflows-fixed-surface
- 상태: 열림
- 발생 횟수: 2
- 최초 발생일: 2026-08-03
- 최근 발생일: 2026-08-03
- 사례:
  - 2026-08-03: `section_free_drawing`의 `그림을 완성했나요?` 아래 도형 요약이 "6개 이상 나오면 넘친다"고 지적. 실측: `.confirm-panel`(850px, padding 55) 안 `.drawing-summary`의 clientWidth는 **728px**인데 `.drawing-summary .paint-shape{width:112px}` + `gap:18px`이라 5개=632px(들어감) / 6개=**762px(넘침, scrollWidth 745 관측)**. 조합은 3모양×4색 = 최대 **12개**까지 늘 수 있어 상한이 없다.
  - 2026-08-03: `section_math_story` 표지판 설명(`.story-card`)이 "아래로 치우쳐 잘린다"고 지적. 카드 600px 중 패딩(282/118)을 빼면 글 영역이 **200px**뿐인데 가장 긴 beat(제목 1줄 + 빈 줄 + 본문 2줄 + 빈 줄 + 마무리 1줄 + `다음 ▸` 버튼)는 360px 이상이라 넘치고, 카드가 `bottom:-115px`로 무대 밖에 걸려 있어 넘친 부분이 화면 아래로 사라진다.
- 조치: **완료 2026-08-03** — `production/1-2/08/complete.md` 31·33번. 요약 도형은 `DRAWING_SUMMARY_MAX=4` 상한 + `…` 한 칸(`.summary-more`), 표지판 카드는 에셋 크림 면 비율 패딩(`101px 64px 153px`)으로 가용 영역을 1177×346px로 되찾아 `--fs-md`에서도 가장 긴 beat(334px)가 들어간다. **두 건 다 표면을 키우지 않고 상한·비율로 해결했다** — 이 태그의 교훈 후보와 정확히 같은 방향이다.
- 규칙화 메모: 아직 2회. 교훈 후보: **개수·길이가 런타임에 정해지는 콘텐츠를 고정 폭·높이 표면에 넣을 때는 "최대 개수/최장 문구"로 맞는지 계산하고, 안 맞으면 표면을 늘리는 대신 표시 상한 + 생략 표기(`…`)를 둔다.** 연관 [clock-hand-overflow], [typeC-question-longer-monitor-overflow], [label-text-wrapping] — 셋 다 같은 계열이라 5회 도달 시 하나로 묶어 승격 검토.

### [dialogue-speaker-misassigned] 원문 음성 스크립트가 화자를 지정했는데 다른 인물에게 배정함

- 대상: production/1-2/08/index.html (`shapeDialogues`, `#shapeCharacter` 정적 마크업 / `showFeedback`, `#feedbackCharacter`)
- 분류 태그: dialogue-speaker-misassigned
- 상태: 열림
- 발생 횟수: 2
- 최초 발생일: 2026-08-03
- 최근 발생일: 2026-08-03
- 사례:
  - 2026-08-03: `section_shape_find` 오프닝의 `여러 가지 모양으로 그리면 좋겠어요.` 대사에 대해 "이 대사는 선생님이 할 거야, 오른쪽에서 나오게 해 달라"고 지적. 구현은 `worker-explaining.png`(공사 작업자)가 **왼쪽에서** 말한다. 원문 `수리력 1차_1학년 2학기 8차시 (백승용) 723 음성 스크립트.md` 씬2는 화자를 번호로 명시한다 — `1. 주인공 / 2. 교사 / 3. 교사 / 4. 주인공`. 요청 md 116~120행의 UI 요소 표도 `1 주인공 오디오 / 2 교사 등장 및 오디오 / 3 교사 오디오 / 4 주인공 오디오`로 같다.
    - **원인:** 요청 md의 "예시화면 문구"는 화자 없이 문구만 나열한 목록(129~133행)인데, builder가 **화자가 적힌 음성 스크립트 대신 이 목록의 순서를 그대로 대사 배열로 옮겼다.** 그래서 (a) 첫 대사의 화자가 작업자로 잘못 붙었고, (b) 음성 스크립트 기준 1번(주인공 `벽화를 어떻게 그려야 되지?`)과 2번(교사)의 **순서까지 뒤바뀌었다.** 사용자가 지적한 것은 (a)뿐이지만 근본 원인은 같다.
  - 2026-08-03: **(내레이션에 화자를 세움 — 반대 방향의 같은 결함)** "**아나운서가 말하는 건 캐릭터까지 나와서 말해줄 필요가 없어**, `정답입니다`라고." 원문 음성 스크립트는 `정답입니다`를 **내레이션**으로 지정한다(씬2-6 · 씬3-2 등 4회). 같은 씬의 `잘 찾았어요!`는 **교사** 대사(씬3-3)다. 그런데 `showFeedback(el,text,onContinue,voice)`은 텍스트와 무관하게 `#feedbackCharacter.src='teacher-praising.png'`를 띄워 **화자가 없는 내레이션을 교사 대사로 만든다.** 씬4 호출 2곳은 `text=''`이라 말풍선도 없이 **인물만 0.7초 번쩍인다**(`feedbackHideTimer`). 앞 사례가 "화자 A 대사를 B에게 줬다"였다면 이번은 "**화자가 없는 대사에 화자를 만들어 붙였다**"로, 원문 화자 표기를 안 읽은 결과라는 점은 같다. 규칙화된 [feedback-as-character-bubble](피드백은 캐릭터+말풍선으로)이 이 방향으로 밀어붙인 면도 있어 **그 규칙의 예외 정리가 함께 필요하다.** (**조치 완료 2026-08-03** — complete.md 60번, 사용자가 **B안**(도장 + 음성만) 선택. `showFeedback`에 `speaker` 인자를 더해 `잘 찾았어요!`만 `'teacher'`로 부르고 나머지는 내레이션으로 도장만 낸다. 진행 표면은 새 `#narrationAdvance`로 옮겨 26번 데드엔드를 막았다. 씬4의 `text=''` 2곳은 인물 번쩍임이 사라졌다. **규칙 예외 정리는 아직 미결** — 아래 규칙화 메모 참조.)
- 조치: **완료 2026-08-03** — `production/1-2/08/complete.md` 34번. `shapeDialogues`의 앞 두 원소를 맞바꾸고 교사 대사를 `teacher-explaining.png`/`right`로 바꿔 원문 음성 스크립트 씬2 순서(1.주인공 → 2.교사 → 3.교사 → 4.주인공)를 복원했다. 정적 마크업 `#shapeDialogue`도 함께 고쳤다(두 벌이라 한쪽만 고치면 첫 프레임에 이전 인물이 번쩍인다). **문구는 하나도 바꾸지 않았다.**
- 규칙화 메모: 2회. 교훈 후보: **화자·순서는 "예시화면 문구" 목록이 아니라 화자가 번호로 명시된 음성 스크립트(및 UI 요소 표)를 정본으로 삼는다. 화자 표기가 `내레이션`이면 화면에 인물을 세우지 않는다 — 없는 화자를 만들어 붙이는 것도 화자 오배정이다.** 예시화면 문구는 *문구의 원문*만 보장하고 *누가 언제 말하는지*는 보장하지 않는다. 두 문서가 어긋나면 음성 스크립트가 우선. 반영 후보: `content-harness-pipeline/prompts/planner_system.md`(dialogue beat 생성 시 화자 소스 지정) + `prompts/builder_system.md`의 "channel 렌더링 계약". 연관 [dialogue-as-speech-bubble](규칙화됨 — 그쪽은 대사를 *어떻게* 렌더링할지, 이쪽은 *누가* 말하는지), [spec-interaction-flow-mismatch].

### [character-relative-scale-mismatch] 아이와 어른 캐릭터를 같은 크기로 그려 인지 부조화가 남

- 대상: production/1-2/08/index.html (`.character.left` / `.character.right` — `student-*.png`와 `teacher-*.png`·`worker-*.png`가 같은 박스를 공유)
- 분류 태그: character-relative-scale-mismatch
- 상태: 열림
- 발생 횟수: 1
- 최초 발생일: 2026-08-03
- 최근 발생일: 2026-08-03
- 사례:
  - 2026-08-03: "아이 캐릭터의 크기와 선생님·인부 캐릭터, 즉 **어른 캐릭터의 크기를 동일하게 만들면서 인지 부조화가 온다** → 아이 캐릭터를 어른 캐릭터의 **70% 정도 크기로 축소**하라"고 지적. 실측: 대사·피드백 캐릭터는 인물 종류와 무관하게 `.character.left`/`.character.right`(둘 다 `440×720`)를 공유하고, 에셋 원본도 3종 모두 1024×1536이라 **아이와 어른이 화면에서 같은 키로 선다.** 씬2 상시 배치 학생(`.classroom-student` 300×494)만 원근 때문에 따로 줄여 놓은 상태라, 같은 아이가 씬에 따라 어른과 같은 키였다가 작아졌다 한다.
  - 참고: 이 결함은 **에셋 생성 단계에서 캐릭터별 기준 신장을 정하지 않고 전부 같은 캔버스에 꽉 채워 그린 것**이 근본 원인이다. CSS 박스로 줄이면 화면은 맞지만 에셋의 유효 해상도가 낮아진다.
- 조치: (미조치 — `production/1-2/08/todo.md` 38번으로 등록)
- 규칙화 메모: 아직 1회. 반복되면 "한 화면에 함께 서는 캐릭터는 **역할별 기준 신장 비율**(예: 성인 1.0 / 저학년 아동 0.7)을 정하고 에셋 생성 시 같은 캔버스에서 그 비율로 그린다. 캔버스를 꽉 채워 그리면 CSS 박스가 같을 때 아이와 어른의 키가 같아진다"를 `prompts/asset_generator_system.md`(캐릭터 엔티티 생성 규격)에 제안 후보. 연관 [character-asset-identity-alpha](규칙화됨 — 그쪽은 포즈 간 **동일 인물** 보장, 이쪽은 인물 **간** 상대 크기), [content-scale-too-small](절대 크기가 작음 — 이쪽은 상대 크기가 어긋남), [object-placement-implausible](같은 "장면 개연성" 계열).

### [scene-title-hidden-during-activity] 씬 제목이 본 활동이 열리면 사라져 학습자가 지금 무엇을 하는 중인지 알 수 없음

- 대상: production/1-2/08/index.html (`#arithTitleSurface` ← `arithIntroTap.onclick`의 intro 분기)
- 분류 태그: scene-title-hidden-during-activity
- 상태: 열림
- 발생 횟수: 1
- 최초 발생일: 2026-08-03
- 최근 발생일: 2026-08-03
- 사례:
  - 2026-08-03: `section_arithmetic_tutorial`에서 "**세 수의 덧셈과 뺄셈 타이틀 … 문제 풀 때 계속 유지하기**"라고 지적. 같은 지시가 담장이 바뀌는 뺄셈 문항에 대해서도 반복됐다("+ 타이틀 유지"). 제목은 도입 대사 동안만 보이고 `arithIntroTap.onclick`의 intro 마지막 분기가 `#arithTitleSurface`에 `hidden`을 붙여 **문항이 열리는 순간 사라진다.** 51번이 제목을 넣을 때 씬3·6은 "도입에서만 보이고 본 활동이 열리면 물러난다"로 잡았는데, 물러나게 한 이유는 **그 자리(`top:180`)를 `.arith-context`(`top:155`, 풀이 말풍선)가 이어받기 때문**이었다. 즉 제목을 숨긴 것은 학습 설계가 아니라 **자리 다툼을 피한 결과**였고, 정작 학습자는 문제를 푸는 내내 단원 이름을 못 본다. 씬4·5는 같은 51번 작업에서 "상단이 비어 있다"는 이유로 씬 내내 남겨 둬서 **같은 문서 안에서 두 방식이 공존**한다. (**조치 완료 2026-08-03** — `production/1-2/08/complete.md` 61번. 62번으로 `.arith-context`가 통째로 없어져 자리 다툼 자체가 사라졌다.)
- 조치: **완료 2026-08-03** — complete.md 61번. intro 분기에서 `#arithTitleSurface`를 숨기던 한 줄을 뺐다. 좌표는 그대로(무대 중앙 · y 180~330) — 사용자가 "가로는 그대로, 유지만"으로 확정했다.
- 규칙화 메모: 아직 1회. 교훈 후보: **씬 제목처럼 "지금 무엇을 하는 중인가"를 알려 주는 표면은 활동 중에도 남긴다. 다른 요소와 자리가 겹쳐서 숨기는 것은 해결이 아니라 미룬 것이다** — 겹치는 쪽의 좌표를 옮기거나, 그 요소가 정말 필요한지를 먼저 따진다(이번엔 겹치던 `.arith-context`가 불필요하다는 판단으로 제거돼 함께 풀렸다). 연관 [bg-anchor-alignment](자리 실측), [overlay-occludes-bg-subject](제목이 배경을 가리는 반대 방향 사례).

### [sfx-too-elaborate-for-repeated-feedback] 반복해서 나는 판정 효과음에 길고 서사가 있는 음원을 골라 단순한 신호로 안 읽힘

- 대상: production/1-2/08/index.html (`tone(ok)` → `assets/audio/sfx/answer-correct.mp3` · `answer-wrong.mp3`)
- 분류 태그: sfx-too-elaborate-for-repeated-feedback
- 상태: 열림
- 발생 횟수: 1
- 최초 발생일: 2026-08-03
- 최근 발생일: 2026-08-03
- 사례:
  - 2026-08-03: 54번으로 넣은 정답음을 두고 "**문제에서 단순한 정답음으로**" 다시 찾으라고 지적(오답음도 함께). 고른 `Doorbell Ding Dong`은 실측 **3.24초**(가청 2.70초)에 딩–동 2음 + 긴 잔향이라, 초인종이라는 **서사**를 갖고 있고 한 문제당 여러 번 나는 자리에는 과하다. 오답 `Marimba Game Over` 역시 2.83초에 "게임 오버"라는 결말 뉘앙스를 얹고 있다.
  - 근본 원인: 후보를 고를 때 **"원문 표현(`딩동`)과의 문자적 일치"** 를 우선하고 **"그 소리가 나는 빈도와 역할"** 을 보지 않았다. 판정음은 한 차시에 수십 번 반복되는 **마이크로 피드백**이라 길이·서사가 짧을수록 좋다. 실제로 검증 로그에서 정답음이 정답 나레이션(`correct-1.wav`)과 같은 순간에 시작해 겹쳤는데, 이때 "겹침"을 미해결로 넘기고 **음원 선택 자체를 되짚지 않은 것**이 놓친 지점이다.
- 조치: **완료** (`production/1-2/08/complete.md` 59번). 후보 14개를 전부 내려받아 디코드하고 **가청 길이·peak·RMS를 실측한 뒤** 골랐다. 판정음 기준은 **가청 1초 이하 · 단일 타격 · 서사 없는 톤**. 정답음 3.24초(가청 2.70초) → **1.32초(가청 0.80초)**, 오답음 2.83초 → **1.06초(가청 0.48초)**. Pixabay 표시 길이는 반올림이라 믿지 않았다(54번에서 "0:01" 표시 파일이 실제 1.61초에 타격 4회였고, 이번에도 "0:01"짜리들이 실제 1.0~1.9초였다).
  - **부수 발견**: 고른 오답음이 peak −14.6dB / RMS −25.5dB로 다른 효과음보다 14dB 작아 사용자가 "좀 작다"고 다시 지적했다. **음원은 길이뿐 아니라 레벨도 서로 맞춰야 한다** — 같은 배포처의 파일이라도 정규화가 제각각이다. 4.8배 증폭해 RMS를 −11.9dB로 맞췄다(정답음 −11.2dB).
- 규칙화 메모: 아직 1회. 반복되면 "**반복 빈도가 높은 판정·조작 효과음은 가청 1초 이하의 단일 신호로 고른다. 서사·멜로디·긴 잔향이 있는 음원은 씬 전환·차시 완료처럼 한 번만 나는 자리에만 쓴다**"를 제안 후보. 함께 넣을 것: "효과음 길이는 배포처 표시값이 아니라 디코드 실측으로 확인한다." 연관 [beat-timing-vs-audio](그쪽은 화면 타이밍이 오디오 길이와 안 맞음, 이쪽은 음원 선택 자체가 역할에 안 맞음), [unwanted-celebration-fx](과한 축하 연출 계열), [content-scale-too-small](저학년 대상 감각 기준 계열).

### [transparent-img-box-swallows-clicks] 투명 여백이 큰 캐릭터 이미지의 요소 박스가 옆 UI의 클릭을 먹어 버튼이 안 눌림

- 대상: production/1-2/08/index.html (`.help-character` / `#randomKeypad`)
- 분류 태그: transparent-img-box-swallows-clicks
- 상태: 열림
- 발생 횟수: 1
- 최초 발생일: 2026-08-04
- 최근 발생일: 2026-08-04
- 사례:
  - 2026-08-04: `section_random_problems`에서 "**가리키는 손가락 모양 때문인지 다이얼 버튼 일부가 안 눌린다**"고 지적. 실측하니 범인은 손가락이 아니라 **선생님 이미지**였다. `.finger-hint`는 `pointer-events:none`이고 박스도 stage x 1541~1721로 키패드(오른쪽 끝 1496) 밖이다. `.help-character`(`right:10;width:500` → 박스 **x 1411~1911**, `z-index:var(--z-character)=12`)가 문제 패널(`.panel`, `--z-content`=10)보다 위에 있어 **키패드 3열(`3`·`6`·`9`·`확인`, x 1358~1496)의 오른쪽 절반을 덮는다.** 그 자리는 인물 알파가 0인 투명 여백(인물 실제 알파 bbox는 x **1570**~1821)이라 화면에는 아무것도 안 보이지만, `<img>`의 히트 영역은 **알파가 아니라 요소 박스**라 클릭을 그대로 먹는다. 눌리면 힌트 말풍선이 열려 "안 눌린다"가 아니라 "엉뚱한 게 열린다"로도 나타난다.
    - 검증: `document.elementFromPoint`를 키 12개의 좌·중·우 세 점에 찍어 3열 4개만 `img#helpCharacter`가 잡히는 것을 확인했다(`tmp/hit-s4.js`).
    - 조치: `.help-character{clip-path:inset(0 0 0 30%)}`. 알파 bbox 왼쪽 경계 31.8%보다 안쪽을 잘라 **보이는 그림은 그대로 두고 히트 영역만** 인물 위로 좁힌다. 상세는 `production/1-2/08/complete.md` 65번.
- 규칙화 메모: 아직 1회. 반복되면 "**여백이 큰 투명 캐릭터·장식 이미지를 인터랙티브 요소 위에 겹칠 때는 `clip-path`(또는 `pointer-events:none`)로 히트 영역을 알파 bbox까지 좁힌다 — `<img>`는 알파가 아니라 요소 박스로 클릭을 받는다**"를 `prompts/common_html_contract.md`에 제안 후보.
  - 연관 [bg-anchor-alignment]의 "(a) 요소 박스가 아니라 알파 bbox" 교훈과 **원인은 같고 층위가 다르다** — 그쪽은 눈에 보이는 정렬이라 캡처로 잡히지만, 이쪽은 **화면상 아무 이상이 없어 캡처로는 절대 안 잡힌다.** 같은 태그로 묶지 말 것. 대신 검사 방법이 다르다는 것을 기억한다: 겹치는 레이어가 있으면 **`elementFromPoint` 히트 테스트**를 돌린다.
  - 같은 씬의 [speech-bubble-anchor-detached](27번)·[bg-anchor-alignment](42번)가 이미 이 인물의 **알파 bbox를 실측해 todo.md 표에 적어 두었는데도** 히트 영역은 아무도 보지 않았다. 실측표가 있어도 **무엇에 쓰는 값인지**(정렬 전용인지 히트 영역까지인지)를 적어 두지 않으면 이렇게 샌다.

### [timer-cancel-without-state-reset] 타이머를 취소하면서 그 타이머가 되돌릴 예정이던 상태(class)는 안 걷어 효과가 켜진 채 멈춤

- 대상: production/1-2/08/index.html (`flashRandomShapes` / `.paint-shape.hint-step`)
- 분류 태그: timer-cancel-without-state-reset
- 상태: 열림
- 발생 횟수: 1
- 최초 발생일: 2026-08-04
- 최근 발생일: 2026-08-04
- 사례:
  - 2026-08-04: `section_random_problems`에서 "**힌트를 연속으로 누르면 도형 글로우 효과가 중간에 멈춰서 일부가 빛나는 형태로 멈춰 있다**"고 지적. `flashRandomShapes`는 진입할 때 `randomHintTimers.forEach(clearTimeout)`로 이전 예약을 전부 지우는데, 그 예약 안에 **"450ms 뒤 `hint-step`을 뗀다"는 되돌리기**가 들어 있다. 켜기(`classList.add`)는 이미 실행됐고 끄기만 취소되므로 그 도형은 **영구히 빛난 채 남는다.** 힌트 단계마다 focus 그룹이 달라(1단계 `[0]` → 2단계 `slot`) 새 호출이 그 노드를 다시 건드리지도 않고, `closeRandomHint()`도 클래스를 안 걷는다.
    - 검증: headless Chrome에서 선생님을 200ms 간격 3회 탭 → 2초 뒤 `.hint-step` 잔류 **1개**, 천천히 1회 탭 → 잔류 **0개**(`tmp/analyze-s4-feedback.js`).
    - 씬2·3의 같은 패턴(`hintCountShapes`·`hintArithmetic`)은 호출 시 타이머를 지우지 않아 이 증상이 없다. **"겹침 방지"로 넣은 `clearTimeout` 한 줄이 오히려 상태를 고착시켰다.**
    - 조치: `clearRandomShapeFlash()`(타이머 취소 + `#randomShapes .hint-step` 전부 제거)를 만들어 `flashRandomShapes` 진입·`closeRandomHint`·`clearRandomShapeIntro` 세 곳에서 부른다. 상세는 `production/1-2/08/complete.md` 69번.
- 규칙화 메모: 아직 1회. 반복되면 "**`setTimeout`으로 되돌리는 일시 효과는 타이머만 취소하지 말고 그 타이머가 되돌릴 상태까지 같은 자리에서 원복한다.** 취소와 원복을 한 함수로 묶고, 효과를 켜는 모든 경로가 그 함수를 지나게 한다"를 `prompts/common_html_contract.md`에 제안 후보. 대안으로 "일시 효과는 class+timer 대신 `animation` + `animationend`로 스스로 꺼지게 만든다"를 함께 적는다.
  - 연관 [content-flow-state-scaffolding-regression](재진입 초기화 계열)과 원인이 닮았으나 **층위가 다르다** — 그쪽은 씬·문항 경계의 상태 초기화, 이쪽은 한 문항 안에서 연타로 깨지는 타이머 경합이다. 검사 방법도 다르다: **연타(빠른 반복 입력)로 재현**해야 나온다.

### [confirm-tap-after-self-evident-result] 결과가 이미 명확한데 진행 확인 탭을 한 번 더 요구

- 대상: production/1-2/08/index.html (`showFeedback` 정답 피드백 / `#narrationAdvance`의 `다음 ▸`)
- 분류 태그: confirm-tap-after-self-evident-result
- 상태: 열림
- 발생 횟수: 1
- 최초 발생일: 2026-08-04
- 최근 발생일: 2026-08-04
- 사례:
  - 2026-08-04: "문제를 맞추면 도장에 다음 버튼이 나오는데 이걸 **다음버튼이 나오지 않고 도장만 1초정도 보여주고 바로 넘어가도록**"이라고 교정. 정답 도장·정답 음성으로 결과가 이미 전달됐는데도 `다음 ▸`를 눌러야 다음 문항으로 갔다. 씬2·3·4 정답마다 붙어 있어 한 차시에서 반복되는 마찰이었다.
    - 이 버튼은 **17·26번이 "정답 뒤 진행 경로가 0개가 되는 데드엔드"를 막으려고 세운 것**이라, 그때는 정당한 조치였다. 데드엔드를 막는 방법으로 "사람이 누를 표면"만 떠올린 것이 문제의 뿌리다 — **타이머는 같은 데드엔드를 막으면서 탭을 요구하지 않는다.**
    - 조치: 진행 표면 배선을 `setTimeout(completeFeedback, …)`으로 대체. 지연은 도장만 낼 때 1.5초(도장 애니 .65s + 정답 음성 1.51s가 끝나는 시점), 글자가 남는 교사 말풍선은 2.5초. 상세는 `production/1-2/08/complete.md` 87번.
- 규칙화 메모: 아직 1회. 반복되면 "**결과가 이미 자명한 자리(판정 도장·정답 음성·즉시 보이는 상태 변화)에서는 진행을 위한 추가 탭을 요구하지 않는다. 자동으로 넘기되 지연은 화면에 남는 것으로 정한다 — 도장이면 판정 애니와 음성이 끝나는 시점, 글자면 읽을 시간까지.**"를 `prompts/common_html_contract.md`에 제안 후보.
  - **경계 조건을 함께 적어야 한다**: 자동 진행이 정당한 것은 진행 방향이 하나뿐이고 되돌릴 필요가 없을 때다. 선택·입력이 남아 있거나 사용자가 내용을 검토해야 하는 자리에서는 여전히 탭을 받는다.
  - 반대 방향의 실패(진행 표면 자체가 없어 막히는 것)는 [content-flow-state-scaffolding-regression]이 이미 다룬다. **두 규칙이 부딪히지 않게 "진행 경로는 반드시 있어야 한다 — 사람의 탭이든 타이머든"으로 상위 문장을 맞춘다.**

### [operation-order-vs-layout-order] 연산 순서를 화면 배치 방향과 어긋나게 처리해 무엇이 먼저 빠지는지 안 읽힘

- 대상: production/1-2/08/index.html (`shapeStepsFor(5)` — 세 수의 뺄셈 `a - b - c`의 `groups`·`steps`, `randomHintSteps`)
- 분류 태그: operation-order-vs-layout-order
- 상태: 열림
- 발생 횟수: 1
- 최초 발생일: 2026-08-04
- 최근 발생일: 2026-08-04
- 사례:
  - 2026-08-04: `section_random_problems` 마지막 문항(세 수의 뺄셈)에서 "**동그라미 네모 세모 순으로 모양이 되어 있는데 흐릿하게 처리되는 게 네모 세모 순이다. 힌트대로라면 세모 네모 순으로 뒤에서부터 처리해야 한다**"고 지적. 힌트 문구도 "**세모를 빼서 10을 만들고 그다음에 네모를 빼라**"가 되어야 한다는 요구가 함께 왔다.
    - 49번이 뺄셈을 [남는 것(a-b-c) / 빼는 b / 빼는 c] 세 그룹으로 갈라 41-a의 색 매핑(초록 ● / 파랑 ■ / 빨강 ▲)을 얹었는데, 이 배치는 **항 순서(term order)** 를 따른 것이다. 그런데 `a - b - c`에서 먼저 빠지는 것은 b라서, 배치 순서대로면 **줄 한가운데(파랑 ■)가 먼저 지워지고 꼬리(빨강 ▲)가 나중에** 지워진다. 화면에서는 가운데에 구멍이 났다가 끝이 마저 사라지는 모양이라, "**뒤에서부터 덜어낸다**"는 뺄셈의 물리적 직관과 어긋난다.
    - 근본 원인: 색·모양 매핑을 **항 순서**에 얹는 규칙(41-a)을 뺄셈에도 그대로 복사했는데, 덧셈은 왼→오른쪽으로 **쌓이므로** 항 순서와 화면 진행 방향이 같고 뺄셈은 오른→왼쪽으로 **덜어내므로 반대**다. 두 연산의 "시간 순서"가 화면에서 반대 방향으로 흐른다는 것을 보지 않고 배치만 대칭으로 맞췄다.
    - 조치: 배치를 [남는 것 / c(파랑 ■) / b(빨강 ▲)]로 바꿔 **먼저 빠지는 b를 꼬리에** 둔다. 지우는 방향이 오른쪽 → 왼쪽 한 방향이 되고, 힌트 1단계가 빨강 ▲(10 만들기) · 2단계가 파랑 ■가 된다. 상세는 `production/1-2/08/complete.md` 89번.
- 규칙화 메모: 아직 1회. 반복되면 "**단계가 있는 연산을 그림으로 보일 때는 연산의 시간 순서와 화면의 공간 순서를 한 방향으로 맞춘다.** 쌓는 연산(덧셈·추가)은 배치 순서대로, 덜어내는 연산(뺄셈·삭제)은 배치의 역순으로 진행되게 항을 놓는다. 항 순서대로 놓는 규칙을 두 방향에 그대로 복사하지 않는다"를 `prompts/builder_system.md`에 제안 후보.
  - 연관 [arith-operand-not-highlighted](같은 씬, 짝을 이루는 것의 시각 처리 비대칭 — 그쪽은 **표시의 유무**, 이쪽은 **진행 방향**). 41-a·49번이 세운 색 매핑 규칙의 직계 후속이다.
  - 함께 볼 것: 힌트 문구가 도형 색·모양을 이름으로 부르므로(`빨강 ▲`), 배치를 바꾸면 `randomHintSteps`의 문구와 `focus` 그룹 번호를 **같은 커밋에서** 고쳐야 한다. 한쪽만 고치면 [narration-visual-mismatch]가 된다.

### [icon-glyph-not-centered-in-button] 아이콘 글리프(×)를 넣은 정사각 버튼에서 글자가 박스 중앙에 안 옴

- 대상: production/1-2/08/index.html (`.course-menu-close`)
- 분류 태그: icon-glyph-not-centered-in-button
- 상태: 열림
- 발생 횟수: 1
- 최초 발생일: 2026-08-04
- 최근 발생일: 2026-08-04
- 사례:
  - 2026-08-04: 왼쪽 햄버거 메뉴(차시 목록)의 **닫기 버튼 × 가 버튼 중앙에 있지 않다**고 지적. headless Chrome 실측(`tmp/measure-menu-close.js`)으로 잉크 bbox 중심이 박스 중심에서 **가로 +2.0px(오른쪽) · 세로 −2.5px(위)** 어긋나 있었다(스테이지 좌표).
    - 원인 둘. (1) **가로**: 버튼에 `display`·`padding` 지정이 없어 UA 기본값 `padding:1px 6px`가 살아 있었고 `box-sizing:border-box`라 42px 박스의 콘텐츠 폭이 `42 − 6(테두리) − 12(패딩) = 24px`인데 `×` 글리프의 advance는 28px이다. **글자가 콘텐츠 박스보다 넓으면 `text-align:center`가 음수 오프셋을 못 내고 한쪽(오른쪽)으로 흘러넘친다.** (2) **세로**: 버튼은 라인박스를 중앙에 놓을 뿐이고, Jua의 `×`는 잉크가 baseline−20 ~ baseline−1이라 잉크 중심이 `baseline−10.5`, 라인박스 중심(`baseline−8`)보다 **2.5px 위**다.
    - 조치: `.course-menu-close`에 `display:grid;place-items:center;padding:5px 0 0`를 넣었다. 좌우 패딩 0 + grid 중앙 정렬로 가로 압착을 없애고(같은 파일 `.debug-close`가 이미 쓰는 방식), 상단 패딩 5px이 콘텐츠 중심을 2.5px 내려 세로 오프셋을 상쇄한다. 실측 결과 offsetX 0.00 / offsetY −0.0000009. 상세는 `production/1-2/08/complete.md` 92번.
- 규칙화 메모: 아직 1회. 반복되면 "**글리프 하나를 아이콘으로 쓰는 정사각 버튼은 `display:grid;place-items:center;padding:0`을 명시한다. UA 기본 `padding:1px 6px` + `box-sizing:border-box`는 콘텐츠 폭을 글리프 advance보다 좁게 만들고, 이때 `text-align:center`는 넘치는 글자를 중앙에 두지 못한다.** 그리고 **글리프의 시각 중심은 라인박스 중심이 아니다** — 서체별로 잉크 bbox를 실측해 남는 오프셋을 패딩으로 보정한다"를 `prompts/common_html_contract.md`에 제안 후보.
  - 함께 볼 것: `production/1-2/01/index.html`의 `.course-menu-close`(30px 박스 / 20px 글자)가 **같은 결함을 그대로 갖고 있다.** 08은 01에서 이식해 온 것이라 원본에 남아 있다. 01을 손볼 때 함께 고친다.
  - **실측 함정**: `getBoundingClientRect`는 device px(#stage 축소 배율이 곱해진 값)이고 canvas 폰트 메트릭은 CSS px이다. 섞으면 오프셋이 배율만큼 작게 나온다(처음에 −1.3으로 잘못 읽었다).
  - 실측 하네스는 `tmp/measure-menu-close.js`(잉크 bbox = canvas `measureText`의 `actualBoundingBox*`)와 `tmp/shot-menu-close.js`(8배 확대 + 중심 십자선 스크린샷)다. 라인박스 `getBoundingClientRect`만으로는 글리프가 중앙인지 판정할 수 없다.

### [feedback-character-unwanted-in-scene] 오답 피드백에 캐릭터 오버레이를 띄우는데 특정 씬에서는 원치 않음

- 대상: production/1-2/08/index.html (`showWrongFeedback` — `#feedbackCharacter`, `section_random_problems`)
- 분류 태그: feedback-character-unwanted-in-scene
- 상태: 열림
- 발생 횟수: 1
- 최초 발생일: 2026-08-04
- 최근 발생일: 2026-08-04
- 사례:
  - 2026-08-04: "무작위 계산 문제에서 틀렸을 때 캐릭터가 피드백으로 나오고 있는데 나오지 않게 해줘." 씬4는 무대에 상시 학생이 없어 `showWrongFeedback()`이 `sceneStudentVisible()` 거짓 분기를 타고 화면 왼쪽에 `#feedbackCharacter`(`student-thinking`)를 0.7초 띄웠다. 이 씬은 오른쪽에 힌트용 선생님(`#helpCharacter`)이 이미 서 있어 **인물이 좌우로 둘**이 되고, 오답 신호(X 도장·오답음·흔들림)는 그것만으로 충분하다.
- 조치: `showWrongFeedback()`에 `NO_WRONG_CHARACTER_SCENES=['section_random_problems']`를 두고 도장 직후·포즈 분기 앞에서 빠져나가게 했다. 호출부(`judgeRandomChoice`·`judgeRandomKey`)는 그대로 둬서 26번 가드와 도장 경로를 유지했다. 검증: headless Chrome 1920×1080에서 씬4 오답 → `#feedbackCharacter` `display:none` + `#randomMark`는 wrong 도장, 같은 실행에서 씬3 오답은 종전대로 오버레이가 떠 회귀 없음. 상세는 `production/1-2/08/complete.md` 94번.
- 규칙화 메모: 아직 1회. 반복되면 "**피드백에 인물을 세울지는 씬 단위 정책으로 둔다** — 씬에 이미 인물이 있거나(상시 배치·힌트 인물) 판정 신호(도장·소리·모션)만으로 읽히는 자리에는 피드백 전용 캐릭터를 추가로 띄우지 않는다"를 `prompts/builder_system.md`의 "channel 렌더링 계약" `feedback` 절에 예외로 추가 제안.
  - 경계: `[same-character-duplicated-on-screen]`(같은 인물이 둘 보임 — 씬2, 무대 인물의 포즈 교체로 해결)과 **원인이 다르다.** 여기는 인물이 중복된 게 아니라 **다른 인물이 하나 더 늘어난** 것이고, 해법도 포즈 교체가 아니라 **안 띄우기**다. 같은 뿌리는 `showWrongFeedback`의 "무대에 학생이 없으면 무조건 오버레이" 기본값 하나다.
  - 연관: `[feedback-as-character-bubble]`(규칙화됨 — 피드백은 캐릭터+말풍선으로) 규칙의 **두 번째 예외 후보**다. 첫 번째는 60번의 "내레이션 대사는 화자를 세우지 않는다"(승인 대기). 둘을 묶어 "피드백 표면은 화자·씬 맥락에 따라 인물 없이 낼 수 있다"로 한 번에 제안하는 편이 낫다.

### [context-file-not-agents-md] 디렉토리 컨텍스트 문서를 README.md로 만들어 AI가 자동으로 읽지 않음

- 대상: content-harness-pipeline/source/common/components/README.md
- 분류 태그: context-file-not-agents-md
- 상태: 열림
- 발생 횟수: 1
- 최초 발생일: 2026-08-08
- 최근 발생일: 2026-08-08
- 사례:
  - 2026-08-08: "common/components에 Readme.md를 바꾸자. 차라리 AGENTS.md나 CLAUDE.md로 바꾸고, 거기에 공용으로 쓸 컴포넌트들이라고 설명을 써두자. 어떤 선생님이든 아니면 다른거에 상관 없이." 컴포넌트 1차 추출 때 디렉토리 설명을 `README.md`로 만들었다. 전역 규칙(`~/.claude/CLAUDE.md`)은 "작업 디렉토리에 `AGENTS.md` 또는 `CLAUDE.md`가 있으면 반드시 먼저 읽는다"인데 `README.md`는 그 트리거에 걸리지 않아, 이 디렉토리에서 작업하는 AI가 사용 계약을 안 읽고 지나갈 수 있었다. 내용에도 "선생님/콘텐츠와 무관한 공용 자산"이라는 범위 선언이 없어 teacher source와의 경계가 안 적혀 있었다.
- 조치: `README.md`를 `AGENTS.md`로 바꾸고 "선생님·차시·콘텐츠 무관"이라는 범위 선언, common에 둘 것과 두지 말 것의 판단 기준, 사용 절차, 네이밍/조회 규칙을 앞쪽에 배치했다.
- 규칙화 메모: 아직 1회. 반복되면 "**AI가 따라야 할 디렉토리 규칙은 `README.md`가 아니라 `AGENTS.md`에 쓴다.** `README.md`는 사람용 소개로만 쓰고, 제약·계약·사용 절차는 자동으로 읽히는 파일에 둔다"를 최상단 `AGENTS.md`에 제안 후보.

### [component-fragment-not-self-verifiable] 컴포넌트 template.html이 css/js를 안 물고 있어 단독으로 열면 아무것도 적용되지 않음

- 대상: content-harness-pipeline/source/common/components/*/template.html
- 분류 태그: component-fragment-not-self-verifiable
- 상태: 열림
- 발생 횟수: 1
- 최초 발생일: 2026-08-08
- 최근 발생일: 2026-08-08
- 사례:
  - 2026-08-08: "template.html에서 css나 js가 import 안되어있어 적용이 안되고있는거 아니야?" `template.html`은 최종 단일 HTML로 inline할 마크업 조각이라 `<head>`가 없는 것이 설계 의도(`docs/reusable-source-design.md` 7.5)지만, **파일만 봐서는 그 의도도, 무엇을 함께 넣어야 동작하는지도 알 수 없었다.** 실제로 브라우저에서 직접 열면 스타일도 동작도 없다.
- 조치: (1) 각 `template.html` 맨 위에 필요한 CSS/JS와 runtime 호출을 적은 주석 헤더를 넣어, 조각만 봐도 무엇과 함께 써야 하는지 알 수 있게 했다. (2) 컴포넌트마다 `preview.html`을 만들어 **그 컴포넌트 하나만** 띄우고 상태를 버튼으로 밟아볼 수 있게 했다(`_shared/preview.css`, `_shared/preview.js` harness). 확인 경로가 두 층이 됐다 — `preview.html`은 컴포넌트가 혼자 성립하는지, `example/index.html`은 조합이 성립하는지 본다.
- 규칙화 메모: 아직 1회. 반복되면 "**단독으로 실행되지 않는 조각 파일은 맨 위 주석에 의존물과 사용법을 적는다** — 조각인지 완성 파일인지가 파일 자체에서 읽혀야 한다"를 `content-harness-pipeline/AGENTS.md`에 제안 후보.
  - 부수 효과: preview가 무엇을 로드하는지가 **그 컴포넌트의 실제 의존 목록**이 됐다. `debug-jumper`만 `scene-controller`를 함께 싣고 나머지는 자기 것만 싣는다. 편의로 전부 로드하면 이 정보가 사라지므로 그렇게 하지 않는다.

### [component-missing-layout-contract] 공용 컴포넌트 루트에 position/z-index가 없어 배치 지시가 무시되고 배경 뒤에 깔림

- 대상: content-harness-pipeline/source/common/components/ticket-button/style.css, runs/2026-08-11_dfbc1027/output/index.html
- 분류 태그: component-missing-layout-contract
- 상태: 열림
- 발생 횟수: 1
- 최초 발생일: 2026-08-11
- 최근 발생일: 2026-08-11
- 사례:
  - 2026-08-11: "html이 다음으로 가는 버튼이 없어서 못간다 input에는 있을텐데". 실제로는 버튼이 **있었고** 라벨도 원문 그대로였다(`모양의 힘으로 색칠하기` 등, `c-ticketButton` 19개). 보이지 않은 이유는 `ticket-button/style.css`에 `position`과 `z-index`가 없어서다. builder는 배치를 `style="left:720px; top:800px"`로 줬지만 `position:static`이라 그 값이 무시되고 요소가 (0,0)에 흘렀으며, `.c-bg`가 `z-index:1`이라 배경 이미지가 버튼 위를 덮었다. `elementFromPoint`로 버튼 중심을 찍으면 `c-bg`가 잡힌다 — 보이지도 눌리지도 않으므로 콘텐츠가 첫 화면에서 더 진행되지 않는다.
- 원인: 나머지 5개 컴포넌트(`speech-bubble`, `keypad`, `feedback-layer`, `topbar`, `debug-jumper`)는 모두 자기 `style.css`에 `position:absolute` + `z-index`를 갖는데 `ticket-button`만 없었다. **`preview.html`과 `example/index.html`이 이 결함을 가렸다** — 두 확인 페이지 모두 `.previewStart`/`.previewBack` 같은 페이지 전용 class로 버튼을 따로 배치하고 있어서, 컴포넌트가 스스로 배치되지 않는다는 사실이 드러나지 않았다.
- 조치: `ticket-button/style.css`에 `position:absolute; z-index:var(--z-interactive)`를 넣어 다른 컴포넌트와 계약을 맞췄다. `component.md`에 "위치는 사용처가 `left`/`top`으로만 준다"를 명시했다. `source/common/components/CLAUDE.md` 규칙에 "stage 위에 얹는 컴포넌트 루트는 자기 `position`과 `z-index`를 갖는다"를 추가했다.
- 규칙화 메모: 아직 1회. 반복되면 "**확인 페이지가 컴포넌트 대신 해주는 일이 있으면 그 결함은 확인 페이지에서 드러나지 않는다** — preview는 위치·크기를 대신 잡아주지 않는다"를 컴포넌트 작성 규칙으로 승격 제안한다. [component-fragment-not-self-verifiable]와 같은 계열(컴포넌트 원본의 불완전함이 실제 사용 시점에야 드러남)이므로 3회째에는 두 항목을 묶어 검토한다.

### [stage-copies-neighbor-run-output] builder가 옆 run 디렉토리의 완성 산출물을 읽어 그대로 이어붙임

- 대상: content-harness-pipeline/runs/2026-08-11_dfbc1027-opus/output/index.html, stages/scripts/codex_client.py (ClaudeClient), prompts/common_html_contract.md
- 분류 태그: stage-copies-neighbor-run-output
- 상태: 열림 (프롬프트 층 금지 조항만 추가, 강제는 미구현)
- 발생 횟수: 1
- 최초 발생일: 2026-08-11
- 최근 발생일: 2026-08-11
- 사례:
  - 2026-08-11: 같은 planner/asset으로 builder를 opus로 다시 돌렸는데, 산출물이 **직전 sonnet 산출물의 확장본**이었다. sonnet 1251줄이 opus 1315줄 안에 **한 줄도 빠짐없이 그대로** 들어 있고(difflib 일치 100%), 늘어난 64줄은 이번에 새로 요구한 debug 패널이었다. 소요 시간도 1543초 → 236초로 6.5배 빨랐다. 스프라이트 좌표(`background-size:1629px 543px; background-position:-30px -165px`)처럼 모델이 독립적으로 같은 값을 낼 수 없는 계산까지 문자 단위로 같았다.
- 원인: `--claude-html-stages` 경로는 CLI를 `cwd=project_dir` + `--permission-mode acceptEdits`로 띄운다. stage는 `runs/` 아래 **다른 run의 완성 HTML을 자유롭게 읽을 수 있다.** 정보 차단 규칙(`content-harness-pipeline/CLAUDE.md`)은 "stage가 임의로 run 디렉토리를 훑어 읽게 만들지 않는다"라고 적혀 있지만, 그건 **runner가 payload를 좁게 준다**는 뜻이었고 파일시스템 접근 자체는 막혀 있지 않았다. codex 경로(`--dangerously-bypass-approvals-and-sandbox`)도 같다.
- 영향: 모델 비교가 성립하지 않는다. 더 중요하게는 **직전 산출물의 결함이 그대로 상속된다** — 이번에도 `[component-missing-layout-contract]`의 깨진 CTA CSS가 글자 그대로 옮겨왔다. 입력(컴포넌트 원본)을 고쳐도 결과가 따라오지 않으므로, 파이프라인을 고쳐서 결과를 개선한다는 전제 자체가 무너진다.
- 조치: `prompts/common_html_contract.md` "공통 금지"에 "다른 run 디렉토리의 산출물을 읽거나 베끼지 않는다"를 넣었다. 프롬프트 층 조항이므로 강제력은 없다.
- 규칙화 메모: 아직 1회. 반복되면 프롬프트가 아니라 **실행 격리**로 올린다 — stage를 그 run에 필요한 파일만 있는 임시 작업 디렉토리에서 돌리고, 끝난 뒤 산출물을 run 디렉토리로 옮기는 방식. 검증 방법도 함께 남긴다: 같은 입력으로 두 번 빌드해 `difflib`로 라인 일치율을 재고, 90%를 넘으면 베낀 것으로 본다.

### [cta-label-overlaid-not-baked] 고정 문구 CTA를 빈 표면으로 만들고 글자를 HTML로 얹어 완성도가 안 나옴

- 대상: content-harness-pipeline/prompts/planner_system.md(이미지 안의 텍스트 절), source/common/components/ticket-button/, production/1-2/08/assets/activity-cta-body.webp
- 분류 태그: cta-label-overlaid-not-baked
- 상태: 열림
- 발생 횟수: 1
- 최초 발생일: 2026-08-11
- 최근 발생일: 2026-08-11
- 사례:
  - 2026-08-11: "CTA가 한번에 이미지로 구워지지 않는 문제도 있어. 결과를 보았을 때 이미지 위에 글을 쓰는 결과가 나왔었다." CTA asset(`activity-cta-body.webp`)은 3-state 스프라이트인데 안이 **완전히 빈 알약**(장식은 왼쪽 스파클 하나뿐)이고, 라벨은 `.c-ticketButton [data-slot="label"]`에 HTML 텍스트로 얹힌다. 타이틀·도장은 글자를 구워 완성도가 나오는데 CTA만 CSS 글자라 같은 화면 안에서 재질이 어긋난다.
- 검증 (2026-08-11, 발생 횟수에 포함하지 않음 — 사용자 지적이 아니라 내가 돌린 테스트 run의 관찰): `runs/2026-08-11_65126dad`(2학년 시간 차시)에서 **CTA 문제가 한 단계 더 나쁜 형태로 재현**됐다. 라벨을 오버레이한 게 아니라 **planner가 CTA·보기 카드 표면을 `asset_plan`에 아예 넣지 않았다**(19개 중 0개). teacher source에 `ctas` 참조 2개와 `surface-choice-plaque`가 있고 `must_follow: true`였는데도 계획 단계에서 빠졌다. 결과적으로 `[시작하기]`는 흰 알약, `[3시][4시][5시]`는 노란 CSS 사각형으로 나왔고 `visual_qa`도 "3 buttons are present and 100% look like generic rounded web buttons"로 잡았다. **즉 이 문제의 상류는 굽기 판정이 아니라 `asset_plan`에 CTA 항목이 생성되지 않는 것이다.** 굽기 규칙만 고쳐서는 asset이 없으므로 아무 효과가 없다.
- 원인: `planner_system.md`의 굽기 판정 3조건 중 ②"타이포그래피 자체가 그 asset의 디자인인 자족적 그래픽"과 ③"선택·입력·판정·측정의 대상이 아니다"에서 CTA가 양쪽으로 읽힌다. 예시 목록("정답/실패 도장, 인트로·완료 타이틀, 장면 속 간판·표지")에 CTA가 없고, 같은 문서의 "배경·표면·컴포넌트 asset은 기본적으로 [코드로 얹는다]에 해당"이 CTA를 표면으로 끌어간다. 굽기 완성도 기준 이미지(`asset_examples/`)에도 CTA 예시가 없어 합격선 자체가 전달되지 않는다.
- 영향: [cta-text-offcenter-padding]·[cert-cta-button-two-lines]가 **같은 뿌리의 하류 증상**이다. 둘 다 "장식 있는 고정 표면에 가변 폭 텍스트를 얹느라 패딩·줄바꿈·폰트를 손으로 맞추는" 일이었다. 라벨을 구우면 이 조정 자체가 사라진다.
- 조치 (2026-08-11): **사용자 결정 = "고정 문구 CTA만 굽기".** 씬을 여닫는 CTA(시작/완료/다음 차시)는 굽고, 한 씬에서 반복되는 진행 버튼(확인/다음)은 `ticket-button` + HTML 라벨을 유지한다. 반영: ①`planner_system.md` 굽기 판정 ②의 예시에 "씬을 여닫는 CTA" 추가, ③을 "**읽고 고르거나 값을 매기는** 대상이 아니다 — 눌러서 다음으로 가는 것은 해당하지 않는다"로 명확화(클릭 대상이라는 이유로 빠지던 경로를 막음). ②"굽는 문구와 얹는 문구의 경계" 조항 신설 — 기준은 **그 문구가 그 화면을 특정하는가**. ③"배경·표면·컴포넌트 asset은 기본적으로 코드로 얹는다"에서 컴포넌트를 분리하고 "몸체를 공유한다는 이유만으로 고정 문구를 오버레이로 내리지 않는다"를 붙임(이게 CTA를 표면으로 끌어가던 문장). ④`ticket-button/component.md`의 `Use when`을 "반복되는 진행 버튼"으로 좁히고 "라벨을 구운 CTA는 이 컴포넌트를 쓰지 않는다" 절 추가. ⑤`asset_generator_system.md`에 "문구를 굽는 asset은 상태 스프라이트로 만들지 않는다" 금지 추가.
- 주의: 굽는 CTA가 `ticket-button`을 쓸 수 없는 이유는 그 몸체가 `[normal|hover|active]` 3-state 스프라이트이고 상태 전환이 `background-position`이기 때문이다. 라벨을 구우면 프레임 3장에 같은 글자를 다시 그려야 해서 누를 때 글자가 어긋난다. 크기도 `868x140` 고정이라 문구 길이에 맞춘 이미지를 못 담는다.
- 미해결: (a) craft example에 **CTA 기준 이미지가 없다** — 굽기 판정은 정해졌지만 합격선은 일반 규칙에만 의존한다. 구운 CTA가 나오면 `source/common/craft-examples/`에 올린다. (b) `production/1-2/08`은 손대지 않았다. 19개 버튼이 여전히 오버레이 방식이며, 그 차시의 `CLAUDE.md` asset 규칙도 그대로다.
- 규칙화 메모: 남은 충돌 지점. ①`ticket-button/component.md`의 `Text policy: HTML text overlay`와 `Slots: label` — 라벨을 구우면 이 컴포넌트는 가변 라벨 전용으로 좁아진다. ②`production/1-2/08/CLAUDE.md`의 "`*-body.png`는 빈 면을 남긴다" 규칙. ③`rendered_text` 대조 — 구운 문구는 HTML에서 사라지므로 `alt_text` 경로(planner_system.md:129, common_html_contract.md:55)가 실제로 동작하는지 확인이 필요하다. 이 대조는 Python이 아니라 content_eval LLM이 하므로 기계적 보장이 없다.

### [source-asset-role-collision] 같은 이미지가 "복사해서 쓰는 컴포넌트 asset"과 "참조만 하는 화풍 참조" 양쪽에 있어 design_review가 오판함

- 대상: content-harness-pipeline/source/baek-seungyong/assets/cta/, source/common/components/ticket-button/assets/, stages/scripts/style_references.py
- 분류 태그: source-asset-role-collision
- 상태: 규칙화됨(코드) — 해석 단계에서 REJECT
- 발생 횟수: 1
- 최초 발생일: 2026-08-11
- 최근 발생일: 2026-08-11
- 사례:
  - 2026-08-11: `runs/2026-08-11_65126dad`의 design_review가 **[high] "must_follow 참조 CTA를 output asset으로 직접 복제했다"** 를 냈다. 사용자가 "복사를 금지해야 하는데 방법이 있을까"라고 물어 확인에 들어갔다. sha256 대조 결과 `output/assets/activity-cta-body.webp`가 `source/baek-seungyong/assets/cta/cta-activity-body.webp`와 **바이트 동일**한 것은 사실이었다.
- 원인: **design_review의 판정은 사실 관찰은 맞고 귀속이 틀렸다.** 그 파일은 화풍 참조가 아니라 `source/common/components/ticket-button/assets/activity-cta-body.webp`에서 왔고, 그 복사는 `prompts/common_html_contract.md:74`가 **지시한** 동작이다("컴포넌트에 `assets/`가 있으면 그 파일을 `output/assets/`로 복사하고"). mtime이 09:06:47로 run 시작(14시) 이전인 것이 근거다 — 컴포넌트 디렉토리에서 메타데이터를 보존한 채 복사됐다.
  진짜 결함은 **내가 teacher source를 만들 때 08 asset을 그대로 복사하면서, 이미 컴포넌트가 소유한 파일을 화풍 참조에도 넣은 것**이다. 두 디렉토리의 계약이 정반대다 — 컴포넌트 `assets/`는 "복사하라", teacher `assets/`는 "참조만 하고 복사하지 마라". 한 파일이 두 계약을 동시에 만족할 수 없다.
- 조치: ①`baek-seungyong/assets.md`의 `cta-activity-body` 항목을 `Status: deprecated`로 바꿔 catalog 스캔에서 제외(파일은 삭제하지 않음, 사용자 확인 대기). ②`style_references.find_component_asset_conflicts()`를 추가해 **해석 단계에서 REJECT**. 파일명이 아니라 **내용 해시**로 비교한다 — 실제 충돌이 `activity-cta-body` vs `cta-activity-body`로 이름이 달랐다. `validate.py --artifact input`에서 run 전에 잡힌다. 검증: 정상 input PASS(참조 16→15), 충돌을 명시로 되살리면 REJECT.
- 주의: **여기서 "output asset이 화풍 참조와 같으면 REJECT"라는 런타임 게이트를 만들면 안 된다.** 정당한 컴포넌트 asset 복사에서 영구 오탐이 난다. 금지해야 할 것은 복사가 아니라 **역할 중복**이고, 그건 run 때가 아니라 source를 만들 때 잡아야 한다.
- 규칙화 메모: 아직 1회지만 코드로 봉인했으므로 재발 시 자동 REJECT다. 사람이 지켜야 할 규칙으로는 승격하지 않는다 — `source/common/components/CLAUDE.md`의 "다음 차시에서 이걸 그대로 쓸까?"로 이미 common에 올라간 것을 teacher에 또 넣지 않는다는 뜻이고, 그건 해시 비교가 대신 판정한다. 연관: [cta-label-overlaid-not-baked](CTA asset이 asset_plan에 없어 생긴 빈자리와 같은 run에서 함께 관찰됨).
