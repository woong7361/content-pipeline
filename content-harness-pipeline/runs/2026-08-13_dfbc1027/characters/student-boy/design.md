# 남학생 주인공 Design

## Source Of Truth

- Character id: `student-boy`
- Identity source: planner `characters[].identity` textual specification; no prior generated identity image exists
- Reference files: `source/baek-seungyong/assets/characters/student-idle.webp`, `teacher-idle.webp`, `teacher-praising.webp` are style-only references and must not donate face, hair, or clothing identity
- Usage target: single-screen educational HTML for `shape-hunt`, `addition-build`, `random-practice`, `intro`, and `subtraction-build`

## Identity Invariants

- Age/read: Korean elementary lower-grade boy
- Face shape: round face, bright peach skin, small round nose
- Hair: dark chestnut short side-parted hair with one small cowlick at the crown
- Eyes: large blue-gray oval eyes with one or two white highlights
- Skin tone: bright peach
- Body proportions: 4–4.5 heads tall, child-sized large head with short limbs, never adult proportions
- Distinctive traits: one small star-shaped freckle on the character's right cheek and the single crown cowlick

## Outfit Invariants

- Main outfit: pale-yellow short-sleeve hoodie T-shirt, cobalt painter apron, beige shorts
- Colors: pale yellow, cobalt, beige, green
- Accessories: none
- Footwear: green Velcro sneakers
- Props allowed: none for this batch
- Props forbidden: paint roller, paint can, handheld tools, signs

## Style Invariants

- Rendering style: polished Korean educational character illustration matching the inspected Baek Seung-yong references
- Line/edge treatment: clean dark-brown medium outline, rounded silhouette, no sketch texture
- Lighting: daylight from above; two to three flat shading steps and narrow highlights only
- Proportions: 4–4.5 heads tall with larger round eyes than adult references
- Mood: friendly, calm, clearly readable for first graders
- Match existing assets: both poses must be the same boy with identical face, hair, outfit, palette, proportions, outline, and light direction

## Alpha And Canvas Rules

- Output format: PNG with alpha
- Background: transparent only after flat chroma-key removal
- Body framing: full body, head and both shoes entirely visible
- Margins: generous clear padding; extra gaze-side clearance for the agreeing pose
- Opacity: character, clothing, hair, shoes, and body parts fully opaque
- Shadows: no floor, contact shadow, or cast shadow

## Negative Constraints

- Do not change: identity invariants, outfit, palette, age, proportions, or signature cheek mark
- Do not include: additional people, scenery, floor, text, watermark, props
- Avoid: realistic photography, copied reference-student identity or orange/teal overalls, paint splashes, exaggerated SD/chibi head, dramatic cel shading, manga action effects, vector UI icon treatment

## Pose Compatibility Notes

- Default facing: front
- UI-safe hand direction: agreeing hand lifts to shoulder height; gaze toward screen left
- Speech bubble side: screen left for agreeing pose
- Important screen clearances: keep all fingers and shoes within frame; leave left-facing gaze room
- Known target scenes: `shape-hunt`, `addition-build`, `random-practice`, `intro`, `subtraction-build`
