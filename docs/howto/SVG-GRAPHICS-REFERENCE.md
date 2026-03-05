# SVG Graphics Reference

Updated: 2026-03-04
Status: active how-to reference

## Runtime Model

SVG generation in v1.5 follows the same assist contract as the rest of uDOS:
- local-first when possible
- Wizard-managed provider routing when cloud use is justified
- Markdown/file workflows remain the system of record

## Supported Styles

- `minimalist`
- `technical`
- `artistic`
- `cartoon`

## Storage Rules

- Keep generated SVG with the owning workflow, mission, or knowledge artifact.
- Prefer Markdown-linked assets over hidden runtime-only output.
- Treat generated SVG like other open-box user artifacts: portable, inspectable, and replaceable.

## Validation Rules

Check for:
- valid SVG structure
- bounded dimensions
- no unsafe external references
- renderability in docs and Wizard UI

## Performance Rules

- use local generation for routine diagrams
- cache repeatable outputs
- reserve cloud generation for higher-value assets

## Troubleshooting

- invalid SVG: tighten the prompt and specify shape limits
- low-quality layout: switch to `technical` style or use Wizard-managed cloud routing
- missing runtime: verify the standard runtime or Dev extension setup

## Start Here

- [SVG Graphics Quickstart](SVG-GRAPHICS-QUICKSTART.md)
