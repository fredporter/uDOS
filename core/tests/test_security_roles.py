"""
Tests for Role-Based Access Control (RBAC) System

Tests user roles, permissions, and role management for v1.1.0.

Author: uDOS Development Team
Date: November 17, 2025
"""

import pytest
from datetime import datetime, timedelta
from core.security.roles import (
    Role, RolePermissions, RoleDefinitions, UserRole, RoleManager,
    get_role_manager
)


class TestRole:
    """Test Role enum and hierarchy"""

    def test_role_hierarchy(self):
        """Test role hierarchy comparisons"""
        assert Role.USER < Role.POWER
        assert Role.POWER < Role.WIZARD
        assert Role.WIZARD < Role.ROOT
        assert Role.USER <= Role.USER
        assert Role.ROOT >= Role.WIZARD

    def test_role_equality(self):
        """Test role equality"""
        assert Role.USER == Role.USER
        assert Role.POWER != Role.USER

    def test_role_descriptions(self):
        """Test role descriptions"""
        assert "Standard" in Role.USER.description
        assert "Extended" in Role.POWER.description
        assert "development" in Role.WIZARD.description
        assert "Emergency" in Role.ROOT.description


class TestRolePermissions:
    """Test RolePermissions class"""

    def test_user_permissions(self):
        """Test USER role permissions"""
        perms = RoleDefinitions.get_user_permissions()
        assert perms.role == Role.USER
        assert 'HELP' in perms.allowed_commands
        assert 'LIST' in perms.allowed_commands
        assert not perms.api_enabled
        assert not perms.web_enabled
        assert not perms.git_enabled

    def test_power_permissions(self):
        """Test POWER role permissions"""
        perms = RoleDefinitions.get_power_permissions()
        assert perms.role == Role.POWER
        # Should inherit USER commands
        assert 'HELP' in perms.allowed_commands
        assert 'LIST' in perms.allowed_commands
        # Should have additional commands
        assert 'API' in perms.allowed_commands
        assert 'WEB' in perms.allowed_commands
        assert perms.api_enabled
        assert perms.web_enabled
        assert perms.api_rate_limit == 100
        assert perms.web_rate_limit == 50
        assert perms.api_cost_limit == 5.0

    def test_wizard_permissions(self):
        """Test WIZARD role permissions"""
        perms = RoleDefinitions.get_wizard_permissions()
        assert perms.role == Role.WIZARD
        # Should inherit USER and POWER commands
        assert 'HELP' in perms.allowed_commands
        assert 'API' in perms.allowed_commands
        # Should have additional commands
        assert 'GIT' in perms.allowed_commands
        assert 'DEBUG' in perms.allowed_commands
        assert perms.git_enabled
        assert perms.debug_enabled
        assert perms.api_rate_limit == 500
        assert perms.web_rate_limit == 200
        assert perms.api_cost_limit == 20.0

    def test_root_permissions(self):
        """Test ROOT role permissions"""
        perms = RoleDefinitions.get_root_permissions()
        assert perms.role == Role.ROOT
        assert '*' in perms.allowed_commands
        assert '*' in perms.read_paths
        assert '*' in perms.write_paths
        assert perms.api_rate_limit == 0  # Unlimited
        assert perms.web_rate_limit == 0  # Unlimited

    def test_permission_inheritance(self):
        """Test permission inheritance"""
        user = RoleDefinitions.get_user_permissions()
        power = RolePermissions(role=Role.POWER)
        power.inherits_from(user)

        assert 'HELP' in power.allowed_commands
        assert 'LIST' in power.allowed_commands


