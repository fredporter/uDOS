# Phase 8: External System Synchronization

**Status**: Architecture Design & Setup
**Target**: Full external system integration (Calendar, Email, Projects, Chat)
**Foundation**: Phase 7 (Binder + uCLI skills), Phase 6 (Unified task format)
**Test Baseline**: 134/134 tests passing

---

## 🎯 Phase 8 Objectives

Integrate external systems with the uDOS Binder ecosystem to create unified task management across all user workflows:

1. **Calendar Synchronization** (Google, Outlook, Apple)
   - Two-way sync for calendar events
   - Parse event titles/descriptions for task extraction
   - Update calendar when Binder tasks change state

2. **Email Ingestion** (Gmail, Outlook, IMAP)
   - Extract actionable items from emails
   - Create tasks from selected messages
   - Link tasks back to original email threads

3. **Project Management** (Jira, Linear)
   - Webhook-driven sync for issue status updates
   - Map Jira/Linear issues to Binder tasks
   - Bi-directional synchronization

4. **Chat Integration** (Slack)
   - Fetch messages from channels/threads
   - Create tasks from Slack discussions
   - Post task updates to Slack channels

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        uDOS Binder Core                         │
│                   (Phase 6 Task Management)                     │
│                          vault/@binders/                        │
└────────────────┬────────────────────────────────────┬───────────┘
                 │                                    │
        ┌────────▼────────┐            ┌──────────────▼──────────┐
        │ Sync Service    │            │   CLI/TUI/MCP Layer     │
        │ (Phase 8)       │            │   (Phase 7)             │
        └────────┬────────┘            └──────────────┬──────────┘
                 │                                    │
    ┌────────────┼────────────────────────────────────┼────────────┐
    │            │                                    │            │
┌───▼───────┐ ┌─▼───────┐ ┌────────┐ ┌────────┐ ┌───▼────┐ ┌────▼──┐
│ Calendar  │ │ Email   │ │ Jira   │ │Linear  │ │ Slack  │ │ OAuth │
│ Providers │ │Provider │ │Webhooks│ │API     │ │ Client │ │Mgmt   │
└───────────┘ └─────────┘ └────────┘ └────────┘ └────────┘ └───────┘
     │            │           │         │          │
     ▼            ▼           ▼         ▼          ▼
  ┌──────────────────────────────────────────────────────┐
  │              Data Transform Pipeline                 │
  │  (unified format → moves.json item types)            │
  └──────────────────────────────────────────────────────┘
     ▼            ▼           ▼         ▼          ▼
  ┌──────────────────────────────────────────────────────┐
  │          Event Queue & Scheduling                    │
  │  (debounce, batch, retry, backoff)                   │
  └──────────────────────────────────────────────────────┘
```

---

## 📋 Service Architecture

### 1. **Sync Service** (`core/services/vibe_sync_service.py` — NEW)

Main orchestrator for all external system synchronization.

```python
class VibeSyncService:
    """Unified external system synchronization."""

    def __init__(self):
        self.calendar_provider = None      # Calendar factory
        self.email_provider = None         # Email factory
        self.project_manager = None        # Jira/Linear factory
        self.slack_client = None           # Slack API client
        self.event_queue = EventQueue()    # Debounced events
        self.sync_history = {}             # Track last sync times

    # Calendar operations
    async def sync_calendar(self, provider: str, credentials: dict) -> dict
    async def fetch_calendar_events(self, provider: str, date_range: dict) -> List[dict]
    async def create_task_from_event(self, mission_id: str, event: dict) -> str
    async def update_calendar_from_task(self, task_id: str, event_id: str) -> bool

    # Email operations
    async def sync_emails(self, provider: str, credentials: dict) -> dict
    async def fetch_emails(self, provider: str, filters: dict) -> List[dict]
    async def create_task_from_email(self, mission_id: str, email: dict) -> str

    # Project management
    async def sync_jira(self, workspace_id: str, jql: str) -> dict
    async def sync_linear(self, team_id: str, status_filter: str) -> dict
    async def handle_webhook(self, provider: str, payload: dict) -> dict

    # Slack integration
    async def sync_slack(self, workspace: str, channels: List[str]) -> dict
    async def post_task_update(self, task_id: str, channel: str, update: dict) -> bool

    # Utility
    async def get_sync_status(self) -> dict
    async def trigger_full_sync(self, systems: List[str]) -> dict
