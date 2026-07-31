# 꼬마 사서 Design

## Source Of Truth

- Character id: `char_child_librarian`
- Identity source: planner `characters[].identity` and `identity_context`; no reference image exists in this batch.
- Reference files: none
- Usage target: elementary-grade interactive library repair adventure, tutorial and lower-left screen placement

## Identity Invariants

- Age/read: early-elementary child
- Face shape: round face, large dark-brown circular eyes, short dark eyebrows, small button nose
- Hair: short dark-brown bowl cut, three-part fringe at center forehead, ears visible
- Skin tone: light peach
- Body proportions: small child build, head-to-body ratio about 1:4
- Distinctive traits: three-part fringe, yellow bow tie, small teal librarian cap

## Outfit Invariants

- Main outfit: light sky-blue shirt; dark teal shorts and suspenders
- Colors: sky blue, teal, yellow, white, brown
- Accessories: yellow bow tie; small teal librarian cap
- Footwear: white socks; brown round-toe shoes
- Props allowed: none
- Props forbidden: speech bubble, punctuation, text, stars, fireworks

## Style Invariants

- Rendering style: polished raster children's storybook illustration, not flat vector and not 3D
- Line/edge treatment: rounded stable medium-weight dark-brown outline; simplified readable silhouette
- Lighting: soft daylight from a library window; weak cel shading; short soft internal shadows; no cast shadow outside character
- Proportions: early-elementary 1:4 head-to-body ratio
- Mood: warm, bright, game-like, encouraging
- Match existing assets: same cream/wood/teal/sky-blue/yellow world palette and unified rendering across all three poses

## Alpha And Canvas Rules

- Output format: PNG
- Background: transparent after chroma-key removal
- Body framing: full body, head/hands/feet fully visible
- Margins: generous clear margin, especially above raised hands and below jumping feet
- Opacity: character, clothing, hair, hat, socks, shoes, and all body parts fully opaque
- Shadows: no cast shadow, no floor plane

## Negative Constraints

- Do not change: face, hairstyle, skin tone, outfit, palette, proportions, hat, bow tie
- Do not include: additional people, question marks, speech bubbles, text, background, scenery, floor, watermark
- Avoid: photorealism, 3D render, flat vector UI, SVG style, icon kit, CSS component, plain geometric panel, neon lighting

## Pose Compatibility Notes

- Default facing: front or gentle 3/4 toward screen center
- UI-safe hand direction: keep all hands away from crop edge
- Speech bubble side: external HTML bubble may appear to the right; do not draw it
- Important screen clearances: full-body vertical cutout with safe space around gesture
- Known target scenes: activity1 tutorial/success, activity2 global and type A/B/C, activity3 popup quiz
