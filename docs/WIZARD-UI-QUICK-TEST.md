# Wizard UI Restyling — Quick Test Guide

**Status:** Ready for manual browser testing  
**Duration:** ~5 minutes to validate

---

## 🚀 Quick Start

### 1. Launch Wizard Server

```bash
cd /Users/fredbook/Code/uDOS

# Option A: Background server only
source .venv/bin/activate
python wizard/launch_wizard_dev.py --no-tui &

# Option B: Using launch script
bin/Launch-Wizard-Dev.command
```

Wait for server to start:

```
✅ Wizard Server running on http://127.0.0.1:8765
```

### 2. Open Config Panel in Browser

```
http://127.0.0.1:8765/api/v1/config/panel
```

---

## ✅ Visual Checklist (30 seconds)

**Theme:**

- [ ] Dark background (very dark gray/black, not light)
- [ ] Dark cards (darker gray, not white)
- [ ] Light text (readable on dark background)
- [ ] Blue accents (buttons, highlights)

**Layout:**

- [ ] Top header with title and logo area
- [ ] Main content area in the middle
- [ ] Bottom status bar at very bottom
- [ ] Centered layout (not edge-to-edge)

**Categories:**

- [ ] Category cards visible
- [ ] Each category has a name
- [ ] Each category shows list of secret keys
- [ ] Keys are properly indented

**Emoji:**

- [ ] Headers have small emoji icons before text
- [ ] Emoji are monochrome (not colored)
- [ ] Emoji are readable size

**Buttons:**

- [ ] "Add Secret" button visible and blue
- [ ] Delete buttons visible (trash icon)
- [ ] Hover effects work (button changes color)

---

## 🔍 Console Check (Browser DevTools)

**Press:** `Ctrl+Shift+K` (or `Cmd+Option+K` on Mac)

**Look for:**

```
✅ NO 404 errors for:
   - /static/css/global.css
   - /static/fonts/NotoColorEmoji.ttf
   - /static/fonts/NotoEmoji-Regular.ttf

✅ NO JavaScript errors
✅ NO CORS errors
```

**If you see 404s:**

- Server not serving static files
- Check: Has `/static/` been mounted in `wizard/server.py`?
- Restart server

---

## 🧪 Functional Checks (2 minutes)

### Test 1: Categories Load

1. View page → should see "database", "api", "github", etc.
2. Each category → shows list of keys inside
3. ✅ If categories empty or missing → bug still present

### Test 2: Add Secret

1. Click "Add Secret" button
2. Fill in name: `test_key`
3. Fill in value: `test_value`
4. Click Save
5. ✅ Key should appear in appropriate category

### Test 3: View Secret

1. Click eye icon next to a secret
2. Value should appear/disappear
3. ✅ Toggle should work smoothly

### Test 4: Delete Secret

1. Click delete (trash) icon
2. Confirmation should appear
3. Click "Yes, Delete"
4. ✅ Secret should disappear from list

### Test 5: Search/Filter (if implemented)

1. Type in search box (if visible)
2. Should filter secrets by name
3. ✅ Only matching secrets show

---

## 📱 Mobile Check (2 minutes)

**Open DevTools:**

- `Ctrl+Shift+I` → toggle device toolbar → `Ctrl+Shift+M`

**Test at 375px width (phone):**

- [ ] Layout still looks good (no horizontal scroll)
- [ ] Text readable
- [ ] Buttons touchable (not too small)
- [ ] Categories still visible (might be stacked)

**Test at 768px width (tablet):**

- [ ] Two-column layout (if supported)
- [ ] All controls accessible

---

## 🎨 Color Verification

**Expected Colors:**

| Element    | RGB           | Hex       | Name      |
| ---------- | ------------- | --------- | --------- |
| Background | `3 7 18`      | `#030712` | gray-950  |
| Cards      | `15 23 42`    | `#0F172A` | slate-900 |
| Text       | `229 231 235` | `#E5E7EB` | gray-200  |
| Accents    | `59 130 246`  | `#3B82F6` | blue-500  |
| Success    | `34 197 94`   | `#22C55E` | green-500 |
| Warning    | `245 158 11`  | `#F59E0B` | amber-500 |

**Check in browser DevTools:**

1. Right-click any element → Inspect
2. In Styles panel, look for color values
3. Should match table above

---

## 🚨 Troubleshooting

### Issue: Page is all white/light

**Cause:** CSS not loading  
**Fix:**

1. Check console for 404 on `/static/css/global.css`
2. Verify file exists: `public/wizard/static/css/global.css`
3. Restart server

### Issue: Emoji shows as colored squares

**Cause:** Font not loading (showing system emoji instead of Noto)  
**Fix:**

1. Check console for 404 on `/static/fonts/NotoEmoji-Regular.ttf`
2. Verify symlinks: `ls -lah public/wizard/static/fonts/`
3. Check Goblin fonts exist: `ls -lah dev/goblin/public/fonts/`

### Issue: Categories empty

**Cause:** API not returning data (not a CSS issue)  
**Fix:**

1. Check server logs for errors
2. Test API directly: `curl http://127.0.0.1:8765/api/v1/config/status`
3. Verify database has secrets stored

### Issue: Page looks right but buttons don't work

**Cause:** JavaScript error  
**Fix:**

1. Open console (DevTools)
2. Look for JavaScript errors
3. Check if config panel API is responding

---

## 📊 Success Metrics

**Minimum (Styling Only):**

- [x] Dark background applied
- [x] Text readable
- [x] Categories visible
- [x] No 404 errors

**Good (With Functionality):**

- [x] Dark background applied
- [x] Text readable
- [x] Categories load with data
- [x] Buttons work (add, delete, view)
- [x] Emoji renders properly
- [x] No console errors

**Excellent (Polish):**

- [x] All of above
- [x] Works on mobile
- [x] Smooth transitions/hover effects
- [x] Bottom-bar status shows correctly
- [x] Delete confirmation appears

---

## 🔗 Resources

**Files Changed:**

- `public/wizard/static/css/global.css` (CSS)
- `public/wizard/routes/config.py` (HTML)
- `public/wizard/server.py` (static mount)
- `public/wizard/services/emoji_map.py` (emoji support)

**Documentation:**

- `docs/WIZARD-UI-RESTYLING-COMPLETE.md` (full report)
- `docs/devlog/2026-01-18-wizard-ui-restyling.md` (session log)

**Emoji Map:**

- 40+ emojis available in `emoji_map.py`
- Usage: `<span class="emoji-mono">🔐</span>`

---

## ⏱️ Timeline

| Task              | Duration   | Status       |
| ----------------- | ---------- | ------------ |
| Start server      | 10 sec     | Ready        |
| Open config panel | 5 sec      | Ready        |
| Visual check      | 30 sec     | Ready        |
| Functional tests  | 2 min      | Ready        |
| Mobile check      | 2 min      | Ready        |
| **Total**         | **~5 min** | **✅ Ready** |

---

## 💾 Commit When Ready

Once testing is complete:

```bash
git add -A
git commit -m "Wizard UI: Dark Tailwind + Emoji + Static files [TESTED ✅]"
```

---

**Last Updated:** 2026-01-18  
**Next:** Extract uFont Manager (use `EXTRACT-UFONT-MANAGER-PLAN.md`)
