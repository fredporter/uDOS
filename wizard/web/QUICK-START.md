# Gmail OAuth Browser Button - Quick Start

**✅ Browser-based Gmail authentication for uDOS**

---

## 🚀 Start the Server

```bash
cd /path/to/uDOS
source .venv/bin/activate
python wizard/web/gmail_oauth_server.py
```

Server starts on [http://127.0.0.1:8080/gmail/](http://127.0.0.1:8080/gmail/)

---

## 📋 Before You Start

### 1. Google Cloud Setup

Follow: [wiki/Google-Cloud-Console-Setup.md](../../wiki/Google-Cloud-Console-Setup.md)

**Quick steps:**
1. Visit [console.cloud.google.com](https://console.cloud.google.com)
2. Create project "uDOS-Alpha"
3. Enable APIs: Gmail, Drive, People
4. Configure OAuth consent screen
5. Create "Desktop app" credentials
6. Download JSON → `memory/bank/user/gmail_credentials.json`

### 2. Verify Setup

```bash
# Check credentials exist
ls -lh memory/bank/user/gmail_credentials.json

# Should show ~1-2 KB file
```

---

## 🎯 Using the OAuth Button

### Step 1: Open Browser

Visit: [http://127.0.0.1:8080/gmail/](http://127.0.0.1:8080/gmail/)

### Step 2: Click "Sign in with Google"

Big blue button with Google logo

### Step 3: Google Consent Screen

1. **Select your Google account**
2. **Review permissions:**
   - 📧 Read Gmail
   - ✉️ Send Gmail
   - 💾 App Data Folder (hidden folder, NOT your files)
   - 👤 User Info (email/name)
3. **Click "Continue"**

### Step 4: Success!

Redirects back to [http://127.0.0.1:8080/gmail/](http://127.0.0.1:8080/gmail/)

Shows:
- ✅ Authenticated
- Your email address
- Your name
- Token expiry time

---

## 🔐 Security Notes

- **Tokens encrypted** with AES-256
- **Stored locally** at `memory/bank/user/.gmail_token.enc`
- **Auto-refresh** when expired
- **Revoke anytime** via [myaccount.google.com/permissions](https://myaccount.google.com/permissions)

---

## ✅ Test with TUI

After authentication, **TUI commands work immediately:**

```bash
# Start uDOS TUI
./start_udos.sh

# Check status
uDOS> STATUS GMAIL
✅ Authenticated
Email: your@email.com

# List emails
uDOS> EMAIL LIST

# Send email
uDOS> EMAIL SEND test@example.com "Subject" "Body"
```

---

## ❌ Troubleshooting

### "Credentials file not found"

```bash
ls memory/bank/user/gmail_credentials.json
# If missing, download from Google Cloud Console
```

### "Access blocked: This app is not verified"

**Expected!** Your app isn't verified yet.

**Fix:**
1. Click "Advanced" (bottom left)
2. Click "Go to uDOS (unsafe)" - Safe, it's YOUR app
3. Continue with auth

### Port 8080 in use

```bash
# Kill existing process
kill -9 $(lsof -ti:8080)

# Restart server
python wizard/web/gmail_oauth_server.py
```

---

## 📦 Files Created

| File | Purpose |
|------|---------|
| `wizard/web/gmail_oauth_server.py` | **Standalone test server** (use this!) |
| `wizard/web/gmail_fastapi_routes.py` | OAuth routes (FastAPI) |
| `wizard/web/templates/gmail_oauth.html` | OAuth UI page |
| `wiki/Google-Cloud-Console-Setup.md` | Setup guide |

---

## 🎨 UI Features

- ✅ Dark theme (matches uDOS)
- ✅ Google branding compliance
- ✅ One-click login/logout
- ✅ Permission explanations
- ✅ Token expiry display
- ✅ Flash messages for feedback

---

## 🚀 Next Steps

1. **Authenticate** - Click button, grant permissions
2. **Test TUI** - Use EMAIL commands
3. **Build features:**
   - Email preview widget
   - Drive quota display
   - Send email form
   - Contact import

---

*Version: v1.0.1.0*
*Date: 2026-01-05*
