# Intake

Ask or infer these before producing character pose batches.

## Required Decisions

1. Scope
   - Are we creating prompts only, generating images, QAing existing images, or integrating final assets?

2. Character sources
   - Is there a reference character image or existing asset?
   - If yes, which file is the identity anchor?
   - If no, should a textual identity spec be created from the user's description?

3. Usage target
   - Where will the character appear: HTML/app, document, slides, game, print, or general asset library?
   - If a target file exists, which file should be inspected?
   - Which scenes/screens/sections use each pose?

4. Output contract
   - Where should files be written?
   - What filename convention should be used?
   - What canvas/framing is needed: full-body, half-body, bust, sprite, or icon?

5. Style and technical constraints
   - Transparent PNG or another format?
   - Existing art style to match?
   - Required dimensions or aspect ratio?
   - Any forbidden traits, outfits, props, or colors?

## Minimal Questions

When context is missing, ask the smallest useful set:

- "Do you have a reference character image/assets to preserve, or should I define the character from text?"
- "What target artifact should these poses serve: an HTML/app screen, a document/storyboard, or a general asset library?"
- "Do you want prompts only, actual image generation, or generation plus QA/integration?"

## Do Not Assume

- Do not assume a specific `index.html` or project artifact.
- Do not assume a reference character from the current repository unless the user points to it.
- Do not reuse a character identity from a previous task unless the user explicitly says to.
