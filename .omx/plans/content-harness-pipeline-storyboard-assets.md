# content-harness-pipeline 전환 계획

## Requirements Summary

`content-harness-pipeline`은 현재 `writing-harness-pipeline`의 복사본에 가깝다. 현재 계약은 단일 글 초안(`content`)을 생성, 비평, 평가, 퇴고하는 구조다.

새 목표는 story board 입력을 바탕으로 단일 HTML과 이미지 asset을 run 디렉토리의 `output/` 아래에 생성하는 것이다. 따라서 파이프라인의 중심 산출물은 "개선된 초안"이 아니라 "재현 가능한 단일 페이지 콘텐츠 run"이 되어야 한다.

현재 근거:

- `docs/readme.md`는 여전히 `Writing Harness Pipeline`이고 1차 산출물을 개선된 초안으로 정의한다.
- `schemas/gen_output.schema.json`은 `content` 문자열 하나만 요구한다.
- `schemas/draft.schema.json`과 `schemas/final.schema.json`도 `content` 중심 계약이다.
- `runner.py`의 `build_draft`와 `build_final`은 `stage_output["content"]`, `draft["content"]`를 그대로 감싼다.
- `rubric.yaml`은 `writing:v1`이고 `structure/evidence/sentence/originality` 축으로 글 품질을 평가한다.
- `steamup-input.json`은 이미 기획서와 HTML 프로토타입 산출물을 요구하지만, 현재 파이프라인은 이를 별도 artifact로 표현하지 못한다.

## Recommended Direction

기존 4단계 흐름은 유지하되 역할 이름과 artifact 계약을 바꾼다.

```text
story_board input
  -> planner: 화면, 섹션, 인터랙션, asset 생성 계획을 구조화
  -> asset_generator: planner의 asset plan을 바탕으로 assets/*와 asset manifest 생성
  -> builder: planner spec + asset manifest를 바탕으로 단일 index.html 생성
  -> critique: UX, 정보구조, 시각 일관성, asset 사용 적절성 검토
  -> eval: 계약, 접근성, 반응형, asset 참조, 브리프 충족 여부 채점
  -> refinePlanner: critique/eval/validation 결과를 바탕으로 다음 수정 액션 결정
```

`Generator/Critique/Evaluator/Refiner`라는 기존 추상 역할은 구현상 재사용할 수 있지만, prompt와 schema에서는 새 역할명을 쓰는 편이 낫다.

- `generator` -> `planner`, `asset_generator`, `builder`로 분리
- `critique` -> `reviewer`
- `eval` -> `qa`
- `refine` -> `refinePlanner`

초기 구현은 파일명을 크게 갈아엎지 않고 내부 계약부터 바꾸는 것이 좋다. runner 구조 재사용 이득이 크기 때문이다.

## Artifact Contracts

### input

`brief`를 글쓰기 요청이 아니라 콘텐츠 제작 요청으로 바꾼다.

필수 후보:

- `brief_hash`
- `created_at`
- `brief.title`
- `brief.goal`
- `brief.audience`
- `brief.story_board`
- `brief.output_targets`

`output_targets` 예시:

```json
{
  "documents": ["content_plan"],
  "html": {
    "id": "prototype",
    "path": "index.html"
  },
  "assets": {
    "strategy": "ai_decides",
    "policy": "AI may create any image assets useful for the storyboard. Every referenced asset must be listed in the manifest."
  }
}
```

### planner_output

planner는 story board를 해석해 단일 페이지 설계와 asset plan을 만든다. 여기서 asset은 입력에서 required로 받지 않고 planner가 판단한다.

```json
{
  "spec": {
    "summary": "...",
    "sections": [
      {
        "id": "hero",
        "purpose": "첫 화면에서 주제와 핵심 흐름을 전달",
        "content_outline": ["..."],
        "interactions": []
      }
    ],
    "interactions": [
      {
        "id": "filter_demo",
        "type": "tabs",
        "description": "콘텐츠 유형에 따라 필터가 바뀌는 흐름"
      }
    ],
    "asset_plan": [
      {
        "id": "hero_image",
        "intended_path": "output/assets/hero.png",
        "purpose": "서비스의 교육 플랫폼 톤을 첫 화면에서 전달",
        "usage": ["hero"]
      }
    ]
  }
}
```

### asset_generator_output

asset generator는 planner의 `asset_plan`을 보고 실제 이미지, placeholder, 또는 prompt 파일을 만든다.

