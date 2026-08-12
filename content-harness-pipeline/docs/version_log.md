# version_log.md

content-harness-pipeline의 버전별 변경 이력이다. 버전은 커밋 메시지의 `versionX.Y` 표기를 기준으로 한다.
(git tag는 사용하지 않는다.)

---

## version 0.34 — 컴포넌트가 요구하는 art를 planner가 계획한다 · 컴포넌트 선택을 input으로 (2026-08-12)

0.33에서 컴포넌트가 이미지를 소유하지 않게 바꾸자, 도서관 차시에 **도장이 사라졌다.**
추적하니 이 차시는 도장을 한 번도 생성한 적이 없었다 — 화면에 있던 건 08의 도장을 컴포넌트가 복사한 것이었다.

### 진단

- 스토리보드에 "도장/스탬프" 언급 **0건**. 정답 피드백은 "딩동댕 + 글로우 + 캐릭터 점프"다.
  planner가 도장을 계획하지 않은 것은 **원문에 충실한 판단**이었다.
- 진짜 결함은 builder가 art를 요구하는 컴포넌트(`feedback-layer`)를 골랐는데 그 art가 `asset_plan`에 없다는
  불일치였고, **컴포넌트의 기본 이미지가 그 불일치를 가리고 있었다.**
- 구조적으로는 **컴포넌트 선택이 asset 생성보다 뒤에 있는 것**이 원인이다.
  `planner(asset_plan 확정) → asset_generator(생성) → builder(컴포넌트 선택)` 순서라
  컴포넌트가 요구하는 art는 생성될 방법이 없었다. planner는 컴포넌트 목록을 보지도 못했다.
- 교훈: **기본값이 있으면 그 값이 필요하다는 사실이 안 보인다.**

### 변경

**1. 컴포넌트가 자기 art 요구를 선언한다**

- `component.md`에 `Requires art` 필드. `feedback-layer` 2개(필수), `ticket-button` 1개(선택).
- **무엇이 필요한지와 구조 제약만 쓴다.** 색·모티프·소재·팔레트는 쓰지 않는다 —
  그건 planner가 `art_direction`과 story board 분위기에서 가져와 `prompt_brief`·`style_constraints`에 쓴다.
  이 경계를 안 지키면 08의 분위기가 모든 콘텐츠로 샌다. craft-examples의 `Take`/`Do not take`와 같은 규칙이다.

**2. 컴포넌트 선택을 input으로 (`input.metadata.components`)**

- 선택이 input에서 끝나므로 **planner는 고르지 않는다.** 그 결과가 요구하는 art를 계획하기만 한다.
- planner에는 선택된 것의 `requires_art`만 넘긴다(`SELECTED_COMPONENTS_JSON`, ~10줄).
  manifest 전체를 실으면 planner가 선택까지 하게 되고 선택 주체가 둘이 된다.
- **`planner_output.schema.json`을 건드리지 않았다.** builder는 input을 이미 받으므로 목록을 거기서 읽는다.
  0.3x에서 `characters`를 required로 만들었을 때처럼 기존 run resume이 깨지는 일이 없다.
- 없는 컴포넌트 이름은 run 전에 REJECT하고 사용 가능 목록을 보여준다.
- 폐기한 방향: planner가 컴포넌트를 고르게 하기(프롬프트에 manifest 전체 + 스키마 변경 + resume 파손).

**3. 정형 예외를 planner 프롬프트에 명시**

> 선택된 컴포넌트가 요구하는 art는 `asset_plan`에 넣습니다. **story board가 요구하지 않아도 넣습니다** —
> 콘텐츠가 아니라 플랫폼의 정형이기 때문입니다.

원문 보존 규칙("story board에 없는 것을 임의로 추가하지 않는다")의 예외를 **이유와 함께** 열었다.
예외인 이유는 그 화면 요소를 story board가 아니라 **선택된 컴포넌트가 요구**하기 때문이다.

**4. `--asset-generator-missing-only`가 한 번도 동작한 적 없었다**

두 결함이 겹쳐 서로를 숨기고 있었다.

- `build_existing_asset_output`이 계획 경로를 **정확히** 찾는데, planner는 늘 `.png`로 계획하고
  산출물은 `.webp`로 압축돼 있어 하나도 못 찾았다 → `existing`이 항상 0.
- 그래서 재사용 항목이 schema required 7개 중 `character_id`를 빠뜨린 것이 **실행된 적이 없어 안 드러났다.**
  첫 번째를 고치자마자 `asset_generator_output_validate REJECT`로 터졌다.
- `resolve_existing_asset()` 추가(확장자를 따지지 않고 stem으로 찾아 **실제 확장자를 기록**) + `character_id` 채움.

**5. 확인 페이지 복구**

