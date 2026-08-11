# content-harness-pipeline

이 문서는 `content-harness-pipeline` 안에서 AI 에이전트가 작업할 때 따라야 하는 프로젝트 규칙이다.

이 파이프라인의 산출물은 **학습 콘텐츠 HTML 한 편**이다.
스토리보드 markdown을 입력으로 받아, 기획 → asset 생성 → HTML 빌드 → 품질 루프를 거쳐
`runs/{run_id}/output/index.html` 단일 파일과 `output/assets/`를 만든다.

2차 산출물은 그 HTML이 만들어진 과정을 재현하고 개선할 수 있는 **반복 가능한 생성 시스템**이다.

## 기본 원칙

- 구현 전 `docs/실행.md`, `schemas/*.schema.json`, `prompts/*_system.md`를 먼저 확인한다.
- 기존 파일 계약, 파일명 규칙, run 디렉토리 구조를 우선한다.
- 단계별 역할을 섞지 않는다.
- LLM stage 사이의 핸드오프는 파일과 JSON payload로만 한다.
- runner가 경로, 파일명, payload 구성을 제어한다.
- stage 코드나 프롬프트가 임의로 run 디렉토리 전체를 훑어 읽게 만들지 않는다.
- 검증 가능한 형태로 마무리한다. 코드 변경 후 가능한 경우 `python runner.py ...` 또는 `python validate.py ...` 계열 검증을 실행한다.

## 실행 명령어

명령어는 `content-harness-pipeline` 디렉토리에서 실행한다.

```bash
cd content-harness-pipeline
python -m pip install -r ./requirement.txt
```

`requirement.txt`는 `jsonschema`와 `playwright`를 요구한다.
`playwright`는 design review가 쓰는 스크린샷 캡처(`stages/visual_qa.py`)에 필요하다.
브라우저 바이너리는 별도로 받아야 한다.

```bash
python -m playwright install chromium
```

입력 JSON만 검증할 때:

```bash
python -B ./validate.py ./input.json --artifact input
```

전체 파이프라인을 실행할 때:

```bash
python -B ./runner.py ./input.json
```

같은 run_id 산출물을 의도적으로 다시 만들 때만 `--overwrite`를 붙인다.

```bash
python -B ./runner.py ./input.json --overwrite
```

비용 문제로 HTML을 다루는 무거운 stage(builder / design_refine / content_refine)만 Claude로 돌릴 수 있다.

```bash
python -B ./runner.py ./input.json --overwrite --claude-html-stages --claude-model sonnet
```

중간 단계부터 이어서 돌릴 때는 `--run-id`로 기존 run을 지정하고 `--start-at`을 쓴다.

```bash
python -B ./runner.py ./input.json --run-id 2026-07-31_dfbc1027 --start-at builder --overwrite
```

단일 stage만 돌리는 플래그는 서로 함께 쓸 수 없다.

```text
--planner-only  --asset-generator-only  --builder-only
--design-review-only  --design-refine-only
--content-critique-only  --content-eval-only
```

더 많은 실행 예시는 `docs/실행.md`에 있다.

Python 문법만 빠르게 확인할 때는 `__pycache__`가 생기지 않도록 `py_compile` 대신 `compile(...)` 기반 명령을 사용한다.

```bash
python -B -c "from pathlib import Path; files=['runner.py','validate.py','stages/builder.py','stages/design_review.py']; [compile(Path(f).read_text(encoding='utf-8'), f, 'exec') for f in files]; print('syntax ok')"
```

## 파이프라인 흐름

```text
input validate
      ↓
planner            → {brief_hash}_planner.json
      ↓
asset_generator    → {brief_hash}_asset_generator.json + output/assets/
      ↓
builder            → {brief_hash}_builder.json + output/index.html
      ↓
품질 루프 (최대 --content-max-iterations, 기본 5)
```

품질 루프 한 iteration은 다음을 돈다.

```text
design_review (visual_qa 스크린샷 포함) ┐
content_critique                       ├ 세 산출물을 만든다
content_eval                           ┘
      ↓
asset 변경 요청 있음 → asset revision → design_refine
design_review REJECT → design_refine
content_eval REJECT  → content_refine   (design_refine 뒤에 순차)
```

### 두 축은 독립이다

