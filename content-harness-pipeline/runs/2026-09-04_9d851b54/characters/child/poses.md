# 초등학생 아이 Poses

## Pose Table

| Output file | Pose | Expression | Facing | Framing | Intended use | Prompt notes | Acceptance criteria |
|---|---|---|---|---|---|---|---|
| `output/assets/child_idle.webp` | 편안한 중립 대기 | 차분한 미소 | 정면 | 전신 | 기준 정체성 및 대기 장면 | 양팔을 자연스럽게 내리고 양발은 안정적으로 섬 | 동일 인물, 4.5등신, 전신, 투명 배경, 완전 불투명 |
| `output/assets/child_speaking.webp` | 한 손을 가볍게 든 말하기 | 밝고 호기심 많은 감탄 | 화면 오른쪽을 보는 시선 | 전신 | 질문·감탄·마무리 대화 | 오른쪽 말풍선으로 이어지는 시선과 손 방향 | idle과 동일 인물·의상·색·비율, 전신, 투명 배경, 완전 불투명 |

## Batch Plan

| Batch | Files | Worker | Notes |
|---|---|---|---|
| 01 | `child_idle.webp`, `child_speaking.webp` | primary | 기준 포즈를 먼저 만들고 같은 이미지를 정체성 참조로 두 번째 포즈 생성 |
