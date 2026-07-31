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
- [feedback-as-character-bubble] · 횟수 5 · 규칙화됨 · solved-log.md#dialogue-as-speech-bubble-대사피드백을-표면-텍스트로-넣고-말풍선을-매번-새로-만듦-channel-렌더링-계약으로-통합 · 반영: prompts/builder_system.md "channel 렌더링 계약"의 `feedback` 절.
- [sequential-scene-choreography] · 횟수 3 · 규칙화됨 · solved-log.md#dialogue-as-speech-bubble-대사피드백을-표면-텍스트로-넣고-말풍선을-매번-새로-만듦-channel-렌더링-계약으로-통합 · 반영: prompts/builder_system.md "channel 렌더링 계약"의 dialogue 순차 beat 조항. (5회 미만이나 dialogue 계열로 통합 승격.)
- [character-asset-identity-alpha] · 횟수 9 · 규칙화됨 · solved-log.md#character-asset-identity-alpha-캐릭터-에셋이-포즈마다-다른-인물로-생성됨-정체성-부분 · 반영: AGENTS.md 문서 규칙이 아니라 파이프라인 구조로 강제 (planner_output.schema.json characters 엔티티 · runner.py patch merge/identity_context · design_review.py allowlist · planner/design_review/asset_generator 프롬프트). 원 항목 17회 중 알파 8회는 [character-asset-alpha-fringe]로 분리되어 열린 상태.

## 문제 로그

<!-- 새 항목은 이 아래에 추가한다. -->

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

- 대상: content-harness-pipeline/runs/2026-07-21_ch8c0718/output/index.html, content-harness-pipeline/runs/2026-07-22_ch8c0719/output/index.html
- 분류 태그: content-refine-learning-flow-integrity
- 상태: 열림
- 발생 횟수: 9
- 최초 발생일: 2026-07-21
- 최근 발생일: 2026-07-22
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

- 대상: content-harness-pipeline/runs/2026-07-08_ch802d08/output/index.html (`#s-b` submitB의 `showStamp(true, q.done, ...)`)
- 분류 태그: typeB-correct-note-card-unwanted
- 상태: 열림
- 발생 횟수: 1
- 최초 발생일: 2026-07-13
- 최근 발생일: 2026-07-13
- 사례:
  - 2026-07-13: 유형 B 정답 시 "정답!" 스탬프와 함께 하단에 초록색 카드('1시간', =`q.done`)가 같이 떠서, 스탬프만 나오게 카드를 없애달라고 요청.
- 조치: submitB 정답 분기의 `showStamp(true, q.done, 1300)`을 `showStamp(true, null, 1300)`으로 변경. `.stamp-fx-note:empty{display:none}` 규칙 덕에 note가 비면 카드가 렌더되지 않아 스탬프만 표시됨. (오답 안내 문구·타 유형은 유지)
- 규칙화 메모: 아직 1회. 참고: 유형 A는 정답 시 `q.note`(풀이 설명)를 카드로 보여줌 — 필요 시 동일하게 뺄지 별도 확인.

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

- 대상: content-harness-pipeline/runs/2026-07-08_ch802d08/output/index.html (`#s-story` `.book-page img.ill` vs `.book` 아트)
- 분류 태그: overlay-plane-perspective-mismatch
- 상태: 열림
- 발생 횟수: 1
- 최초 발생일: 2026-07-13
- 최근 발생일: 2026-07-13
- 사례:
  - 2026-07-13: 이야기 씬에서 책 아트(`storybook_base.png`)는 살짝 눕혀진 원근으로 그려져 있는데, 그 위에 얹은 삽화 사진(`.book-page img.ill`)이 정면으로 반듯이 선 사각형이라 책 지면 위에 붕 떠 보임("책은 눕혀져 있는데 사진은 서 있어서 안 맞아"). 사진을 눕히거나 책을 세우는 두 방향 중 어느 쪽이 나은지 문의.
  - 2026-07-13: (후속) 적용한 `rotate(-1.5deg)`(왼쪽 기울기) 때문에 사진 좌상단이 지면 금색 테두리 밖으로 나감. 오른쪽(시계방향)으로 3도 정도 기울여 달라고 요청 → `rotate(-1.5deg)`→`rotate(3deg)`로 변경해 좌상단을 지면 안으로 들임.
- 조치: 책은 raster 아트 에셋이라 세우려면 재생성+연쇄 재정렬 비용이 큼 → 대신 사진+오버레이를 함께 감싼 `#s-story .bp-left .ill-wrap`에 `transform:perspective(900px) rotateX(8deg) rotate(-1.5deg);transform-origin:center 68%`를 얹어 지면 면에 눕히고, `img.ill` 드롭섀도를 `0 6px 14px`→`0 3px 7px`로 줄여 '떠 있는 카드' 인상 제거. Playwright로 3페이지 렌더 검증(오버레이 `24`/`30분`도 사진과 함께 눕음, 오른쪽 지면 텍스트는 그대로 유지). 각도는 아트 지면 원근 실측 기반 시작값이라 ±3° 미세조정 여지 있음.
- 규칙화 메모: 아직 1회. [bg-anchor-alignment]와 같은 '아트에 요소 맞추기' 계열이나 remedy가 다름(위치 정렬이 아니라 오버레이 면의 원근/기울기 정합). 반복되면 "아트 표면(책 지면·모니터 유리 등) 위에 얹는 raster 오버레이는 그 표면이 그려진 원근/기울기에 맞춰 CSS transform으로 눕힌다. 아트 에셋 자체를 바꾸기보다 오버레이를 아트에 맞춘다" 규칙을 builder_system.md에 제안 후보.

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

