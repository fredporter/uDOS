# uCLI Launcher

Single CLI entrypoint: `ucli`.

## Quick Start

```bash
./bin/ucli
```

## Commands

```bash
./bin/ucli               # Start uCLI terminal interface
./bin/ucli tui           # Explicit terminal interface
./bin/ucli wizard        # Start Wizard server + GUI APIs
./bin/ucli prompt        # Shell-integrated prompt loop
./bin/ucli cmd "STATUS" # One-shot uCODE command via Wizard API
```

## Runtime Model

- `uCLI` is the only TUI.
- `uCODE` is the command surface.
- `Wizard GUI` is the GUI host for platform features.
- `uDOS` is the underlying TS/Python runtime.

## Process Management

```bash
./bin/kill-udos.sh
```

## Notes

- `ucli wizard` starts Wizard server only. It does not spawn another TUI.
- Dev workspace execution (`/dev/goblin/scripts`, `/dev/goblin/tests`) is exposed through Wizard Dev Mode APIs.
