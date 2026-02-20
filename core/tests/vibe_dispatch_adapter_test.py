"""
Tests for Vibe Dispatch Adapter (TUI integration of CommandDispatchService).

Tests cover:
- Three-stage dispatch with confidence scoring
- Fuzzy command matching
- Shell validation
- Vibe skill routing
- Confirmation flow for medium-confidence matches
- Fallback to OK
"""

import pytest
from core.tui.vibe_dispatch_adapter import (
    VibeDispatchAdapter,
    VibeDispatchResult,
    get_vibe_adapter,
)


class TestVibeDispatchAdapter:
    """Test VibeDispatchAdapter three-stage dispatch."""

    def test_adapter_instantiation(self):
        """Test adapter can be instantiated."""
        adapter = VibeDispatchAdapter()
        assert adapter is not None
        assert adapter.dispatcher is not None
        assert adapter.skill_mapper is not None

    def test_singleton_instance(self):
        """Test get_vibe_adapter returns same instance."""
        adapter1 = get_vibe_adapter()
        adapter2 = get_vibe_adapter()
        assert adapter1 is adapter2

    def test_dispatch_empty_input(self):
        """Test dispatch rejects empty input."""
        adapter = VibeDispatchAdapter()
        result = adapter.dispatch("")
        assert result.status == "error"
        assert "Empty" in result.message

    def test_dispatch_exact_ucode_command(self):
        """Test exact match of uCODE command (100% confidence)."""
        adapter = VibeDispatchAdapter()
        result = adapter.dispatch("MAP")
        assert result.status == "success"
        assert result.command == "MAP"
        assert result.confidence == 1.0

    def test_dispatch_ucode_command_fuzzy_match(self):
        """Test fuzzy match of uCODE command (typo tolerance)."""
        adapter = VibeDispatchAdapter()
        # "MAp" should match "MAP" (distance 1)
        result = adapter.dispatch("MAp")
        assert result.status == "success"
        assert result.command == "MAP"
        assert result.confidence >= 0.95

    def test_dispatch_medium_confidence_without_confirmation(self):
        """Test medium confidence (0.80-0.95) without confirmation function."""
        adapter = VibeDispatchAdapter()
        # "HAP" ~= "HELP", "GRAB", "MAP" (distance 2)
        # Should route to "ask" skill as fallback
        result = adapter.dispatch("HAP", ask_confirm_fn=None)
        # Without confirmation function, should proceed to fallback
        assert result.status in {"fallback_ok", "vibe_routed"}

    def test_dispatch_medium_confidence_with_confirmation_yes(self):
        """Test medium confidence match with user confirming."""
        adapter = VibeDispatchAdapter()

        def mock_confirm(question, default, help_text, variant):
            # Simulate user saying "yes" to confirmation
            return "yes"

        # "MAB" ~= "MAP", "GRAB" (distance 1-2)
        result = adapter.dispatch("MAB", ask_confirm_fn=mock_confirm)
        # User confirmed, so command should execute
        assert result.status == "success"
        assert result.command is not None

    def test_dispatch_medium_confidence_with_confirmation_no(self):
        """Test medium confidence match with user declining."""
        adapter = VibeDispatchAdapter()

        def mock_confirm(question, default, help_text, variant):
            # Simulate user saying "no"
            return "no"

        # "MAB" ~= "MAP", "GRAB"
        result = adapter.dispatch("MAB", ask_confirm_fn=mock_confirm)
        # User declined, so should fallback
        assert result.status in {"fallback_ok", "vibe_routed"}

    def test_dispatch_medium_confidence_with_confirmation_skip(self):
        """Test medium confidence match with user skipping (shell fallback)."""
        adapter = VibeDispatchAdapter()

        def mock_confirm(question, default, help_text, variant):
            # Simulate user skipping to shell fallback
            return "skip"

        # "MAB" ~= "MAP", "GRAB"
        result = adapter.dispatch("MAB", ask_confirm_fn=mock_confirm)
        # User skipped, so should try shell/fallback
        assert result.status in {"fallback_ok", "vibe_routed"}

    def test_dispatch_vibe_device_skill_inference(self):
        """Test inference of device skill from keywords."""
        adapter = VibeDispatchAdapter()
        result = adapter.dispatch("list devices")
        assert result.status == "vibe_routed"
        assert result.skill == "device"
        assert result.action == "list"

    def test_dispatch_vibe_vault_skill_inference(self):
        """Test inference of vault skill from keywords."""
        adapter = VibeDispatchAdapter()
        result = adapter.dispatch("get secret password")
        assert result.status == "vibe_routed"
        assert result.skill == "vault"
        assert result.action == "get"

    def test_dispatch_vibe_workspace_skill_inference(self):
        """Test inference of workspace skill from keywords."""
        adapter = VibeDispatchAdapter()
        result = adapter.dispatch("switch workspace")
        assert result.status == "vibe_routed"
        assert result.skill == "workspace"
        assert result.action == "switch"

    def test_dispatch_vibe_network_skill_inference(self):
        """Test inference of network skill from keywords."""
        adapter = VibeDispatchAdapter()
        result = adapter.dispatch("scan network")
        assert result.status == "vibe_routed"
        assert result.skill == "network"
        assert result.action == "scan"

    def test_dispatch_shell_command_safe(self):
        """Test safe shell command passes validation."""
        adapter = VibeDispatchAdapter()
        result = adapter.dispatch("echo hello")
        assert result.status == "success"
        assert result.validation_reason == "shell_valid"
        assert result.data.get("shell_command") == "echo hello"

    def test_dispatch_fallback_to_ok(self):
        """Test fallback to OK (language model) for unmatched input."""
        adapter = VibeDispatchAdapter()
        result = adapter.dispatch("some random unmatched text")
        # Should eventually fallback to OK
        assert result.status in {"fallback_ok", "vibe_routed"}
        if result.status == "fallback_ok":
            assert "language model" in result.message.lower()

    def test_dispatch_result_to_dict(self):
        """Test VibeDispatchResult can be converted to dict."""
        result = VibeDispatchResult(
            status="success",
            command="MAP",
            confidence=1.0,
            message="Test message",
        )
        d = result.to_dict()
        assert isinstance(d, dict)
        assert d["status"] == "success"
        assert d["command"] == "MAP"
        assert d["confidence"] == 1.0


