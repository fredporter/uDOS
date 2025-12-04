"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
exports.UPYHoverProvider = void 0;
const vscode = __importStar(require("vscode"));
class UPYHoverProvider {
    constructor() {
        this.commandDocs = {
            // Knowledge Management
            'GUIDE': `**GUIDE** - Knowledge Management System

Manage survival knowledge guides across categories: water, fire, shelter, food, navigation, medical.

**Commands:**
- \`GUIDE ADD tier<N> <type> <title>\` - Add new guide
- \`GUIDE SEARCH <query>\` - Search knowledge base
- \`GUIDE LIST [category]\` - List guides
- \`GUIDE TAG <id> <tags>\` - Add tags
- \`GUIDE UPDATE <id> <field> <value>\` - Update guide
- \`GUIDE DELETE <id>\` - Delete guide
- \`GUIDE EXPORT <id> <format>\` - Export (markdown, json, pdf)
- \`GUIDE STATS\` - Show statistics

**Example:**
\`\`\`upy
GUIDE ADD tier3 guide "Water Purification Methods"
GUIDE TAG guide_123 survival,water,essential
GUIDE SEARCH "fire starting"
\`\`\`

**Categories:** water, fire, shelter, food, navigation, medical
**Tiers:** tier1 (basic), tier2 (intermediate), tier3 (advanced)`,
            'MAP': `**MAP** - Geographic Navigation System

Navigate the global grid using 2-letter TILE codes and layer system.

**Commands:**
- \`MAP GOTO <tile> [layer]\` - Navigate to location
- \`MAP ASCEND\` - Move up layer (surface → cloud → satellite)
- \`MAP DESCEND\` - Move down layer (satellite → surface → underground)
- \`MAP SEARCH <query>\` - Search locations
- \`MAP INFO [tile]\` - Show location details
- \`MAP DISTANCE <from> <to>\` - Calculate distance
- \`MAP ROUTE <from> <to>\` - Find route
- \`MAP NEARBY [radius]\` - Show nearby locations
- \`MAP LAYER <layer_id>\` - Jump to specific layer

**Example:**
\`\`\`upy
MAP GOTO AA340 100     # Sydney, world layer
MAP ASCEND             # Cloud layer
MAP SEARCH "London"    # Find London (returns JF57)
\`\`\`

**Layers:** 100 (world), 200 (region), 300 (city), 400 (district), 500 (block)
**Tile Format:** 2-letter column (AA-RL) + row number (0-269)`,
            'MISSION': `**MISSION** - Mission Management System

Create, track, and manage missions with objectives and progress tracking.

**Commands:**
- \`MISSION CREATE "<name>"\` - Create new mission
- \`MISSION START <id>\` - Start execution
- \`MISSION PAUSE <id>\` - Pause active mission
- \`MISSION RESUME <id>\` - Resume paused mission
- \`MISSION COMPLETE <id>\` - Mark complete
- \`MISSION FAIL <id> <reason>\` - Mark failed
- \`MISSION STATUS [id]\` - Show status
- \`MISSION LIST [filter]\` - List missions
- \`MISSION UPDATE <id> <field> <value>\` - Update field
- \`MISSION DELETE <id>\` - Delete mission

**Example:**
\`\`\`upy
MISSION CREATE "Water Source Survey"
MISSION SET objective "Find 3 clean water sources"
MISSION START mission_001
CHECKPOINT SAVE step_1
MISSION COMPLETE mission_001
\`\`\`

**Status:** DRAFT, ACTIVE, PAUSED, COMPLETED, FAILED`,
            'WORKFLOW': `**WORKFLOW** - Workflow Automation System

Execute automated workflows for complex multi-step operations.

**Commands:**
- \`WORKFLOW START <name>\` - Execute workflow script
- \`WORKFLOW STOP <id>\` - Stop running workflow
- \`WORKFLOW PAUSE <id>\` - Pause execution
- \`WORKFLOW RESUME <id>\` - Resume paused workflow
- \`WORKFLOW STATUS [id]\` - Show status
- \`WORKFLOW LIST\` - List all workflows

**Example:**
\`\`\`upy
WORKFLOW START knowledge-expansion
WORKFLOW STATUS workflow_001
WORKFLOW PAUSE workflow_001
\`\`\`

**System Variables:**
- \`$WORKFLOW.NAME\` - Current workflow name
- \`$WORKFLOW.PHASE\` - Execution phase
- \`$WORKFLOW.ITERATION\` - Loop iteration count
- \`$WORKFLOW.ELAPSED_TIME\` - Execution time in seconds`,
            'CHECKPOINT': `**CHECKPOINT** - State Checkpoint System

Save and restore execution state at critical points.

**Commands:**
- \`CHECKPOINT SAVE <id>\` - Save current state
- \`CHECKPOINT LOAD <id>\` - Load saved state
- \`CHECKPOINT LIST\` - List all checkpoints
- \`CHECKPOINT DELETE <id>\` - Delete checkpoint
- \`CHECKPOINT RESTORE <id>\` - Restore from checkpoint

**Example:**
\`\`\`upy
CHECKPOINT SAVE mission_step_5
# ... execution continues
CHECKPOINT RESTORE mission_step_5  # Rollback if needed
\`\`\`

**System Variables:**
- \`$CHECKPOINT.ID\` - Checkpoint identifier
- \`$CHECKPOINT.TIMESTAMP\` - Save time
- \`$CHECKPOINT.DATA\` - Serialized state
- \`$CHECKPOINT.PREVIOUS\` - Previous checkpoint (linked list)`,
            'GENERATE': `**GENERATE** - Content Generation System

Generate knowledge guides and diagrams using AI assistance.

**Commands:**
- \`GENERATE GUIDE <category> "<title>"\` - Generate knowledge guide
- \`GENERATE DIAGRAM <category> "<subject>"\` - Generate SVG diagram

**Options:**
- \`--complexity <level>\` - simple, detailed, technical
- \`--regen\` - Regenerate existing content
- \`--tier <N>\` - Guide tier (1-3)

**Example:**
\`\`\`upy
GENERATE GUIDE water "Rainwater Collection" --complexity detailed
GENERATE DIAGRAM fire "Friction Fire Starting" --tier 2
\`\`\`

**Requires:** Gemini API key in .env file
**Categories:** water, fire, shelter, food, navigation, medical`,
            'SET': `**SET** - Variable Assignment

Assign values to variables for use in scripts.

**Syntax:**
\`SET <variable> <value>\`

**Example:**
\`\`\`upy
SET $LOCATION "AA340"
SET $MISSION.OBJECTIVE "Find water sources"
SET $COUNT 0
SET $ACTIVE TRUE
\`\`\`

**Variable Naming:**
- Must start with \`$\`
- Use uppercase (convention)
- Dot notation for properties (\`$MISSION.ID\`)`,
            'GET': `**GET** - Retrieve Variable Value

Get the value of a variable.

**Syntax:**
\`GET <variable>\`

**Example:**
\`\`\`upy
GET $LOCATION           # Returns current location
GET $MISSION.STATUS     # Returns mission status
GET $WORKFLOW.ITERATION # Returns iteration count
\`\`\`

**System Variables:**
- \`$MISSION.*\` - Mission context
- \`$WORKFLOW.*\` - Workflow state
- \`$CHECKPOINT.*\` - Checkpoint data
- \`$LOCATION\` - Current tile code
- \`$LAYER\` - Current map layer`,
            'IF': `**IF** - Conditional Execution

Execute code block only if condition is true.

**Syntax:**
\`\`\`upy
IF <condition> THEN
    # code block
ELSE
    # alternative block
END
\`\`\`

**Operators:**
- Comparison: \`==\`, \`!=\`, \`<\`, \`>\`, \`<=\`, \`>=\`
- Logical: \`AND\`, \`OR\`, \`NOT\`

**Example:**
\`\`\`upy
IF $COUNT > 10 THEN
    ECHO "Count exceeds threshold"
ELSE
    ECHO "Count is low"
END

IF $STATUS == "ACTIVE" AND $PROGRESS < 100 THEN
    MISSION CONTINUE
END
\`\`\``,
            'FOREACH': `**FOREACH** - Loop Over Items

Iterate over items in a list or collection.

**Syntax:**
\`\`\`upy
FOREACH $item IN $list
    # process item
END
\`\`\`

**Example:**
\`\`\`upy
GUIDE LIST water
FOREACH $guide IN $guides
    GUIDE TAG $guide survival
    ECHO "Tagged: $guide"
END

FOREACH $location IN $nearby_tiles
    MAP INFO $location
END
\`\`\`

**Break/Continue:**
- \`BREAK\` - Exit loop
- \`CONTINUE\` - Skip to next iteration`,
            'WHILE': `**WHILE** - Conditional Loop

Repeat code block while condition is true.

**Syntax:**
\`\`\`upy
WHILE <condition>
    # code block
END
\`\`\`

**Example:**
\`\`\`upy
SET $count 0
WHILE $count < 100
    SET $count ($count + 1)
    ECHO "Iteration: $count"
END

WHILE $MISSION.STATUS == "ACTIVE"
    MISSION UPDATE progress ($progress + 10)
    CHECKPOINT SAVE auto_save_$count
END
\`\`\`

**Warning:** Ensure loop has exit condition to avoid infinite loops`,
            'BACKUP': `**BACKUP** - File Backup System

Create timestamped backups in .archive/ folders.

**Commands:**
- \`BACKUP <file>\` - Create backup
- \`BACKUP LIST <file>\` - List backups
- \`BACKUP RESTORE <file> [timestamp]\` - Restore from backup
- \`BACKUP CLEAN [days]\` - Remove old backups

**Example:**
\`\`\`upy
BACKUP memory/system/user/config.json
BACKUP LIST config.json
BACKUP RESTORE config.json 20251204_143022
\`\`\`

**Location:** \`.archive/backups/\` (30-day retention)`,
            'UNDO': `**UNDO** - Version History Navigation

Revert file to previous version.

**Commands:**
- \`UNDO <file>\` - Revert to previous version
- \`REDO <file>\` - Re-apply undone changes

**Example:**
\`\`\`upy
# Made changes to script
UNDO memory/workflows/missions/water-survey.upy
# Changed your mind
REDO memory/workflows/missions/water-survey.upy
\`\`\`

**Location:** \`.archive/versions/\` (90-day retention, last 5 versions)`,
            'CLEAN': `**CLEAN** - Workspace Cleanup

Clean memory workspace and manage .archive/ folders.

**Commands:**
- \`CLEAN\` - Interactive cleanup
- \`CLEAN --scan\` - Show archive health metrics
- \`CLEAN --purge [days]\` - Remove old archives

**Example:**
\`\`\`upy
CLEAN --scan              # Check archive usage
CLEAN --purge 30          # Remove archives older than 30 days
\`\`\`

**Scans:**
- Trash files
- Temporary files
- Old backups (>30 days)
- Old versions (>90 days)
- Deleted files (>7 days)`,
            'STATUS': `**STATUS** - System Status Dashboard

Show comprehensive system status and metrics.

**Options:**
- \`STATUS\` - Basic status
- \`STATUS --detailed\` - Full dashboard
- \`STATUS --health\` - Health metrics

**Displays:**
- Current location and layer
- Active missions
- Running workflows
- Knowledge bank statistics
- Memory usage
- Archive health
- Extension status
- Server status

**Example:**
\`\`\`upy
STATUS --detailed
\`\`\``,
        };
    }
    provideHover(document, position) {
        const range = document.getWordRangeAtPosition(position);
        if (!range) {
            return null;
        }
        const word = document.getText(range);
        // Check for command documentation
        if (this.commandDocs[word]) {
            return new vscode.Hover(new vscode.MarkdownString(this.commandDocs[word]));
        }
        // Check for system variables
        if (word.startsWith('$')) {
            return this.getVariableHover(word);
        }
        return null;
    }
    getVariableHover(variable) {
        const varDocs = {
            '$MISSION.ID': '**Mission ID** - Unique identifier for current mission',
            '$MISSION.NAME': '**Mission Name** - Human-readable mission name',
            '$MISSION.STATUS': '**Mission Status** - Current status (DRAFT, ACTIVE, PAUSED, COMPLETED, FAILED)',
            '$MISSION.PROGRESS': '**Mission Progress** - Completion percentage or ratio',
            '$MISSION.START_TIME': '**Mission Start Time** - ISO timestamp when mission started',
            '$MISSION.OBJECTIVE': '**Mission Objective** - Primary mission goal',
            '$WORKFLOW.NAME': '**Workflow Name** - Current workflow script name',
            '$WORKFLOW.PHASE': '**Workflow Phase** - Execution phase (INIT, SETUP, EXECUTE, MONITOR, COMPLETE)',
            '$WORKFLOW.ITERATION': '**Workflow Iteration** - Current loop iteration count',
            '$WORKFLOW.ERRORS': '**Workflow Errors** - Number of errors encountered',
            '$WORKFLOW.ELAPSED_TIME': '**Workflow Elapsed Time** - Seconds since workflow started',
            '$CHECKPOINT.ID': '**Checkpoint ID** - Unique checkpoint identifier',
            '$CHECKPOINT.TIMESTAMP': '**Checkpoint Timestamp** - When checkpoint was saved',
            '$CHECKPOINT.DATA': '**Checkpoint Data** - Serialized state data',
            '$LOCATION': '**Current Location** - Current TILE code (e.g., AA340)',
            '$TILE': '**Current Tile** - Current grid tile code',
            '$LAYER': '**Current Layer** - Current map layer (100-500)',
            '$MODE': '**Current Mode** - System mode (REGULAR, DEV, ASSIST)',
            '$THEME': '**Current Theme** - Active theme name',
        };
        if (varDocs[variable]) {
            return new vscode.Hover(new vscode.MarkdownString(varDocs[variable]));
        }
        return null;
    }
}
exports.UPYHoverProvider = UPYHoverProvider;
//# sourceMappingURL=hover.js.map