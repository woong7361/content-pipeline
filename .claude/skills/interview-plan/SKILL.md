---
name: interview-plan
description: planner가 낸 계획(planner.json)을 화면 단위로 인터뷰해서 빈 자리를 채우고 planner가 승인 없이 정한 것을 확정한 뒤, 계획을 직접 편집하고 질문·답·편집 전후를 로그로 남긴다. "계획 인터뷰 해줘", "planner 결과 보고 채우자", "에셋 그림 내용 정하자" 같은 요청에 쓴다.
---

# 계획 인터뷰

`--planner-only`로 나온 계획을 받아 화면별로 인터뷰하고, **그 계획 파일을 직접 고친다.**

산출물은 셋이다.

```text
runs/<run_id>/<hash>_planner.json                # 편집 대상. 하류가 읽는 계약
runs/<run_id>/<hash>_planner_pre_interview.json  # 편집 전 사본. 회귀 검사의 기준
interviews/<hash>_<run_id>.jsonl                 # 질문·답·편집 전후. 자동화의 입력
```

**인터뷰 로그를 run 디렉토리에 두지 않는다.** 그 안의 파일은 하류 stage가 직접 열 수 있고, 로그에는
초안·기각된 안·판단 근거가 들어 있다. 하류가 그것을 읽으면 계획이 아니라 인터뷰에 anchor된다.
`CLAUDE.md`의 "run 디렉토리에는 파이프라인이 만든 산출물만 둔다"가 이 경우다.

## 왜 계획을 인터뷰하는가

스토리보드를 인터뷰하면 **계획에 무엇이 내려갔는지 모른 채** 묻게 된다. 계획을 인터뷰하면
하류가 실제로 읽을 값을 보고 묻는다. 그 자리에서 판단할 것이 두 종류다.

- **빈 자리** — planner가 규칙상 채우지 못한 것. `prompts/planner_system.md`가 스토리보드에 없는
  학습 내용·수치·보상 구조를 만들지 못하게 막으므로, 원문이 비워둔 구조는 계획에서도 비어 있다.
- **조용히 채워진 자리** — planner가 승인 없이 정한 것. 같은 규칙이 **시각 층은 덮지 않아서**
  에셋의 그림 내용과 화면 연출은 planner가 스스로 만들어 낸다. 그대로 그림이 되고 그대로 화면이 된다.

두 번째가 이 인터뷰가 존재하는 이유다. **결손 목록만 뽑으면 그 종류가 통째로 보이지 않는다.**
빈 자리와 채워진 자리를 같은 화면에 함께 놓는다.

스토리보드에 써두는 것으로는 이 자리에 닿지 못한다. 실측으로 확인된 것이다 — 원문이 정답 반응을
사건(효과음·글로우·점프)으로 적어둔 계획에서 네 문항의 `feedback.correct`가 모두 비어 있었다.
사건은 연출 요소로 내려갔고 **학습자가 읽을 문장은 아무 자리에도 없었다.**

## 순서

### 1. 계획을 전개도로 되돌린다

**묻기 전에 읽는다.** 전개도는 손으로 그리지 않는다. 계획에서 만든다.

```bash
cd content-harness-pipeline
python -B -m stages.scripts.plan_scene_view <planner.json>              # 화면 목록과 빈 자리 수
python -B -m stages.scripts.plan_scene_view <planner.json> <section_id> # 화면 하나 전개
```

목록으로 어디에 빈 자리가 몰려 있는지 보고, 그다음부터는 화면 하나씩 연다.

### 2. 여섯 축만 본다

각 축은 **하류가 실제로 판정하는 자리**와 짝이 맞는다. 이 밖은 묻지 않는다 — 하류가 안 보는 것을
채우면 계획만 길어지고 결과는 그대로다.

| 축 | 계획의 자리 | 하류에서 판정하는 곳 |
|---|---|---|
| 상호작용 | `questions[]`, `interactions[]` | content_eval 흐름 명확성 |
| 피드백 | `questions[].feedback.correct` / `.wrong` | content_eval 피드백의 질 |
| 화면 구성 | `elements[].channel`, `asset_plan[].composition_notes` | design_review |
| 전환 | `advance.interaction_id` / `.to_section_id` | content_eval 흐름 명확성 |
| 연출 | `staging_notes[]`, `elements[].reveal` | design_review `motion_review` |
| 그림 내용 | `asset_plan[].prompt_brief`, `visual_role`, `negative_prompt` | asset_generator가 그대로 그린다 |

