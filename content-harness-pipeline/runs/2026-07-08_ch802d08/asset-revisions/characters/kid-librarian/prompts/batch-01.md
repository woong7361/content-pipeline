# Kid Librarian Prompt Batch 01

Do not use any existing `kid_librarian_*.png` file as an identity reference. Generate a new kid librarian from the textual identity below. Existing files are only filename/use-target references for the HTML.

Shared identity lock for every prompt:

```text
New child librarian character: elementary-school child with warm light peach skin, rounded child face, large dark-brown eyes, deep black-brown shoulder-length bob hair with soft outward-curled ends, side-swept bangs, two small mint star hair clips on the viewer-left side, no glasses. Outfit: ivory short-sleeve blouse, teal sleeveless librarian capelet/vest with a small open-book badge, coral ribbon tie, mustard-yellow A-line skirt, yellow book-shaped crossbody satchel, cream socks, chestnut brown Mary Jane shoes. Polished 3D storybook educational game character, warm soft library lighting, compact full-body transparent PNG cutout, fully opaque character, no background, no floor, no scenery, no extra characters.
```

Shared negative prompt:

```text
Do not copy the old kid_librarian_explaining image. No round glasses, no orange polka-dot headband, no yellow smock with purple pockets, no gray vest, no orange neckerchief, no tan trousers, no short-haired boy replacement, no adult proportions, no teacher character, no speech bubble, no wall clock, no UI, no text, no background, no semi-transparent clothing or body parts.
```

## Prompt 01 - `kid_librarian_explaining.png`

Intended HTML use:

- `section_problem_intro` / `#s-problem`: `probKid` appears as the helper kid who says she can fix the clock.
- `section_tutorial_clock` / `#s-tut`: kid explains the first repair.
- `section_popup_quiz` / `#s-quiz`: kid presents the final quiz before switching to success on correct answer.

Generation prompt:

```text
Create a full-body transparent PNG of a new kid librarian character in a confident explaining pose. She is an elementary-school child with warm light peach skin, rounded child face, large dark-brown eyes, deep black-brown shoulder-length bob hair with soft outward-curled ends, side-swept bangs, two small mint star hair clips on the viewer-left side, and no glasses. She wears an ivory short-sleeve blouse, teal sleeveless librarian capelet/vest with a small open-book badge, coral ribbon tie, mustard-yellow A-line skirt, yellow book-shaped crossbody satchel, cream socks, and chestnut brown Mary Jane shoes.

Pose: bright helper introduction. One hand is open in a presenting gesture. The other hand is raised across the body with the index finger clearly pointing diagonally toward the viewer's upper-left corner of the image. The pointing direction must be visually unambiguous: the fingertip aims up-left in image coordinates, not up-right. Friendly confident smile, eyes bright, body in 3/4 view toward screen center. Keep hands clear of the face and central UI. Full body from hair clips to shoes, clean cutout silhouette, safe transparent margin.

Style and technical: polished 3D storybook educational game character, warm soft library lighting, fully opaque character, transparent background only, no scenery, no floor, no UI, no text, no extra characters.
```

Acceptance checks:

- Looks like the new textual identity, not any existing kid asset.
- Explaining gesture reads clearly at small CSS size and points to the viewer's upper-left.
- Hands, hair clips, satchel, skirt, socks, and shoes all remain visible.
- Transparent background and fully opaque character.

## Prompt 02 - `kid_librarian_idle.png`

Intended HTML use:

- `section_mission_type_a` / `#s-a`: `aKid` idle state while the student chooses matching analog clocks.
- `section_mission_type_b` / `#s-b`: `bKid` idle state while the student restores the reading-class schedule.
- `section_mission_type_c` / `#s-c`: `cKid` idle state while the student drags number blocks into the monitor.

Generation prompt:

```text
Create a full-body transparent PNG of the same new kid librarian character in a relaxed standing idle pose. She has warm light peach skin, rounded child face, large dark-brown eyes, deep black-brown shoulder-length bob hair with soft outward-curled ends, side-swept bangs, two small mint star hair clips on the viewer-left side, and no glasses. She wears an ivory short-sleeve blouse, teal sleeveless librarian capelet/vest with a small open-book badge, coral ribbon tie, mustard-yellow A-line skirt, yellow book-shaped crossbody satchel, cream socks, and chestnut brown Mary Jane shoes.

Pose: attentive ready-to-help idle stance, feet planted, shoulders relaxed, hands visible near her sides or lightly open. Friendly focused expression with a small confident smile. Face and torso turned 3/4 toward screen center, suitable for right-side placement facing left into the lesson UI. Compact silhouette so center choices, board, and monitor stay clear. Full body from hair clips to shoes, clean cutout silhouette, safe transparent margin.

Style and technical: polished 3D storybook educational game character, warm soft library lighting, fully opaque character, transparent background only, no scenery, no floor, no UI, no text, no extra characters.
```

Acceptance checks:

- Same new identity as explaining pose.
- Calm compact silhouette does not reach far into center UI.
- Full body and both shoes visible.
- Transparent background and fully opaque character.