컴포넌트에서 이미지를 들어내면서 `feedback-layer/preview.html`과 `example/index.html`이 깨졌다(4건).
preview 전용 이미지는 `example/assets/`에 `preview-*`로 둔다 — 거기는 번들에서 제외되므로 컴포넌트 소유가 아니다.

### 검증

- **정형 예외 작동** — planner 재실행 시 `asset_plan` 19 → 27. 도장 2장이 계획됐고
  `purpose`에 "feedback-layer가 ... 표시하도록 필수 정답 도장을 제공한다"고 **근거를 스스로 적었다.**
- **분위기가 들어갔다** — 08의 파란 물결 씰이 아니라 **도서 대출일 도장**(황동 인장 + 숲청록 손잡이,
  정답=펼친 책+체크 `정답`, 오답=되돌림 화살표 `다시 생각해보세요`). `Requires art`에 색·모티프가 없는데
  planner가 `art_direction`에서 가져왔다. craft-examples의 구조 규칙(문구를 도장 면 안쪽 밴드에,
  밴드 곡률을 따라, 정답/오답 별개 asset, 상태색은 글자·심볼만)은 전부 지켰다.
- **CTA도 해결** — `--cta-body`가 선택인데도 4장을 계획했고 **문구를 구웠다**
  (`[시작하기]` 등 대괄호까지 원문 그대로, 각각 단일 이미지). 0.33에서 고친 굽기 판정의 첫 실물이다.
  반복되는 `[3시][4시][5시]` 보기는 계획되지 않아 굽기 경계도 맞았다.
- **missing-only** — 재사용 0 → 4 → (재실행) 27, 재생성 0장으로 0.03초 PASS.

### 정리

- `output/assets/` 고아 18개 제거(이름이 바뀐 옛 asset + 컴포넌트 복사 잔재).
- 산출물·스크린샷 png → webp: **25.4MB → 2.3MB**, **43.2MB → 4.6MB** (각 91%·90% 감소).
  스크린샷 경로를 들고 있던 json 4개의 참조도 함께 갱신했다.
  단 `design_review/`를 가리키는 22건은 디렉토리 자체가 없어 원래부터 dangling이므로 기록을 원래대로 뒀다.
- run 디렉토리 약 100MB → 31MB.

### 미해결

- `content_refine` 경로(`runner.py:1823`)는 단독 플래그가 없어 여전히 미검증.
- `design_review`가 craft example 기준을 보지 않는다.
- 참조가 실제로 쓰였는지 산출물에 기록되지 않는다(`style_references_used` 없음).
- `--overwrite`가 `output/assets/`를 비우지 않아 run 간 고아가 누적된다. 이번엔 손으로 지웠다.
- `iter_001/design_review/`·`builder_visual_qa/` 스크린샷이 디스크에 없는데 json은 참조한다(각 11건).

---

## version 0.33 — 재사용 source 3축 스캔 연결 · 컴포넌트 CSS를 코드가 소유 · teacher 화풍 축 (2026-08-11)

컴포넌트를 `common`으로 뽑았는데 다른 차시 산출물의 헤더가 08과 달라진 것에서 출발했다.
실측하니 `.c-topbar`가 `height:70px` / `backdrop-filter` 없음 / `3px` 테두리로 **재작성**돼 있었다.

### 진단

- 클래스명·`data-slot`·DOM은 전부 보존됐고 **CSS만 새로 쓰였다.** 컴포넌트별로 대조하니
  `ticket-button`(1.1KB)·`keypad`(1.8KB)·`speech-bubble`(2.2KB)는 원본 그대로였고
  **`topbar`(10.6KB) 하나만** 재작성됐다. 전형적인 satisficing이다.
- 구조적 원인: `common_components.py`는 `COMMON_BASE_CSS`만 전문을 싣고 컴포넌트는 **경로만** 넘긴다.
  즉 `style.css`를 최종 HTML에 넣는 일을 **모델이 파일을 열어 자발적으로 옮겨 적기를 기대**하고,
  그렇게 했는지 **검증하지 않았다.** `common_html_contract.md:71`에 "기억으로 재작성하지 않습니다"라는
  조항이 이미 있었는데도 샜다.
- 교훈: **글자 단위 복사는 모델의 일이 아니다.** 규칙으로 막을 게 아니라 옮겨 적을 일 자체를 없애야 한다.

### 변경

**1. 컴포넌트 CSS/JS를 코드가 소유 (`stages/scripts/component_bundle.py` 신규)**

- `emit_common(run_dir, teacher_root)`가 `output/common.css`(24KB) · `output/common.js`(15KB)를 원본에서 쓴다.
  모델은 `index.html`에 `<link>` · `<script src>` **두 줄만** 유지한다.
- `runner.finalize_html_artifact()`가 HTML을 쓰는 세 지점(builder `:1113`, content_refine `:1823`,
  design_refine `:1884`) 뒤에서 부른다. 이미 `validate_builder_files`가 그 세 자리에 있어 새 seam을 만들지 않았다.
