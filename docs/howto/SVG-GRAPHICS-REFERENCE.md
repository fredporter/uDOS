# SVG Graphics Reference

Updated: 2026-03-03
Status: active how-to reference

## Scope

Detailed reference for:
- SVG generation architecture
- supported styles
- prompt design
- integration patterns
- validation
- performance and caching
- troubleshooting

## Generation Model

The SVG path may use:
- local Ollama-backed generation for speed and zero marginal cost
- cloud-backed generation for higher-quality output

## Supported Styles

Supported styles:
- minimalist
- technical
- artistic
- cartoon

## Integration

Primary integration points:
- Wizard graphics service
- markdown and docs workflows
- command or workflow automation that stores generated SVG artifacts

## Quality and Validation

Check:
- valid SVG structure
- safe and bounded dimensions
- style consistency
- renderability in downstream docs or GUIs

## Performance

Optimize with:
- caching repeated diagrams
- batching repeated generations
- local-first generation where acceptable

## Troubleshooting

Common issues:
- invalid SVG output
- slow cloud response
- safety filter refusal

## Canonical Front Door

Start with:
- [SVG Graphics Quickstart](/Users/fredbook/Code/uDOS/docs/howto/SVG-GRAPHICS-QUICKSTART.md)

