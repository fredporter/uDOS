# Seed Data and Custom Templates

Updated: 2026-03-05  
Status: user-facing template guide

This page explains where v1.5 seed data lives, what you can safely customize, and how to use templates for your own onboarding, mission, and workspace flows.

## Seed Data Roots

Canonical tracked seeds:
- `core/framework/seed/bank/graphics/`
- `core/framework/seed/bank/templates/`
- `core/framework/seed/bank/system/`

Runtime copies for local customization:
- `memory/system/themes/` (message theme runtime copies)
- `memory/system/` and binder-local workspace files for operator edits

Reference docs:
- [../core/framework/seed/bank/README.md](../core/framework/seed/bank/README.md)
- [../docs/examples/ucode_v1_5_release_pack/08-seed-library-generation.md](../docs/examples/ucode_v1_5_release_pack/08-seed-library-generation.md)

## What To Customize

Good customization targets:
- user profile defaults (`user.template.json`)
- story/session defaults (`story.template.json`)
- mission templates (`templates/missions/`)
- workflow templates (`templates/workflows/`)
- message theme vocabulary (`system/themes/*.json`)

Do not edit tracked seed files for per-user experimentation. Keep local variants in runtime memory paths or binder-local project files.

## Example 1: User Template Variant

Base file:
- `core/framework/seed/bank/templates/user.template.json`

Create a local variant for your workspace:

```json
{
  "SYSTEM_NAME": "uDOS",
  "VERSION": "1.5",
  "USER_PROFILE": {
    "NAME": "Operator",
    "LOCATION": "Brisbane",
    "TIMEZONE": "Australia/Brisbane",
    "PREFERRED_MODE": "STANDARD"
  },
  "PROJECT": {
    "NAME": "my-first-binder",
    "DESCRIPTION": "Onboarding project",
    "START_DATE": "2026-03-05"
  }
}
```

Use it as a local starter profile for new binder/workspace initialization.

## Example 2: Mission Template Variant

Base file:
- `core/framework/seed/bank/templates/missions/MISSION-template.md`

Create a mission file such as `missions/onboarding-checkpoint.md`:

```md
# MISSION: onboarding-checkpoint

## Goal
Complete setup checks and capture one publishable artifact.

## Steps
1. Run doctor/status checks.
2. Execute one mission workflow.
3. Save the resulting artifact and update completion state.

## Outputs
- outputs/onboarding-checkpoint.md
```

Run it through your normal mission path (for example the same flow used in onboarding demos).

## Example 3: Workflow Template Variant

Template folder:
- `core/framework/seed/bank/templates/workflows/`

Copy one workflow template and specialize fields:
- objective
- deliverables
- constraints
- output path

Keep output paths deterministic so review and replay are easy.

## Example 4: Theme Vocabulary Variant

Theme seeds:
- `core/framework/seed/bank/system/themes/`

Runtime theme copies:
- `memory/system/themes/`

Use theme variants to adjust terminal message tone without changing command or log contracts.

Related map rules:
- [TUI Z-Layer and TOYBOX](TUI-Z-Layer-and-TOYBOX.md)
- [../docs/features/THEME-LAYER-MAPPING.md](../docs/features/THEME-LAYER-MAPPING.md)

## Practical Usage Flow

1. Start from tracked seed templates.
2. Copy to a local runtime/binder file.
3. Customize values for your current project.
4. Run your mission/workflow.
5. Keep successful variants as reusable local templates.

## Repair and Re-Seed

If local runtime seed state drifts, use the documented repair path and re-seed flow from:
- [../docs/howto/TOOLS-SYSTEM-HEALTH-REFERENCE.md](../docs/howto/TOOLS-SYSTEM-HEALTH-REFERENCE.md)
- [../docs/examples/ucode_v1_5_release_pack/09-dev-mode-repair-and-self-extension.md](../docs/examples/ucode_v1_5_release_pack/09-dev-mode-repair-and-self-extension.md)

## Related Pages

- [Onboarding Flow](Onboarding-Flow.md)
- [Installation](Installation.md)
- [Dev Tools](Dev-Tools.md)