- 대상: content-harness-pipeline/runs/2026-07-08_ch802d08/output/index.html (`#bigClock`, `#s-tut .wb-clock`, `#repairClock`)
- 분류 태그: bg-anchor-alignment
- 상태: 제안됨
- 발생 횟수: 6
- 최초 발생일: 2026-07-09
- 최근 발생일: 2026-07-13
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
- 규칙화 메모: **6회 → rule 승격 제안.** 교훈: **asset을 얹는 컨테이너는 `aspect-ratio`를 asset 원본 비율에 맞춰라 — 안 맞으면 `object-fit:contain`이 레터박스를 만들어 %좌표 오버레이가 어긋난다. 또 `background-size:cover` 배경의 앵커(원형 거치대 등)는 정적 %로 못 맞추므로, 원 지오메트리를 픽셀 측정해 런타임에서 cover 스케일·크롭을 계산하는 JS로 앉히고 resize에 재적용한다(intro의 `__placeBigClock`/복구의 `__placeRepairClock` 패턴 재사용).** 반영 위치: builder_system.md. 사용자 승인 대기.

### [motion-supporting-narration] 나레이션이 말하는 상황을 뒷받침하는 시각 액션이 없고 등장 애니메이션이 밋밋함

- 대상: content-harness-pipeline/runs/2026-07-08_ch802d08/output/index.html (`#s-problem` `#bigClock`, `.dlg-actor`)
- 분류 태그: motion-supporting-narration
- 상태: 열림
- 발생 횟수: 1
- 최초 발생일: 2026-07-10
- 최근 발생일: 2026-07-10
- 사례:
  - 2026-07-10: 인트로에서 선생님이 "큰일 났어! 시계가 고장 나서 시간이 뒤죽박죽이야!"라고 말하는데 **무엇이 큰일인지 보여주는 시각 액션이 없음**. 시계가 (CSS `.spin`으로) 처음부터 일정하게만 돌아, '정상이던 시계가 점점 빨라지며 고장 나는' 서사가 안 보임. 또 꼬마 사서 등장이 `.pop`(단순 튀어오름)이라 "그냥 생성되는" 느낌. 사용자가 (a)시계 정상→점점 빨라짐 표현 + 하이라이트, (b)등장 애니메이션 개선을 요청.
    - 조치: (a) `#bigClock`에서 CSS `spin` 제거하고 JS 컨트롤러(`__introClock`) 추가 — `startNormal`(느긋, 6s/바퀴) → beat0에서 `runaway`로 ease-in 가속(2.6s)해 폭주(0.24s/바퀴). 하이라이트는 경고 글로우(`clockPanicGlow` 펄스) + 진입 흔들림(`clockShake`, 배치 transform 유지). (b) `.pop` → `hero-in`(오른쪽에서 슬라이드+오버슈트 안착) + 착지 반짝임(`sparkOnEl`). __playProblemIntro/beat 컨트롤러에 연결.
- 규칙화 메모: 아직 1회. 반복되면 "대사가 상황·감정을 말하면(예: 위기·고장·성공) 그 상황을 보여주는 시각 액션을 동반하고 하이라이트한다(정적 나레이션 금지). 캐릭터 등장은 단순 pop/opacity가 아니라 방향성 있는 등장(슬라이드+오버슈트+착지 이펙트)으로" 규칙을 builder_system.md에 제안 후보.

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
- 발생 횟수: 3
- 최초 발생일: 2026-07-09
- 최근 발생일: 2026-07-13
- 사례:
  - 2026-07-09: 말풍선 위 `.who` 요약 라벨(`📢 도서관 고장 알림`, `🕑 깨진 전광판 안내`)이 바로 아래 대사와 같은 내용을 중복. 전광판 asset 위에 얹힌 문제 문구를 JS가 `전광판: … — 같은 시각의 시계는?`로 감싸, 이미 전광판 이미지로 표현된 맥락을 텍스트로 다시 명명함. 한 번의 피드백에 같은 성격의 사례 3건.
  - 2026-07-09: (재발/실적용) 사용자가 유형 A 화면의 `🕑 깨진 전광판 안내` 라벨과 `aPrompt`의 `전광판:` 접두어를 "AI가 자주 하는 의미 없는 설명"이라며 삭제 요청. 실제로 제거함.
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
- 발생 횟수: 3
- 최초 발생일: 2026-07-08
- 최근 발생일: 2026-07-31
- 사례:
  - 2026-07-08: 사용자가 인트로의 `시간이 뒤죽박죽! / 수학의 힘으로 도서관 시계를 수리하라!` 문구를 예시처럼 이미지 생성 타이틀로 만들고, 1번 후보를 인트로에 삽입하길 요청했다.
  - 2026-07-08: 사용자가 삽입된 생성 이미지를 화면 가운데에 오게 하고, 주변 화면을 어둡게 만들어 아직 시작하기 전이라는 느낌을 주길 요청했다.
  - 2026-07-31: run dfbc1027 인트로 제목이 다시 빈 제목판(`school-title-banner-body.png`) + HTML `<h2>` 오버레이로 나갔다. 사용자가 "글자까지 title 이미지로 제작하기로 하지 않았나"라고 지적. planner가 하나의 제목판 몸체를 intro·arithmetic·story·completion 4개 씬에 공용으로 계획하면서 문구를 가변으로 취급해 `negative_prompt`에 텍스트 금지를 넣었고, planner_system.md:124-129의 "고정 문구 = 이미지에 굽는다(인트로·완료 타이틀 명시)" 조항을 우회했다.
