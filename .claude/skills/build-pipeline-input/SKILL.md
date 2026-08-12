---
name: build-pipeline-input
description: content-harness-pipeline의 input.json을 만든다. 스토리보드 md, 따라갈 선생님 화풍(또는 plain), 쓸 공용 컴포넌트를 정하고 brief_hash를 계산해 validate까지 통과시킨다. "파이프라인 input 만들어줘", "이 스토리보드로 콘텐츠 만들자", "input.json 새로 만들어줘" 같은 요청에 쓴다.
---

# 파이프라인 input 만들기

`content-harness-pipeline/runner.py`에 넘길 `input.json`을 만든다.

**손으로 쓰지 않는다.** `brief_hash`는 스토리보드 md의 sha256 앞 8자이고, 컴포넌트 이름과 teacher root는
디렉토리를 스캔해야 나오며, 잘못 쓰면 run 중간이 아니라 시작조차 못 한다.

## 순서

### 1. 무엇이 있는지 먼저 스캔한다

물어보기 전에 선택지를 만든다. 기억으로 목록을 적지 않는다 — 컴포넌트와 선생님은 계속 늘어난다.

```bash
cd content-harness-pipeline
python -B -c "
import sys,io; sys.path.insert(0,'.')
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8')
from stages.scripts.common_components import load_components
from pathlib import Path
for c in sorted(load_components(), key=lambda x: x['name']):
    d=Path(c['dir']).as_posix()
    src='common' if '/source/common/' in d else Path(c['dir']).parent.parent.name
    print(f\"{c['name']:18} {src:14} art={len(c.get('requires_art',[]))}  {c.get('role','')}\")
print('teacher:', [p.name for p in Path('source').iterdir() if p.is_dir() and p.name!='common'])"
```

출력이 보고서의 `출처`·`art`·`역할` 세 열이 된다. `art=N`이 0보다 크면 **그 컴포넌트를 넣는 순간 N장이 추가로 생성된다.**

### 2. 스토리보드를 읽고 스스로 정한다

**컴포넌트를 사용자에게 나열해 고르게 하지 않는다.** 스토리보드가 근거를 이미 갖고 있다.

스토리보드를 읽고 컴포넌트마다 근거를 찾은 뒤, 아래 규칙으로 기본값을 정한다.

| 스토리보드 근거 | art 비용 | 기본 |
|---|---|---|
| 있음 | 0 | **포함** |
| 있음 | 있음 | **포함** — 근거가 있으니 비용이 정당하다 |
| 없음 | 0 | **포함** — 인프라다. 안 넣을 이유가 없다 |
| **없음** | **있음** | **제외** — 보고서에 올려 사용자가 결정하게 한다 |

마지막 줄이 유일하게 사용자 판단이 필요한 칸이다. **비용이 드는데 근거가 없는 것만 남긴다.**
나머지를 함께 물으면 정작 물어야 할 하나가 묻힌다.

### 3. 세션에 보고서를 보여준다 (파일로 만들지 않는다)

**`AskUserQuestion`을 쓰지 않는다.** 선택지가 최대 4개인데 컴포넌트도 teacher 목록도 계속 늘어난다.
4칸에 맞추면 필요한 항목이 조용히 잘린다(실제로 `topbar`·`debug-jumper`가 그렇게 빠진 적이 있다).

**긴 산문을 표 셀에 넣지 않는다.** 터미널 표는 폭이 넘치면 **조용히 잘라낸다.**
근거가 잘린 줄 모르고 결정하게 되므로 위험하다(실제로 "스토리보드 근거: 없음 (인프라, art" 처럼 문장이 끊겼다).

표는 값이 짧을 때만 쓴다. 산문은 **고정 라벨 + 한 줄**로 쓴다. 라벨이 앞에 오면 폭이 넘쳐도 줄바꿈만 되고 내용은 남는다.

````markdown
## 컴포넌트

### 포함 (6) — 결정 불필요

- **`topbar`** · common · art 0
  - 역할: 차시 전체에 걸리는 상단 HUD(제목·단계·진행률·소리)와 차시 목록 드로어
  - 근거: "좌측 상단(햄버거 메뉴): 1~10차시 목록 슬라이드 아웃", "우측 상단(에너지 게이지)"
