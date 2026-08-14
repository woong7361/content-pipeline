# 꼬마 사서 Poses

## Pose Table

| Output file | Pose | Expression | Facing | Framing | Intended use | Prompt notes | Acceptance criteria |
|---|---|---|---|---|---|---|---|
| `little_librarian_idle.png` | confident volunteering stance, one hand raised | small confident smile | toward center/right | full-body | tutorial and activity 2 idle state | canonical identity anchor | same identity, full body, transparent background, no prop |
| `little_librarian_success.png` | jumping with both arms raised | bright eyes and large joyful smile | toward center | full-body | correct-answer and tutorial success feedback | preserve idle identity; airborne with no shadow | same identity, full body, transparent background, hands and feet intact |
| `little_librarian_proud.webp` | one hand on hip, other hand making V sign | proud bright smile | toward center | full-body | restoration, final quiz, certificate | preserve idle identity; clear V gesture | same identity, full body, transparent background, no prop |

## Batch Plan

| Batch | Files | Worker | Notes |
|---|---|---|---|
| 01 | all three pose files | primary agent | generate idle first, then use it as identity reference for success and proud |
