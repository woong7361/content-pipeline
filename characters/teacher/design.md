# Teacher Design

## Source Of Truth

- Character id: `teacher`
- Identity source: `teacher_worried.png` is the sole visual identity and style anchor.
- Reference files: `content-harness-pipeline/runs/2026-07-08_ch802d08/output/assets/teacher_worried.png`
- Usage target: reusable full-body educational web character assets

## Identity Invariants

- Age/read: warm adult female teacher or librarian, youthful and approachable
- Face shape: softly rounded oval face with a small chin and large expressive features
- Hair: rich chestnut-brown hair in a large, loosely braided high bun; side-swept fringe and a few soft face-framing strands
- Eyes: very large warm brown eyes with detailed lashes
- Skin tone: warm light peach
- Body proportions: stylized storybook proportions, slightly oversized head, slim adult full body
- Distinctive traits: thin round gold-brown glasses and highly expressive eyebrows

## Outfit Invariants

- Main outfit: ivory cable-knit cardigan over a white blouse, coral-orange dotted neck scarf, teal calf-length A-line skirt with small orange and yellow floral sprigs
- Colors: warm cream, coral, teal, chestnut brown, muted gold
- Accessories: rectangular gold name badge, brown belt with brass buckle, round glasses
- Footwear: cream ruffled socks and brown leather Mary Jane shoes
- Props allowed: brass-rimmed wooden-handled magnifying glass
- Props forbidden: books, pointer sticks, bags, hats, jewelry, or unrelated classroom objects

## Style Invariants

- Rendering style: polished hand-painted digital storybook illustration with softly modeled volume and fine material texture
- Line/edge treatment: refined dark warm-brown contours integrated into the painting; crisp silhouette without thick cartoon outlines
- Lighting: soft warm frontal studio light with gentle dimensional shading; no cast shadow
- Proportions: match the reference head-to-body ratio, facial scale, hand scale, and long skirt silhouette
- Mood: friendly, intelligent, expressive, suitable for young learners
- Match existing assets: preserve the richer painterly detail, nuanced face modeling, voluminous hair, cardigan knit, and floral skirt rendering of `teacher_worried.png`; do not imitate the flatter or narrower look of the old pointing/happy files

## Alpha And Canvas Rules

- Output format: PNG with alpha
- Background: transparent only
- Body framing: complete full body from bun to shoe soles, including extended hands and props
- Margins: generous transparent safe margin on every side; pointing fingertip must not touch the canvas edge
- Opacity: the character, clothing, hair, glasses, shoes, magnifying glass, and all body parts must be fully opaque
- Shadows: no floor, cast shadow, contact shadow, halo, or reflection

## Negative Constraints

- Do not change: face, hairstyle, glasses, outfit construction, outfit palette, floral pattern language, body proportions, or illustration technique
- Do not include: scenery, floor, text, watermark, extra props, extra fingers, duplicated limbs
- Avoid: semi-transparent fabric, pale fringe, black fringe, blurry hands, flat anime cel shading, 3D-rendered plastic surfaces, overly youthful child proportions

## Pose Compatibility Notes

- Default facing: frontal or subtle three-quarter view
- UI-safe hand direction: pointing arm extends toward image-right
- Speech bubble side: image-right for the pointing pose; either side for happy pose
- Important screen clearances: retain open space beyond the extended pointing finger and around raised hands
- Known target scenes: teaching/explanation state and success/celebration state