- 조치: 2026-07-08 건은 이미지 생성 후보 1번을 `output/assets/intro_title_time_repair_v1.png`로 삽입·중앙 정렬. 2026-07-31 건은 미조치(아래 규칙화 메모 참조).
- 규칙화 메모: 3회. 규칙 문구 자체는 planner_system.md:122-134에 이미 있으나 "몸체 하나를 여러 씬에 재사용"이라는 경로로 우회되고 있다. 반복되면 planner_system.md에 "제목판은 씬마다 문구를 구운 개별 asset으로 계획하고, 몸체 공용화를 이유로 고정 제목을 오버레이로 내리지 않는다" 조항을 추가하는 안을 제안 후보로 둔다.

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
- 발생 횟수: 12
- 최초 발생일: 2026-07-09
- 최근 발생일: 2026-07-31
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
- 규칙화 메모: **발생 12회 → rule 승격 제안.** 초안: "초등(저학년) 대상 콘텐츠는 본문/질문/힌트/**버튼(CTA)** 글자 clamp의 max와 vw 계수를 성인 기준보다 크게 잡는다(예: 본문 max ≥ 1.6rem, 주요 CTA max ≥ 1.8rem). 표면 박스/티켓 asset 위 텍스트도 동일 배율." 반영 위치: content-harness-pipeline/builder_system.md. 사용자 승인 대기.

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
- 발생 횟수: 2
- 최초 발생일: 2026-07-09
- 최근 발생일: 2026-07-09
- 사례:
  - 2026-07-09: 유형 B 보드의 문제 제목(`독서 교실이 8시에 시작해 9시에 끝났어요…`)이 코르크 배경 위에서 진갈색(`color:#5a3b1b`)이라 잘 안 보임. 다른 색으로 요청.
    - 조치: 제목을 크림색 라벨 칩(`#s-b .b-qtitle`, `background:rgba(255,248,232,.94)` + 진한 적갈색 글자 `#7a1f10`)으로 감싸 코르크 배경과 무관하게 고대비 확보.
  - 2026-07-09: "✨ 카드를 끌어서 놓아요 ✨" 큐가 갈색 계열(`color:#b5791b`)이라 나무 바닥/러그 배경 위에서 잘 안 보임. 더 하이라이트 필요.
    - 조치: 큐를 어두운 알약 배경(갈색 그라디언트)+금색 글자(`#ffe89a`)+내부 금테/글로우 box-shadow로 변경하고 bounce에 글로우 맥동 추가. 배경과 무관하게 대비 확보.
  - 2026-07-09: (후속) 큐가 실제 화면에서 아예 안 보인다고 지적. 원인은 대비가 아니라 **CSS 애니메이션 override로 인한 opacity 미해제**: 큐 엘리먼트에 `enter d3`가 있어 `.scene .enter{opacity:0}`로 시작하는데, opacity를 1로 올리는 `enterUp` 애니메이션이 내가 큐에 준 `cueBounce`(명시도 `#s-tut ...`가 더 높음)에 덮여 실행되지 않음 → opacity 0 고정. (검증 스크린샷은 opacity를 강제로 켜서 버그가 가려져 있었음.)
    - 조치: `#s-tut .tut-drag-cue`에 `opacity:1` 명시. opacity 강제 없이(실제 CSS만) virtual-time 렌더로 큐 표시 확인.
- 규칙화 메모: 아직 1회(가독) + 별개의 가시성 버그 1건. 반복되면 (a) "유도 큐/힌트는 고대비 칩으로", (b) "`.enter`(entrance opacity:0)를 가진 엘리먼트에 별도 `animation`을 주면 `enterUp` 리빌이 덮여 안 보일 수 있으니 opacity를 명시하거나 `.enter`를 빼거나 애니메이션을 합성" 규칙을 builder_system.md에 제안 후보.

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

- 대상: content-harness-pipeline/runs/2026-07-08_ch802d08/output/index.html (`#s-b .kb-blank`)
- 분류 태그: weak-input-affordance
- 상태: 열림
- 발생 횟수: 1
- 최초 발생일: 2026-07-09
- 최근 발생일: 2026-07-09
- 사례:
  - 2026-07-09: 유형 B의 정답 입력 `?`칸(`.kb-blank`)이 눌러서 선택하는 요소인데, 활성(`.active`) 전에는 아무 시각 신호가 없어 선택 가능한지 알기 어려움. 글로우/하이라이트로 선택 가능함을 알려야 함.
- 조치: `#s-b .kb-blank:not(.filled):not(.active)`에 상시 골드 글로우 펄스(`kbInvite`) 추가. 활성/입력완료 시에는 애니메이션이 멈추고 각각 `.active` 글로우/`.filled` 상태로 전환. (튜토리얼 빈 슬롯 `slotPulse`와 같은 상시 pulse 어포던스 계열)
- 규칙화 메모: 아직 1회. `[weak-drag-affordance]`(드래그 소스/타깃 유도)와 묶어 "탭·드래그 등 상호작용 대상은 유휴 상태에서도 상시 pulse/glow로 조작 가능함을 알린다" 규칙으로 발전 가능. 반복되면 builder_system.md에 제안 후보.

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
- 발생 횟수: 1
- 최초 발생일: 2026-07-09
- 최근 발생일: 2026-07-09
- 사례:
  - 2026-07-09: 유형 C 정답 완료 시 스펙(md Scene 3 항목 5)은 "모니터 화면이 밝아지며 [시스템 재부팅 완료!] 메시지 출력"인데, 구현은 mon-status 한 줄 텍스트만 `q.done`으로 바꾸고 문제를 그대로 둔 채 넘어감. 또 진행중 표시(재부팅 중 `…`)가 정적이라 진행감이 없음.
- 조치: `checkC`를 "화면(`.mon-screen.rebooted` glow)이 밝아지며 문제/트레이를 지우고 `✅ 시스템 재부팅 완료!` 메시지만 2초 출력 후 다음 문제"로 변경. 마지막 문제는 `nextC`에서 중복 메시지 제거하고 곧장 수리 아웃트로로. 상태문구 끝 점을 `. / .. / ...` 반복(`startMonLoading`/`stopMonLoading` + `.mon-status .dots` 고정폭)으로 진행중 연출 추가.

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

- 대상: content-harness-pipeline/runs/2026-07-08_ch802d08/output/index.html (`#s-quiz #btnToCert`)
- 분류 태그: cta-reveal-reflow-shift
- 상태: 열림
- 발생 횟수: 1
- 최초 발생일: 2026-07-10
- 최근 발생일: 2026-07-10
- 사례:
  - 2026-07-10: 마무리 퀴즈에서 정답을 맞히면 하단 `인증서 받으러 가기` 버튼(`#btnToCert`)이 `.hidden` 해제되며 나타나는데, 이 버튼이 `.center-col`(transform으로 세로 중앙정렬된 flex 컬럼)의 flex 자식이라 나타나는 순간 컬럼 높이가 커져 퀴즈(문제 plaque+보기)가 위로 밀려 올라감. 사용자가 "밀어 올리지 말고 CTA를 오버레이로 위에 덮으라"고 지적.
