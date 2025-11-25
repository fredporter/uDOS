#!/usr/bin/env python3
"""
Test session minimal - validates core events appear in the last session log.

This test ensures basic uDOS logging functionality is working.
"""

import pytest
from pathlib import Path
import tempfile
import os
from datetime import datetime


def test_dev_logger_basic():
    """Test that dev_logger can create log entries."""
    # Import after sys.path adjustment
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))

    from core.dev_logger import dev_log_path, dev_log

    # Test log path generation
    path = dev_log_path("TEST-LOC", 5)
    assert "dev-" in str(path)
    assert "TEST-LOC" in str(path)
    assert "Z5" in str(path)

    # Test log writing
    with tempfile.NamedTemporaryFile(mode="w+", delete=False, suffix=".log") as tmp:
        dev_log(tmp, "TEST-LOC", 5, "TEST CMD", 0, 123, "test message")
        tmp.flush()

        # Read back the log
        with open(tmp.name, "r") as f:
            content = f.read()

        assert "TEST-LOC" in content
        assert "Z5" in content
        assert "TEST CMD" in content
        assert "test message" in content
        assert "|" in content  # Check format

        # Clean up
        os.unlink(tmp.name)


def test_dev_logger_redaction():
    """Test that secrets are properly redacted."""
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))

    from core.dev_logger import _redact_secrets

    # Test environment variable redaction
    assert _redact_secrets("secret=${API_KEY}") == "secret=[REDACTED_ENV]"
    assert _redact_secrets("value=$TOKEN") == "value=[REDACTED_ENV]"

    # Test secret pattern redaction
    assert "[REDACTED_SECRET]" in _redact_secrets("apikey=abc123")
    assert "[REDACTED_SECRET]" in _redact_secrets("token: secret_value")


def test_copilot_summary_basic():
    """Test that copilot summary generation works."""
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))

    from core.copilot_summary import generate_summary

    # This should not raise an exception
    log_path = generate_summary("test summary", 100, 0, "TEST-LOC", 1)

    # Check file was created
    assert log_path.exists()

    # Check content
    with open(log_path, "r") as f:
        content = f.read()

    assert "DEV SUMMARY" in content
    assert "test summary" in content
    assert "TEST-LOC" in content
    assert "Z1" in content


if __name__ == "__main__":
    pytest.main([__file__])