class TestUserRole:
    """Test UserRole class"""

    def test_user_role_creation(self):
        """Test creating a user role"""
        user_role = UserRole(
            username="testuser",
            role=Role.USER,
            assigned_at=datetime.now()
        )
        assert user_role.username == "testuser"
        assert user_role.role == Role.USER
        assert not user_role.is_expired()

    def test_user_role_expiration(self):
        """Test role expiration"""
        user_role = UserRole(
            username="testuser",
            role=Role.POWER,
            assigned_at=datetime.now(),
            expires_at=datetime.now() - timedelta(hours=1)
        )
        assert user_role.is_expired()

    def test_can_execute_command(self):
        """Test command execution permissions"""
        user_role = UserRole(
            username="testuser",
            role=Role.USER,
            assigned_at=datetime.now()
        )
        assert user_role.can_execute_command('HELP')
        assert user_role.can_execute_command('LIST')
        assert not user_role.can_execute_command('API')
        assert not user_role.can_execute_command('GIT')

    def test_power_can_execute_api(self):
        """Test POWER user can execute API commands"""
        power_role = UserRole(
            username="poweruser",
            role=Role.POWER,
            assigned_at=datetime.now()
        )
        assert power_role.can_execute_command('API')
        assert power_role.can_execute_command('WEB')
        assert power_role.can_execute_command('HELP')  # Inherited from USER

    def test_wizard_can_execute_git(self):
        """Test WIZARD user can execute Git commands"""
        wizard_role = UserRole(
            username="wizard",
            role=Role.WIZARD,
            assigned_at=datetime.now()
        )
        assert wizard_role.can_execute_command('GIT')
        assert wizard_role.can_execute_command('DEBUG')
        assert wizard_role.can_execute_command('API')   # Inherited from POWER
        assert wizard_role.can_execute_command('HELP')  # Inherited from USER

    def test_root_can_execute_anything(self):
        """Test ROOT user can execute any command"""
        root_role = UserRole(
            username="root",
            role=Role.ROOT,
            assigned_at=datetime.now()
        )
        assert root_role.can_execute_command('ANYTHING')
        assert root_role.can_execute_command('CUSTOM_COMMAND')

    def test_can_access_path_read(self):
        """Test file path read access"""
        user_role = UserRole(
            username="testuser",
            role=Role.USER,
            assigned_at=datetime.now()
        )
        assert user_role.can_access_path('KNOWLEDGE/file.txt', 'read')
        assert user_role.can_access_path('docs/guide.md', 'read')
        assert not user_role.can_access_path('core/main.py', 'read')

    def test_can_access_path_write(self):
        """Test file path write access"""
        user_role = UserRole(
            username="testuser",
            role=Role.USER,
            assigned_at=datetime.now()
        )
        assert user_role.can_access_path('MEMORY/PRIVATE/notes.txt', 'write')
        assert not user_role.can_access_path('MEMORY/SHARED/config.json', 'write')
        assert not user_role.can_access_path('core/main.py', 'write')

    def test_power_write_access(self):
        """Test POWER user write access"""
        power_role = UserRole(
            username="poweruser",
            role=Role.POWER,
            assigned_at=datetime.now()
        )
        assert power_role.can_access_path('MEMORY/SHARED/file.txt', 'write')
        assert power_role.can_access_path('sandbox/test.py', 'write')
        assert not power_role.can_access_path('core/main.py', 'write')

    def test_wizard_core_read_access(self):
        """Test WIZARD user can read core files"""
        wizard_role = UserRole(
            username="wizard",
            role=Role.WIZARD,
            assigned_at=datetime.now()
        )
        assert wizard_role.can_access_path('core/main.py', 'read')
        assert wizard_role.can_access_path('extensions/core/ext.py', 'read')
        # But still can't write to core
        assert not wizard_role.can_access_path('core/main.py', 'write')

    def test_root_path_access(self):
        """Test ROOT user can access any path"""
        root_role = UserRole(
            username="root",
            role=Role.ROOT,
            assigned_at=datetime.now()
        )
        assert root_role.can_access_path('core/main.py', 'read')
        assert root_role.can_access_path('core/main.py', 'write')
        assert root_role.can_access_path('/etc/passwd', 'read')

    def test_requires_2fa(self):
        """Test 2FA requirement"""
        user_role = UserRole("user", Role.USER, datetime.now())
        power_role = UserRole("power", Role.POWER, datetime.now())
        wizard_role = UserRole("wizard", Role.WIZARD, datetime.now())
        root_role = UserRole("root", Role.ROOT, datetime.now())

        assert not user_role.requires_2fa()
        assert not power_role.requires_2fa()
        assert not wizard_role.requires_2fa()
        assert root_role.requires_2fa()

    def test_to_dict(self):
        """Test serialization to dict"""
        user_role = UserRole(
            username="testuser",
            role=Role.USER,
            assigned_at=datetime.now()
        )
        data = user_role.to_dict()
        assert data['username'] == "testuser"
        assert data['role'] == "user"
        assert 'assigned_at' in data

    def test_from_dict(self):
        """Test deserialization from dict"""
        data = {
            'username': 'testuser',
            'role': 'user',
            'assigned_at': datetime.now().isoformat(),
            'session_timeout': 3600
        }
        user_role = UserRole.from_dict(data)
        assert user_role.username == "testuser"
        assert user_role.role == Role.USER


