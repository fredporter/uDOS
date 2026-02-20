"""Three-stage command dispatch service for uCLI.

Dispatches user input through:
1. uCODE command matching (high confidence)
2. Shell passthrough (syntax safe)
3. Vibe skill fallback (AI handling)
"""

from __future__ import annotations

import re
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass

from core.services.logging_manager import get_logger

logger = get_logger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# UCODE Registry (Authoritative from core/tui/dispatcher.py)
# ─────────────────────────────────────────────────────────────────────────────

UCODE_COMMANDS = {
    # Navigation (5)
    "MAP", "ANCHOR", "GRID", "PANEL", "GOTO", "FIND",
    # Information (2)
    "TELL", "BAG",
    # Interaction (3)
    "GRAB", "SPAWN", "TALK",
    # Persistor (2)
    "SAVE", "LOAD",
    # System (4)
    "HELP", "HEALTH", "VERIFY", "CONFIG",
    # Wizard (2)
    "WIZARD", "SETUP",
    # Extensions (3)
    "EMPIRE", "SONIC", "MUSIC",
    # Workspace (1)
    "BINDER",
    # Files (1)
    "FILE",
    # Rendering (1)
    "DRAW",
    # Ops (3)
    "RUN", "SCHEDULE", "RULE",
    # Data (3)
    "READ", "MIGRATE", "COMPOST",
    # Vault/Storage (1)
    "LIBRARY",
    # Admin (6)
    "REBOOT", "SETUP", "REPAIR", "DESTROY", "UNDO", "CLEAN",
    # TUI (3)
    "THEME", "SKIN", "VIEWPORT",
    # Dev (3)
    "DEV", "LOGS", "SCHEDULER",
    # User (2)
    "USER", "PLAY",
    # Script (1)
    "SCRIPT",
    # Utility (5)
    "UID", "TOKEN", "GHOST", "RESTART", "NPC",
}

# Subcommands that expand a parent command (for fuzzy matching)
SUBCOMMAND_ALIASES = {
    "PAT": "DRAW",
    "PATTERN": "DRAW",
    "DATA": "RUN",
    "EDIT": "FILE",
    "NEW": "FILE",
}


# ─────────────────────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class DispatchConfig:
    """Dispatch service configuration."""
    shell_enabled: bool = True
    shell_timeout_sec: float = 5.0
    shell_blocklist: set[str] = None
    shell_allowlist: set[str] = None
    vibe_timeout_sec: float = 2.0
    debug: bool = False

    def __post_init__(self):
        if self.shell_blocklist is None:
            self.shell_blocklist = {
                # Command injection
                "nc", "ncat", "netcat", "curl", "wget", "xargs",
                # Privilege escalation
                "sudo", "su", "chmod", "chown",
                # Filesystem abuse
                "rm", "dd", "mkfs", "fdisk", "parted",
                # Data exfiltration
                "scp", "sftp", "rsync", "tar",
            }
        if self.shell_allowlist is None:
            self.shell_allowlist = {
                "ls", "cat", "echo", "grep", "head", "tail", "wc",
                "find", "pwd", "cd", "mkdir", "touch", "cp", "mv",
                "sort", "uniq", "cut", "awk", "sed", "diff", "less",
                "git", "python", "node", "npm", "make",
            }


# ─────────────────────────────────────────────────────────────────────────────
# Stage 1: uCODE Command Matching
# ─────────────────────────────────────────────────────────────────────────────

def _levenshtein_distance(a: str, b: str) -> int:
    """Compute Levenshtein distance between two strings."""
    if len(a) < len(b):
        return _levenshtein_distance(b, a)

    if len(b) == 0:
        return len(a)

    previous_row = range(len(b) + 1)
    for i, c1 in enumerate(a):
        current_row = [i + 1]
        for j, c2 in enumerate(b):
            # j+1 instead of j since previous_row and current_row are one character longer
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]


