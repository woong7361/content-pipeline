# 사서 선생님 Design

## Source Of Truth

- Character id: `librarian_teacher`
- Identity source: planner `characters[].identity` 텍스트 명세. 기존 캐릭터 기준 이미지는 없으며 이 문서가 인물 정체성 source of truth다.
- Style references: `teacher-idle.webp`, `teacher-praising.webp`, `indoor-classroom.webp` (얼굴·헤어·의상 복제 금지, 작화·동작·조명 언어만 사용)
- Usage target: 단일 HTML 교육 콘텐츠의 도입, 설명, 성공, 완료 장면

## Identity Invariants

- Age/read: 안정감 있는 성인 여성 사서
- Face shape: 부드러운 긴 타원형, 따뜻한 밝은 베이지 피부, 옅은 장밋빛 홍조
- Hair: 푸른 기가 아주 약한 짙은 흑갈색, 왼쪽 가르마, 귀가 드러나는 낮은 둥근 번, 관자놀이의 짧은 곡선 잔머리 한 가닥
- Eyes: 짙은 호박색의 큰 타원형 눈, 흰 하이라이트 두 점, 가는 아치형 눈썹
- Body proportions: 성인 여성 7~7.5등신, 곧고 안정적인 체형과 보통 어깨 폭
- Distinctive traits: 낮은 둥근 번과 왼쪽 가슴의 작은 황동 책갈피 브로치

## Outfit Invariants

- Main outfit: 아이보리 둥근 칼라 블라우스, 허리선 자두색 카디건, 종아리 중간 길이 짙은 숲색 A라인 스커트
- Colors: 아이보리, 짙은 자두색, 숲색, 짙은 갈색, 황동색
- Accessories: 왼쪽 가슴 작은 황동 책갈피 브로치
- Footwear: 짙은 갈색 로퍼
- Props allowed: idle pose에만 단순한 돋보기 한 개
- Props forbidden: 책, 시계, 땀 아이콘, UI 요소

## Style Invariants

- Rendering style: 따뜻한 마을 도서관 셀 일러스트
- Line/edge treatment: 캐릭터 외곽은 짙은 갈색 중간 굵기, 큰 색면과 읽기 쉬운 실루엣
- Lighting: 위에서 내려오는 부드러운 확산광, 밝은 면·중간 면·얕은 그림자의 2~3단계
- Proportions: 모든 pose에서 7~7.5등신과 동일한 머리·어깨·팔다리 비율 고정
- Mood: 따뜻하고 차분하며 교육적으로 신뢰감 있는 표정 언어
- Match existing assets: 동일 인물의 세 pose에서 얼굴, 번, 의상, 브로치, 색, 광원 방향을 고정

## Alpha And Canvas Rules

- Output format: PNG
- Background: 투명 배경만 허용
- Body framing: 머리, 손, 발, 돋보기가 잘리지 않는 전신
- Margins: 사방에 충분한 안전 여백
- Opacity: 인물, 의상, 머리, 신발, 소품과 모든 신체 부위는 완전 불투명
- Shadows: 바닥 그림자와 배경 그림자 없음

## Negative Constraints

- Do not change: 얼굴형, 피부톤, 눈동자색, 낮은 둥근 번, 의상 구조·색, 황동 책갈피 브로치, 성인 비율
- Do not include: 배경, 다른 인물, 글자, 워터마크, UI, 땀 아이콘, 소품성 장식
- Avoid: 실사, 3D, 수채화, 픽셀 아트, 검은색 굵은 외곽선, 과도한 표정 변형, 복잡하거나 기형적인 손가락

## Pose Compatibility Notes

- Default facing: 정면 또는 학습 대상 방향의 약한 3/4
- UI-safe hand direction: idle은 옆 학습 대상을 안내, worried는 오른쪽 위를 바라봄, praise는 가슴 앞 박수
- Speech bubble side: pose 바깥의 비어 있는 쪽에 HTML 말풍선을 배치
- Important screen clearances: worried는 오른쪽 시계·말풍선 공간 확보, 다른 pose는 좌우 배치 가능
- Known target scenes: `a1_scene2_problem`, `a1_scene3_tutorial`, `a1_scene4_success`, `a2_scene1_type_a`, `a2_scene2_type_b`, `a2_scene3_type_c`, `a2_scene4_outro`, `a3_scene1_gallery`, `a3_scene3_certificate`

