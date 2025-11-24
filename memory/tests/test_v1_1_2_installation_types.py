"""
Test Suite for Feature 1.1.2.4: Installation Types & Integrity
v1.1.2 Phase 1: Advanced Security & Roles

Tests Clone/Spawn/Hybrid installation detection, core/extensions protection,
sandbox development mode, Wizard/Root role constraints, and integrity verification.

Test Categories:
1. Installation Detection (5 tests)
2. Core Protection (6 tests)
3. Extensions Protection (5 tests)
4. Sandbox Mode (6 tests)
5. Role Constraints (6 tests)
6. Integrity Verification (5 tests)
7. Installation Metadata (5 tests)
8. Path Protection (5 tests)
9. Development vs Production (5 tests)
10. Security Boundaries (4 tests)
11. Installation Upgrade (4 tests)
12. Integration Scenarios (3 tests)

Total: 59 tests
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import os
import hashlib
from datetime import datetime
from enum import Enum
from pathlib import Path


class InstallationType(Enum):
    """Installation type enumeration."""
    CLONE = "clone"
    SPAWN = "spawn"
    HYBRID = "hybrid"


class InstallationMode(Enum):
    """Installation mode enumeration."""
    PRODUCTION = "production"
    DEVELOPMENT = "development"
    SANDBOX = "sandbox"


class InstallationManager:
    """Installation type detection and integrity management."""

    def __init__(self, root_path="/udos"):
        self.root_path = root_path
        self.installation_type = None
        self.installation_mode = InstallationMode.PRODUCTION
        self.core_protected = True
        self.extensions_protected = True
        self.integrity_hashes = {}
        self.metadata = {
            "installed_at": datetime.now().isoformat(),
            "version": "1.1.2",
            "verified": False
        }
        self.sandbox_active = False

    def detect_installation_type(self):
        """Detect installation type (Clone/Spawn/Hybrid)."""
        # Check for .git directory (Clone)
        git_exists = os.path.exists(os.path.join(self.root_path, ".git"))

        # Check for spawn marker
        spawn_marker = os.path.join(self.root_path, ".spawn_install")
        spawn_exists = os.path.exists(spawn_marker)

        # Check for core source code
        core_source = os.path.join(self.root_path, "core/uDOS_main.py")
        has_core_source = os.path.exists(core_source)

        if git_exists and has_core_source:
            self.installation_type = InstallationType.CLONE
        elif spawn_exists and not git_exists:
            self.installation_type = InstallationType.SPAWN
        elif has_core_source and not git_exists:
            self.installation_type = InstallationType.HYBRID
        else:
            raise RuntimeError("Cannot determine installation type")

        return self.installation_type

    def get_installation_type(self):
        """Get current installation type."""
        if self.installation_type is None:
            return self.detect_installation_type()
        return self.installation_type

    def set_installation_mode(self, mode):
        """Set installation mode."""
        if not isinstance(mode, InstallationMode):
            raise ValueError(f"Invalid mode: {mode}")

        self.installation_mode = mode

        # In production, protect core and extensions
        if mode == InstallationMode.PRODUCTION:
            self.core_protected = True
            self.extensions_protected = True
            self.sandbox_active = False

        # In development, allow modifications
        elif mode == InstallationMode.DEVELOPMENT:
            self.core_protected = False
            self.extensions_protected = False
            self.sandbox_active = False

        # In sandbox, isolate modifications
        elif mode == InstallationMode.SANDBOX:
            self.core_protected = True
            self.extensions_protected = True
            self.sandbox_active = True

        return True

    def is_core_protected(self):
        """Check if core is protected."""
        return self.core_protected

    def is_extensions_protected(self):
        """Check if extensions/core is protected."""
        return self.extensions_protected

    def check_path_writable(self, path):
        """Check if path is writable based on protection rules."""
        normalized = os.path.normpath(path)

        # Core paths
        if normalized.startswith(os.path.join(self.root_path, "core")):
            if self.core_protected:
                return False

        # Core extensions
        if normalized.startswith(os.path.join(self.root_path, "extensions/core")):
            if self.extensions_protected:
                return False

        # System paths
        if normalized.startswith(os.path.join(self.root_path, "system")):
            if self.installation_mode == InstallationMode.PRODUCTION:
                return False

        # Sandbox paths
        if self.sandbox_active:
            # Only sandbox directory is writable in sandbox mode
            if not normalized.startswith(os.path.join(self.root_path, "sandbox")):
                return False

        return True

    def enforce_write_protection(self, path):
        """Enforce write protection on path."""
        if not self.check_path_writable(path):
            raise PermissionError(f"Path is write-protected: {path}")
        return True

    def compute_file_hash(self, filepath):
        """Compute SHA-256 hash of file."""
        sha256 = hashlib.sha256()

        try:
            with open(filepath, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b''):
                    sha256.update(chunk)
            return sha256.hexdigest()
        except FileNotFoundError:
            return None

    def verify_core_integrity(self, expected_hashes=None):
        """Verify core files integrity."""
        if expected_hashes is None:
            expected_hashes = {}

        core_files = [
            "core/uDOS_main.py",
            "core/uDOS_parser.py",
            "core/uDOS_commands.py"
        ]

        results = {
            "verified": True,
            "files_checked": 0,
            "mismatches": []
        }

        for file_rel in core_files:
            filepath = os.path.join(self.root_path, file_rel)

            # Compute current hash
            current_hash = self.compute_file_hash(filepath)

            if current_hash is None:
                results["verified"] = False
                results["mismatches"].append({
                    "file": file_rel,
                    "reason": "File not found"
                })
                continue

            results["files_checked"] += 1

            # Check against expected
            if file_rel in expected_hashes:
                if current_hash != expected_hashes[file_rel]:
                    results["verified"] = False
                    results["mismatches"].append({
                        "file": file_rel,
                        "expected": expected_hashes[file_rel],
                        "actual": current_hash
                    })

            # Store hash
            self.integrity_hashes[file_rel] = current_hash

        self.metadata["verified"] = results["verified"]
        self.metadata["last_verified"] = datetime.now().isoformat()

        return results

    def get_installation_info(self):
        """Get installation information."""
        return {
            "type": self.installation_type.value if self.installation_type else None,
            "mode": self.installation_mode.value,
            "core_protected": self.core_protected,
            "extensions_protected": self.extensions_protected,
            "sandbox_active": self.sandbox_active,
            "metadata": self.metadata.copy()
        }

    def check_role_allowed_in_installation(self, role_name):
        """Check if role is allowed in current installation."""
        # In SPAWN installations, no Wizard or Root roles
        if self.installation_type == InstallationType.SPAWN:
            if role_name in ["Wizard", "Root"]:
                return False

        # In SANDBOX mode, no Root role
        if self.installation_mode == InstallationMode.SANDBOX:
            if role_name == "Root":
                return False

        return True

    def enforce_role_constraint(self, role_name):
        """Enforce role constraints for installation type."""
        if not self.check_role_allowed_in_installation(role_name):
            raise PermissionError(
                f"Role '{role_name}' not allowed in {self.installation_type.value} "
                f"installation ({self.installation_mode.value} mode)"
            )
        return True

    def get_protected_paths(self):
        """Get list of protected paths."""
        protected = []

        if self.core_protected:
            protected.append(os.path.join(self.root_path, "core"))

        if self.extensions_protected:
            protected.append(os.path.join(self.root_path, "extensions/core"))

        if self.installation_mode == InstallationMode.PRODUCTION:
            protected.append(os.path.join(self.root_path, "system"))

        return protected

    def enable_sandbox(self):
        """Enable sandbox mode."""
        self.sandbox_active = True
        self.core_protected = True
        self.extensions_protected = True
        self.installation_mode = InstallationMode.SANDBOX
        return True

    def disable_sandbox(self):
        """Disable sandbox mode."""
        self.sandbox_active = False
        # Restore to previous mode (default to development)
        self.set_installation_mode(InstallationMode.DEVELOPMENT)
        return True

    def create_sandbox_workspace(self, workspace_name):
        """Create isolated sandbox workspace."""
        if not self.sandbox_active:
            raise RuntimeError("Sandbox mode not active")

        workspace_path = os.path.join(self.root_path, "sandbox", workspace_name)

        return {
            "name": workspace_name,
            "path": workspace_path,
            "created_at": datetime.now().isoformat(),
            "isolated": True
        }

    def validate_integrity(self):
        """Validate installation integrity."""
        checks = {
            "type_detected": self.installation_type is not None,
            "core_exists": os.path.exists(os.path.join(self.root_path, "core")),
            "extensions_exists": os.path.exists(os.path.join(self.root_path, "extensions")),
            "hashes_stored": len(self.integrity_hashes) > 0,
            "metadata_valid": "installed_at" in self.metadata
        }

        checks["valid"] = all(checks.values())
        return checks

    def get_upgrade_constraints(self):
        """Get constraints for upgrading installation."""
        constraints = {
            "can_upgrade": True,
            "requires_backup": True,
            "restrictions": []
        }

        # Clone installations can upgrade freely
        if self.installation_type == InstallationType.CLONE:
            constraints["restrictions"].append("Must use git pull")

        # Spawn installations are restricted
        elif self.installation_type == InstallationType.SPAWN:
            constraints["restrictions"].append("Core updates not allowed")
            constraints["restrictions"].append("Use extension updates only")

        # Hybrid installations need care
        elif self.installation_type == InstallationType.HYBRID:
            constraints["restrictions"].append("Manual core updates required")

        # Production mode requires extra checks
        if self.installation_mode == InstallationMode.PRODUCTION:
            constraints["requires_backup"] = True
            constraints["restrictions"].append("Integrity verification required")

        return constraints

    def mark_as_spawn(self):
        """Mark installation as SPAWN type."""
        spawn_marker = os.path.join(self.root_path, ".spawn_install")

        # Create marker (in real implementation)
        self.metadata["spawn_marker"] = spawn_marker
        self.installation_type = InstallationType.SPAWN

        # Apply spawn constraints
        self.core_protected = True
        self.extensions_protected = False  # Allow extension development

        return True

    def get_security_boundaries(self):
        """Get security boundaries for installation."""
        boundaries = {
            "read_only_paths": [],
            "writable_paths": [],
            "forbidden_paths": []
        }

        # Protected paths are read-only
        if self.core_protected:
            boundaries["read_only_paths"].append("core/")

        if self.extensions_protected:
            boundaries["read_only_paths"].append("extensions/core/")

        # Sandbox paths
        if self.sandbox_active:
            boundaries["writable_paths"].append("sandbox/")
            boundaries["forbidden_paths"].extend(["core/", "extensions/", "system/"])
        else:
            # Development mode allows more
            if self.installation_mode == InstallationMode.DEVELOPMENT:
                boundaries["writable_paths"].extend([
                    "extensions/custom/",
                    "memory/workspace/",
                    "sandbox/"
                ])

        return boundaries

    def check_development_mode_available(self):
        """Check if development mode is available."""
        # Only CLONE installations support full development mode
        return self.installation_type == InstallationType.CLONE

    def transition_to_production(self):
        """Transition installation to production mode."""
        # Verify integrity first
        verification = self.verify_core_integrity()

        if not verification["verified"]:
            raise RuntimeError(
                f"Cannot transition to production: {len(verification['mismatches'])} "
                "integrity issues found"
            )

        # Set production mode
        self.set_installation_mode(InstallationMode.PRODUCTION)

        # Record transition
        self.metadata["production_since"] = datetime.now().isoformat()

        return True


class TestInstallationDetection(unittest.TestCase):
    """Test installation type detection."""

    def setUp(self):
        self.manager = InstallationManager("/test_udos")

    @patch('os.path.exists')
    def test_detect_clone_installation(self, mock_exists):
        """Test detecting CLONE installation."""
        def exists_side_effect(path):
            if path.endswith(".git"):
                return True
            if path.endswith("core/uDOS_main.py"):
                return True
            return False

        mock_exists.side_effect = exists_side_effect

        install_type = self.manager.detect_installation_type()
        self.assertEqual(install_type, InstallationType.CLONE)

    @patch('os.path.exists')
    def test_detect_spawn_installation(self, mock_exists):
        """Test detecting SPAWN installation."""
        def exists_side_effect(path):
            if path.endswith(".spawn_install"):
                return True
            if path.endswith(".git"):
                return False
            return False

        mock_exists.side_effect = exists_side_effect

        install_type = self.manager.detect_installation_type()
        self.assertEqual(install_type, InstallationType.SPAWN)

    @patch('os.path.exists')
    def test_detect_hybrid_installation(self, mock_exists):
        """Test detecting HYBRID installation."""
        def exists_side_effect(path):
            if path.endswith("core/uDOS_main.py"):
                return True
            if path.endswith(".git"):
                return False
            if path.endswith(".spawn_install"):
                return False
            return False

        mock_exists.side_effect = exists_side_effect

        install_type = self.manager.detect_installation_type()
        self.assertEqual(install_type, InstallationType.HYBRID)

    def test_get_installation_type_cached(self):
        """Test installation type is cached."""
        self.manager.installation_type = InstallationType.CLONE
        self.assertEqual(self.manager.get_installation_type(), InstallationType.CLONE)

    @patch('os.path.exists')
    def test_installation_type_detection_failure(self, mock_exists):
        """Test detection failure when markers missing."""
        mock_exists.return_value = False

        with self.assertRaises(RuntimeError):
            self.manager.detect_installation_type()


class TestCoreProtection(unittest.TestCase):
    """Test core file protection."""

    def setUp(self):
        self.manager = InstallationManager("/test_udos")

    def test_core_protected_in_production(self):
        """Test core is protected in production mode."""
        self.manager.set_installation_mode(InstallationMode.PRODUCTION)
        self.assertTrue(self.manager.is_core_protected())

    def test_core_writable_in_development(self):
        """Test core is writable in development mode."""
        self.manager.set_installation_mode(InstallationMode.DEVELOPMENT)
        self.assertFalse(self.manager.is_core_protected())

    def test_core_protected_in_sandbox(self):
        """Test core is protected in sandbox mode."""
        self.manager.set_installation_mode(InstallationMode.SANDBOX)
        self.assertTrue(self.manager.is_core_protected())

    def test_core_path_write_check(self):
        """Test write check for core path."""
        self.manager.core_protected = True

        writable = self.manager.check_path_writable("/test_udos/core/uDOS_main.py")
        self.assertFalse(writable)

    def test_core_write_enforcement(self):
        """Test core write enforcement."""
        self.manager.core_protected = True

        with self.assertRaises(PermissionError):
            self.manager.enforce_write_protection("/test_udos/core/config.py")

    def test_protected_paths_list(self):
        """Test getting list of protected paths."""
        self.manager.core_protected = True

        protected = self.manager.get_protected_paths()
        self.assertIn("/test_udos/core", protected)


class TestExtensionsProtection(unittest.TestCase):
    """Test extensions/core protection."""

    def setUp(self):
        self.manager = InstallationManager("/test_udos")

    def test_extensions_protected_in_production(self):
        """Test extensions/core protected in production."""
        self.manager.set_installation_mode(InstallationMode.PRODUCTION)
        self.assertTrue(self.manager.is_extensions_protected())

    def test_extensions_writable_in_development(self):
        """Test extensions/core writable in development."""
        self.manager.set_installation_mode(InstallationMode.DEVELOPMENT)
        self.assertFalse(self.manager.is_extensions_protected())

    def test_extensions_path_write_check(self):
        """Test write check for extensions/core path."""
        self.manager.extensions_protected = True

        writable = self.manager.check_path_writable("/test_udos/extensions/core/plugin.py")
        self.assertFalse(writable)

    def test_custom_extensions_writable(self):
        """Test custom extensions are writable."""
        self.manager.set_installation_mode(InstallationMode.DEVELOPMENT)

        writable = self.manager.check_path_writable("/test_udos/extensions/custom/my_ext.py")
        self.assertTrue(writable)

    def test_extensions_in_protected_list(self):
        """Test extensions/core in protected paths."""
        self.manager.extensions_protected = True

        protected = self.manager.get_protected_paths()
        self.assertIn("/test_udos/extensions/core", protected)


class TestSandboxMode(unittest.TestCase):
    """Test sandbox development mode."""

    def setUp(self):
        self.manager = InstallationManager("/test_udos")

    def test_enable_sandbox(self):
        """Test enabling sandbox mode."""
        self.manager.enable_sandbox()

        self.assertTrue(self.manager.sandbox_active)
        self.assertEqual(self.manager.installation_mode, InstallationMode.SANDBOX)

    def test_sandbox_protects_core(self):
        """Test sandbox mode protects core."""
        self.manager.enable_sandbox()

        self.assertTrue(self.manager.core_protected)
        self.assertTrue(self.manager.extensions_protected)

    def test_sandbox_only_allows_sandbox_writes(self):
        """Test sandbox mode only allows sandbox/ writes."""
        self.manager.enable_sandbox()

        # Sandbox path writable
        self.assertTrue(
            self.manager.check_path_writable("/test_udos/sandbox/test.py")
        )

        # Core path not writable
        self.assertFalse(
            self.manager.check_path_writable("/test_udos/core/main.py")
        )

    def test_create_sandbox_workspace(self):
        """Test creating sandbox workspace."""
        self.manager.enable_sandbox()

        workspace = self.manager.create_sandbox_workspace("experiment1")

        self.assertEqual(workspace["name"], "experiment1")
        self.assertTrue(workspace["isolated"])
        self.assertIn("sandbox/experiment1", workspace["path"])

    def test_sandbox_requires_activation(self):
        """Test sandbox workspace requires activation."""
        with self.assertRaises(RuntimeError):
            self.manager.create_sandbox_workspace("test")

    def test_disable_sandbox(self):
        """Test disabling sandbox mode."""
        self.manager.enable_sandbox()
        self.manager.disable_sandbox()

        self.assertFalse(self.manager.sandbox_active)
        self.assertEqual(self.manager.installation_mode, InstallationMode.DEVELOPMENT)


class TestRoleConstraints(unittest.TestCase):
    """Test role constraints in different installations."""

    def setUp(self):
        self.manager = InstallationManager("/test_udos")

    def test_wizard_allowed_in_clone(self):
        """Test Wizard role allowed in CLONE installation."""
        self.manager.installation_type = InstallationType.CLONE

        allowed = self.manager.check_role_allowed_in_installation("Wizard")
        self.assertTrue(allowed)

    def test_wizard_denied_in_spawn(self):
        """Test Wizard role denied in SPAWN installation."""
        self.manager.installation_type = InstallationType.SPAWN

        allowed = self.manager.check_role_allowed_in_installation("Wizard")
        self.assertFalse(allowed)

    def test_root_denied_in_spawn(self):
        """Test Root role denied in SPAWN installation."""
        self.manager.installation_type = InstallationType.SPAWN

        allowed = self.manager.check_role_allowed_in_installation("Root")
        self.assertFalse(allowed)

    def test_root_denied_in_sandbox(self):
        """Test Root role denied in SANDBOX mode."""
        self.manager.enable_sandbox()

        allowed = self.manager.check_role_allowed_in_installation("Root")
        self.assertFalse(allowed)

    def test_role_constraint_enforcement(self):
        """Test enforcing role constraints."""
        self.manager.installation_type = InstallationType.SPAWN

        with self.assertRaises(PermissionError):
            self.manager.enforce_role_constraint("Wizard")

    def test_user_role_always_allowed(self):
        """Test User role always allowed."""
        self.manager.installation_type = InstallationType.SPAWN

        allowed = self.manager.check_role_allowed_in_installation("User")
        self.assertTrue(allowed)


class TestIntegrityVerification(unittest.TestCase):
    """Test installation integrity verification."""

    def setUp(self):
        self.manager = InstallationManager("/test_udos")

    @patch.object(InstallationManager, 'compute_file_hash')
    def test_verify_core_integrity(self, mock_hash):
        """Test verifying core integrity."""
        mock_hash.return_value = "abc123"

        result = self.manager.verify_core_integrity()

        self.assertIn("verified", result)
        self.assertGreater(result["files_checked"], 0)

    @patch.object(InstallationManager, 'compute_file_hash')
    def test_integrity_mismatch_detection(self, mock_hash):
        """Test detecting integrity mismatches."""
        mock_hash.return_value = "wrong_hash"

        expected = {"core/uDOS_main.py": "correct_hash"}
        result = self.manager.verify_core_integrity(expected)

        self.assertFalse(result["verified"])
        self.assertGreater(len(result["mismatches"]), 0)

    def test_compute_file_hash(self):
        """Test computing file hash."""
        # Mock file would be needed for real test
        hash_val = self.manager.compute_file_hash("/nonexistent")
        self.assertIsNone(hash_val)

    @patch.object(InstallationManager, 'compute_file_hash')
    def test_integrity_hashes_stored(self, mock_hash):
        """Test integrity hashes are stored."""
        mock_hash.return_value = "hash123"

        self.manager.verify_core_integrity()

        self.assertGreater(len(self.manager.integrity_hashes), 0)

    @patch.object(InstallationManager, 'compute_file_hash')
    def test_metadata_updated_on_verification(self, mock_hash):
        """Test metadata updated after verification."""
        mock_hash.return_value = "hash"

        self.manager.verify_core_integrity()

        self.assertIn("verified", self.manager.metadata)
        self.assertIn("last_verified", self.manager.metadata)


class TestInstallationMetadata(unittest.TestCase):
    """Test installation metadata management."""

    def setUp(self):
        self.manager = InstallationManager("/test_udos")

    def test_metadata_initialization(self):
        """Test metadata is initialized."""
        self.assertIn("installed_at", self.manager.metadata)
        self.assertIn("version", self.manager.metadata)

    def test_get_installation_info(self):
        """Test getting installation info."""
        self.manager.installation_type = InstallationType.CLONE

        info = self.manager.get_installation_info()

        self.assertEqual(info["type"], "clone")
        self.assertIn("metadata", info)

    def test_metadata_includes_protection_status(self):
        """Test metadata includes protection status."""
        info = self.manager.get_installation_info()

        self.assertIn("core_protected", info)
        self.assertIn("extensions_protected", info)

    def test_spawn_marker_in_metadata(self):
        """Test spawn marker stored in metadata."""
        self.manager.mark_as_spawn()

        self.assertIn("spawn_marker", self.manager.metadata)

    def test_production_transition_recorded(self):
        """Test production transition is recorded."""
        self.manager.installation_type = InstallationType.CLONE

        with patch.object(self.manager, 'verify_core_integrity') as mock_verify:
            mock_verify.return_value = {"verified": True, "files_checked": 3, "mismatches": []}
            self.manager.transition_to_production()

        self.assertIn("production_since", self.manager.metadata)


class TestPathProtection(unittest.TestCase):
    """Test path protection rules."""

    def setUp(self):
        self.manager = InstallationManager("/test_udos")

    def test_system_path_protected_in_production(self):
        """Test system/ path protected in production."""
        self.manager.set_installation_mode(InstallationMode.PRODUCTION)

        writable = self.manager.check_path_writable("/test_udos/system/config.py")
        self.assertFalse(writable)

    def test_memory_path_writable(self):
        """Test memory/ path is writable."""
        self.manager.set_installation_mode(InstallationMode.DEVELOPMENT)

        writable = self.manager.check_path_writable("/test_udos/memory/user/data.json")
        self.assertTrue(writable)

    def test_path_normalization(self):
        """Test path normalization."""
        self.manager.core_protected = True

        # Different path formats should normalize to same result
        writable1 = self.manager.check_path_writable("/test_udos/core/main.py")
        writable2 = self.manager.check_path_writable("/test_udos/core/../core/main.py")

        self.assertEqual(writable1, writable2)

    def test_security_boundaries(self):
        """Test getting security boundaries."""
        self.manager.enable_sandbox()

        boundaries = self.manager.get_security_boundaries()

        self.assertIn("read_only_paths", boundaries)
        self.assertIn("writable_paths", boundaries)
        self.assertIn("forbidden_paths", boundaries)

    def test_forbidden_paths_in_sandbox(self):
        """Test forbidden paths in sandbox mode."""
        self.manager.enable_sandbox()

        boundaries = self.manager.get_security_boundaries()

        self.assertIn("core/", boundaries["forbidden_paths"])


class TestDevelopmentVsProduction(unittest.TestCase):
    """Test development vs production modes."""

    def setUp(self):
        self.manager = InstallationManager("/test_udos")

    def test_development_mode_allows_core_edits(self):
        """Test development mode allows core edits."""
        self.manager.set_installation_mode(InstallationMode.DEVELOPMENT)

        writable = self.manager.check_path_writable("/test_udos/core/test.py")
        self.assertTrue(writable)

    def test_production_mode_blocks_core_edits(self):
        """Test production mode blocks core edits."""
        self.manager.set_installation_mode(InstallationMode.PRODUCTION)

        writable = self.manager.check_path_writable("/test_udos/core/test.py")
        self.assertFalse(writable)

    def test_development_mode_availability(self):
        """Test development mode availability check."""
        self.manager.installation_type = InstallationType.CLONE

        available = self.manager.check_development_mode_available()
        self.assertTrue(available)

    def test_development_mode_restricted_for_spawn(self):
        """Test development mode restricted for SPAWN."""
        self.manager.installation_type = InstallationType.SPAWN

        available = self.manager.check_development_mode_available()
        self.assertFalse(available)

    def test_production_transition_requires_verification(self):
        """Test production transition requires verification."""
        with patch.object(self.manager, 'verify_core_integrity') as mock_verify:
            mock_verify.return_value = {"verified": False, "mismatches": ["error"]}

            with self.assertRaises(RuntimeError):
                self.manager.transition_to_production()


class TestSecurityBoundaries(unittest.TestCase):
    """Test security boundaries."""

    def setUp(self):
        self.manager = InstallationManager("/test_udos")

    def test_read_only_boundaries(self):
        """Test read-only boundaries."""
        self.manager.core_protected = True

        boundaries = self.manager.get_security_boundaries()

        self.assertIn("core/", boundaries["read_only_paths"])

    def test_writable_boundaries_in_development(self):
        """Test writable boundaries in development."""
        self.manager.set_installation_mode(InstallationMode.DEVELOPMENT)

        boundaries = self.manager.get_security_boundaries()

        self.assertIn("sandbox/", boundaries["writable_paths"])

    def test_forbidden_boundaries_in_sandbox(self):
        """Test forbidden boundaries in sandbox."""
        self.manager.enable_sandbox()

        boundaries = self.manager.get_security_boundaries()

        self.assertGreater(len(boundaries["forbidden_paths"]), 0)

    def test_validate_integrity(self):
        """Test validating installation integrity."""
        self.manager.installation_type = InstallationType.CLONE

        with patch('os.path.exists') as mock_exists:
            mock_exists.return_value = True

            validation = self.manager.validate_integrity()

            self.assertIn("valid", validation)


class TestInstallationUpgrade(unittest.TestCase):
    """Test installation upgrade constraints."""

    def setUp(self):
        self.manager = InstallationManager("/test_udos")

    def test_clone_upgrade_constraints(self):
        """Test CLONE installation upgrade constraints."""
        self.manager.installation_type = InstallationType.CLONE

        constraints = self.manager.get_upgrade_constraints()

        self.assertTrue(constraints["can_upgrade"])
        self.assertIn("Must use git pull", constraints["restrictions"])

    def test_spawn_upgrade_constraints(self):
        """Test SPAWN installation upgrade constraints."""
        self.manager.installation_type = InstallationType.SPAWN

        constraints = self.manager.get_upgrade_constraints()

        self.assertIn("Core updates not allowed", constraints["restrictions"])

    def test_production_upgrade_requires_backup(self):
        """Test production mode upgrade requires backup."""
        self.manager.set_installation_mode(InstallationMode.PRODUCTION)

        constraints = self.manager.get_upgrade_constraints()

        self.assertTrue(constraints["requires_backup"])

    def test_hybrid_upgrade_constraints(self):
        """Test HYBRID installation upgrade constraints."""
        self.manager.installation_type = InstallationType.HYBRID

        constraints = self.manager.get_upgrade_constraints()

        self.assertIn("Manual core updates required", constraints["restrictions"])


class TestIntegrationScenarios(unittest.TestCase):
    """Test end-to-end installation scenarios."""

    def setUp(self):
        self.manager = InstallationManager("/test_udos")

    @patch('os.path.exists')
    def test_clone_development_workflow(self, mock_exists):
        """Test CLONE installation in development mode."""
        # Detect as CLONE
        def exists_side_effect(path):
            if path.endswith(".git"):
                return True
            if path.endswith("core/uDOS_main.py"):
                return True
            return False

        mock_exists.side_effect = exists_side_effect

        install_type = self.manager.detect_installation_type()
        self.assertEqual(install_type, InstallationType.CLONE)

        # Set development mode
        self.manager.set_installation_mode(InstallationMode.DEVELOPMENT)

        # Core should be writable
        self.assertTrue(
            self.manager.check_path_writable("/test_udos/core/test.py")
        )

        # Development mode available
        self.assertTrue(self.manager.check_development_mode_available())

    @patch('os.path.exists')
    def test_spawn_production_workflow(self, mock_exists):
        """Test SPAWN installation in production mode."""
        # Detect as SPAWN
        def exists_side_effect(path):
            if path.endswith(".spawn_install"):
                return True
            return False

        mock_exists.side_effect = exists_side_effect

        install_type = self.manager.detect_installation_type()
        self.assertEqual(install_type, InstallationType.SPAWN)

        # Set production mode
        self.manager.set_installation_mode(InstallationMode.PRODUCTION)

        # Wizard role should be denied
        with self.assertRaises(PermissionError):
            self.manager.enforce_role_constraint("Wizard")

        # Core should be protected
        self.assertTrue(self.manager.is_core_protected())

    def test_sandbox_isolation_workflow(self):
        """Test sandbox isolation workflow."""
        # Enable sandbox
        self.manager.enable_sandbox()

        # Create workspace
        workspace = self.manager.create_sandbox_workspace("exp1")
        self.assertTrue(workspace["isolated"])

        # Only sandbox writable
        self.assertTrue(
            self.manager.check_path_writable("/test_udos/sandbox/exp1/code.py")
        )

        self.assertFalse(
            self.manager.check_path_writable("/test_udos/core/main.py")
        )

        # Root role denied
        self.assertFalse(
            self.manager.check_role_allowed_in_installation("Root")
        )


if __name__ == "__main__":
    unittest.main()
