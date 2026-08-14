# 사서 선생님 Poses

## Pose Table

| Output file | Pose | Expression | Facing | Framing | Intended use | Prompt notes | Acceptance criteria |
|---|---|---|---|---|---|---|---|
| `librarian_teacher_explaining.webp` | 한 손 돋보기, 다른 손으로 왼쪽 위를 가리킴 | 친절한 미소 | 3/4 왼쪽 | 전신 | 튜토리얼, 문제 유형 안내, 생활 사례 갤러리 | 기준 정체성 포즈. 시선과 손끝이 같은 왼쪽 위 대상을 향함 | 동일 정체성의 기준, 전신·돋보기·손·발 미절단, 투명 배경 |
| `librarian_teacher_distressed.webp` | 두 손으로 머리 양옆을 감쌈 | 눈썹을 올린 당황, 작은 땀방울 | 정면에 가까운 3/4, 시선 위쪽 | 허리 위 반신 | 고장 난 시계 문제 발생 | 공포·울음이 아닌 친근한 당황, 위쪽 시계 응시 | 기준 얼굴·안경·머리·의상 유지, 머리와 손 미절단, 투명 배경 |
| `librarian_teacher_cheering.webp` | 가슴 높이에서 두 손 박수 | 눈이 부드럽게 휘고 입을 크게 연 환한 웃음 | 3/4 왼쪽 | 전신 | 정답, 복구, 최종 완료 축하 | 박수치는 두 손 사이가 분명하고 시선은 왼쪽 학습 결과로 향함 | 기준 정체성·비율·의상 유지, 전신·손·발 미절단, 투명 배경 |

## Batch Plan

| Batch | Files | Worker | Notes |
|---|---|---|---|
| 01 | `librarian_teacher_explaining.webp` | primary agent | 최초 기준 포즈 생성 및 알파 QA |
| 02 | `librarian_teacher_distressed.webp`, `librarian_teacher_cheering.webp` | primary agent | Batch 01 이미지를 정체성 참조로 한 순차 생성 및 비교 QA |