- 조치: `#btnToCert`를 `.center-col` flex 흐름에서 빼내 다른 씬 전환 CTA와 동일한 절대배치 `.bottom-bar`(position:absolute; bottom:3.5%; z-index:16) 오버레이로 이동. 나타나도 컬럼 높이가 변하지 않아 퀴즈가 그대로 유지되고 버튼은 위(z-index)로 떠서 덮음. `hidden` 토글은 버튼 자체에 유지되어 JS 변경 불필요.
- 규칙화 메모: 아직 1회. 반복되면 "정답/완료 시 나중에 나타나는 CTA·요소는 중앙 정렬(flex/translate) 컨테이너의 흐름에 넣지 말고, 절대배치 오버레이(`.bottom-bar` 등)로 배치해 reflow로 기존 콘텐츠가 튀지 않게 한다" 규칙을 builder_system.md에 제안 후보. (`[action-control-on-art-surface]`의 'CTA 배치' 계열)

### [unwanted-celebration-fx] 특정 씬에서 원치 않는 축하 이펙트 제거 요청

- 대상: content-harness-pipeline/runs/2026-07-08_ch802d08/output/index.html (`goldBurst`, `#s-cert` 진입)
- 분류 태그: unwanted-celebration-fx
- 상태: 열림
- 발생 횟수: 3
- 최초 발생일: 2026-07-10
- 최근 발생일: 2026-07-10
- 사례:
  - 2026-07-10: 인증서(`#s-cert`) 진입 시 화면 아래에서 위로 ✨🌟💫 아이콘이 쏟아져 올라가는 효과(`goldBurst`, `.particle floatUp`)를 지워달라고 요청. (fireworks 방사형 스파크·fanfare 사운드는 별개로 유지)
  - 2026-07-10: (후속) 같은 효과를 마무리 퀴즈(`#s-quiz`) 정답 시에도 지워달라고 요청.
  - 2026-07-10: (후속) 유형 C에서 복구 씬으로 넘어갈 때(`checkC`→`showSceneById('s-repair')` 진입, `goldBurst(20)`)의 효과도 지워달라고 요청.
- 조치: 인증서 진입(btnToCert)·퀴즈 정답 분기(`.quiz-op`)·유형 C→복구 씬 진입에서 `goldBurst()` 호출 제거(fanfare·fireworks·sparkOnEl 등은 유지). goldBurst는 아직 복구 씬 2곳(messy→clean 배경 전환 `goldBurst(16)`·복구 완료 celebrate `goldBurst(16)`)에 남아 있음 — 추가 제거는 확인 후 진행.
- 규칙화 메모: 아직 1회. 반복되면 "공용 축하 이펙트(goldBurst/fireworks 등)는 씬별로 on/off를 명시적으로 관리하고, 특정 씬에서 빼달라는 요청 시 같은 이펙트의 다른 호출부까지 함께 점검한다" 규칙을 builder_system.md에 제안 후보.

### [spec-interaction-flow-mismatch] 원본 기획의 화면 흐름/상호작용을 임의로 다르게 구현

- 대상: content-harness-pipeline/runs/2026-07-08_ch802d08/output/index.html (`#s-story` 마무리 퀴즈 흐름)
- 분류 태그: spec-interaction-flow-mismatch
- 상태: 열림
- 발생 횟수: 1
- 최초 발생일: 2026-07-10
- 최근 발생일: 2026-07-10
- 사례:
  - 2026-07-10: 원본 기획(`2학년_8차시(시간)_임상현_no_img.md` 활동3 Scene2)의 마무리 퀴즈는 "갤러리를 **모두 넘겨보면** 꼬마 사서가 톡 튀어나오며 **돌발 팝업 퀴즈**를 그 자리에 띄우고, 맞히면 게이지 100%+인증서 유도" 구조인데, 구현본은 `[마무리 퀴즈 풀러 가기]` 버튼으로 **별도 s-quiz 씬 이동**이었음. 사용자가 원본대로 책 위 팝업 퀴즈(이미지 겹침 허용)로 바꾸고 맞히면 `[인증서 받으러 가기]`가 나오도록 요청.
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
- 상태: 제안됨 (5회 도달, 2026-07-31 rule 승격 제안 — 사용자 판단 대기)
- 발생 횟수: 5
- 최초 발생일: 2026-07-31
- 최근 발생일: 2026-07-31
- 사례:
  - 2026-07-31: content critique에서 무작위 C·D의 step1/step2가 서로 다른 operands를 생성하고, 도입·모양 찾기 재진입 초기화가 불완전하며, 수리 이야기 도입 질문이 즉시 숨는 문제를 지적했다. 또한 페인트 색·모양 대응 설명의 순서가 세기 문항 뒤로 밀렸고, 산술 도형의 추가·삭제가 최종 상태로만 보이며, 오답·도움말·3회 오답 이후 진행이 학습자의 다음 행동을 충분히 안내하지 못했다. 고정 진행률과 `O` 제출 라벨, 자유 그리기 `버튼` CTA도 현재 상태와 조작 의미를 명확히 전달하지 못했다.
  - 2026-07-31: 후속 content critique에서 다음 차시 대상이 주입되어도 버튼이 항상 disabled인 문제, 대부분 문항의 개념 설명·재시도 안내 부족, ①·② 대사와 페인트 추가·삭제 사건의 합침, 보수 확인과 세 수 계산이 고정 A→D 순회로 분리된 문제, 세 번째 오답 뒤 정답 위치 번호·후속 행동 부족, 목록으로 미완료 단계를 건너뛰는 문제를 지적했다. 키패드 `O`, 자유 그리기 `버튼` 라벨도 조작 의미가 불명확하다고 재차 지적했다.
  - 2026-07-31: 이번 content refine packet에서 독립 실행 환경의 `나가기` 비활성, 문항별 근거·단계형 힌트 부족과 자동 전환, 자유 그리기 완료 CTA의 의미 없는 `버튼` 라벨, 표지판별 예측 질문 단계 축약, 계산 성공과 담장 작업 진행·자유 그리기 해금의 연결 부족을 지적했다.
  - 2026-07-31: **(실사용 관측)** `production/1-2/08/index.html` 모양 찾기에서 `■모양 2개`를 다 찾았는데 다음 모양(`●`)으로 넘어가지 않고 진행이 멈춘다고 지적. 위 네 사례가 "자동 전환 제거 → 원문 표면을 직접 눌러 진행"으로 여러 번 방향을 튼 결과, `selectHotspot`이 `found.size===2`에서 `showFeedback(..., advanceSearch)`를 부르고 `showFeedback`은 `feedbackSpeech`를 눌러야만 `completeFeedback→advanceSearch`가 돌게 되어 있다(index.html:732·909). 즉 진행 조건이 "보이지 않거나 누를 수 있는지 알 수 없는 말풍선 클릭" 하나에 묶여 있어 실제로는 데드엔드로 보인다. 앞선 조치들이 만든 **수동 진행 게이트가 검증(Playwright hook)에서는 통과하지만 사람 조작에서는 막히는** 형태의 회귀다. (미조치 — `production/1-2/08/todo.md` 17번으로 등록)
  - 2026-07-31: 후속 content refine packet에서 무작위 문제 풀이 뒤 가시적인 다음 조작 부재, 모양 찾기 hotspot 밖 클릭 무반응, 세 번째 오답 자동 공개를 직접 정답처럼 처리하는 상태 혼동, 자유 그리기 최소 참여 조건·완료 장면 결과 보존 부족, 문항별 계산·관찰 근거 피드백 부족을 지적했다. `다음 문제`·`자유 그리기로 이동`·`그림 완성하기` 같은 새 가시 문구 제안은 planner 외 문구 추가 금지와 충돌하므로 기능·상태·기존 원문 표면으로 해결해야 한다.
