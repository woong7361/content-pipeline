# Teacher Source — 백승용

## 이 디렉토리의 성격

**백승용 선생님 콘텐츠의 화풍 기준이다.**

같은 선생님이 만든 차시들이 하나의 코스처럼 보이게 하는 것이 목적이다.
두 차시의 asset을 나란히 놓았을 때 **같은 작가가 그린 것으로 보여야 한다.**

| 문서 | 담는 것 |
|---|---|
| `style.md` | 화풍 계약과 판별 지점 |
| `characters.md` | 연령대별 캐릭터 작화 기준 |
| `assets.md` | 배경·소품·UI 표면·CTA의 화풍 기준 |

## 소재가 아니라 화풍을 가져온다

여기 있는 이미지는 **재사용할 asset이 아니다.**

`production/1-2/08`(학교 담장 색칠)에서 뽑았으므로 담장·페인트·교실이 찍혀 있지만,
다른 차시가 가져올 것은 그 소재가 아니라 **선, 채도, 명암 단계, 밀도, 재질 표현, 등신, 표정 언어**다.

새 차시의 소재는 그 스토리보드가 정한다. 도서관 차시면 도서관을 그리되, 그 도서관이
이 이미지들과 같은 손으로 그려진 것으로 보여야 한다.

캐릭터도 같다. 새 차시는 그 스토리보드의 인물을 쓴다.
`characters.md`의 인물은 **얼굴·헤어·의상·이름을 복제하라고 두는 것이 아니라**,
성인 여성 / 성인 남성 / 어린이를 각각 어떻게 그리는지 보여주려고 둔다.

## craft example과 반대다

`source/common/craft-examples`는 "베끼면 실패"다. 완성도만 가져오고 색·모티프는 새로 그린다.

**이 디렉토리는 그 반대다.** 화풍은 그대로 따라야 한다.
`must_follow: true`로 넘기면 **이미지에서 직접 관찰한 것이 자유로운 스타일 해석보다 우선한다.**

다만 "화풍을 따른다"와 "소재를 베낀다"는 다르다. 위 절을 참조한다.

## 파이프라인에 넘기는 법

`input.json`의 `metadata.style_reference_set`으로 넘긴다. **`categories`는 적지 않는다.**

```json
{
  "metadata": {
    "style_reference_set": {
      "id": "baek-seungyong-basic",
      "must_follow": true,
      "root": "source/baek-seungyong",
      "usage_policy": {
        "summary": "이미지를 직접 열어 확인하고 description보다 reference image를 우선한다. 항목별 use/avoid는 이 catalog가 소유한다."
      }
    }
  }
}
```

`categories`를 생략하면 `stages/scripts/teacher_source.py`가 `root`의 md를 스캔해 채운다.
**항목별 `use`·`avoid`는 `assets.md`·`characters.md`가 소유한다. input.json에 다시 적지 않는다.**

차시마다 같은 문장을 옮겨 적으면 그 사본이 catalog와 갈라지고, 어느 쪽이 맞는지 알 수 없게 된다.
`components`·`craft-examples` 축이 목록을 프롬프트에 손으로 적지 않는 것과 같은 이유다.

`categories`를 명시하면 그대로 쓴다. catalog 밖의 이미지를 한 번만 끼워 넣을 때만 쓴다.

**`style_reference_set` 키의 유무가 곧 on/off다.** `teacher_reference: true` 같은 별도 플래그를 두지 않는다 —
플래그와 내용이 어긋나면(true인데 `root`가 없는 상태) 어느 쪽이 맞는지 판정할 근거가 없다.
강도는 `must_follow`가 표현한다.

input을 새로 만들면 **run 전에 반드시 검증한다.** 없는 경로·오타 필드·빈 catalog를 여기서 잡는다.

```bash
python -B ./validate.py ./your_input.json --artifact input
```

- `root`는 프로젝트 기준 상대 경로다. `path`는 `root` 기준이며 `root` 밖으로 나갈 수 없다.
- 지원 범주는 **`backgrounds` / `characters` / `props` / `ctas` 네 개뿐**이다(`stages/scripts/style_references.py`).
  `assets/ui/`의 표면 asset은 `Category: props`로 둔다. 디렉토리만 `ui/`다.
- 확장자는 `.png` / `.jpg` / `.jpeg` / `.webp`만 된다.
- 존재하지 않는 경로를 넣으면 stage가 아니라 **입력 해석 단계에서 즉시 실패한다.**

## catalog 항목 쓰는 법

`## 제목` 절에 `- Path:`를 달면 catalog 항목이 된다. `Path`가 없는 절은 산문으로 보고 건너뛴다.
따라서 사람이 읽는 설명과 기계가 읽는 항목이 한 파일에 함께 있어도 된다.

| 필드 | 내용 |
|---|---|
| `Path` | `root` 기준 상대 경로. 이게 있어야 항목이다 |
| `Category` | `backgrounds` / `characters` / `props` / `ctas` |
| `Status` | `deprecated`면 스캔에서 제외된다 |
| `Role` | 이 이미지가 무엇의 기준인지 한 줄 |
| `Use` | **그 이미지에서 무엇을 볼지** |
| `Avoid` | **그 이미지의 소재 중 무엇을 가져오면 안 되는지** |

`asset_generator`는 asset마다 **관련 있는 작은 묶음만** 이미지 생성 참조로 쓴다
(배경 2~3개, 캐릭터 2~3개, 소품·타이틀 2~3개). 전체를 한 호출에 몰아넣지 않는다.
따라서 항목이 많아도 되지만, **`Role`과 `Use`가 정확해야 고르기가 된다.**

캐릭터는 계열당 한둘만 항목으로 만든다. 같은 인물의 모든 pose를 항목으로 만들면
그 계열이 참조 묶음을 다 차지해 배경·소품이 밀린다. pose 목록은 표로 두고 스캔되지 않게 한다.

## 파일명이 `CLAUDE.md`인 이유

Claude Code는 `CLAUDE.md`만 자동으로 읽는다. 같은 디렉토리의 `AGENTS.md`는 이 파일을 가리킨다.

상세 설계는 `docs/reusable-source-design.md` 4장을 따른다.
