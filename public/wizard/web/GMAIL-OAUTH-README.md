# Gmail OAuth - Wizard Server Web Interface

**Quick Start:** Browser-based Gmail authentication for uDOS

## 🚀 Launch

```bash
# From uDOS root
./wizard/web/start_wizard_web.sh
```

**Or manually:**
```bash
cd /path/to/uDOS
source .venv/bin/activate
python -c "from wizard.web.app import start_web_server; start_web_server()"
```

---

## 🔗 Access

Once running, open in your browser:

- **Gmail OAuth:** [http://127.0.0.1:8080/gmail/](http://127.0.0.1:8080/gmail/)
- **Dashboard:** [http://127.0.0.1:8080/](http://127.0.0.1:8080/)

---

## 📋 Prerequisites

### 1. Google Cloud Credentials

**Follow:** [wiki/Google-Cloud-Console-Setup.md](../../wiki/Google-Cloud-Console-Setup.md)

**Quick version:**
1. Create project at [console.cloud.google.com](https://console.cloud.google.com)
2. Enable Gmail, Drive, People APIs
3. Configure OAuth consent screen
4. Create Desktop app credentials
5. Download JSON → `memory/system/user/gmail_credentials.json`

### 2. Python Dependencies

```bash
pip install fastapi uvicorn python-multipart jinja2 \
    google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

(Automatically installed by startup script)

---

## 🎯 Using the OAuth Button

### First Time Login

1. **Open:** [http://127.0.0.1:8080/gmail/](http://127.0.0.1:8080/gmail/)
2. **Click:** "Sign in with Google" button
3. **Browser redirects** to Google consent screen
4. **Select** your Google account
5. **Review** permissions:
   - Read Gmail
   - Send Gmail
   - App Data Folder (Drive)
   - User Info
6. **Click** "Continue"
7. **Redirect back** to Wizard Server
8. **Success!** Shows your email/name

### After Authentication

**Status shows:**
- ✅ Authenticated
- Email address
- Name
- Token expiry time

**Available:**
- Logout button
- Auto-refresh tokens (transparent)
- Encrypted storage

---

## 🔐 Security

### Token Storage

- **Location:** `memory/system/user/.gmail_token.enc`
- **Encryption:** AES-256 (Fernet)
- **Key:** `.env` file (gitignored)

### Permissions

| Scope | What It Does |
|-------|-------------|
| `gmail.readonly` | Read your emails |
| `gmail.send` | Send emails as you |
| `drive.appdata` | Hidden app folder (NOT your files) |
| `userinfo.email` | Your email & name |

### Revoke Access

**Anytime:**
1. Visit [myaccount.google.com/permissions](https://myaccount.google.com/permissions)
2. Find "uDOS"
3. Click "Remove Access"

**Or click "Logout" button** in web interface

---

## 🧪 Testing

```bash
# 1. Start web server
./wizard/web/start_wizard_web.sh

# 2. Open browser
open http://127.0.0.1:8080/gmail/

# 3. Click "Sign in with Google"

# 4. After authentication, test status API
curl http://127.0.0.1:8080/gmail/status
```

**Expected response:**
```json
{
  "authenticated": true,
  "email": "your@email.com",
  "name": "Your Name",
  "token_expiry": "2026-01-05T15:30:00",
  "scopes": [...]
}
```

---

## ❌ Troubleshooting

### "Credentials file not found"

**Fix:**
```bash
# Check file exists
ls -lh memory/system/user/gmail_credentials.json

# If missing, download from Google Cloud Console
# Follow: wiki/Google-Cloud-Console-Setup.md
```

### "Access blocked: This app is not verified"

**Expected** - Your app isn't verified yet

**Fix:**
1. Click "Advanced" (bottom left)
2. Click "Go to uDOS (unsafe)" - Safe, it's YOUR app
3. Continue

### Port 8080 already in use

```bash
# Find process
lsof -ti:8080

# Kill it
kill -9 $(lsof -ti:8080)

# Restart wizard server
./wizard/web/start_wizard_web.sh
```

### Session state errors

**Cause:** FastAPI needs session middleware

**Fix:** (already handled in code)
```python
from starlette.middleware.sessions import SessionMiddleware
app.add_middleware(SessionMiddleware, secret_key="your-secret-key")
```

---

## 🔗 Integration with TUI

Once authenticated via browser, **TUI commands work immediately:**

```bash
# Start uDOS TUI
./start_udos.sh

# Commands now work
uDOS> STATUS GMAIL
✅ Authenticated
Email: your@email.com

uDOS> EMAIL LIST
Fetching recent emails...

uDOS> EMAIL SEND test@example.com "Hello" "Test from uDOS"
✅ Email sent
```

---

## 📚 Files Created

| File | Purpose |
|------|---------|
| `wizard/web/gmail_fastapi_routes.py` | FastAPI OAuth routes |
| `wizard/web/gmail_routes.py` | Flask version (legacy) |
| `wizard/web/templates/gmail_oauth.html` | OAuth UI page |
| `wizard/web/start_wizard_web.sh` | Startup script |

---

## 🎨 UI Features

- **Dark theme** (matches uDOS aesthetic)
- **Google branding** compliance
- **Responsive** design
- **Flash messages** for feedback
- **Permission explanations** clear
- **One-click login/logout**

---

## 🚀 Next Steps

1. **Test OAuth flow** - Authenticate with your account
2. **Try TUI commands** - EMAIL LIST, STATUS GMAIL
3. **Build dashboard** - Add email/Drive stats
4. **Add features:**
   - Email preview
   - Drive quota widget
   - Send email form
   - Token refresh UI

---

*Version: v1.0.1.0*  
*Last Updated: 2026-01-05*