- **성격이 반대인 둘을 구분한다** — `common.*`는 코드 소유라 **무조건 덮어쓰고**(검증 없음),
  `index.html`은 모델 소유라 **되돌릴 수 없으므로 검증**해 REJECT한다(`check_html_links`, 순서까지).
  기준은 "되돌릴 수 있으면 되돌리고, 없으면 검증한다".
- drift는 **로그이지 게이트가 아니다.** 게이트로 만들면 정당한 오버라이드 시도까지 run을 죽인다.
- 보장 대상을 바꿨다 — "결과가 동일하다"가 아니라 **"컴포넌트 원본이 항상 온전히 그 자리에 있다"**.
  콘텐츠는 `<link>` 뒤 `<style>`에서 소스 순서로 오버라이드할 수 있고 그건 막지 않는다.
- 폐기한 방향: 마커+구간 교체(HTML 파싱 필요, 마크업 재탐지 필요), 컴포넌트 CSS 전문을 프롬프트에 싣기
  (34KB를 넣고도 복사를 강제하지 못해 문제 성격이 안 바뀜).

**2. 공용 컴포넌트가 이미지를 소유하지 않는다**

- `ticket-button`·`feedback-layer`가 08의 CTA·도장 art 3장을 갖고 있었다. `components/CLAUDE.md`가
  "여기 두지 않는 것: 특정 선생님 캐릭터가 들어간 말풍선·**CTA**·**피드백**"이라고 **명시한 바로 그 세 범주**였고,
  common이 정당하게 소유한 이미지는 0개였다.
- `craft-examples`가 "콘텐츠 세계관이 다르면 도장도 그 세계의 물건이어야 한다"고 금지하는 것을
  다른 축이 실행하고 있었다. 실제로 도서관 차시 화면에 08의 크림·갈색 CTA와 파란 도장이 섞였다.
- 3장을 제거하고 `ticket-button`은 `--cta-body`(없으면 토큰 CSS), `feedback-layer`는 `data-*-src`로
  생성 asset 경로를 밖에서 받게 했다. `1-2/01`의 시작 버튼이 이미 이미지 없이 토큰 CSS로 만들어져 있다.
- `common_html_contract.md`의 "컴포넌트 `assets/`를 `output/assets/`로 복사한다" 조항을 삭제.
  **`source/`의 어떤 파일도 output으로 복사하지 않는다.**

**3. teacher 화풍 축 신설 (`source/baek-seungyong/`, `stages/scripts/teacher_source.py`)**

- `production/1-2/08` 51개에서 대표 21장을 골라 catalog화(16항목). `style.md`에 **이미지를 봐야 갈리는
  판별 지점**을 적었다 — 외곽선 3층 위계(배경 없음 / 캐릭터 중간 / 소품 굵은 남색), 등신 분리(성인 7~7.5 vs 어린이 4~4.5).
- `load_catalog()`가 `source/[teacher]/*.md`를 스캔한다. `## 항목`에 `- Path:`가 있으면 catalog,
  없으면 산문 — 사람이 읽는 설명과 기계가 읽는 항목이 한 파일에 공존한다.
- `style_reference_set.categories`를 **생략하면 스캔이 채운다.** 항목별 `use`/`avoid`는 catalog가 소유하고
  input에 다시 적지 않는다. **input이 103줄 → 20줄**로 줄었는데 화풍 추종은 떨어지지 않았다.
- 명시하면 그대로 쓴다(catalog 밖 이미지 1회용 + 기존 input 호환).

**4. 이름이 같으면 teacher가 common을 덮는다 (`stages/scripts/source_resolve.py`)**

- 세부가 일반을 이긴다. `source/[teacher]/components/keypad/`가 있으면 common 것은 무시된다.
  **병합이 아니라 통째 교체** — 섞으면 teacher가 일부러 뺀 규칙이 common에서 되살아난다.
- 컴포넌트 축·craft example 축·`emit_common`이 같은 `shadowed_dirs()`를 쓴다.
  teacher는 `input.metadata.style_reference_set.root`가 정하고, 없으면 common만.

**5. craft example을 `source/common/craft-examples/`로 이관 + 스캔**

- `prompts/asset_examples/`(하드코딩 md + 3장)를 옮기고 `craft_examples.py`가 스캔한다.
  `CRAFT_EXAMPLES_RULES`(전문) + `CRAFT_EXAMPLES_JSON`(경로)의 2블록 구조는 컴포넌트 축과 같다.
- **이 축만 참조와 결과의 관계가 반대다** — "베끼면 실패". `art_direction`이 예시를 이긴다는 조항이
  빠지면 모델이 `identity_context` 습관대로 예시 팔레트를 복제해 run의 화풍을 덮어쓴다.

