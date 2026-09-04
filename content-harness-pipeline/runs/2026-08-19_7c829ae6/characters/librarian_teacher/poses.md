# 사서 선생님 Poses

## Pose Table

| Output file | Pose | Expression | Facing | Framing | Intended use | Prompt notes | Acceptance criteria |
|---|---|---|---|---|---|---|---|
| `librarian-idle.png` | relaxed standing idle | neutral small smile | front | full-body | identity anchor and neutral helper state | arms relaxed at sides, empty hands | same locked identity, full body, transparent, opaque |
| `librarian-distressed.png` | worried head-hold | inner brows raised, small open mouth | body leans and gaze up-left | full-body | activity 1 problem reaction | both hands hold head, one sweat drop, open space left | same locked identity, readable worry without fear, transparent |
| `librarian-explaining.png` | magnifier-and-point-right | calm smile | gaze right | full-body | tutorial, activity 2, storybook guidance | one round magnifier, other hand points gently right, no face overlap | same locked identity, clear prop and gesture, transparent |

## Batch Plan

| Batch | Files | Worker | Notes |
|---|---|---|---|
| 01 | all three poses | primary agent | sequential generation; idle becomes the identity anchor for later poses |

