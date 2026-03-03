# uDOS Go TUI

This is the v1.5 terminal frontend described by:

- [v1-5-ucode-tui-spec.md](/Users/fredbook/Code/uDOS/docs/decisions/v1-5-ucode-tui-spec.md)
- [u_dos_robust_teletext_tui_brief_bubble_tea_lip_gloss.md](/Users/fredbook/Code/uDOS/docs/decisions/u_dos_robust_teletext_tui_brief_bubble_tea_lip_gloss.md)

The Go frontend owns:

- layout
- key handling
- panel rendering
- teletext-safe presentation

The Python backend remains responsible for:

- command routing
- workflow execution
- research/template operations
- local file-backed runtime behavior

## Build

```bash
./scripts/build_udos_tui.sh
```

## Run

```bash
./bin/udos-tui
```
