# 꼬마 사서 Design

## Source Of Truth

- Character id: `little_librarian`
- Identity source: planner `characters[].identity` and the generated idle pose
- Reference files: `output/assets/little_librarian_idle.webp`
- Usage target: activity 1 tutorial/success, activity 2 problem and outro scenes, activity 3 quiz/certificate

## Identity Invariants

- Age/read: elementary lower-grade child
- Face shape: round light-skinned face, large round dark-brown eyes, tiny dot nose, wide readable mouth
- Hair: dark-brown short bob below the ears, three rounded bang locks, right tip flicking outward
- Eyes: large, round, dark brown
- Skin tone: light
- Body proportions: 3.5-head picture-book child proportions with slightly enlarged head and hands
- Distinctive traits: exactly two tiny freckles on each cheek

## Outfit Invariants

- Main outfit: sky-blue short-sleeve shirt, mustard-yellow librarian vest, navy shorts
- Colors: sky blue, mustard yellow, navy, red, dark brown, white
- Accessories: red bow tie and small open-book badge on the vest's left chest
- Footwear: white socks and dark-brown low shoes
- Props allowed: none for this batch
- Props forbidden: all hand props

## Style Invariants

- Rendering style: warm sunlit children's picture-book illustration
- Line/edge treatment: softly rounded forms with consistent medium dark-brown outlines
- Lighting: soft daytime light from upper left, one-to-two-step cel shading
- Proportions: fixed 3.5-head child proportions
- Mood: bright, encouraging, game-like
- Match existing assets: all three poses share the idle pose as identity and style anchor

## Alpha And Canvas Rules

- Output format: PNG with alpha
- Background: transparent only
- Body framing: full body
- Margins: generous padding around head, hands, and feet
- Opacity: character, clothing, hair, shoes, and body fully opaque
- Shadows: no cast or contact shadow

## Negative Constraints

- Do not change: face, freckles, hair, age, proportions, outfit, palette, badge, line style, lighting
- Do not include: other people, scenery, text, speech bubbles, props, watermark
- Avoid: cropped limbs, malformed hands, semi-transparency, photorealism, 3D rendering, flat vector UI

## Pose Compatibility Notes

- Default facing: toward screen center
- UI-safe hand direction: keep raised gestures within the character canvas
- Speech bubble side: outside the cutout; no baked speech bubble
- Important screen clearances: preserve full-body margins for left, right, and foreground placement
- Known target scenes: all planner usage sections listed in `poses.md`