class TestRoleManager:
    """Test RoleManager class"""

    def test_assign_role(self):
        """Test assigning a role to a user"""
        manager = RoleManager()
        user_role = manager.assign_role("testuser", Role.POWER)
        assert user_role.username == "testuser"
        assert user_role.role == Role.POWER

    def test_get_role(self):
        """Test getting user's role"""
        manager = RoleManager()
        manager.assign_role("testuser", Role.POWER)
        role = manager.get_role("testuser")
        assert role.role == Role.POWER

    def test_default_role(self):
        """Test default role for unassigned users"""
        manager = RoleManager()
        role = manager.get_role("newuser")
        assert role.role == Role.USER  # Default role

    def test_expired_role_returns_default(self):
        """Test expired role returns default"""
        manager = RoleManager()
        manager.assign_role(
            "testuser",
            Role.POWER,
            expires_at=datetime.now() - timedelta(hours=1)
        )
        role = manager.get_role("testuser")
        assert role.role == Role.USER  # Default role (expired POWER)

    def test_elevate_temporarily(self):
        """Test temporary role elevation"""
        manager = RoleManager()
        manager.assign_role("testuser", Role.USER)
        elevated = manager.elevate_temporarily("testuser", Role.POWER, duration_seconds=300)
        assert elevated.role == Role.POWER
        assert elevated.expires_at is not None

    def test_cannot_elevate_to_same_role(self):
        """Test cannot elevate to same or lower role"""
        manager = RoleManager()
        manager.assign_role("testuser", Role.POWER)
        with pytest.raises(ValueError):
            manager.elevate_temporarily("testuser", Role.POWER)
        with pytest.raises(ValueError):
            manager.elevate_temporarily("testuser", Role.USER)

    def test_cannot_elevate_to_root_without_2fa(self):
        """Test cannot elevate to ROOT without 2FA"""
        manager = RoleManager()
        manager.assign_role("testuser", Role.WIZARD)
        with pytest.raises(PermissionError):
            manager.elevate_temporarily("testuser", Role.ROOT)

    def test_revoke_role(self):
        """Test revoking a role"""
        manager = RoleManager()
        manager.assign_role("testuser", Role.POWER)
        manager.revoke_role("testuser")
        role = manager.get_role("testuser")
        assert role.role == Role.USER  # Reverted to default

    def test_list_roles(self):
        """Test listing all roles"""
        manager = RoleManager()
        manager.assign_role("user1", Role.USER)
        manager.assign_role("user2", Role.POWER)
        manager.assign_role("user3", Role.WIZARD)
        roles = manager.list_roles()
        assert len(roles) == 3

    def test_get_role_hierarchy(self):
        """Test getting role hierarchy"""
        manager = RoleManager()
        hierarchy = manager.get_role_hierarchy()
        assert hierarchy == [Role.USER, Role.POWER, Role.WIZARD, Role.ROOT]

    def test_singleton_role_manager(self):
        """Test global role manager singleton"""
        manager1 = get_role_manager()
        manager2 = get_role_manager()
        assert manager1 is manager2


class TestRoleIntegration:
    """Integration tests for complete role workflows"""

    def test_user_workflow(self):
        """Test typical USER workflow"""
        manager = RoleManager()
        user_role = manager.assign_role("alice", Role.USER)

        # Can execute basic commands
        assert user_role.can_execute_command('HELP')
        assert user_role.can_execute_command('LIST')
        assert user_role.can_execute_command('DOCS')

        # Cannot execute advanced commands
        assert not user_role.can_execute_command('API')
        assert not user_role.can_execute_command('WEB')
        assert not user_role.can_execute_command('GIT')

        # Can read knowledge
        assert user_role.can_access_path('KNOWLEDGE/guide.md', 'read')

        # Can write to private memory
        assert user_role.can_access_path('MEMORY/PRIVATE/notes.txt', 'write')

        # Cannot write to shared memory
        assert not user_role.can_access_path('MEMORY/SHARED/config.json', 'write')

    def test_power_workflow(self):
        """Test typical POWER workflow"""
        manager = RoleManager()
        power_role = manager.assign_role("bob", Role.POWER)

        # Can execute API commands
        assert power_role.can_execute_command('API')
        assert power_role.can_execute_command('WEB')

        # Can write to sandbox
        assert power_role.can_access_path('sandbox/test.py', 'write')

        # Can write to shared memory
        assert power_role.can_access_path('MEMORY/SHARED/config.json', 'write')

        # Still cannot access core
        assert not power_role.can_access_path('core/main.py', 'write')

    def test_wizard_workflow(self):
        """Test typical WIZARD workflow"""
        manager = RoleManager()
        wizard_role = manager.assign_role("charlie", Role.WIZARD)

        # Can execute git commands
        assert wizard_role.can_execute_command('GIT')
        assert wizard_role.can_execute_command('DEBUG')

        # Can read core files
        assert wizard_role.can_access_path('core/main.py', 'read')

        # Still cannot write to core
        assert not wizard_role.can_access_path('core/main.py', 'write')

    def test_temporary_elevation(self):
        """Test temporary privilege elevation"""
        manager = RoleManager()
        manager.assign_role("dave", Role.USER)

        # Initially USER
        role = manager.get_role("dave")
        assert role.role == Role.USER
        assert not role.can_execute_command('API')

        # Elevate to POWER temporarily
        elevated = manager.elevate_temporarily("dave", Role.POWER, duration_seconds=5)
        assert elevated.role == Role.POWER
        assert elevated.can_execute_command('API')

        # Wait for expiration
        import time
        time.sleep(6)

        # Should revert to USER
        role = manager.get_role("dave")
        assert role.role == Role.USER
        assert not role.can_execute_command('API')