**피드백 축은 사건이 아니라 문장을 받는다.** 효과음·글로우·점프는 연출 축이다. 이 축이 받아야 하는
것은 학습자가 읽을 문장이며, 그것이 없으면 정답만 공개하고 왜 그 답인지는 말하지 않는 화면이 된다.

**전환 축은 방법과 안내를 함께 받는다.** 자동으로 넘어간다고만 정하면 학습자는 다음에 뭘 할지 모른다.

**그림 내용 축은 계획 뒤에서만 물을 수 있다.** 에셋이 결정으로 존재해야 그 안에 무엇을 그릴지가
질문이 된다. 원문이 사물의 이름만 부른 자리는 planner가 그 사물의 재질·색·주변까지 혼자 정해두므로,
**전개도에 뜬 `그림` 줄은 비어 있지 않아도 승인 대상이다.**

### 3. 답이 하나로 정해지는 것은 묻지 않는다

인터뷰는 **사용자만 아는 정보**를 얻는 자리다. 판정은 하나다.

> 이 질문에 사용자가 아닌 다른 답을 할 수 있는가?

답이 하나뿐이면 질문이 아니다. 질문 수를 줄이는 게 목적이 아니라, 남은 질문이 전부 진짜가 되게
하는 것이 목적이다. 답이 하나로 정해지는 것은 두 곳에서 온다.

- **관례** — 조작하면 반응이 있다, 비활성 버튼은 눌리지 않는다 같은 것
- **공용 컴포넌트** — 선택된 컴포넌트가 이미 소유한 상태·애니메이션·전환

두 번째는 **스캔해서 확인한다.** 기억으로 적지 않는다 — 컴포넌트는 계속 늘어나고, 늘어날수록
물을 것이 줄어든다.

```bash
python -B -c "
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from pathlib import Path
for md in sorted(Path('source').glob('*/components/*/component.md')):
    css = md.parent / 'style.css'
    s = css.read_text(encoding='utf-8') if css.exists() else ''
    owns = []
    if ':hover' in s or ':active' in s: owns.append('hover/active')
    if '@keyframes' in s: owns.append('애니메이션')
    if 'data-transition' in s: owns.append('씬 전환')
    print(md.parent.name, '|', ', '.join(owns) or '-')"
```

여기 나온 것은 그 컴포넌트를 쓰는 한 자동으로 따라온다. 결손으로 세지 않는다. 다만 전개도에서
**조용히 지우지 않고 `(컴포넌트: 이름)`으로 표시한다.** 안 보이면 사용자는 그것을 고려했는지
빠뜨렸는지 구별할 수 없다.

### 4. 빈칸이 아니라 초안을 준다

인터뷰의 목적은 정보를 얻는 것이지 사용자에게 작문을 시키는 것이 아니다. "이 화면을 어떻게
채울까요?"는 인터뷰가 아니라 일 떠넘기기다. **결손마다 구체적인 초안을 먼저 쓰고, 사용자는
고치거나 승인한다.**

초안은 지어내지 않고 근거에서 끌어온다. 근거는 이 넷뿐이다.

- **같은 계획의 다른 화면** — 이미 채워진 화면의 조작 방식·피드백 형식을 이어간다
- **스토리보드 원문** — planner가 무엇을 근거로 그렇게 정했는지 대조한다
- **선택된 공용 컴포넌트** — 그것이 소유한 것 위에 얹는다
- **planner가 이미 정한 이웃 값** — 같은 에셋의 `visual_role`, 같은 화면의 `staging_notes`

근거를 못 찾은 축은 **초안 대신 그냥 묻는다.** 근거 없이 쓴 초안은 승인 한 번으로 계획에 들어가고,
계획은 하류의 계약이므로 아무도 그것을 다시 의심하지 않는다.

### 5. 화면 하나씩 진행한다

