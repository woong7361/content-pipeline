# Character Asset Planning QA

## Accepted Planning Outputs

- `teacher/design.md`
- `teacher/poses.md`
- `teacher/prompts/batch-01.md`
- `teacher/prompts/batch-02.md`
- `kid-librarian/design.md`
- `kid-librarian/poses.md`
- `kid-librarian/prompts/batch-01.md`
- `kid-librarian/prompts/batch-02.md`
- `kid-librarian/prompts/batch-03.md`

## QA Notes

- Teacher docs correctly use the existing teacher assets as identity/style references and explicitly call out the skirt alpha issue as a defect to fix.
- Kid librarian docs correctly use a new textual identity spec as the source of truth. Existing `kid_librarian_*.png` files are usage references and previous-failure examples only, not identity anchors.
- Both character specs require full-body transparent PNGs and fully opaque clothing, hair, body parts, shoes, and props.
- Pose tables cite the target HTML sections and storyboard intent.
- `kid_librarian_proud.png` was added as an optional storyboard-accurate repair-complete pose for `#s-repair`; it is not currently wired into `output/index.html`.

## Needs Attention Before Image Generation

| Item | Reason | Suggested action |
|---|---|---|
| `kid_librarian_proud.png` | Optional asset not referenced by current HTML. | Generate only if planning to update `#s-repair` from `kid_librarian_success.png` to `kid_librarian_proud.png`. |

## Integration Notes

- If regenerated images keep the same filenames as current assets, no HTML path changes are needed for the required teacher and kid explaining/idle/success/confused poses.
- If `kid_librarian_proud.png` is generated, update `#s-repair` to use it for the left-side kid character.
- After image generation, inspect every PNG on a dark and light background to catch transparent clothing, fringe, and identity drift.

## Generated Final Assets

Generated under `generated/final/` on 2026-07-09.

| File | Status |
|---|---|
| `teacher_worried.png` | Passed: RGBA, transparent corners, held magnifier, full-body. |
| `teacher_pointing.png` | Passed: RGBA, transparent corners, right-pointing pose, magnifier visible. |
| `teacher_happy.png` | Passed: RGBA, transparent corners, clapping pose, opaque skirt. |
| `kid_librarian_explaining.png` | Passed: RGBA, transparent corners, new textual identity, points to the viewer's upper-left after v2 regeneration. |
| `kid_librarian_idle.png` | Passed: RGBA, transparent corners, compact idle pose, new textual identity. |
| `kid_librarian_success.png` | Passed: RGBA, transparent corners, raised-hands success pose, new textual identity. |
| `kid_librarian_confused.png` | Passed: RGBA, transparent corners, mild confused-thinking pose, new textual identity. |
| `kid_librarian_proud.png` | Passed: RGBA, transparent corners, hand-on-waist plus V-sign pose, new textual identity. |

Raw chroma-key intermediates are retained under `generated/raw/`; use only `generated/final/` for integration.
