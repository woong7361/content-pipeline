# Painter Student Poses

## Pose Table

| Output file | Pose | Expression | Facing | Framing | Prompt notes | Acceptance criteria |
|---|---|---|---|---|---|---|
| `student-idle.webp` | source idle stance | gentle smile | front | full-body | lowered screen-left hand grips roller; roller hangs outside thigh | source pose/identity unchanged; roller never overlaps body |
| `student-thinking.webp` | source thinking pose | thoughtful | slight three-quarter | full-body | chin hand untouched; lowered screen-right hand grips roller | chin hand untouched; clean wrist alpha; roller outside thigh |
| `student-volunteer.webp` | source volunteering pose | cheerful | front | full-body | raised arm untouched; lowered screen-right hand grips roller | raised arm untouched; clean wrist alpha; roller outside thigh |

## Batch Plan

| Batch | Files | Worker | Notes |
|---|---|---|---|
| 01 | all three files | primary agent | one identity-preserving edit per pose, then technical and visual QA |
