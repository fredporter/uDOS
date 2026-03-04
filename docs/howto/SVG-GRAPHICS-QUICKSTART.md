# SVG Graphics Quickstart

Updated: 2026-03-04
Status: active how-to

## Purpose

Use this guide for the v1.5 SVG workflow: local-first generation, Markdown-safe storage, and Wizard-managed cloud escalation only when needed.

## Fastest Path

1. Prepare the standard runtime with [INSTALLATION.md](/Users/fredbook/Code/uDOS/docs/INSTALLATION.md).
2. If you want contributor-side local generation, prepare the `@dev` workspace lane with [VIBE-Setup-Guide.md](/Users/fredbook/Code/uDOS/dev/docs/howto/VIBE-Setup-Guide.md).
3. Generate or review SVG assets through the Wizard graphics service or the matching workflow/template lane.

## Local-First Example

```python
from wizard.services.graphics_service import SVGGenerator

gen = SVGGenerator()
svg = await gen.generate_diagram(
    description="A distributed system with 3 nodes and message flow",
    style="technical",
    size="800x600",
)
```

## When To Escalate To Cloud

Use Wizard-managed provider routing only when:
- the local result is structurally wrong
- a higher-fidelity illustration is required
- policy and budget permit network use

## Prompt Rules

Always specify:
- canvas size or viewBox
- exact labels
- allowed shapes
- line/fill constraints
- whether the output is diagrammatic or decorative

## Related Docs

- [SVG Graphics Reference](/Users/fredbook/Code/uDOS/docs/howto/SVG-GRAPHICS-REFERENCE.md)
- [INSTALLATION.md](/Users/fredbook/Code/uDOS/docs/INSTALLATION.md)
- [VIBE-Setup-Guide.md](/Users/fredbook/Code/uDOS/dev/docs/howto/VIBE-Setup-Guide.md)
