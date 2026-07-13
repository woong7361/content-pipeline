# Teacher Poses

## Pose Table

| Output file | Pose | Expression | Facing | Framing | Intended use | Prompt notes | Acceptance criteria |
|---|---|---|---|---|---|---|---|
| `teacher_pointing_v2.png` | confidently point toward image-right with one fully extended arm; hold the magnifying glass naturally in the other hand | warm, encouraging teaching smile | subtle three-quarter toward image-right | full-body | `index.html` scenes `#s-tut`, `#s-a`, `#s-b`, and `#s-c` | match `teacher_worried.png` exactly; readable index-finger gesture; keep fingertip inside safe margin | same identity and painterly style, correct hands, whole body visible, transparent background, all materials opaque |
| `teacher_happy_v2.png` | delighted success pose with both hands raised near shoulder/chest height in a small celebratory cheer; magnifying glass remains securely held in one hand | broad joyful smile, bright open eyes | frontal | full-body | `index.html` scenes `#s-tutok`, `#s-repair`, `#s-story`, and `#s-cert`; runtime success state for `#storyTeacher` | energetic but gentle; visibly happier than pointing pose; preserve outfit and silhouette | same identity and painterly style, clearly distinct happy pose, correct hands, whole body visible, transparent background, all materials opaque |

## Batch Plan

| Batch | Files | Worker | Notes |
|---|---|---|---|
| 01 | `teacher_pointing_v2.png`, `teacher_happy_v2.png` | primary agent | Generate sequentially against the same identity anchor to minimize style drift. |
