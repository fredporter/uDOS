# Configuration Quick Reference Card

**Dashboard:** http://localhost:8765/api/v1/config/dashboard

---

## Files at a Glance

| File            | Where                   | What                            | Commit |
| --------------- | ----------------------- | ------------------------------- | ------ |
| **wizard.json** | `public/wizard/config/` | Server config, features, limits | ✅ YES |
| **.env**        | `~/.uDOS/config/`       | API keys, credentials           | ❌ NO  |
| **.env-local**  | `~/.uDOS/config/`       | Dev overrides (optional)        | ❌ NO  |

---

## Adding API Keys - 3 Steps

1. **Open Dashboard**

   ```
   http://localhost:8765/api/v1/config/dashboard
   ```

2. **Select .env (secrets)**
   - Click file dropdown
   - Choose `.env (secrets)`

3. **Add Key & Save**
   ```env
   OPENAI_API_KEY=sk-proj-your-key
   ```

   - Add your API keys
   - Click 💾 Save (or Ctrl+S)
   - See 🟢 CONNECTED in API Status

---

## API Key Providers

| API     | Site                                 | Key Starts With |
| ------- | ------------------------------------ | --------------- |
| OpenAI  | https://platform.openai.com/api-keys | `sk-proj-`      |
| Claude  | https://console.anthropic.com/       | `sk-ant-`       |
| Gemini  | https://ai.google.dev/               | `AIza`          |
| Mistral | https://console.mistral.ai/          | varies          |
| GitHub  | https://github.com/settings/tokens   | `ghp_`          |
| AWS     | https://console.aws.amazon.com/iam/  | `AKIA`          |

---

## Format Rules

```
✅ CORRECT:
OPENAI_API_KEY=sk-proj-abc123
GITHUB_TOKEN=ghp_xyz789

❌ WRONG:
OPENAI_API_KEY = sk-proj-abc123  (spaces around =)
OPENAI_API_KEY="sk-proj-abc123"  (quotes)
$OPENAI_API_KEY=sk-proj-abc123   ($ prefix)
```

---

## Status Indicators

| Status       | Meaning              | Action       |
| ------------ | -------------------- | ------------ |
| 🟢 CONNECTED | Key configured       | Ready to use |
| 🟡 PARTIAL   | Key exists but empty | Add value    |
| 🔴 MISSING   | Key not configured   | Add to .env  |

---

## CLI Commands

```bash
# View all config files
ls -la ~/.uDOS/config/

# Edit .env directly
nano ~/.uDOS/config/.env

# Check .env syntax
grep "^[A-Z]" ~/.uDOS/config/.env

# List all configured keys
grep "^[A-Z]" ~/.uDOS/config/.env | wc -l

# Verify a key is set
grep "OPENAI_API_KEY" ~/.uDOS/config/.env

# Secure permissions
chmod 600 ~/.uDOS/config/.env

# View server config
cat public/wizard/config/wizard.json | jq .
```

---

## Available APIs (11 Total)

### AI Providers (4)

- OpenAI - `OPENAI_API_KEY`
- Anthropic - `ANTHROPIC_API_KEY`
- Google - `GOOGLE_API_KEY`
- Mistral - `MISTRAL_API_KEY`

### Developer (2)

- GitHub - `GITHUB_TOKEN`
- GitLab - `GITLAB_TOKEN`

### Cloud (2)

- AWS - `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`
- Google Cloud - `GOOGLE_CLOUD_KEY_JSON`

### Integrations (3)

- Notion - `NOTION_API_KEY`
- Slack - `SLACK_BOT_TOKEN`
- HubSpot - `HUBSPOT_PRIVATE_APP_TOKEN`

---

## Troubleshooting

| Problem                   | Solution                           |
| ------------------------- | ---------------------------------- |
| Dashboard shows 429 error | Rate limit fixed ✅ - reload page  |
| File dropdown empty       | Create `~/.uDOS/config/.env` first |
| Can't save .env           | `chmod 600 ~/.uDOS/config/.env`    |
| Keys not loading          | Check spelling (case-sensitive)    |
| API Status empty          | Restart server: `pkill -f uvicorn` |

---

## Security Reminders

✅ **DO:**

- Add all API keys to `~/.uDOS/config/.env`
- Keep `.env` file safe and secure
- Set file permissions: `chmod 600`
- Rotate keys regularly
- Use separate keys for dev/prod

❌ **DON'T:**

- Commit `.env` to git
- Share `.env` files
- Put API keys in wizard.json
- Log or print API keys
- Use production keys in dev

---

## Useful Links

- **Full Guide:** `docs/CONFIG-SYSTEM-COMPLETE.md`
- **Step-by-Step:** `docs/howto/ADDING-API-KEYS.md`
- **Architecture:** `docs/howto/CONFIGURATION-STRATEGY.md`
- **Template:** `public/wizard/config/.env.example`

---

## Server Control

```bash
# Start server
cd /Users/fredbook/Code/uDOS
source .venv/bin/activate
python -m uvicorn public.wizard.server:app --host 127.0.0.1 --port 8765

# Stop server
pkill -f uvicorn

# Check if running
lsof -i :8765

# View logs
tail -f /tmp/wizard_server.log
```

---

**Configuration System v1.1.0** | Ready to use! 🚀
