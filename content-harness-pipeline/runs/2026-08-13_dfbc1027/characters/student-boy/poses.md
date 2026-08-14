# 남학생 주인공 Poses

## Pose Table

| Output file | Pose | Expression | Facing | Framing | Intended use | Prompt notes | Acceptance criteria |
|---|---|---|---|---|---|---|---|
| `output/assets/student-boy-ready.webp` | relaxed ready stance; one hand on hip and the other naturally lowered | comfortable closed-mouth smile | front | full body | helper/default state in `shape-hunt`, `addition-build`, `random-practice` | feet planted; no prop; eyes forward | same locked identity; whole head, hands, and shoes visible; transparent background; all clothing opaque |
| `output/assets/student-boy-agreeing.webp` | one hand raised to shoulder height in agreement; other arm relaxed | bright smile with mouth only slightly open | body front, gaze screen left | full body | “네”, “도와드릴게요” response in `intro`, `shape-hunt`, `addition-build`, `subtraction-build` | calm readable gesture; no jump; extra space to screen left | same person and outfit as ready pose; hand readable; whole body visible; transparent background; all clothing opaque |

## Batch Plan

| Batch | Files | Worker | Notes |
|---|---|---|---|
| 01 | `student-boy-ready.webp`, `student-boy-agreeing.webp` | primary agent | Generate ready first, then use it as the identity anchor for agreeing; use the same inspected style references and chroma-key workflow. |