design 축의 게이트는 `design_review`, content 축의 게이트는 `content_eval`이다.
각 축은 **자기 게이트에만 반응한다.**

과거에는 이 둘이 `if/elif/else` 한 줄로 묶여 있어 `content_refine`이 "design_review가 PASS일 때만"
도달하는 3순위 분기였다. 그 결과 design이 REJECT인 동안 `content_refine`이 한 번도 실행되지 않고
`content_critique`는 매 iteration 생성만 되고 아무도 읽지 않았다(run `ch8c0716`, `ch8c0717`).
이 구조를 다시 하나로 합치지 않는다.

### 순서에도 이유가 있다

`content_refine`은 항상 `design_refine` **뒤**에 돈다.
`content_refine`은 CSS·레이아웃을 건드리지 않는 보수적인 stage이고,
`design_refine`은 HTML을 통째로 다시 쓴다. 순서를 뒤집으면 design_refine이 content 수정을 지운다.

### PASS 조건

`design_review`가 PASS이고, `content_eval`이 PASS이고, **asset 변경 요청이 없어야** 한다.
셋 중 하나라도 아니면 다음 iteration으로 간다.
`--content-max-iterations`를 소진하면 REJECT로 끝난다.

asset 재생성·신규 요청은 `design_review`만 낸다.
`content_critique_output.schema.json`에는 `asset_review`가 없고 `additionalProperties`도 막혀 있다.

## run 디렉토리 구조

`run_id`는 `YYYY-MM-DD_{brief_hash}` 형식이다.

```text
runs/2026-07-31_dfbc1027/
  dfbc1027_input.json
  dfbc1027_planner.json
  dfbc1027_asset_generator.json
  dfbc1027_builder.json

  iter_001/
    dfbc1027_iter-001_design_review.json
    dfbc1027_iter-001_content_critique.json
    dfbc1027_iter-001_content_eval.json
    design_review/            # visual_qa 스크린샷
    design_refine_preview/
    content_refine_preview/

  output/
    index.html                # 최종 산출물
    assets/
```

`output/index.html`은 단일 파일 계약을 따른다. 상세는 `prompts/common_html_contract.md`.

## 역할 경계

### Planner

- 입력: `{brief_hash}_input.json`, `md_path`가 가리키는 스토리보드 원문
- 출력: `{brief_hash}_planner.json`
- 책임: 화면 구성, scene/interaction 설계, 캐릭터 엔티티, asset_plan을 만든다.
- 금지: HTML 작성, 자기 평가, 최종 판정.

### Asset Generator

- 입력: input, planner
- 출력: `{brief_hash}_asset_generator.json`, `output/assets/*`
- 책임: `asset_plan`에 따라 이미지 asset을 생성한다.
- 금지: HTML 작성, planner 설계 변경.

### Builder

- 입력: input, planner, asset_generator
- 출력: `{brief_hash}_builder.json`, `output/index.html`
- 책임: 단일 HTML을 만든다.
- 금지: 자기 평가, 점수 생성, asset 재생성.

### Design Review

- 입력: input, planner, asset_generator, builder, `output/index.html`, **visual_qa 스크린샷 이미지**
- 출력: `{brief_hash}_iter-{iteration}_design_review.json`
- 책임: 시각 품질을 판정하고 우선순위 findings와 asset 재생성/신규 요청을 낸다.
- 금지: HTML 직접 수정, content 축 판정.
- design review는 HTML 텍스트만 읽지 않는다. `stages/visual_qa.py`가 먼저 스크린샷을 찍고 그 이미지를 입력으로 받는다.

### Content Critique

- 입력: input, planner, asset_generator, builder, HTML
- 출력: `{brief_hash}_iter-{iteration}_content_critique.json`
- 책임: 학습 흐름과 콘텐츠가 약한 지점, 다음 수정 방향을 제시한다.
- 금지: 점수표 생성, HTML 재작성, 최종 판정, asset 요청.

### Content Eval

- 입력: planner, asset_generator, builder, HTML, `content_rubric.yaml`
- 출력: `{brief_hash}_iter-{iteration}_content_eval.json`
- 책임: 루브릭 기반 점수와 축별 근거를 낸다.
- 금지: critique를 읽고 채점하기, HTML 재작성.
- **input을 받지 않는다.** `input.json`에는 스토리보드 본문이 없고 `md_path` 경로 문자열만 있다.
  평가에 필요한 스펙은 planner 출력에서 온다.