- **`keypad`** · common · art 0
  - 역할: 숫자를 눌러 넣는 입력 키패드
  - 근거: "빈칸 터치 시 우측 하단에 숫자 키패드 팝업"

### 결정 ① — `feedback-layer`를 넣을까요?

- **`feedback-layer`** · common · **art 2** · 현재 **제외**
  - 역할: 정답/오답 판정을 도장으로 찍어 보여주는 레이어
  - 뺀 이유: 스토리보드에 도장 언급이 0건이다. 정답은 "딩동댕 + 글로우 + 꼬마 사서 점프",
    오답은 "띠익 + 흔들림 + 손가락 아이콘"으로 이미 구체적으로 지정돼 있다
  - 넣으면: 도장 2장이 추가 생성된다

## 화풍

### 결정 ② — 어떤 화풍을 따를까요?

- 현재: **`baek-seungyong`** · `must_follow: true`
- 고를 수 있는 것:
  - `baek-seungyong` — 08 학교 담장 차시에서 뽑은 화풍. 16항목
  - `plain` — 참조 없이 자유 화풍. `style_reference_set`을 아예 넣지 않는다
- `must_follow`: `true`(참조가 자유 해석을 이긴다) / `false`(참고만)
````

- **출처**는 manifest의 `dir`에서 낸다. `source/common/` 아래면 `common`, 아니면 그 teacher 이름.
  teacher가 같은 이름의 common 컴포넌트를 덮었으면 그 항목에 `· 백승용이 common을 덮음`을 붙인다 —
  그게 실제로 무엇이 쓰이는지 결정한다.
- **역할**은 `component.md`의 `Role` 필드를 **그대로 옮긴다.** 매번 새로 요약하면 보고서마다 말이 달라진다.
- **근거**는 스토리보드 원문을 짧게 인용한다. 지어내지 않는다 — 못 찾았으면 "없음"이다.
- **화풍은 teacher가 하나뿐이어도 목록을 보여준다.** `plain`이 항상 대안이고, 그게 있다는 걸 모르면 못 고른다.

### 3.1 결정을 번호로 묶고 끝에 다시 모은다

사용자가 무엇을 답해야 하는지 한눈에 보이게 한다. 보고서 마지막은 항상 이 형태로 끝낸다.

```markdown
## 결정할 것

① `feedback-layer` 포함 여부 — 현재 **제외** (넣으면 도장 2장 추가)
② 화풍 — 현재 **`baek-seungyong`, must_follow: true**

그대로 좋으면 답하지 않아도 됩니다. 파일은 이미 만들어져 검증을 통과했습니다.
바꿀 것만 번호로 알려주세요.
```

- **포함으로 정한 것에는 번호를 붙이지 않는다.** 번호는 "답해야 할 것"의 표시다.
  전부 번호를 매기면 무엇이 질문인지 사라진다.
- 결정이 하나도 없으면 "결정할 것: 없음"이라고 쓰고 그대로 끝낸다.

### 4. 정한 대로 파일을 만들고 보고서와 함께 낸다

**답을 기다리지 않는다.** 기본값으로 파일을 만들어 검증까지 통과시킨 뒤, 보고서와 함께 낸다.
사용자는 다음 프롬프트에서 고치면 된다. 맞으면 왕복이 0번이고, 틀려도 1번이다.

바꿀 것이 있으면 알려달라고 마지막에 적는다.

### 5. 파일 형태

`brief_hash`와 `source_sha256`은 **계산한다.** 사용자에게 묻지 않는다.

```python
import hashlib, json
raw = open(md_path, 'rb').read()
sha = hashlib.sha256(raw).hexdigest()
# brief_hash = sha[:8], metadata.source_sha256 = sha
```

`created_at`은 ISO 8601 + 오프셋.

**파일은 항상 새로 만든다. 기존 input을 고치거나 덮어쓰지 않는다.**
그래서 파일명에 생성 시각을 넣어 겹치지 않게 한다.

```
{학년}_{차시}_{주제}_{YYYYMMDD-HHMM}_input.json
예: grade2_lesson8_time_20260812-1432_input.json
```

