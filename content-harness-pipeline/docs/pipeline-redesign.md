# content-pipeline 재설계

세 가지를 동시에 바꾼다.

1. planner의 의도를 **실행되는 결정적 게이트**로 만든다.
2. design system을 `source/common`에서 가져와 **획일화**한다.
3. `source/[teacher]`로 **선생님별 특성화**를 얹는다.

이 문서는 설계만 담는다. 구현 순서는 9장에 있다.
현재 파이프라인의 사실관계는 `CLAUDE.md`, 재사용 source 설계는 `reusable-source-design.md`를 따른다.

---

## 1. 왜 바꾸는가

### 1.1 품질 게이트가 실행되지 않는다

`content_rubric.yaml`에는 이미 결정적 의도가 들어 있다.

- `functional_integrity` 축: "필수 버튼, 입력, 진행 상태, 완료 처리가 의도한 흐름대로 동작하는지"
- `hard_gates`: `required_interactions_reachable`, `no_blocking_runtime_errors`

그런데 이 판정을 **LLM이 HTML 텍스트를 읽어서** 한다.
버튼을 눌러 본 적이 없으므로 "동작한다"는 판단에 근거가 없다.

`content_fidelity` 축은 `grep -cF`로 대조해 결정적이지만, **정적 문자열만** 잡는다.
`production/1-2/08/index.html:1702`처럼 보기를 런타임에 난수로 만드는 화면은 원리적으로 못 잡는다.

```js
// 이 문항의 보기는 HTML 파일 안에 문자열로 존재하지 않는다
input.innerHTML = '<div class="choices">' +
  vals.map(n => `<button class="choice"><span>${a} + ${n} = 10</span></button>`).join('') + '</div>';
```

즉 지금은 **"문제를 클릭하면 정답 처리가 되는가"를 아무도 확인하지 않는다.**

### 1.2 design system이 매 콘텐츠마다 새로 태어난다

디자인 토큰이 두 곳에 **다른 값으로** 존재한다.

| 위치 | `--fs-sm` | 팔레트 | 형태 |
|---|---|---|---|
| `prompts/common_html_contract.md` | 31px | 도서관 톤(`#062c3c`) | md 안의 CSS 문자열 |
| `source/common/components/_shared/base.css` | 37px | 파랑 톤(`#49b9ed`) | 실제 CSS 파일 |

프롬프트 안의 CSS는 버전 관리도, 재사용도, 검증도 되지 않는다.
`source/common/components/`에 컴포넌트 6개를 뽑아 뒀지만 **파이프라인이 참조하지 않는다.**

### 1.3 선생님별 정체성을 실을 길이 반쪽이다

`input.metadata.style_reference_set`은 이미 있고 `stages/scripts/style_references.py`가 해석한다.
다만 **이미지 전용**(`backgrounds`/`characters`/`props`/`ctas`)이라 CSS 토큰과 컴포넌트는 못 실어 나른다.

---

## 2. 목표와 비목표

### 목표

- planner가 선언한 의도가 **실행으로 검증**되고, 실패가 게이트를 막는다.
- 콘텐츠가 달라도 구조 토큰과 공용 컴포넌트는 **같다**.
- 선생님이 다르면 팔레트와 asset 화풍이 **다르다**.

### 비목표

- 전체 자동화. `source` 승격과 teacher 생성은 사람 승인을 유지한다.
- 반응형. 1920×1080 고정 캔버스 계약은 그대로다.
- 기존 run 재현. 구계약 run은 마이그레이션 대상이 아니다.

---

## 3. 결정 사항

