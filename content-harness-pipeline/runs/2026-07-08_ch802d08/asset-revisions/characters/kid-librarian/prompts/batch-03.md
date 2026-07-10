# Kid Librarian Prompt Batch 03

Do not use any existing `kid_librarian_*.png` file as an identity reference. Generate a new kid librarian from the textual identity below. Existing files are only filename/use-target references for the HTML.

Shared identity lock:

```text
New child librarian character: elementary-school child with warm light peach skin, rounded child face, large dark-brown eyes, deep black-brown shoulder-length bob hair with soft outward-curled ends, side-swept bangs, two small mint star hair clips on the viewer-left side, no glasses. Outfit: ivory short-sleeve blouse, teal sleeveless librarian capelet/vest with a small open-book badge, coral ribbon tie, mustard-yellow A-line skirt, yellow book-shaped crossbody satchel, cream socks, chestnut brown Mary Jane shoes. Polished 3D storybook educational game character, warm soft library lighting, compact full-body transparent PNG cutout, fully opaque character, no background, no floor, no scenery, no extra characters.
```

Shared negative prompt:

```text
Do not copy the old kid_librarian_explaining image. No round glasses, no orange polka-dot headband, no yellow smock with purple pockets, no gray vest, no orange neckerchief, no tan trousers, no short-haired boy replacement, no adult proportions, no teacher character, no speech bubble, no wall clock, no UI, no text, no background, no semi-transparent clothing or body parts.
```

## Prompt 01 - `kid_librarian_proud.png`

Intended HTML use:

- Optional replacement for `section_repair_outro` / `#s-repair`, where the source document says the kid librarian watches the restored library while placing one hand on the waist and making a V sign.

Generation prompt:

```text
Create a full-body transparent PNG of the same new kid librarian character in a proud repair-complete stance. She has warm light peach skin, rounded child face, large dark-brown eyes, deep black-brown shoulder-length bob hair with soft outward-curled ends, side-swept bangs, two small mint star hair clips on the viewer-left side, and no glasses. She wears an ivory short-sleeve blouse, teal sleeveless librarian capelet/vest with a small open-book badge, coral ribbon tie, mustard-yellow A-line skirt, yellow book-shaped crossbody satchel, cream socks, and chestnut brown Mary Jane shoes.

Pose: confident proud stance with one hand resting on her waist and the other hand raised near shoulder or head height making a clear V sign. Her expression is proud, bright, and satisfied, like a young helper who successfully restored the library with math. Face and torso turn slightly toward screen center for left-side placement. Full body from hair clips to shoes, V-sign hand fully visible, compact silhouette for use beside a central success plaque, clean cutout silhouette, safe transparent margin.

Style and technical: polished 3D storybook educational game character, warm soft library lighting, fully opaque character, transparent background only, no scenery, no floor, no UI, no text, no extra characters.
```

Acceptance checks:

- Same new identity as the other new kid-librarian poses.
- One hand is clearly on the waist and the other clearly forms a V sign.
- Full body and V-sign hand are not cropped.
- Transparent background only; clothing, hair, shoes, satchel, and body fully opaque.
