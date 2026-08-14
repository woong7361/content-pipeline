# 작업자 대표 Design

## Source Of Truth

- Character id: `worker-lead`
- Identity source: planner `characters[].identity`; no prior identity image exists in this batch.
- Reference files: `source/baek-seungyong/assets/characters/worker-idle.webp`, `teacher-idle.webp`, `teacher-praising.webp` are style-only references and must not donate identity or clothing.
- Usage target: intro, paint-ten, addition-build, subtraction-build sections in one HTML learning screen.

## Identity Invariants

- Age/read: adult male construction worker.
- Face shape: softly angular square face with warm tan skin and a rounded nose tip.
- Hair: short dark-brown curls; exactly three visible fringe tufts above the forehead.
- Eyes: dark-brown oval eyes; thick nearly horizontal eyebrows.
- Body proportions: 7–7.5 heads tall, broad shoulders, sturdy but not exaggerated build.
- Distinctive traits: small orange circle centered on the front of a white safety helmet.

## Outfit Invariants

- Main outfit: white safety helmet, orange safety vest, dark-gray work jacket and trousers.
- Colors: white, safety orange, dark charcoal gray, brown.
- Accessories: gray work gloves.
- Footwear: brown work boots.
- Props allowed: none in this batch.
- Props forbidden: hammer, tools, paint can.

## Style Invariants

- Rendering style: polished Korean elementary-learning character illustration matching the inspected Baek Seungyong references.
- Line/edge treatment: medium dark-brown character outline, rounded clean silhouette, restrained interior lines.
- Lighting: clear daylight from above, two or three flat shading steps, one narrow highlight.
- Proportions: adult 7–7.5 heads tall; never childlike or SD.
- Mood: warm, friendly, emotionally legible without manga exaggeration.
- Match existing assets: consistent eyes, facial simplicity, line weight, flat shading, and gesture language across all three poses.

## Alpha And Canvas Rules

- Output format: PNG with alpha.
- Background: transparent only after chroma-key removal.
- Body framing: full body with helmet and both boots visible.
- Margins: generous padding on every side; additional right-side clearance for the explaining pose and headroom for the apologetic pose.
- Opacity: character, clothes, helmet, gloves, hair, and boots fully opaque.
- Shadows: no floor, contact shadow, cast shadow, or reflection.

## Negative Constraints

- Do not change: face, skin tone, hair, helmet mark, outfit, footwear, body proportions.
- Do not include: extra person, tool, scenery, floor, text, watermark.
- Avoid: photorealism, copied blue-shirt/yellow-helmet reference identity, exaggerated muscles, dramatic cel shading, vector icon or 3D rendering.

## Pose Compatibility Notes

- Default facing: front.
- UI-safe hand direction: explaining hand points toward screen right.
- Speech bubble side: above the head for apologetic; right-side content clearance for explaining.
- Important screen clearances: never crop helmet, fingers, or boots.
- Known target scenes: intro dialogue, paint explanation, addition guidance, subtraction guidance.
