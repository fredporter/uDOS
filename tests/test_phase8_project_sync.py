"""Tests for Phase 8.4: Project Management Sync (Jira + Linear)."""

import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

from core.sync.jira_manager import JiraManager
from core.sync.linear_manager import LinearManager
from core.sync.project_manager_factory import ProjectManagerFactory
from core.sync.base_providers import Issue, SyncStatus
from core.sync.transformers import IssueTransformer
from core.services.vibe_sync_service import VibeSyncService


# ===================== TestProjectManagerFactory =====================


class TestProjectManagerFactory:
    """Tests for project manager factory."""

    def test_factory_create_jira_provider(self):
        """Test factory creates Jira manager."""
        provider = ProjectManagerFactory.create_provider("jira")
        assert provider is not None
        assert isinstance(provider, JiraManager)

    def test_factory_create_linear_provider(self):
        """Test factory creates Linear manager."""
        provider = ProjectManagerFactory.create_provider("linear")
        assert provider is not None
        assert isinstance(provider, LinearManager)

    def test_factory_create_unknown_provider(self):
        """Test factory returns None for unknown provider."""
        provider = ProjectManagerFactory.create_provider("unknown")
        assert provider is None

    def test_factory_available_providers(self):
        """Test factory lists available providers."""
        providers = ProjectManagerFactory.get_available_providers()
        assert "jira" in providers
        assert "linear" in providers
        assert len(providers) >= 2


# ===================== TestJiraManager =====================


class TestJiraManager:
    """Tests for Jira manager."""

    @pytest.fixture
    def jira_mgr(self):
        """Create Jira manager instance."""
        return JiraManager()

    @pytest.mark.asyncio
    async def test_jira_authenticate_success(self, jira_mgr):
        """Test successful Jira authentication."""
        credentials = {
            "instance_url": "https://company.atlassian.net",
            "email": "user@company.com",
            "api_token": "fake_token_123",
        }
        result = await jira_mgr.authenticate(credentials)
        assert result is True
        assert jira_mgr.authenticated is True
        assert jira_mgr.instance_url == "https://company.atlassian.net"

    @pytest.mark.asyncio
    async def test_jira_authenticate_missing_credentials(self, jira_mgr):
        """Test Jira authentication with missing credentials."""
        credentials = {"email": "user@company.com"}
        result = await jira_mgr.authenticate(credentials)
        assert result is False
        assert jira_mgr.authenticated is False

    @pytest.mark.asyncio
    async def test_jira_fetch_issues(self, jira_mgr):
        """Test fetching Jira issues."""
        # Authenticate first
        credentials = {
            "instance_url": "https://company.atlassian.net",
            "email": "user@company.com",
            "api_token": "fake_token",
        }
        await jira_mgr.authenticate(credentials)

        # Fetch issues
        issues = await jira_mgr.fetch_issues(
            query="project = PROJ",
            filters={"max_results": 10},
        )
        assert isinstance(issues, list)

    @pytest.mark.asyncio
    async def test_jira_fetch_issue_not_authenticated(self, jira_mgr):
        """Test fetching Jira issue when not authenticated."""
        issue = await jira_mgr.get_issue("PROJ-1")
        assert issue is None

    @pytest.mark.asyncio
    async def test_jira_handle_webhook_issue_created(self, jira_mgr):
        """Test handling Jira webhook for issue creation."""
        payload = {
            "webhookEvent": "jira:issue_created",
            "issue": {
                "key": "PROJ-123",
                "fields": {
                    "summary": "New issue",
                },
            },
        }
        result = await jira_mgr.handle_webhook(payload)
        assert result["status"] == "received"
        assert result["issue_key"] == "PROJ-123"

    @pytest.mark.asyncio
    async def test_jira_handle_webhook_issue_updated(self, jira_mgr):
        """Test handling Jira webhook for issue update."""
        payload = {
            "webhookEvent": "jira:issue_updated",
            "issue": {
                "key": "PROJ-124",
                "fields": {"summary": "Updated issue"},
            },
        }
        result = await jira_mgr.handle_webhook(payload)
        assert result["status"] == "received"
        assert result["event"] == "jira:issue_updated"

    @pytest.mark.asyncio
    async def test_jira_update_issue(self, jira_mgr):
        """Test updating a Jira issue."""
        credentials = {
            "instance_url": "https://company.atlassian.net",
            "email": "user@company.com",
            "api_token": "fake_token",
        }
        await jira_mgr.authenticate(credentials)

        result = await jira_mgr.update_issue(
            "PROJ-123",
            {"status": "Done"},
        )
        assert result is True

    @pytest.mark.asyncio
    async def test_jira_get_sync_status(self, jira_mgr):
        """Test getting Jira sync status."""
        credentials = {
            "instance_url": "https://company.atlassian.net",
            "email": "user@company.com",
            "api_token": "fake_token",
        }
        await jira_mgr.authenticate(credentials)

        status = await jira_mgr.get_sync_status()
        assert status["provider"] == "jira"
        assert status["authenticated"] is True
        assert "instance_url" in status


