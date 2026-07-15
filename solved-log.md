# solved-log.md

`problem.md`에서 `규칙화됨`이 된 항목의 **문제 + 해결 전문**을 옮겨 보존하는 지식 로그다.
운영 규칙은 `problem.md` 상단 "사용 규칙 > 규칙화됨 항목 보관과 재발 처리"와 최상단 `AGENTS.md`의 "피드백 → problem.md → rule 루프" 섹션을 따른다.

## 목적

- 규칙화되어 `problem.md`에서 스텁으로 축소된 항목의 상세(어떤 문제였고 어떻게 해결했는가)를 잃지 않는다.
- `problem.md`에는 스텁만 남겨 중복 감지·재발 카운트를 유지하고, 상세 지식은 여기서 참조한다.
- 재발 시 그 재발 사례를 해당 항목 아래에 덧붙여 "rule 있는데도 또 터진" 이력을 남긴다.

## 항목 형식

```markdown
### [분류태그] 한 줄 요약   <!-- problem.md 스텁의 solved-log#앵커가 이 제목을 가리킨다 -->

- 대상: content-harness-pipeline/... (구체 경로 또는 index.html)
- 분류 태그: <problem.md 스텁과 동일>
- 최종 발생 횟수: N
- 규칙화일: YYYY-MM-DD
- 반영한 rule 위치: (AGENTS.md 경로/섹션)
- 사례:
  - YYYY-MM-DD: <지적 내용 요약>
- 조치: <어떻게 해결했는지 전문>
- rule 문구: <실제 승격된 rule 요약>
- 재발 이력:
  - <없으면 "없음". 재발 시 YYYY-MM-DD와 대응 추가>
```

## 로그

<!-- 규칙화된 항목의 전문을 이 아래에 추가한다. -->

### [dialogue-as-speech-bubble] 대사·피드백을 표면 텍스트로 넣고 말풍선을 매번 새로 만듦 (channel 렌더링 계약으로 통합)

- 대상: content-harness-pipeline/prompts/builder_system.md (산출: runs/2026-07-08_ch802d08/output/index.html 전반)
- 분류 태그: dialogue-as-speech-bubble · feedback-as-character-bubble · sequential-scene-choreography **3개 태그를 하나의 규칙으로 통합**
- 최종 발생 횟수: 16 (dialogue 8 + feedback 5 + sequential 3)
- 규칙화일: 2026-07-15
- 반영한 rule 위치: `prompts/builder_system.md`의 "channel 렌더링 계약" 절
- 사례:
  - **dialogue-as-speech-bubble (8회)** — 튜토리얼 대사를 작업대 보드 빈 공간(`.wb-note`)에 끼워 넣음 / 말풍선을 상단 코너에 고정해 캐릭터와 떨어져 "붕 떠 보임" / 유형 A·B·C 안내 대사가 전광판·보드·모니터의 표면 텍스트로 들어감 / 퀴즈 정답 대사가 다른 씬과 **다른 `.bubble` 컴포넌트**로 떠 있음 / 인증서 마무리 대사가 인증서 종이 안 `.cert-caption`에 박힘 / 이야기 대사가 책 지면 `.cap` 캡션에 박힘.
  - **feedback-as-character-bubble (5회)** — 정오답 피드백이 3:1 좁은 `.status-tag`에서 세로로 깨짐 / 스펙이 요구한 중앙 말풍선 팝업 미적용 / 피드백을 전용 도장 이미지로 요청 / 캐릭터 옆 짧은 대사를 모든 문제에 요청했는데 **새 말풍선을 만들어 "기존 것을 재사용하라"고 재지적** / 오답 시 confused pose가 idle로 복귀하지 않아 고민 표정이 고착됨.
  - **sequential-scene-choreography (3회)** — 문제 인트로가 모든 요소를 한 번에 띄우는 단일 장면 / 복구 씬이 두 캐릭터 대사를 하나의 plaque banner에 통째로 담음 / 인증서 씬도 마무리 대사가 캡션으로 박힌 단일 장면.
