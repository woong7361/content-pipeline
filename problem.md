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

- 대상: content-harness-pipeline/runs/2026-07-15_ch8a0715/output/index.html
- 분류 태그: asset-native-ui-design-reject
- 상태: 열림
- 발생 횟수: 3
- 최초 발생일: 2026-07-15
- 최근 발생일: 2026-07-15
- 사례:
  - 2026-07-15: design_review가 desktop 기준 REJECT. 튜토리얼, 활동2 유형 A/B/C, 팝업 퀴즈, 최종 인증서에서 핵심 학습 UI가 장면 속 asset 표면에 흡수되지 않고 흰 웹 패널/카드/키패드/모달처럼 떠 있으며, 최종 장면에서는 말풍선과 CTA가 겹친다고 지적.
  - 2026-07-15: design_review iter_002가 desktop 기준 REJECT. Type B/C 키패드와 확인 버튼이 콘솔 밖으로 돌출되고, 팝업 퀴즈 질문·선택지가 종이 카드 밖에 떠 있으며, 팝업북 asset이 배경을 포함해 restored lobby 위에 다른 장면처럼 겹친다고 지적. 반복 CTA도 일반 CSS 버튼처럼 보인다고 지적.
  - 2026-07-15: design_review iter_003가 desktop 기준 REJECT. 튜토리얼 작업대의 안내문·카드 라벨이 asset surface 경계에 걸치고, 활동2 Type A/B/C 콘솔의 시계 라벨·키패드·확인 CTA가 버튼/슬롯 중심에 맞지 않으며, 에너지 게이지와 scene title도 웹 UI처럼 보인다고 지적.
- 조치: 이번 refine에서 기존 생성 asset(`title_mission_banner`, `reusable_library_ticket_button`, `tutorial_repair_workbench`, `time_quiz_control_console`, `popup_quiz_paper_card`, `final_certificate_frame`)을 활용해 HTML/CSS/JS 배치를 수정하고 `design_refine_preview` desktop 캡처로 확인.
- 규칙화 메모: 아직 2회. 반복되면 "builder/refine은 planner가 요구한 interaction surface asset이 존재할 때 full-width 웹 패널을 유지하지 말고, 동적 텍스트와 조작 target을 asset safe zone 안으로 정렬한다" 규칙을 builder/refine prompt에 제안 후보.

### [planner-storyboard-detail-loss] planner.json이 storyboard 세부(문제 보기·대사·오디오·모션·효과)를 압축/누락함

- 대상: content-harness-pipeline/stages/planner.py, schemas/planner_output.schema.json, prompts/planner_system.md (산출: runs/2026-07-08_ch802d08/ch802d08_planner.json)
- 분류 태그: planner-storyboard-detail-loss
- 상태: 열림
- 발생 횟수: 1
- 최초 발생일: 2026-07-13
- 최근 발생일: 2026-07-13
- 사례:
  - 2026-07-13: `2학년_8차시(시간)_임상현.md`(storyboard)와 `ch802d08_planner.json`을 비교하니 차이가 큼. storyboard가 요구한 요소(이미지, 대사, 문제 문구, 보기(distractor), 캐릭터 포즈, 효과, 애니메이션, 오디오/SFX)가 요약되거나 생략됨. 특히 활동2 12문제의 정확한 문제 문구·보기 3개·정답이 planner에서는 content_outline 한 줄로 압축되어 정답만 남고 오답 보기가 사라짐. 사용자가 schema가 너무 정적이거나 prompt 문제로 추정하고, storyboard를 온전히 담을 수정 방향을 요청.
- 조치: (분석 제공) 근본원인 = (1) section schema가 scene-level 자유문자열 배열(content_outline/staging_notes)뿐이라 문제항목/대사/오디오/피드백을 담을 typed 슬롯이 없음 → 모델이 압축. (2) 문제·보기·정답을 담는 구조가 아예 없어 12문제가 한 줄로 뭉개짐(하류 [typeB-problem-text-mismatch-spec]/[typeA-prompt-text-small-terse]의 상류 원인). (3) prompt가 verbatim 보존을 요구하지 않고 오히려 "생략" 을 정상 절차로 언급, asset 지시(20여 줄)에 편중. (4) 오디오/SFX는 schema·prompt 어디에도 없음. → 권고: ①section에 닫힌 `questions` 배열(prompt/choices/answer/input_type/feedback, 모든 필드 required·N/A는 빈값) 추가 ②대사/오디오/피드백 typed 슬롯 분리 ③"문제문구·보기·정답·대사·버튼/전환 텍스트는 원문 그대로 보존, 오답 보기도 전부 보존" verbatim 규칙을 prompt에 추가 ④section에 `source_ref`(storyboard scene) 추가해 커버리지 결정적 검증(→[content-eval-scoring-too-lenient] 연계) ⑤오디오 범위 명시(담을지/의도적 제외인지).
- 규칙화 메모: 아직 1회. 이 항목은 상위 원인(메타)에 가까움 — 하류 [typeB-problem-text-mismatch-spec], [typeA-prompt-text-small-terse], [spec-success-feedback-missing], [type-per-problem-answer-format] 계열이 "builder가 spec대로 안 만든다"로 반복되는데, 실은 planner가 spec을 온전히 안 넘긴 것이 상류 원인. 반복되면 "planner는 storyboard의 문제 문구·보기·정답·대사·전환/성공 메시지를 원문 그대로 보존하고, 자유문자열로 압축하지 말고 typed 슬롯(questions/dialogue/audio/feedback)에 담는다" 규칙을 planner_system.md에 제안 후보.

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

