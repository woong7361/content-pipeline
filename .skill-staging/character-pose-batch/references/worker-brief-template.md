# Worker Brief Template

Use this for sub-agent delegation.

```markdown
You are producing a bounded character pose batch.

You are not alone in the workspace. Do not overwrite unrelated files or revert edits made by others. Work only in:

- <assigned-output-directory>

Read:

- <character-design.md>
- <pose-rows-or-poses.md>

Task:

1. Create prompts or generate images for only these files:
   - <file-1>
   - <file-2>
2. Preserve the character identity invariants exactly.
3. Follow the alpha/canvas rules exactly.
4. Save outputs using the requested filenames.
5. Return a short final report listing:
   - files created or changed;
   - any pose that needs regeneration;
   - any uncertainty about identity, alpha, crop, or target fit.

Hard constraints:

- Do not use a project-specific reference unless it appears in the provided design spec.
- Do not invent extra characters.
- Do not generate extra poses.
- Do not make clothing or body parts semi-transparent.
```