| # | 결정 | 근거 |
|---|---|---|
| D1 | 결정적 test는 **별도 stage**(`functional_test`)로 분리한다 | 결정적 실행과 LLM 채점을 섞으면 실패 원인 추적이 불가능하다 |
| D2 | test 명세는 **`test_spec` stage**가 만들고, **planner만** 입력으로 받는다 | HTML을 보고 쓴 테스트는 구현을 검증하지 못한다 |
| D3 | **DOM hook 계약을 도입**하고 hook 누락은 게이트 실패로 잡는다 | hook 없이는 난수 생성 문항을 지목할 방법이 없다 |
| D4 | 구조 토큰 SSOT는 `source/common`, 팔레트는 teacher/art_direction | 획일화 목표와 특성화 목표를 층으로 나눈다 |
| D5 | `content_eval`·`content_critique`를 **폐지하지 않고 3축으로 축소**한다 | 테스트는 planner를 검증하지 못하고, 스스로 고치지도 못한다 (5.6) |

---

## 4. 변경 후 파이프라인

```text
input validate
      ↓
planner                         planner.json
      ↓
test_spec        ← 신설         test_spec.json      (planner만 입력, LLM)
      ↓
design_system    ← 신설         resolved_tokens.css (LLM 아님, runner 결정)
      ↓
asset_generator
      ↓
builder                         output/index.html
      ↓
┌─ 품질 루프 ────────────────────────────────────┐
│ functional_test  ← 신설  (playwright, LLM 없음) │
│      ↓ FAIL이면 LLM 리뷰를 건너뛴다             │
│ design_review / content_critique / content_eval │
│      ↓                                          │
│ asset revision → design_refine → content_refine │
└─────────────────────────────────────────────────┘
      ↓
output/index.html
```

`test_spec`과 `design_system`이 **builder보다 앞**에 있는 것이 핵심이다.
builder는 이미 만들어진 검증 계약과 토큰을 **받아서** HTML을 쓴다.

---

## 5. Part 1 — 결정적 게이트

### 5.1 `test_spec` stage

- 입력: `planner.json` **만**
- 출력: `{brief_hash}_test_spec.json`
- LLM: 쓴다 (Codex 기본)
- 금지 입력: HTML, builder output, asset output, design_review, content_eval

builder보다 먼저 돌기 때문에 **구현을 볼 수가 없다.** 규율이 아니라 순서로 강제된다.

#### 출력 schema (초안)

```json
{
  "cases": [
    {
      "id": "case_q3_correct",
      "question_id": "q_shape_count_1",
      "section_id": "section_shape_find",
      "input_type": "choice",
      "intent": "정답 보기를 고르면 정답 피드백이 나오고 다음으로 진행할 수 있다",
      "steps": [{ "action": "select_correct" }],
      "expect": ["feedback_correct_visible", "progress_advances"]
    },
    {
      "id": "case_q3_wrong",
      "question_id": "q_shape_count_1",
      "section_id": "section_shape_find",
      "input_type": "choice",
      "intent": "오답 보기를 고르면 오답 피드백이 나오고 재시도할 수 있다",
      "steps": [{ "action": "select_wrong" }],
      "expect": ["feedback_wrong_visible", "retry_available"]
    }
  ]
}
```

`steps[].action`과 `expect[]`는 **닫힌 enum**이다.
LLM이 자유 문자열로 쓰면 실행기가 해석할 수 없다.

| `action` | 의미 |
|---|---|
| `select_correct` | 정답으로 표시된 선택지를 고른다 |
| `select_wrong` | 오답으로 표시된 선택지 하나를 고른다 |
| `enter_answer` | 정답 값을 입력한다 (keypad) |
| `enter_wrong_answer` | 오답 값을 입력한다 |
| `drag_to_correct` | 정답 대상으로 끌어다 놓는다 |
| `drag_to_wrong` | 오답 대상으로 끌어다 놓는다 |
| `activate` | 버튼/CTA를 누른다 |

| `expect` | 판정 방법 |
|---|---|
| `feedback_correct_visible` | `[data-qa-feedback="correct"]`가 보인다 |
| `feedback_wrong_visible` | `[data-qa-feedback="wrong"]`가 보인다 |
| `progress_advances` | `data-qa-progress` 값이 증가하거나 다음 scene이 활성화된다 |
| `retry_available` | 같은 문항의 입력이 다시 활성 상태다 |
| `completion_reached` | `[data-qa-complete]`가 보인다 |
| `no_console_error` | 이 케이스 실행 중 console error/pageerror가 없다 |

