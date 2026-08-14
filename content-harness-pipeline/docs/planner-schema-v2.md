# planner_output schema v2 설계안

상태: **승인 대기**. v1은 그대로 살아 있고 이 문서가 가리키는 파일은 전부 초안이라 아직 아무것도 안 깨진다.

- 초안 스키마: `schemas/planner_output.v2.draft.schema.json`
- 실제 샘플: `docs/planner-schema-v2-sample.json` (`shape-find`·`shape-count`를 v2로 새로 씀, 스키마 PASS, 문구 손실 0)

## 1. 왜 바꾸는가

v1의 `sections[].elements[]`는 **스토리보드 줄의 목록**이고, 순서는 부수적인 주석이다.
필요한 것은 **실행 타임라인**이다. 이 차이 때문에 세 가지가 무너져 있다.

### 1.1 빌드를 지시하는 필드와 검증을 파생하는 필드가 다르다

```
planner ──reveal──────────► test_spec_derive ──► functional_test   (검증)
        └─notes / staging_notes ──► builder                         (빌드)
```

`prompts/builder_system.md`에는 **`reveal`이 한 번도 안 나온다.** builder는 `notes`와
`staging_notes`(둘 다 자유 산문)만 읽으라고 지시받는다. 반면 `stages/scripts/test_spec_derive.py`는
`reveal`만 읽어 타임라인을 만든다. 둘을 맞추는 코드는 없다.

그래서 planner가 순서를 산문에만 적고 `reveal`을 전부 `scene_enter/0`으로 두면 —
실제로 `runs/2026-08-14_dfbc1027`의 `shape-count`는 9개 요소 중 6개가 그랬다 —
테스트는 "진입 즉시 전부 보여야 한다"를 요구하고 builder는 순차 연출할 근거가 없어 한꺼번에 띄운다.
**두 결함이 서로를 가려 게이트가 통과된다.**

### 1.2 `reveal`은 텍스트 노출 계약이라 연출을 겸할 수 없다 (실측)

손보정 실험(`runs/2026-08-14_dfbc1027-seq`, builder + 루프 3회 완주)에서 확정했다.
`collect_reveals`가 `rendered_text`가 빈 요소를 건너뛰므로(`test_spec_derive.py:98`),
글자를 안 띄우는 연출 지시 요소는 beat를 줘도 타임라인에 들어가지 않는다.
그 상태로 builder에 beat index만 전달되자 builder는 자기가 아는 유일한 beat 어휘인
`dialogue`로 해석해 **같은 문구를 4번 복제한 beat를 만들었다.**

```js
// 손보정한 planner를 받은 builder의 산출
beats: [
  { type: "dialogue", text: "잘 찾았어요!" },
  { type: "dialogue", text: "페인트 색깔마다 모양이 달라요" },
  { type: "dialogue", text: "● ■ ▲ 모양" },   // ← 연출 step이 대사로 퇴화
  { type: "dialogue", text: "● ■ ▲ 모양" },
  { type: "dialogue", text: "● ■ ▲ 모양" },
  { type: "dialogue", text: "● ■ ▲ 모양" },
  { type: "activity" }
]
paintCan: { style: "left:360px;top:520px" }   // 통 하나 고정. 초록→파랑→빨강 순차 없음
```

`animation-delay` 0건, stagger 로직 없음. design_review가 독립적으로 같은 것을 잡았다 —
*"씬 진입 요소의 순차 등장 연출이 없다. stageFadeIn만 있고 개별 요소 delay나 stagger class가 없다."*

**손보정 전보다 나쁜 산출이다.** 표현할 자리가 없는 것을 있는 자리에 밀어 넣으면 이렇게 된다.

### 1.3 문항이 시점을 갖지 못한다

`questions[]`에는 `reveal`이 없다. 문항의 시점은 그 문항을 `refs`로 가리키는 element가 들고 있는데,
`build_question_cases`는 `reveals`를 인자로 받고도 lead step에 쓰지 않는다.
그래서 4장짜리 캐러셀의 2번째 장 문항을 1번째 장에서 누르려다 타임아웃한다.

이것이 `2026-08-14_dfbc1027`의 iter_001~003에서 계속 잡힌 실패 3건의 정체이고 **HTML 버그가 아니다.**
content_refine이 3 iteration 동안 멀쩡한 HTML을 고치러 갔다.

더 나쁜 것은 그 다음이다. 손보정 run의 iter_002는 97/97 PASS가 났는데, 통과 경로가
builder가 넣은 검증기 전용 텔레포트 훅이었다. builder가 코드에 직접 남긴 주석:

> `// '다음 문제'는 풀지 않아도 열 수 있다(검증기가 각 문항에 도달하는 통로다).`

**테스트가 학습 설계를 바꾸고 있다.** 그리고 `text_case`는 `text_visible`만 단언하고
"아직 안 보여야 한다"는 단언하지 않으므로 이 약화는 어떤 게이트에도 안 걸린다.

## 2. 무엇을 바꾸는가

