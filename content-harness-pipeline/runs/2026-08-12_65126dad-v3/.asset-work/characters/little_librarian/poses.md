# 꼬마 사서 Poses

## Pose Table

| Output file | Pose | Expression | Facing | Framing | Intended use | Prompt notes | Acceptance criteria |
|---|---|---|---|---|---|---|---|
| `char-little-idle.webp` | 자신 있게 한 손 들기 | 작은 미소 | 정면, 시선 중앙 | 전신 | 대기·등장 | 가슴을 펴고 손 모양 단순화 | 동일 정체성, 전신, 투명, 발 아래 여백 |
| `char-little-confused.webp` | 몸을 약간 기울이고 한 손을 턱 가까이 | 한쪽 눈썹을 올린 궁금함 | 선택 답 쪽 시선 | 전신 | 오답·재시도 | 울거나 좌절하지 않음 | 동일 정체성, 물음표 없음, 말풍선 여백 |
| `char-little-success.webp` | 한 손 V, 다른 손 허리 | 입을 열어 밝게 웃음 | 학습자 응시 | 전신 | 정답·최종 성공 | V 손가락이 정확히 두 개 | 동일 정체성, 전신, 투명, 점프 여백 |

## Batch Plan

| Batch | Files | Worker | Notes |
|---|---|---|---|
| 01 | 세 포즈 전체 | primary | 한 호출로 시트 생성 후 포즈별 분리하여 정체성 드리프트를 최소화한다. |
