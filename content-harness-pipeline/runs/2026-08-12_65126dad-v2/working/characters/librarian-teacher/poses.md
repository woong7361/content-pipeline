# 사서 선생님 Poses

## Pose Table

| Output file | Pose | Expression | Facing | Framing | Intended use | Prompt notes | Acceptance criteria |
|---|---|---|---|---|---|---|---|
| `librarian-teacher-idle.webp` | relaxed-standing-idle | 편안한 중립 | 정면 | 전신 | 정체성 기준, 도입·공통 대기 | 팔을 자연스럽게 내리고 손 소품 없음 | 동일 정체성, 전신 무절단, 투명 배경, 충분한 여백 |
| `librarian-teacher-distressed.webp` | worried-head-hold | 눈썹만 걱정스럽게, 작은 땀 1~2개 | 몸은 정면에 가깝고 시선은 오른쪽 위 | 전신 | activity1 문제 발생 | 두 손을 머리 가까이, 어깨 약간 움츠림 | 공포·울음·얼굴 왜곡 없음, 제스처 무절단, 투명 배경 |
| `librarian-teacher-explaining.webp` | magnifier-open-palm-explain | 친절한 미소 | 화면 중앙인 왼쪽을 향한 열린 제스처 | 전신 | 튜토리얼·유형 A/B/C·갤러리 안내 | 작은 돋보기 한 손, 다른 손은 열린 손바닥 | 몸 왼쪽 safe zone, 손·돋보기 무절단, 동일 정체성, 투명 배경 |

## Batch Plan

| Batch | Files | Worker | Notes |
|---|---|---|---|
| 01 | idle, distressed, explaining | primary agent | 한 호출에서 동일 캐릭터 포즈 시트 생성 후 개별 패널 분리 금지; 각 자산은 별도 호출하되 idle을 먼저 고정하고 후속 포즈에서 참조 |

