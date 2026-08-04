# Character Asset QA

## Accepted

- `student-idle.webp`: roller hangs below the screen-left wrist outside the thigh; no body overlap.
- `student-thinking.webp`: thinking hand and pose preserved; gripping wrist is clean.
- `student-volunteer.webp`: raised arm and hand preserved; gripping wrist is clean.
- All paint marks are irregular, outlined, and limited to teal overall fabric.
- All files are `1024 x 1536` RGBA WebP with zero-alpha corners and no floor shadow.
- All alpha-bbox y differences are within `0.02`; horizontal expansion is at most `30 px`.

## Needs Regeneration

None.

## Integration Notes

- Final files overwrite only `assets/preview-painter/student-*.webp`.
- The unmodified `assets/student-*.webp` source files remain the identity and pose anchors.