**여러 화면을 한 번에 처리하지 않는다.** 실측으로 확인된 것이다 — 화면을 묶어서 훑으면 앞쪽만
제대로 보고 뒤쪽은 satisficing으로 넘어간다. 전개도 하나를 다시 읽고, 그 화면만 다룬다.

전개도를 그대로 보여준 다음, `???`와 승인이 필요한 값마다 초안과 근거를 쓰고, 마지막에 답할 것을 모은다.

```markdown
## 이대로 갑니다 (근거가 계획 안에 있음)

- 전환 — 네 문항 뒤 자동 전환 (staging_notes가 이미 정함)

## 답할 것

① 피드백 문구 — 네 문항의 정답 문구가 비어 있습니다. 문항마다 왜 그 답인지 한 줄로 넣을까요?
   초안: "맞아요! 3시가 되기 5분 전이니까 2시 55분이에요."
   근거: 오답 문구가 이미 한 문장으로 통일돼 있습니다

② 그림 — 이 배경의 벽 색과 소품을 planner가 혼자 정했습니다. 이대로 갈까요?

그대로 좋으면 "다음"이라고만 하세요. 바꿀 것만 번호로 알려주세요.
```

- **근거가 계획 안에 있는 초안에는 번호를 붙이지 않는다.** 번호는 답해야 할 것의 표시다.
- **결손이 없는 화면에서는 멈추지 않는다.** 전개도만 보여주고 다음 화면으로 넘어간다.
- 승인된 답은 그때그때 기억해 두고, 파일은 아직 쓰지 않는다.

### 6. 완료 신호를 받으면 편집한다

사용자가 "완료", "끝", "이제 만들어" 같은 신호를 줄 때만 쓴다. 화면이 남았는데 쓰지 않는다.

**편집은 추가만 하는 연산이다.** 다시 쓰기가 아니다. 이 파이프라인은 같은 실패를 두 번 겪었다 —
HTML을 통째로 재작성하는 stage가 앞선 수정을 지워 순서를 고정해야 했고, 계획을 다시 쓰는 stage는
*"줄어든 것은 고친 것이 아니라 잃은 것으로 본다"* 는 조항과 회귀 검사를 붙여야 했다.

1. 편집 전 사본을 남긴다.

```bash
cp runs/<run_id>/<hash>_planner.json runs/<run_id>/<hash>_planner_pre_interview.json
```

2. 승인된 값만 해당 필드에 넣는다. **답을 받지 못한 필드는 건드리지 않는다.**
3. 화면이나 문항을 새로 추가할 때는 id를 새로 만들고, `advance` 사슬과 `interactions`,
   `asset_ids` ↔ `asset_plan`을 함께 잇는다. 기존 id를 바꾸지 않는다.

### 7. 기계로 검증한다. 통과할 때까지 넘기지 않는다

```bash
python -B -c "
import sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from stages.scripts.planner_check import check_planner, compare_planner, format_violations
before = json.load(open(sys.argv[1], encoding='utf-8'))
after = json.load(open(sys.argv[2], encoding='utf-8'))
print(format_violations(check_planner(after)))
losses = compare_planner(before, after)
print('회귀:', losses or '없음')
sys.exit(1 if losses else 0)
" runs/<run_id>/<hash>_planner_pre_interview.json runs/<run_id>/<hash>_planner.json
```

schema도 함께 통과해야 한다.

```bash
python -B validate.py --artifact planner_output runs/<run_id>/<hash>_planner.json
```

**하나라도 실패하면 사용자에게 넘기지 않는다.** 계획을 고쳐서 다시 돌린다. 실패를 보고하고
넘어가지 않는다 — 이 검증은 통과할 때까지 반복하라고 있는 것이다.

### 8. 로그를 남긴다

인터뷰를 그대로 남긴다. **이 로그가 자동화의 입력이다.** 그래서 대화가 아니라 **편집**을 기록한다 —
질문과 답만 남기면 무엇을 어떻게 고쳤는지가 사라져서 다음 차시에 재현할 수 없다.

`interviews/<hash>_<run_id>.jsonl`에 결정 하나당 한 줄을 쓴다.

