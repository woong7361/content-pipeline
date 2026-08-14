# 사서 선생님 Design

## Source Of Truth

- Character id: `char_librarian_teacher`
- Identity source: planner의 `characters[].identity` 텍스트가 최초 기준이며, 생성 후 `librarian_teacher_explaining.webp`를 형제 포즈의 시각 기준으로 사용한다.
- Reference files: 최초 생성 전에는 없음.
- Usage target: 초등 2학년 시간 학습용 단일 HTML의 설명·당황·축하 상태.

## Identity Invariants

- Age/read: 친절하고 안정감 있는 성인 여성 사서 선생님.
- Face shape: 둥근 타원형 얼굴, 작은 둥근 코, 얇은 미소형 입.
- Hair: 짙은 밤색 턱선 길이 단발, 왼쪽 가르마, 끝이 안쪽으로 둥글게 말림.
- Eyes: 짙은 갈색의 둥근 눈, 짧고 완만한 눈썹, 청록색 둥근 테 안경.
- Skin tone: 밝은 황갈색.
- Body proportions: 약 5.5등신의 안정적인 성인 여성 체형.
- Distinctive traits: 청록색 둥근 테 안경과 왼쪽 가슴의 작은 책 모양 명찰.

## Outfit Invariants

- Main outfit: 아이보리 셔츠 위 청록색 무릎 길이 앞치마 원피스, 갈색 허리 벨트.
- Colors: 아이보리, 밝은 청록, 짙은 밤색, 따뜻한 갈색.
- Accessories: 청록색 둥근 테 안경, 왼쪽 가슴 책 모양 명찰.
- Footwear: 짙은 갈색 낮은 굽 신발.
- Props allowed: 설명 포즈의 돋보기만 허용.
- Props forbidden: 시계, 책, 말풍선, 폭죽 및 포즈 목적과 무관한 소품.

## Style Invariants

- Rendering style: 밝은 교육용 게임에 맞는 완성도 높은 2D 디지털 스토리북 일러스트. 평면 벡터 UI가 아닌 부드러운 불투명 색면과 미세한 회화적 질감.
- Line/edge treatment: 둥글고 안정적인 중간 굵기의 짙은 갈색 외곽선, 작은 화면에서도 즉시 읽히는 단순화된 실루엣.
- Lighting: 도서관 창의 부드러운 확산광을 연상시키는 좌상단 광원, 짧고 부드러운 내부 음영. 배경 투사 그림자는 없음.
- Proportions: 모든 포즈에서 같은 5.5등신, 같은 머리 크기와 어깨 폭.
- Mood: 밝고 친근하며 위협적이지 않은 감정 과장.
- Match existing assets: 세 포즈는 동일한 팔레트, 선 굵기, 색면 질감, 조명 방향을 공유한다.

## Alpha And Canvas Rules

- Output format: PNG with alpha.
- Background: 투명 배경만 허용.
- Body framing: 설명·축하는 전신, 당황은 허리 위 반신.
- Margins: 머리, 손, 발, 돋보기 주변에 충분한 안전 여백.
- Opacity: 캐릭터, 옷, 머리, 안경, 신발, 소품, 모든 신체 부위는 완전 불투명.
- Shadows: 캐릭터 내부의 부드러운 음영만 허용하고 바닥·접촉 그림자는 금지.

## Negative Constraints

- Do not change: 얼굴형, 피부톤, 머리 모양과 색, 안경, 의상, 명찰, 체형, 연령감.
- Do not include: 배경, 추가 인물, 텍스트, 말풍선, 시계, 바닥, 워터마크.
- Avoid: 실사, 3D 렌더, 플랫 벡터 UI, SVG 아이콘풍, 과도한 원근, 잘린 신체, 반투명 옷과 신체, 공포스러운 표정.

## Pose Compatibility Notes

- Default facing: 화면 오른쪽 배치에 맞춰 몸과 시선이 화면 왼쪽의 학습 영역으로 자연스럽게 향한다.
- UI-safe hand direction: 설명 포즈의 빈손은 왼쪽 위를 가리킨다.
- Speech bubble side: 캐릭터 왼쪽·상단에 말풍선과 학습 UI가 놓일 수 있다.
- Important screen clearances: 손끝·돋보기·머리·발이 캔버스 경계와 닿지 않는다.
- Known target scenes: `activity1_scene2_problem`, `activity1_scene3_tutorial`, `activity1_scene4_success`, `activity2_scene_a`, `activity2_scene_b`, `activity2_scene_c`, `activity2_scene4_outro`, `activity3_scene1_story`, `activity3_scene3_certificate`.
