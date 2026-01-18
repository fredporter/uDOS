# 🔐 Secure Config Panel - Quick Reference

> One-page cheat sheet for managing API keys through Wizard server

---

## 🚀 Launch (1 Command)

```bash
cd /Users/fredbook/Code/uDOS && source .venv/bin/activate && \
  python wizard/launch_wizard_dev.py --no-tui
```

**Then open:** `http://127.0.0.1:8765/api/v1/config/panel`

---

## 🎯 Three Steps to Add a Key

1. **Copy** API key from provider
2. **Paste** into field in web panel
3. **Click** "Save" → See ✅ success

Done! Key is encrypted and secure.

---

## 📋 Key Categories

### AI Providers (5)

- `GEMINI_API_KEY` (Google)
- `OPENAI_API_KEY` (OpenAI)
- `ANTHROPIC_API_KEY` (Anthropic)
- `MISTRAL_API_KEY` (Mistral)
- `OPENROUTER_API_KEY` (OpenRouter)

### GitHub (2)

- `GITHUB_TOKEN` (40+ chars)
- `GITHUB_WEBHOOK_SECRET` (32+ chars)

### OAuth (8)

- Google: `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`
- GitHub: `GITHUB_OAUTH_ID`, `GITHUB_OAUTH_SECRET`
- Microsoft: `MICROSOFT_CLIENT_ID`, `MICROSOFT_CLIENT_SECRET`
- Apple: `APPLE_CLIENT_ID`, `APPLE_CLIENT_SECRET`

### Integrations (7)

- Slack: `SLACK_API_TOKEN`
- Notion: `NOTION_API_KEY`
- HubSpot: `HUBSPOT_API_KEY`
- Gmail: `GMAIL_API_KEY`
- Nounproject: `NOUNPROJECT_API_KEY`
- iCloud: `ICLOUD_API_KEY`
- Twilio: `TWILIO_API_KEY`

### Cloud Services (5)

- `OPENAI_ORG_ID`
- `ANTHROPIC_ORG_ID`
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `CLOUD_PROVIDER_TOKEN`

---

## 🔗 Provider Links

| Provider         | Get Key                                           | Cost                |
| ---------------- | ------------------------------------------------- | ------------------- |
| **Gemini**       | https://makersuite.google.com/app/apikey          | Free                |
| **OpenAI**       | https://platform.openai.com/api-keys              | Pay-as-you-go       |
| **Anthropic**    | https://console.anthropic.com/account/keys        | Pay-as-you-go       |
| **Mistral**      | https://console.mistral.ai/api-keys/              | Free tier available |
| **OpenRouter**   | https://openrouter.ai/keys                        | Pay-as-you-go       |
| **GitHub**       | https://github.com/settings/tokens                | Free                |
| **Google OAuth** | https://console.cloud.google.com/apis/credentials | Free                |
| **Slack**        | https://api.slack.com/apps                        | Free tier available |
| **Notion**       | https://www.notion.so/my-integrations             | Free                |

---

## ✅ After Adding Keys

Generate config files:

```bash
./bin/setup-secrets.sh
```

Verify:

```bash
ls -la wizard/config/*_keys.json
tail wizard/config/keys.audit.log
```

---

## 🔒 Security at a Glance

| Feature         | Status            | Details                                   |
| --------------- | ----------------- | ----------------------------------------- |
| **Encryption**  | ✅ Fernet AES-256 | At-rest encryption in `keys.enc.json`     |
| **Audit Log**   | ✅ Always On      | Tracks all key access in `keys.audit.log` |
| **Validation**  | ✅ Automatic      | Checks key format on save                 |
| **Git Safe**    | ✅ .gitignored    | Config files excluded from git            |
| **Permissions** | ✅ 0o600          | Owner read/write only                     |

---

## 🐛 Troubleshooting

**Port 8765 taken?**

```bash
kill $(lsof -ti:8765)
```

**Module not found?**

```bash
pip install cryptography
```

**Permissions error?**

```bash
chmod 0o600 wizard/config/keys.*.json
```

**Check logs?**

```bash
tail -30 wizard/config/keys.audit.log
```

---

## 📞 URLs

| Purpose          | URL                                          |
| ---------------- | -------------------------------------------- |
| **Config Panel** | `http://127.0.0.1:8765/api/v1/config/panel`  |
| **API Status**   | `http://127.0.0.1:8765/api/v1/config/status` |
| **Health Check** | `http://127.0.0.1:8765/health`               |
| **API Docs**     | `http://127.0.0.1:8765/docs` (debug only)    |

---

## 🎓 REST API Examples

```bash
# Get status
curl http://127.0.0.1:8765/api/v1/config/status | jq

# List keys
curl http://127.0.0.1:8765/api/v1/config/keys | jq

# Set key
curl -X POST http://127.0.0.1:8765/api/v1/config/keys/GEMINI_API_KEY \
  -H "Content-Type: application/json" \
  -d '{"value":"AIzaSy...","provider":"Google","category":"ai_providers"}'

# Delete key
curl -X DELETE http://127.0.0.1:8765/api/v1/config/keys/GEMINI_API_KEY

# Validate key
curl -X POST http://127.0.0.1:8765/api/v1/config/validate/GEMINI_API_KEY
```

---

## 🛡️ Best Practices

✅ **DO:**

- Use unique keys per environment
- Rotate keys monthly
- Monitor audit logs
- Set key expiration dates
- Enable 2FA on provider accounts

❌ **DON'T:**

- Commit `.env` to git
- Share keys in chat
- Use same key for dev/prod
- Ignore audit logs
- Leave old keys in config

---

## 📚 Full Docs

See: `/docs/howto/SECURE-CONFIG-PANEL.md` (comprehensive guide)

---

_Last Updated: 2026-01-18_
