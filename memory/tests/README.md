# uDOS Test Suite

This directory contains all tests for the uDOS system, organized by type and version.

## Structure

```
memory/tests/
├── README.md                          # This file
├── shakedown.uscript                  # Quick system validation test
├── v1_0_7_file_operations_test.sh     # v1.0.7 advanced file operations test
├── test_files/                       # Test data files for file operations
│   ├── test1.md
│   ├── test2.txt
│   ├── script.py
│   └── config.conf
├── integration/                      # Integration tests
│   ├── test_cli_v1_0_6.py
│   ├── test_file_integration_v1_0_2.py
│   ├── test_map_integration.py
│   ├── test_teletext_integration.py
│   └── test_v1_0_2_integration.py
├── unit/                             # Unit tests
│   ├── test_dashboard.py
│   ├── test_file_operations_v1_0_2.py
│   ├── test_palette_tree.py
│   └── test_remaining_commands.py
├── test_map_surface.py               # Standalone map surface tests
├── test_session_minimal.py           # Minimal session tests
├── test_v1_0_2_enhancements.py       # v1.0.2 enhancements
├── test_v1_0_2_simple_integration.py # v1.0.2 simple integration
└── test_v1_0_2_standalone.py         # v1.0.2 standalone tests
```

## Running Tests

### Quick Validation
```bash
# Run shakedown test for basic system validation
./memory/tests/shakedown.uscript
```

### Feature-Specific Tests
```bash
# Test v1.0.7 advanced file operations
./memory/tests/v1_0_7_file_operations_test.sh
```

### VS Code Integration
Tests can be run from VS Code using the configured tasks:
- **Run Shakedown Test** - Quick system validation
- **Run v1.0.2 Standalone Tests** - v1.0.2 feature tests
- **Run v1.0.2 Integration Tests** - v1.0.2 integration tests

## Test Data

The `test_files/` directory contains sample files for testing file operations:
- `test1.md` - Markdown test file
- `test2.txt` - Plain text test file
- `script.py` - Python script test file
- `config.conf` - Configuration test file

## Adding New Tests

When adding new tests:
1. Place unit tests in `unit/`
2. Place integration tests in `integration/`
3. Place feature-specific tests in the root with descriptive names
4. Update this README with new test descriptions
5. Add test tasks to `.vscode/tasks.json` if needed

## Test Coverage

Current test coverage includes:
- ✅ System commands (v1.0.1)
- ✅ Configuration management (v1.0.2)
- ✅ Mapping system (v1.0.3)
- ✅ CLI terminal features (v1.0.6)
- ✅ Advanced file operations (v1.0.7)

---

*Last updated: November 2, 2025*

## Running Tests

From the workspace root:

```bash
# Run all tests
pytest -q memory/tests

# Run specific test file
pytest -q memory/tests/test_session_minimal.py

# Run with verbose output
pytest -v memory/tests
```

Or use the VS Code task: **Run Pytest**

## Test Philosophy

- **Fast shakedowns** - Tests should run quickly for rapid feedback
- **Minimal dependencies** - Tests should work with basic Python setup
- **Clear failure messages** - When tests fail, it should be obvious why
- **Smoke tests preferred** - Basic functionality validation over exhaustive testing

## Adding New Tests

1. Follow naming convention: `test_*.py`
2. Use descriptive test function names: `test_feature_specific_behavior`
3. Include docstrings explaining what the test validates
4. Keep tests independent - no test should depend on another test's state

## Directory Structure (Legacy)

### `/integration/`
Integration tests that verify complete workflows and system interactions:
- `test_map_integration.py` - Complete MAP command system testing
- `test_teletext_integration.py` - Teletext web extension integration
- `test_file_integration_v1_0_2.py` - File operations integration (v1.0.2)
- `test_v1_0_2_integration.py` - General v1.0.2 integration testing

### `/unit/`
Unit tests for individual components:
- `test_dashboard.py` - Dashboard and status display testing
- `test_palette_tree.py` - Color palette and tree structure testing
- `test_file_operations_v1_0_2.py` - File operations unit tests
- `test_remaining_commands.py` - Command handler unit tests

## Running Tests

### Integration Tests
```bash
# Run all integration tests
cd tests/integration
python3 test_map_integration.py
python3 test_teletext_integration.py

# Specific test example
python3 test_map_integration.py
```

### Unit Tests
```bash
# Run unit tests
cd tests/unit
python3 test_dashboard.py
python3 test_palette_tree.py
```

## Test Environment

Tests should be run from the uDOS root directory with the virtual environment activated:

```bash
cd /Users/fredbook/Code/uDOS
source .venv/bin/activate
python3 tests/integration/test_map_integration.py
```

## Historical Tests

Version-specific development tests have been moved to `/dev/docs/development/` for historical reference.
