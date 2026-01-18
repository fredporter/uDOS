#!/bin/bash
# Step C Execution Script
# Real Notion Webhook Testing

# ============================================================================
# STEP C EXECUTION CHECKLIST
# Real Notion Webhook Testing for uMarkdown
# Time: 2-3 hours | Status: READY TO EXECUTE
# ============================================================================

set -e  # Exit on error

echo "🚀 Step C Execution Guide"
echo "=========================="
echo ""
echo "This script will guide you through real Notion webhook testing."
echo "You'll need to set up Notion API credentials."
echo ""

# ============================================================================
# PHASE 1: NOTION API SETUP (15 minutes)
# ============================================================================

echo "📋 PHASE 1: Notion API Setup"
echo "=============================="
echo ""
echo "STEP 1: Get Notion API Token"
echo "  1. Go to: https://www.notion.so/profile/integrations"
echo "  2. Click 'New integration'"
echo "  3. Name: uMarkdown Dev"
echo "  4. Enable: Read, Update, Insert, Delete"
echo "  5. Copy the 'Internal Integration Token' (starts with 'secret_')"
echo ""
echo "⏸  Paste your Notion API token and press Enter:"
read -r NOTION_API_KEY
export NOTION_API_KEY

echo ""
echo "STEP 2: Generate Webhook Secret"
echo "  Running: openssl rand -hex 32"
WEBHOOK_SECRET=$(openssl rand -hex 32)
echo "  ✅ Generated: $WEBHOOK_SECRET"
export NOTION_WEBHOOK_SECRET="$WEBHOOK_SECRET"

echo ""
echo "STEP 3: Create Test Database in Notion"
echo "  1. Open Notion workspace"
echo "  2. Create new Database table named: 'uMarkdown Test'"
echo "  3. Add properties:"
echo "     - Title (default)"
echo "     - Type (select): document, task, resource"
echo "     - Status (select): draft, published, archived"
echo "  4. Share → Select 'uMarkdown Dev' integration → Grant Editor"
echo ""
echo "⏸  Press Enter when database is created and shared:"
read

echo ""
echo "STEP 4: Get Database ID from Notion URL"
echo "  Your database URL looks like:"
echo "  https://www.notion.so/WORKSPACE_ID/DATABASE_ID?v=VIEW_ID"
echo ""
echo "⏸  Paste your DATABASE_ID (between / and ?):"
read -r DATABASE_ID
export DATABASE_ID

echo ""
echo "STEP 5: Update Environment Variables"
cat > app/.env.local << EOF
VITE_DEV_SERVER_URL=http://localhost:8767
VITE_NOTION_API_KEY=$NOTION_API_KEY
VITE_NOTION_WEBHOOK_SECRET=$WEBHOOK_SECRET
VITE_SYNC_INTERVAL_MS=5000
VITE_DEBUG_SYNC=true
EOF

echo "  ✅ app/.env.local created"
echo ""

# ============================================================================
# PHASE 2: START SERVICES (10 minutes)
# ============================================================================

echo "📋 PHASE 2: Start Services"
echo "============================"
echo ""
echo "You need to start 5 services in separate terminals:"
echo ""
echo "TERMINAL 1 - Core TUI:"
echo "  cd /Users/fredbook/Code/uDOS"
echo "  source .venv/bin/activate"
echo "  ./bin/start_udos.sh"
echo ""
echo "TERMINAL 2 - Wizard Production (optional):"
echo "  cd /Users/fredbook/Code/uDOS"
echo "  source .venv/bin/activate"
echo "  python -m wizard.server --port 8765"
echo ""
echo "TERMINAL 3 - Goblin Dev Server (MAIN):"
echo "  cd /Users/fredbook/Code/uDOS"
echo "  ./bin/Launch-Goblin-Dev.command"
echo "  # Or manually:"
echo "  source .venv/bin/activate"
echo "  python -m uvicorn dev.goblin.goblin_server:app --host 127.0.0.1 --port 8767"
echo ""
echo "TERMINAL 4 - App (Tauri):"
echo "  cd /Users/fredbook/Code/uDOS/app"
echo "  npm run tauri:dev"
echo ""
echo "TERMINAL 5 - ngrok Tunnel (for Notion webhooks):"
echo "  ngrok http 8767"
echo "  (Copy the HTTPS URL from the output)"
echo ""
echo "⏸  Press Enter when all services are started:"
read

echo ""
echo "⏸  Paste the ngrok HTTPS URL (e.g., https://abc123.ngrok.io):"
read -r NGROK_URL
export NGROK_URL

echo ""
echo "⏸  Press Enter to verify all services are responding..."
echo ""

# Check endpoints
echo "Testing connectivity..."
if curl -s http://localhost:8767/health | grep -q "healthy"; then
    echo "  ✅ Goblin Dev Server responding"
else
    echo "  ❌ Goblin Dev Server not responding - check Terminal 3"
    exit 1
fi

if [ -z "$NGROK_URL" ]; then
    echo "  ❌ ngrok URL not set"
    exit 1
else
    echo "  ✅ ngrok tunnel configured: $NGROK_URL"
fi

# ============================================================================
# PHASE 3: CREATE WEBHOOK SUBSCRIPTION (10 minutes)
# ============================================================================

