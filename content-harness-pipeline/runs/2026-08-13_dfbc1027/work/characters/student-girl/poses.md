# 여학생 주인공 Poses

## Pose Table

| Output file | Pose | Expression | Facing | Framing | Intended use | Prompt notes | Acceptance criteria |
|---|---|---|---|---|---|---|---|
| `student-girl-ready.webp` | relaxed ready stance, both hands loosely gathered in front | calm friendly closed-mouth smile | front | full body | random-practice helper | centered, symmetric weight, no props | exact identity, 4–4.5 heads, full body, clean transparent alpha |
| `student-girl-agreeing.webp` | one hand giving a clear thumbs-up | small friendly smile | gaze toward screen left | full body | intro/addition/subtraction agreement | extra breathing room on left, no jump or exaggerated cheer | exact same girl and outfit as ready pose, readable thumb, clean transparent alpha |

## Batch Plan

| Batch | Files | Worker | Notes |
|---|---|---|---|
| 01 | ready, agreeing | primary image generator | generate ready first, then use it as the identity anchor for agreeing |
