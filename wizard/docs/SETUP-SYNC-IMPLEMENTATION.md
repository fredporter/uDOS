# TUI Setup Story ↔ Wizard Profile Synchronization

**Implementation Date:** 2026-01-28  
**Status:** ✅ Complete

---

## 🎯 Problem

The TUI setup story (`wizard-setup-story.md`) was collecting user information (name, role, timezone, location, etc.), but these values weren't visible in the Wizard Server dashboard or console after submission.

---

## ✅ Solution

Implemented a complete synchronization system with three components:

### 1. **API Endpoints** (New)

Added three new endpoints to `/api/v1/setup/profile/*`:

- **GET /api/v1/setup/profile/user** — Retrieve user profile
- **GET /api/v1/setup/profile/install** — Retrieve installation profile + metrics
- **GET /api/v1/setup/profile/combined** — Get everything in one call

### 2. **Interactive Console Command** (New)

Added `setup` command to Wizard Server console:

```bash
wizard> setup
```

Displays complete user and installation profile with formatted output showing:

- User identity (username, role, timezone, location)
- Installation details (ID, OS type, lifespan mode)
- Capabilities (with ✅/❌ indicators)
- Metrics (moves used/remaining)

### 3. **Documentation** (New)

Created comprehensive documentation:

- [wizard/docs/SETUP-PROFILE-SYNC.md](wizard/docs/SETUP-PROFILE-SYNC.md)

---

## 📁 Files Modified

### wizard/routes/setup_routes.py

**Added:**

- `get_user_profile()` endpoint
- `get_install_profile()` endpoint
- `get_combined_profile()` endpoint

**Lines:** +53 lines added

### wizard/services/interactive_console.py

**Added:**

- `cmd_setup()` method
- "setup" command registration in commands dict
- Updated docstring with new command

**Lines:** +71 lines added

### wizard/docs/SETUP-PROFILE-SYNC.md (New)

**Created:**

- Complete documentation on synchronization
- API endpoint reference
- Console command usage
- Data flow diagrams
- Security notes

**Lines:** +234 lines

---

## 🔄 Data Flow

```
┌─────────────────────────────┐
│   TUI Setup Story           │
│   (memory/story/            │
│    wizard-setup-story.md)   │
└─────────────┬───────────────┘
              │
              ↓ User completes story
              │
┌─────────────▼───────────────┐
│  POST /api/v1/setup/        │
│       story/submit          │
└─────────────┬───────────────┘
              │
              ↓ Saves to secret store
              │
┌─────────────▼───────────────┐
│    Secret Store             │
│  (Encrypted Storage)        │
│                             │
│  • wizard-user-profile      │
│  • wizard-install-profile   │
└─────────────┬───────────────┘
              │
              ↓ Auto-syncs capabilities
              │
┌─────────────▼───────────────┐
│  wizard/config/wizard.json  │
│  (Service Toggles)          │
└─────────────┬───────────────┘
              │
              ↓ Retrieve via API/Console
              │
┌─────────────▼───────────────┐
│  GET /api/v1/setup/         │
│       profile/combined      │
│         OR                  │
│  wizard> setup              │
└─────────────────────────────┘
```

---

## 🧪 Testing

### Test Profile Retrieval via API

```bash
# Get combined profile
curl -H "Authorization: Bearer $(cat memory/private/wizard_admin_token.txt)" \
  http://localhost:8765/api/v1/setup/profile/combined | jq

# Get user profile only
curl -H "Authorization: Bearer $(cat memory/private/wizard_admin_token.txt)" \
  http://localhost:8765/api/v1/setup/profile/user | jq

# Get install profile only
curl -H "Authorization: Bearer $(cat memory/private/wizard_admin_token.txt)" \
  http://localhost:8765/api/v1/setup/profile/install | jq
```

### Test Console Command

```bash
# Start Wizard Server with interactive console
./bin/start_wizard.sh

# In the console, type:
wizard> setup
```

**Expected Output:**

```
🧙 SETUP PROFILE:

  User Identity:
    • Username: fred
    • Role: admin
    • Timezone: America/Los_Angeles
    • Location: San Francisco (L001-usa-sanfrancisco)

  Installation:
    • ID: udos-a1b2c3d4e5f6g7h8
    • OS Type: macos
    • Lifespan Mode: infinite

  Capabilities:
    ✅ Web Proxy
    ✅ Gmail Relay
    ✅ Ai Gateway
    ❌ GitHub Push
    ...

  Metrics:
    • Moves Used: 0
```

---

## 🔐 Security

- User and installation profiles stored in **encrypted secret store**
- Requires `WIZARD_KEY` environment variable
- API endpoints require **admin authentication**
- Console command only accessible via **localhost**
- Metrics stored in filesystem (non-sensitive)

---

## 📊 Profile Structure

### User Profile

```json
{
  "username": "fred",
  "date_of_birth": "1980-01-15",
  "role": "admin",
  "timezone": "America/Los_Angeles",
  "location_id": "L001-usa-sanfrancisco",
  "location_name": "San Francisco"
}
```

### Installation Profile

```json
{
  "installation_id": "udos-a1b2c3d4e5f6g7h8",
  "os_type": "macos",
  "lifespan_mode": "infinite",
  "moves_limit": null,
  "capabilities": {
    "web_proxy": true,
    "gmail_relay": true,
    "ai_gateway": true,
    "github_push": false,
    ...
  }
}
```

---

## 🎨 User Experience

**Before:**

- Setup story collected data but it wasn't visible anywhere
- No way to verify what was entered
- Dashboard couldn't display user context

**After:**

- Type `setup` in Wizard console to see all details
- API endpoints available for dashboard integration
- User identity and preferences visible in formatted display
- Capabilities automatically sync to Wizard config

---

## 🚀 Next Steps

### Wizard Dashboard Integration

The new `/api/v1/setup/profile/combined` endpoint can be integrated into the Wizard dashboard UI:

```typescript
// Example dashboard integration
const response = await fetch('/api/v1/setup/profile/combined');
const { user_profile, install_profile, install_metrics } = await response.json();

// Display in dashboard
<ProfileCard>
  <UserInfo name={user_profile.username} role={user_profile.role} />
  <LocationInfo location={user_profile.location_name} />
  <Capabilities list={install_profile.capabilities} />
</ProfileCard>
```

### TUI Integration

The setup command can also be exposed in the Core TUI:

```python
# In core/commands/setup_handler.py
class SetupHandler:
    def handle_show_profile(self):
        # Call Wizard API to get profile
        response = requests.get('http://localhost:8765/api/v1/setup/profile/combined')
        profile = response.json()
        # Display in TUI format
        ...
```

---

## 📚 References

- [wizard/routes/setup_routes.py](../wizard/routes/setup_routes.py)
- [wizard/services/setup_profiles.py](../wizard/services/setup_profiles.py)
- [wizard/services/interactive_console.py](../wizard/services/interactive_console.py)
- [wizard/docs/SETUP-PROFILE-SYNC.md](../wizard/docs/SETUP-PROFILE-SYNC.md)
- [memory/story/wizard-setup-story.md](../memory/story/wizard-setup-story.md)

---

**Status:** ✅ Implementation Complete  
**Testing:** Ready for user validation  
**Documentation:** Complete