```json
{"section_id":"...","axis":"피드백","kind":"빈자리","field":"sections[5].questions[0].feedback.correct","before":"","question":"정답 문구가 비어 있습니다","draft":"맞아요! ...","rationale":"오답 문구가 이미 통일돼 있음","answer":"승인","after":"맞아요! ..."}
```

- `kind`는 `빈자리`(planner가 못 채운 것)와 `무단결정`(planner가 승인 없이 정한 것) 둘뿐이다.
  이 둘의 비율이 planner를 어느 방향으로 고쳐야 하는지를 말해 준다.
- `before`와 `after`를 **둘 다** 남긴다. 이 쌍이 없으면 로그는 읽을거리일 뿐 학습 대상이 아니다.
- **승인만 하고 넘어간 것도 남긴다.** `answer`가 승인이고 `before`와 `after`가 같은 줄이 쌓이면
  그 질문은 물을 필요가 없었다는 뜻이고, 그것이 다음에 지울 질문이다.
- 기각된 초안도 `draft`에 그대로 남긴다. 무엇이 안 통했는지가 초안 규칙을 고치는 근거다.

### 9. 다음 명령을 알린다

계획은 이미 run 디렉토리에 있으므로 그 자리에서 이어 돈다. **input.json을 새로 만들지 않는다** —
계획을 고쳤을 뿐 요청은 그대로다.

```markdown
- 편집한 계획: `runs/<run_id>/<hash>_planner.json` (빈 자리 16 → 0, 무단결정 승인 9)
- 인터뷰 로그: `interviews/<hash>_<run_id>.jsonl` (25줄)
- planner_check: PASS · 회귀: 없음 · schema: PASS

다음: `python runner.py <input.json> --run-id <run_id> --start-at asset`
```

## 하지 않을 것

- **인터뷰 로그를 run 디렉토리에 두지 않는다.** 하류가 열 수 있고, 열면 계획 대신 인터뷰에 anchor된다.
- **편집 전 사본 없이 고치지 않는다.** 회귀 검사의 기준이 사라진다.
- **계획을 다시 쓰지 않는다.** 값을 넣고 자리를 나눌 뿐, 기존 id·문구·개수를 줄이지 않는다.
- **답을 받지 못한 필드를 채우지 않는다.** 계획은 하류의 계약이므로 여기서 지어낸 것은 아무도 다시 의심하지 않는다.
- **빈 자리만 묻지 않는다.** planner가 승인 없이 정해둔 값이 이 인터뷰의 절반이다.
- **피드백을 사건으로만 묻지 않는다.** 효과음·글로우는 연출이다. 학습자가 읽을 문장을 받아야 이 축이 채워진다.
- **전환을 방법만 묻고 끝내지 않는다.** 학습자가 다음 행동을 아는지 함께 묻는다.
- 하류가 안 보는 것을 묻지 않는다. **오디오(BGM/SFX)는 planner가 범위에서 제외하므로 묻지 않는다.**
  소리는 안 나가지만 **움직임은 나간다.** 오디오를 뺀다고 연출까지 빼지 않는다.
- 연출 질문을 요소마다 쪼개지 않는다. 화면당 하나로 묶는다.
- **답이 하나로 정해지는 것을 묻지 않는다.** 관례와 공용 컴포넌트가 소유한 것은 물을 정보가 아니다.
- 컴포넌트가 무엇을 소유하는지 기억으로 적지 않는다. 매번 스캔한다.
- 근거 없이 초안을 쓰지 않는다. 근거가 없으면 초안 없이 묻는다.
- **여러 화면을 한 번에 처리하지 않는다.** 일괄 처리는 뒤쪽 화면을 부실하게 만든다.
- **전개도를 손으로 그리지 않는다.** 계획에서 만든다. 손으로 그리면 계획에 없는 것이 섞인다.
- 사용자의 완료 신호 없이 파일을 쓰지 않는다.
- 검증에 실패한 채로 넘기지 않는다.
- **스토리보드 md를 고치지 않는다.** 인터뷰의 결과는 계획에 들어간다.
- `input.json`을 새로 만들지 않는다. 요청은 바뀌지 않았다.