`intent`는 사람이 읽는 필드다. 실행에는 쓰지 않지만 spec 리뷰에 필요하다.

Codex structured output 제약 때문에 `properties`의 모든 키는 `required`에 넣는다(최상단 `CLAUDE.md` 참조).
선택 값은 빈 배열·빈 문자열로 표현한다.

#### 무엇을 case로 만드는가

planner의 `sections[].questions[]` **모든 문항**에 대해 최소 2개(정답 1, 오답 1)를 만든다.
`choices`가 빈 배열이면 `input_type`에 맞는 action을 고른다.
`interactions[]` 중 학습 진행에 필수인 것은 `activate` case를 만든다.

### 5.2 DOM hook 계약

`prompts/common_html_contract.md`의 "Visual QA scene contract"를 확장한다.
기존 `data-qa-scene` / `data-qa-order` / `data-qa-label` / `__contentHarnessShowScene`은 그대로 두고 아래를 **필수**로 추가한다.

| 속성 | 위치 | 값 |
|---|---|---|
| `data-qa-question` | 문항 root | planner `questions[].id` 그대로 |
| `data-qa-choice` | 보기 하나 | 안정적인 식별자. planner에 id가 없으므로 index 기반 허용 |
| `data-qa-correct` | 보기 하나 | `"true"` / `"false"` |
| `data-qa-input` | 입력 위젯 root | `"keypad"` / `"drag_drop"` 등 `input_type` |
| `data-qa-drop` | 드롭 대상 | `"correct"` / `"wrong"` |
| `data-qa-feedback` | 피드백 표면 | `"correct"` / `"wrong"` |
| `data-qa-progress` | 진행 표시 root | 현재 진행 수치 |
| `data-qa-complete` | 완료 화면 root | 존재 자체가 신호 |

```html
<div data-qa-question="q_shape_count_1">
  <button class="choice" data-qa-choice="0" data-qa-correct="false"><span>3개</span></button>
  <button class="choice" data-qa-choice="1" data-qa-correct="true"><span>4개</span></button>
</div>
<div class="feedback" data-qa-feedback="correct" hidden>...</div>
```

세 가지를 못박는다.

- **런타임 생성 요소에도 붙인다.** 난수로 보기를 만드는 코드는 만들면서 hook을 함께 붙여야 한다. 이게 이 계약의 존재 이유다.
- **hook은 UI가 아니다.** 화면에 노출하지 않는다. 기존 QA hook 규칙과 같다.
- **`data-qa-correct`는 정답을 화면에 드러내지 않는다.** DOM 속성일 뿐이고 시각적으로 구분되면 안 된다.

hook이 없으면 `functional_test`가 해당 case를 `hook_missing`으로 실패 처리한다.
이건 "테스트 실패"가 아니라 **"계약 위반"**으로 따로 집계해, 무엇을 고쳐야 하는지 구분되게 한다.

### 5.3 `functional_test` stage

- 입력: `test_spec.json`, `output/index.html`
- 출력: `{brief_hash}_iter-{iteration}_test_report.json` + 실패 케이스 스크린샷
- **LLM을 쓰지 않는다.** playwright 스크립트다.

```python
# LLM 호출 0회
for case in spec["cases"]:
    page.goto(html_uri)
    page.evaluate(show_scene_script, case["section_id"])
    for step in case["steps"]:
        run_action(page, case, step)      # 위 enum → 셀렉터
    for expectation in case["expect"]:
        assert_expectation(page, case, expectation)
```

`stages/visual_qa.py`의 브라우저 기동, 시스템 chromium 탐색, console/pageerror 수집은 그대로 재사용한다.
다만 **visual_qa에 넣지 않는다.** visual_qa는 design_review 소유이고, content 축 게이트를 design 축이 들면 "두 축은 독립" 원칙이 깨진다.

#### 출력 schema (초안)

