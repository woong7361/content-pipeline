# Character Asset QA

## Accepted

- `librarian-teacher-idle.webp`: 동일한 얼굴·헤어·안경·브로치·의상·팔레트·7~7.5등신 유지, 중립 정면 전신, 손 소품 없음, 1024×1536 RGBA, 네 모서리 alpha 0.
- `librarian-teacher-distressed.webp`: 동일 정체성 유지, 양손을 머리 가까이 둔 절제된 당황 포즈, 오른쪽 위 시선과 땀 아이콘 2개, 전신·제스처 무절단, 1024×1536 RGBA, 네 모서리 alpha 0.
- `librarian-teacher-explaining.webp`: 동일 정체성 유지, 오른손의 작은 돋보기와 왼쪽을 향한 열린 손바닥, 왼쪽 학습 대상 safe zone, 전신·소품 무절단, 1024×1536 RGBA, 네 모서리 alpha 0.

## Needs Regeneration

| File | Reason | Suggested fix |
|---|---|---|

## Integration Notes

- 세 파일 모두 투명 배경의 세로형 전신 PNG이며 검은 화면은 뷰어의 투명 영역 표시다.
- 조명은 위에서 내려오는 따뜻한 확산광, 외곽선은 짙은 갈색 중간 굵기, 명암은 2~3단계로 통일했다.
- `explaining`은 화면 오른쪽 배치 시 왼쪽의 문제·말풍선 영역을 가리지 않도록 열린 제스처를 왼쪽으로 뻗는다.

