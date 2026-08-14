# Character Asset QA

## Accepted

- `output/assets/teacher-idle.webp`: same locked teacher identity, neutral front pose, full body and hands/feet visible.
- `output/assets/teacher-explaining.webp`: same locked teacher identity, calm open-mouth explanation, gaze and open palm directed screen-right with clear integration space.
- Both files are 1024×1536 RGBA PNGs with fully transparent corners, fully opaque character interiors, and no scenery, text, watermark, or UI.
- Hair, face, left-cheek beauty mark, lavender cardigan, dark teal pleated skirt, beige flats, and silver watch remain consistent across poses.

## Needs Regeneration

- None.

## Integration Notes

- Idle alpha bounding box: `(315, 66, 694, 1471)`.
- Explaining alpha bounding box: `(140, 66, 712, 1478)`; the remaining right-side transparent space supports the learning target.
