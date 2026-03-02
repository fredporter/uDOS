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
