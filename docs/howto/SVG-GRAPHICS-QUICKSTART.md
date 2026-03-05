# SVG Graphics Quickstart

Updated: 2026-03-04
Status: active how-to

## Purpose

Use this guide for the v1.5 SVG workflow: local-first generation, Markdown-safe storage, and Wizard-managed cloud escalation only when needed.

## Fastest Path

1. Prepare the standard runtime with [INSTALLATION.md](../INSTALLATION.md).
2. If you want contributor-side local generation, prepare the `@dev` workspace lane with [MISTRAL-VIVE-DEV-WORKSPACE.md](MISTRAL-VIVE-DEV-WORKSPACE.md).
3. Generate or review SVG assets through the Wizard graphics service or the matching workflow/template lane.

## Local-First Example

```python
from wizard.services.graphics_service import get_graphics_service

graphics = get_graphics_service()
artifact = graphics.render_mermaid_svg(
    source="graph TD; A[Wizard]-->B[Beacon Portal]; B-->C[Resource Library]",
    output_file="architecture/wizard-beacon.svg",
)

svg = artifact.content
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

- [SVG Graphics Reference](SVG-GRAPHICS-REFERENCE.md)
- [INSTALLATION.md](../INSTALLATION.md)
- [MISTRAL-VIVE-DEV-WORKSPACE.md](MISTRAL-VIVE-DEV-WORKSPACE.md)