**6. input 계약 (`schemas/input.schema.json`, `validate.py`)**

- `metadata.style_reference_set` 모양을 스키마로 강제(`required: id, root`, `additionalProperties: false`).
- **on/off 플래그를 두지 않았다.** 키의 유무가 곧 on/off다. `teacher_reference: true`를 따로 두면
  "true인데 root가 없는 상태"가 생기고 어느 쪽이 맞는지 판정할 근거가 없다. 강도는 `must_follow`가 표현한다.
- `validate.py`가 스키마 통과 후 **경로까지 해석**한다. stage 안에서 처음 해석하면
  run 디렉토리와 input 사본을 만든 뒤에야 실패하므로 입력 검증 단계로 당겼다.
- `find_component_asset_conflicts()` — 같은 파일이 "복사해서 쓰는 컴포넌트 asset"과 "참조만 하는 화풍 참조"
  양쪽에 있으면 REJECT. **파일명이 아니라 내용 해시로 비교**한다(실제 충돌이 `activity-cta-body` vs
  `cta-activity-body`로 이름이 달랐다).

**7. CTA 굽기 판정 (`planner_system.md`)**

- 굽기 조건 ③ "선택·입력·판정·측정의 대상이 아니다"가 **버튼을 클릭 대상이라는 이유로 배제**하고 있었다.
  "**읽고 고르거나 값을 매기는** 대상이 아니다 — 눌러서 다음으로 가는 것은 해당하지 않는다"로 명확화.
- "굽는 문구와 얹는 문구의 경계" 신설 — 기준은 **그 문구가 그 화면을 특정하는가**.
  씬을 여닫는 CTA는 굽고, 한 씬에서 반복되는 진행 버튼은 컴포넌트 + HTML 라벨.
- 굽는 asset은 상태 스프라이트로 만들지 않는다(프레임마다 글자가 어긋난다).

### 검증

- **화풍 추종 (실제 run `2026-08-11_65126dad`, 임상현 2학년 시간 차시 × 백승용 화풍)**
  - planner PASS. `art_direction.line_style`이 외곽선 3층 위계를 잡았고, `characters`가
    7~7.5등신 / 4~4.5등신 대두 + "사서 선생님 키의 약 60%"로 분리했다.
  - `forbidden_styles`에 "학교 담장·교실 책상 배열·도로 표지·페인트 소재의 복제", "참조 캐릭터의 얼굴·헤어·의상 복제".
    **소재는 안 가져오고 화풍만 가져왔다.** 배경은 도서관 로비, 인물 의상은 전부 새로.
  - asset 19/19 생성. `clock-body`에 **바늘이 없다**(가변부 규칙 작동 — 시간 차시라 깨졌으면 12문항이 전부 재생성 대상).
    `mission-title`은 craft example의 완성도만 가져오고 색·모티프는 새로(노랑·별 → 청록·버건디·책갈피·시계).
  - 얇은 input(20줄, 스캔)과 명시형 input(103줄)을 각각 planner에 태워 대조 — **결과 동등**.
- **컴포넌트 계약 (builder 재실행)**
  - `common.css` 24.6KB / `common.js` 15.5KB 생성, `<link>`·`<script src>` 두 줄 삽입 확인.
  - `.c-topbar`가 08과 **값 일치** — `height:56px` · `backdrop-filter:blur(14px) saturate(1.3)` ·
    `1px solid rgba(113,63,18,.16)` · 그라데이션. 재작성이 사라졌다.
  - `index.html`의 `<style>`이 35KB+ → 11KB, `.c-topbar` 재선언 0, `:root` 재선언 0.
- **design_refine 경로 (제일 위험한 지점)** — HTML을 통째로 재작성하고도 두 줄이 남았고,
  `common.*`가 종료 시각에 재생성됐으며, `common-restored` 로그 없음(= 손대지 않음).
  `<style>`은 11KB → 17KB로 늘었는데 findings 12건을 반영한 콘텐츠 CSS다.
- **emit_common 단위** — 멱등(2회차 drift 0), 자가복구(망가뜨린 뒤 22591자 복원 + 로그),
  link 검증 4/4(누락·순서 뒤집힘·script 누락 전부 REJECT).
- **teacher shadow** — 임시 teacher `ticket-button`을 만들어 확인. 컴포넌트 7개(중복 없음),
  teacher 버전 채택, `common.css`에 common 규칙 제외, 정리 후 common 복귀.
- **input 계약** — 정상 2종 PASS, `root` 누락·오타 필드·없는 디렉토리·없는 이미지 4종 전부 REJECT.

### 미해결

