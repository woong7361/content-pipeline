# 작업자 대표 Poses

## Pose Table

| Output file | Pose | Expression | Facing | Framing | Intended use | Prompt notes | Acceptance criteria |
|---|---|---|---|---|---|---|---|
| `worker-lead-idle.png` | relaxed standing idle | small relieved smile | front | full-body | intro, paint-ten | arms naturally at sides, gaze front | identity locked, full body, alpha background |
| `worker-lead-apologetic.webp` | slight bow, hands clasped at lower abdomen | mildly apologetic, eyebrow ends slightly lowered | front | full-body | intro beat 0 | restrained emotion, extra headroom | same identity, no crying or kneeling, alpha background |
| `worker-lead-explaining.png` | one arm extended with open hand toward screen right | small open mouth, attentive | front with gaze right | full-body | intro, paint-ten, addition-build, subtraction-build | wide clearance beyond pointing hand | same identity, correct hand direction, alpha background |

## Batch Plan

| Batch | Files | Worker | Notes |
|---|---|---|---|
| 01 | `worker-lead-idle.png` | root | establish identity anchor first |
| 02 | `worker-lead-apologetic.webp`, `worker-lead-explaining.png` | root | generate sequentially using accepted idle as identity reference |
