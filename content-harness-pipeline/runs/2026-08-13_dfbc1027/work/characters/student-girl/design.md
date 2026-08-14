# 여학생 주인공 Design

## Source Of Truth

- Character id: `student-girl`
- Identity source: planner `characters[].identity` textual specification
- Reference files: `student-idle.webp`, `teacher-idle.webp`, `teacher-praising.webp` are style-only anchors; their identities must not be copied
- Usage target: single-screen elementary math learning content

## Identity Invariants

- Age/read: Korean elementary lower-grade girl
- Face shape: round face, light peach skin, small nose, shallow left-cheek dimple when smiling
- Hair: black shoulder-length hair in two low braids, coral round hair ties
- Eyes: large dark plum oval eyes with one or two white highlights
- Body proportions: childlike 4–4.5 heads tall, large head and short limbs
- Distinctive traits: two low braids with coral ties and left-cheek dimple

## Outfit Invariants

- Main outfit: white-and-sky-blue striped short-sleeve T-shirt, raspberry painter apron, dark navy leggings
- Footwear: mustard sneakers
- Props allowed: none
- Props forbidden: paint can, brush, UI objects

## Style Invariants

- Rendering style: clean polished Korean educational character illustration matching the inspected Baek Seung-yong references
- Line/edge treatment: medium dark-brown character outline, rounded clear silhouette, no vector-kit appearance
- Lighting: daylight from above, two or three flat shading steps, narrow highlights, soft low-contrast shadow only on the character
- Mood: friendly and calm; emotion shown mostly with brows and mouth corners
- Match existing assets: both poses must depict the exact same girl, outfit, palette, proportions, line weight, and lighting

## Alpha And Canvas Rules

- Output format: PNG RGBA
- Background: transparent only
- Body framing: full body with head, hands, and shoes fully visible
- Margins: generous even padding; matching foot baseline and scale across poses
- Opacity: character and all clothing fully opaque
- Shadows: no cast or contact shadow outside the silhouette

## Negative Constraints

- Do not change: face, hair, braids, hair ties, eyes, skin tone, outfit, shoes, age, body proportions
- Do not include: text, watermark, scenery, floor, extra person, paint can, prop
- Avoid: photorealism, 3D, watercolor, exaggerated SD proportions or celebration, copied reference-character identity

## Pose Compatibility Notes

- Default facing: ready pose faces front; agreeing pose keeps the torso readable and looks toward screen left
- UI-safe hand direction: agreeing thumb-up hand must remain inside the silhouette with clear fingers
- Important screen clearances: preserve space toward screen left in the agreeing asset
- Known target scenes: random-practice, intro, addition-build, subtraction-build
