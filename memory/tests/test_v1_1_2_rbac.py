"""
Test Suite for Feature 1.1.2.1: User Role System (RBAC)
v1.1.2 Phase 1: Advanced Security & Roles

Tests role-based access control (RBAC) with User, Power, Wizard, Root roles.
All core functionality routes through RBAC checks including command execution,
file access, and AI/web features.

Test Categories:
1. Role Definition (5 tests)
2. Role Assignment (5 tests)
3. Command Permissions (6 tests)
4. File Access Control (6 tests)
5. AI Feature Permissions (5 tests)
6. Web Feature Permissions (5 tests)
7. Role Inspection (4 tests)
8. Role Transitions (5 tests)
9. Audit Logging (5 tests)
10. Permission Inheritance (4 tests)
11. Security Boundaries (5 tests)
12. Integration Scenarios (3 tests)

Total: 58 tests
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import json
from datetime import datetime
from enum import Enum


class Role(Enum):
    """User role enumeration."""
    USER = "user"
    POWER = "power"
    WIZARD = "wizard"
    ROOT = "root"


class Permission(Enum):
    """Permission enumeration."""
    # Command permissions
    BASIC_COMMANDS = "basic_commands"
    ADVANCED_COMMANDS = "advanced_commands"
    SYSTEM_COMMANDS = "system_commands"
    ADMIN_COMMANDS = "admin_commands"
    
    # File permissions
    READ_USER_FILES = "read_user_files"
    WRITE_USER_FILES = "write_user_files"
    READ_SYSTEM_FILES = "read_system_files"
    WRITE_SYSTEM_FILES = "write_system_files"
    
    # Feature permissions
    AI_BASIC = "ai_basic"
    AI_ADVANCED = "ai_advanced"
    WEB_FETCH = "web_fetch"
    WEB_CRAWL = "web_crawl"
    
    # Memory tier permissions
    TIER1_ACCESS = "tier1_access"
    TIER2_ACCESS = "tier2_access"
    TIER3_ACCESS = "tier3_access"
    TIER4_ACCESS = "tier4_access"
    
    # Special permissions
    ROLE_CHANGE = "role_change"
    EXTENSION_INSTALL = "extension_install"
    CONFIG_MODIFY = "config_modify"


class RBACManager:
    """Role-Based Access Control manager for uDOS."""
    
    def __init__(self, initial_role=None):
        self.current_role = initial_role or Role.USER
        self.role_permissions = self._initialize_permissions()
        self.audit_log = []
        self.role_history = []
        self.protected_paths = [
            "/core/",
            "/extensions/core/",
            "/system/"
        ]
        self.bypass_security = False  # For testing/admin operations
        
    def _initialize_permissions(self):
        """Initialize permission matrix for each role."""
        return {
            Role.USER: {
                Permission.BASIC_COMMANDS,
                Permission.READ_USER_FILES,
                Permission.WRITE_USER_FILES,
                Permission.AI_BASIC,
                Permission.TIER4_ACCESS
            },
            Role.POWER: {
                Permission.BASIC_COMMANDS,
                Permission.ADVANCED_COMMANDS,
                Permission.READ_USER_FILES,
                Permission.WRITE_USER_FILES,
                Permission.READ_SYSTEM_FILES,
                Permission.AI_BASIC,
                Permission.AI_ADVANCED,
                Permission.WEB_FETCH,
                Permission.TIER3_ACCESS,
                Permission.TIER4_ACCESS
            },
            Role.WIZARD: {
                Permission.BASIC_COMMANDS,
                Permission.ADVANCED_COMMANDS,
                Permission.SYSTEM_COMMANDS,
                Permission.READ_USER_FILES,
                Permission.WRITE_USER_FILES,
                Permission.READ_SYSTEM_FILES,
                Permission.WRITE_SYSTEM_FILES,
                Permission.AI_BASIC,
                Permission.AI_ADVANCED,
                Permission.WEB_FETCH,
                Permission.WEB_CRAWL,
                Permission.EXTENSION_INSTALL,
                Permission.CONFIG_MODIFY,
                Permission.TIER2_ACCESS,
                Permission.TIER3_ACCESS,
                Permission.TIER4_ACCESS
            },
            Role.ROOT: set(Permission)  # All permissions
        }
    
    def get_current_role(self):
        """Get current user role."""
        return self.current_role
    
    def set_role(self, role, reason=None, bypass=False):
        """Set user role with audit logging."""
        if not isinstance(role, Role):
            raise ValueError(f"Invalid role: {role}")
        
        # Check permission for role change (unless bypassing)
        if not bypass and not self.bypass_security:
            if self.current_role != Role.ROOT and role in [Role.WIZARD, Role.ROOT]:
                if not self.has_permission(Permission.ROLE_CHANGE):
                    self._log_audit("role_change_denied", {
                        "from": self.current_role.value,
                        "to": role.value,
                        "reason": "insufficient_permissions"
                    })
                    raise PermissionError(f"Cannot change to {role.value} role")
        
        old_role = self.current_role
        self.current_role = role
        
        # Log role transition
        self.role_history.append({
            "from": old_role.value,
            "to": role.value,
            "timestamp": datetime.now().isoformat(),
            "reason": reason
        })
        
        self._log_audit("role_changed", {
            "from": old_role.value,
            "to": role.value,
            "reason": reason
        })
        
        return True
    
    def has_permission(self, permission):
        """Check if current role has specific permission."""
        if not isinstance(permission, Permission):
            raise ValueError(f"Invalid permission: {permission}")
        
        return permission in self.role_permissions.get(self.current_role, set())
    
    def check_command_permission(self, command):
        """Check if user can execute command."""
        # Map commands to permission levels
        basic = ["help", "list", "read", "search", "docs"]
        advanced = ["write", "edit", "mission", "map", "inventory"]
        system = ["config", "theme", "extension", "server"]
        admin = ["role", "security", "audit", "install"]
        
        if command in basic:
            required = Permission.BASIC_COMMANDS
        elif command in advanced:
            required = Permission.ADVANCED_COMMANDS
        elif command in system:
            required = Permission.SYSTEM_COMMANDS
        elif command in admin:
            required = Permission.ADMIN_COMMANDS
        else:
            required = Permission.BASIC_COMMANDS
        
        has_perm = self.has_permission(required)
        
        self._log_audit("command_check", {
            "command": command,
            "required": required.value,
            "allowed": has_perm
        })
        
        return has_perm
    
    def check_file_access(self, path, operation="read"):
        """Check file access permissions."""
        is_protected = any(path.startswith(p) for p in self.protected_paths)
        
        if operation == "read":
            if is_protected:
                required = Permission.READ_SYSTEM_FILES
            else:
                required = Permission.READ_USER_FILES
        elif operation == "write":
            if is_protected:
                required = Permission.WRITE_SYSTEM_FILES
            else:
                required = Permission.WRITE_USER_FILES
        else:
            raise ValueError(f"Invalid operation: {operation}")
        
        has_perm = self.has_permission(required)
        
        self._log_audit("file_access_check", {
            "path": path,
            "operation": operation,
            "protected": is_protected,
            "allowed": has_perm
        })
        
        return has_perm
    
    def check_ai_permission(self, operation="basic"):
        """Check AI feature permissions."""
        if operation == "basic":
            required = Permission.AI_BASIC
        elif operation == "advanced":
            required = Permission.AI_ADVANCED
        else:
            raise ValueError(f"Invalid AI operation: {operation}")
        
        has_perm = self.has_permission(required)
        
        self._log_audit("ai_check", {
            "operation": operation,
            "allowed": has_perm
        })
        
        return has_perm
    
    def check_web_permission(self, operation="fetch"):
        """Check web feature permissions."""
        if operation == "fetch":
            required = Permission.WEB_FETCH
        elif operation == "crawl":
            required = Permission.WEB_CRAWL
        else:
            raise ValueError(f"Invalid web operation: {operation}")
        
        has_perm = self.has_permission(required)
        
        self._log_audit("web_check", {
            "operation": operation,
            "allowed": has_perm
        })
        
        return has_perm
    
    def check_tier_access(self, tier):
        """Check memory tier access permission."""
        tier_map = {
            1: Permission.TIER1_ACCESS,
            2: Permission.TIER2_ACCESS,
            3: Permission.TIER3_ACCESS,
            4: Permission.TIER4_ACCESS
        }
        
        required = tier_map.get(tier)
        if not required:
            raise ValueError(f"Invalid tier: {tier}")
        
        has_perm = self.has_permission(required)
        
        self._log_audit("tier_access_check", {
            "tier": tier,
            "allowed": has_perm
        })
        
        return has_perm
    
    def get_role_permissions(self, role=None):
        """Get permissions for specific role."""
        target_role = role or self.current_role
        if not isinstance(target_role, Role):
            raise ValueError(f"Invalid role: {target_role}")
        
        return [p.value for p in self.role_permissions.get(target_role, set())]
    
    def get_role_info(self, role=None):
        """Get detailed role information."""
        target_role = role or self.current_role
        if not isinstance(target_role, Role):
            raise ValueError(f"Invalid role: {target_role}")
        
        return {
            "role": target_role.value,
            "permissions": self.get_role_permissions(target_role),
            "is_current": target_role == self.current_role
        }
    
    def get_role_history(self):
        """Get role transition history."""
        return self.role_history.copy()
    
    def get_audit_log(self, filter_type=None):
        """Get audit log with optional filtering."""
        if filter_type:
            return [
                entry for entry in self.audit_log 
                if entry["type"] == filter_type
            ]
        return self.audit_log.copy()
    
    def _log_audit(self, event_type, data):
        """Log security audit event."""
        entry = {
            "type": event_type,
            "timestamp": datetime.now().isoformat(),
            "role": self.current_role.value,
            "data": data
        }
        self.audit_log.append(entry)
    
    def can_modify_config(self):
        """Check if user can modify configuration."""
        return self.has_permission(Permission.CONFIG_MODIFY)
    
    def can_install_extensions(self):
        """Check if user can install extensions."""
        return self.has_permission(Permission.EXTENSION_INSTALL)
    
    def get_accessible_tiers(self):
        """Get list of accessible memory tiers."""
        tiers = []
        for tier in [1, 2, 3, 4]:
            if self.check_tier_access(tier):
                tiers.append(tier)
        return tiers


class TestRoleDefinition(unittest.TestCase):
    """Test role definition and structure."""
    
    def setUp(self):
        self.rbac = RBACManager()
    
    def test_role_enumeration(self):
        """Test role enum values."""
        self.assertEqual(Role.USER.value, "user")
        self.assertEqual(Role.POWER.value, "power")
        self.assertEqual(Role.WIZARD.value, "wizard")
        self.assertEqual(Role.ROOT.value, "root")
    
    def test_permission_enumeration(self):
        """Test permission enum values."""
        self.assertEqual(Permission.BASIC_COMMANDS.value, "basic_commands")
        self.assertEqual(Permission.AI_ADVANCED.value, "ai_advanced")
        self.assertEqual(Permission.TIER1_ACCESS.value, "tier1_access")
    
    def test_role_hierarchy(self):
        """Test role hierarchy (more permissions at higher levels)."""
        user_perms = len(self.rbac.role_permissions[Role.USER])
        power_perms = len(self.rbac.role_permissions[Role.POWER])
        wizard_perms = len(self.rbac.role_permissions[Role.WIZARD])
        root_perms = len(self.rbac.role_permissions[Role.ROOT])
        
        self.assertLess(user_perms, power_perms)
        self.assertLess(power_perms, wizard_perms)
        self.assertLess(wizard_perms, root_perms)
    
    def test_root_has_all_permissions(self):
        """Test root role has all permissions."""
        all_perms = set(Permission)
        root_perms = self.rbac.role_permissions[Role.ROOT]
        self.assertEqual(root_perms, all_perms)
    
    def test_default_role(self):
        """Test default role is USER."""
        self.assertEqual(self.rbac.get_current_role(), Role.USER)


class TestRoleAssignment(unittest.TestCase):
    """Test role assignment and transitions."""
    
    def setUp(self):
        self.rbac = RBACManager()
    
    def test_set_role(self):
        """Test setting user role."""
        self.rbac.set_role(Role.POWER)
        self.assertEqual(self.rbac.get_current_role(), Role.POWER)
    
    def test_role_transition_logging(self):
        """Test role transitions are logged."""
        self.rbac.set_role(Role.POWER, reason="user_upgrade")
        history = self.rbac.get_role_history()
        
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["from"], "user")
        self.assertEqual(history[0]["to"], "power")
        self.assertEqual(history[0]["reason"], "user_upgrade")
    
    def test_invalid_role_rejection(self):
        """Test invalid role is rejected."""
        with self.assertRaises(ValueError):
            self.rbac.set_role("invalid_role")
    
    def test_privilege_escalation_denied(self):
        """Test user cannot escalate to wizard/root."""
        with self.assertRaises(PermissionError):
            self.rbac.set_role(Role.WIZARD)  # No bypass - should fail
    
    def test_root_can_change_any_role(self):
        """Test root can change to any role."""
        self.rbac.set_role(Role.ROOT, bypass=True)
        self.rbac.set_role(Role.USER)
        self.assertEqual(self.rbac.get_current_role(), Role.USER)


class TestCommandPermissions(unittest.TestCase):
    """Test command execution permissions."""
    
    def setUp(self):
        self.rbac = RBACManager()
    
    def test_user_basic_commands(self):
        """Test user role can execute basic commands."""
        self.assertTrue(self.rbac.check_command_permission("help"))
        self.assertTrue(self.rbac.check_command_permission("list"))
        self.assertTrue(self.rbac.check_command_permission("read"))
    
    def test_user_denied_advanced(self):
        """Test user role denied advanced commands."""
        self.assertFalse(self.rbac.check_command_permission("mission"))
        self.assertFalse(self.rbac.check_command_permission("edit"))
    
    def test_power_advanced_commands(self):
        """Test power role can execute advanced commands."""
        self.rbac.set_role(Role.POWER)
        self.assertTrue(self.rbac.check_command_permission("mission"))
        self.assertTrue(self.rbac.check_command_permission("edit"))
    
    def test_wizard_system_commands(self):
        """Test wizard role can execute system commands."""
        self.rbac.set_role(Role.WIZARD, bypass=True)
        self.assertTrue(self.rbac.check_command_permission("config"))
        self.assertTrue(self.rbac.check_command_permission("extension"))
    
    def test_root_admin_commands(self):
        """Test root role can execute admin commands."""
        self.rbac.set_role(Role.ROOT, bypass=True)
        self.assertTrue(self.rbac.check_command_permission("role"))
        self.assertTrue(self.rbac.check_command_permission("security"))
    
    def test_command_permission_audit(self):
        """Test command permission checks are audited."""
        self.rbac.check_command_permission("help")
        audit = self.rbac.get_audit_log("command_check")
        
        self.assertEqual(len(audit), 1)
        self.assertEqual(audit[0]["data"]["command"], "help")
        self.assertTrue(audit[0]["data"]["allowed"])


class TestFileAccessControl(unittest.TestCase):
    """Test file access control."""
    
    def setUp(self):
        self.rbac = RBACManager()
    
    def test_user_read_user_files(self):
        """Test user can read user files."""
        self.assertTrue(self.rbac.check_file_access("/user/file.txt", "read"))
    
    def test_user_write_user_files(self):
        """Test user can write user files."""
        self.assertTrue(self.rbac.check_file_access("/user/file.txt", "write"))
    
    def test_user_denied_system_read(self):
        """Test user denied system file read."""
        self.assertFalse(self.rbac.check_file_access("/core/config.py", "read"))
    
    def test_power_read_system_files(self):
        """Test power can read system files."""
        self.rbac.set_role(Role.POWER)
        self.assertTrue(self.rbac.check_file_access("/core/config.py", "read"))
    
    def test_wizard_write_system_files(self):
        """Test wizard can write system files."""
        self.rbac.set_role(Role.WIZARD, bypass=True)
        self.assertTrue(self.rbac.check_file_access("/core/config.py", "write"))
    
    def test_file_access_audit(self):
        """Test file access checks are audited."""
        self.rbac.check_file_access("/core/test.py", "read")
        audit = self.rbac.get_audit_log("file_access_check")
        
        self.assertEqual(len(audit), 1)
        self.assertEqual(audit[0]["data"]["path"], "/core/test.py")
        self.assertTrue(audit[0]["data"]["protected"])


class TestAIFeaturePermissions(unittest.TestCase):
    """Test AI feature permissions."""
    
    def setUp(self):
        self.rbac = RBACManager()
    
    def test_user_basic_ai(self):
        """Test user has basic AI access."""
        self.assertTrue(self.rbac.check_ai_permission("basic"))
    
    def test_user_denied_advanced_ai(self):
        """Test user denied advanced AI."""
        self.assertFalse(self.rbac.check_ai_permission("advanced"))
    
    def test_power_advanced_ai(self):
        """Test power role has advanced AI."""
        self.rbac.set_role(Role.POWER)
        self.assertTrue(self.rbac.check_ai_permission("advanced"))
    
    def test_ai_permission_audit(self):
        """Test AI permissions are audited."""
        self.rbac.check_ai_permission("basic")
        audit = self.rbac.get_audit_log("ai_check")
        
        self.assertEqual(len(audit), 1)
        self.assertEqual(audit[0]["data"]["operation"], "basic")
    
    def test_invalid_ai_operation(self):
        """Test invalid AI operation rejected."""
        with self.assertRaises(ValueError):
            self.rbac.check_ai_permission("invalid")


class TestWebFeaturePermissions(unittest.TestCase):
    """Test web feature permissions."""
    
    def setUp(self):
        self.rbac = RBACManager()
    
    def test_user_denied_web_fetch(self):
        """Test user denied web fetch."""
        self.assertFalse(self.rbac.check_web_permission("fetch"))
    
    def test_power_web_fetch(self):
        """Test power role can fetch from web."""
        self.rbac.set_role(Role.POWER)
        self.assertTrue(self.rbac.check_web_permission("fetch"))
    
    def test_power_denied_web_crawl(self):
        """Test power denied web crawling."""
        self.rbac.set_role(Role.POWER)
        self.assertFalse(self.rbac.check_web_permission("crawl"))
    
    def test_wizard_web_crawl(self):
        """Test wizard can crawl web."""
        self.rbac.set_role(Role.WIZARD, bypass=True)
        self.assertTrue(self.rbac.check_web_permission("crawl"))
    
    def test_web_permission_audit(self):
        """Test web permissions are audited."""
        self.rbac.set_role(Role.POWER)
        self.rbac.check_web_permission("fetch")
        audit = self.rbac.get_audit_log("web_check")
        
        self.assertEqual(len(audit), 1)
        self.assertEqual(audit[0]["data"]["operation"], "fetch")


class TestRoleInspection(unittest.TestCase):
    """Test role inspection capabilities."""
    
    def setUp(self):
        self.rbac = RBACManager()
    
    def test_get_role_info(self):
        """Test getting role information."""
        info = self.rbac.get_role_info()
        self.assertEqual(info["role"], "user")
        self.assertIn("permissions", info)
        self.assertTrue(info["is_current"])
    
    def test_get_other_role_info(self):
        """Test inspecting other role info."""
        info = self.rbac.get_role_info(Role.WIZARD)
        self.assertEqual(info["role"], "wizard")
        self.assertFalse(info["is_current"])
    
    def test_get_role_permissions(self):
        """Test getting role permissions list."""
        perms = self.rbac.get_role_permissions()
        self.assertIn("basic_commands", perms)
        self.assertIn("read_user_files", perms)
    
    def test_accessible_tiers(self):
        """Test getting accessible memory tiers."""
        tiers = self.rbac.get_accessible_tiers()
        self.assertEqual(tiers, [4])  # User only has tier 4


class TestRoleTransitions(unittest.TestCase):
    """Test role transition workflows."""
    
    def setUp(self):
        self.rbac = RBACManager()
    
    def test_user_to_power(self):
        """Test user to power transition."""
        self.rbac.set_role(Role.POWER)
        self.assertEqual(self.rbac.get_current_role(), Role.POWER)
    
    def test_power_to_wizard_denied(self):
        """Test power to wizard denied without permission."""
        self.rbac.set_role(Role.POWER)
        with self.assertRaises(PermissionError):
            self.rbac.set_role(Role.WIZARD)  # No bypass - should fail
    
    def test_root_downgrade(self):
        """Test root can downgrade to any role."""
        self.rbac.set_role(Role.ROOT, bypass=True)
        self.rbac.set_role(Role.USER)
        self.assertEqual(self.rbac.get_current_role(), Role.USER)
    
    def test_role_history_tracking(self):
        """Test role history tracks all transitions."""
        self.rbac.set_role(Role.POWER, "upgrade")
        self.rbac.set_role(Role.ROOT, "admin_task", bypass=True)
        
        history = self.rbac.get_role_history()
        self.assertEqual(len(history), 2)
        self.assertEqual(history[1]["to"], "root")
    
    def test_transition_audit_logging(self):
        """Test transitions are audit logged."""
        self.rbac.set_role(Role.POWER)
        audit = self.rbac.get_audit_log("role_changed")
        
        self.assertEqual(len(audit), 1)
        self.assertEqual(audit[0]["data"]["to"], "power")


class TestAuditLogging(unittest.TestCase):
    """Test comprehensive audit logging."""
    
    def setUp(self):
        self.rbac = RBACManager()
    
    def test_audit_log_structure(self):
        """Test audit log entry structure."""
        self.rbac.check_command_permission("help")
        audit = self.rbac.get_audit_log()
        
        entry = audit[0]
        self.assertIn("type", entry)
        self.assertIn("timestamp", entry)
        self.assertIn("role", entry)
        self.assertIn("data", entry)
    
    def test_audit_log_filtering(self):
        """Test filtering audit log by type."""
        self.rbac.check_command_permission("help")
        self.rbac.check_file_access("/test", "read")
        
        cmd_audit = self.rbac.get_audit_log("command_check")
        file_audit = self.rbac.get_audit_log("file_access_check")
        
        self.assertEqual(len(cmd_audit), 1)
        self.assertEqual(len(file_audit), 1)
    
    def test_denied_access_logged(self):
        """Test denied access is logged."""
        self.rbac.check_ai_permission("advanced")
        audit = self.rbac.get_audit_log("ai_check")
        
        self.assertFalse(audit[0]["data"]["allowed"])
    
    def test_audit_timestamp(self):
        """Test audit entries have timestamps."""
        self.rbac.check_command_permission("help")
        audit = self.rbac.get_audit_log()
        
        self.assertIn("timestamp", audit[0])
        # Verify ISO format
        datetime.fromisoformat(audit[0]["timestamp"])
    
    def test_audit_role_tracking(self):
        """Test audit tracks current role."""
        self.rbac.set_role(Role.POWER)
        self.rbac.check_command_permission("mission")
        audit = self.rbac.get_audit_log("command_check")
        
        self.assertEqual(audit[0]["role"], "power")


class TestPermissionInheritance(unittest.TestCase):
    """Test permission inheritance across roles."""
    
    def setUp(self):
        self.rbac = RBACManager()
    
    def test_power_inherits_user_permissions(self):
        """Test power role has all user permissions."""
        user_perms = self.rbac.role_permissions[Role.USER]
        power_perms = self.rbac.role_permissions[Role.POWER]
        
        self.assertTrue(user_perms.issubset(power_perms))
    
    def test_wizard_inherits_power_permissions(self):
        """Test wizard role has all power permissions."""
        power_perms = self.rbac.role_permissions[Role.POWER]
        wizard_perms = self.rbac.role_permissions[Role.WIZARD]
        
        self.assertTrue(power_perms.issubset(wizard_perms))
    
    def test_root_has_all_role_permissions(self):
        """Test root has all permissions from all roles."""
        for role in [Role.USER, Role.POWER, Role.WIZARD]:
            role_perms = self.rbac.role_permissions[role]
            root_perms = self.rbac.role_permissions[Role.ROOT]
            self.assertTrue(role_perms.issubset(root_perms))
    
    def test_tier_access_hierarchy(self):
        """Test tier access follows hierarchy."""
        self.rbac.set_role(Role.WIZARD, bypass=True)
        accessible = self.rbac.get_accessible_tiers()
        
        # Wizard has tiers 2, 3, 4
        self.assertIn(2, accessible)
        self.assertIn(3, accessible)
        self.assertIn(4, accessible)


class TestSecurityBoundaries(unittest.TestCase):
    """Test security boundaries and edge cases."""
    
    def setUp(self):
        self.rbac = RBACManager()
    
    def test_protected_paths(self):
        """Test protected path detection."""
        self.assertFalse(self.rbac.check_file_access("/core/test.py", "write"))
        self.assertFalse(self.rbac.check_file_access("/extensions/core/ext.py", "write"))
    
    def test_config_modification_restricted(self):
        """Test config modification requires permission."""
        self.assertFalse(self.rbac.can_modify_config())
        
        self.rbac.set_role(Role.WIZARD, bypass=True)
        self.assertTrue(self.rbac.can_modify_config())
    
    def test_extension_install_restricted(self):
        """Test extension install requires permission."""
        self.assertFalse(self.rbac.can_install_extensions())
        
        self.rbac.set_role(Role.WIZARD, bypass=True)
        self.assertTrue(self.rbac.can_install_extensions())
    
    def test_tier1_restricted(self):
        """Test Tier 1 (private) is restricted."""
        self.assertFalse(self.rbac.check_tier_access(1))
        
        self.rbac.set_role(Role.ROOT, bypass=True)
        self.assertTrue(self.rbac.check_tier_access(1))
    
    def test_invalid_permission_check(self):
        """Test invalid permission raises error."""
        with self.assertRaises(ValueError):
            self.rbac.has_permission("invalid")


class TestIntegrationScenarios(unittest.TestCase):
    """Test end-to-end RBAC scenarios."""
    
    def setUp(self):
        self.rbac = RBACManager()
    
    def test_user_workflow(self):
        """Test typical user workflow."""
        # User can do basic operations
        self.assertTrue(self.rbac.check_command_permission("help"))
        self.assertTrue(self.rbac.check_file_access("/user/notes.txt", "read"))
        self.assertTrue(self.rbac.check_ai_permission("basic"))
        
        # But is restricted
        self.assertFalse(self.rbac.check_command_permission("config"))
        self.assertFalse(self.rbac.check_web_permission("fetch"))
        self.assertFalse(self.rbac.check_tier_access(1))
    
    def test_power_user_workflow(self):
        """Test power user workflow."""
        self.rbac.set_role(Role.POWER)
        
        # Can do advanced operations
        self.assertTrue(self.rbac.check_command_permission("mission"))
        self.assertTrue(self.rbac.check_ai_permission("advanced"))
        self.assertTrue(self.rbac.check_web_permission("fetch"))
        self.assertTrue(self.rbac.check_file_access("/core/data.json", "read"))
        
        # Still restricted from system changes
        self.assertFalse(self.rbac.can_modify_config())
        self.assertFalse(self.rbac.check_web_permission("crawl"))
    
    def test_admin_workflow(self):
        """Test admin (wizard/root) workflow."""
        self.rbac.set_role(Role.WIZARD, bypass=True)
        
        # Full system access
        self.assertTrue(self.rbac.check_command_permission("config"))
        self.assertTrue(self.rbac.can_modify_config())
        self.assertTrue(self.rbac.can_install_extensions())
        self.assertTrue(self.rbac.check_file_access("/core/system.py", "write"))
        self.assertTrue(self.rbac.check_web_permission("crawl"))
        
        # Audit trail
        audit = self.rbac.get_audit_log()
        self.assertGreater(len(audit), 0)


if __name__ == "__main__":
    unittest.main()