# ===================== TestLinearManager =====================


class TestLinearManager:
    """Tests for Linear manager."""

    @pytest.fixture
    def linear_mgr(self):
        """Create Linear manager instance."""
        return LinearManager()

    @pytest.mark.asyncio
    async def test_linear_authenticate_success(self, linear_mgr):
        """Test successful Linear authentication."""
        credentials = {"api_key": "lin_fake_key_123"}
        result = await linear_mgr.authenticate(credentials)
        assert result is True
        assert linear_mgr.authenticated is True

    @pytest.mark.asyncio
    async def test_linear_authenticate_missing_credentials(self, linear_mgr):
        """Test Linear authentication with missing credentials."""
        credentials = {}
        result = await linear_mgr.authenticate(credentials)
        assert result is False

    @pytest.mark.asyncio
    async def test_linear_fetch_issues(self, linear_mgr):
        """Test fetching Linear issues."""
        credentials = {"api_key": "lin_fake_key"}
        await linear_mgr.authenticate(credentials)

        issues = await linear_mgr.fetch_issues(
            query="",
            filters={"team_id": "team-123", "max_results": 20},
        )
        assert isinstance(issues, list)

    @pytest.mark.asyncio
    async def test_linear_fetch_issue_not_authenticated(self, linear_mgr):
        """Test fetching Linear issue when not authenticated."""
        issue = await linear_mgr.get_issue("TEAM-123")
        assert issue is None

    @pytest.mark.asyncio
    async def test_linear_handle_webhook_created(self, linear_mgr):
        """Test handling Linear webhook for issue creation."""
        payload = {
            "action": "create",
            "data": {
                "id": "issue-uuid-123",
                "identifier": "TEAM-321",
            },
        }
        result = await linear_mgr.handle_webhook(payload)
        assert result["status"] == "received"
        assert result["action"] == "create"

    @pytest.mark.asyncio
    async def test_linear_handle_webhook_updated(self, linear_mgr):
        """Test handling Linear webhook for issue update."""
        payload = {
            "action": "update",
            "data": {
                "id": "issue-uuid-124",
                "identifier": "TEAM-322",
            },
        }
        result = await linear_mgr.handle_webhook(payload)
        assert result["status"] == "received"

    @pytest.mark.asyncio
    async def test_linear_update_issue(self, linear_mgr):
        """Test updating a Linear issue."""
        credentials = {"api_key": "lin_fake_key"}
        await linear_mgr.authenticate(credentials)

        result = await linear_mgr.update_issue(
            "issue-uuid-123",
            {"title": "Updated title"},
        )
        assert result is True

    @pytest.mark.asyncio
    async def test_linear_get_sync_status(self, linear_mgr):
        """Test getting Linear sync status."""
        credentials = {"api_key": "lin_fake_key"}
        await linear_mgr.authenticate(credentials)

        status = await linear_mgr.get_sync_status()
        assert status["provider"] == "linear"
        assert status["authenticated"] is True