def match_ucode_command(user_input: str) -> Tuple[Optional[str], float]:
    """
    Stage 1: Match uCODE command with confidence score.

    Args:
        user_input: Raw user input string

    Returns:
        (command, confidence) where confidence ∈ [0.0, 1.0]
    """
    if not user_input:
        return None, 0.0

    tokens = user_input.strip().split(None, 1)
    first_token = tokens[0].upper() if tokens else ""

    if not first_token:
        return None, 0.0

    # Handle subcommand aliases (e.g., EDIT → FILE, PAT → DRAW)
    if first_token in SUBCOMMAND_ALIASES:
        first_token = SUBCOMMAND_ALIASES[first_token]

    # Exact match
    if first_token in UCODE_COMMANDS:
        return first_token, 1.0

    # Fuzzy match (Levenshtein distance ≤ 2)
    candidates: list[Tuple[str, int]] = []
    for cmd in UCODE_COMMANDS:
        dist = _levenshtein_distance(first_token, cmd)
        if dist <= 2:
            candidates.append((cmd, dist))

    if candidates:
        # Pick closest candidate; break ties alphabetically
        best = min(candidates, key=lambda x: (x[1], x[0]))
        # Confidence: inversely proportional to distance
        confidence = max(0.80, 1.0 - (best[1] * 0.1))
        return best[0], confidence

    return None, 0.0


# ─────────────────────────────────────────────────────────────────────────────
# Stage 2: Shell Validation
# ─────────────────────────────────────────────────────────────────────────────

def validate_shell_command(user_input: str, config: DispatchConfig) -> Tuple[bool, str]:
    """
    Stage 2: Validate shell command for syntax and safety.

    Args:
        user_input: Raw user input string
        config: Dispatch configuration

    Returns:
        (is_safe, reason)
    """
    if not user_input:
        return False, "Empty command"

    # Quick syntax check: basic shell metacharacters
    if not re.match(r"^[a-zA-Z0-9_\-./:\s]*$", user_input):
        # Allow pipes, redirects, variables for more complex commands
        if re.match(r"[|&;<>$`]", user_input):
            return False, "Complex shell syntax detected (pipes, redirects, variables)"

    # Extract first token
    tokens = user_input.split(None, 1)
    first_cmd = tokens[0] if tokens else ""

    if not first_cmd:
        return False, "No command found"

    # Strip common path prefixes
    first_cmd = first_cmd.lstrip("./")

    # Check blocklist
    if first_cmd.lower() in {cmd.lower() for cmd in config.shell_blocklist}:
        return False, f"Command '{first_cmd}' is blocked for safety"

    # If allowlist is strict, enforce it
    if config.shell_allowlist:
        if first_cmd.lower() not in {cmd.lower() for cmd in config.shell_allowlist}:
            return False, f"Command '{first_cmd}' is not in allowlist"

    # Pattern safety checks
    dangerous_patterns = [
        (r";\s*rm\s+-rf", "rm -rf pattern detected"),
        (r">\s*/dev/", "direct device write detected"),
        (r"\$\(.*\)", "command substitution detected"),
        (r"`.*`", "backtick substitution detected"),
    ]

    for pattern, reason in dangerous_patterns:
        if re.search(pattern, user_input, re.IGNORECASE):
            return False, reason

    return True, "Safe command"


# ─────────────────────────────────────────────────────────────────────────────
# Stage 3: Vibe Skill Routing
# ─────────────────────────────────────────────────────────────────────────────

def infer_vibe_skill(user_input: str) -> str:
    """
    Stage 3: Infer Vibe skill from user input.

    Attempts to categorize input into a skill namespace.

    Args:
        user_input: Raw user input string

    Returns:
        Skill name (e.g., "device", "vault", "ask")
    """
    lower = user_input.lower()

    # Heuristic skill inference based on keywords
    skill_patterns = {
        "device": [
            r"\b(device|machine|computer|node|host)\b",
            r"\b(list|status|add|update|health)\s+(device|machine)",
        ],
        "vault": [
            r"\b(vault|secret|token|password|key)\b",
            r"\b(get|set|store|retrieve)\s+(secret|token|password)",
        ],
        "workspace": [
            r"\b(workspace|project|environment)\b",
            r"\b(switch|change|create|list)\s+(workspace|project)",
        ],
        "wizard": [
            r"\b(wizard|automation|task|workflow)\b",
            r"\b(start|stop|run|execute|automate)\s+(wizard|task)",
        ],
        "network": [
            r"\b(network|connection|host|endpoint)\b",
            r"\b(scan|connect|check)\s+(network|connection|host)",
        ],
        "script": [
            r"\b(script|flow|rule|automation)\b",
            r"\b(run|execute|test)\s+(script|flow)",
        ],
        "user": [
            r"\b(user|account|profile|identity)\b",
            r"\b(add|remove|manage|create)\s+(user|account)",
        ],
        "help": [
            r"\b(help|guide|tutorial|documentation|reference)\b",
            r"\b(what|how|where|when|why)\s+(help|guide)",
        ],
    }

    for skill, patterns in skill_patterns.items():
        for pattern in patterns:
            if re.search(pattern, lower):
                return skill

    # Default: general query
    return "ask"


