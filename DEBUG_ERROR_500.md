# How to Debug the Error 500

The error logging is now in place. To get the actual error:

## Option 1: Check Server Stderr (Recommended)

1. **Open a new terminal window**
2. **Restart the Wizard server with stderr visible:**
   ```bash
   cd /home/wizard/Code/uDOS
   pkill -f "wizard.server" || true
   PYTHONPATH="/home/wizard/Code/uDOS" python -m wizard.server --port 9001 2>&1 | tee /tmp/wizard-stderr.log
   ```

3. **In another terminal, access the Dashboard:**
   ```bash
   # Get the URL from the server output above
   # Typically something like: http://127.0.0.1:9001
   ```

4. **Click one of the self-heal buttons in the Dashboard:**
   - INSTALL VIBE
   - SEED ICONS
   - PULL MODEL

5. **Look at the first terminal where you ran the server - you should see `[ERROR]` lines printed**

6. **Copy those error lines and share them**

## Option 2: Check the Log File

After testing, check the log file:
```bash
tail -50 /tmp/wizard-stderr.log
```

## Option 3: Run Route Test Directly

```bash
cd /home/wizard/Code/uDOS
python test_routes_direct.py
```

This will show any import errors.

---

Once you run one of these and see the error, send me the output and I can fix the actual issue.
