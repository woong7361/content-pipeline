# Teacher/Librarian Poses

## Pose Table

| Output file | Pose | Expression | Facing | Framing | Intended use | Prompt notes | Acceptance criteria |
|---|---|---|---|---|---|---|---|
| `teacher_worried.png` | Worried head-hold with magnifying glass | Alarmed, eyebrows raised, mouth open, small sweat drops allowed | 3/4 front, facing slightly toward center/right | Full body, shoes visible | HTML `#s-problem` / `section_problem_intro` / "고장 난 도서관 시계"; initial crisis dialogue where the teacher says the library clock is broken. Also used by JS when the problem scene resets. | Both hands near head or one hand near head; magnifying glass may remain in hand or tucked visibly; keep body narrow enough for left-side placement. | Same identity as references; full body; transparent background only; cream cardigan, blouse, scarf, teal floral skirt, socks, shoes, hair, glasses, props, and body all fully opaque; no cropped hands or feet; no background. |
| `teacher_pointing.png` | Friendly right-pointing instruction pose with magnifying glass | Calm, encouraging smile | 3/4 front, placed left and pointing toward screen center/right | Full body, extended hand fully visible | HTML `#s-tut` / `section_tutorial_clock` / "꼬마 사서의 첫 수리"; HTML `#s-a` / `section_mission_type_a` / "유형 A: 엉망이 된 도서관 시계 맞추기"; HTML `#s-c` / `section_mission_type_c` / "유형 C: 도서 대출 시스템 재부팅". Used to guide the learner toward the clock, signboard, or monitor. | Right arm extended to viewer's right; other hand may hold magnifying glass near chest; keep the pointing finger clear and not clipped. | Same identity as references; direction clearly points right; full body; transparent background only; all clothing fully opaque, especially the teal skirt; no text, UI, clocks, or scenery. |
| `teacher_happy.png` | Happy clapping / proud congratulation pose | Big warm smile, proud and relieved | 3/4 front, facing slightly toward center/left or center depending placement | Full body, hands visible near chest | HTML `#s-problem` via JS success transition to `teacher_happy.png`; HTML `#s-tutok` / `section_tutorial_success`; HTML `#s-repair` / `section_repair_outro`; HTML `#s-story` / `section_story_gallery`; HTML `#s-cert` / `section_final_certificate`. Used for success, repair completion, story gallery, and final thanks. | Hands together in clapping gesture near chest; magnifying glass may hang from cardigan pocket as in reference; keep expression celebratory but not exaggerated. | Same identity as references; full body; transparent background only; all character pixels fully opaque; skirt has solid opacity with floral pattern visible; no cropped shoes or hands; no background elements. |

## Batch Plan

| Batch | Files | Worker | Notes |
|---|---|---|---|
| 01 | `teacher_worried.png`, `teacher_pointing.png` | prompt batch only | Crisis and instructional poses. Use existing assets as identity/style references and explicitly fix the skirt/clothing alpha issue. |
| 02 | `teacher_happy.png` | prompt batch only | Success/congratulation pose. Use existing assets as identity/style references and explicitly fix the skirt/clothing alpha issue. |
