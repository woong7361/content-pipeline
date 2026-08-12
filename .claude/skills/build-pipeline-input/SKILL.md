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
for c in load_components():
    ra=c.get('requires_art',[])
    uw=(c.get('use_when') or ['-'])[0]
    print(f\"{c['name']:18} art={len(ra)}  {uw[:46]}\")
print('teacher:', [p.name for p in Path('source').iterdir() if p.is_dir() and p.name!='common'])"
```

`art=N`이 0보다 크면 **그 컴포넌트를 고르는 순간 N장이 추가로 생성된다.** 고를 때 함께 알린다.

### 2. 사용자에게 묻는다

한 번에 묻고, 각 항목에 스캔 결과를 붙인다.

| 묻는 것 | 비고 |
|---|---|
| 스토리보드 md 경로 | 필수. 존재와 `.md` 확장자를 확인한다 |
| 따라갈 선생님 화풍 | 스캔한 teacher 목록 + **`plain`(참조 없이 자유 화풍)** |
| `must_follow` | 화풍을 강제할지. teacher를 고른 경우만 |
| 쓸 공용 컴포넌트 | 스캔 목록에서 다중 선택. `art=N`을 함께 보여준다 |
| 추가 요청 | `user_request`. 없으면 비운다 |

`plain`이 유효한 모드다. `style_reference_set` 키를 아예 넣지 않으면 화풍 참조 없이 돈다.

**컴포넌트를 고르지 않아도 된다.** 그러면 builder가 `use_when`/`avoid`로 알아서 고르는데,
그때는 art를 요구하는 컴포넌트가 계획되지 않은 art를 쓰려다 빈 자리가 생길 수 있다.
차시 전체에 걸리는 것(`topbar`, `scene-controller`, `debug-jumper`)은 대체로 넣는 편이 낫다고 안내한다.

### 3. 파일을 만든다

`brief_hash`와 `source_sha256`은 **계산한다.** 사용자에게 묻지 않는다.

```python
import hashlib, json
raw = open(md_path, 'rb').read()
sha = hashlib.sha256(raw).hexdigest()
# brief_hash = sha[:8], metadata.source_sha256 = sha
```

`created_at`은 ISO 8601 + 오프셋. 파일명은 `{학년}_{학기}_{차시}_{주제}_input.json` 꼴로 짓는다.

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

### 4. 반드시 검증한다

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

### 5. 다음 명령을 알려준다

```bash
cd content-harness-pipeline
python -B ./runner.py ./<파일>
```

컴포넌트를 골랐다면 **그 art가 asset으로 추가 생성된다는 것**을 함께 알린다.

## 하지 않을 것

- `brief_hash`를 사람에게 묻거나 임의로 짓지 않는다. 스토리보드 해시에서 나온다.
- 컴포넌트 목록·teacher 목록을 기억으로 적지 않는다. 매번 스캔한다.
- `categories`를 손으로 채우지 않는다.
- 검증을 건너뛰지 않는다.
- 같은 `brief_hash`로 기존 run이 있으면 알린다. `runner.py`는 `--overwrite` 없이 덮어쓰지 않는다.

상세 계약은 `content-harness-pipeline/docs/reusable-source-design.md` 8장,
`schemas/input.schema.json`, `source/[teacher]/CLAUDE.md`에 있다.