### Design Refine

- 입력: input, planner, asset_generator, builder, HTML, design_review
- 출력: 갱신된 `output/index.html`
- 책임: design review findings를 HTML에 반영한다.
- 금지: content_eval 점수 맞추기.

### Content Refine

- 입력: input, planner, asset_generator, builder, HTML, content_critique
- 출력: 갱신된 `output/index.html`
- 책임: content critique를 HTML에 반영한다.
- 금지: CSS·레이아웃 통짜 재작성, eval 총점 원문 참조.

### Visual QA

- 입력: `output/index.html`
- 출력: 스크린샷과 `visual_qa_output.schema.json` 형태의 요약
- 책임: playwright로 화면을 캡처해 design review에 이미지 근거를 제공한다.
- design review 안에서 자동 실행된다. 단독으로 돌리려면 `capture_visual_qa.py`를 쓴다.

### Validator

- 입력: 검사 대상 JSON, 해당 schema, 기계적 계약, 필요한 rubric threshold
- 출력: PASS/REJECT/ERROR 성격의 검사 결과
- 책임: schema, `brief_hash`, 필수 조건, 점수 하한처럼 기계적으로 판정 가능한 항목만 검사한다.
- 금지: 시각 품질 판단, 창작, 비평, 점수 근거 작성.

## 정보 차단 규칙

단계별로 허용된 입력만 payload로 전달한다.
아래 표는 `stages/*.py`의 실제 함수 시그니처와 일치해야 한다. 시그니처를 바꾸면 이 표도 함께 고친다.

| 단계 | 봐도 되는 것 | 보면 안 되는 것 |
| --- | --- | --- |
| Planner | input, 스토리보드 md 원문 | 이후 모든 산출물 |
| Asset Generator | input, planner | builder, review, eval |
| Builder | input, planner, asset_generator | review, critique, eval |
| Design Review | input, planner, asset, builder, HTML, 스크린샷 | content_critique, content_eval |
| Content Critique | input, planner, asset, builder, HTML | content_eval, design_review |
| Content Eval | planner, asset, builder, HTML, content_rubric | **input**, content_critique, design_review |
| Design Refine | input, planner, asset, builder, HTML, design_review | content_eval 총점 |
| Content Refine | input, planner, asset, builder, HTML, content_critique | **content_eval 총점** |
| Validate | 검사 대상 JSON, schema | LLM 대화 히스토리 |

핵심은 두 가지다.

- **Eval은 Critique에 anchor되지 않는다.** `content_eval`은 critique 파일 경로를 아예 받지 않는다.
- **Refine은 점수를 보지 않는다.** `content_refine`은 critique만 받는다. 점수를 보면 점수 맞추기가 시작된다.

## 프롬프트와 schema 규칙

- 역할별 system prompt를 섞지 않는다. `prompts/{stage}_system.md`는 그 stage 지시만 담는다.
- 프롬프트를 바꿀 때는 어떤 schema 출력과 연결되는지 함께 확인한다.
- 모든 stage가 공유하는 HTML 계약은 `prompts/common_html_contract.md` 한 곳에만 둔다.
- schema를 우회하기 위해 임의 필드를 top-level에 추가하지 않는다.

Codex structured output schema 제약은 최상단 `CLAUDE.md`의 "문제사항과 교훈"을 따른다.
요약하면 object의 `properties`에 있는 모든 필드는 `required`에 포함해야 하고,
새 output schema를 만들면 실제 `codex exec --output-schema` 경로까지 한 번 검증한다.

## 실패와 검증 결과

- 성공한 validate 결과는 기본적으로 별도 파일로 남기지 않는다.
- 실패한 validate 결과만 원인 분석을 위해 `*.validation.json`으로 저장한다.
- `REJECT`는 파일은 생성됐지만 schema, 계약, 품질 하한, 필수 조건을 통과하지 못한 상태다.
- `ERROR`는 stage 실행, 파일 읽기/쓰기, JSON 파싱, schema/rubric 로딩 등 파이프라인 자체가 진행하지 못한 상태다.
- validate 호출은 검사 대상 파일을 직접 수정하지 않는다.
- HTML 전문을 다루는 stage는 다른 stage보다 오래 걸린다.
  `design_refine`과 `design_review`는 전역 `--timeout-seconds`와 별도로 더 큰 기본 timeout을 가진다.
  무거운 stage를 추가할 때 전역 timeout에만 의존하지 않는다.

