# Kid Librarian Design

## Source Of Truth

- Character id: `kid-librarian`
- Identity source: New textual identity spec below. No existing kid-librarian image is an identity anchor.
- Reference files:
  - Usage references only: `content-harness-pipeline/runs/2026-07-08_ch802d08/output/assets/kid_librarian_explaining.png`, `kid_librarian_idle.png`, `kid_librarian_success.png`, `kid_librarian_confused.png`
  - These existing files show where the character appears and what pose filenames the HTML expects, but they must not be copied as the new identity.
- Usage target: HTML interactive lesson `content-harness-pipeline/runs/2026-07-08_ch802d08/output/index.html`, a grade 2 time lesson set in a village library repair mission.

## Identity Invariants

- Age/read: elementary-school child, cheerful "kid librarian" and player avatar for grade 2 learners.
- Face shape: rounded child face, soft cheeks, small rounded nose, bright approachable expression.
- Hair: deep black-brown shoulder-length bob with soft outward-curled ends, side-swept bangs, and two small mint star hair clips on the viewer-left side.
- Eyes: large dark-brown eyes with bright catchlights.
- Eyewear: no glasses.
- Skin tone: warm light peach skin with gentle blush.
- Body proportions: child proportions with a slightly larger head, short full-body figure, compact silhouette.
- Distinctive traits: mint star hair clips, shoulder-length bob, teal librarian capelet, yellow book-shaped crossbody satchel, bright helper energy.

## Outfit Invariants

- Main outfit: ivory short-sleeve blouse under a teal sleeveless librarian capelet/vest, mustard-yellow A-line skirt, book-shaped yellow crossbody satchel, coral ribbon tie at the collar.
- Colors: teal capelet/vest, ivory blouse, mustard skirt, coral ribbon, yellow satchel, cream socks, chestnut Mary Jane shoes, mint hair clips.
- Accessories: two mint star hair clips, small open-book badge on the teal vest, yellow book-shaped crossbody satchel.
- Footwear: chestnut brown Mary Jane shoes with cream socks.
- Props allowed: small book-shaped satchel, tiny opaque sparkle marks only for celebration poses if requested.
- Props forbidden: round glasses, orange polka-dot headband, yellow smock with purple pockets, gray vest, orange neckerchief, tan trousers, teacher cardigan, magnifying glass.

## Style Invariants

- Rendering style: polished 3D storybook educational game character, warm and playful.
- Line/edge treatment: clean transparent PNG cutout, soft painted detail, crisp antialiased silhouette.
- Lighting: warm library-like key light with subtle self-shading on the character only.
- Proportions: childlike, readable at small CSS character size, about 0.8x the teacher height in the target HTML.
- Mood: capable, upbeat, brave, and kind without looking older than an elementary child.
- Match existing assets: match the general storybook/game quality of the lesson, but do not copy any existing kid-librarian identity.

## Alpha And Canvas Rules

- Output format: transparent PNG planning target, portrait canvas around 1024 x 1536.
- Background: transparent background only.
- Body framing: full body from hair clips to shoes, with all fingers and feet visible.
- Margins: leave safe transparent margin around hair, raised hands, satchel, and shoes for CSS animation.
- Opacity: Transparent background only. The character, clothing, hair, shoes, props, and all body parts must be fully opaque. Do not make skirts, sleeves, hair, glasses, legs, or props semi-transparent. No ghosted fabric. No see-through clothing. No background color, no floor, no scenery.
- Shadows: subtle self-shadow or painted shading on the character is allowed, but no separate floor shadow.

## Negative Constraints

- Do not change: bob hair, mint star hair clips, no-glasses identity, teal vest/capelet, ivory blouse, mustard skirt, coral ribbon, yellow book satchel, Mary Jane shoes.
- Do not include: adult proportions, teacher character traits, extra classmates, extra project-specific characters, scenery, floor, wall clock background, speech bubbles, UI labels.
- Avoid: copying `kid_librarian_explaining.png` or the current idle/success/confused assets; round glasses; orange polka-dot bow headband; yellow smock with purple pockets; gray-blue vest; orange neckerchief; tan trousers; boyish short-hair replacement; unrelated face.

## Pose Compatibility Notes

- Default facing: 3/4 toward screen center. Right-side placements should face slightly left; left-side placements should face slightly right.
- UI-safe hand direction: pointing or presenting hands should leave central lesson UI clear; raised cheer hands need top margin for the `.cheer` animation.
- Speech bubble side: problem intro and tutorial use right-side kid placement with a bubble beside the kid's head; quiz uses left-side kid placement.
- Important screen clearances: keep full-body silhouette readable at `--kid-h` scale. Avoid wide props that collide with center clock, board, monitor, plaque, or certificate.
- Known target scenes:
  - `section_problem_intro` / `#s-problem`: kid enters as helper and speaks.
  - `section_tutorial_clock` / `#s-tut`: kid explains during first repair.
  - `section_tutorial_success` / `#s-tutok`: kid celebrates first repair.
  - `section_mission_type_a` / `#s-a`: idle, success, and confused states swap during clock-choice questions.
  - `section_mission_type_b` / `#s-b`: idle, success, and confused states swap during schedule input questions.
  - `section_mission_type_c` / `#s-c`: idle and success states swap during number-block system reboot.
  - `section_repair_outro` / `#s-repair`: kid celebrates library repair.
  - `section_popup_quiz` / `#s-quiz`: kid explains quiz and switches to success on correct answer.
  - `section_final_certificate` / `#s-cert`: kid celebrates final completion.
