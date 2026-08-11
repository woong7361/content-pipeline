# Craft Examples

## 이 디렉토리의 성격

**글자를 이미지에 굽는 asset의 완성도 기준(craft bar)을 그림으로 보여주는 예시 모음이다.**

여기 있는 이미지는 **재사용할 asset이 아니다.** 가져다 쓰라고 두는 것이 아니라, 이미 프롬프트에
말로 적혀 있는 규칙("글자를 아트와 한 덩어리로 통합한다")의 **합격선이 어느 정도인지**를 보여주려고 둔다.
그 합격선은 문장으로 전달되지 않으므로 그림으로 둔다.

## 우선순위 — 이 축의 핵심

**`art_direction`이 예시 이미지보다 우선한다.**

이것이 `source/[teacher]` 화풍 참조나 `identity_context`와 **정반대**라는 점이 이 디렉토리의 전부다.

| | 예시(craft example) | 화풍 참조(`style_reference_set`) · `identity_context` |
|---|---|---|
| 무엇을 보여주나 | 얼마나 잘 만들어야 하는가 | 어떤 그림이어야 하는가 |
| 범위 | run 무관 상수 | run별 / 캐릭터별 |
| 충돌하면 | **`art_direction`이 이긴다** | **참조 이미지가 이긴다** |
| 베끼면 | 실패 | 정답 |

명시하지 않으면 모델이 `identity_context` 습관대로 예시의 팔레트와 모티프를 복제해,
그 run에서 새로 정한 `art_direction`을 덮어쓴다.

예시에서 가져오는 것은 **구조와 재질 논리**뿐이다.
색·팔레트·모티프·소재·세계관은 그 run의 `art_direction`과 `asset_plan`을 따라 **새로 그린다.**

## 합격 판정

- 글자를 나중에 CSS로 얹은 것처럼 보이면 실패다.
- 예시와 나란히 놓았을 때 **같은 완성도**로 보이되 **같은 그림**으로 보이면 실패다.
- 예시를 그대로 쓰거나, 색만 바꿔 베끼거나, 예시의 모티프를 콘텐츠와 무관하게 끌어오면 실패다.

## 구조

```text
craft-examples/
  CLAUDE.md              # 이 파일. 축 전체의 우선순위와 합격 판정
  AGENTS.md              # CLAUDE.md를 가리킨다
  [example]/
    example.md           # 이 예시의 사용 계약
    *.png                # 기준 이미지. 실제로 열어서 봐야 한다
```

한 디렉토리 = 하나의 **craft 주제**다. 이미지 한 장을 뜻하지 않는다.
같은 주제 안에서 서로 대비되는 이미지가 여러 장이면 한 디렉토리에 함께 둔다(`stamp-lettering`).
그 장들이 서로 어떤 관계인지(형제인지 별개 asset인지)는 `example.md`가 적는다.

## `example.md` 형식

머리 목록은 manifest가 얕게 파싱한다. 아래 필드 이름을 그대로 쓴다.

```md
# Stamp Lettering

- Type: `craft_example`
- Status: `approved`
- Source: `production/1-2/08/assets/feedback-stamp-correct.webp`
- Images:
  - `stamp-lettering-correct.png`
- Applies to:
  - 정답/오답 판정 도장
- Take:
  - 문구가 도장 면 안쪽 밴드에 들어간다
- Do not take:
  - 코랄 레드·슬레이트 블루라는 특정 색

## 상세

(manifest는 여기까지 읽지 않는다. stage가 이 예시를 고른 뒤 직접 읽는다.)
```

`Applies to`가 선택 기준이다. **어떤 asset을 만들 때 이 예시를 열어야 하는지**를 적는다.
`Take`는 콘텐츠가 달라도 유지되는 구조·재질 논리, `Do not take`는 그 예시에만 해당하는
색·모티프·소재다. 둘의 경계가 곧 위 우선순위 표를 개별 예시에 적용한 결과다.

## 규칙

- 이미지가 기준이고 텍스트는 선택을 돕는 설명이다. **설명문을 길게 써서 이미지를 대체하지 않는다.**
- 새 예시를 넣을 때는 `Applies to`가 기존 예시와 겹치지 않는지 본다. 겹치면 새 디렉토리가 아니라
  기존 `example.md`에 이미지를 추가한다.
- 목록을 프롬프트에 손으로 적지 않는다. `stages/scripts/craft_examples.py`가 이 디렉토리를 스캔한다.
- 예시 파일은 읽기 전용이다. 파이프라인이 생성 대상에 넣거나 덮어쓰지 않는다.

## 왜 `source/common/assets/`가 아닌가

`source/common/assets/`(설계상 이미지 catalog)는 **가져다 쓰는 asset**을 두는 곳이고,
`source/[teacher]/`는 **따라야 할 화풍**을 두는 곳이다. 둘 다 "참조가 이긴다".

craft example은 "참조를 베끼면 실패"이므로 같은 디렉토리에 섞으면 우선순위 규칙이 무너진다.
그래서 이름도 `assets`가 아니라 역할을 드러내는 `craft-examples`다.

상세 설계는 `docs/reusable-source-design.md` 12장을 따른다.
