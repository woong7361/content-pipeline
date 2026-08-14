# Character Asset QA

## Accepted

- `output/assets/student-boy-ready.webp`: accepted. Same locked identity, front-facing ready pose, full head/hands/shoes visible, RGBA 1024×1536, transparent corners, no visible chroma color.
- `output/assets/student-boy-agreeing.webp`: accepted. Same locked identity and outfit, readable shoulder-height raised hand, screen-left gaze, full head/hand/shoes visible, RGBA 1024×1536, transparent corners, no visible chroma color.

## Needs Regeneration

| File | Reason | Suggested fix |
|---|---|---|

## Integration Notes

- Display both poses at equal CSS height to preserve their shared 4–4.5-head child scale.
- The agreeing pose has additional screen-left gesture and gaze clearance; keep dialogue or adult-character staging on that side.
- Alpha bounding boxes leave safe padding on every side; character pixels, clothing, hair, shoes, and body parts remain opaque apart from antialiased silhouette edges.