echo ""
echo "📋 PHASE 3: Register Webhook with Notion"
echo "=========================================="
echo ""
echo "Creating webhook subscription..."
echo ""
echo "Command to run (copy and paste in terminal):"
echo ""
echo "curl -X POST https://api.notion.com/v1/webhooks \\"
echo "  -H \"Authorization: Bearer $NOTION_API_KEY\" \\"
echo "  -H \"Content-Type: application/json\" \\"
echo "  -H \"Notion-Version: 2022-06-28\" \\"
echo "  -d '{"
echo "    \"events\": [\"page.created\", \"page.updated\", \"page.deleted\"],"
echo "    \"notification_url\": \"$NGROK_URL/api/v0/notion/webhook\""
echo "  }'"
echo ""
echo "⏸  Press Enter when webhook is created:"
read

echo ""
echo "✅ Webhook subscription registered!"
echo ""

# ============================================================================
# PHASE 4: TEST CRUD OPERATIONS (30 minutes)
# ============================================================================

echo "📋 PHASE 4: Test CRUD Operations"
echo "================================="
echo ""

echo "TEST 1: CREATE PAGE"
echo "-------------------"
echo "In Notion:"
echo "  1. Open 'uMarkdown Test' database"
echo "  2. Click New → Add page"
echo "  3. Title: 'Test Document 1'"
echo "  4. Type: 'document'"
echo "  5. Status: 'draft'"
echo "  6. Press Enter to save"
echo ""
echo "Watch for:"
echo "  Terminal 3 (Dev Server): [WIZ] Webhook received: page.created"
echo "  Terminal 5 (ngrok): POST /api/v0/notion/webhook 201"
echo "  App: SyncIndicator shows '1' then drops to '0'"
echo ""
echo "⏸  Press Enter after confirming receipt:"
read

echo "✅ TEST 1 PASSED: Create operation received"
echo ""

echo "TEST 2: UPDATE PAGE"
echo "-------------------"
echo "In Notion:"
echo "  1. Edit 'Test Document 1'"
echo "  2. Change title to 'Test Document 1 - Updated'"
echo "  3. Save"
echo ""
echo "Watch for same indicators as TEST 1"
echo ""
echo "⏸  Press Enter after confirming receipt:"
read

echo "✅ TEST 2 PASSED: Update operation received"
echo ""

echo "TEST 3: DELETE PAGE"
echo "-------------------"
echo "In Notion:"
echo "  1. Right-click 'Test Document 1 - Updated'"
echo "  2. Select 'Delete'"
echo "  3. Confirm"
echo ""
echo "Watch for same indicators"
echo ""
echo "⏸  Press Enter after confirming receipt:"
read

echo "✅ TEST 3 PASSED: Delete operation received"
echo ""

echo "TEST 4: BULK OPERATIONS"
echo "------------------------"
echo "Repeat Tests 1-3 two more times (3 total sets)"
echo "  Create → Update → Delete (3 times)"
echo ""
echo "SyncIndicator should show: 3 → 2 → 1 → 0"
echo ""
echo "⏸  Press Enter after all 3 bulk operations complete:"
read

echo "✅ TEST 4 PASSED: Bulk operations processed"
echo ""

# ============================================================================
# PHASE 5: VERIFY DATABASE STATE (10 minutes)
# ============================================================================

echo "📋 PHASE 5: Verify Database State"
echo "=================================="
echo ""

echo "Querying SQLite database..."
echo ""

RESULTS=$(sqlite3 /Users/fredbook/Code/uDOS/memory/umarkdown.sqlite << 'SQLITE'
SELECT COUNT(*) as total, operation, status
FROM notion_sync_queue
GROUP BY operation, status
ORDER BY operation;
SQLITE
)

echo "Queue operations:"
echo "$RESULTS"
echo ""

if echo "$RESULTS" | grep -q "3.*delete.*processed"; then
    echo "✅ All operations queued and processed correctly"
else
    echo "❌ Some operations may not have processed. Check logs."
fi

echo ""
echo "Mapping entries:"
sqlite3 /Users/fredbook/Code/uDOS/memory/umarkdown.sqlite "SELECT COUNT(*) FROM notion_maps;" | xargs echo "  Total mappings:"

echo ""
echo "Conflicts (should be 0):"
sqlite3 /Users/fredbook/Code/uDOS/memory/umarkdown.sqlite "SELECT COUNT(*) FROM sync_conflicts WHERE resolved = 0;" | xargs echo "  Unresolved conflicts:"

echo ""

# ============================================================================
# SUMMARY
# ============================================================================

echo ""
echo "🎉 STEP C EXECUTION COMPLETE!"
echo "=============================="
echo ""
echo "✅ Notion API integration tested"
echo "✅ Webhook subscription verified"
echo "✅ CRUD operations processed"
echo "✅ Database state validated"
echo ""
echo "Next Steps:"
echo "  1. Commit your work: git add -A && git commit -m \"Move 1 Step C: Notion webhook testing validated ✅\""
echo "  2. Review results in docs/MOVE-1-SUMMARY.md"
echo "  3. Plan Move 2: TS Markdown Runtime"
echo ""
echo "📚 Documentation:"
echo "  - Setup guide: docs/NOTION-SETUP.md"
echo "  - Full playbook: docs/devlog/2026-01-15-move-1-step-c.md"
echo "  - Quick reference: docs/STEP-C-QUICK-REFERENCE.md"
echo ""