```json
{
  "total": 24,
  "passed": 21,
  "failed": 2,
  "hook_missing": 1,
  "verdict": "REJECT",
  "failures": [
    {
      "case_id": "case_q3_wrong",
      "question_id": "q_shape_count_1",
      "reason": "expect_failed",
      "expectation": "feedback_wrong_visible",
      "detail": "[data-qa-feedback=\"wrong\"] not visible after 2000ms",
      "screenshot": "iter_001/functional_test/case_q3_wrong.webp"
    }
  ]
}
```

`verdict`는 `passed == total`일 때만 PASS다.

### 5.4 루프 연결

```text
functional_test
   ├─ PASS → design_review / content_critique / content_eval 정상 진행
   └─ FAIL → LLM 리뷰 3개를 건너뛰고 바로 content_refine
```

**FAIL이면 LLM 리뷰를 건너뛴다.** 기능이 깨진 HTML을 세 LLM이 읽어 봐야
"버튼이 동작하지 않습니다"를 세 번 다른 말로 반복할 뿐이고, 그 iteration의 토큰이 통째로 낭비된다.
깨진 것부터 고치고 다음 iteration에서 품질을 본다.

수리 담당은 `content_refine`이다.

- 기능 결함과 hook 누락은 마크업·JS 문제이지 CSS·레이아웃 문제가 아니다.
- `design_refine`은 HTML을 통째로 다시 쓰므로, 여기에 맡기면 고친 hook이 다음 재작성에서 다시 날아갈 수 있다.
- `content_refine`에 `test_report.json`의 `failures[]`를 그대로 넘긴다. 이건 점수가 아니라 **사실**이므로 "refine에 eval 총점을 넘기지 않는다" 원칙에 걸리지 않는다.

`design_refine`도 hook을 보존해야 한다. `common_html_contract`의 "기존 DOM id, event target, data attribute를 보존한다" 조항에 `data-qa-*`를 명시한다.

### 5.5 rubric 축 재배치

테스트가 들어오면 5축 중 2축은 LLM이 판단할 이유가 없어진다.
축을 "실행으로 검증되는 것"과 "판단이 필요한 것"으로 나눈다.

| 축 | 가중치 | 판정 주체 | 근거 |
|---|---|---|---|
| `content_fidelity` | 0.28 | **functional_test** | 문항·보기·정답·순서는 DOM에서 확인된다 |
| `functional_integrity` | 0.12 | **functional_test** | 눌러 보면 안다 |
| `feedback_scaffolding` | 0.20 | test + eval | **존재**는 test, **문장의 질**은 eval |
| `interaction_flow_clarity` | 0.18 | test + eval | **도달 가능성**은 test, **명확성**은 eval |
| `learning_goal_alignment` | 0.22 | eval | 실행으로 나오지 않는다 |

- `content_fidelity`는 테스트가 지금보다 **더 잘한다.** `grep -cF`는 정적 문자열만 보므로 런타임에 생성되는 보기를 못 잡는다. DOM에서 보면 잡힌다.
- `feedback_scaffolding`에서 테스트가 확인하는 것은 "오답 피드백이 떴다"까지다. rubric의 3점과 5점을 가르는 기준은 "결과만 통보하는가" 대 "왜 틀렸는지와 다음 행동을 안내하는가"이고, 이건 문장 내용 판단이라 단언으로 나오지 않는다.
- `interaction_flow_clarity`도 같다. 진행이 되는지와 사용자가 알 수 있는지는 다른 문제다.

환산 규칙: test가 판정하는 축은 실패 0개 = 5, 1개 = 3, 2개 이상 = 1.
기존 `counting_rule`과 같은 모양이지만 세는 주체가 실행기다.
`hard_gates`의 `required_interactions_reachable`, `no_blocking_runtime_errors`는 `functional_test`가 판정한다.

### 5.6 테스트가 대체하지 못하는 것

test가 들어오면 `content_eval`과 `content_refine`이 필요 없어지는가.
아니다. 다만 **역할이 좁아진다.** 테스트에는 두 가지 원리적 한계가 있다.