이름순 정렬이 곧 시간순이라 어느 것이 최신인지 보인다.

형태:

```json
{
  "brief_hash": "<sha[:8]>",
  "created_at": "<ISO8601>",
  "brief": {
    "md_path": "<절대 경로>",
    "title": "<차시 제목>",
    "user_request": "<선택>"
  },
  "metadata": {
    "components": ["topbar", "scene-controller", "debug-jumper"],
    "source_sha256": "<sha>",
    "style_reference_set": {
      "id": "<teacher>-basic",
      "must_follow": true,
      "root": "source/<teacher>",
      "usage_policy": {
        "summary": "이미지를 직접 열어 확인하고 description보다 reference image를 우선한다. 항목별 use/avoid는 catalog가 소유한다."
      }
    }
  }
}
```

**`style_reference_set.categories`는 적지 않는다.** 생략하면 `root`의 md catalog를 스캔해 채운다.
항목별 `use`/`avoid`를 여기 옮겨 적으면 그 사본이 catalog와 갈라진다.

`plain`이면 `style_reference_set` 블록 전체를 뺀다.

### 6. 반드시 검증한다

```bash
cd content-harness-pipeline && python -B ./validate.py ./<파일> --artifact input
```

`PASS`가 아니면 사용자에게 넘기지 않는다. 이 검증이 잡는 것:

- 스키마 — `root` 누락, 오타 필드, 타입 불일치
- 해석 — 없는 디렉토리, 없는 이미지, root 밖 경로, 지원 안 하는 확장자
- `must_follow: true`인데 참조 0개
- catalog에 `- Path:` 항목이 하나도 없음
- 화풍 참조가 공용 컴포넌트 asset과 **같은 파일**인 경우(내용 해시로 비교)

컴포넌트 이름 오타는 여기서 안 잡히고 planner 시작 시 잡힌다. 미리 확인하려면:

```bash
python -B -c "
import sys,json; sys.path.insert(0,'.')
from stages.scripts.common_components import build_required_art_section
build_required_art_section(json.load(open('<파일>',encoding='utf-8')))
print('components ok')"
```

### 7. 다음 명령과 결정할 것을 알려준다

```bash
cd content-harness-pipeline
python -B ./runner.py ./<파일>
```

컴포넌트를 골랐다면 **그 art가 asset으로 추가 생성된다는 것**을 함께 알린다.
같은 `brief_hash`로 기존 run이 있으면 run_id가 어떻게 갈리는지도 알린다.

마지막은 항상 3.1의 "결정할 것" 블록으로 끝낸다.

## 하지 않을 것

- `brief_hash`를 사람에게 묻거나 임의로 짓지 않는다. 스토리보드 해시에서 나온다.
- 컴포넌트 목록·teacher 목록을 기억으로 적지 않는다. 매번 스캔한다.
- **`AskUserQuestion`으로 컴포넌트나 teacher를 고르게 하지 않는다.** 선택지 4개 상한에 걸려 조용히 잘린다.
- 역할 설명을 새로 지어내지 않는다. `component.md`의 `Role`을 옮긴다.
- 스토리보드 근거를 지어내지 않는다. 못 찾았으면 "없음"이다.
- `categories`를 손으로 채우지 않는다.
- 검증을 건너뛰지 않는다.
- **긴 산문을 표 셀에 넣지 않는다.** 터미널 표는 폭이 넘치면 조용히 잘라내서 근거가 사라진다.
- 포함으로 정한 항목에 번호를 붙이지 않는다. 번호는 답해야 할 것의 표시다.
- teacher가 하나뿐이어도 목록과 `plain`을 함께 보여준다.
- 기존 input 파일을 고치거나 덮어쓰지 않는다. 항상 새로 만든다.
- 같은 `brief_hash`로 기존 run이 있으면 알린다. **`run_id`는 `{날짜}_{brief_hash}`라 파일명과 무관하다** —
  같은 날 두 input을 돌리면 같은 run 디렉토리를 쓰므로, 둘 다 남기려면 `--run-id`를 따로 준다.

상세 계약은 `content-harness-pipeline/docs/reusable-source-design.md` 8장,
`schemas/input.schema.json`, `source/[teacher]/CLAUDE.md`에 있다.
