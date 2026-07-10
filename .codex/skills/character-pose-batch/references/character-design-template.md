# Character Design Template

Copy this into `characters/<character-id>/design.md`.

```markdown
# <Character Display Name> Design

## Source Of Truth

- Character id:
- Identity source:
- Reference files:
- Usage target:

## Identity Invariants

- Age/read:
- Face shape:
- Hair:
- Eyes:
- Skin tone:
- Body proportions:
- Distinctive traits:

## Outfit Invariants

- Main outfit:
- Colors:
- Accessories:
- Footwear:
- Props allowed:
- Props forbidden:

## Style Invariants

- Rendering style:
- Line/edge treatment:
- Lighting:
- Proportions:
- Mood:
- Match existing assets:

## Alpha And Canvas Rules

- Output format:
- Background:
- Body framing:
- Margins:
- Opacity:
- Shadows:

## Negative Constraints

- Do not change:
- Do not include:
- Avoid:

## Pose Compatibility Notes

- Default facing:
- UI-safe hand direction:
- Speech bubble side:
- Important screen clearances:
- Known target scenes:
```

## Alpha Rule Wording

Use strict wording when transparent PNGs are required:

```text
Transparent background only. The character, clothing, hair, shoes, props, and all body parts must be fully opaque. Do not make skirts, sleeves, hair, glasses, legs, or props semi-transparent. No ghosted fabric. No see-through clothing. No background color, no floor, no scenery.
```