- 조치: **2026-07-31 수정·검증 완료.** 무작위 C·D는 문제 묶음별 operand 객체를 만들어 step1/step2가 같은 수를 공유하게 했고, 도입·모양 찾기는 재진입 때 배경·캐릭터 위치/pose·대사 index·숨김 상태·CTA·입력·타이머를 초기화한다. 모양 찾기 뒤 `페인트 색깔마다 모양이 달라요`→`● ■ ▲ 모양`을 먼저 순차 노출한 다음 세기 문항을 시작하도록 storyboard 순서를 복원했다. 산술 튜토리얼은 10개 등장, 7→3 추가, 10→2 추가, 12→2 삭제→3 삭제를 DOM 상태 변화로 순차 실행하고 애니메이션이 끝날 때까지 키패드를 disabled로 둔다. 세기·산술·무작위 문항은 오답 때 현재 도형/operand를 강조하고, 3회 오답 뒤 정답을 표시하되 기존 `O` 조작으로 직접 확인해야 다음 문항으로 넘어가게 했다. 제작자용 생성 규칙 도움말은 현재 operands의 중간식으로 교체했고, 상단 게이지를 문항마다 갱신한다. 자유 그리기는 도형이 1개 이상 놓이기 전 완료 CTA를 disabled로 유지하며, 수리 이야기는 제목·`모양을 길에서 본 적이 있나요?`를 첫 beat로 실제 노출한 뒤 표지판을 연다. 원문 보존 계약 때문에 critique가 제안한 `확인`·`그림 완성하기` 같은 새 라벨은 적용하지 않고 기존 `O`·`버튼` 원문을 유지했다. 검증: planner rendered_text·문항·보기 100개 누락 0, JS 구문·중복 DOM id·asset·QA scene·고정 캔버스 계약 정상. Playwright에서 intro/shape 재진입 reset, 페인트 설명 선행, 산술 입력 잠금·순차 변화, C·D operand 공유, 세 종류 3회 오답→정답 확인, 빈 그리기 완료 차단, 수리 이야기 첫 beat를 확인했고 console/page 오류는 0건이었다. Visual QA 캡처 8장도 broken image·overflow·text clipping·overlap 0건이며, 자동 REJECT 한 건은 공통 계약상 필수인 `#viewport {position:fixed; inset:0}`를 100% fixed overlay로 오인한 기존 휴리스틱 false positive다.
  - 2026-07-31 후속 조치: 다음 차시 버튼은 `nextLessonUrl`·`onNextLesson` 존재를 초기화·완료 진입·호스트 갱신 이벤트·주기 동기화에서 다시 검사해 활성화하고, 종료 수단이 없으면 나가기 버튼을 비활성화한 채 완료 화면을 유지한다. 목록은 실제로 해제된 단계만 이동 가능하게 했다. 도입과 산술의 ①·② 대사, 페인트 추가·담장 이동·삭제 사건을 독립 beat로 분리해 각 확인 뒤에만 도형 모션과 문항을 연다. 무작위 문제는 런타임에서 A→같은 A·B를 쓰는 C 또는 B→같은 C를 쓰는 D 묶음 하나를 선택하고, 정답·세 번째 오답 뒤에는 중간값 10 식을 보여 준 뒤 자동 진행한다. 모양 찾기 세 번째 오답에는 두 정답 위치 번호를 표시하며, 키패드 강제 공개도 자동 진행으로 통일했다. 보이는 `O`·`버튼`은 공통 원문 계약 때문에 그대로 두고 각각 `확인`·`그림 완성하기` 접근성 라벨을 추가했으며, 자유 그리기 도형·색 `aria-pressed`를 상태와 동기화했다. 효과음과 대사·문항·안전 이야기 내레이션은 모두 소리 조절 상태를 따른다. 검증: planner 텍스트 127개(고유 102개) 누락 0, JS 구문·중복 DOM id·asset·8개 QA scene·고정 캔버스 계약 정상. Playwright에서 host route 활성화, 메뉴 잠금, 산술 독립 beat, 모양 정답 번호, 연결된 무작위 A→C operands를 확인했고 page error는 없었다.
  - 2026-07-31 이번 조치: `나가기`는 호스트 callback·부모 frame·opener를 우선 사용하고 독립 실행에서는 차시 시작 화면으로 돌아가는 fallback을 연결해 항상 활성화했다. 모양 찾기는 오답 2회에 정답 윤곽, 3회에 위치 번호와 정답 피드백을 공개하고, 모양 찾기·세기·산술·무작위 문제는 정답/자동 정답 뒤 원문 피드백 또는 중간식을 직접 눌러야 다음 문항으로 진행하도록 자동 전환을 제거했다. 무작위 문제 하단에는 기존 도형 asset 3개로 담장 작업 진행을 표시해 계산 성공과 자유 그리기 해금을 연결했다. 수리 이야기는 원·사각형·삼각형마다 `무슨 표지판일까요?` 예측 beat를 거친 뒤 설명을 공개한다. 자유 그리기 확인에는 사용한 도형·색 조합을 텍스트 추가 없이 asset 표본으로 요약한다. critique의 보이는 `그림 완성하기` 라벨은 planner에 없는 문구를 새로 노출하지 못하는 공통 원문 계약이 우선하므로 기존 `버튼`을 유지하고 이미 있던 `aria-label="그림 완성하기"`를 보존했다. 검증: planner rendered_text·문항·보기·정답·피드백 고유 102개 누락 0, JS 구문·중복 DOM id·asset 34개·8개 QA scene 정상. Playwright에서 대사 표면 진행, 피드백 수동 진행, 무작위 3단계 담장 진행과 수동 전환, 자유 그리기 요약, 표지판 예측 3회, 독립 실행 나가기 fallback을 확인했고 console/page 오류는 0건이었다. Visual QA는 broken image·overflow·text clipping·overlap 0건이며, REJECT는 고정 캔버스 계약의 필수 `#viewport`를 fixed overlay로 오인한 기존 false positive 한 건뿐이다.
  - 2026-07-31 후속 content refine 조치: 모양 찾기 장면 전체를 오답 판정 영역으로 연결하고 hotspot 밖 클릭도 기존 오답 횟수·도장·힌트에 반영했다. 세 번째 오답은 정답으로 완료시키지 않고 정답 위치·숫자 또는 입력값만 공개한 뒤 학습자가 정답 hotspot을 직접 선택하거나 기존 `O`를 눌러 확인해야 진행하도록 모양 찾기·세기·산술·무작위 문항을 통일했다. 무작위 풀이 표면에는 원문 밖 문구를 추가하지 않고 기존 풀이를 유지한 채 진행점을 표시하고 초점을 이동해 다음 조작 affordance를 보강했다. 자유 그리기는 도형 3개 이상·도형 종류 2개 이상·색 2개 이상의 명시적 완료 검사로 바꾸고, 배치 상태를 완료 장면의 담장 위에 그대로 복원했다. planner 밖 가시 문구를 추가할 수 없어 `다음 문제`·`자유 그리기로 이동`·`그림 완성하기` 제안은 적용하지 않았고 기존 `aria-label`과 원문 `버튼`을 유지했다. 검증: planner 원문·문항·보기·정답·피드백 고유 102개 누락 0, JS 구문·중복 DOM id·asset 참조 정상. Playwright에서 배경 오답 3회→정답 직접 선택, 세기·산술·무작위 자동 공개→기존 확인 조작, 자유 그리기 최소 조건과 완료 장면 3개 결과 복원을 확인했고 page error는 없었다.
