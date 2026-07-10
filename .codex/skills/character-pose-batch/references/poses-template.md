# Poses Template

Copy this into `characters/<character-id>/poses.md`.

```markdown
# <Character Display Name> Poses

## Pose Table

| Output file | Pose | Expression | Facing | Framing | Intended use | Prompt notes | Acceptance criteria |
|---|---|---|---|---|---|---|---|
| <character>_idle.png | relaxed standing idle | friendly | 3/4 toward center | full-body | default helper state | hands visible, neutral stance | same identity, full-body, transparent background |

## Batch Plan

| Batch | Files | Worker | Notes |
|---|---|---|---|
| 01 |  |  |  |
```

## Pose Row Guidance

- Keep pose names concrete: `pointing-right`, `worried-head-hold`, `success-cheer`, `confused-thinking`.
- Include target screen or document section only when provided by the user.
- Prefer full-body for reusable app characters unless the user requests bust/half-body.
- Record whether a hand must point left/right. This avoids later mirroring problems.
