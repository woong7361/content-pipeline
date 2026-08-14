# 여 교사 Poses

| Output file | Pose | Expression | Facing | Framing | Intended use | Acceptance criteria |
|---|---|---|---|---|---|---|
| `output/assets/teacher-idle.webp` | relaxed standing idle, arms naturally down | comfortable small smile | front | full body | shape-hunt, free-drawing | same locked identity, full body, transparent background, no props |
| `output/assets/teacher-explaining.webp` | one open palm at chest height indicating screen-right, other arm relaxed | small open speaking mouth | gaze right | full body | shape-hunt, shape-count, activity-one-bridge, free-drawing | same locked identity, readable open hand, clear space to right, transparent background |

## Batch Plan

- Batch 01: generate idle first as the identity anchor, then generate explaining with idle as the batch identity reference.
