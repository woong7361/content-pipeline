# 꼬마 사서 Design

## Source Of Truth

- Character id: `little_librarian`
- Identity source: planner `characters[].identity`와 `identity_context`
- Reference files: `student-idle.webp`, `teacher-idle.webp`, `teacher-praising.webp`는 그림체만 참고
- Usage target: 활동 1~3의 대기, 오답 재시도, 성공 상태

## Identity Invariants

- Age/read: 초등 저학년 어린이
- Face shape: 넓고 둥근 얼굴, 따뜻한 중간 밝기 베이지 피부
- Hair: 밤색 짧은 버섯형, 오른쪽으로 흐르는 둥근 앞머리, 정수리 한 가닥
- Eyes: 크고 둥근 짙은 갈색 눈, 흰 하이라이트 두 점
- Body proportions: 4~4.5등신, 짧은 팔다리와 둥근 손발
- Distinctive traits: 코 양옆 옅은 주근깨 세 점씩

## Outfit Invariants

- Main outfit: 아이보리 반소매 셔츠, 짙은 남색 도서관 조끼, 황토색 나비넥타이, 벽돌색 무릎 길이 반바지
- Accessories: 조끼 왼쪽의 작은 책 모양 이름표
- Footwear: 아이보리 양말, 짙은 갈색 발목 부츠
- Props forbidden: 도구, 트로피, 책 등 임의 소품

## Style Invariants

- Rendering style: 따뜻한 마을 도서관 셀 일러스트
- Line/edge treatment: 짙은 갈색 중간 굵기 외곽선, 큰 읽기 쉬운 면
- Lighting: 위쪽 부드러운 확산광, 2~3단계 명암, 짧은 흰 하이라이트
- Mood: 경쾌하고 친근하며 과장되지 않은 표정 언어
- Match existing assets: 제공된 어린이 참조의 선, 4~4.5등신, 눈과 홍조 표현

## Alpha And Canvas Rules

- Output format: PNG
- Background: 완전 투명
- Body framing: 전신, 머리와 손과 발이 모두 보임
- Margins: 머리 위와 발 아래 포함 충분한 투명 여백
- Opacity: 캐릭터와 의상 전체 완전 불투명
- Shadows: 바닥이나 배경 그림자 없음

## Negative Constraints

- Do not change: 얼굴, 피부톤, 헤어, 의상, 팔레트, 이름표, 비율
- Do not include: 배경, 다른 인물, 글자, UI, 소품, 워터마크
- Avoid: 실사, 3D, 플랫 벡터 UI, 검은 굵은 외곽선, 과장된 데포르메

## Pose Compatibility Notes

- Default facing: 화면 정면 또는 중앙을 향한 자연스러운 3/4 시선
- Speech bubble side: 포즈 주변에 넉넉한 투명 공간
- Known target scenes: planner의 각 asset `usage_section_ids`
