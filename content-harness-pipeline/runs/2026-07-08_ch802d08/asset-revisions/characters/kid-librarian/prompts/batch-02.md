# Kid Librarian Prompt Batch 02

Do not use any existing `kid_librarian_*.png` file as an identity reference. Generate a new kid librarian from the textual identity below. Existing files are only filename/use-target references for the HTML.

Shared identity lock for every prompt:

```text
New child librarian character: elementary-school child with warm light peach skin, rounded child face, large dark-brown eyes, deep black-brown shoulder-length bob hair with soft outward-curled ends, side-swept bangs, two small mint star hair clips on the viewer-left side, no glasses. Outfit: ivory short-sleeve blouse, teal sleeveless librarian capelet/vest with a small open-book badge, coral ribbon tie, mustard-yellow A-line skirt, yellow book-shaped crossbody satchel, cream socks, chestnut brown Mary Jane shoes. Polished 3D storybook educational game character, warm soft library lighting, compact full-body transparent PNG cutout, fully opaque character, no background, no floor, no scenery, no extra characters.
```

Shared negative prompt:

```text
Do not copy the old kid_librarian_explaining image. No round glasses, no orange polka-dot headband, no yellow smock with purple pockets, no gray vest, no orange neckerchief, no tan trousers, no short-haired boy replacement, no adult proportions, no teacher character, no speech bubble, no wall clock, no UI, no text, no background, no semi-transparent clothing or body parts.
```

## Prompt 01 - `kid_librarian_success.webp`

Intended HTML use:

- `section_tutorial_success` / `#s-tutok`: first repair completion.
- Correct feedback in `section_mission_type_a` / `#s-a`, `section_mission_type_b` / `#s-b`, and `section_mission_type_c` / `#s-c`.
- `section_repair_outro` / `#s-repair`: library repair completion unless optional proud pose is generated and integrated.
- `section_popup_quiz` / `#s-quiz`: final quiz correct answer.
- `section_final_certificate` / `#s-cert`: final certificate celebration.

Generation prompt:

```text
Create a full-body transparent PNG of the same new kid librarian character celebrating a correct answer. She has warm light peach skin, rounded child face, large dark-brown eyes, deep black-brown shoulder-length bob hair with soft outward-curled ends, side-swept bangs, two small mint star hair clips on the viewer-left side, and no glasses. She wears an ivory short-sleeve blouse, teal sleeveless librarian capelet/vest with a small open-book badge, coral ribbon tie, mustard-yellow A-line skirt, yellow book-shaped crossbody satchel, cream socks, and chestnut brown Mary Jane shoes.

Pose: joyful small jump or cheer with both arms raised high, delighted open smile, bright eyes, proud helpful energy. Keep her face turned slightly toward screen center so the pose works on either side of the screen. Allow a few tiny opaque golden sparkle marks near the character only if they remain separate from any background and do not obscure the silhouette. Full body from raised hands and hair clips to shoes, extra transparent top margin for CSS cheer animation.

Style and technical: polished 3D storybook educational game character, warm soft library lighting, fully opaque character, transparent background only, no scenery, no floor, no UI, no text, no extra characters.
```

Acceptance checks:

- Same new identity as explaining/idle poses.
- Raised hands, hair clips, satchel, and shoes are not cropped.
- Reads clearly as success at small on-screen size.
- Transparent background and fully opaque character.

## Prompt 02 - `kid_librarian_confused.webp`

Intended HTML use:

- `section_mission_type_a` / `#s-a`: wrong-answer feedback for analog-clock choices.
- `section_mission_type_b` / `#s-b`: wrong-answer feedback for reading-class schedule input.

Generation prompt:

```text
Create a full-body transparent PNG of the same new kid librarian character in a gentle confused-thinking pose. She has warm light peach skin, rounded child face, large dark-brown eyes, deep black-brown shoulder-length bob hair with soft outward-curled ends, side-swept bangs, two small mint star hair clips on the viewer-left side, and no glasses. She wears an ivory short-sleeve blouse, teal sleeveless librarian capelet/vest with a small open-book badge, coral ribbon tie, mustard-yellow A-line skirt, yellow book-shaped crossbody satchel, cream socks, and chestnut brown Mary Jane shoes.

Pose: mild confused-thinking feedback, head tilted slightly, one hand touching her chin or cheek, the other hand relaxed and visible. Eyebrows softly raised or knitted, eyes looking upward toward the problem area, expression puzzled but encouraging rather than sad or upset. Face and torso turn 3/4 toward screen center, suitable for right-side placement facing left. Full body from hair clips to shoes, clean cutout silhouette, safe transparent margin.

Style and technical: polished 3D storybook educational game character, warm soft library lighting, fully opaque character, transparent background only, no scenery, no floor, no UI, no text, no extra characters.
```

Acceptance checks:

- Same new identity as explaining/idle/success poses.
- Hand does not cover the eyes or too much of the face.
- Confusion feels mild and age-appropriate.
- Full body, transparent background, fully opaque clothing and body.
