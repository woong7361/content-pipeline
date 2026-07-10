# Character Pose Batch Intake

## Scope

- Create reusable character planning docs and image-generation prompts.
- Do not generate images in this pass.
- Do not integrate assets into `output/index.html` in this pass.

## User-Provided Target Artifacts

- Story/document source: `2학년_8차시(시간)_임상현_no_img.md`
- HTML target: `content-harness-pipeline/runs/2026-07-08_ch802d08/output/index.html`
- Existing asset folder: `content-harness-pipeline/runs/2026-07-08_ch802d08/output/assets/`

## Characters

1. `teacher`
   - Role: friendly librarian teacher.
   - Existing assets may be used as identity/style references.
   - Known issue: skirt/clothing alpha looks semi-transparent; regenerated assets must fix this.

2. `kid-librarian`
   - Role: player/helper kid librarian.
   - Identity source: new textual character design in `kid-librarian/design.md`.
   - Existing `kid_librarian_*.png` files are not identity anchors. They are only usage references and examples of the previous drift problem.

## Technical Contract

- Output planning files under this directory.
- Final character image targets should be full-body transparent PNGs unless a pose says otherwise.
- Character, clothing, hair, shoes, props, and body parts must be fully opaque.
- No background scenery, floor, text, watermark, or UI inside character PNGs.
- For `kid-librarian`, generate a new character from the textual identity spec rather than preserving any existing kid asset.

## Scene Use Targets

- Use the HTML sections in `output/index.html` as the target screen placement source.
- Use the story document as the canonical source for character roles, motions, and dialogue intent.
- Cite target scenes in each character's `poses.md`.