- 규칙화 메모: **5회 도달 → rule 승격 제안(2026-07-31, 사용자 승인 대기).** 초안: “다단계 문항은 operands를 문제 묶음 상태로 공유하고, 모든 scene 재진입 시 DOM·배경·캐릭터·입력·타이머를 초기화한다. **문항에서 다음 단계로 넘어가는 경로는 항상 하나 이상 사람이 볼 수 있는 표면(가시·활성·포커스 가능)이어야 하며, 자동 전환을 제거할 때는 그 자리를 대신할 표면이 실제로 보이고 눌리는지 사람 조작 기준으로 확인한다.** Playwright hook 통과는 진행 가능의 근거가 아니다.” 반영 위치: `content-harness-pipeline/AGENTS.md`. 5회 중 4회는 파이프라인 critique, 5번째는 실사용 데드엔드 관측이라 **critique 루프가 못 잡는 층위**임이 드러났다.


### [cross-lesson-shell-inconsistency] 같은 학기 차시인데 공통 화면(상단 헤더·타이틀 화면) 양식이 차시마다 달라짐

- 대상: production/1-2/08/index.html (기준: production/1-2/01/index.html)
- 분류 태그: cross-lesson-shell-inconsistency
- 상태: 열림
- 발생 횟수: 3
- 최초 발생일: 2026-07-31
- 최근 발생일: 2026-07-31
- 사례:
  - 2026-07-31: 1-2/08의 헤더가 1-2/01과 전혀 다른 양식(이미지 프레임 HUD, 164x68 목록/소리 버튼, 3단계 chip, 전폭 progress track, 146px 높이)이라 1-2/01의 topbar 양식과 똑같이 맞추라고 지적했다. 파이프라인이 차시마다 공통 shell을 새로 설계해 차시 간 UI 연속성이 깨진다.
  - 2026-07-31: 타이틀 화면도 같은 일이 반복됐다. "01을 참고해서" 타이틀 로고를 가운데 이미지로 두라는 요청에 대해, 01의 `#introStartWrap` 구조를 가져오지 않고 08 기존 좌표계로 비슷하게만 만들었다. 사용자가 "css도 그렇고 크기도 그렇고 색감도 그렇고 글꼴도" 다르다고 지적. 실측 차이 — (a) 01은 `#app.title-mode .topbar{opacity:0}`으로 타이틀 화면에서 헤더를 숨기는데 08은 노출, (b) 01은 로고+시작버튼을 `#introStartWrap` 한 덩어리로 `top:50%` 중앙 배치하는데 08은 로고 `top:297px` / 버튼 `bottom:70px`로 분리, (c) 시작 버튼 폭이 01은 화면폭 28.6%(390/1366)·28px인데 08은 21.9%(420/1920)·34px, (d) 버튼 색이 01은 `#fff46d→#ffc72f→#ff8f18` 금색 그라데이션 + `#113d78` 테두리/글자인데 08은 흰/크림 스프라이트(`cta-intro-body.png`), (e) 서체가 01 `Noto Sans KR` vs 08 `Malgun Gothic`, (f) 01의 `titleLogoDrop` 로고 낙하 애니메이션 누락.
  - 2026-07-31: 세 번째 반복. (a) 08의 말풍선(`.speech`)이 씬마다 고정 좌표·고정 크기라 대사 길이가 달라도 박스가 그대로여서 글자 수에 따라 크기가 늘고 줄어야 한다는 지적, (b) 01에는 음소거 버튼과 다음(진행) 버튼이 공통 UI로 있는데 08에는 없으니 **01에서 가져와 쓰라**는 지시. 앞선 두 사례(헤더·타이틀 화면)와 같은 패턴이 조작 UI 층위에서 또 나왔다 — 차시별로 진행/소리 조작을 각자 만들어 두면 같은 코스인데 조작법이 차시마다 달라진다.