```

---

## 🔧 Provider Implementations

### 2.1 Calendar Providers (`core/sync/calendar_provider.py` — NEW)

```python
class CalendarProvider(ABC):
    """Base for calendar implementations."""

    @abstractmethod
    async def authenticate(self, credentials: dict) -> bool
    @abstractmethod
    async def fetch_events(self, start_date, end_date) -> List[CalendarEvent]
    @abstractmethod
    async def create_event(self, event: CalendarEvent) -> str
    @abstractmethod
    async def update_event(self, event_id: str, changes: dict) -> bool
    @abstractmethod
    async def delete_event(self, event_id: str) -> bool

class GoogleCalendarProvider(CalendarProvider):
    """Google Calendar API integration."""
    # Implements oauth2, event CRUD, timezone handling

class OutlookCalendarProvider(CalendarProvider):
    """Microsoft Outlook/Office 365 Calendar integration."""
    # Implements oauth2, event CRUD, timezone handling

class AppleCalendarProvider(CalendarProvider):
    """Apple Calendar (iCal) integration."""
    # Implements local file sync, iCal parsing, event CRUD
```

### 2.2 Email Providers (`core/sync/email_provider.py` — NEW)

```python
class EmailProvider(ABC):
    """Base for email implementations."""

    @abstractmethod
    async def authenticate(self, credentials: dict) -> bool
    @abstractmethod
    async def fetch_messages(self, query: str, limit: int) -> List[EmailMessage]
    @abstractmethod
    async def get_message(self, message_id: str) -> EmailMessage
    @abstractmethod
    async def mark_as_processed(self, message_id: str) -> bool

class GmailProvider(EmailProvider):
    """Gmail API integration."""
    # Implements oauth2, label parsing, attachment handling

class OutlookEmailProvider(EmailProvider):
    """Outlook/Office 365 Email integration."""
    # Implements oauth2, folder parsing, attachment handling

class IMAPProvider(EmailProvider):
    """Generic IMAP email integration."""
    # Implements IMAP protocol, folder parsing, TLS/SSL
```

### 2.3 Project Management (`core/sync/project_manager.py` — NEW)

```python
class ProjectManager(ABC):
    """Base for project management systems."""

    @abstractmethod
    async def authenticate(self, credentials: dict) -> bool
    @abstractmethod
    async def fetch_issues(self, jql: str) -> List[Issue]
    @abstractmethod
    async def handle_webhook(self, payload: dict) -> IssueUpdate
    @abstractmethod
    async def update_issue(self, issue_id: str, changes: dict) -> bool

class JiraManager(ProjectManager):
    """Jira Cloud API and webhooks."""
    # JQL queries, custom fields, status transitions, webhooks

class LinearManager(ProjectManager):
    """Linear API integration."""
    # GraphQL queries, issue state, webhooks, team sync
```

### 2.4 Slack Integration (`core/sync/slack_client.py` — NEW)

```python
class SlackClient:
    """Slack API integration."""

    async def authenticate(self, credentials: dict) -> bool
    async def fetch_channel_messages(self, channel_id: str, ts_from: float) -> List[Message]
    async def get_thread_messages(self, channel_id: str, thread_ts: str) -> List[Message]
    async def post_message(self, channel: str, blocks: List[dict]) -> str
    async def post_task_update(self, channel: str, task: TaskItem) -> str
    async def handle_event(self, event: dict) -> EventResponse
```

---

## 🔄 Data Transformation Pipeline

Convert external system data formats into uDOS Binder items (Phase 6 unified format).

```python
# core/sync/transformers.py

