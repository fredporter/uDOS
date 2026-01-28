# Setup Profile Sync Troubleshooting

**Issue:** "Secret store locked: Unable to decrypt tomb with provided key"

---

## 🔍 Root Cause

The `secrets.tomb` file is encrypted, but the `WIZARD_KEY` environment variable either:

1. Doesn't match the key used to encrypt the file, OR
2. Isn't set/loaded when Wizard Server starts

---

## ✅ Quick Fix

### Option 1: Reset and Re-Submit (Recommended)

```bash
# 1. Backup and remove the old tomb
cd ~/uDOS
source .venv/bin/activate
python wizard/tools/reset_secrets_tomb.py

# 2. Restart Wizard Server
./bin/start_wizard.sh

# 3. Re-run TUI setup story
# (Open new terminal)
./bin/start_udos.sh
# Then complete the setup story questions again
```

After completing the story, the `setup` command will work!

### Option 2: Check Environment Loading

```bash
# 1. Verify WIZARD_KEY is in .env
cat .env | grep WIZARD_KEY

# 2. Restart Wizard Server (to reload .env)
# Stop current server (Ctrl+C in Wizard console)
./bin/start_wizard.sh

# 3. Test
wizard> setup
```

---

## 🧪 Diagnostic Tools

### Check Secret Store Status

```bash
cd ~/uDOS
source .venv/bin/activate
export $(cat .env | xargs)
python wizard/tools/check_secrets_tomb.py
```

**Expected output if working:**

```
✅ WIZARD_KEY is set (length: 43)
✅ secrets.tomb exists (396 bytes)
✅ Secret store unlocked successfully!
   Found 2 entries:
   • wizard-user-profile (provider: wizard_setup)
   • wizard-install-profile (provider: wizard_setup)
✅ User profile found: fred
✅ Install profile found: udos-a1b2c3d4e5f6g7h8
```

---

## 🔐 Understanding the Problem

### How Encryption Works

1. **Setup story submission** creates encrypted profiles:

   ```
   TUI Story → POST /api/v1/setup/story/submit → secrets.tomb
                                                  (encrypted with WIZARD_KEY)
   ```

2. **Reading profiles** requires same key:

   ```
   wizard> setup → load_user_profile() → decrypt secrets.tomb
                                          (needs matching WIZARD_KEY)
   ```

3. **Key mismatch** = locked tomb:
   ```
   If encryption key ≠ decryption key → "Unable to decrypt"
   ```

### Why Keys Might Not Match

- WIZARD_KEY was changed after profiles were saved
- secrets.tomb created before .env file existed
- Server not loading .env properly
- Different WIZARD_KEY between TUI and Wizard environments

---

## 🛠️ Manual Recovery (Advanced)

If you need to recover data without re-running the story:

### 1. Find the Original Key

Check if there's a backup .env:

```bash
cd ~/uDOS
ls -la .env*
# Look for .env.backup or similar
```

### 2. Temporarily Use Old Key

```bash
# Set old key temporarily
export WIZARD_KEY=<old-key-value>
python wizard/tools/check_secrets_tomb.py
# If this works, you found the right key
```

### 3. Export and Re-Import

```python
# With old key loaded:
from wizard.services.setup_profiles import load_user_profile, load_install_profile
user = load_user_profile()
install = load_install_profile()

# Save to JSON
import json
with open('profiles_backup.json', 'w') as f:
    json.dump({
        'user': user.data,
        'install': install.data
    }, f, indent=2)

# Now use new key and re-import via API
```

---

## 📊 Prevention

### Always Keep WIZARD_KEY Stable

The `.env` file should be:

1. ✅ Created before first setup story submission
2. ✅ Never modified after profiles are saved
3. ✅ Backed up securely
4. ✅ Gitignored (never committed)

### Backup Strategy

```bash
# Before changing WIZARD_KEY:
cp wizard/secrets.tomb wizard/secrets.tomb.backup
cp .env .env.backup

# After setup story:
cp wizard/secrets.tomb ~/.udos_secrets_backup
```

---

## 🚀 Starting Fresh (Clean Slate)

If you want to completely reset:

```bash
cd ~/uDOS

# 1. Backup everything
cp wizard/secrets.tomb wizard/secrets.tomb.old
cp .env .env.old

# 2. Remove tomb
rm wizard/secrets.tomb

# 3. Optionally generate new key
# (or keep existing WIZARD_KEY in .env)

# 4. Restart Wizard
./bin/start_wizard.sh

# 5. Re-run TUI setup
./bin/start_udos.sh
```

---

## 📞 Getting Help

If none of these solutions work:

1. **Check logs:** `memory/logs/wizard-server-YYYY-MM-DD.log`
2. **Verify environment:** `env | grep WIZARD`
3. **Test secret store:** `python wizard/tools/check_secrets_tomb.py`
4. **Check tomb permissions:** `ls -la wizard/secrets.tomb`

---

## ✅ Success Indicators

After fixing, you should see:

```bash
wizard> setup

🧙 SETUP PROFILE:

  User Identity:
    • Username: fred
    • Role: admin
    • Timezone: America/Los_Angeles
    • Location: San Francisco (L001-usa-sanfrancisco)

  Installation:
    • ID: udos-a1b2c3d4e5f6g7h8
    • OS Type: macos
    ...
```

---

**Status:** Diagnostic Guide  
**Last Updated:** 2026-01-28