- 조치(1회차): 1-2/01 topbar의 실제 CSS/DOM 값을 그대로 이식했다. 구조는 `.topbar`(56px, 크림 유리 그라디언트, 하단 보더) > `.topbar-left`(`.btn-home` + `.header-voice-volume-button` + `.step-label`) / 중앙 절대배치 `.lesson-header-title`(금색 밑줄) / 우측 `.lesson-bar-reward`(track+fill+`%`)로 통일했다. 내용은 planner/input에서 가져왔다 — 제목은 `알록달록, 학교 담장 색칠하기`, step-label은 1-2/01의 stageLabels 사다리에 맞춰 `수리력 +`·`수리가 필요해요 1`·`수리가 필요해요 2`·`수리로 해결해요`·`수리 이야기`로 sceneMeta에 매핑, 진행률은 기존 `setProgress()` 호출을 그대로 lesson-bar에 연결했다. 좌상단 버튼은 1-2/01의 실제 런타임 형태인 햄버거 아이콘 + `목록` 라벨(`.course-menu-btn`)로 맞췄고, 글자 서체도 1-2/01과 같은 Noto Sans KR을 `--font-topbar`로 topbar에만 적용했다(로드 실패 시 기존 `--font-body`로 폴백). 1-2/01에 없는 3단계 chip과 `assets/global-hud-frame.png` 프레임은 제거했다(파일은 삭제하지 않고 남겨 둠). 검증: node --check로 inline JS 구문 정상. 1-2/01(title-mode topbar 숨김만 해제한 사본)과 1-2/08을 각각 로컬 HTTP로 띄워 headless Chrome 1920x1080으로 캡처하고 상단 60px를 나란히 비교해 버튼·구분선·중앙 제목·금색 밑줄·우측 진행 pill이 같은 위치·크기·서체로 렌더되는 것을 확인했다.
- 조치(2회차): 01의 `#introStartWrap` / `.intro-title-copy` / `.intro-start-cta` / `titleLogoDrop` / `ctapulse` / `shimmer` / `title-mode`를 같은 이름으로 이식하고 값은 1920 배율(×1.4056)로 환산했다. **여기서 한 번 더 틀렸다 — 01의 CSS를 소스 순서로 읽어 `#introStartWrap .intro-start-cta`(네이비+금색)를 이식했는데, 이는 뒤쪽 `#app .cta,#app #introStartWrap .intro-start-cta`에 덮인 죽은 규칙이었다.** `getComputedStyle` 실측으로 실제 값(앰버 pill `#fef08a→#ca8a04`, `border-radius:999px`, 글자 `Jua` 27px `#713f12`)을 다시 읽어 교정했다. 서체도 같은 함정 — 01은 Noto Sans KR을 선언한 뒤 아래에서 `html,body,button{font-family:"Jua",...}`로 덮는다. 사용자 승인으로 08도 `--font-body`를 Jua 스택으로 전역 교체했다. 타이틀 이미지 아트 자체(색감·글자 형태)가 01 로고와 다른 건 CSS로 불가 — 사용자가 현재 이미지 유지 결정.
- 규칙화 메모: 3회. 반복되면 `content-harness-pipeline/AGENTS.md`에 "차시 공통 화면(상단 헤더/타이틀 화면/진행 표시/목록·소리 조작/대사 진행 버튼)은 차시마다 새로 설계하지 않고, 기준 차시의 클래스명·수치를 `getComputedStyle` 실측으로 읽어 스테이지 배율만 환산해 그대로 이식한다"는 rule 승격을 제안한다. 2회차 관찰로 범위를 '상단 헤더'에서 '공통 화면 전반'으로, 3회차 관찰로 '조작 UI(소리·다음)'까지 넓혔다 — 근본 패턴은 "기준 차시를 참고하라고 했을 때 실제 값을 읽지 않고 비슷하게 새로 만들거나, 아예 안 만드는 것"이다. 연관 [[port-styles-via-computed-style]].

### [overlay-occludes-bg-subject] 오버레이(타이틀 이미지)가 배경 아트의 핵심 피사체를 가림

- 대상: production/1-2/08/index.html `#introTitleSurface` (`assets/colorful-school-wall-title.png`)
- 분류 태그: overlay-occludes-bg-subject
- 상태: 열림
- 발생 횟수: 1
- 최초 발생일: 2026-07-31
- 최근 발생일: 2026-07-31
- 사례:
  - 2026-07-31: 도입 장면 타이틀 이미지가 배경의 학교 담장(무너진 구간 포함) 위에 겹쳐 얹혀 있어, 이 차시의 핵심 피사체인 담장을 가린다고 지적했다. 위로 올려 담장을 가리지 않게 요청.
