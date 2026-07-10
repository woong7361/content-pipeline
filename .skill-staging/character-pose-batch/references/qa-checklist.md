# QA Checklist

Use this after each batch.

## Identity

- Same person across all poses.
- Same face shape, hair, eyes, skin tone, age/read, and body proportions.
- Same outfit colors, accessories, and signature props.
- No accidental gender/age/species/style drift.

## Pose

- Matches requested action and expression.
- Facing direction fits the target placement.
- Hands and props support the intended UI/story action.
- The pose is readable at expected display size.

## Technical

- Correct file format.
- Transparent background if requested.
- Full-body/half-body/bust framing matches request.
- No clipped head, hands, feet, or props unless requested.
- Adequate safe margin around the character.

## Alpha And Visual Artifacts

- Clothing fully opaque.
- Hair, glasses, legs, shoes, and props fully opaque.
- No ghosted fabric or see-through clothing.
- No unwanted black/white background fringe.
- No background scenery, floor, text, watermark, or UI.

## Integration Fit

- Character does not cover critical UI.
- Speech bubble side and hand direction make sense.
- Scale is consistent with other characters.
- Shadows/lighting match the target artifact.

## QA Result Format

```markdown
# Character Asset QA

## Accepted

- 

## Needs Regeneration

| File | Reason | Suggested fix |
|---|---|---|
|  |  |  |

## Integration Notes

- 
```