**`sections`만 바꾼다.** `page`·`art_direction`·`characters`·`interactions`·`asset_plan`·`asset_groups`는
문제의 원인이 아니므로 손대지 않는다. 초안 스키마도 v1에서 프로그램으로 파생시켜 이 부분이
한 글자도 안 달라지게 만들었다.

### 2.1 새 구조

```
sections[]
  id · title · purpose
  steps[]        ⭐ 신설. 배열 순서가 곧 시간 순서다
  questions[]    정의만 담는다. 언제 푸는지는 steps가 정한다
  asset_ids[] · advance
```

`steps[]` 항목:

| 필드 | 역할 |
|---|---|
| `id` | step 식별자 |
| `kind` | `narration` \| `staging` \| `question` \| `feedback` \| `transition` |
| `lines[]` | 이 시점에 나타나는 스토리보드 줄. `channel`·`speaker`·`content`(원문)·`rendered_text[]` |
| `staging[]` | 이 시점에 일어나는 화면 변화 ⭐ 신설 |
| `question_id` | `kind=question`일 때 푸는 문항. **한 시점에 문항 하나** |
| `condition` | `on`: `always` \| `correct` \| `wrong` \| `exhausted` + `question_id` |
| `advance` | `by`: `auto` \| `tap` \| `correct_answer` \| `exhaust_attempts` \| `none` + `label` |
| `notes` | 남는 자유 서술. **여기 적은 것은 아무도 검증하지 않는다**고 명시 |

`staging[]` 항목 — v1에 없던 자리:

| 필드 | 역할 |
|---|---|
| `order` | 같은 step 안에서 **자동으로 이어지는** 순번(0부터). 학습자 조작이 개입하지 않는다 |
| `target` / `target_kind` | 변하는 대상과 그 이름이 속한 목록(`asset`\|`character`\|`question`\|`surface`) |
| `action` | `appear` `disappear` `move` `highlight` `replace` `change_state` `background_transition` |
| `to_state` | 변화 뒤의 상태를 평어로 |
| `duration_hint` | `instant`\|`short`\|`medium`\|`long`. **ms는 planner가 정하지 않는다** |
| `source_line` | 이 연출의 근거가 된 원문 조각. 계획이 정한 배치면 빈 문자열 |

`questions[].targets[]` — hotspot·drag_drop의 정답 실체:

`name` · `anchor_asset_id` · `correct` · `appear_order`

### 2.2 v1 → v2 매핑

| v1 | v2 | 비고 |
|---|---|---|
| `elements[]` | `steps[].lines[]` | 줄 개수는 그대로 보존 |
| `elements[].reveal.when=beat/index` | `steps[]` 배열 순서 | 순서가 주석이 아니라 구조가 된다 |
| `elements[].reveal.when=on_page` | `steps[]` 배열 순서 | 캐러셀은 구현 선택이지 계획 어휘가 아니다 |
| `elements[].reveal.when=on_correct/on_wrong` | `steps[].condition.on` | 분기가 제자리를 얻는다 |
| `elements[].notes` (연출) | `steps[].staging[]` | 산문 → typed |
| `staging_notes[]` (섹션 산문) | `steps[].staging[]` | 없어진다 |
| `elements[].refs` | `staging[].target` + `step.question_id` | 참조처가 하나로 모인다 |
| `questions[].answer`(hotspot 개수) | `questions[].targets[]` | 개수 → 실체 |
| — | `steps[].advance.by` | 신설. 진행 계약 |
| — | `staging[].duration_hint` | 신설. ms 없이 크기만 |

**`reveal` 어휘 5종이 통째로 사라진다.** 순서는 배열이, 조건은 `condition`이 담는다.

### 2.3 이건 새 철학이 아니다

`test_spec_derive.collect_prose_only_rules`는 이미 이렇게 적혀 있다.

> 이런 규칙은 planner가 원문을 온전히 보존하고 있는데도 (a) 산문이고 (b) 어느 문항에 걸리는지
> 주소가 없어서 실행 단언으로 못 바뀐다.

v2는 **그 원칙을 시도 규칙에서 순서·연출로 확장한 것**이다. 새로 만드는 규범이 아니다.

## 3. 이걸로 요구가 담기는가

사용자 요구: *"배경은 담장이고, 모양 2개를 찾아봅시다 하면 뒤에 페인트통이 있고, 세모 모양 2개가 순차적으로 나타나는"*

`docs/planner-schema-v2-sample.json`에서 `shape-count`의 그 자리:

```json
{ "id": "paint-sequence", "kind": "staging", "advance": { "by": "auto", "label": "" },
  "staging": [
    { "order": 0, "target": "paint-can-body", "action": "appear",
      "to_state": "초록 페인트통이 담장 앞 왼쪽에 놓임",
      "source_line": "페인트와 모양이 초록, 파랑, 빨강 순으로 등장" },
    { "order": 1, "target": "paint-can-body", "action": "change_state",
      "to_state": "초록 원 3개가 담장에 찍힘",
      "source_line": "예)초록 페인트-> 원 모양 3개 등장 순" },
    { "order": 2, "target": "paint-can-body", "action": "appear",
      "to_state": "파랑 페인트통이 가운데에 놓임" },
    ...
  ]
}
```

