# Character Asset QA

## Accepted

- `output/assets/librarian_explaining.webp`: 동일한 얼굴·헤어·안경·의상·배지 정체성, 화면 중앙을 향한 손과 돋보기, 전신 및 소품 여백, RGBA 투명 배경 확인.
- `output/assets/librarian_distressed.webp`: 기준 포즈와 동일 정체성, 양손 머리 감싸기·올라간 어깨·땀방울·중앙 상단 시선, 전신 여백, RGBA 투명 배경 확인.
- `output/assets/librarian_success.webp`: 기준 포즈와 동일 정체성, 가슴 앞 박수·환한 미소·화면 중앙 시선, 전신 및 손 여백, RGBA 투명 배경 확인.

## Needs Regeneration

| File | Reason | Suggested fix |
|---|---|---|

## Integration Notes

- 세 파일 모두 네 모서리 alpha가 0이며 캐릭터 본체는 완전 불투명 픽셀을 유지한다.
- 이미지 크기는 세로 약 1.66K이며 머리, 손, 발, 안경, 배지와 각 포즈 소품이 잘리지 않는다.
- 설명 포즈의 손은 오른쪽 배치에서 화면 안쪽인 왼쪽을 가리킨다.
- 성공 포즈의 제한적인 금빛 외곽 강조는 success 조명 규칙과 일치한다.
