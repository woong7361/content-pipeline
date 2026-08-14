# Character Asset QA

## Accepted

- `worker-lead-idle.png`: identity anchor is full-body, front-facing, evenly padded, and visually matches the required reference style without copying reference clothing or identity.
- `worker-lead-apologetic.webp`: same identity and outfit; slight bow, clasped hands, restrained apology, and extra headroom are present.
- `worker-lead-explaining.png`: same identity and outfit; open hand, gaze, and clear space correctly direct attention toward screen right.
- All three files are 1024×1536 `Format32bppArgb` PNGs with zero-alpha corners and no text, scenery, tools, extra characters, or clipped body parts.

## Needs Regeneration

| File | Reason | Suggested fix |
|---|---|---|
| None | — | — |

## Integration Notes

- Keep consistent display height across poses; the apologetic pose naturally occupies less vertical space because of the bow.
- Use the explaining pose on the left side of the learning target so its open hand and gaze lead toward the content.
