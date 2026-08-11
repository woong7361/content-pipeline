# Common Source

**선생님·차시·콘텐츠 세계관과 무관하게 재사용하는 것들을 둔다.**

특정 선생님의 얼굴·의상·말투·브랜드 색이 들어간 것은 여기 두지 않는다. 그런 것은 `source/[teacher]/`에 둔다.
판단이 애매하면 **"다음 차시에서 이걸 그대로 쓸까?"** 를 묻고, 아니라면 콘텐츠 쪽에 두었다가
두 번째 콘텐츠에서 같은 게 또 필요해질 때 올린다.

## 축

| 디렉토리 | 다루는 것 | 참조와 결과의 관계 |
|---|---|---|
| `components/` | HTML/CSS/JS 재사용 원본 | **그대로 inline한다** |
| `craft-examples/` | 글자를 굽는 asset의 완성도 기준 | **베끼면 실패다** |
| `assets/` (미구현) | 재사용 이미지와 사용 계약 | 그대로 쓴다 |

각 디렉토리의 `CLAUDE.md`가 그 축의 사용 계약이다. 작업 전에 먼저 읽는다.

**`craft-examples`만 관계가 반대**라는 점을 섞지 않는다.
`components`와 `assets`는 참조를 그대로 가져오는 것이 정답이지만,
`craft-examples`는 완성도만 가져오고 색·모티프·세계관은 그 run의 `art_direction`을 따라 새로 그린다.
그래서 세 축을 한 디렉토리로 합치지 않는다.

## 파이프라인 연결

`components`와 `craft-examples`는 `stages/scripts/`의 스캔 모듈이 프롬프트에 자동으로 싣는다.
**목록을 프롬프트에 손으로 적지 않는다** — 새 항목은 디렉토리에 넣기만 하면 되고, 프롬프트는 고치지 않는다.

`assets`(이미지 catalog)는 아직 연결되지 않았다. `input.json`의 `metadata.style_reference_set`이나
작업 지시로 사람이 경로를 넘긴다.

## 파일명이 `CLAUDE.md`인 이유

Claude Code는 `CLAUDE.md`만 자동으로 읽는다(`AGENTS.md`는 안 읽는다).
같은 디렉토리의 `AGENTS.md`는 이 파일을 가리킨다. 내용은 하나다.

상세 설계는 `docs/reusable-source-design.md`를 따른다.