class EventTransformer:
    """Transform external events into Binder items."""

    @staticmethod
    def calendar_event_to_task(event: CalendarEvent, mission_id: str) -> TaskItem:
        """Convert calendar event → task item."""
        return TaskItem(
            id=event.id,
            type="task",
            title=event.title,
            description=f"Calendar event: {event.description}",
            status="todo",
            due_date=event.end_time.isoformat(),
            assigned_provider="calendar",
            external_id=event.id,
            external_provider=event.provider
        )

    @staticmethod
    def email_to_task(email: EmailMessage, mission_id: str) -> TaskItem:
        """Convert email → task item."""
        return TaskItem(
            id=f"email-{email.message_id}",
            type="task",
            title=email.subject,
            description=f"Email from {email.from_addr}\n\n{email.body[:500]}",
            status="todo",
            assigned_provider="email",
            external_id=email.message_id,
            external_provider="email"
        )

    @staticmethod
    def jira_issue_to_task(issue: Issue, mission_id: str) -> TaskItem:
        """Convert Jira issue → task item."""
        return TaskItem(
            id=f"jira-{issue.key}",
            type="task",
            title=f"[{issue.key}] {issue.summary}",
            description=issue.description,
            status=_map_jira_status(issue.status),
            assigned_to=issue.assignee,
            assigned_provider="jira",
            external_id=issue.key,
            external_provider="jira",
            url=issue.permalink
        )

    @staticmethod
    def linear_issue_to_task(issue: LinearIssue, mission_id: str) -> TaskItem:
        """Convert Linear issue → task item."""
        return TaskItem(
            id=f"linear-{issue.id}",
            type="task",
            title=f"[{issue.identifier}] {issue.title}",
            description=issue.description,
            status=_map_linear_status(issue.state),
            assigned_to=issue.assignee_id,
            assigned_provider="linear",
            external_id=issue.id,
            external_provider="linear",
            url=issue.url
        )
```

---

## 🔐 Security & Credential Management

### OAuth2 Integration

Use existing `security/oauth_handler.py` pattern from Wizard to manage provider credentials:

```python
# core/sync/oauth_manager.py

class OAuthManager:
    """Handle OAuth2 flows for all providers."""

    PROVIDER_CONFIGS = {
        "google_calendar": {...oauth2 config...},
        "outlook": {...oauth2 config...},
        "github": {...oauth2 config...},
        "jira": {...oauth2 config...},
        "linear": {...oauth2 config...},
        "slack": {...oauth2 config...},
    }

    async def get_authorization_url(self, provider: str) -> str
    async def handle_callback(self, provider: str, code: str) -> dict
    async def refresh_token(self, provider: str) -> str
    async def get_credentials(self, provider: str) -> dict
    async def revoke_credentials(self, provider: str) -> bool
```

**Storage**: Use Wizard's existing encrypted credential vault:
- `wizard/config/assistant_keys.json` (encrypted with secrets.tomb)
- Fallback to environment variables: `GOOGLE_CALENDAR_TOKEN`, `JIRA_API_TOKEN`, etc.

---

## ⏱️ Event Queue & Scheduling

Prevent sync storms and enable batching:

```python
# core/sync/event_queue.py

class EventQueue:
    """Debounce and batch external system events."""

    def __init__(self):
        self.pending_events = defaultdict(list)
        self.last_sync = {}
        self.debounce_interval = 30  # seconds
        self.batch_size = 50

    async def enqueue(self, event: SyncEvent):
        """Add event to queue."""
        self.pending_events[event.provider].append(event)

    async def process_batch(self, provider: str = None):
        """Process queued events with debouncing and retry."""
        # Wait for debounce interval
        # Check last sync time
        # Batch events into single mutation
        # Retry on failure with exponential backoff
```

**Debouncing Strategy**:
- Calendar events: 30-second debounce, process hourly
- Email ingestion: 5-minute debounce, process every 15 minutes
- Webhooks: immediate processing with deduplication
- Slack: 1-minute debounce, process as needed

---

## 🧪 Testing Strategy

### Unit Tests
- `tests/test_sync_service.py` — Sync service orchestration
- `tests/test_calendar_providers.py` — Each calendar provider
- `tests/test_email_providers.py` — Each email provider
- `tests/test_project_managers.py` — Jira/Linear managers
- `tests/test_slack_client.py` — Slack integration
- `tests/test_event_transformers.py` — Data transformation accuracy
- `tests/test_oauth_manager.py` — OAuth2 flows

### Integration Tests
- `tests/integration/test_calendar_sync_e2e.py` — Full calendar sync workflow
- `tests/integration/test_email_sync_e2e.py` — Full email ingestion workflow
- `tests/integration/test_jira_webhook_flow.py` — Webhook handling
- `tests/integration/test_sync_conflict_resolution.py` — Conflict handling

### Mock Fixtures
```python
# tests/fixtures/mock_providers.py
@pytest.fixture
def mock_google_calendar():
    """Mocked Google Calendar API responses."""

