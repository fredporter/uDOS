# User Onboarding Flow (Ghost to Wizard)

Updated: 2026-03-05  
Status: user-facing onboarding map

This page is the short user-facing onboarding guide for uDOS v1.5.

The onboarding experience is a playable terminal mission where each step both teaches a concept and performs real setup.

Canonical mission script:
- [../docs/examples/ghost-to-wizard-script.md](../docs/examples/ghost-to-wizard-script.md)

Canonical demo extension pack:
- [../docs/examples/ucode_v1_5_release_pack/README.md](../docs/examples/ucode_v1_5_release_pack/README.md)

## Mission Path

1. Ghost: Awakening Chamber
- Learn basic controls and help flow.
- Run: `help`, `udos doctor`
- Outcome: environment checks completed.

2. Apprentice: Command Vault
- Learn baseline command language.
- Run: `udos status`, `udos install core`
- Outcome: local runtime initialized.

3. Apprentice: TUI Hall
- Learn panel and command controls.
- Run: `udos init my-first-binder`
- Outcome: first workspace structure created.

4. Operator: Workflow Engine
- Learn mission/task execution model.
- Run: `run mission hello_world`
- Outcome: workflow output + task progression.

5. Alchemist: Extension Forge
- Learn extension lane.
- Run: `udos install extension.image`, `generate image`
- Outcome: extension setup + first generated artifact.

6. Alchemist: Research Tower
- Learn research and knowledge flow.
- Run: `research topic terminal interfaces`
- Outcome: markdown research artifact generated.

7. Wizard: Surface Trial
- Complete full project lifecycle.
- Run: `create project guidebook`, `publish`
- Outcome: output + publish artifact generation.

## View and Rendering Learnings

Use these demos to learn the TUI view matrix:
- [../docs/examples/ucode_v1_5_release_pack/05-grid-and-view-rendering.md](../docs/examples/ucode_v1_5_release_pack/05-grid-and-view-rendering.md)
- [../docs/examples/ucode_v1_5_release_pack/07-layer-mapping-and-z-index.md](../docs/examples/ucode_v1_5_release_pack/07-layer-mapping-and-z-index.md)

Coverage includes:
- text panels
- column layouts
- ASCII/teletext rendering
- calendar/task views
- block/grid/container composition

## Repair and Self-Extension Learnings

Use these demos after onboarding:
- [../docs/examples/ucode_v1_5_release_pack/08-seed-library-generation.md](../docs/examples/ucode_v1_5_release_pack/08-seed-library-generation.md)
- [../docs/examples/ucode_v1_5_release_pack/09-dev-mode-repair-and-self-extension.md](../docs/examples/ucode_v1_5_release_pack/09-dev-mode-repair-and-self-extension.md)

These show how v1.5 can:
- maintain seed libraries for renderer/workflow templates
- run repair flows through official command lanes
- extend from Dev Mode with policy-gated cloud-code-agent operations

## Where To Start

- New users:
  [Installation](Installation.md) -> this page -> [Core](Core.md)
- Operator deep dive:
  [../docs/howto/UCODE-COMMAND-REFERENCE.md](../docs/howto/UCODE-COMMAND-REFERENCE.md)
- Runtime standard:
  [../docs/decisions/v1-5-ucode-tui-spec.md](../docs/decisions/v1-5-ucode-tui-spec.md)
