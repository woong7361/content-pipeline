# Prompt Batch 01: Teacher Worried And Pointing

## Shared Identity And Style Reference

Use these existing assets as identity and style references:

- `content-harness-pipeline/runs/2026-07-08_ch802d08/output/assets/teacher_worried.png`
- `content-harness-pipeline/runs/2026-07-08_ch802d08/output/assets/teacher_pointing.png`
- `content-harness-pipeline/runs/2026-07-08_ch802d08/output/assets/teacher_happy.png`

Generate the same teacher/librarian character: warm young adult librarian teacher, high rounded brown hair bun with loose wisps, round thin-rimmed glasses, large brown eyes, cream cable-knit cardigan, white blouse with scalloped collar, coral neck scarf, brown belt, teal A-line midi skirt with small floral pattern, cream socks, brown Mary Jane shoes, gold/brass name badge, and magnifying glass.

Strict alpha requirement: transparent background only. The character, clothing, hair, shoes, props, and all body parts must be fully opaque. Fix the existing skirt/alpha issue: the teal floral skirt must be solid opaque fabric, never translucent or ghosted. No see-through clothing. No background color, no floor, no scenery, no shadow on the ground.

Canvas: full-body transparent PNG, 1024x1536, shoes visible, clean antialiased cutout, safe padding around hair, hands, props, and feet.

## Prompt: `teacher_worried.png`

Intended HTML use:

- `#s-problem` / `section_problem_intro` / "고장 난 도서관 시계"
- Used for the opening crisis dialogue where the teacher is anxious about the broken library clock.
- Also used by the problem-scene reset JavaScript when the teacher returns to the worried state.

Prompt:

```text
Create a full-body transparent PNG of the same warm young adult librarian teacher character from the reference images. She has a high rounded medium-brown hair bun with loose side wisps, round thin-rimmed glasses, large warm brown eyes, fair warm skin, a cream cable-knit cardigan over a white blouse with a scalloped collar, a coral neck scarf, a brown belt, a teal A-line midi skirt with small floral flowers, cream socks, brown Mary Jane shoes, a small gold/brass name badge, and a librarian magnifying glass.

Pose: worried head-hold pose for a broken library clock crisis. She stands full-body in a 3/4 front view, facing slightly toward the viewer's right. Her eyebrows are raised and curved with concern, her mouth is open in a gentle alarmed expression, and small sweat drops may appear near her face. Both hands are near her head, or one hand holds the magnifying glass while the other touches her hair, but keep the magnifying glass visible and consistent with the references. Keep the silhouette readable for placement on the left side of an educational HTML game scene.

Style: polished 2D storybook educational game illustration, warm soft painterly texture, crisp clean cutout edges, same proportions, face, outfit, colors, lighting, and visual weight as the reference teacher assets.

Alpha and opacity: transparent background only. The entire character must be fully opaque: skin, hair, glasses, cardigan, blouse, scarf, belt, skirt, socks, shoes, sweat drops, name badge, and magnifying glass. The teal floral skirt must be solid opaque fabric with visible floral pattern; no semi-transparent skirt, no ghosted fabric, no see-through clothing. No background, no floor, no scenery, no speech bubble, no clock, no UI, no text.
```

Negative prompt:

```text
different character, child, elderly, different hairstyle, no glasses, different outfit, pants, apron, hat, book in hand, clock in hand, background, floor, wall, furniture, text, speech bubble, UI, cropped feet, cropped hands, malformed hands, extra fingers, distorted glasses, translucent skirt, transparent clothing, ghosted fabric, semi-transparent body parts, low-resolution edges
```

## Prompt: `teacher_pointing.png`

Intended HTML use:

- `#s-tut` / `section_tutorial_clock` / "꼬마 사서의 첫 수리"
- `#s-a` / `section_mission_type_a` / "유형 A: 엉망이 된 도서관 시계 맞추기"
- `#s-c` / `section_mission_type_c` / "유형 C: 도서 대출 시스템 재부팅"
- Used when the teacher guides learners toward the clock, broken signboard, or monitor.

Prompt:

```text
Create a full-body transparent PNG of the same warm young adult librarian teacher character from the reference images. She has a high rounded medium-brown hair bun with loose side wisps, round thin-rimmed glasses, large warm brown eyes, fair warm skin, a cream cable-knit cardigan over a white blouse with a scalloped collar, a coral neck scarf, a brown belt, a teal A-line midi skirt with small floral flowers, cream socks, brown Mary Jane shoes, a small gold/brass name badge, and a librarian magnifying glass.

Pose: friendly instructional pointing pose. She stands full-body in a 3/4 front view, positioned as if she will appear on the left side of the screen and point toward the center/right. Extend her right arm to the viewer's right with a clear pointing finger. Her other hand holds the magnifying glass near her chest. Her expression is calm, kind, and encouraging, with a small confident smile. Make the pointing hand and finger fully visible inside the canvas with safe transparent padding.

Style: polished 2D storybook educational game illustration, warm soft painterly texture, crisp clean cutout edges, same proportions, face, outfit, colors, lighting, and visual weight as the reference teacher assets.

Alpha and opacity: transparent background only. The entire character must be fully opaque: skin, hair, glasses, cardigan, blouse, scarf, belt, skirt, socks, shoes, name badge, and magnifying glass. The teal floral skirt must be solid opaque fabric with visible floral pattern; no semi-transparent skirt, no ghosted fabric, no see-through clothing. No background, no floor, no scenery, no speech bubble, no clock, no UI, no text.
```

Negative prompt:

```text
different character, child, elderly, different hairstyle, no glasses, different outfit, pointing left, cropped pointing hand, cropped feet, book, tablet, clock, background, floor, wall, furniture, text, speech bubble, UI, malformed hands, extra fingers, distorted glasses, translucent skirt, transparent clothing, ghosted fabric, semi-transparent body parts, low-resolution edges
```