- **planner가 CTA·보기 카드·표면을 `asset_plan`에 넣지 않는다**(19개 중 0개). 컴포넌트가 art를 안 갖게 됐으므로
  이제 그 자리는 토큰 CSS로만 남는다. **7번의 굽기 규칙이 효과를 내려면 이게 먼저다.**
  (`problem.md` `[cta-label-overlaid-not-baked]`)
- `content_refine` 경로(`:1823`)는 단독 플래그가 없어 미검증. 품질 루프로만 도달한다.
- `design_review`가 craft example 기준을 보지 않는다. 구운 글자의 완성도가 낮아도 게이트에 안 걸린다.
- 참조가 실제로 쓰였는지 산출물에 기록되지 않는다. codex는 `view_image`와
  `image_gen__imagegen(referenced_image_paths)`를 갖고 있고 프롬프트가 둘 다 지시하지만,
  `asset_generator_output.schema.json`에 기록 필드가 없어 사후 검증이 안 된다.
- 최종 산출물이 단일 HTML이 아니다(`index.html` + `common.css` + `common.js`). 필요하면
  run 끝에 `<link>`를 인라인으로 치환하는 단계를 하나 두기로 하고 미뤘다.

---

## version 0.32 — design_review 픽셀 우선 검수 · 정렬 오프셋 계량 (2026-07-22)

ch8c0718 튜토리얼 화면에서 시계 에셋이 트레이 홈을 일부만 덮고 `[?]`·티켓 글자가 표면 중심에서 어긋났는데
design_review가 그 씬을 "정확히 결합/중앙 정렬됨"으로 **칭찬하며 통과**시킨 것에서 출발했다.

### 진단 (정정 포함)

- 처음엔 "codex가 스크린샷 경로만 받아 픽셀을 못 본다(blind)"로 단정했으나 **직접 프로브 테스트로 반증**됐다.
  codex는 `-i` 첨부 없이 경로만으로도 파일을 열어 픽셀을 정확히 읽는다(말풍선 원문·시계 시각·소품·색 전부 정답).
- 실제 원인은 capability가 아니라 **11씬 136KB 일괄 리뷰의 per-scene satisficing** — 더 눈에 띄는 결함(도장 CSS,
  잘린 트레이)에 주의를 몰고 tutorial의 ~12px 미세 오프셋은 "정렬됨"으로 러버스탬프. 프롬프트의 면죄부 조항
  (*"이미지 못 보면 HTML/CSS로 판단"*)이 CSS `place-items:center`에 기대게 해 이를 부추겼다.
- 교훈: **능력을 코드 경로·출력 스타일로 단정하지 말고 직접 실측한다.** (problem.md `[design-review-no-image-input]`)

### 변경

- **픽셀 우선 검수 절차** (`design_review_system.md`) — 16행 면죄부 조항 제거 → "반드시 각 screenshot을 직접 열어
  픽셀로 판정, CSS 선언만으로 정렬·덮음 결론 금지". "리뷰 순서"에 STEP 1(씬별 픽셀 전수 검사, 네 축) → STEP 2(소스 보조,
  픽셀 판정 확정 뒤에만 코드 확인) 절차 삽입. 축3 정렬 항목에 표면 중심 대비 오프셋 px 측정 지시 추가.
- **정렬 오프셋 계량 필드** (`design_review_model_output.schema.json` + `design_review_output.schema.json`) —
  `designFinding`에 `alignment_offset{measured, dx_px, dy_px, surface_w, surface_h}` 추가(두 스키마 거울로 일치).
  모델은 표면별 오프셋을 이 필드에 숫자로 채우고, severity는 그 수치에서 파생하는 방향으로 설계했다.
- **프롬프트 중복 정리** — 픽셀-우선 원칙(16행/STEP1/STEP2)·`alignment_offset` 지시(STEP1/축3/출력절)·텍스트 경계이탈
  판정(축3/Asset-internal text/REJECT)의 삼중 반복을 각 1곳+포인터로 통합(지시 내용은 보존).

### 검증 (격리 프롬프트 테스트, scratchpad `test_vision*.py`)

- 원본 프롬프트(cell5)는 tutorial을 findings 0으로 칭찬 → STEP1 지시(cell6·cell8)는 오프셋을 px 좌표로 잡음.
- `alignment_offset` 반영본(cell9): 전 씬 34개 finding이 `measured=true`로 px 채움. tutorial `[?]` = (-13,-18)px on
  394×280 → 코드 파생 **6.4% → HIGH**(모델은 medium), 티켓 3개 3.6~3.9% → **MEDIUM**(모델은 low), CSS 도장은
  `measured=false`로 코드가 건너뜀. **cell7에서 모델이 -14px 재고도 "괜찮다"로 0건 내던 severity 흔들림이 코드 임계값으로 제거됨.**
- 폐기한 방향: 이미지 `-i` 첨부(효과 없음), HTML 경로화(효과 없음), 코드의 크림-centroid 슬롯 검출(검색창을 박스에
  앵커해 편향 — 오버레이로 확인).

