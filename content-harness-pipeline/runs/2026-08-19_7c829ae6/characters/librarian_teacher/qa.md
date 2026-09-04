# Character Asset QA

## Accepted

- `output/assets/librarian-idle.png`: same locked identity, neutral front pose, complete full-body crop, no props or text.
- `output/assets/librarian-distressed.png`: same face, hair, outfit, palette, and proportions; clear up-left worry gesture with one sweat drop; enclosed background gap corrected to alpha.
- `output/assets/librarian-explaining.png`: same face, hair, outfit, palette, and proportions; clear rightward teaching gesture; magnifying-glass lens corrected to alpha.
- All three files are 1024×1536 PNGs with `Format32bppArgb` and transparent corner pixels.

## Needs Regeneration

| File | Reason | Suggested fix |
|---|---|---|
|  |  |  |

## Integration Notes

- Full-body crop, opaque character surfaces, directional safe zones, and identity continuity were visually checked on a colored backing.
- Built-in generation supplied a baked light checker pattern, so alpha was repaired after generation without changing the character art.