- 조치: 배경 `school-wall-damaged.png`(1672x941, cover 배율 1.148)에서 담장 기둥 윗면이 stage 좌표 y≈550인 것을 캡처 픽셀 스캔으로 확인했다. 타이틀 에셋은 알파 bbox가 y 100~758/824라 폭 1068px로 그리면 높이 461px 중 실제 그림이 박스 상단 +56~+424에만 있다. 도입 화면은 작업 도중 01의 `#introStartWrap`(타이틀+시작 버튼 세로 컬럼, `top:50%`+`translate:0 -50%`) 구조로 교체되었고, 그 정중앙 배치에서는 그림이 y 305~673을 차지해 담장을 덮었다. 01 규칙은 그대로 두고 씬 스코프 오버라이드 `#section_intro #introStartWrap{translate:0 calc(-50% - 140px)}`만 더해 그림을 y 165~533으로 올렸다(명시도 id 2개 > id 1개라 `!important` 불필요). 시작 버튼도 컬럼째 올라가 바리케이드·콘과 겹치던 위치에서 담장의 깨끗한 면 위로 옮겨졌다. 검증: headless Chrome 1920x1080에서 도입 장면을 캡처해 담장 전체·무너진 구간·벽돌 더미·콘·바리케이드가 모두 드러나고 타이틀이 상단 헤더와 겹치지 않는 것을 확인했다.
- 규칙화 메모: 아직 1회. 반복되면 `content-harness-pipeline/AGENTS.md`에 "장면 오버레이(타이틀/배너/패널)는 배경 아트의 학습 주제 피사체 위에 얹지 않고 하늘·여백 등 빈 영역에 배치하며, 배치 전 배경의 피사체 경계를 확인한다"는 rule 승격을 제안한다.

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

- 대상: production/1-2/08/index.html (`findObjects` — `classroom-shape-search.png` 위 6종 사물)
- 분류 태그: object-placement-implausible
- 상태: 열림
- 발생 횟수: 1
- 최초 발생일: 2026-07-31
- 최근 발생일: 2026-07-31
- 사례:
  - 2026-07-31: 모양 찾기에서 "너무 뜬금없는 물건들이 뜬금없는 위치에 나온다"고 지적. 사용자가 제시한 기준은 **사물의 실제 소속 위치** — 공은 바닥에 붙어 있으면 좋다(현재 OK), 삼각자는 칠판 위, 시계는 교실 가운데 상단, 네모는 사물함·창문 말고 책상 위에 있을 법한 다른 에셋을 다시 생각할 것. 더불어 칠판 오른쪽이 비어 있으니 학생을 상시 배치해 교실처럼 보이게 하라고 요청. 현재 좌표는 배경 아트와 무관하게 stage 좌표로만 흩어 놓아(`rect:[830,240,215,215]` 등) 사물이 공중에 떠 있거나 맥락 없는 면에 얹힌다.
- 조치: (미조치 — `production/1-2/08/todo.md` 18번으로 등록)
- 규칙화 메모: 아직 1회. 반복되면 "탐색·찾기 장면의 사물은 도형 난이도만 보고 배치하지 말고 그 사물이 실제로 놓이는 표면(바닥/책상/벽/칠판)에 앵커를 두고, 배경 아트의 빈 면은 장면 맥락(인물·소품)으로 채운다"를 `prompts/builder_system.md`에 제안 후보. **[bg-anchor-alignment]와 구분할 것** — 그쪽은 "배경에 그려진 자리에 못 맞춤"(기하 정합), 이쪽은 "자리 자체가 개연성이 없음"(장면 의미). 같은 태그로 묶지 말 것.

### [narration-visual-mismatch] 대사가 말하는 것과 화면에 보이는 것이 다름(색·개수)

- 대상: production/1-2/08/index.html (`section_arithmetic_tutorial` — `#arithSpeech` 대사 vs `.paint-shape` 색, 페인트 통 에셋)
- 분류 태그: narration-visual-mismatch
- 상태: 열림
- 발생 횟수: 2
- 최초 발생일: 2026-07-31
- 최근 발생일: 2026-07-31
- 사례:
  - 2026-07-31: 세 수의 덧셈·뺄셈 튜토리얼에서 대사는 `초록색부터 알려드릴게요`(index.html:452·764)라고 하는데 화면의 도형은 여러 색으로 나온다.
  - 2026-07-31: 같은 튜토리얼에서 "페인트 통이 하나 더 필요하다"는 대사가 나오는데 화면에는 페인트 통이 한 통만 그려져 있다. 대사가 요구하는 수량 변화가 화면에 반영되지 않는다.
- 조치: (미조치 — `production/1-2/08/todo.md` 19·21번으로 등록)
- 규칙화 메모: 아직 2회지만 둘 다 같은 씬에서 나왔다. 반복되면 "대사 원문이 색·개수·방향 같은 관찰 가능한 속성을 말하면 그 속성이 화면 상태와 일치하는지 씬 단위로 대조한다(원문은 못 바꾸므로 화면을 원문에 맞춘다)"를 `prompts/content_refine_system.md`에 제안 후보. 연관 [spec-fx-color-mismatch](스펙 지정 색을 임의로 바꿈 — 그쪽은 구현이 스펙을 어긴 것, 이쪽은 구현이 **원문 대사**와 어긋난 것), [refine-alters-spec-text].

### [arith-operand-not-highlighted] 더하는 대상은 표시가 없고 빼는 대상만 표시돼 연산 방향이 안 읽힘

- 대상: production/1-2/08/index.html (`section_arithmetic_tutorial` — `#arithShapes` 추가/삭제 연출)
- 분류 태그: arith-operand-not-highlighted
- 상태: 열림
- 발생 횟수: 1
- 최초 발생일: 2026-07-31
- 최근 발생일: 2026-07-31
- 사례:
  - 2026-07-31: "7개에서 3개를 색칠"에서 **빼기는 빼는 표시가 잘 되어 있는데 더하기는 어떤 게 더해지는 것인지 표시가 없다**고 지적. 사용자가 제안한 해법은 네모로 묶어 glow를 주거나 그에 준하는 다른 표시. 짝을 이루는 두 연산에 시각 처리가 비대칭이라 덧셈 쪽만 관찰 근거가 사라진다.
- 조치: (미조치 — `production/1-2/08/todo.md` 20번으로 등록)
- 규칙화 메모: 아직 1회. 반복되면 "짝을 이루는 조작(추가/삭제, 정답/오답, 이전/다음)은 시각 처리를 대칭으로 만든다 — 한쪽에만 강조·모션을 주면 다른 쪽은 관찰 근거가 없는 상태가 된다"를 `prompts/builder_system.md`에 제안 후보. 연관 [motion-supporting-narration](나레이션이 말하는 사건에 시각 액션이 없음 — 이쪽은 **한쪽에만 있음**).

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
