"""
uDOS Transport Policy Validator
Alpha v1.0.0.2+

Runtime enforcement of transport policy rules.
Validates all operations against roles.yaml, capabilities.yaml, and policy.yaml.

CRITICAL: This is the enforcement layer - all operations MUST pass through here.
"""

import yaml
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from enum import Enum
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


class ExposureTier(Enum):
    """Command exposure tier"""

    LOCAL = "LOCAL"
    PRIVATE_SAFE = "PRIVATE_SAFE"
    WIZARD_ONLY = "WIZARD_ONLY"


class ValidationResult(Enum):
    """Validation result status"""

    PERMITTED = "permitted"
    REJECTED = "rejected"
    REJECTED_AND_AUDIT = "rejected_and_audit"
    PERMITTED_WITH_WARNING = "permitted_with_warning"


@dataclass
class ValidationError:
    """Policy validation error"""

    code: str
    message: str
    severity: str
    rule: str
    recommendation: Optional[str] = None


class PolicyValidator:
    """
    Transport policy validator and enforcer.

    Loads policy from YAML files and validates operations at runtime.
    """

    def __init__(self):
        """Initialize policy validator"""
        self.security_dir = Path(__file__).parent.parent.parent / "core" / "security"
        self.transport_dir = Path(__file__).parent

        # Load policy files
        self.roles = self._load_yaml(self.security_dir / "roles.yaml")
        self.capabilities = self._load_yaml(self.security_dir / "capabilities.yaml")
        self.policy = self._load_yaml(self.transport_dir / "policy.yaml")

        logger.info("[POLICY] Transport policy validator initialized")

    def _load_yaml(self, path: Path) -> Dict:
        """Load YAML policy file"""
        if not path.exists():
            logger.warning(f"[POLICY] Policy file not found: {path}")
            return {}

        with open(path, "r") as f:
            return yaml.safe_load(f)

    def validate_command(
        self, command: str, role: str, transport: str, realm: str = "user_mesh"
    ) -> Tuple[ValidationResult, Optional[ValidationError]]:
        """
        Validate if a command can be executed over a transport by a role.

        Args:
            command: Command name (e.g., 'FILE', 'MESH', 'WEB')
            role: Role executing command (e.g., 'device_owner', 'wizard_server')
            transport: Transport used (e.g., 'meshcore', 'internet')
            realm: Realm context ('user_mesh' or 'wizard_server')

        Returns:
            (ValidationResult, Optional[ValidationError])
        """
        # Get command binding
        command_binding = self.capabilities.get("command_bindings", {}).get(command)
        if not command_binding:
            return (
                ValidationResult.REJECTED,
                ValidationError(
                    code="UNKNOWN_COMMAND",
                    message=f"Command '{command}' not found in policy",
                    severity="ERROR",
                    rule="command_existence",
                ),
            )

        # Check exposure tier
        tier = ExposureTier(command_binding["exposure_tier"])
        tier_check = self._validate_exposure_tier(tier, transport, realm)
        if tier_check:
            return (ValidationResult.REJECTED, tier_check)

        # Check role capabilities
        required_caps = command_binding.get("required_capabilities", [])
        role_check = self._validate_role_capabilities(role, required_caps)
        if role_check:
            return (ValidationResult.REJECTED, role_check)

        # Check transport rules
        transport_check = self._validate_transport(transport, command_binding, realm)
        if transport_check:
            return (ValidationResult.REJECTED_AND_AUDIT, transport_check)

        # Check Bluetooth Public violations (CRITICAL)
        if transport == "bluetooth_public":
            return (
                ValidationResult.REJECTED_AND_AUDIT,
                ValidationError(
                    code="BT_PUBLIC_VIOLATION",
                    message="Bluetooth Public NEVER allows data or commands",
                    severity="CRITICAL",
                    rule="bluetooth_public_strict",
                    recommendation="Use Bluetooth Private for data transfer",
                ),
            )

        return (ValidationResult.PERMITTED, None)

    def _validate_exposure_tier(
        self, tier: ExposureTier, transport: str, realm: str
    ) -> Optional[ValidationError]:
        """Validate exposure tier constraints"""
        tier_config = self.capabilities.get("exposure_tiers", {}).get(tier.value, {})

        if tier == ExposureTier.LOCAL:
            # Local operations shouldn't use any transport
            if transport != "local":
                return ValidationError(
                    code="LOCAL_TIER_VIOLATION",
                    message=f"LOCAL tier operations cannot use transport '{transport}'",
                    severity="WARNING",
                    rule="exposure_tier_enforcement",
                )

        elif tier == ExposureTier.WIZARD_ONLY:
            # Wizard operations require wizard role
            if realm != "wizard_server":
                return ValidationError(
                    code="WIZARD_ONLY_VIOLATION",
                    message="WIZARD_ONLY operations require Wizard Server role",
                    severity="ERROR",
                    rule="wizard_only_enforcement",
                    recommendation="Use Wizard Server for web/cloud operations",
                )

        return None

    def _validate_role_capabilities(
        self, role: str, required_capabilities: List[str]
    ) -> Optional[ValidationError]:
        """Validate role has required capabilities"""
        role_config = self.roles.get("roles", {}).get(role)
        if not role_config:
            return ValidationError(
                code="UNKNOWN_ROLE",
                message=f"Role '{role}' not found in policy",
                severity="ERROR",
                rule="role_existence",
            )

        role_caps = role_config.get("capabilities", [])

        for cap in required_capabilities:
            if cap not in role_caps:
                return ValidationError(
                    code="INSUFFICIENT_CAPABILITY",
                    message=f"Role '{role}' lacks required capability '{cap}'",
                    severity="ERROR",
                    rule="capability_requirement",
                    recommendation=f"Upgrade role or request capability '{cap}'",
                )

        return None

    def _validate_transport(
        self, transport: str, command_binding: Dict, realm: str
    ) -> Optional[ValidationError]:
        """Validate transport is allowed for command"""
        transport_config = self.policy.get("transports", {}).get(transport)
        if not transport_config:
            return ValidationError(
                code="UNKNOWN_TRANSPORT",
                message=f"Transport '{transport}' not found in policy",
                severity="ERROR",
                rule="transport_existence",
            )

        # Check if transport allows commands
        if not transport_config.get("commands_allowed", False):
            return ValidationError(
                code="TRANSPORT_NO_COMMANDS",
                message=f"Transport '{transport}' does not allow commands",
                severity="ERROR",
                rule="transport_capability",
                recommendation="Use a private transport (meshcore, bluetooth_private, etc.)",
            )

        # Check realm constraints
        transport_realm = transport_config.get("realm")
        if transport_realm == "wizard_server" and realm != "wizard_server":
            return ValidationError(
                code="REALM_VIOLATION",
                message=f"Transport '{transport}' is Wizard Server only",
                severity="ERROR",
                rule="realm_enforcement",
                recommendation="Use private transports for User Mesh operations",
            )

        # Check allowed transports for command
        allowed_transports = command_binding.get("transports_allowed", [])
        if allowed_transports and transport not in allowed_transports:
            return ValidationError(
                code="TRANSPORT_NOT_ALLOWED",
                message=f"Transport '{transport}' not allowed for this command",
                severity="WARNING",
                rule="command_transport_binding",
                recommendation=f"Use one of: {', '.join(allowed_transports)}",
            )

        return None

    def get_allowed_transports(self, role: str, realm: str = "user_mesh") -> List[str]:
        """
        Get list of transports allowed for a role.

        Args:
            role: Role name
            realm: Realm context

        Returns:
            List of allowed transport names
        """
        role_config = self.roles.get("roles", {}).get(role)
        if not role_config:
            return []

        return role_config.get("transport_allowed", [])

    def audit_violation(self, error: ValidationError, context: Dict):
        """
        Log policy violation for auditing.

        Args:
            error: Validation error
            context: Additional context (user, command, transport, etc.)
        """
        audit_entry = {
            "code": error.code,
            "message": error.message,
            "severity": error.severity,
            "rule": error.rule,
            "context": context,
        }

        logger.error(f"[AUDIT] Policy violation: {audit_entry}")

        # TODO: Store in audit log file
        # audit_log = Path("memory/logs/security-audit.log")
        # with open(audit_log, "a") as f:
        #     json.dump(audit_entry, f)
        #     f.write("\n")


