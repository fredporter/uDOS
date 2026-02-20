"""Tests for three-stage command dispatch.

Covers:
- Stage 1: uCODE command matching
- Stage 2: Shell validation
- Stage 3: Vibe skill routing
"""

import pytest
from core.services.command_dispatch_service import (
    CommandDispatchService,
    DispatchConfig,
    match_ucode_command,
    validate_shell_command,
    infer_vibe_skill,
)


# ─────────────────────────────────────────────────────────────────────────────
# Stage 1: uCODE Command Matching Tests
# ─────────────────────────────────────────────────────────────────────────────

class TestStage1CommandMatching:
    """Test Stage 1 uCODE command matching."""

    def test_exact_match_confidence_1_0(self):
        """Exact match should have confidence 1.0."""
        cmd, conf = match_ucode_command("HELP")
        assert cmd == "HELP"
        assert conf == 1.0

    def test_case_insensitive_match(self):
        """Command matching should be case-insensitive."""
        cmd, conf = match_ucode_command("help")
        assert cmd == "HELP"
        assert conf == 1.0

    def test_match_with_args(self):
        """Match should work with additional arguments."""
        cmd, conf = match_ucode_command("HELP commands")
        assert cmd == "HELP"
        assert conf == 1.0

    def test_fuzzy_match_typo(self):
        """Single character typo should fuzzy match with 0.80+ confidence."""
        cmd, conf = match_ucode_command("HLEP")
        assert cmd == "HELP"
        assert conf >= 0.80

    def test_fuzzy_match_typo_two_chars(self):
        """Two character distance should fuzzy match with 0.80+ confidence."""
        cmd, conf = match_ucode_command("HEPLL")
        assert cmd == "HELP"
        assert conf >= 0.80

    def test_no_match_completely_wrong(self):
        """Completely wrong command should have <0.80 confidence."""
        cmd, conf = match_ucode_command("XYZABC")
        # Either no match or very low confidence
        if cmd:
            assert conf < 0.80
        else:
            assert conf == 0.0

    def test_no_match_empty_input(self):
        """Empty input should not match."""
        cmd, conf = match_ucode_command("")
        assert cmd is None
        assert conf == 0.0

    def test_subcommand_alias_edit(self):
        """EDIT should alias to FILE."""
        cmd, conf = match_ucode_command("EDIT myfile.md")
        assert cmd == "FILE"
        assert conf == 1.0

    def test_subcommand_alias_pat(self):
        """PAT should alias to DRAW."""
        cmd, conf = match_ucode_command("PAT grid")
        assert cmd == "DRAW"
        assert conf == 1.0

    def test_all_known_commands(self):
        """All known uCODE commands should match with confidence 1.0."""
        known_commands = ["HELP", "HEALTH", "VERIFY", "PLACE", "BINDER",
                           "DRAW", "RUN", "PLAY", "RULE", "LIBRARY"]
        for cmd_name in known_commands:
            cmd, conf = match_ucode_command(cmd_name)
            assert cmd == cmd_name, f"Failed to match {cmd_name}"
            assert conf == 1.0, f"Confidence not 1.0 for {cmd_name}"


# ─────────────────────────────────────────────────────────────────────────────
# Stage 2: Shell Validation Tests
# ─────────────────────────────────────────────────────────────────────────────