class TestVibeDispatchResultTypes:
    """Test different result types from dispatch."""

    def test_result_success_ucode(self):
        """Test success result for uCODE command."""
        adapter = VibeDispatchAdapter()
        result = adapter.dispatch("VERIFY")
        assert result.status == "success"
        assert result.command == "VERIFY"

    def test_result_vibe_routed(self):
        """Test vibe_routed result type."""
        adapter = VibeDispatchAdapter()
        result = adapter.dispatch("show all devices")
        if result.status == "vibe_routed":
            assert result.skill in {"device", "help", "ask"}
            assert isinstance(result.data, dict)

    def test_result_fallback_ok(self):
        """Test fallback_ok result type."""
        adapter = VibeDispatchAdapter()
        result = adapter.dispatch("explain this concept")
        if result.status == "fallback_ok":
            assert "ok_prompt" in result.data

    def test_result_error(self):
        """Test error result type."""
        adapter = VibeDispatchAdapter()
        result = adapter.dispatch("")
        assert result.status == "error"


class TestVibeDispatchIntegrationScenarios:
    """Test realistic integration scenarios."""

    def test_scenario_user_types_misspelled_command(self):
        """Scenario: User types 'GRAAB' (should match GRAB with confirmation)."""
        adapter = VibeDispatchAdapter()

        confirmation_asked = False

        def mock_confirm(question, default, help_text, variant):
            nonlocal confirmation_asked
            confirmation_asked = True
            return "yes"

        result = adapter.dispatch("GRAAB", ask_confirm_fn=mock_confirm)
        # Should ask for confirmation due to fuzzy match
        assert confirmation_asked or (result.status in {"success", "vibe_routed"})

    def test_scenario_user_asks_for_help(self):
        """Scenario: User asks 'help me with devices'."""
        adapter = VibeDispatchAdapter()
        result = adapter.dispatch("help me with devices")
        # Could match HELP command or device skill - both are acceptable
        assert result.status in {"vibe_routed", "fallback_ok", "success"}

    def test_scenario_user_runs_shell_command(self):
        """Scenario: User runs 'ls ~/Documents'."""
        adapter = VibeDispatchAdapter()
        result = adapter.dispatch("ls ~/Documents")
        # Should be routed as valid shell command
        assert result.status == "success"
        assert result.validation_reason == "shell_valid"

    def test_scenario_user_tries_dangerous_command(self):
        """Scenario: User tries 'rm -rf /' (dangerous)."""
        adapter = VibeDispatchAdapter()
        result = adapter.dispatch("rm -rf /")
        # Should be blocked or routed to fallback
        # Not executed directly
        assert result.status != "success" or result.validation_reason != "shell_valid"

    def test_scenario_user_queries_ok(self):
        """Scenario: User sends query 'how do I backup my data?'."""
        adapter = VibeDispatchAdapter()
        result = adapter.dispatch("how do I backup my data?")
        # Should be routed somewhere (skill or OK)
        assert result.status in {"vibe_routed", "fallback_ok"}


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
