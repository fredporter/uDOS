# uDOS Installation

One command installs uDOS and launches the unified entry point.

## One-Command Install (macOS/Linux)

```bash
curl -fsSL https://raw.githubusercontent.com/fredporter/uDOS/main/bin/install.sh | UDOS_AUTOSTART=1 bash
```

This bootstraps the repo, runs the installer, and self-heals missing deps.
Omit `UDOS_AUTOSTART=1` to install without launching.

## Launch

```bash
./bin/ucli
```

## Wizard Runtime Setup

```bash
./bin/ucli wizard install
./bin/ucli wizard doctor
```

### Options

```bash
./bin/ucli
./bin/ucli wizard
```

## Notes

- For forks: `UDOS_REPO_URL=https://github.com/<you>/<repo>.git`.
- For a different install location: `UDOS_HOME_ROOT=/path/to/udos`.
- Check version with `python -m core.version`.
