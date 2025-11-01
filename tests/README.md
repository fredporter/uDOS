# uDOS Test Suite

This directory contains organized tests for the uDOS system.

## Directory Structure

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

Version-specific development tests have been moved to `/docs/development/` for historical reference.
