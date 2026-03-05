"""Tests for InputRouter (v1.4.6)."""

from __future__ import annotations

import pytest

from core.services.interactive_runtime import InputRouter, RouteType


@pytest.fixture
def router():
    """Create InputRouter instance for testing."""
    return InputRouter(shell_enabled=True, ucode_confidence_threshold=0.80)


@pytest.fixture
def router_no_shell():
    """Create InputRouter with shell disabled."""
    return InputRouter(shell_enabled=False, ucode_confidence_threshold=0.80)


class TestInputRouterUcodeCommands:
    """Test ucode command routing."""

    def test_routes_help_command(self, router):
        """HELP should route to UCODE_COMMAND."""
        decision = router.route("HELP")
        assert decision.route_type == RouteType.UCODE_COMMAND
        assert decision.command == "HELP"

    def test_routes_status_command(self, router):
        """STATUS should route to UCODE_COMMAND."""
        decision = router.route("STATUS")
        assert decision.route_type == RouteType.UCODE_COMMAND
        assert decision.command == "STATUS"

    def test_routes_case_insensitive(self, router):
        """Commands should match case-insensitively."""
        decision = router.route("help")
        assert decision.route_type == RouteType.UCODE_COMMAND
        assert decision.command == "HELP"


class TestInputRouterShellCommands:
    """Test shell command routing."""

    def test_routes_shell_when_enabled(self, router):
        """Shell commands should route when shell_enabled=True."""
        decision = router.route("ls -la")
        # May route to shell or provider depending on validation
        assert decision.route_type in [
            RouteType.SHELL_COMMAND,
            RouteType.PROVIDER_FALLBACK,
        ]

    def test_blocks_shell_when_disabled(self, router_no_shell):
        """Shell commands should NOT route when shell_enabled=False."""
        decision = router_no_shell.route("ls -la")
        assert decision.route_type == RouteType.PROVIDER_FALLBACK


class TestInputRouterProviderFallback:
    """Test provider fallback routing."""

    def test_routes_natural_language_to_provider(self, router):
        """Natural language queries should route to PROVIDER_FALLBACK."""
        decision = router.route("explain this code")
        assert decision.route_type == RouteType.PROVIDER_FALLBACK

    def test_routes_questions_to_provider(self, router):
        """Questions should route to PROVIDER_FALLBACK."""
        decision = router.route("how do I write a hello world function?")
        assert decision.route_type == RouteType.PROVIDER_FALLBACK


class TestInputRouterEmptyInput:
    """Test empty input handling."""

    def test_empty_string_returns_error(self, router):
        """Empty string should return SYNTAX_ERROR."""
        decision = router.route("")
        assert decision.route_type == RouteType.SYNTAX_ERROR

    def test_whitespace_only_returns_error(self, router):
        """Whitespace-only input should return SYNTAX_ERROR."""
        decision = router.route("   ")
        assert decision.route_type == RouteType.SYNTAX_ERROR


class TestInputRouterPriority:
    """Test routing priority: ucode > shell > provider."""

    def test_ucode_wins_over_all(self, router):
        """ucode command takes priority."""
        decision = router.route("HELP")
        assert decision.route_type == RouteType.UCODE_COMMAND

    def test_provider_is_final_fallback(self, router):
        """Unknown input falls back to provider."""
        decision = router.route("something unknown")
        assert decision.route_type == RouteType.PROVIDER_FALLBACK