# ===================== TestIssueTransformer =====================


class TestIssueTransformer:
    """Tests for issue to task transformation."""

    def test_transform_jira_issue_to_task(self):
        """Test transforming Jira issue to task."""
        issue = Issue(
            id="jira-issue-1",
            key="PROJ-123",
            title="Fix bug in login",
            description="User cannot login with OAuth",
            status="In Progress",
            assignee="alice@company.com",
            created_at=datetime(2024, 1, 15, 10, 0),
            updated_at=datetime(2024, 1, 20, 14, 30),
            due_date=datetime(2024, 1, 31),
            url="https://company.atlassian.net/browse/PROJ-123",
            provider="jira",
            custom_fields={"story_points": 5, "epic": "Auth"},
        )

        task = IssueTransformer.issue_to_task_item(issue, "mission-auth")

        assert task["type"] == "issue"
        assert task["title"] == "[PROJ-123] Fix bug in login"
        assert task["parent_mission"] == "mission-auth"
        assert "description" in task
        assert "due_date" in task
        assert "jira" in task["tags"]
        assert "PROJ" in task["tags"]

    def test_transform_linear_issue_to_task(self):
        """Test transforming Linear issue to task."""
        issue = Issue(
            id="linear-uuid-456",
            key="TEAM-456",
            title="Design dashboard UI",
            description="Create mockups for dashboard",
            status="Todo",
            assignee="bob@company.com",
            created_at=datetime(2024, 1, 10),
            updated_at=datetime(2024, 1, 22),
            due_date=None,
            url="https://linear.app/team/issue/TEAM-456",
            provider="linear",
            custom_fields={"priority": "high"},
        )

        task = IssueTransformer.issue_to_task_item(issue, "mission-ui")

        assert task["type"] == "issue"
        assert task["title"] == "[TEAM-456] Design dashboard UI"
        assert task["parent_mission"] == "mission-ui"
        assert "linear" in task["tags"]
        assert "TEAM" in task["tags"]


# ===================== TestVibeSyncServiceProjects =====================