## 금지 행동

- LLM stage가 허용되지 않은 파일을 임의로 읽게 하지 않는다.
- Builder가 `self_score`, `verdict` 같은 자기 판정을 만들게 하지 않는다.
- Content Critique가 점수표나 asset 요청을 만들게 하지 않는다.
- Content Eval이 critique를 읽거나 input 원문을 받게 하지 않는다.
- Refine stage에 eval 총점 원문을 넘기지 않는다.
- design 축과 content 축의 게이트를 하나로 합치지 않는다.
- `content_refine`을 `design_refine`보다 먼저 돌리지 않는다.
- Validator가 시각 품질을 주관적으로 판단하게 하지 않는다.
- 동일 run artifact를 사용자 의도 없이 덮어쓰지 않는다. 재실행 덮어쓰기는 명시적 `--overwrite`가 있을 때만 허용한다.

## 재사용 source

반복해서 쓰는 컴포넌트와 asset은 `source/` 아래에 둔다.
설계는 `docs/reusable-source-design.md`를 따르고, 각 축의 사용 규칙은 그 디렉토리의 `CLAUDE.md`에 있다.

스캔 모듈이 **항상 싣는 규칙 블록**과 **선택용 manifest**를 만들어 프롬프트에 붙인다. 두 축이 같은 패턴이다.

| 축 | 모듈 | 블록 | 붙는 stage |
|---|---|---|---|
| 컴포넌트 | `stages/scripts/common_components.py` | `COMMON_BASE_CSS` + `COMMON_COMPONENTS_JSON` | `builder`, `design_refine`, `content_refine` |
| craft example | `stages/scripts/craft_examples.py` | `CRAFT_EXAMPLES_RULES` + `CRAFT_EXAMPLES_JSON` | `asset_generator` |
| teacher 화풍 | `stages/scripts/teacher_source.py` | `STYLE_REFERENCE_SET_JSON` | `planner`, `asset_generator` |

- **목록을 프롬프트에도 input에도 손으로 적지 않는다.** 손으로 적으면 항목이 늘 때 사본과 디렉토리가 어긋난다.
  새 컴포넌트·새 예시·새 화풍 참조는 디렉토리에 넣기만 하면 되고, 프롬프트와 input은 고치지 않는다.
- teacher 축만 입구가 다르다. 프롬프트가 아니라 **`input.json`의 `metadata.style_reference_set`** 이 어느 선생님을
  쓸지 고르고, `categories`를 생략하면 `root`의 md catalog를 스캔해 채운다.
  항목별 `use`·`avoid`는 **`source/[teacher]/*.md`가 소유한다.** input에 다시 적지 않는다.
- **이름이 같으면 teacher가 common을 덮는다.** 세부가 일반을 이긴다.
  `source/[teacher]/components/keypad/`가 있으면 `source/common/components/keypad/`는 무시된다.
  **병합이 아니라 통째 교체다** — 섞으면 teacher가 일부러 뺀 규칙이 common에서 되살아난다.
  판정은 `stages/scripts/source_resolve.py`의 `shadowed_dirs()`가 하고 컴포넌트·craft example 축이 함께 쓴다.
- **공용 컴포넌트는 이미지를 소유하지 않는다.** 버튼 몸체·도장 art는 콘텐츠마다 세계관이 달라 재사용 대상이 아니다.
  `source/`의 어떤 파일도 `output/assets/`로 복사하지 않으며, art가 필요한 컴포넌트는 그 run이 생성한
  asset 경로를 밖에서 받는다(`ticket-button`은 `--cta-body`, `feedback-layer`는 `data-*-src`).
  이 규칙을 어기면 다른 차시의 팔레트가 화면에 섞이고, teacher/common 우선순위 판정도 무너진다.
- 규칙 블록에는 **어긋나면 그 뒤 모든 판단이 함께 흔들리는 것**만 통째로 싣는다.
  컴포넌트는 `:root` 토큰, craft example은 우선순위 규칙이 그렇다.
  개별 항목의 상세 계약은 stage가 고른 뒤 `component.md` / `example.md`를 직접 열어 읽는다.