```json
{
  "assets": [
    {
      "id": "hero_image",
      "path": "output/assets/hero.png",
      "status": "placeholder",
      "prompt_path": "output/assets/hero.prompt.md",
      "usage": ["hero"],
      "source_plan_id": "hero_image"
    }
  ]
}
```

### builder_output

`gen_output.schema.json`의 `{ "content": "..." }`를 다음 형태로 교체한다.

```json
{
  "build": {
    "summary": "...",
    "files": [
      {
        "path": "output/index.html",
        "kind": "html",
        "content": "<!doctype html>..."
      },
      {
        "path": "output/assets/hero.prompt.md",
        "kind": "asset_prompt",
        "content": "..."
      }
    ],
    "asset_manifest_path": "asset_manifest.json"
  }
}
```

초기 MVP에서는 실제 이미지 생성을 외부 API까지 붙이지 않아도 된다. `asset_generator`가 placeholder 이미지 또는 prompt 파일을 생성하고, manifest에 상태를 기록하면 충분하다.

### build artifact

`draft.schema.json`은 `content` 대신 planner/asset/build 결과를 추적한다.

필수 후보:

- `brief_hash`
- `iteration`
- `stage`
- `spec`
- `asset_manifest`
- `build.files[]`
- `generated_at`
- `model`
- `metadata`

검증 규칙:

- HTML 파일은 정확히 1개이며 기본 경로는 `output/index.html`
- 모든 asset reference는 `asset_manifest.assets[].id` 또는 실제 파일 경로와 매칭
- `index.html`은 `<!doctype html>` 또는 full HTML 문서 형태
- 외부 CDN 사용 여부를 정책으로 명시
- 이미지 asset은 `planned`, `generated`, `placeholder`, `missing` 중 하나의 status

### final

별도 package 단계는 두지 않는다. `final.schema.json`은 run 디렉토리에 생성된 결과물을 다시 포장하지 않고, 통과한 run의 요약과 검증 스냅샷만 남긴다.

필수 후보:

- `brief_hash`
- `final_iteration`
- `entrypoint`
- `asset_manifest`
- `accepted_at`
- `quality_snapshot`
- `contract_result`
- `lineage`

`final.json` 예시:

```json
{
  "entrypoint": "output/index.html",
  "asset_manifest": "asset_manifest.json",
  "result_files": ["output/index.html", "asset_manifest.json", "output/assets/hero.png"]
}
```

## Rubric

`writing:v1`은 `content_prototype:v1`로 바꾼다.

권장 축:

- `brief_alignment`: story board와 요구 산출물을 얼마나 충실히 반영했는가
- `information_architecture`: 화면 흐름, 섹션 구조, 탐색 동선이 명확한가
- `visual_composition`: 레이아웃, 계층, 밀도, 색상, 반응형 구성이 적절한가
- `interaction_clarity`: 필터, 탭, CTA, 상태 변화가 이해 가능한가
- `asset_coherence`: AI가 선택한 이미지/시각 asset이 목적에 맞고 참조가 깨지지 않는가
- `implementation_integrity`: HTML/CSS/JS가 깨지지 않고 로컬에서 열 수 있는가

MVP threshold는 너무 높이지 않는다. 예:

```json
{
  "min_total": 3.4,
  "min_axis": {
    "brief_alignment": 3.0,
    "asset_coherence": 3.0,
    "implementation_integrity": 3.0
  }
}
```

## Implementation Steps

1. 문서와 명명 정리
   - `docs/readme.md`, `docs/schema-contracts.md`, `AGENTS.md`의 writing 용어를 content run 용어로 바꾼다.
   - `writing-harness-pipeline`을 가리키는 잔여 문구를 `content-harness-pipeline`으로 정리한다.

2. schema를 먼저 교체
   - `input.schema.json`: story board, output targets, asset policy 추가. 단, required asset 목록은 두지 않는다.
   - `planner_output.schema.json`: story board를 단일 페이지 spec과 asset plan으로 변환.
   - `asset_output.schema.json`: asset manifest와 생성 상태를 기록.
   - `builder_output.schema.json`: `content` 단일 필드에서 `build.files[]`로 변경.
   - `draft.schema.json`: `content` 대신 spec, asset_manifest, build artifact를 추적.
   - `final.schema.json`: final content 대신 run summary와 validation snapshot 기록.
   - `eval_output.schema.json`, `eval.schema.json`: 새 rubric 축으로 변경.

