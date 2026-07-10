---
name: character-pose-batch
description: Create reusable character design specs, pose lists, image-generation prompts, parallel sub-agent batches, and QA checklists for character asset production. Use when the user asks to generate or regenerate character pose assets, make character-specific design.md files, keep multiple poses visually consistent, delegate character image work to sub-agents, or plan batches for transparent PNG character assets. Do not trigger for one-off casual image requests that do not need reusable character identity or batch coordination.
---

# Character Pose Batch

## Core Rule

Keep this skill project-agnostic. Do not anchor prompts to a specific `index.html`, document, existing character, brand, or repository artifact unless the user explicitly provides it for the current task.

## Workflow

1. Run the intake before writing prompts. If the answer is not available from user-provided context, ask only the missing high-impact question.
2. Create one `design.md` per character. Lock identity, style, outfit, alpha rules, and non-negotiable invariants.
3. Create one `poses.md` per character. List output filenames, intended pose, expression, facing direction, scene/use target, and acceptance criteria.
4. Split work into small pose batches. Default to 1 character identity per batch. For image generation, prefer no more than 2 concurrent workers per character identity unless the user explicitly prioritizes speed over identity consistency.
5. Spawn sub-agents only when the user explicitly asks for sub-agents, delegation, or parallel agent work. Give each worker a self-contained batch brief and a disjoint output path.
6. QA every returned image before integration. Check identity consistency, pose fit, full-body crop, transparent background, opaque clothing, and target-surface fit.

## Intake

Use `references/intake.md` when the request does not already define:

- whether reference character images or existing assets should be used;
- whether the assets are for an HTML/app screen, document, slide deck, game, or general library;
- where the generated files should be saved;
- the exact characters and required poses;
- whether the user wants prompts only, image generation, QA, or integration into a target file.

If the user provides an HTML file, document, storyboard, or existing assets, inspect those artifacts and cite the exact scene/use targets in the generated `poses.md`.

## Character Design Specs

Use `references/character-design-template.md` for each character. The design spec must separate:

- `Identity invariants`: never change across poses.
- `Style invariants`: rendering style, line weight, lighting, proportions.
- `Outfit invariants`: clothes, colors, accessories, opacity rules.
- `Alpha/background rules`: transparent background only; no semi-transparent clothing or body parts.
- `Negative constraints`: what must not appear.
- `Pose compatibility`: facing direction, hand availability, safe margins, and likely screen placement.

If a reference image is provided, describe it as the identity anchor in `design.md`. If no reference image is provided, create a precise textual identity spec and mark it as the source of truth.

## Pose Lists

Use `references/poses-template.md`. For each pose, include:

- output filename;
- pose and expression;
- body framing;
- facing direction;
- intended use target;
- prompt notes;
- QA acceptance criteria.

Avoid duplicate near-identical poses unless the target UI genuinely needs them.

## Sub-Agent Batching

Give each worker only the relevant character `design.md`, its assigned pose rows, target output folder, and naming contract. Tell workers they are not alone in the workspace and must not overwrite unrelated work.

Recommended batch sizing:

- prompt writing: 3-6 poses per worker is usually fine;
- image generation: 1-2 poses per worker is safer for identity consistency;
- QA: can be delegated separately after generation.

For the same character, do not fan out too widely unless a stable visual reference is provided. More parallelism increases identity drift risk.

Use `references/worker-brief-template.md` for delegation prompts.

## QA

Use `references/qa-checklist.md` after generation and before integrating assets. Reject or request regeneration when:

- the character looks like a different person across poses;
- clothes, hair, glasses, accessories, skin tone, or body proportions drift;
- clothing or body parts are semi-transparent;
- the image is not full-body when full-body was requested;
- the background is not transparent;
- hands, face, eyes, or feet are malformed;
- the pose does not fit the intended screen placement.

## Outputs

Prefer this portable structure unless the user specifies another layout:

```text
characters/
  <character-id>/
    design.md
    poses.md
    prompts/
      batch-01.md
      batch-02.md
    qa.md
```
