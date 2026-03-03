# WORKFLOW: image-prompt-pack-v1

## Purpose
Generate a reusable image prompt pack using the shared v1.5 workflow template
shape.

## Inputs
- Goal: {{goal}}
- Style: {{style}}
- Aspect ratio: {{aspect_ratio}}
- Count: {{count}}

## Goal
{{goal}}

## Constraints
- Style: {{style}}
- Aspect ratio: {{aspect_ratio}}
- Count: {{count}}

## Phases
1. Concept extraction (image/concept -> 01-concept.md)
2. Prompt engineering (image/prompt-engine -> 02-prompts.md)

## Steps
1. Derive the concept from the goal and constraints.
2. Generate prompts in a reusable pack format.
3. Record outputs and operator-visible evidence.

## Outputs
- 01-concept.md
- 02-prompts.md

## Evidence
- Concept file written
- Prompt pack generated
- Constraints reflected in output

## Notes
- Keep outputs operator-readable and ready to duplicate into local work.