#### 한계 1 — 테스트는 planner를 검증하지 못한다

테스트가 planner에서 생성되기 때문이다.
planner가 학습적으로 나쁜 기획을 냈다면 — 문항이 학습 목표와 무관하거나 피드백 문구가 부실하다면 —
builder가 그것을 **충실하게 구현할수록 테스트는 전부 통과한다.**

spec 기반 검증의 본질적 한계이고, 테스트를 아무리 늘려도 사라지지 않는다.
따라서 planner 산출물을 학습 관점에서 볼 눈이 하류에 하나는 남아야 한다. 그게 `content_eval`이다.

#### 한계 2 — 테스트는 고치지 않는다

테스트는 실패를 알려줄 뿐이다. 수리는 여전히 LLM의 일이다.
`content_refine`은 없어지기는커녕 **더 잘 작동하게 된다.** 입력이 바뀌기 때문이다.

```text
전:  "피드백이 약해 보입니다"                          (모호한 산문)
후:  case_q3_wrong: [data-qa-feedback="wrong"] not visible  (사실)
```

#### 각 stage에 남는 역할

| stage | 변경 |
|---|---|
| `functional_test` | 신설. 기능·충실도 게이트를 가져간다 |
| `content_eval` | **5축 → 3축.** 역할이 "품질 게이트"에서 "학습 품질 하한선"으로 좁아진다 |
| `content_critique` | **5축 → 3축.** 기능·충실도 지적은 test_report와 중복이므로 뺀다 |
| `content_refine` | 유지. 입력에 `test_report.failures`가 추가된다 |

`content_critique`가 가장 없애기 쉬워 보인다. `priority_issues[].suggested_fix`가 test_report의 구체 실패와 겹치기 때문이다.
**그래도 없애지 않는다.** 없애면 `content_refine`이 방향을 얻을 곳이 `content_eval`밖에 남지 않고,
그러면 refine이 점수와 rationale을 보게 되어 **"refine에 점수를 넘기지 않는다"** 원칙이 깨진다.
critique는 refine에게 점수 없이 방향을 주는 유일한 통로다.

---

## 6. Part 2 — design system 획일화

### 6.1 토큰 층 구조

```text
층 1  구조 토큰   source/common/components/_shared/base.css   ← SSOT, 콘텐츠 무관 고정
층 2  팔레트     source/[teacher]/tokens.css                  ← 선생님별
층 3  콘텐츠     planner art_direction                        ← teacher 없을 때만
```

- **층 1은 값이 고정이다.** 타이포 사다리, z-index, 모서리, 모션, 그림자.
- **층 2가 있으면 층 3을 무시한다.** 선생님 팔레트가 콘텐츠 분위기보다 우선한다.
- **층 2가 없으면 층 3이 채운다.** 지금 동작과 같다.

### 6.2 값 충돌 해결

`--fs-sm`이 31px(contract)과 37px(base.css)로 갈린다.
**base.css(37px)를 기준으로 통일한다.**

근거: `source/common/components/`의 CSS 6개가 이미 그 사다리 위에서 실측·조정됐고,
`production/1-2/08`이라는 실제 합격 산출물에서 나온 값이다.
contract의 31px은 어느 산출물에서 검증된 값인지 추적할 수 없다.

같은 이유로 z-index도 base.css 쪽을 쓴다. contract에만 있는 `--z-flash:90`은 base.css로 옮긴다.

이 변경은 **기존 run의 시각적 결과를 바꾼다.** 다음 콘텐츠부터 적용하고 기존 run은 건드리지 않는다.

### 6.3 `design_system` 해석 단계

runner 안의 **결정적 단계**다. LLM stage가 아니다.

- 입력: `input.metadata.teacher`(선택), `planner.art_direction`, `source/`
- 출력: `runs/{run_id}/design_system/tokens.css`, `components/`, `design_system.json`

동작:

1. `source/common/components/_shared/base.css`에서 구조 토큰을 읽는다.
2. teacher가 있으면 `source/[teacher]/tokens.css`의 팔레트로 덮어쓴다.
3. 없으면 `art_direction`에서 팔레트 값을 채운다.
4. 이번 콘텐츠에 쓸 컴포넌트를 골라 `components/`로 복사한다.
5. builder/refine 프롬프트에 **경로와 함께 원문을 실어 준다.**

builder에게는 이렇게 준다.

```text
DESIGN_SYSTEM_TOKENS_CSS   (그대로 <style> 맨 앞에 inline한다. 값을 바꾸지 않는다)
DESIGN_SYSTEM_COMPONENTS   (template.html / style.css / behavior.js 원문)
```

`common_html_contract.md`의 `:root` CSS 블록은 **삭제하고** "주입된 토큰을 그대로 쓴다"는 규칙만 남긴다.
CSS가 md 문자열로 갇혀 있는 상태를 끝낸다.

### 6.4 컴포넌트 선택

어떤 컴포넌트를 실을지는 planner가 정한다.
`interactions[].type`과 `questions[].input_type`으로 매핑한다.

| planner 신호 | 주입 컴포넌트 |
|---|---|
| 항상 | `scene-controller`, `debug-jumper` |
| `elements[].channel == "dialogue"` 또는 `"feedback"` | `speech-bubble` |
| `channel == "feedback"` | `feedback-layer` |
| `input_type == "keypad"` | `keypad` |
| CTA가 있는 section | `ticket-button` |

매핑은 runner의 결정적 규칙이다. LLM이 고르게 하지 않는다.

이 결정이 5장과 맞물린다. 공용 컴포넌트가 hook을 **이미 갖고 있으면** builder가 hook을 빠뜨릴 여지가 줄어든다.
따라서 `source/common/components/`의 template에 `data-qa-*`를 미리 넣어 둔다.

---

## 7. Part 3 — teacher source

### 7.1 구조

`reusable-source-design.md` 4장의 구조를 따르되 토큰 파일을 추가한다.

```text
source/[teacher]/
  CLAUDE.md
  tokens.css          ← 신설. 팔레트 토큰만
  characters.md
  assets.md
  style.md
  assets/
    characters/ backgrounds/ props/ ui/ cta/
```

`tokens.css`는 **팔레트만** 담는다. 구조 토큰을 재정의하면 획일화가 깨진다.

```css
/* source/teacher-a/tokens.css */
:root {
  --bg: #49b9ed;
  --surface: #1f73c9;
  --ink: #153f6b;
  --accent: #ffd84d;
  --cream: #fff8df;
  --danger: #e65043;   /* 역할 고정: 오답 신호는 빨강 계열 유지 */
}
```

### 7.2 input 연결

`input.metadata`에 `teacher`를 추가한다. `metadata`는 `additionalProperties: true`라 schema 변경 없이 들어간다.

```json
{
  "metadata": {
    "teacher": "teacher-a"
  }
}
```

runner가 `source/teacher-a/`를 찾아 `tokens.css`와 `style_reference_set`을 자동 구성한다.
기존 `metadata.style_reference_set`을 직접 쓰는 경로도 유지한다. 둘 다 있으면 명시적으로 쓴 쪽이 이긴다.

### 7.3 teacher가 없을 때

**자동 생성하지 않는다.**

- `metadata.teacher`가 없으면 common만 쓴다. 지금 동작과 같다.
- `metadata.teacher`가 있는데 디렉토리가 없으면 **에러로 멈춘다.** 오타를 조용히 삼키면 안 된다.
- 새 teacher를 만드는 것은 별도 명령이다.

```bash
python -B ./runner.py --bootstrap-teacher teacher-b --from-run 2026-07-31_dfbc1027
```

이 명령은 run 산출물에서 팔레트를 추출해 `source/teacher-b/`의 뼈대와 `Status: candidate`를 만든다.
**사람이 검토하고 승격한다.** 선생님 정체성은 자동 판단 대상이 아니고,
이건 `reusable-source-design.md` 10.1의 운영 절차와 같은 규칙이다.

---

## 8. 정보 차단 규칙 갱신