### 미완 / 미검증

- **B의 px→severity 재계산이 `stages/design_review.py`에 아직 미배선.** 현재 모델 severity가 그대로 나간다
  (테스트에선 하네스가 대행). 켜기 전 임계값을 과잉플래그 완화(예: 3% mid / 6% high)로 조정하고 재검증할 것.
- **full run 미검증** — 격리 프롬프트 테스트만 했다. 파이프라인 최종 validation은 스키마 일치로 통과 확인(`verify_pipeline.py`).
- **비용**: `alignment_offset` 필수화로 리뷰 생성이 ~1.7~2배 느려짐(cell9 642초, design_review timeout 2400초 내라 무방).

---

## version 0.31 — 원문 보존 · channel 계약 · 텍스트 정책 (2026-07-15)

0.3의 full run 검증에서 드러난 문제들을 잡고, 누적된 피드백 3건을 규칙으로 승격했다.

### full run에서 드러난 것

- **content 품질 루프가 순손실이었다.** content_eval 총점이 iter를 거치며 **4.2 → 3.08 → 2.9**로 하락.
  iter 001은 이미 min_total(4.2)을 만족했고 `feedback_scaffolding`(3<4.0) 하나 때문에 REJECT였는데,
  그것을 고치려 돌린 refine이 나머지를 무너뜨렸다. `content_fidelity`가 **5 → 1**로 추락.
- 원인: **design_refine이 HTML을 재작성하며 원문 CTA 라벨을 축약**했다.
  `[좋아요! 본격적으로 수리하러 가기 →]` → `본격적으로 수리하러 가기 →` 식. planner에 없는 버튼도 추가했다.
  design_refine_system.md는 텍스트를 "장면 속 물건으로 흡수하라"고 **옮기라고만** 하고, 내용을 바꾸지 말라는 제약이 없었다.

### 변경

- **원문 텍스트 보존 계약** (`design_refine_system.md`, `design_review_system.md`) —
  planner의 `elements[].content`·`questions` 텍스트는 한 글자도 변경 금지(축약·재서술·대괄호 제거·어미 변경 포함).
  할 수 있는 것은 위치·표면·크기·줄바꿈·정렬뿐. planner에 없는 버튼·라벨 추가 금지.
  design_review는 문구 축약을 **제안조차 하지 않고**, design_refine은 그런 제안이 와도 따르지 않는다(이중 방어).
  problem.md `[refine-alters-spec-text]`.
- **channel 렌더링 계약** (`builder_system.md`) — planner가 `elements[].channel`로 이미 태깅한 역할에 렌더 계약을 붙였다.
  `dialogue`는 기존 speech_bubble asset 재사용 + 화자 머리 옆 배치 + 표면 텍스트 금지 + 여러 줄이면 순차 beat.
  `feedback`은 표정 전환 + 캐릭터 말풍선 + 중앙 도장의 3층, 오답 pose는 말풍선 종료 시 idle 복귀.
  problem.md `[dialogue-as-speech-bubble]`(8) + `[feedback-as-character-bubble]`(5) + `[sequential-scene-choreography]`(3) = 16회를 통합.
- **이미지 안의 텍스트 정책 전환** (planner/asset_generator/builder/design_review/design_refine + planner schema) —
  판단 축을 **"텍스트냐"에서 "변하느냐"로** 바꿨다. 반복 컴포넌트에서 시곗바늘을 빼는 이유가 "바늘이라서"가 아니라
  "변해서"인 것과 같은 원칙이다. 문구가 고정이고 타이포그래피 자체가 디자인인 asset(도장, 타이틀, 간판)은
  글자를 아트와 통합해 **이미지에 그린다**. 근거: 기존 `stamp_correct_time.png`(정답!)·인트로 타이틀이
  한글 깨짐 없이 아트와 통합된 품질로 나왔고, CSS 오버레이로는 재현 불가능하다.
  asset_generator_system.md의 *"텍스트가 이미지 안에 들어가면 실패로 봅니다"* 제거.
  **가드**: 구운 텍스트는 `alt`에 원문 그대로 넣는다 — 그러지 않으면 HTML에서 사라져 content_eval의 원문 검증과 접근성이 함께 깨진다.
  값이 변하거나 입력·판정에 쓰이는 텍스트는 계속 코드로 얹는다.
- **design_refine 타임아웃 분리** (`runner.py`) — `DEFAULT_DESIGN_REFINE_TIMEOUT_SECONDS = 2400`,
  `--design-refine-timeout-seconds`. 10만 자 HTML을 재작성하는 stage라 1200초에서 실제로 TimeoutError가 났다.
  `max(전역, 2400)` 규칙이라 전역을 더 올린 의도를 깎지 않는다. 다른 stage는 1200 유지.