두 화면의 타임라인이 이렇게 나온다.

```
shape-find (14 steps)                          shape-count (8 steps)
  open              narration  auto              praise         narration  tap
  d-boy             narration  tap               intro-color    narration  tap
  d-teacher-1       narration  tap               legend         narration  auto
  d-teacher-2       narration  tap               paint-sequence staging    auto  ×6
  d-kids            narration  tap               q-circle       question   correct
  open-observation  staging    auto              q-triangle     question   correct
  q1                question   correct           q-square       question   correct
  q1-wrong          feedback   auto  [wrong]     exit           staging    none
  q1-exhausted      feedback   auto  [exhausted]
  q1-correct        feedback   auto  [correct]
  swap-observation  transition auto  [correct]
  q2                question   correct
  q2-correct        feedback   auto  [correct]
  exit              staging    none
```

검증 결과: **v2 스키마 PASS · 학습자 노출 문구 15개 중 손실 0 · Codex strict 감사 위반 없음.**

`3번 오답이면 정답 모양에 숫자가 뜬다`처럼 v1에서 `attempt_policy`에만 있고 화면에서 무슨 일이
일어나는지는 아무도 몰랐던 규칙이, 이제 `q1-exhausted` step의 `staging`으로 내려온다.

## 4. 하류 변경 목록

| # | 파일 | 무엇을 |
|---|---|---|
| 1 | `schemas/planner_output.schema.json` | 초안을 승격. v1은 `planner_output.v1.schema.json`으로 보존 |
| 2 | `validate.py` | `schema_version`/`steps` 유무로 v1·v2 분기. **v1은 `revalidation=True`에서만 통과** |
| 3 | `stages/scripts/planner_check.py` | `check_section` 재작성. `compare_planner`의 `count_view`·`text_view`를 steps 기준으로 |
| 4 | `stages/scripts/test_spec_derive.py` | `collect_reveals`·`build_pace_steps`·`build_timing_cases` 폐기, steps 순회로 대체. **`build_question_cases`가 문항 앞 step들을 lead로 받는다** |
| 5 | `prompts/planner_system.md` | steps 타임라인 작성 규칙. "순서는 배열이고 연출은 staging이다" |
| 6 | `prompts/builder_system.md` | **`reveal`이 아니라 `steps`를 타임라인 계약으로 명시** (현재 언급 자체가 없다) |
| 7 | `prompts/planner_refine_system.md` | 고칠 대상 어휘 갱신 |

### 새로 가능해지는 기계 검사 (LLM 0회)

- 한 step에 문항 둘 이상 → 위반 (v1의 캐러셀 4문항 묶임을 잡는다)
- `condition.on != always` 인데 `question_id`가 빔 → 위반
- `staging[].target`이 `target_kind` 목록에 없음 → 위반 (미아 참조)
- `advance.by=tap` 인데 `label`이 `rendered_text` 어디에도 없음 → 위반 (누를 것이 화면에 없다)
- 마지막 step의 `advance.by`가 `none`이 아님 → 위반
- 문항 도달 lead step이 파생됨 → **텔레포트 훅 없이 걸어서 문항에 닿는다**

### 함께 고쳐야 하는 것

`text_case`에 "이 시점엔 아직 안 보인다" 단언을 추가하지 않으면, 위를 다 고쳐도
**게이트가 여전히 순차성을 안 지킨 산출물을 통과시킨다.** 지금은 positive 단언만 한다.

## 5. 위험과 미해결 질문

1. **산출 크기.** step 구조는 v1보다 장황하다. 현재 planner 산출이 117KB인데 12개 화면 전체가
   v2로 가면 더 커진다. 생성 truncation이 나면 화면 수를 줄이는 게 아니라 화면 단위로 나눠
   생성하는 쪽을 봐야 한다.
2. **회귀 검사 오탐.** v2는 v1이 중복으로 들고 있던 것을 정당하게 합친다(예: 문제 문구 템플릿과
   그 인스턴스). `compare_planner`가 이를 손실로 잡을 수 있다. 마이그레이션 시 1회 예외가 필요할지
   판단해야 한다.
3. **`targets[]`의 지어내기 경계.** 스토리보드가 `모양 2개를 찾아 봅시다`라고만 하고 *어떤* 모양인지
   말하지 않는 자리가 실제로 있다. 샘플에서는 범례 순서(●■▲)를 근거로 원 모양으로 읽었지만,
   planner가 이런 원문 공백을 조용히 메울지 드러낼지는 정해야 한다. `planner_refine_system.md`의
   "스토리보드에 없는 것을 만들지 않는다"와 닿는 자리다.
4. **원문 자체의 모순.** `shape-count` 한 화면에서 내레이션은 ●▲■ 순, UI 요소 표는 원→사각형→삼각형
   순이다. v2도 이 모순을 자동으로 풀지는 못한다. 계획이 한쪽으로 정하고 근거를 `source_line`에
   남기는 것까지가 한계다.
5. **구 run 재개.** 결정대로 v1은 재검증만 유지한다. 기존 20개 run은 validate는 되지만
   `--start-at builder` 재개는 안 된다.
