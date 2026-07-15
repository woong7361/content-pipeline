# version_log.md

content-harness-pipeline의 버전별 변경 이력이다. 버전은 커밋 메시지의 `versionX.Y` 표기를 기준으로 한다.
(git tag는 사용하지 않는다.)

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