- **problem.md 루프 개선** — `보류(SKIP)` 상태 도입(5회를 넘어도 승격을 재제안하지 않음, 해제 조건 필수 기재).
  알파 계열 3건 16회를 보류 처리(프롬프트로 해결 불가 — 누적 사례가 전부 수동 픽셀 보정으로만 해결됨).
  `solved-log.md` 흐름 첫 적용(규칙화 전문 이관 + 스텁).

### 미검증

이번 변경은 전부 **프롬프트 규칙**이라 스키마처럼 강제되지 않는다. 검증은 새 run이 필요하다.
- 원문 보존: `content_fidelity`가 iter를 거쳐도 5를 유지하는지.
- channel 계약: `dialogue` 요소가 speech_bubble asset 위에 렌더되는지.
- 텍스트 정책: 도장 asset의 `negative_prompt`에 텍스트 금지가 없고 `prompt_brief`·`alt_text`에 문구가 들어가는지.

### 미해결

- `asset_generator`도 1200초에서 타임아웃했다(run B, 배경 2장). 이번엔 design_refine만 올렸다.
- `feedback_scaffolding`이 3점에 고착(*"왜 맞고 틀렸는지 설명이 약하다"*). 이는 피드백 **텍스트 내용**의 문제라
  channel 계약(렌더 위치)으로는 해결되지 않는다. planner/builder 쪽 사안으로 남아 있다.

---

## version 0.3 — character identity ownership (2026-07-15)

캐릭터가 포즈마다 다른 인물로 생성되던 문제(problem.md `[character-asset-identity-alpha]`, 17회 누적)를
프롬프트 지시가 아니라 **파이프라인 구조**로 해결했다.

### 원인

정체성 재생성 경로에 세 개의 구조적 결함이 있었다.

- **D1 — 원본을 못 본 채 덮어씀.** `compact_planner_context()`가 allowlist라 asset의 `style_constraints`를
  design_review에 전달하지 않는데, `assetRegenerationRequest` 스키마는 그 필드를 required로 출력하라고 요구했고
  runner가 그 값으로 원본을 통째로 대입했다.
- **D2 — 형제 포즈가 batch에서 제거됨.** `build_batch_planner_output()`이 재생성 대상만 남기고 asset_plan을 좁혀,
  포즈를 하나만 재생성하면 기준이 될 형제 포즈가 payload에서 사라졌다.
- **D3 — 정체성 소유자 부재.** 정체성이 `art_direction.character_rules`(모든 캐릭터를 한 문자열에)와
  asset마다의 `style_constraints`에 흩어져 있었고, 실제로는 `"teacher_worried와 동일 캐릭터"` 같은
  **참조 사슬**이었다. D2가 그 참조 대상을 잘라내 맞출 기준이 사라졌다.

### 변경

- **`characters[]` 엔티티 신설** (`planner_output.schema.json`) — 정체성의 단일 소유자.
  `identity`(face/hair/outfit/palette/proportions/distinctive_features) + `reference_asset_id`(기준 포즈).
  `asset_plan`에 `character_id` 참조 추가.
- **`style_constraints` 축소** — 그 컷의 포즈·표정·소품·시선만. `art_direction.character_rules`도
  공통 연출 기법만 담도록 축소(비율·얼굴·헤어·의상·팔레트 서술 금지. 외곽선은 `line_style`, 음영은 `lighting` 담당).
- **patch merge 도입** (`runner.py: apply_asset_regeneration_patch`) — 재생성 요청의 wholesale 대입을 폐기.
  빈 문자열/빈 배열은 "원본 유지"로 읽는다. `character_id`는 patch 대상에서 제외해 캐릭터 소속 변조를 차단(D1).
- **`identity_context` 도입** (`runner.py: attach_identity_context`) — asset_plan을 좁히기 전에 캐릭터 identity·
  형제 포즈·기준 포즈 이미지 경로를 붙여 batch까지 전파. `asset_plan`에는 넣지 않아 형제가 재생성되지 않는다(D2).
- **design_review payload 확충** (`stages/design_review.py: compact_planner_context`) —
  `characters`, `character_id`, `style_constraints`, `composition_notes`, `negative_prompt`, `page`, `asset_groups` 추가.
  이제 planner의 모든 키가 전달된다. `page.audience`/`page.tone`이 디자인 판정 기준으로 프롬프트에 연결됐다.
- **`asset_generator_output`에 `character_id` 기록** — 어떤 정체성으로 생성됐는지 추적.
- **죽어 있던 필드 수정** — `interaction_summary`(planner에 없는 키, 항상 `""`)→`interactions`,
  `section.interaction`(항상 `None`)→`interaction_ids`, `notes`(스키마에 없음)→`alt_text`+`status`.
