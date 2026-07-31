# 사서 선생님 Design

## Source Of Truth

- Character id: `char_librarian`
- Identity source: planner `characters[].identity` 텍스트가 최초 기준이며, 먼저 생성하는 `librarian_explaining.png`를 이후 포즈의 시각 기준으로 사용한다.
- Reference files: 최초 생성 전에는 없음.
- Usage target: 초등 2학년 도서관 시간 학습 콘텐츠의 전신 조력자 캐릭터.

## Identity Invariants

- Age/read: 따뜻하고 신뢰감 있는 성인 여성 사서.
- Face shape: 부드러운 타원형 얼굴, 작은 둥근 코.
- Hair: 짙은 밤색 턱선 단발, 안쪽으로 말린 끝, 오른쪽 가르마.
- Eyes: 짙은 갈색의 둥근 눈, 짧고 완만한 눈썹.
- Skin tone: 따뜻한 베이지.
- Body proportions: 머리 대 몸 약 1:5.5의 성인 체형.
- Distinctive traits: 얇은 청록색 원형 안경, 왼쪽 가슴의 작은 금색 책 모양 배지.

## Outfit Invariants

- Main outfit: 크림색 긴팔 블라우스와 청록색 무릎길이 조끼 원피스.
- Colors: 크림색, 청록색, 짙은 밤색, 제한적인 금색 포인트.
- Accessories: 청록색 원형 안경, 금색 책 배지.
- Footwear: 짙은 갈색 낮은 굽 신발.
- Props allowed: explaining 포즈에만 둥근 돋보기.
- Props forbidden: 그 외 포즈의 돋보기, 말풍선, 문자, UI.

## Style Invariants

- Rendering style: 어린이 교육용 고급 raster storybook illustration. 벡터 UI나 3D가 아닌 부드러운 셀 음영의 디지털 삽화.
- Line/edge treatment: 둥글고 안정적인 중간 굵기 외곽선, 단순하고 명료한 전신 실루엣.
- Lighting: 왼쪽 위에서 들어오는 부드러운 낮 햇빛, 약한 셀 음영. 별도 바닥 그림자 없음.
- Proportions: 성인 여성 1:5.5 비율 고정.
- Mood: 밝고 경쾌하며 표정과 손동작을 즉시 읽을 수 있음.
- Match existing assets: 세 포즈에서 얼굴, 헤어, 안경, 의상, 배지, 색감, 비율을 동일하게 유지한다.

## Alpha And Canvas Rules

- Output format: PNG RGBA.
- Background: 투명 배경만 허용.
- Body framing: 머리, 손, 발, 소품이 잘리지 않는 전신 세로형.
- Margins: 머리·손·발 주변에 충분한 안전 여백.
- Opacity: 캐릭터, 의상, 머리, 안경, 신발, 돋보기와 모든 신체 부위는 완전 불투명.
- Shadows: 배경 또는 바닥에 닿는 그림자 없음. 캐릭터 내부 셀 음영만 허용.

## Negative Constraints

- Do not change: 얼굴형, 머리색과 길이, 피부톤, 안경, 의상, 배지, 신발, 신체 비율.
- Do not include: 추가 인물, 배경, 바닥, 말풍선, 글자, 워터마크, UI, 반투명 의상.
- Avoid: 실사, 3D, flat vector UI, SVG style, icon kit, 과도한 미세 장식, 강한 네온 조명.

## Pose Compatibility Notes

- Default facing: 완만한 3/4 정면.
- UI-safe hand direction: explaining은 화면 중앙인 왼쪽을 가리킨다.
- Speech bubble side: 캐릭터 왼쪽/화면 중앙 쪽을 비운다.
- Important screen clearances: 손 또는 머리 동작 방향에 넉넉한 여백을 둔다.
- Known target scenes: `activity1_problem`, `activity1_tutorial`, `activity1_success`, `activity2_type_a`, `activity2_type_b`, `activity2_type_c`, `activity2_outro`, `activity3_final`.