- 조치(전문):
  - **근본 원인.** planner는 `elements[].channel`로 각 줄의 역할(`dialogue`, `feedback`, ...)을 **이미 태깅하고 있었는데**, builder에는 그 channel을 어떻게 렌더할지에 대한 계약이 없었다. 그래서 builder가 매번 자기 판단으로 표면을 골랐고, 대사가 plaque·board·monitor·인증서·책 지면 등 그때그때 다른 곳에 들어갔다. 말풍선도 계약이 없으니 씬마다 새로 만들어져 `.speech`와 `.bubble`과 `.kid-say`가 혼재했다.
  - **수정.** `builder_system.md`에 "channel 렌더링 계약" 절 신설. `dialogue`는 반드시 기존 speech_bubble asset 재사용 + 화자 머리 옆(head-height) 배치, 표면 텍스트·자막 카드 금지, 한 section에 여러 줄이면 순차 beat 전개. `feedback`은 캐릭터 표정 전환 + 캐릭터 옆 말풍선(dialogue와 같은 에셋) + 중앙 도장의 3층 동시 구현, 오답 pose는 말풍선 종료 시 idle 복귀(취소 가능 타이머).
  - **왜 이 위치인가.** design_review의 creative_direction(제안)이 아니라 builder의 계약(예방)에 넣었다. 검출만 두면 builder가 계속 틀리고 iteration을 낭비한다. 그리고 `channel`이 planner 스키마의 실제 필드이므로 "태깅은 스키마가, 렌더는 계약이" 맡는 반(半)구조적 형태가 된다.
- rule 문구: "`elements[].channel`이 `dialogue`면 기존 speech_bubble 에셋 말풍선으로 화자 머리 옆에 렌더하고 표면 텍스트로 넣지 않는다. 말풍선은 새로 만들지 말고 재사용한다. 여러 줄이면 순차 beat로 전개한다. `feedback`이면 표정 전환 + 캐릭터 말풍선 + 중앙 도장을 함께 구현하고, 오답 pose는 말풍선 종료 시 idle로 되돌린다."
- 검증: **미검증.** 프롬프트 계약이라 builder 산출 HTML을 실제로 확인해야 한다. 2026-07-15 full run(ch8a0715)이 돌긴 했으나 이 계약을 넣기 **전**의 프롬프트로 실행된 것이라 검증에 쓸 수 없다. 검증 방법은 명확하다 — 새 run의 HTML에서 `channel: dialogue` 요소가 speech_bubble asset 위에 렌더됐는지, 씬마다 다른 말풍선 컴포넌트가 섞이지 않았는지 확인한다.
- 한계: 스키마로 강제할 수 없는 프롬프트 규칙이다. 다만 "dialogue 요소가 `.speech` 안에 렌더됐는가"는 사후 검증이 가능하므로, 재발하면 design_review 체크나 코드 검증으로 승격할 여지가 있다.
- 재발 이력:
  - 없음 (2026-07-15 기준).

### [character-asset-identity-alpha] 캐릭터 에셋이 포즈마다 다른 인물로 생성됨 (정체성 부분)

