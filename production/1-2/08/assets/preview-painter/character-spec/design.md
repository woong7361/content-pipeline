# Painter Student Design

## Source Of Truth

- Character id: `student-painter`
- Identity source: the three unmodified `assets/student-*.webp` files
- Usage target: `production/1-2/08` painter character assets

## Identity Invariants

- Same child in all poses: round face, warm light skin, black tousled hair with one upward tuft, navy eyes.
- Preserve each source pose, expression, body proportions, and full-body placement exactly.
- Never alter the thinking hand at the chin or the volunteer's raised arm.

## Outfit Invariants

- Orange T-shirt, teal overall shorts and bib/straps, yellow buttons, white socks, blue hook-and-loop sneakers.
- Painter prop: a small roller held only in the lowered hand, hanging below the wrist outside the thigh.
- Paint marks may occur only on teal overall fabric.

## Style Invariants

- 2D flat vector illustration with clean flat shading.
- Bold, even, medium-weight dark outlines; no photo, 3D, texture, or noise.
- Paint marks use fine dark outlines matching the base illustration.

## Alpha And Canvas Rules

- `1024 x 1536`, RGBA WebP.
- Fully transparent background and zero-alpha corners.
- No floor, cast shadow, contact shadow, scenery, text, or watermark.
- Preserve each source alpha-bbox y range within 0.02 normalized units.
- Horizontal prop expansion must remain within 0.03 normalized units of the source bbox.

## Negative Constraints

- No roller part may cross the torso, arm, shirt, or clothes.
- No white or angular chroma-key residue around the gripping wrist or fingers.
- No paint marks on orange shirt, skin, hair, socks, or shoes.
- No perfect circles, straight sprinkle bars, or outline-free confetti marks.