class TestVibeSyncServiceProjects:
    """Tests for sync service project management integration."""

    @pytest.fixture
    def sync_service(self):
        """Create sync service instance."""
        service = VibeSyncService()
        return service

    @pytest.mark.asyncio
    async def test_sync_jira_success(self, sync_service):
        """Test successful Jira sync."""
        with patch("core.services.vibe_sync_service.get_oauth_manager") as mock_oauth:
            mock_oauth_instance = AsyncMock()
            mock_oauth_instance.get_credentials = AsyncMock(
                return_value={
                    "instance_url": "https://company.atlassian.net",
                    "email": "user@company.com",
                    "api_token": "fake_token",
                }
            )
            mock_oauth.return_value = mock_oauth_instance
            sync_service.oauth_manager = mock_oauth_instance

            result = await sync_service.sync_jira(
                workspace_id="workspace-1",
                mission_id="mission-1",
            )

            assert result["status"] == "success"
            assert result["provider"] == "jira"
            assert "timestamp" in result

    @pytest.mark.asyncio
    async def test_sync_linear_success(self, sync_service):
        """Test successful Linear sync."""
        with patch("core.services.vibe_sync_service.get_oauth_manager") as mock_oauth:
            mock_oauth_instance = AsyncMock()
            mock_oauth_instance.get_credentials = AsyncMock(
                return_value={"api_key": "lin_fake_key"}
            )
            mock_oauth.return_value = mock_oauth_instance
            sync_service.oauth_manager = mock_oauth_instance

            result = await sync_service.sync_linear(
                team_id="team-123",
                mission_id="mission-1",
            )

            assert result["status"] == "success"
            assert result["provider"] == "linear"

    @pytest.mark.asyncio
    async def test_sync_jira_no_credentials(self, sync_service):
        """Test Jira sync with no credentials."""
        with patch.object(sync_service.oauth_manager, "get_credentials", new_callable=AsyncMock) as mock_creds:
            mock_creds.return_value = None

            result = await sync_service.sync_jira(
                workspace_id="workspace-1",
                mission_id="mission-1",
            )

            assert result["status"] == "error"

    @pytest.mark.asyncio
    async def test_handle_webhook_jira(self, sync_service):
        """Test handling Jira webhook."""
        payload = {
            "webhookEvent": "jira:issue_updated",
            "issue": {
                "key": "PROJ-999",
                "fields": {"summary": "Issue updated"},
            },
        }

        result = await sync_service.handle_webhook("jira", payload)
        assert result["status"] == "received"

    @pytest.mark.asyncio
    async def test_handle_webhook_linear(self, sync_service):
        """Test handling Linear webhook."""
        payload = {
            "action": "update",
            "data": {"id": "issue-uuid-999"},
        }

        result = await sync_service.handle_webhook("linear", payload)
        assert result["status"] == "received"

    @pytest.mark.asyncio
    async def test_create_task_from_issue(self, sync_service):
        """Test creating task from issue."""
        issue_dict = {
            "id": "jira-123",
            "key": "PROJ-123",
            "title": "Fix critical bug",
            "description": "High priority bug",
            "status": "In Progress",
            "assignee": "alice@company.com",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "provider": "jira",
            "url": "https://company.atlassian.net/browse/PROJ-123",
        }

        task_id = await sync_service.create_task_from_issue(
            mission_id="mission-1",
            issue=issue_dict,
        )

        assert task_id is not None
        assert isinstance(task_id, str)


# ===================== Integration Tests =====================


class TestPhase8ProjectManagementIntegration:
    """Integration tests for Phase 8.4 project management."""

    @pytest.mark.asyncio
    async def test_full_jira_sync_flow(self):
        """Test complete Jira sync flow."""
        # Create service
        service = VibeSyncService()

        # Auth and sync (with mocked OAuth)
        with patch.object(service.oauth_manager, "get_credentials", new_callable=AsyncMock) as mock_creds:
            mock_creds.return_value = {
                "instance_url": "https://test.atlassian.net",
                "email": "test@test.com",
                "api_token": "fake",
            }

            result = await service.sync_jira(
                workspace_id="work-1",
                mission_id="mis-1",
                jql="project = TEST",
            )

            assert result["provider"] == "jira"
            assert "timestamp" in result

    @pytest.mark.asyncio
    async def test_full_linear_sync_flow(self):
        """Test complete Linear sync flow."""
        service = VibeSyncService()

        with patch.object(service.oauth_manager, "get_credentials", new_callable=AsyncMock) as mock_creds:
            mock_creds.return_value = {"api_key": "lin_test_key"}

            result = await service.sync_linear(
                team_id="team-test",
                mission_id="mis-1",
                status_filter="active",
            )

            assert result["provider"] == "linear"
            assert "timestamp" in result

    @pytest.mark.asyncio
    async def test_webhook_integration_flow(self):
        """Test webhook integration."""
        service = VibeSyncService()

        # Handle Jira webhook
        jira_payload = {
            "webhookEvent": "jira:issue_created",
            "issue": {"key": "PROJ-1", "fields": {"summary": "New"}},
        }
        jira_result = await service.handle_webhook("jira", jira_payload)
        assert jira_result["status"] == "received"

        # Handle Linear webhook
        linear_payload = {
            "action": "create",
            "data": {"id": "uuid-1"},
        }
        linear_result = await service.handle_webhook("linear", linear_payload)
        assert linear_result["status"] == "received"