`CLAUDE.md`의 표에 두 줄을 추가하고 한 줄을 고친다.

| 단계 | 봐도 되는 것 | 보면 안 되는 것 |
|---|---|---|
| **test_spec** | planner | **HTML, builder, asset, 모든 review/eval** |
| **functional_test** | test_spec, HTML | planner 원문, LLM 산출물 전부 |
| Content Refine | 기존 + **test_report.failures** | content_eval 총점 |

`test_spec`의 차단이 이 설계에서 가장 중요한 한 줄이다.

---

## 9. 구현 순서

각 단계가 **단독으로 가치가 있고 되돌릴 수 있게** 자른다.

| 단계 | 내용 | 완료 판정 |
|---|---|---|
| 1 | DOM hook 계약을 `common_html_contract.md`에 추가 | 새 run의 HTML에 `data-qa-question`이 나온다 |
| 2 | `functional_test` stage + `--functional-test-only` 플래그 | 기존 run에 대해 리포트가 나온다 (게이트 아님) |
| 3 | `test_spec` stage + schema | planner에서 spec이 나오고 사람이 읽어 납득된다 |
| 4 | 루프 연결, FAIL 시 LLM 리뷰 스킵 | 실패가 게이트를 막는다 |
| 5 | rubric 축 재배치. eval·critique를 3축으로 축소 | eval이 fidelity·functional을 스스로 판단하지 않는다 |
| 6 | 토큰 값 통일(37px 기준), `design_system` 해석 단계 | contract의 `:root` 블록이 사라진다 |
| 7 | 컴포넌트 주입 + template에 hook 반영 | builder가 공용 컴포넌트를 쓴다 |
| 8 | `source/[teacher]/tokens.css` + `metadata.teacher` | 같은 planner로 팔레트만 다른 결과가 나온다 |
| 9 | `--bootstrap-teacher` | run에서 teacher 뼈대가 나온다 |

1~2단계는 게이트를 켜지 않고 **관찰만** 한다.
실패율을 보고 hook 계약이 현실적인지 판단한 뒤 4단계에서 켠다.

---

## 10. 리스크

| 리스크 | 대응 |
|---|---|
| 초기 hook 누락으로 게이트가 계속 막힌다 | 1~2단계에서 게이트를 끄고 실패율만 관찰한다 |
| `test_spec`이 planner만 보고 실행 불가능한 case를 만든다 | `action`/`expect`를 닫힌 enum으로 제한한다 |
| `design_refine`의 통짜 재작성이 hook을 날린다 | contract의 보존 조항에 `data-qa-*`를 명시하고, 다음 iteration의 `functional_test`가 잡는다 |
| 토큰 통일이 기존 산출물 톤을 바꾼다 | 기존 run은 마이그레이션하지 않는다. 다음 콘텐츠부터 적용한다 |
| playwright 미설치 환경에서 파이프라인이 멈춘다 | `functional_test`는 브라우저가 없으면 ERROR로 명확히 실패한다. 조용히 PASS하지 않는다 |
| stage가 2개 늘어 run 시간이 길어진다 | `test_spec`은 run당 1회, `functional_test`는 LLM이 없어 빠르다. FAIL 시 LLM 3개를 스킵하므로 총 시간은 오히려 줄 수 있다 |

---

## 11. 미결

- `test_spec`을 매 run 새로 만들 것인가, 같은 planner면 캐시할 것인가.
- `drag_drop`의 실행 방식. playwright `drag_to`가 커스텀 포인터 구현에서 동작하는지 실측이 필요하다.
- `data-qa-choice`를 index로 둘 때, 보기 순서를 섞는 구현에서 안정적인지.
- teacher 팔레트와 생성 asset 색의 일치를 누가 보증하는가. 지금은 `art_direction`이 asset과 CSS의 공통 출처인데, teacher가 팔레트를 덮으면 asset은 여전히 `art_direction`을 따른다.

마지막 항목이 가장 큰 구멍이다. 8단계 전에 결정해야 한다.
