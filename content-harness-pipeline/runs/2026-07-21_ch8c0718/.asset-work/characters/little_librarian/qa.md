# Character Asset QA

## Accepted

- `little_librarian_idle.png`: canonical identity, confident raised-hand pose, full-body crop, intact hands and feet, transparent corners, opaque clothing.
- `little_librarian_success.png`: same identity and outfit, readable airborne hooray pose, full-body crop, intact hands and feet, transparent corners, opaque clothing.
- `little_librarian_proud.png`: same identity and outfit, readable hand-on-hip and V-sign pose, full-body crop, intact hands and feet, transparent corners, opaque clothing.
- All outputs are 1024×1536 RGBA PNGs with zero-alpha corner pixels and consistent upper-left daylight, line weight, palette, freckles, bow tie, and open-book badge.

## Needs Regeneration

| File | Reason | Suggested fix |
|---|---|---|

## Integration Notes

- Idle and success poses are composed for lower-left placement; proud pose has safe margin for right-side and foreground placement.
- No text, speech bubbles, props, scenery, cast shadows, or gold success effects are baked into the cutouts.