class TestStage2ShellValidation:
    """Test Stage 2 shell command validation."""

    def test_simple_safe_command(self):
        """Simple commands like 'ls' should be safe."""
        config = DispatchConfig()
        is_safe, reason = validate_shell_command("ls", config)
        assert is_safe is True

    def test_command_with_args(self):
        """Commands with arguments should validate correctly."""
        config = DispatchConfig()
        is_safe, reason = validate_shell_command("ls -la /tmp", config)
        assert is_safe is True

    def test_blocklisted_command_nc(self):
        """Blocklisted commands like 'nc' should be rejected."""
        config = DispatchConfig()
        is_safe, reason = validate_shell_command("nc localhost 1234", config)
        assert is_safe is False
        assert "blocked" in reason.lower()

    def test_blocklisted_command_sudo(self):
        """Dangerous commands like 'sudo' should be rejected."""
        config = DispatchConfig()
        is_safe, reason = validate_shell_command("sudo rm -rf /", config)
        assert is_safe is False

    def test_rm_rf_pattern_detection(self):
        """rm -rf pattern should be detected."""
        config = DispatchConfig()
        is_safe, reason = validate_shell_command("rm -rf /", config)
        assert is_safe is False

    def test_command_injection_attempt(self):
        """Command injection attempts should be rejected."""
        config = DispatchConfig()
        is_safe, reason = validate_shell_command("cat file; rm important", config)
        assert is_safe is False

    def test_backtick_substitution(self):
        """Backtick command substitution should be rejected."""
        config = DispatchConfig()
        is_safe, reason = validate_shell_command("echo `whoami`", config)
        assert is_safe is False

    def test_dollar_paren_substitution(self):
        """$() command substitution should be rejected."""
        config = DispatchConfig()
        is_safe, reason = validate_shell_command("echo $(whoami)", config)
        assert is_safe is False

    def test_redirect_to_device(self):
        """Redirects to devices should be rejected."""
        config = DispatchConfig()
        is_safe, reason = validate_shell_command("echo data > /dev/sda", config)
        assert is_safe is False

    def test_empty_command(self):
        """Empty command should be rejected."""
        config = DispatchConfig()
        is_safe, reason = validate_shell_command("", config)
        assert is_safe is False

    def test_allowlist_mode_strict(self):
        """With allowlist, only allowlisted commands should pass."""
        config = DispatchConfig(shell_allowlist={"ls", "cat"})
        is_safe, _ = validate_shell_command("ls", config)
        assert is_safe is True

        is_safe, _ = validate_shell_command("rm file", config)
        assert is_safe is False

    def test_shell_disabled(self):
        """With shell disabled, validation is skipped."""
        config = DispatchConfig(shell_enabled=False)
        is_safe, reason = validate_shell_command("echo hello", config)
        # Just checking that config disabling doesn't break the function
        # (actual disabling is handled at dispatcher level)

    @pytest.mark.parametrize("cmd", ["ls", "cat", "grep", "find", "git"])
    def test_safe_commands(self, cmd):
        """Common safe commands should pass validation."""
        config = DispatchConfig()
        is_safe, _ = validate_shell_command(cmd, config)
        assert is_safe is True


# ─────────────────────────────────────────────────────────────────────────────
# Stage 3: Vibe Skill Routing Tests
# ─────────────────────────────────────────────────────────────────────────────

class TestStage3VibeSkillRouting:
    """Test Stage 3 Vibe skill inference and routing."""

    def test_infer_device_skill(self):
        """Input mentioning devices should infer device skill."""
        skill = infer_vibe_skill("list all devices")
        assert skill == "device"

    def test_infer_vault_skill(self):
        """Input mentioning vault/secrets should infer vault skill."""
        skill = infer_vibe_skill("get my api token")
        assert skill == "vault"

    def test_infer_workspace_skill(self):
        """Input mentioning workspace should infer workspace skill."""
        skill = infer_vibe_skill("switch to production workspace")
        assert skill == "workspace"

    def test_infer_wizard_skill(self):
        """Input mentioning wizard should infer wizard skill."""
        skill = infer_vibe_skill("start automation task")
        assert skill == "wizard"

    def test_infer_network_skill(self):
        """Input mentioning network should infer network skill."""
        skill = infer_vibe_skill("scan network connections")
        assert skill == "network"

    def test_infer_script_skill(self):
        """Input mentioning script should infer script skill."""
        skill = infer_vibe_skill("run my automation script")
        assert skill == "script"

    def test_infer_user_skill(self):
        """Input mentioning users should infer user skill."""
        skill = infer_vibe_skill("add new user alice")
        assert skill == "user"

    def test_infer_help_skill(self):
        """Input asking for help should infer help skill."""
        skill = infer_vibe_skill("show me the documentation")
        assert skill == "help"

    def test_default_to_ask_skill(self):
        """Unknown/unclear input should default to ask skill."""
        skill = infer_vibe_skill("xyzabc random nonsense")
        assert skill == "ask"

    def test_case_insensitive_inference(self):
        """Skill inference should be case-insensitive."""
        skill1 = infer_vibe_skill("DEVICE LIST")
        skill2 = infer_vibe_skill("device list")
        assert skill1 == skill2 == "device"