3. runner의 build/write 책임 확장
   - runner 흐름을 `planner -> asset_generator -> builder -> critique -> eval -> refinePlanner`로 재배치한다.
   - `builder` 결과의 `index.html`을 `runs/{run_id}/output/index.html`에 쓴다.
   - `asset_generator` 결과의 asset 파일과 `asset_manifest.json`을 `runs/{run_id}/output/assets/*`, `runs/{run_id}/asset_manifest.json`에 쓴다.
   - 경로 traversal 방지를 위해 모든 file path는 run directory 내부 상대 경로만 허용한다.

4. validate 확장
   - `validate.py`에 content run contract 검사를 추가한다.
   - 단일 HTML entrypoint 존재 여부, asset 참조 일치, 필수 output target 충족, 파일 경로 안전성, HTML 기본 구조를 검사한다.
   - asset 개수나 종류는 검증하지 않는다. 대신 HTML이 참조한 asset은 manifest에 있고, manifest의 asset path는 run directory 내부에 있어야 한다.
   - 이미지가 실제 생성되지 않은 MVP에서는 `status=planned|placeholder`를 PASS 가능 정책으로 둘지 결정한다.

5. prompt 교체
   - `gen_system.md`: 작가 역할에서 콘텐츠 프로토타입 제작자 역할로 변경.
   - `critique_system.md`: 편집자에서 UX/content reviewer로 변경.
   - `eval_system.md`: 글 평가자에서 QA evaluator로 변경.
   - `refine_system.md`: 퇴고자가 아니라 refine planner로 변경.

6. sample input과 golden run 추가
   - `steamup-input.json`을 새 input schema에 맞게 정리한다.
   - 최소 샘플은 단일 HTML 1개를 요구한다. asset은 AI가 필요하다고 판단하면 생성한다.
   - `python validate.py --artifact ...`와 runner dry run이 통과해야 한다.

## Acceptance Criteria

- `content-harness-pipeline` 문서에서 `Writing Harness Pipeline`과 `writing-harness-pipeline` 잔여 참조가 제거된다.
- generator 직접 출력은 더 이상 `{ "content": "..." }`만 허용하지 않는다.
- draft/final artifact는 HTML entrypoint와 asset manifest를 추적하되 별도 package artifact를 만들지 않는다.
- runner가 최종 PASS 시 `final.json` 외에 실제 `output/index.html` 파일을 run directory 안에 생성한다.
- validator가 깨진 HTML entrypoint, 참조와 manifest가 불일치한 asset, run directory 밖 경로를 REJECT한다.
- rubric 축이 글쓰기 품질이 아니라 콘텐츠 프로토타입 품질을 평가한다.

## Risks and Mitigations

- 리스크: HTML과 이미지 생성을 한 번에 붙이면 stage 책임이 커진다.
  - 완화: MVP는 HTML과 asset manifest/prompt까지 생성하고, 실제 이미지 생성은 다음 단계로 분리한다.

- 리스크: LLM이 임의 파일 경로를 만들 수 있다.
  - 완화: runner가 허용 확장자와 상대 경로만 쓰고, resolved path가 run directory 내부인지 검사한다.

- 리스크: 평가자가 디자인 취향만 평가할 수 있다.
  - 완화: rubric에 asset 목적 적합성, asset 참조 무결성, output target 충족, HTML entrypoint 같은 기준을 포함한다.

- 리스크: 기존 refine loop가 run artifact 전체를 매번 다시 쓰며 drift가 생긴다.
  - 완화: refine request에 `files_to_repair`, `assets_to_fix`, `contract_errors`를 명시한다.

## Verification Steps

- `python validate.py sample-input.json --artifact input`
- `python validate.py temp-gen-output.json --artifact gen_output`
- runner 실행 후 `runs/{run_id}/output/index.html`과 `runs/{run_id}/output/assets/*` 존재 확인
- final validation에서 HTML asset 참조와 manifest가 불일치하는 fixture가 REJECT되는지 확인
- 브라우저 또는 Playwright로 HTML entrypoint를 열어 console error와 비어 있는 화면 여부 확인

## Recommended MVP Scope

1차 MVP는 다음까지만 한다.

- story board JSON input
- 단일 `index.html` 생성
- AI가 선택한 asset manifest와 asset prompt 생성
- placeholder 이미지 파일 또는 planned asset 상태 기록
- run-level validation
- 콘텐츠 프로토타입 rubric 평가

실제 이미지 생성, Playwright screenshot 비교, asset 자동 삽입은 2차로 뺀다.
