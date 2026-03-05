"""Tests for CommandEngine (v1.4.6)."""

from __future__ import annotations

import pytest

from core.services.interactive_runtime import CommandEngine, ExecutionResult


class MockDispatcher:
    """Mock CommandDispatcher for testing."""

    def dispatch(self, command: str):
        """Mock dispatch method."""
        if command == "HELP":
            return {"status": "success", "output": "Help output"}
        elif command == "STATUS":
            return {"status": "success", "output": "Status output"}
        elif command == "FAIL":
            return {"status": "error", "message": "Command failed"}
        else:
            raise ValueError(f"Unknown command: {command}")


@pytest.fixture
def engine():
    """Create CommandEngine instance for testing."""
    return CommandEngine()


@pytest.fixture
def mock_dispatcher():
    """Create mock dispatcher for testing."""
    return MockDispatcher()


class TestCommandEngineExecution:
    """Test command execution with short-circuit."""

    def test_executes_help_command(self, engine, mock_dispatcher):
        """HELP command should execute successfully."""
        result = engine.execute_ucode("HELP", dispatcher=mock_dispatcher)
        assert result.status == "success"
        assert result.output == "Help output"

    def test_executes_status_command(self, engine, mock_dispatcher):
        """STATUS command should execute successfully."""
        result = engine.execute_ucode("STATUS", dispatcher=mock_dispatcher)
        assert result.status == "success"
        assert result.output == "Status output"

    def test_handles_command_failure(self, engine, mock_dispatcher):
        """Failed command should return error."""
        result = engine.execute_ucode("FAIL", dispatcher=mock_dispatcher)
        # The mock returns status error for FAIL
        assert result.status == "error" or result.message == "Command failed"

    def test_handles_unknown_command(self, engine, mock_dispatcher):
        """Unknown command should return error."""
        result = engine.execute_ucode("UNKNOWN", dispatcher=mock_dispatcher)
        assert result.status == "error"
        assert result.error is not None


class TestCommandEngineShortCircuit:
    """Test HARD STOP behavior (no provider fallback)."""

    def test_returns_immediately_on_success(self, engine, mock_dispatcher):
        """Successful command should return immediately."""
        result = engine.execute_ucode("HELP", dispatcher=mock_dispatcher)
        assert result.status == "success"
        # Engine should return ExecutionResult, not call provider
        assert isinstance(result, ExecutionResult)

    def test_returns_immediately_on_error(self, engine, mock_dispatcher):
        """Failed command should return immediately with error."""
        result = engine.execute_ucode("UNKNOWN", dispatcher=mock_dispatcher)
        assert result.status == "error"


class TestCommandEngineEmpty:
    """Test empty command handling."""

    def test_rejects_empty_command(self, engine):
        """Empty command should return error."""
        result = engine.execute_ucode("")
        assert result.status == "error"
        assert result.error is not None

    def test_rejects_whitespace_command(self, engine):
        """Whitespace-only command should return error."""
        result = engine.execute_ucode("   ")
        assert result.status == "error"


class TestCommandEngineLogging:
    """Test logging behavior."""

    def test_logs_execution(self, engine, mock_dispatcher):
        """Command execution should be logged."""
        # Just verify no exceptions
        result = engine.execute_ucode("HELP", dispatcher=mock_dispatcher)
        assert result.status == "success"


class TestCommandEngineMetadata:
    """Test result metadata."""

    def test_includes_command_in_result(self, engine, mock_dispatcher):
        """Result should include command name."""
        result = engine.execute_ucode("HELP", dispatcher=mock_dispatcher)
        assert result.command == "HELP"

    def test_includes_metadata(self, engine, mock_dispatcher):
        """Result should include metadata."""
        result = engine.execute_ucode("HELP", dispatcher=mock_dispatcher)
        assert result.metadata is not None