- **컴포넌트 CSS·JS는 모델이 옮겨 적지 않는다.** `stages/scripts/component_bundle.py`의 `emit_common()`이
  `output/common.css` · `output/common.js`를 원본에서 만들고, 모델은 `index.html`에 `<link>`·`<script src>`
  두 줄만 유지한다. HTML을 쓰는 세 stage 뒤에서 `runner.finalize_html_artifact()`가 매번 다시 쓴다.
  - **되돌릴 수 있는 것은 되돌리고, 되돌릴 수 없는 것만 검증한다.** `common.*`는 코드 소유라 덮어쓰면 그만이고,
    `index.html`은 모델 소유라 되돌릴 수 없으므로 두 줄의 존재와 순서를 검증해 REJECT한다.
  - drift는 **로그이지 게이트가 아니다.** 게이트로 만들면 정당한 오버라이드 시도까지 run을 죽인다.
    같은 항목이 반복되면 모델이 틀린 게 아니라 컴포넌트가 부족하다는 신호로 읽는다.
  - 보장하는 것은 "결과가 동일하다"가 아니라 **"컴포넌트 원본이 항상 온전히 그 자리에 있다"** 이다.
    콘텐츠는 `<link>` 뒤 `<style>`에서 소스 순서로 오버라이드할 수 있고, 그건 막지 않는다.
- 디자인 토큰의 원본은 `_shared/base.css` **한 곳**이다. 프롬프트의 `COMMON_BASE_CSS`는 **어떤 토큰이 있는지
  알려주는 참고용**이지 옮겨 적을 원본이 아니다. `prompts/common_html_contract.md`에 값을 다시 적지 않는다.
- 컴포넌트 사용 규칙(선택 기준, inline 순서, 계약 보존)은 `common_html_contract.md`의 "공용 컴포넌트 재사용" 한 곳에만 둔다.
- **HTML을 다시 쓰는 stage가 `c-` prefix·`data-slot`·`window.Common*`를 바꾸지 않게 하는 조항을 지운다면 이 연결은 무의미해진다.** design_refine은 HTML을 통째로 재작성하므로 그 조항이 없으면 컴포넌트가 한 iteration 만에 풀어헤쳐진다.
- **craft example은 참조와 결과의 관계가 나머지 축과 반대다.** 컴포넌트와 화풍 참조는 그대로 가져오는 것이 정답이지만,
  craft example은 완성도만 가져오고 색·모티프·세계관은 그 run의 `art_direction`을 따라 새로 그려야 한다.
  `art_direction`이 예시를 이긴다는 조항을 지우면 모델이 예시를 복제해 run마다 정한 화풍을 덮어쓴다.

## 삭제된 글쓰기 파이프라인 잔재 (2026-08-11)

글쓰기 파이프라인에서 넘어와 실행되지 않던 코드를 지웠다. 다음 경로는 **이제 없다.**

- `runner.py`의 `run_writing_loop()`와 그 전용 헬퍼
  (`build_draft`/`build_critique`/`build_eval`/`build_refine_request`/`build_final`,
  `get_weak_axes`, `get_refine_contract_errors`, `format_eval_scores`,
  `write_max_iteration_failed`, `categorize_failure`, `failure_rule`)
- `RunContext`의 `draft_path`·`critique_path`·`eval_path`·`final_path`·`failed_path` 계열 속성
- `--gen-model`, `--critique-model`, `--eval-model`, `--refine-model`, `--rubric` 인자와 `rubric.yaml`
- `stages/generator.py`, `stages/critique.py`, `stages/evaluator.py`, `stages/refine.py`
- `prompts/gen_system.md`, `critique_system.md`, `eval_system.md`, `refine_system.md`
- `schemas/draft`, `critique`, `eval`, `final`, `gen_output`, `critique_output`, `eval_output`
- `validate.py`의 같은 이름 artifact와 `validate_draft_contract` 계열 검증기,
  그리고 그 검증기 전용이던 `--brief-hash`·`--iteration` 인자

`content_rubric.yaml`과 `content_critique`/`content_eval` 계열은 **현재 파이프라인의 일부다.** 이름이 비슷하다고 함께 지우지 않는다.
과거 run 산출물에서 이 이름을 보더라도 되살리지 않는다.
