# Quick Test: Setup Profile Sync

## ✅ What Was Implemented

Your TUI setup story answers are now synchronized with the Wizard Server! You can view them using:

---

## 🚀 Quick Test

### Option 1: Interactive Console (Easiest)

```bash
# Start Wizard Server
./bin/start_wizard.sh

# In the console prompt, type:
wizard> setup
```

You should see your name, role, timezone, location, and all the details you entered!

---

### Option 2: API Endpoint

```bash
# Get all your profile info
curl -H "Authorization: Bearer $(cat memory/private/wizard_admin_token.txt)" \
  http://localhost:8765/api/v1/setup/profile/combined | jq
```

---

## 📋 What You'll See

```
🧙 SETUP PROFILE:

  User Identity:
    • Username: [your entered username]
    • Role: [admin/user]
    • Timezone: [your timezone]
    • Location: [your city] ([location ID])

  Installation:
    • ID: udos-[unique ID]
    • OS Type: [macos/alpine/ubuntu/windows]
    • Lifespan Mode: [infinite/moves/calendar]

  Capabilities:
    ✅ Web Proxy [if enabled]
    ✅ Gmail Relay [if enabled]
    ✅ Ai Gateway [if enabled]
    ❌ GitHub Push [if disabled]
    ...

  Metrics:
    • Moves Used: 0
```

---

## 🎯 What's Synchronized

### From TUI Story → Wizard Server

- ✅ Username
- ✅ Date of birth
- ✅ Role (admin/user)
- ✅ Timezone
- ✅ Location (city + grid ID)
- ✅ Installation ID
- ✅ OS type
- ✅ Lifespan settings
- ✅ Capabilities (which services are enabled)

### Automatic Syncs

- ✅ Wizard config (`wizard/config/wizard.json`)
- ✅ Secret store (encrypted profiles)
- ✅ Installation metrics

---

## 📍 Where Data Lives

1. **User Profile** → Secret store (encrypted)
   - Key: `wizard-user-profile`
   - Requires `WIZARD_KEY` env var

2. **Installation Profile** → Secret store (encrypted)
   - Key: `wizard-install-profile`

3. **Metrics** → Filesystem
   - Path: `memory/wizard/installation-metrics.json`

4. **Capabilities** → Wizard config
   - Path: `wizard/config/wizard.json`

---

## 🔧 New Console Commands

| Command  | Description                 |
| -------- | --------------------------- |
| `setup`  | Show complete setup profile |
| `config` | Show Wizard configuration   |
| `status` | Show server status          |

---

## 📖 Full Documentation

- [SETUP-PROFILE-SYNC.md](SETUP-PROFILE-SYNC.md) — Complete technical docs
- [SETUP-SYNC-IMPLEMENTATION.md](SETUP-SYNC-IMPLEMENTATION.md) — Implementation summary

---

**Ready to test!** 🎉
