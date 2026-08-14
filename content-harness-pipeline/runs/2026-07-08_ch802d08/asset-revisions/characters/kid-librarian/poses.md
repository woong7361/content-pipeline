# Kid Librarian Poses

## Pose Table

| Output file | Pose | Expression | Facing | Framing | Intended use | Prompt notes | Acceptance criteria |
|---|---|---|---|---|---|---|---|
| `kid_librarian_explaining.webp` | confident explaining, one open presenting hand and the other hand pointing diagonally to the viewer's upper-left | bright, confident, helpful | 3/4 toward screen center; reusable on right or left | full body | Used in `section_problem_intro` / `#s-problem` as `probKid`, `section_tutorial_clock` / `#s-tut`, and `section_popup_quiz` / `#s-quiz` as `quizKid` before the correct answer. | Generate this as the new character's explaining pose. Do not preserve the old explaining asset identity. The pointing index finger must clearly aim toward the image's upper-left corner, not upper-right. | Same new textual identity from `design.md`; full body; transparent background; mint star hair clips, no glasses, teal vest, mustard skirt, yellow book satchel visible; no scene background or extra characters; direction QA passes for viewer upper-left. |
| `kid_librarian_idle.webp` | relaxed standing idle, hands down or lightly ready at sides | attentive, friendly, ready to help | right-side placement should face slightly left toward center | full body | Initial/helper state in `section_mission_type_a` / `#s-a` as `aKid`, `section_mission_type_b` / `#s-b` as `bKid`, and `section_mission_type_c` / `#s-c` as `cKid`; restored after success/confused feedback in JS. | Calm and compact so center choices, board, and monitor stay clear. | Same new identity and outfit exactly; both hands visible; no old anchor traits; transparent background; full body with shoes. |
| `kid_librarian_success.webp` | joyful cheer or small jump, both arms raised | delighted, proud, celebratory | works on either left or right; face slightly toward center | full body with extra top margin | Used in `section_tutorial_success` / `#s-tutok`, correct feedback in `#s-a`, `#s-b`, `#s-c`, library repair in `section_repair_outro` / `#s-repair`, quiz correct state in `section_popup_quiz` / `#s-quiz`, and `section_final_certificate` / `#s-cert`. | Arms may rise above head, but keep the bob hair, mint clips, teal vest, mustard skirt, satchel, socks, and shoes intact. Sparkles may be included only as small opaque decorative marks around the character if they do not imply a background. | Same new identity; full body not cropped; raised hands fully visible; cheer pose reads at small CSS size; no old kid-librarian identity drift. |
| `kid_librarian_confused.webp` | thoughtful confused tilt, one hand on chin or near cheek | puzzled but gentle, not sad | right-side placement should face slightly left toward center | full body | Wrong-answer feedback in `section_mission_type_a` / `#s-a` as `aKid` and `section_mission_type_b` / `#s-b` as `bKid`. | Keep expression mild and encouraging for grade 2 learners. Avoid making the character look distressed or like a different child. | Same new identity and outfit; hand does not hide the face too much; full body; transparent background; no old asset traits. |
| `kid_librarian_proud.png` | proud repair-complete stance, one hand on waist and one hand making a V sign | proud, satisfied, heroic but childlike | left-side placement should face slightly right toward center | full body | Recommended optional replacement for `section_repair_outro` / `#s-repair`, matching the storyboard note that the kid librarian watches the restored library with one hand on waist and a V sign. The current HTML reuses `kid_librarian_success.webp`, so this pose needs integration only if generated. | Make the stance compact enough to sit beside the restored library scene and central plaque. One hand rests on the waist; the other makes a clear V sign near shoulder/head height. | Same new identity; full body; transparent background; no cropped V-sign hand; outfit fully opaque; reads as proud completion rather than generic cheer. |

## Batch Plan

| Batch | Files | Worker | Notes |
|---|---|---|---|
| 01 | `kid_librarian_explaining.webp`, `kid_librarian_idle.webp` | image prompt batch | Establish the new textual identity in the two most common helper states. |
| 02 | `kid_librarian_success.webp`, `kid_librarian_confused.webp` | image prompt batch | Feedback poses must preserve the new identity without borrowing old asset traits. |
| 03 | `kid_librarian_proud.png` | optional image prompt batch | Optional storyboard-accurate repair-complete pose for `#s-repair`; generate if we want to replace the current success-pose reuse. |

## HTML Scene Citations

- `section_problem_intro` / `#s-problem`: `kid_librarian_explaining.webp` appears as `probKid`, the helper kid who says she can fix the clock.
- `section_tutorial_clock` / `#s-tut`: `kid_librarian_explaining.webp` appears on the right while the first clock-reading repair is introduced.
- `section_tutorial_success` / `#s-tutok`: `kid_librarian_success.webp` appears on the left for the first repair completion.
- `section_mission_type_a` / `#s-a`: `aKid` starts as `kid_librarian_idle.webp`, switches to `success` on correct answers, switches to `confused` on wrong answers, then returns to idle.
- `section_mission_type_b` / `#s-b`: `bKid` starts as `kid_librarian_idle.webp`, switches to `success` on correct answers, switches to `confused` on wrong answers, then returns to idle.
- `section_mission_type_c` / `#s-c`: `cKid` starts as `kid_librarian_idle.webp`, switches to `success` when number blocks complete a reboot question, then returns to idle.
- `section_repair_outro` / `#s-repair`: `kid_librarian_success.webp` currently celebrates the restored library.
- `section_repair_outro` / `#s-repair`: optional `kid_librarian_proud.png` better matches the source document's "hand on waist + V sign" completion motion if the HTML is updated to use it.
- `section_popup_quiz` / `#s-quiz`: `kid_librarian_explaining.webp` presents the final quiz, then switches to `kid_librarian_success.webp` on the correct answer.
- `section_final_certificate` / `#s-cert`: `kid_librarian_success.webp` celebrates the final certificate.