@pytest.fixture
def mock_jira_webhook():
    """Mocked Jira webhook payloads."""

@pytest.fixture
def mock_slack_events():
    """Mocked Slack event payloads."""
```

**Target**: Maintain 134/134 test baseline + 50+ new Phase 8 tests

---

## 📊 Implementation Phases

### Phase 8.1: Architecture & Foundation (Current)
- [x] Design sync service architecture
- [ ] Create OAuth manager
- [ ] Implement event queue with debouncing
- [ ] Set up basic provider interfaces
- **Estimated**: 2-3 hours

### Phase 8.2: Calendar Integration
- [ ] Google Calendar provider (oauth2, fetch, create, update)
- [ ] Outlook Calendar provider
- [ ] Apple Calendar provider
- [ ] Calendar event → task transformation
- [ ] Calendar sync with conflict resolution
- **Tests**: 15-20 tests, maintain 134+ baseline
- **Estimated**: 4-5 hours

### Phase 8.3: Email Integration
- [ ] Gmail provider (oauth2, label parsing, attachments)
- [ ] Outlook Email provider
- [ ] IMAP generic provider
- [ ] Email → task transformation
- [ ] Email ingestion pipeline with filtering
- **Tests**: 15-20 tests, maintain 134+ baseline
- **Estimated**: 4-5 hours

### Phase 8.4: Project Management
- [ ] Jira Cloud integration (API, custom fields, JQL)
- [ ] Linear integration (GraphQL API)
- [ ] Webhook handling for both platforms
- [ ] Issue → task transformation with bidirectional sync
- [ ] Conflict resolution for issue status
- **Tests**: 15-20 tests, maintain 134+ baseline
- **Estimated**: 5-6 hours

### Phase 8.5: Slack Integration
- [ ] Slack app registration and oauth2
- [ ] Message fetching and thread parsing
- [ ] Task update posting to Slack
- [ ] Event handling (app_mention, message, etc.)
- [ ] Slack blocks formatting for task updates
- **Tests**: 10-15 tests, maintain 134+ baseline
- **Estimated**: 3-4 hours

### Phase 8.6: CLI/MCP Exposure
- [ ] Add sync commands to vibe_skill_mapper.py (SYNC_SKILL with 6-8 actions)
- [ ] Add sync handlers to vibe_cli_handler.py (_handle_sync method)
- [ ] Add sync tools to Wizard MCP (8-10 vibe_sync_* tools)
- [ ] Update uCLI service for sync status view
- **Tests**: All Phase 8 tests passing, 134+ baseline
- **Estimated**: 2-3 hours

### Phase 8.7: Documentation & Production Ready
- [ ] Create PHASE8-EXTERNAL-SYNC-COMPLETE.md guide
- [ ] Update QUICKSTART.md with sync setup steps
- [ ] Create provider setup guides (Google, Outlook, Jira, Linear, Slack)
- [ ] Full test validation (170+ tests expected)
- [ ] Commit and push Phase 8
- **Estimated**: 2-3 hours

---

## 🎯 Success Criteria

- [x] Phase 8 architecture document (this file)
- [ ] All 5 provider systems integrated
- [ ] 170+ tests passing (134 + 35+ new)
- [ ] Sync status dashboard (uCLI view)
- [ ] All 6 external systems accessible via:
  - shell: `ucli SYNC STATUS`, `ucli SYNC CALENDAR`, etc.
  - MCP: `vibe_sync_*` tools available to Claude
  - Python: `from core.services.vibe_sync_service import get_sync_service()`
- [ ] Comprehensive documentation with provider setup guides
- [ ] Production deployment ready with secrets management

---

## 🚀 Next Steps

1. **Immediate**: Create `VibeSyncService` skeleton with OAuth manager
2. **Then**: Implement Google Calendar provider as proof-of-concept
3. **Then**: Build email ingestion pipeline (Gmail)
4. **Then**: Add Jira webhook handler
5. **Then**: Implement Linear API integration
6. **Finally**: Slack integration and CLI/MCP exposure

---

**Target Completion**: 4-6 hours of focused development
**Estimated Tests**: 170+ passing (134 baseline + 35+ new)
**Estimated CLI Commands**: 18 (existing) + 6-8 (SYNC) = 24-26 total
**Estimated MCP Tools**: 15 (existing) + 8-10 (sync) = 23-25 total
