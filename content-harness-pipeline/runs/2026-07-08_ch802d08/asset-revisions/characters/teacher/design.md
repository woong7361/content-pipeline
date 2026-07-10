# Teacher/Librarian Design

## Source Of Truth

- Character id: `teacher`
- Identity source: Existing teacher assets are the visual identity anchors.
- Reference files:
  - `output/assets/teacher_worried.png`
  - `output/assets/teacher_pointing.png`
  - `output/assets/teacher_happy.png`
- Usage target: `content-harness-pipeline/runs/2026-07-08_ch802d08/output/index.html`
- Lesson context: `2학년_8차시(시간)_임상현_no_img.md`, a grade 2 time-learning library repair mission.

## Identity Invariants

- Age/read: Warm young adult librarian teacher, friendly and trustworthy for elementary learners.
- Face shape: Soft rounded face, gentle cheeks, small nose, expressive eyebrows.
- Hair: Medium brown hair gathered in a high rounded bun, loose side wisps around the face.
- Eyes: Large warm brown eyes behind round thin-rimmed glasses.
- Skin tone: Fair warm skin with soft blush.
- Body proportions: Full-body stylized educational character, slightly large head and eyes, approachable proportions.
- Distinctive traits: Round glasses, high bun, coral neck scarf, cream cardigan, teal floral skirt, librarian name badge, magnifying glass.

## Outfit Invariants

- Main outfit: Cream cable-knit cardigan over a white blouse with a scalloped collar, coral scarf tied at the neck, brown belt, teal A-line midi skirt with small floral pattern, cream socks, brown Mary Jane shoes.
- Colors: Cream cardigan, white blouse, coral scarf, teal skirt, brown belt/shoes, gold/brass name badge and magnifying glass rim.
- Accessories: Round glasses, name badge, magnifying glass.
- Footwear: Brown Mary Jane shoes with cream socks.
- Props allowed: Magnifying glass for worried or pointing/inspection poses; optional small sweat drops only for worried pose.
- Props forbidden: Books, tablets, unrelated tools, clocks held in hand, new project-specific characters.
- Known issue to fix: The skirt and any clothing must not appear semi-transparent. Regenerated clothing must be fully opaque with only the outer background transparent.

## Style Invariants

- Rendering style: Polished 2D storybook/game character illustration, soft painterly texture, clean silhouette, warm educational app tone.
- Line/edge treatment: Crisp transparent PNG cutout with clean antialiased edges; no visible rectangular background.
- Lighting: Soft warm front lighting with subtle highlights, matching the existing assets.
- Proportions: Same full-body scale and visual weight as the 1024x1536 reference assets.
- Mood: Kind, expressive, lightly comedic when worried, encouraging when teaching, proud and grateful when happy.
- Match existing assets: Preserve the same face, hair volume, glasses size, outfit, color balance, and painterly detail across all poses.

## Alpha And Canvas Rules

- Output format: Transparent PNG, 1024x1536 recommended.
- Background: Transparent background only.
- Body framing: Full body, shoes visible, no cropped feet, no cut-off pointing hand.
- Margins: Leave safe transparent padding around hair, hands, props, and shoes for HTML placement and bob/cheer animations.
- Opacity: Transparent background only. The character, clothing, hair, shoes, props, and all body parts must be fully opaque. Do not make skirts, sleeves, hair, glasses, legs, or props semi-transparent. No ghosted fabric. No see-through clothing. No background color, no floor, no scenery.
- Shadows: No floor shadow or environmental cast shadow. A subtle internal painted shadow on the character is acceptable.

## Negative Constraints

- Do not change: Hair bun, round glasses, outfit, teal floral skirt, cream cardigan, coral scarf, brown shoes, magnifying-glass librarian identity.
- Do not include: Other characters, library background, wall clocks, UI panels, text, speech bubbles, badges with readable text, scenery, floor, furniture.
- Avoid: Cropped limbs, extra fingers, distorted glasses, changed hairstyle, changed skirt color, translucent skirt, low-resolution edges, inconsistent face age.

## Pose Compatibility Notes

- Default facing: 3/4 front view, generally facing toward the center of the screen.
- UI-safe hand direction: When placed on the left side of the HTML scene, pointing should direct attention toward the center/right content area.
- Speech bubble side: Teacher speech bubbles appear beside a left-positioned teacher in `#s-problem` and `#s-tut`; keep the head and upper torso readable and not too wide.
- Important screen clearances: Keep extended arms inside the canvas; preserve transparent padding so CSS animations do not clip hands or shoes.
- Known target scenes:
  - `#s-problem` / `section_problem_intro` / "고장 난 도서관 시계"
  - `#s-tut` / `section_tutorial_clock` / "꼬마 사서의 첫 수리"
  - `#s-tutok` / `section_tutorial_success` / "첫 번째 시계 수리 성공"
  - `#s-a` / `section_mission_type_a` / "유형 A: 엉망이 된 도서관 시계 맞추기"
  - `#s-c` / `section_mission_type_c` / "유형 C: 도서 대출 시스템 재부팅"
  - `#s-repair` / `section_repair_outro` / "수리 완료와 도서관 복구"
  - `#s-story` / `section_story_gallery` / "수리 이야기: 생활 속 시간"
  - `#s-cert` / `section_final_certificate` / "최종 완료와 인증"
