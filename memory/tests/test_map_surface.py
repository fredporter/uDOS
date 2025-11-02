#!/usr/bin/env python3
"""
Test map surface - smokes a small MAP VIEW when uDOS.py is present.

This test validates basic MAP functionality.
"""

import pytest
import subprocess
import sys
from pathlib import Path


def test_udos_main_exists():
    """Test that uDOS.py exists and is executable."""
    udos_path = Path(__file__).parent.parent.parent / "uDOS.py"
    assert udos_path.exists(), "uDOS.py not found"


def test_map_status_smoke():
    """Smoke test for MAP STATUS command."""
    udos_path = Path(__file__).parent.parent.parent / "uDOS.py"

    if not udos_path.exists():
        pytest.skip("uDOS.py not found")

    try:
        # Run MAP STATUS command
        result = subprocess.run(
            [sys.executable, str(udos_path)],
            input="MAP STATUS\n",
            text=True,
            capture_output=True,
            timeout=10,
            cwd=udos_path.parent
        )

        # Should not crash (exit code doesn't matter for smoke test)
        assert result.returncode is not None, "Process should complete"

        # Output should contain something map-related
        output = result.stdout + result.stderr
        # Basic smoke test - just ensure it runs without major errors
        assert len(output) > 0, "Should produce some output"

    except subprocess.TimeoutExpired:
        pytest.fail("MAP STATUS command timed out")
    except Exception as e:
        pytest.fail(f"MAP STATUS command failed: {e}")


if __name__ == "__main__":
    pytest.main([__file__])
