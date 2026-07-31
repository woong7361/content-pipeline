# 사서 선생님 Poses

## Pose Table

| Output file | Pose | Expression | Facing | Framing | Intended use | Prompt notes | Acceptance criteria |
|---|---|---|---|---|---|---|---|
| `librarian_explaining.png` | 한 손에 둥근 돋보기를 들고 다른 손으로 화면 중앙을 가리킴 | 차분하고 친절함 | 오른쪽 배치용, 몸과 시선은 화면 왼쪽 | full-body | tutorial, type A/B/C 안내 | 최초 정체성 기준 포즈 | 동일 정체성, 손과 돋보기 완전 노출, 투명 배경 |
| `librarian_distressed.png` | 두 손으로 머리를 감싸고 어깨를 올림 | 놀람, 이마 옆 땀방울 | 완만한 3/4 정면, 시선 중앙 상단 | full-body | activity1_problem | 설명 포즈의 인물 정체성을 그대로 유지 | 동일 정체성, 머리·손·발 완전 노출, 투명 배경 |
| `librarian_success.png` | 두 손을 가슴 앞에서 박수침 | 환한 웃음과 안도 | 오른쪽 배치용, 시선 화면 중앙 | full-body | success, outro, final | 설명 포즈의 인물 정체성을 그대로 유지 | 동일 정체성, 박수치는 두 손과 발 완전 노출, 투명 배경 |

## Batch Plan

| Batch | Files | Worker | Notes |
|---|---|---|---|
| 01 | `librarian_explaining.png`, `librarian_distressed.png`, `librarian_success.png` | primary agent | explaining을 먼저 만들고 나머지 두 포즈의 시각 기준으로 사용한다. |
