# Terminal Styling Decisions (v1.3)

## Context

Wizard dashboard includes multiple terminal-like surfaces (`uCLI Console`, `Dev Mode runner`, log streams). These had duplicated styling and drifted over time.

## Decision

Use shared terminal design tokens and utility classes from:

- `wizard/dashboard/src/styles/terminal.css`

Core tokens:

- `--wiz-terminal-bg`
- `--wiz-terminal-bg-elevated`
- `--wiz-terminal-border`
- `--wiz-terminal-text`
- `--wiz-terminal-accent`

Shared classes:

- `.wiz-terminal-panel`
- `.wiz-terminal-chip`
- `.wiz-terminal-input`
- `.wiz-terminal-log`
- `.wiz-terminal-btn`

Reusable components:

- `wizard/dashboard/src/lib/components/terminal/TerminalPanel.svelte`
- `wizard/dashboard/src/lib/components/terminal/TerminalButton.svelte`
- `wizard/dashboard/src/lib/components/terminal/TerminalChip.svelte`
- `wizard/dashboard/src/lib/components/terminal/TerminalInput.svelte`
- `wizard/dashboard/src/lib/components/terminal/TerminalTextarea.svelte`
- `wizard/dashboard/src/lib/components/terminal/TerminalSelect.svelte`
- `wizard/dashboard/src/lib/components/terminal/TerminalTimezonePicker.svelte`
- `wizard/dashboard/src/lib/components/terminal/TerminalLocationPicker.svelte`

Setup-story advanced control coverage (v1.2+ parity):

- Date picker (`field.type = date`)
- Time picker (`field.type = time`)
- Date-time picker (`field.type = datetime-local`)
- Timezone picker with suggestions (`field.type = timezone`)
- Location picker with search/suggestions (`field.type = location`)

## Applied Surfaces

- `wizard/dashboard/src/routes/UCodeConsole.svelte`
- `wizard/dashboard/src/routes/DevMode.svelte`

## Rationale

- Keeps terminal surfaces visually coherent while preserving route-specific layout.
- Reduces CSS duplication and future rebrand cost.
- Keeps `uCLI` and Wizard Dev surfaces aligned with one style system.

## Follow-up

- Extend shared terminal classes/components to `Logs.svelte` and `Ports.svelte`.
- Move PAT/webhook cards in `DevMode.svelte` to terminal component primitives.
