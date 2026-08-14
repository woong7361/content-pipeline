# 사서 선생님 Poses

## Pose Table

| Output file | Pose | Expression | Facing | Framing | Intended use | Prompt notes | Acceptance criteria |
|---|---|---|---|---|---|---|---|
| `char-librarian-idle.webp` | 돋보기를 들고 다른 손으로 옆 학습 대상을 안내 | 차분한 미소 | 정면 기반, 시선은 화면 중앙 | 전신 | 튜토리얼·유형 A~C·갤러리 설명 | 좌우 배치 가능한 여백, 단순한 손가락 | 동일 정체성, 전신 무크롭, 투명 배경, 돋보기 완전 불투명 |
| `char-librarian-worried.webp` | 양손을 머리 가까이 올린 걱정 동작 | 안쪽으로 올라간 눈썹, 작게 열린 입 | 몸은 정면, 시선은 오른쪽 위 | 전신 | 문제 발생 장면 | 땀 아이콘 금지, 오른쪽 safe zone | 동일 정체성, 공포·울음 금지, 손·발 무크롭, 투명 배경 |
| `char-librarian-praise.webp` | 가슴 앞에서 두 손을 모아 박수 | 환한 미소, 부드럽게 올라간 눈썹 | 정면, 시선은 학습자 | 전신 | 성공·복구·최종 완료 | 손 실루엣을 몸과 분리해 명확히 | 동일 정체성, 두 손 정상, 전신 무크롭, 투명 배경 |

## Batch Plan

| Batch | Files | Worker | Notes |
|---|---|---|---|
| 01 | 세 pose 전체 | root | 동일 호출에서 하나의 캐릭터 시트로 생성한 뒤 개별 PNG로 분리하여 정체성 드리프트를 최소화한다. |