- **데드 코드 제거** — content_critique는 출력 계약상 `asset_review`를 낼 수 없는데
  `merge_asset_review_outputs`/`has_asset_review_changes`가 거기서 읽고 있었다(항상 빈손).
  asset 재생성은 design_review가 단독으로 구동한다. `run_asset_revision_stage`의 `asset_review_output=None`
  폴백도 제거(트리거되면 조용히 아무것도 안 하는 경로였다).
- **스키마/프롬프트 모순 해소** — `assetRegenerationRequest`의 `minLength:1`이 빈 문자열 patch 정책을 금지하고 있어 제거.
  `design_review_output`의 `newAssetRequest`에 `character_id`가 없어 `additionalProperties:false`로
  최종 출력이 REJECT 날 상태였던 것을 model 스키마와 거울로 맞춤.

### ⚠️ 호환성 깨짐

`characters`가 required가 되어 **기존 run은 재개할 수 없다.** 기존 run을 resume하면
`planner_output_validate`(`runner.py`의 `--start-at`이 planner가 아닌 경로, builder_only 포함)에서
디스크의 옛 `planner.json`을 새 스키마로 재검증하다 REJECT된다.
마이그레이션은 하지 않기로 결정했고, 기존 run 포기를 전제로 진행했다.
산출물 파일 자체는 그대로 남아 있어 `output/index.html` 직접 편집은 가능하다.

### 검증

- codex `--output-schema` 3종(planner / asset_generator / design_review_model) 수락, 산출물도 스키마 통과.
- 실제 스토리보드로 planner-only run 2회(`runs/2026-07-15_ch802d14`).
  캐릭터 2명·포즈 8개가 나왔고 **전부 `style_constraints`에 정체성 재서술 0건**.
  스토리보드 12문제(유형 A/B/C 각 4개)와 오답 보기 보존 확인.
- 부수 효과: `character_rules`가 "모두 3등신"으로 못박아 성인/어린이 구분을 뭉개던 모순이 사라지고,
  두 캐릭터의 비율이 실제로 달라졌다.
- **정정(2026-07-15)** — 최초 작성 시 "codex에 이미지 생성 도구가 없어 asset_generator가 PIL로 폴백하므로 전체 run이 불가하다"고
  적었으나 **이는 사실이 아니었다.** `~/.codex/config.toml`의 MCP 목록에 image-gen이 없는 것만 보고 problem.md의 2026-07-10 기록
  (`[asset-generation-method-mismatch]`)을 검증 없이 그대로 믿은 결과다. 실제 산출물을 확인하니 이미지 생성이 정상 동작한다
  (runs/2026-07-14_ch802d14: asset 21개 전부 `generated`, 800KB~2.2MB alpha PNG 일러스트).
- **full run 검증(2026-07-15)** — ch8_input.json으로 동일 입력 2회(ch8a0715 / ch8b0715) 실행.
  - 캐릭터 정체성은 **run 안에서 완벽하게 유지**됐다. 두 캐릭터 × 3포즈가 모두 같은 인물이고 `characters[].identity` 명세와 일치.
    ch802d08에서 `teacher_happy`와 `teacher_worried`가 서로 다른 인물이던 것과 대조된다.
  - **다만 이번 run은 이 수정의 타깃 시나리오가 아니었다.** design_review가 요청한 재생성 13건이 전부 소품·표면이고 캐릭터가 하나도
    없었으며, 각 캐릭터의 포즈가 한 batch에 묶여 생성됐다(teacher=batch001, child=batch002). 즉 "포즈 하나만 따로 재생성"이라는
    D1/D2의 문제 상황 자체가 발생하지 않았다. **좋은 결과지만 이 수정의 증거는 아니다.**
  - run 간 정체성 편차(A: 청록 앞치마 / B: 남색 조끼)는 정상이다. 이 수정의 대상은 run 사이가 아니라 한 run 안의 일관성이다.
  - 두 run 모두 `TimeoutError`로 완주 실패(A: iter003 design_refine, B: asset_generator). 별건으로 기록.

### 함께 정리한 것

- problem.md에 `규칙화됨 아카이브(스텁)` 도입 + `solved-log.md` 신설.
  `[character-asset-identity-alpha]` 17회를 정체성 9회(규칙화됨 → solved-log로 전문 이관)와
  알파/프린지 8회(`[character-asset-alpha-fringe]`로 분리, 열림)로 쪼갰다.
  알파 후처리는 후순위로 미뤘고, `[transparent-asset-alpha-not-validated]`(7회)와 병합 권장으로 남겨뒀다.

---

## version 0.2 — asset-oriented-pipeline (2026-07-09)

## version 0.11 — redesign asset 추가 (2026-07-08)

## version 0.1 — character reuse (2026-07-08)

<!-- 0.1~0.2는 커밋 메시지만 남아 있어 상세 내역을 소급 기록하지 않았다. -->