# ─────────────────────────────────────────────────────────────────────────────
# Main Dispatcher
# ─────────────────────────────────────────────────────────────────────────────

class CommandDispatchService:
    """Three-stage command dispatch service."""

    def __init__(self, config: Optional[DispatchConfig] = None):
        """Initialize dispatcher with configuration."""
        self.config = config or DispatchConfig()
        self.logger = get_logger("dispatch-service")

    def dispatch(self, user_input: str) -> Dict[str, Any]:
        """
        Dispatch user input through three-stage chain.

        Args:
            user_input: Raw user input from REPL

        Returns:
            Result dictionary with keys:
            - status: "success", "error", "pending"
            - stage: 1, 2, or 3 (which stage handled it)
            - command: (Stage 1) Command name
            - confidence: (Stage 1) Confidence score [0.0, 1.0]
            - rendered: (any) Rendered output
            - message: (any) Status message
            - debug: (debug mode) Detailed stage reasoning
        """
        result = {
            "status": "success",
            "stage": None,
            "debug": {},
        }

        if not user_input:
            result["status"] = "error"
            result["message"] = "Command required"
            return result

        # Extract debug flag
        debug = "--dispatch-debug" in user_input
        if debug:
            user_input = user_input.replace("--dispatch-debug ", "", 1).strip()
            result["debug"]["enabled"] = True

        # ───────────────────────────────────────────────────────────────────
        # STAGE 1: uCODE Command Matching
        # ───────────────────────────────────────────────────────────────────

        self.logger.debug(f"[STAGE 1] Matching: {user_input}")
        command, confidence = match_ucode_command(user_input)

        if debug:
            result["debug"]["stage_1"] = {
                "command": command,
                "confidence": confidence,
            }

        if confidence >= 0.95:
            self.logger.debug(f"[STAGE 1] High confidence match: {command}")
            result["stage"] = 1
            result["command"] = command
            result["confidence"] = confidence
            # Mark for execution but don't execute here (let caller handle it)
            result["dispatch_to"] = "ucode"
            return result

        if confidence >= 0.80:
            self.logger.debug(f"[STAGE 1] Medium confidence match: {command}")
            result["stage"] = 1
            result["command"] = command
            result["confidence"] = confidence
            result["dispatch_to"] = "confirm"  # Ask user for confirmation
            return result

        # ───────────────────────────────────────────────────────────────────
        # STAGE 2: Shell Passthrough
        # ───────────────────────────────────────────────────────────────────

        if self.config.shell_enabled:
            self.logger.debug("[STAGE 2] Validating shell command")
            is_safe, reason = validate_shell_command(user_input, self.config)

            if debug:
                result["debug"]["stage_2"] = {
                    "is_safe": is_safe,
                    "reason": reason,
                }

            if is_safe:
                self.logger.debug(f"[STAGE 2] Safe shell command")
                result["stage"] = 2
                result["message"] = "Shell passthrough"
                result["dispatch_to"] = "shell"
                return result
            elif debug:
                self.logger.debug(f"[STAGE 2] Unsafe or invalid: {reason}")

        # ───────────────────────────────────────────────────────────────────
        # STAGE 3: Vibe Fallback
        # ───────────────────────────────────────────────────────────────────

        self.logger.debug("[STAGE 3] Routing to Vibe skill")
        skill = infer_vibe_skill(user_input)

        if debug:
            result["debug"]["stage_3"] = {
                "skill": skill,
                "input": user_input,
            }

        result["stage"] = 3
        result["skill"] = skill
        result["message"] = f"Routing to Vibe skill: {skill}"
        result["dispatch_to"] = "vibe"
        return result


# ─────────────────────────────────────────────────────────────────────────────
# Convenience Functions
# ─────────────────────────────────────────────────────────────────────────────

def dispatch_input(user_input: str, config: Optional[DispatchConfig] = None) -> Dict[str, Any]:
    """
    Dispatch user input (convenience function).

    Args:
        user_input: Raw user input
        config: Optional dispatch configuration

    Returns:
        Dispatch result dictionary
    """
    service = CommandDispatchService(config)
    return service.dispatch(user_input)
