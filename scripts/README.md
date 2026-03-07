# Project Management Scripts

This directory contains scripts that support project versioning and deployment workflows.

## Testing

### Canonical pytest entrypoint

```bash
./scripts/run_pytest.sh wizard/tests
./scripts/run_pytest.sh core/tests tests
```

### Profile-based pytest entrypoint

```bash
./scripts/run_pytest_profile.sh core
./scripts/run_pytest_profile.sh wizard
./scripts/run_pytest_profile.sh full
```

### Core stdlib smoke lane

```bash
./scripts/run_pytest_core_stdlib.sh
```

### Core stdlib strict demo lane

```bash
./scripts/demo_core_stdlib_py_strict.sh
```

### Wizard advanced strict demo lane

```bash
./scripts/demo_wizard_advanced_strict.sh
```

### TUI story form selectors/elements demo

```bash
# Preview generated form spec (non-interactive)
./scripts/demo_story_form_tui.sh --spec

# Run interactive TUI form demo
./scripts/demo_story_form_tui.sh
```

### Clean Python artifacts

```bash
./scripts/clean_python_artifacts.sh
```

## Versioning

### Usage

```bash
# Bump major version (1.0.0 -> 2.0.0)
uv run scripts/bump_version.py major

# Bump minor version (1.0.0 -> 1.1.0)
uv run scripts/bump_version.py minor

# Bump patch/micro version (1.0.0 -> 1.0.1)
uv run scripts/bump_version.py micro
# or
uv run scripts/bump_version.py patch
```