- 대상: content-harness-pipeline (planner/design_review/asset_generator 경로 전반), 산출 예: runs/2026-07-08_ch802d08/output/assets/teacher_*.png, kid_librarian_*.png
- 분류 태그: character-asset-identity-alpha
- 최종 발생 횟수: 9 (원 항목 17회 중 정체성 관련 9회. 알파/프린지 8회는 [character-asset-alpha-fringe]로 분리되어 problem.md에 열린 상태로 남음)
- 규칙화일: 2026-07-15
- 반영한 rule 위치: **AGENTS.md 문서 규칙이 아니라 파이프라인 구조로 강제함.** `schemas/planner_output.schema.json`(characters 엔티티 + asset_plan.character_id), `prompts/planner_system.md`, `stages/design_review.py`(compact_planner_context), `runner.py`(apply_asset_regeneration_patch, attach_identity_context), `prompts/design_review_system.md`, `prompts/asset_generator_system.md`, `schemas/asset_generator_output.schema.json`, `schemas/design_review_{model_,}output.schema.json`
- 사례:
  - 2026-07-09: 꼬마 사서가 원래 필요한 캐릭터가 아니라 다른 학생으로 생성됨.
  - 2026-07-09: 꼬마 사서를 기존 에셋과 무관한 새 캐릭터로 설계하도록 요청. 기존 에셋은 실패 사례 참고로만 취급.
  - 2026-07-10: output/assets의 꼬마 사서가 포즈마다 성별이 바뀜 — idle/success/confused는 남자아이, explaining만 여자아이.
  - 2026-07-10: `teacher_happy`/`teacher_pointing`이 `teacher_worried`와 색상·디자인이 달라 같은 인물로 안 보임. worried 기준으로 통일 요청.
  - 2026-07-10: 재생성한 `teacher_happy` 얼굴에 기준보다 강한 홍조.
  - 2026-07-13: `kid_librarian_idle`만 다른 포즈보다 전체 색감이 붉음.
  - 2026-07-13: `teacher_happy`가 다른 teacher 포즈와 통일성이 어색.
  - 2026-07-13: 재생성 시안 얼굴에 얼룩처럼 불균일한 피부 명암.
  - 2026-07-13: 로컬 보정으로 해결 안 돼 새 기준 이미지를 첨부하고 전체 재생성 요청. 이후에도 조건 없이 재생성 재요청.
