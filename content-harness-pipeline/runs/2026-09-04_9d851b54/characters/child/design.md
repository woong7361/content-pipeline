# 초등학생 아이 Design

## Source Of Truth

- Character id: `child`
- Identity source: planner `characters[].identity` 및 `identity_context`의 텍스트 명세
- Reference files: 없음
- Usage target: 경주 박물관 큰 수 학습 HTML의 대기·말하기 포즈

## Identity Invariants

- Age/read: 초등학생 연령감, 친근하고 호기심 많은 여자아이
- Face shape: 둥근 얼굴, 작은 둥근 코, 또렷한 미소
- Hair: 짙은 갈색 어깨 길이 머리, 양쪽 귀 아래 같은 높이의 양갈래, 짧은 앞머리
- Eyes: 짙은 갈색의 큰 타원형 눈
- Skin tone: 밝은 중간 피부톤
- Body proportions: 4.5등신, 작은 키, 둥근 손발
- Distinctive traits: 양갈래 끝의 작은 남색 리본

## Outfit Invariants

- Main outfit: 분홍색 단추 가디건, 흰색 둥근 칼라 셔츠, 무릎 길이 남색 주름치마
- Colors: 분홍·남색·흰색·짙은 갈색, 가디건의 둥근 노란 단추
- Accessories: 작은 남색 머리 리본
- Footwear: 흰 양말, 짙은 남색 운동화
- Props allowed: 없음
- Props forbidden: 모든 손 소품

## Style Invariants

- Rendering style: 따뜻한 경주 박물관 탐험 동화풍의 손그림 캐릭터 일러스트
- Line/edge treatment: 둥글고 안정적인 중간 굵기 외곽선, 단순화한 형태
- Lighting: 낮의 부드러운 확산광, 2~3단계 명암, 짧고 부드러운 그림자
- Proportions: 과도한 만화식 왜곡 없이 4.5등신 고정
- Mood: 밝고 친근하며 작은 화면에서도 표정이 즉시 읽힘
- Match existing assets: 두 포즈의 얼굴·헤어·의상·팔레트·비율·조명을 동일하게 유지

## Alpha And Canvas Rules

- Output format: PNG
- Background: 완전 투명
- Body framing: 머리부터 운동화 끝까지 보이는 전신
- Margins: 머리 위와 발 아래, 좌우 손끝 바깥에 안전 여백
- Opacity: 캐릭터, 옷, 머리카락, 신발, 리본, 신체 전부 완전 불투명
- Shadows: 바닥 그림자와 배경 그림자 없음

## Negative Constraints

- Do not change: 얼굴형, 피부톤, 양갈래 높이, 머리색, 의상, 단추와 리본, 비율
- Do not include: 배경 장면, 바닥, 소품, 텍스트, 워터마크
- Avoid: 실사, 3D, flat vector UI, 가는 장식선, 반투명 의상, 잘린 신체, 기형 손발

## Pose Compatibility Notes

- Default facing: 대기는 정면, 말하기는 몸은 거의 정면이며 시선은 화면 오른쪽
- UI-safe hand direction: 말하기 포즈의 한 손은 오른쪽 말풍선 방향으로 가볍게 듦
- Speech bubble side: 오른쪽
- Important screen clearances: 전신 실루엣 바깥 여백, 오른쪽 손과 시선 앞 여백
- Known target scenes: `s1-greeting`, `s1-admission`, `s2-interior`, `s4-dialogue`, `s5-dialogue-intro`, `s5-check-dialogue`, `s6-wrap-dialogue`
