# 꼬마 사서 Poses

## Pose Table

| Output file | Pose | Expression | Facing | Framing | Intended use | Prompt notes | Acceptance criteria |
|---|---|---|---|---|---|---|---|
| `child_librarian_idle.png` | stable neutral standing pose, both arms relaxed naturally | comfortable smile | gentle 3/4 toward screen center | full-body | activity1 tutorial and activity2 lower-left waiting state | speech bubble clearance above and right; no gesture props | same locked identity; neutral pose; full body; clean alpha; no background |
| `child_librarian_volunteer.png` | chest open, one hand raised high to volunteer | confident smile | gentle 3/4 toward screen center and slightly upward | full-body | activity1 tutorial and activity3 popup quiz entrance | generous motion clearance above raised hand | same locked identity; exactly one raised hand; full body; clean alpha; no background |
| `child_librarian_success.png` | both arms raised in celebration, both feet slightly airborne | large joyful smile | front | full-body | activity1 success, activity2 correct-answer feedback, activity3 popup success | generous jump clearance above and below; no stars | same locked identity; readable jump; full body; clean alpha; no background |

## Batch Plan

| Batch | Files | Worker | Notes |
|---|---|---|---|
| 01 | all three pose files | primary agent | Generate idle first as the identity anchor, then derive the two action poses sequentially and compare all three during QA. |
