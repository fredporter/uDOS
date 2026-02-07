# Slack Web API Integration Guide

**Version:** v1.0.5.0  
**Component:** Wizard Server (Port 8765)  
**Status:** Complete

---

## Overview

This guide covers setting up and using Slack Web API integration with the uDOS Wizard Server. Notifications can be sent to Slack channels, threads can be managed, and files can be uploaded.

---

## Setup

### 1. Create a Slack App

1. Go to [Slack API](https://api.slack.com/apps)
2. Click **Create New App** → **From scratch**
3. **App Name:** `uDOS`
4. **Workspace:** Select your Slack workspace
5. Click **Create App**

### 2. Configure Bot Token Scopes

In your new app's dashboard:

1. Go to **OAuth & Permissions** (left sidebar)
2. Under **Scopes**, click **Add an OAuth Scope**
3. Add these scopes:
   - `chat:write` - Send messages
   - `channels:read` - List channels
   - `channels:manage` - Manage channel topics
   - `users:read` - Read user profiles
   - `files:write` - Upload files
   - `conversations:read` - Read conversations

### 3. Install App to Workspace

1. Go back to **OAuth & Permissions**
2. Click **Install to Workspace**
3. Review permissions and authorize
4. Copy the **Bot User OAuth Token** (starts with `xoxb-`)

### 4. Set Environment Variable

```bash
export SLACK_BOT_TOKEN="xoxb-your-token-here"
```

Or add to `.env` in the uDOS root:

```env
SLACK_BOT_TOKEN=xoxb-your-token-here
SLACK_DEFAULT_CHANNEL=#notifications
```

For local setup, copy the template to the Wizard config area (gitignored) and fill in your values:

```bash
cp wizard/config/slack_keys.template.json wizard/config/slack_keys.json
# edit slack_keys.json with your bot token and defaults (kept out of git)
```

### 5. Add Bot to Channels

In Slack, invite the bot to any channels where it should post:

```
/invite @uDOS
```

---

## API Endpoints

All endpoints require the server to be running on port 8765.

### Send Message

**POST** `/api/slack/send`

Send a notification to a Slack channel.

**Request:**

```bash
curl -X POST http://localhost:8765/api/slack/send \
  -H "Content-Type: application/json" \
  -d '{
    "text": "uDOS is ready to go!",
    "channel": "#notifications",
    "title": "System Status"
  }'
```

**Response:**

```json
{
  "ok": true,
  "data": {
    "ok": true,
    "channel": "C12345678",
    "ts": "1234567890.123456",
    "message": {
      "type": "message",
      "subtype": null,
      "text": "System Status: uDOS is ready to go!"
    }
  }
}
```

### List Channels

**GET** `/api/slack/channels`

List all public and private channels the bot is member of.

**Request:**

```bash
curl http://localhost:8765/api/slack/channels
```

**Response:**

```json
{
  "ok": true,
  "data": {
    "ok": true,
    "channels": [
      {
        "id": "C12345678",
        "name": "notifications",
        "is_member": true,
        "is_private": false,
        "created": 1234567890,
        "members": ["U87654321", "U11111111"]
      }
    ],
    "response_metadata": {
      "messages": [],
      "warnings": [],
      "ok": true
    }
  }
}
```

### Get Channel Info

**GET** `/api/slack/channels/{channel_id}`

Get detailed information about a specific channel.

**Request:**

```bash
curl http://localhost:8765/api/slack/channels/C12345678
```

**Response:**

```json
{
  "ok": true,
  "data": {
    "ok": true,
    "channel": {
      "id": "C12345678",
      "name": "notifications",
      "is_member": true,
      "created": 1234567890,
      "topic": {
        "value": "uDOS notifications and alerts",
        "creator": "U87654321",
        "last_set": 1234567890
      },
      "members": ["U87654321", "U11111111"]
    }
  }
}
```

### Reply in Thread

**POST** `/api/slack/thread`

Reply to a message in a Slack thread.

**Request:**

```bash
curl -X POST http://localhost:8765/api/slack/thread \
  -H "Content-Type: application/json" \
  -d '{
    "thread_ts": "1234567890.123456",
    "channel": "C12345678",
    "text": "Thanks for the update!"
  }'
```

**Response:**

```json
{
  "ok": true,
  "data": {
    "ok": true,
    "ts": "1234567890.789012",
    "channel": "C12345678",
    "message": {
      "type": "message",
      "text": "Thanks for the update!",
      "thread_ts": "1234567890.123456"
    }
  }
}
```

### Upload File

**POST** `/api/slack/upload`

Upload a file to Slack.

**Request:**

```bash
curl -X POST http://localhost:8765/api/slack/upload \
  -F "file=@/path/to/file.txt" \
  -F "channel=C12345678" \
  -F "title=My File"
```

**Response:**

```json
{
  "ok": true,
  "data": {
    "ok": true,
    "file": {
      "id": "F12345678",
      "created": 1234567890,
      "timestamp": 1234567890,
      "name": "file.txt",
      "title": "My File",
      "pretty_type": "Text",
      "user": "U87654321",
      "channels": ["C12345678"]
    }
  }
}
```

### Get User Info

**GET** `/api/slack/user/{user_id}`

Get user profile information.

**Request:**

```bash
curl http://localhost:8765/api/slack/user/U87654321
```

**Response:**

```json
{
  "ok": true,
  "data": {
    "ok": true,
    "user": {
      "id": "U87654321",
      "team_id": "T12345678",
      "name": "john.doe",
      "deleted": false,
      "profile": {
        "title": "Engineer",
        "phone": "+1 234 567 8900",
        "skype": "john.doe",
        "real_name": "John Doe",
        "display_name": "John",
        "username": "johnporter",
        "image_24": "https://...",
        "image_32": "https://...",
        "image_48": "https://...",
        "image_72": "https://...",
        "image_192": "https://...",
        "image_512": "https://..."
      }
    }
  }
}
```

### Check Health

**GET** `/api/slack/health`

Check Slack API connectivity and authentication.

**Request:**

```bash
curl http://localhost:8765/api/slack/health
```

**Response (Healthy):**

```json
{
  "ok": true,
  "data": {
    "status": "healthy",
    "user_id": "U12345678",
    "team_id": "T12345678"
  }
}
```

**Response (Not Configured):**

```json
{
  "ok": false,
  "error": "not_configured",
  "data": {
    "status": "disabled"
  }
}
```

### Get Config Status

**GET** `/api/slack/config`

Get Slack configuration status (without exposing secrets).

**Request:**

```bash
curl http://localhost:8765/api/slack/config
```

**Response:**

```json
{
  "ok": true,
  "data": {
    "is_configured": true,
    "default_channel": "#notifications",
    "rate_limit_per_minute": 20
  }
}
```

---

## Integration with Mac App

The Mac App can send notifications to Slack by calling the Wizard API:

```typescript
import { addToast } from "./stores/notifications";

async function notifySlack(message: string) {
  try {
    const response = await fetch("http://localhost:8765/api/slack/send", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        text: message,
        channel: "#notifications",
        title: "uMarkdown",
      }),
    });

    const result = await response.json();

    if (result.ok) {
      addToast({
        type: "success",
        title: "Slack notified",
        message: "Message sent to #notifications",
      });
    } else {
      addToast({
        type: "error",
        title: "Slack notification failed",
        message: result.data?.error || "Unknown error",
      });
    }
  } catch (error) {
    addToast({
      type: "error",
      title: "Connection error",
      message: error instanceof Error ? error.message : "Unknown error",
    });
  }
}
```

---

## Troubleshooting

### "not_configured" Error

**Cause:** `SLACK_BOT_TOKEN` is not set or invalid.

**Fix:**

```bash
# Check environment variable
echo $SLACK_BOT_TOKEN

# Should output: xoxb-...
# If empty, set it:
export SLACK_BOT_TOKEN="xoxb-your-actual-token"
```

### "token_expired" Error

**Cause:** Bot token has been revoked or expired.

**Fix:**

1. Go to Slack App dashboard → OAuth & Permissions
2. Regenerate a new token
3. Update `SLACK_BOT_TOKEN`

### "channel_not_found" Error

**Cause:** Channel name is incorrect or bot is not member.

**Fix:**

1. List channels: `GET /api/slack/channels`
2. Copy the exact channel ID from response
3. Use `#channel-name` or channel ID in requests
4. Invite bot to channel: `/invite @uDOS`

### Rate Limiting

**Limit:** 20 messages per minute by default.

If exceeded, responses return:

```json
{
  "ok": false,
  "error": "rate_limited"
}
```

To adjust, modify `SLACK_RATE_LIMIT_PER_MINUTE` environment variable:

```bash
export SLACK_RATE_LIMIT_PER_MINUTE=30
```

### Timeout Issues

**Limit:** 10 second timeout by default.

If requests timeout, check:

1. Network connectivity
2. Slack API status: https://status.slack.com
3. Firewall rules blocking outbound HTTPS

---

## Security Best Practices

1. **Never commit tokens** - Use environment variables only
2. **Rotate tokens regularly** - Slack recommends monthly rotation
3. **Limit scopes** - Only request scopes your app needs
4. **Use HTTPS** - All Slack API calls are over HTTPS
5. **Validate messages** - Sanitize user input before sending
6. **Rate limiting** - Respect Slack API rate limits
7. **Error handling** - Don't expose tokens in error messages

---

## References

- [Slack API Documentation](https://api.slack.com/methods)
- [OAuth Scopes](https://api.slack.com/scopes)
- [Bot Tokens](https://api.slack.com/authentication/token-types#bot)
- [Rate Limits](https://api.slack.com/docs/rate-limits)

---

**Last Updated:** 2026-01-17  
**Component Version:** v1.0.5.0