- 대상: content-harness-pipeline/runs/2026-07-08_ch802d08/output/assets/stamp_correct_time.png, stamp_fail_time.png
- 분류 태그: feedback-stamp-visual-overload
- 상태: 열림
- 발생 횟수: 4
- 최초 발생일: 2026-07-09
- 최근 발생일: 2026-07-16
- 사례:
  - 2026-07-09: 정답/실패 도장 시안이 시계 눈금, 바늘, 체크/X, 깨짐선, 큰 글자가 겹쳐 너무 이상하게 보임. 사용자가 원형 시계 배경 위에 `정답!`/`실패!` 글자를 단순히 얹는 방식이 낫다고 지적.
  - 2026-07-09: 재생성한 시계 배경까지 초록/빨강으로 물들어 `index.html`의 애니메이션풍 도서관 시계 톤과 맞지 않음. 사용자가 시계는 상태색이 아니라 index.html 느낌의 애니메이션풍 시계로 두고, 글자만 초록/빨강으로 하라고 지적.
  - 2026-07-09: 기존 시계 asset을 결합하는 방식이 아니라, 도장 자체를 단일 이미지로 생성해야 한다고 지적.
  - 2026-07-16: asset_generator 예시(exemplar) 도입 검증 중 관측. leak test(심해 정거장, 보라·라임 art_direction)에서 오답 도장이 연보라 잉크 on 보라 패널로 나와 "오답"이 안 읽힘. 정답=코랄, 오답=슬레이트로 만든 예시도 한국 관습(빨간펜=오답)과 반대였음. 사용자가 "오답이 빨간색이면 좋겠다, 문자열이라도"라고 교정. **결정**(질문 확인): 오답 신호는 **글자·심볼만 빨강**, 도장 몸체는 그 run의 세계관 팔레트 유지. 예시 재생성은 안 함(예시 색은 어차피 art_direction이 덮어씀). 2026-07-09 두 번째 사례("몸체는 세계관색, 글자만 상태색")와 **같은 원칙의 재발**이며, 이번엔 index.html이 아니라 asset_generator/exemplar 층에서 발생.
- 조치: **2026-07-16 프롬프트 규칙 추가.** planner_system.md 이미지 텍스트 절에 "판정 피드백(오답) 도장의 문구·심볼은 art_direction 팔레트와 무관하게 경고 빨강을 유지하고, 도장 몸체·테두리만 세계관 팔레트를 따른다"를 명시. 상류 2026-07-09 조치(도장형 과밀 그래픽·상태색 배경 버리고 단일 생성 이미지)는 유지.
- 규칙화 메모: **4회 — 5회 도달 시 다음 작업 전 rule 승격 제안 예정.** 누적 원칙이 안정적임: "학습 피드백 이미지는 핵심 메시지 텍스트와 배경 메타포를 분리하고, 배경 오브젝트는 화면 기존 asset 팔레트를 유지하며 상태색(특히 오답=빨강)은 텍스트/심볼에만 쓴다. 사용자가 단일 asset을 요구하면 기존 asset 합성/코드 합성 대신 생성 이미지 하나로 만든다." 반영 위치 후보: `content-harness-pipeline/AGENTS.md`(파이프라인 지역 규칙). 연관 [spec-fx-color-mismatch](오답 연출색을 임의로 바꾸지 말 것 — index.html 층의 같은 '오답=빨강' 계열).

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

- 대상: content-harness-pipeline/runs/2026-07-08_2d08c0de/output/index.html
- 분류 태그: intro-title-raster-image
- 상태: 열림
- 발생 횟수: 2
- 최초 발생일: 2026-07-08
- 최근 발생일: 2026-07-08
- 사례:
  - 2026-07-08: 사용자가 인트로의 `시간이 뒤죽박죽! / 수학의 힘으로 도서관 시계를 수리하라!` 문구를 예시처럼 이미지 생성 타이틀로 만들고, 1번 후보를 인트로에 삽입하길 요청했다.
  - 2026-07-08: 사용자가 삽입된 생성 이미지를 화면 가운데에 오게 하고, 주변 화면을 어둡게 만들어 아직 시작하기 전이라는 느낌을 주길 요청했다.
- 조치: 이미지 생성 후보 1번을 `output/assets/intro_title_time_repair_v1.png`로 복사하고 인트로 타이틀 영역에 삽입한다. 이후 인트로 이미지 타이틀을 중앙 정렬하고 배경 dim/vignette를 강화한다.
- 규칙화 메모: 아직 발생 2회로 rule 승격 대상이 아니다.

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
- 발생 횟수: 11
- 최초 발생일: 2026-07-09
- 최근 발생일: 2026-07-10
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
- 규칙화 메모: **발생 11회 → rule 승격 제안.** 초안: "초등(저학년) 대상 콘텐츠는 본문/질문/힌트/**버튼(CTA)** 글자 clamp의 max와 vw 계수를 성인 기준보다 크게 잡는다(예: 본문 max ≥ 1.6rem, 주요 CTA max ≥ 1.8rem). 표면 박스/티켓 asset 위 텍스트도 동일 배율." 반영 위치: content-harness-pipeline/builder_system.md. 사용자 승인 대기.

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