- 조치(전문):
  - **근본 원인 규명(2026-07-15, 코드 확인).** 원인은 이미지 생성 품질이 아니라 **재생성 경로의 구조**였다.
    - **D1 — 눈 감고 덮어쓰기.** `design_review.py`의 `compact_planner_context()`가 allowlist라 asset의 `style_constraints`를 design_review에 **전달하지 않는데**, `assetRegenerationRequest` 스키마는 `style_constraints`를 required로 **출력하라고** 요구했고, `runner.py`가 그 값으로 원본을 **통째로 대입**했다. 즉 원본을 본 적 없는 stage가 정체성이 살던 유일한 자리를 재작성했다.
    - **D2 — 형제 포즈 제거.** `build_batch_planner_output()`이 재생성 대상만 남기고 asset_plan을 좁혀, `teacher_happy` 하나만 재생성하면 `teacher_worried`/`teacher_pointing` 스펙이 payload에서 사라졌다. `asset_generator_system.md`는 "batch 안의 asset끼리 캐릭터를 강하게 맞춘다"고 지시하지만 **batch에 혼자면 맞출 대상이 없다.**
    - **D3 — 정체성 소유자 부재.** 정체성이 `art_direction.character_rules`(모든 캐릭터를 한 문자열에) + asset마다의 `style_constraints` 자유문자열에 흩어져 있었다. ch802d08 planner를 실제로 열어보니 `style_constraints`가 `"teacher_worried와 동일 캐릭터"`, `"반복 캐릭터 규칙 유지"` 같은 **참조 사슬**이었다 — 그런데 D2가 그 참조 대상을 batch에서 잘라냈다. 맞출 기준이 payload에 없으니 drift는 필연이었다.
  - **수정(구조로 강제).**
    - planner에 `characters[]` 1급 엔티티 신설 — `identity`(face/hair/outfit/palette/proportions/distinctive_features) + `reference_asset_id`(기준 포즈 = source of truth). `asset_plan`에 `character_id` 참조 추가. `style_constraints`는 그 컷의 포즈·표정·소품·시선만 담도록 축소하고, `art_direction.character_rules`는 공통 그리기 규칙만 담도록 축소.
    - `compact_planner_context`에 `characters`·`character_id`·`style_constraints`·`composition_notes`·`negative_prompt` 전달 추가(D1 차단). 겸사겸사 죽어 있던 필드 수정: `interaction_summary`(planner에 없는 키 → 항상 "")→`interactions`, `section.interaction`(항상 None)→`interaction_ids`, `notes`(스키마에 없음)→`alt_text`+`status`.
    - `apply_asset_regeneration_patch()` 도입 — wholesale 대입 → **patch merge**. 빈 문자열/빈 배열 = "원본 유지". `character_id`는 patch 대상에서 제외해 캐릭터 소속 변조 자체를 불가능하게 함(D1 차단).
    - `attach_identity_context()` 도입 — asset_plan을 좁히기 **전에** 캐릭터 identity + 형제 포즈 + 기준 포즈 이미지 경로를 붙여, `build_batch_planner_output`의 `.copy()`로 배치까지 전파. **`asset_plan`에는 넣지 않아** 형제가 재생성되지 않게 함(D2 차단).
    - `asset_generator_output`에 `character_id` 기록(정체성 추적).
    - 스키마/프롬프트 모순 해소: `assetRegenerationRequest`의 `minLength:1`이 빈 문자열 patch 정책을 금지하고 있어 제거. `design_review_output`의 `newAssetRequest`에 `character_id`가 없어 `additionalProperties:false`로 최종 출력이 REJECT 날 상태였던 것을 model 스키마와 거울로 맞춤. `reason`/`impact` 등 근거 필드는 `minLength:1` 유지해 근거 없는 재생성 요청은 계속 차단.
  - **검증.** codex `--output-schema` 3개(planner/asset_generator/design_review_model) 전부 수락, 산출물도 스키마 통과. 실제 스토리보드로 planner-only run 실행(`runs/2026-07-15_ch802d14`, PASS, 196s) → 캐릭터 2명·포즈 7개가 나왔고 **7개 전부 `style_constraints`에 정체성 재서술 0건**(포즈·표정·시선만). 단일 포즈 재생성 시뮬레이션에서 batch에 asset 1개만 남아도 identity + 기준 포즈 + 형제 목록이 따라오는 것 확인.
  - **full run 검증(2026-07-15).** 위에 "codex에 이미지 생성 도구가 없어 전체 run 불가"라고 적었던 것은 **틀린 판단이었다**(MCP 목록만 보고 problem.md의 7/10 기록을 검증 없이 믿음 — 실제로는 이미지 생성이 정상 동작). ch8_input.json으로 full run 2회 실행 결과:
    - **정체성은 run 안에서 완벽히 유지됐다.** 두 캐릭터 × 3포즈가 모두 같은 인물이고 identity 명세와 일치.
    - **그러나 이 수정의 타깃 시나리오는 발생하지 않았다.** design_review의 재생성 요청 13건이 전부 소품·표면이라 캐릭터가 하나도 재생성되지 않았고, 각 캐릭터의 포즈가 한 batch에 묶여 생성돼 기존 "batch 안에서 맞춘다" 방식만으로도 성립하는 상황이었다. **즉 D1/D2가 막는 상황이 안 왔으므로 이 수정의 효과는 여전히 미검증이다.**
    - 검증에 필요한 조건: design_review가 **캐릭터 asset**의 재생성을 요청하고, 그 포즈가 형제와 분리된 batch로 가는 경우. 재현하려면 캐릭터 하나를 의도적으로 `--asset-generator-missing-only`로 단독 재생성해 보는 것이 가장 빠르다.
- rule 문구: "캐릭터 정체성은 planner의 `characters`가 단일 소유자다. asset은 `character_id`로 참조만 하고 정체성을 재서술하지 않는다. 정체성 판단이 갈리면 `reference_asset_id`의 기준 포즈가 source of truth다. 재생성 요청은 덮어쓰기가 아니라 patch이며(빈 값 = 원본 유지), 원본을 보지 못한 stage는 그 필드를 재작성하지 않는다. 포즈를 하나만 재생성하더라도 identity와 기준 포즈가 batch까지 따라간다." — 문서 규칙이 아니라 schema/runner/prompt로 강제됨.
- 재발 이력:
  - 없음 (2026-07-15 기준). 재발 시 problem.md 스텁의 횟수를 +1 하고 여기에 사례를 덧붙인다.