# Singleton instance
_validator = None


def get_validator() -> PolicyValidator:
    """Get global policy validator instance"""
    global _validator
    if _validator is None:
        _validator = PolicyValidator()
    return _validator


def validate_command(
    command: str, role: str, transport: str, realm: str = "user_mesh"
) -> Tuple[ValidationResult, Optional[ValidationError]]:
    """
    Convenience function to validate a command.

    Args:
        command: Command name
        role: Role executing command
        transport: Transport used
        realm: Realm context

    Returns:
        (ValidationResult, Optional[ValidationError])
    """
    validator = get_validator()
    return validator.validate_command(command, role, transport, realm)


# Example usage
if __name__ == "__main__":
    print("🛡️  uDOS Transport Policy Validator Test\n")

    validator = get_validator()

    # Test cases
    test_cases = [
        # (command, role, transport, realm, expected)
        ("FILE", "device_owner", "local", "user_mesh", "✓"),
        ("MESH", "device_owner", "meshcore", "user_mesh", "✓"),
        (
            "WEB",
            "device_owner",
            "internet",
            "user_mesh",
            "✗",
        ),  # User mesh can't access web
        ("WEB", "wizard_server", "internet", "wizard_server", "✓"),
        (
            "FILE",
            "mobile_console",
            "qr_relay",
            "user_mesh",
            "✗",
        ),  # Mobile can't write files
        ("VIEW", "mobile_console", "qr_relay", "user_mesh", "✓"),
        (
            "MESH",
            "device_owner",
            "bluetooth_public",
            "user_mesh",
            "✗",
        ),  # BT public = signal only
    ]

    for command, role, transport, realm, expected in test_cases:
        result, error = validator.validate_command(command, role, transport, realm)

        status = "✓" if result == ValidationResult.PERMITTED else "✗"
        match = "✓" if status == expected else "✗"

        print(f"{match} {status} {command:<8} | {role:<15} | {transport:<18} | {realm}")
        if error:
            print(f"     └─ {error.code}: {error.message}")
        print()

    print("✅ Policy validation test complete")
