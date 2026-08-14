# Prompt Batch 02: Teacher Happy

## Shared Identity And Style Reference

Use these existing assets as identity and style references:

- `content-harness-pipeline/runs/2026-07-08_ch802d08/output/assets/teacher_worried.webp`
- `content-harness-pipeline/runs/2026-07-08_ch802d08/output/assets/teacher_pointing.webp`
- `content-harness-pipeline/runs/2026-07-08_ch802d08/output/assets/teacher_happy.webp`

Generate the same teacher/librarian character: warm young adult librarian teacher, high rounded brown hair bun with loose wisps, round thin-rimmed glasses, large brown eyes, cream cable-knit cardigan, white blouse with scalloped collar, coral neck scarf, brown belt, teal A-line midi skirt with small floral pattern, cream socks, brown Mary Jane shoes, gold/brass name badge, and magnifying glass.

Strict alpha requirement: transparent background only. The character, clothing, hair, shoes, props, and all body parts must be fully opaque. Fix the existing skirt/alpha issue: the teal floral skirt must be solid opaque fabric, never translucent or ghosted. No see-through clothing. No background color, no floor, no scenery, no shadow on the ground.

Canvas: full-body transparent PNG, 1024x1536, shoes visible, clean antialiased cutout, safe padding around hair, hands, props, and feet.

## Prompt: `teacher_happy.webp`

Intended HTML use:

- `#s-problem` / `section_problem_intro` / "고장 난 도서관 시계", via JavaScript success transition to `teacher_happy.webp`
- `#s-tutok` / `section_tutorial_success` / "첫 번째 시계 수리 성공"
- `#s-repair` / `section_repair_outro` / "수리 완료와 도서관 복구"
- `#s-story` / `section_story_gallery` / "수리 이야기: 생활 속 시간"
- `#s-cert` / `section_final_certificate` / "최종 완료와 인증"

Prompt:

```text
Create a full-body transparent PNG of the same warm young adult librarian teacher character from the reference images. She has a high rounded medium-brown hair bun with loose side wisps, round thin-rimmed glasses, large warm brown eyes, fair warm skin, a cream cable-knit cardigan over a white blouse with a scalloped collar, a coral neck scarf, a brown belt, a teal A-line midi skirt with small floral flowers, cream socks, brown Mary Jane shoes, a small gold/brass name badge, and a librarian magnifying glass.

Pose: happy clapping congratulation pose for success and final thanks. She stands full-body in a 3/4 front view with a big warm smile, proud and relieved. Her hands are together near her chest in a clear clapping gesture. The magnifying glass may hang from the cardigan pocket or be tucked visibly at her side, matching the reference style. Keep the pose compact enough for both right-side success placement and left-side story-gallery placement.

Style: polished 2D storybook educational game illustration, warm soft painterly texture, crisp clean cutout edges, same proportions, face, outfit, colors, lighting, and visual weight as the reference teacher assets.

Alpha and opacity: transparent background only. The entire character must be fully opaque: skin, hair, glasses, cardigan, blouse, scarf, belt, skirt, socks, shoes, name badge, and magnifying glass. The teal floral skirt must be solid opaque fabric with visible floral pattern; no semi-transparent skirt, no ghosted fabric, no see-through clothing. No background, no floor, no scenery, no speech bubble, no clock, no UI, no text.
```

Negative prompt:

```text
different character, child, elderly, different hairstyle, no glasses, different outfit, waving pose, holding book, holding clock, background, floor, wall, furniture, text, speech bubble, UI, cropped feet, cropped hands, malformed hands, extra fingers, distorted glasses, translucent skirt, transparent clothing, ghosted fabric, semi-transparent body parts, low-resolution edges
```
