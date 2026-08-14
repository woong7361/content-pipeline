# 사서 선생님 Design

## Source Of Truth

- Character id: `librarian-teacher`
- Identity source: planner `characters[].identity`와 `identity_context`
- Reference files: `source/baek-seungyong/assets/characters/teacher-idle.webp`, `teacher-praising.webp`; identity가 아니라 선·비율·명암·표정 언어 참조
- Usage target: 단일 HTML 교육 콘텐츠의 도입·튜토리얼·문제 안내 캐릭터

## Identity Invariants

- Age/read: 안정감 있고 친근한 성인 여성 사서
- Face shape: 부드러운 긴 타원형, 따뜻한 밝은 베이지 피부
- Hair: 짙은 흑갈색, 왼쪽 가르마 긴 옆머리, 목덜미의 낮고 둥근 번
- Eyes: 바깥쪽이 살짝 올라간 짙은 헤이즐 타원 눈, 흰 하이라이트 1~2점
- Body proportions: 7~7.5등신, 곧고 안정적인 체형과 자연스러운 어깨 폭
- Distinctive traits: 둥근 모서리의 자주색 반무테 안경, 옅은 홍조, 왼쪽 가슴의 작은 책 모양 브로치

## Outfit Invariants

- Main outfit: 아이보리 긴소매 블라우스, 짙은 청록 종아리 길이 A라인 치마, 겨자색 허리 앞치마
- Colors: 아이보리, 짙은 청록, 겨자색, 와인색, 흑갈색
- Accessories: 자주색 반무테 안경, 책 모양 브로치
- Footwear: 짙은 와인색 로퍼
- Props allowed: explaining 포즈에만 작은 돋보기
- Props forbidden: idle과 distressed 포즈의 손 소품

## Style Invariants

- Rendering style: 따뜻한 도서관 셀 애니메이션 어드벤처, 참조 이미지의 한국 교육용 캐릭터 작화 밀도
- Line/edge treatment: 짙은 갈색 중간 굵기 외곽선, 둥글고 단순한 형태
- Lighting: 위에서 내려오는 따뜻한 확산광, 밝은 면·기본 면·부드러운 그림자 면의 2~3단계
- Proportions: 모든 포즈에서 동일한 7~7.5등신
- Mood: 친근하고 절제된 감정, 얼굴 변형 없이 눈썹·입꼬리·팔 방향으로 표현
- Match existing assets: 세 포즈의 얼굴, 헤어, 의상, 팔레트, 신체 비율, 조명 방향 고정

## Alpha And Canvas Rules

- Output format: PNG
- Background: 완전히 평평한 제거용 `#00ff00` 크로마키 원본 후 투명 알파로 변환
- Body framing: 머리부터 발끝과 모든 손·소품이 보이는 전신
- Margins: 머리 위·발 아래·제스처 바깥에 충분한 여백
- Opacity: 인물, 의상, 머리, 신발, 안경, 브로치, 돋보기와 신체 모든 부분은 완전 불투명
- Shadows: 바닥 그림자·접지 그림자 없음

## Negative Constraints

- Do not change: 얼굴형, 피부톤, 헤어·번 위치, 안경, 의상, 앞치마, 브로치, 로퍼, 등신과 체형
- Do not include: 배경 풍경, 바닥, 텍스트, 워터마크, UI, 추가 인물
- Avoid: 실사, 3D, 과장된 SD, 참조 교사 인물의 갈색 단발·민트 블라우스·크림 팬츠 복제, 반투명 의상, 잘린 손발

## Pose Compatibility Notes

- Default facing: idle 정면; distressed는 화면 중앙 위쪽(오른쪽 위) 시선; explaining은 화면 중앙(왼쪽)으로 열린 제스처
- UI-safe hand direction: explaining은 몸 왼쪽으로 열린 손바닥, 다른 손의 돋보기는 몸 가까이
- Speech bubble side: explaining은 몸 왼쪽 safe zone
- Important screen clearances: 전신 실루엣과 제스처를 캐릭터 주위에만 유지해 중앙 학습 대상을 가리지 않음
- Known target scenes: activity1-problem, activity1-tutorial, activity2-global, activity2-type-a/b/c, activity3-gallery

