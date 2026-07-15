# version_log.md

content-harness-pipeline의 버전별 변경 이력이다. 버전은 커밋 메시지의 `versionX.Y` 표기를 기준으로 한다.
(git tag는 사용하지 않는다.)

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
- **미검증** — 전체 run은 돌리지 못했다. 현재 codex 설정에 이미지 생성 MCP/도구가 없어(등록: db 3종, open-design)
  asset_generator가 PIL로 폴백한다. "재생성해도 같은 인물인가"라는 최종 확인은 이미지 생성 경로가 생긴 뒤에야 가능하다.
  확인된 범위는 정체성이 payload에 온전히 실려 생성기까지 도달한다는 것까지다.
  (problem.md `[asset-generation-method-mismatch]` 참조)

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