# ─────────────────────────────────────────────────────────────────────────────
# Integration Tests: Three-Stage Dispatch
# ─────────────────────────────────────────────────────────────────────────────

class TestThreeStageDispatch:
    """Test full three-stage dispatch flow."""

    def test_stage_1_high_confidence(self):
        """High confidence Stage 1 match should dispatch to ucode."""
        service = CommandDispatchService()
        result = service.dispatch("HELP")
        assert result["stage"] == 1
        assert result["dispatch_to"] == "ucode"
        assert result["confidence"] == 1.0

    def test_stage_1_medium_confidence(self):
        """Medium confidence Stage 1 match should ask for confirmation."""
        service = CommandDispatchService()
        result = service.dispatch("HLEP")
        assert result["stage"] == 1
        assert result["dispatch_to"] == "confirm"
        assert result["confidence"] >= 0.80

    def test_stage_2_safe_shell(self):
        """Safe shell command should dispatch to shell in Stage 2."""
        service = CommandDispatchService()
        result = service.dispatch("ls -la")
        assert result["stage"] == 2
        assert result["dispatch_to"] == "shell"

    def test_stage_2_unsafe_shell_rejected(self):
        """Unsafe shell command should proceed to Stage 3."""
        service = CommandDispatchService()
        result = service.dispatch("nc localhost 1234")
        # Should skip Stage 2 due to safety, so proceed to Stage 3
        # (or Stage 2 might reject it and move to Stage 3)
        if result["stage"] == 2:
            # Stage 2 accepted it (shouldn't happen)
            assert False, "Unsafe shell command should not be accepted"
        assert result["stage"] == 3

    def test_stage_3_fallback(self):
        """Unknown input should fallback to Stage 3 (Vibe)."""
        service = CommandDispatchService()
        result = service.dispatch("how do I reset my password?")
        assert result["stage"] == 3
        assert result["dispatch_to"] == "vibe"
        assert result["skill"] == "ask"

    def test_stage_3_inferred_device_skill(self):
        """Input about devices should infer device skill in Stage 3."""
        service = CommandDispatchService()
        result = service.dispatch("show me all the devices")
        assert result["stage"] == 3
        assert result["skill"] == "device"

    def test_dispatch_with_debug(self):
        """Debug mode should include debug info."""
        service = CommandDispatchService()
        result = service.dispatch("--dispatch-debug HELP")
        assert result["debug"]["enabled"] is True
        assert "stage_1" in result["debug"]

    def test_empty_input(self):
        """Empty input should return error."""
        service = CommandDispatchService()
        result = service.dispatch("")
        assert result["status"] == "error"

    def test_shell_disabled_skips_stage_2(self):
        """With shell disabled, should skip Stage 2."""
        config = DispatchConfig(shell_enabled=False)
        service = CommandDispatchService(config)
        result = service.dispatch("ls -la")
        # Should go directly to Stage 3 since Stage 2 is disabled
        assert result["stage"] == 3 or result["stage"] == 1


# ─────────────────────────────────────────────────────────────────────────────
# Latency Tests
# ─────────────────────────────────────────────────────────────────────────────

class TestDispatchLatency:
    """Test dispatch latency budgets."""

    def test_stage_1_latency(self):
        """Stage 1 dispatch should complete in <10ms."""
        import time
        service = CommandDispatchService()
        start = time.perf_counter()
        service.dispatch("HELP")
        elapsed = time.perf_counter() - start
        assert elapsed < 0.01, f"Stage 1 took {elapsed*1000}ms, should be <10ms"

    def test_stage_2_latency(self):
        """Stage 2 dispatch should complete in <50ms."""
        import time
        service = CommandDispatchService()
        start = time.perf_counter()
        service.dispatch("ls -la /tmp")
        elapsed = time.perf_counter() - start
        assert elapsed < 0.05, f"Stage 2 took {elapsed*1000}ms, should be <50ms"

    def test_stage_3_latency(self):
        """Stage 3 dispatch should complete in <500ms."""
        import time
        service = CommandDispatchService()
        start = time.perf_counter()
        service.dispatch("what is the meaning of life?")
        elapsed = time.perf_counter() - start
        assert elapsed < 0.5, f"Stage 3 took {elapsed*1000}ms, should be <500ms"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
