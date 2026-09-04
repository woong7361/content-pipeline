# 사서 선생님 Design

## Source Of Truth

- Character id: `librarian_teacher`
- Identity source: planner `characters[].identity` and `identity_context`; no existing identity image
- Reference files: `teacher-idle.webp`, `teacher-praising.webp`, `worker-idle.webp` are style/proportion references only, never identity copies
- Usage target: single-screen educational HTML scenes across activities 1–3

## Identity Invariants

- Age/read: adult female librarian, warm and dependable
- Face shape: soft oval, warm medium-light beige skin, pale peach blush, no glasses
- Hair: very dark brown-black, mid-back wavy hair, right-side part, low tie at nape, short side locks at both cheeks
- Eyes: large dark-brown ovals with two white highlights, thin gently curved eyebrows
- Body proportions: slim adult, about 7.25 heads tall, long limbs
- Distinctive traits: low-tied long wavy hair; ivory blouse, deep-teal waistcoat, burgundy skirt

## Outfit Invariants

- Main outfit: ivory long-sleeve blouse, deep-teal fitted waistcoat, mid-calf burgundy A-line skirt
- Colors: ivory, deep teal, burgundy, dark brown, warm beige, tiny gold trim
- Accessories: small rectangular library name badge on left chest
- Footwear: dark-brown loafers
- Props allowed: round magnifying glass only in `librarian-explaining`
- Props forbidden: all other props

## Style Invariants

- Rendering style: polished 2D educational character illustration matching the inspected Baek Seungyong references
- Line/edge treatment: medium dark-brown contour, rounded simplified forms, clean color fields
- Lighting: warm diffuse top light, one soft shadow step, one or two narrow highlights
- Proportions: adult 7–7.5-head reference language, fixed 7.25-head identity
- Mood: comfortable, readable, never melodramatic
- Match existing assets: all three outputs must read as the same woman, outfit, palette, lighting, and line weight

## Alpha And Canvas Rules

- Output format: PNG
- Background: genuine transparency only
- Body framing: full body, no crop
- Margins: clear head, feet, hands, and prop margins
- Opacity: character, clothing, hair, shoes, props, and body parts fully opaque
- Shadows: no floor or cast-ground shadow; only internal form shading

## Negative Constraints

- Do not change: face, hair, outfit, skin tone, age, proportions, badge side
- Do not include: scenery, floor, other characters, UI, text, watermark, unrequested props
- Avoid: photorealism, 3D, heavy cel shading, rough watercolor/crayon texture, exaggerated anime distortion

## Pose Compatibility Notes

- Default facing: front
- UI-safe hand direction: distressed opens toward screen-left; explaining gestures toward screen-right
- Speech bubble side: preserve open space above and in the direction of gaze/gesture
- Important screen clearances: no clipped fingers, hair, skirt hem, shoes, or magnifying glass
- Known target scenes: activities 1–3 as listed in planner usage sections

