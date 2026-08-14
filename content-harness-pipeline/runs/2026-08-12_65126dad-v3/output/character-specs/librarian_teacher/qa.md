# Character Asset QA

## Accepted

- `char-librarian-idle.webp`: 동일한 얼굴형·낮은 번·자두색 카디건·숲색 스커트·황동 브로치가 유지되며, 돋보기와 안내 손이 분명하고 전신 및 소품이 잘리지 않았다.
- `char-librarian-worried.webp`: 같은 인물과 의상을 유지하고, 오른쪽 위 시선·양손 걱정 동작·절제된 표정이 요구 장면에 맞으며 땀 아이콘이 없다.
- `char-librarian-praise.webp`: 같은 인물과 의상을 유지하고, 박수치는 두 손이 몸통과 구분되며 학습자를 향한 밝은 표정이 읽힌다.
- 세 파일 모두 32bpp ARGB PNG이며 실제 투명 배경, 완전한 전신, 사방 안전 여백, 불투명한 의상과 신체, 글자·워터마크·배경 없음 조건을 충족한다.
- 세 pose의 얼굴, 머리, 피부톤, 성인 비율, 의상 구조, 팔레트, 브로치 위치와 상부 확산광 방향이 일치한다.

## Needs Regeneration

| File | Reason | Suggested fix |
|---|---|---|
| 없음 | 없음 | 없음 |

## Integration Notes

- 세 파일의 캔버스 높이는 941px로 같아 HTML에서 동일 높이 기준으로 스케일링할 수 있다.
- idle은 오른쪽 안내 손 쪽 40px, worried는 오른쪽 131px, praise는 오른쪽 187px의 투명 여백을 보유한다.
- 말풍선, 땀 아이콘, 시계와 학습 정보는 계획대로 HTML/CSS 오버레이로 배치한다.
