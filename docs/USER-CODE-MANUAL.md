# uCODE MODULAR SCRIPTING REFERENCE MANUAL

```ascii
    ██╗   ██╗ ██████╗ ██████╗ ██████╗ ███████╗
    ██║   ██║██╔════╝██╔═══██╗██╔══██╗██╔════╝
    ██║   ██║██║     ██║   ██║██║  ██║█████╗
    ██║   ██║██║     ██║   ██║██║  ██║██╔══╝
    ╚██████╔╝╚██████╗╚██████╔╝██████╔╝███████╗
     ╚═════╝  ╚═════╝ ╚═════╝ ╚═════╝ ╚══════╝

    uCODE & uSCRIPT Technical Reference
    ═══════════════════════════════════════════════════
```

**Version**: 1.0.4.1
**Date**: August 26, 2025
**Part Number**: uCODE-REF-002
**Status**: Production Ready

Complete technical reference for uCODE native programming language and uSCRIPT modular scripting system on uDOS. Features universal shortcode syntax `[COMMAND|OPTION]` structure, role-based container execution, and integrated template processing.

---

## TABLE OF CONTENTS

- [SYSTEM OVERVIEW](#system-overview)
- [uCODE CORE COMMANDS](#ucode-core-commands)
- [uSCRIPT MODULAR SYSTEM](#uscript-modular-system)
- [CONTAINER EXECUTION](#container-execution)
- [ROLE MANAGEMENT](#role-management)
- [TEMPLATE INTEGRATION](#template-integration)
- [MEMORY & DATA SYSTEMS](#memory--data-systems)
- [GRID DISPLAY SYSTEM](#grid-display-system)
- [WORKFLOW AUTOMATION](#workflow-automation)
- [ERROR HANDLING](#error-handling)
- [ADVANCED SCRIPTING](#advanced-scripting)
- [BEST PRACTICES](#best-practices)
- [IMPLEMENTATION GUIDE](#implementation-guide)

---

## SYSTEM OVERVIEW

### Architecture Hierarchy
```
uDOS v1.0.4.1 System Stack
┌─────────────────────────────────────┐
│ uCODE Native Language              │ ← Direct system commands
├─────────────────────────────────────┤
│ uSCRIPT Modular System             │ ← Container execution (Crypt+)
├─────────────────────────────────────┤
│ uSERVER Runtime Engine             │ ← Script execution environment
├─────────────────────────────────────┤
│ uMEMORY Template & Variable System │ ← System state management
├─────────────────────────────────────┤
│ uGRID Display & Navigation         │ ← Visual interface layer
└─────────────────────────────────────┘
```

### Universal Shortcode Structure
**Every command supports shortcode syntax:**
```ucode
DIRECT:     COMMAND PARAMETER
SHORTCODE:  [COMMAND|OPTION]
ADVANCED:   [COMMAND|OPTION*PARAMETER*VALUE]
```

### Role-Based Access Control
```ucode
👻 GHOST (10)     → Read-only, basic uCODE
⚰️ TOMB (20)      → Storage access, simple scripts
🔐 CRYPT (30)     → Container access, uSCRIPT execution ★
🤖 DRONE (40)     → Automation scripts, scheduled execution
⚔️ KNIGHT (50)    → Security scripts, system management
😈 IMP (60)       → Advanced automation, multi-language containers
🧙‍♂️ SORCERER (80) → Development tools, full scripting access
🧙‍♀️ WIZARD (100)  → System administration, all features
```

**★ uSCRIPT Minimum**: CRYPT (30) role required for container execution

---

## uCODE CORE COMMANDS
- [SETUP COMMANDS](#setup-commands)
- [SCRIPT EXECUTION](#script-execution)
- [UNDO/REDO OPERATIONS](#undoredo-operations)
- [ERROR HANDLING](#error-handling)
- [EXAMPLES](#examples)
- [BEST PRACTICES](#best-practices)

## CORE COMMANDS

### [SYS] <ACTION> {PARAMETER}
```ucode
~ System operations
[SYS] <STATUS>              ~ Check system status
[SYS] <STATUS> {VERBOSE}    ~ Detailed status
[SYS] <STATUS|BRIEF>        ~ Brief status with pipe option
[SYS] <INFO> {HARDWARE}     ~ Hardware information
[SYS] <INFO|DETAILED> {CPU} ~ Detailed CPU info with pipe
[SYS] <VERSION>             ~ Version information
[SYS] <RESTART>             ~ Restart system
[SYS] <RESTART|SAFE>        ~ Safe restart with pipe option
[SYS] <OPTIMIZE> {TARGET}   ~ System optimization
[SYS] <OPTIMIZE|FORCE> {MEMORY} ~ Force memory optimization
```

### [LOG] <LEVEL> {MESSAGE}
```ucode
~ Logging operations
[LOG] <INFO> {MESSAGE}      ~ Information logging
[LOG] <WARNING> {MESSAGE}   ~ Warning logging
[LOG] <ERROR> {MESSAGE}     ~ Error logging
[LOG] <DEBUG> {MESSAGE}     ~ Debug logging
[LOG] <INFO|TIMESTAMP> {MESSAGE} ~ Info with timestamp option
[LOG] <ERROR|CRITICAL> {MESSAGE} ~ Critical error logging
```

## DIRECT COMMANDS

### TRASH <ACTION> {PARAMETER}
```bash
~ Direct trash management commands
TRASH {FILE-PATH}           ~ Move file/folder to role-specific trash
TRASH list                  ~ List trash contents for current role
TRASH empty                 ~ Empty trash (permanent deletion)
TRASH restore {ITEM-NAME}   ~ Restore specific item from trash
```

### BACKUP <ACTION> {PARAMETER}
```bash
~ Direct backup management commands
BACKUP create               ~ Create backup of current role's data
BACKUP list                 ~ List available backups for current role
BACKUP restore {BACKUP-NAME} ~ Restore from specific backup file
```

### ROLE <ACTION> {PARAMETER}
```bash
~ Direct role management commands
ROLE list                   ~ List all available roles with descriptions
ROLE switch {ROLE-NAME}     ~ Switch to different role
ROLE check                  ~ Check current role setup and permissions
ROLE install {EXTENSION}    ~ Install role-specific extensions
```

---

## uSCRIPT MODULAR SYSTEM

### Overview
**uSCRIPT** provides containerized execution of Python, Shell, and JavaScript scripts within uCODE. Requires **CRYPT (30+)** role and active **uSERVER** + **uMEMORY** systems.

### Container Types
```ucode
<PYTHON>    ~ Python 3.8+ container
<SHELL>     ~ Bash/Shell container
<NODE>      ~ Node.js/JavaScript container
<UNIVERSAL> ~ Multi-language container
```

### Basic uSCRIPT Commands
```ucode
[SCRIPT|CREATE*CONTAINER*NAME*LANGUAGE] ~ Create new script container
[SCRIPT|RUN*NAME]                       ~ Execute script container
[SCRIPT|LIST]                           ~ List available containers
[SCRIPT|DELETE*NAME]                    ~ Delete script container
[SCRIPT|EDIT*NAME]                      ~ Edit container content
[SCRIPT|STATUS*NAME]                    ~ Check container status
```

### Advanced uSCRIPT Commands
```ucode
[SCRIPT|CREATE*PYTHON*ANALYZER*DATA-ANALYSIS]     ~ Create Python container
[SCRIPT|CREATE*SHELL*BACKUP*SYSTEM-BACKUP]       ~ Create Shell container
[SCRIPT|CREATE*NODE*API*WEB-SERVICE]             ~ Create Node.js container
[SCRIPT|RUN*ANALYZER*INPUT-DATA*OUTPUT-PATH]     ~ Run with parameters
[SCRIPT|SCHEDULE*BACKUP*DAILY*06:00]             ~ Schedule execution
[SCRIPT|MONITOR*API*HEALTH-CHECK]                ~ Monitor execution
```

---

## CONTAINER EXECUTION

### Python Container Example
```ucode
[SCRIPT|CREATE*PYTHON*DATA-PROCESSOR*DATA-ANALYSIS]

<PYTHON NAME="DATA-PROCESSOR" ROLE="CRYPT+">
    # uDOS Python Container v1.0.4.1
    import json, sys, os
    from pathlib import Path

    # Access uDOS variables through environment
    udos_data = os.environ.get('UDOS_DATA_PATH', '/sandbox/data')
    udos_role = os.environ.get('UDOS_CURRENT_ROLE', 'CRYPT')

    def process_data(input_file, output_file):
        """Process uDATA format files"""
        with open(input_file, 'r') as f:
            data = [json.loads(line) for line in f]

        # Process data using uDOS standards
        processed = []
        for record in data:
            if 'metadata' not in record:
                record['processed_by'] = f"uSCRIPT-{udos_role}"
                record['timestamp'] = "{{SYSTEM:TIMESTAMP}}"
                processed.append(record)

        # Write back in uDATA format
        with open(output_file, 'w') as f:
            for record in processed:
                f.write(json.dumps(record, separators=(',', ':')) + '\n')

    if __name__ == "__main__":
        input_path = sys.argv[1] if len(sys.argv) > 1 else f"{udos_data}/input.json"
        output_path = sys.argv[2] if len(sys.argv) > 2 else f"{udos_data}/processed.json"
        process_data(input_path, output_path)
        print(f"Data processed: {input_path} → {output_path}")
</PYTHON>

~ Execute the container
[SCRIPT|RUN*DATA-PROCESSOR*/sandbox/data/raw.json*/sandbox/data/clean.json]
```

### Shell Container Example
```ucode
[SCRIPT|CREATE*SHELL*SYSTEM-MAINTENANCE*AUTOMATION]

<SHELL NAME="SYSTEM-MAINTENANCE" ROLE="DRONE+">
    #!/bin/bash
    # uDOS Shell Container v1.0.4.1

    # Access uDOS environment
    UDOS_ROOT="${UDOS_ROOT:-/uDOS}"
    UDOS_ROLE="${UDOS_CURRENT_ROLE:-DRONE}"
    SANDBOX_PATH="${UDOS_ROOT}/sandbox"

    # uDOS standard logging
    log_info() {
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] [${UDOS_ROLE}] INFO: $1"
    }

    log_error() {
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] [${UDOS_ROLE}] ERROR: $1" >&2
    }

    # Main maintenance function
    perform_maintenance() {
        log_info "Starting system maintenance from uSCRIPT container"

        # Clean sandbox temporary files
        find "${SANDBOX_PATH}/temp" -type f -mtime +7 -delete 2>/dev/null || true
        log_info "Cleaned temporary files older than 7 days"

        # Archive old logs
        find "${SANDBOX_PATH}/logs" -name "*.log" -mtime +30 -exec gzip {} \; 2>/dev/null || true
        log_info "Compressed log files older than 30 days"

        # Update system templates with current role
        if [ -d "${UDOS_ROOT}/uMEMORY/templates" ]; then
            echo "LAST_MAINTENANCE={{SYSTEM:TIMESTAMP}}" > "${UDOS_ROOT}/uMEMORY/templates/maintenance.status"
            echo "MAINTENANCE_ROLE=${UDOS_ROLE}" >> "${UDOS_ROOT}/uMEMORY/templates/maintenance.status"
        fi

        log_info "System maintenance completed successfully"
    }

    # Execute maintenance
    perform_maintenance
</SHELL>

~ Schedule for daily execution
[SCRIPT|SCHEDULE*SYSTEM-MAINTENANCE*DAILY*03:00]
```

### Node.js Container Example
```ucode
[SCRIPT|CREATE*NODE*API-SERVICE*WEB-SERVICE]

<NODE NAME="API-SERVICE" ROLE="IMP+">
    // uDOS Node.js Container v1.0.4.1
    const express = require('express');
    const fs = require('fs').promises;
    const path = require('path');

    // uDOS environment integration
    const UDOS_ROOT = process.env.UDOS_ROOT || '/uDOS';
    const UDOS_ROLE = process.env.UDOS_CURRENT_ROLE || 'IMP';
    const SANDBOX_PATH = path.join(UDOS_ROOT, 'sandbox');

    const app = express();
    app.use(express.json());

    // uDOS standard logging
    const log = {
        info: (msg) => console.log(`[${new Date().toISOString()}] [${UDOS_ROLE}] INFO: ${msg}`),
        error: (msg) => console.error(`[${new Date().toISOString()}] [${UDOS_ROLE}] ERROR: ${msg}`)
    };

    // API endpoints for uDOS integration
    app.get('/api/status', (req, res) => {
        res.json({
            service: 'uDOS-API-Service',
            version: '1.0.4.1',
            role: UDOS_ROLE,
            timestamp: new Date().toISOString(),
            sandbox_path: SANDBOX_PATH
        });
    });

    app.post('/api/data/process', async (req, res) => {
        try {
            const { input_file, output_file } = req.body;
            const inputPath = path.join(SANDBOX_PATH, 'data', input_file);
            const outputPath = path.join(SANDBOX_PATH, 'data', output_file);

            // Read uDATA format
            const data = await fs.readFile(inputPath, 'utf8');
            const records = data.trim().split('\n').map(line => JSON.parse(line));

            // Process with uDOS metadata
            const processed = records.map(record => ({
                ...record,
                processed_by: `uSCRIPT-${UDOS_ROLE}`,
                processed_at: new Date().toISOString(),
                container: 'NODE-API-SERVICE'
            }));

            // Write back in uDATA format
            const output = processed.map(record => JSON.stringify(record)).join('\n') + '\n';
            await fs.writeFile(outputPath, output);

            log.info(`Processed ${records.length} records: ${input_file} → ${output_file}`);
            res.json({
                success: true,
                records_processed: records.length,
                output_file: output_file
            });

        } catch (error) {
            log.error(`Processing failed: ${error.message}`);
            res.status(500).json({ error: error.message });
        }
    });

    const PORT = process.env.PORT || 3000;
    app.listen(PORT, () => {
        log.info(`uDOS API Service running on port ${PORT}`);
    });
</NODE>

~ Start the service
[SCRIPT|RUN*API-SERVICE*BACKGROUND]
[SCRIPT|MONITOR*API-SERVICE*HEALTH-CHECK]
```

## ROLE MANAGEMENT

### [ROLE] <ACTION> {ROLE-NAME}
```ucode
~ Role operations (8-Role System)
[ROLE] <ACTIVATE> {GHOST}           ~ Activate Ghost role (Level 10)
[ROLE] <ACTIVATE> {TOMB}            ~ Activate Tomb role (Level 20)
[ROLE] <ACTIVATE> {CRYPT}           ~ Activate Crypt role (Level 30)
[ROLE] <ACTIVATE> {DRONE}           ~ Activate Drone role (Level 40)
[ROLE] <ACTIVATE> {KNIGHT}          ~ Activate Knight role (Level 50)
[ROLE] <ACTIVATE> {IMP}             ~ Activate Imp role (Level 60)
[ROLE] <ACTIVATE> {SORCERER}        ~ Activate Sorcerer role (Level 80)
[ROLE] <ACTIVATE> {WIZARD}          ~ Activate Wizard role (Level 100)
[ROLE] <ACTIVATE|FORCE> {ROLE}      ~ Force role activation
[ROLE] <CURRENT>                    ~ Get current role
[ROLE] <CURRENT|DETAILED>           ~ Get detailed role info
[ROLE] <SWITCH> {NEW-ROLE}          ~ Switch to new role
[ROLE] <SWITCH|PRESERVE> {NEW-ROLE} ~ Switch preserving session
[ROLE] <LIST>                       ~ List available roles
[ROLE] <LIST|ACTIVE>                ~ List only active roles
[ROLE] <PERMISSIONS> {ROLE}         ~ Check role permissions
[ROLE] <PERMISSIONS|FULL> {ROLE}    ~ Full permission details
[ROLE] <DEV-ACCESS> {WIZARD}        ~ Check development environment access
[ROLE] <DEV-MODE> {ENABLE}          ~ Enable development mode (Wizard only)
```

### Role Access Control Matrix
```ucode
CONTAINER TYPE   │ GHOST │ TOMB │ CRYPT │ DRONE │ KNIGHT │ IMP │ SORCERER │ WIZARD
═════════════════┼═══════┼══════┼═══════┼═══════┼════════┼═════┼══════════┼═══════
uCODE Commands   │   ✓   │  ✓   │   ✓   │   ✓   │   ✓    │  ✓  │    ✓     │   ✓
File Operations  │   R   │  R   │  R/W  │  R/W  │  R/W   │ R/W │   R/W    │  R/W
uSCRIPT Containers│   ✗   │  ✗   │   ✓   │   ✓   │   ✓    │  ✓  │    ✓     │   ✓
Python Containers│   ✗   │  ✗   │   ✓   │   ✓   │   ✓    │  ✓  │    ✓     │   ✓
Shell Containers │   ✗   │  ✗   │   ✗   │   ✓   │   ✓    │  ✓  │    ✓     │   ✓
Node.js Containers│   ✗   │  ✗   │   ✗   │   ✗   │   ✗    │  ✓  │    ✓     │   ✓
Scheduled Execution│   ✗   │  ✗   │   ✗   │   ✓   │   ✓    │  ✓  │    ✓     │   ✓
System Administration│   ✗   │  ✗   │   ✗   │   ✗   │   ✓    │  ✗  │    ✓     │   ✓
```

---

## TEMPLATE INTEGRATION

### uMEMORY Template System
Templates stored in `uMEMORY/system/templates/` provide variable substitution and configuration management.

### Template Variables
```ucode
{SYSTEM:TIMESTAMP}      ~ Current system timestamp
{SYSTEM:ROLE}           ~ Current user role
{SYSTEM:VERSION}        ~ uDOS version (1.0.4.1)
{USER:NAME}             ~ Current username
{USER:HOME}             ~ User home directory
{SANDBOX:PATH}          ~ Sandbox working directory
{MEMORY:PATH}           ~ uMEMORY storage path
{CONTAINER:NAME}        ~ Current container name
{CONTAINER:TYPE}        ~ Container language type
```

### Template Processing in Containers
```ucode
[TEMPLATE|PROCESS*INPUT-TEMPLATE*OUTPUT-FILE*VARIABLES]

~ Example template file: data-processor.template
<PYTHON NAME="{{CONTAINER:NAME}}" ROLE="{{SYSTEM:ROLE}}">
    # Generated by uDOS Template System v{{SYSTEM:VERSION}}
    # Created: {{SYSTEM:TIMESTAMP}}
    # Role: {{SYSTEM:ROLE}}

    import os, sys
    from pathlib import Path

    # uDOS environment
    UDOS_ROOT = "{{SANDBOX:PATH}}"
    USER_ROLE = "{{SYSTEM:ROLE}}"
    CONTAINER_NAME = "{{CONTAINER:NAME}}"

    def main():
        print(f"Container {CONTAINER_NAME} running as {USER_ROLE}")
        # Container logic here

    if __name__ == "__main__":
        main()
</PYTHON>

~ Process template with variables
[TEMPLATE|PROCESS*data-processor.template*my-script.py*NAME:DATA-ANALYZER]
```

### System Templates
```ucode
[TEMPLATE|SYSTEM*LIST]              ~ List system templates
[TEMPLATE|SYSTEM*CREATE*NAME*TYPE]  ~ Create system template
[TEMPLATE|USER*LIST]                ~ List user templates
[TEMPLATE|USER*CREATE*NAME*TYPE]    ~ Create user template
```

---

## MEMORY & DATA SYSTEMS

### [SANDBOX] <ACTION> {PARAMETER}
```ucode
~ Sandbox workspace operations
[SANDBOX] <INIT> {PROJECT-NAME}     ~ Initialize sandbox workspace
[SANDBOX] <INIT|WORKSPACE> {NAME}   ~ Initialize with workspace template
[SANDBOX] <STATUS>                  ~ Check sandbox status
[SANDBOX] <CLEAN>                   ~ Clean temporary sandbox data
[SANDBOX] <CLEAN|FORCE>             ~ Force clean all sandbox data
[SANDBOX] <BACKUP> {TARGET}         ~ Backup sandbox to uMEMORY
[SANDBOX] <BACKUP|AUTO> {SESSION}   ~ Auto-backup current session
[SANDBOX] <RESTORE> {BACKUP-NAME}   ~ Restore from uMEMORY backup
[SANDBOX] <LOG> {MESSAGE}           ~ Write to sandbox logs
[SANDBOX] <LOG|SESSION> {MESSAGE}   ~ Write session-specific log
```

### [MEM] <ACTION> {KEY} {VALUE}
```ucode
~ Permanent memory operations (uMEMORY)
[MEM] <STORE> {KEY} {VALUE}         ~ Store data permanently
[MEM] <STORE|ENCRYPT> {KEY} {VALUE} ~ Store encrypted data
[MEM] <RETRIEVE> {KEY}              ~ Retrieve permanent data
[MEM] <RETRIEVE|DECRYPT> {KEY}      ~ Retrieve and decrypt data
[MEM] <ARCHIVE> {SANDBOX-DATA}      ~ Archive sandbox data to uMEMORY
[MEM] <ARCHIVE|COMPRESS> {DATA}     ~ Compressed archive operation
[MEM] <LIST>                        ~ List stored items
[MEM] <LIST> {PATTERN}              ~ List with pattern
[MEM] <LIST|SORTED> {PATTERN}       ~ List sorted with pattern
[MEM] <CLEAR> {KEY}                 ~ Clear specific item
[MEM] <CLEAR> {PATTERN-WILDCARD}    ~ Clear with pattern
[MEM] <CLEAR|FORCE> {PATTERN}       ~ Force clear pattern
```

### [KNOW] <ACTION> {TOPIC} {CONTENT}
```ucode
~ Knowledge management
[KNOW] <SEARCH> {QUERY}         ~ Search knowledge base
[KNOW] <SEARCH|FUZZY> {QUERY}   ~ Fuzzy search
[KNOW] <ADD> {TOPIC} {CONTENT}  ~ Add knowledge entry
[KNOW] <ADD|REPLACE> {TOPIC} {CONTENT} ~ Add or replace entry
[KNOW] <UPDATE> {TOPIC} {CONTENT} ~ Update entry
[KNOW] <UPDATE|MERGE> {TOPIC} {CONTENT} ~ Merge update
[KNOW] <CATEGORIES>             ~ List categories
[KNOW] <CATEGORIES|TREE>        ~ List as tree structure
```

### [FILE] <ACTION> {PATH} {CONTENT}
```ucode
~ File operations
[FILE] <READ> {FILE-PATH}       ~ Read file
[FILE] <READ|BINARY> {FILE-PATH} ~ Read binary file
[FILE] <WRITE> {FILE-PATH} {CONTENT} ~ Write file
[FILE] <WRITE|APPEND> {FILE-PATH} {CONTENT} ~ Append to file
[FILE] <EXISTS> {FILE-PATH}     ~ Check if file exists
[FILE] <LIST> {DIRECTORY}       ~ List directory
[FILE] <LIST|RECURSIVE> {DIRECTORY} ~ List recursively
```

## DATA CONTROL

### [GET] <SOURCE> {URL} {PARAMETERS}
```ucode
~ HTTP GET operations
[GET] <REQUEST> {URL}           ~ Simple GET request
[GET] <REQUEST> {URL} {HEADERS} ~ GET with headers
[GET] <REQUEST|ASYNC> {URL}     ~ Async GET request
[GET] <API> {ENDPOINT} {AUTH-TOKEN} ~ API GET request
[GET] <API|RETRY> {ENDPOINT} {AUTH-TOKEN} ~ API GET with retry
[GET] <FILE> {URL} {SAVE-PATH}  ~ Download file
[GET] <FILE|RESUME> {URL} {SAVE-PATH} ~ Resume download
[GET] <JSON> {API-URL} {PARAMS} ~ GET JSON data
[GET] <JSON|VALIDATE> {API-URL} {PARAMS} ~ GET and validate JSON
```

### [POST] <TARGET> {URL} {DATA}
```ucode
~ HTTP POST operations
[POST] <REQUEST> {URL} {DATA}   ~ Simple POST request
[POST] <REQUEST|SECURE> {URL} {DATA} ~ Secure POST request
[POST] <JSON> {API-URL} {JSON-DATA} ~ POST JSON data
[POST] <JSON|COMPRESS> {API-URL} {JSON-DATA} ~ Compressed JSON POST
[POST] <FORM> {URL} {FORM-DATA} ~ POST form data
[POST] <FORM|MULTI-PART> {URL} {FORM-DATA} ~ Multipart form POST
[POST] <FILE> {URL} {FILE-PATH} ~ Upload file
[POST] <FILE|CHUNKED> {URL} {FILE-PATH} ~ Chunked file upload
[POST] <API> {ENDPOINT} {DATA} {AUTH-TOKEN} ~ API POST
[POST] <API|CALLBACK> {ENDPOINT} {DATA} {AUTH-TOKEN} ~ API POST with callback
```

### [DATA] <ACTION> {SOURCE} {TARGET}
```ucode
~ Data transformation and transfer
[DATA] <PARSE> {JSON-STRING}    ~ Parse JSON data
[DATA] <PARSE|STRICT> {JSON-STRING} ~ Strict JSON parsing
[DATA] <CONVERT> {XML} {JSON}   ~ Convert between formats
[DATA] <CONVERT|PRESERVE> {XML} {JSON} ~ Convert preserving structure
[DATA] <VALIDATE> {DATA} {SCHEMA} ~ Validate data structure
[DATA] <VALIDATE|REPORT> {DATA} {SCHEMA} ~ Validate with error report
[DATA] <MERGE> {DATA-1} {DATA-2} ~ Merge data objects
[DATA] <MERGE|DEEP> {DATA-1} {DATA-2} ~ Deep merge data objects
[DATA] <FILTER> {DATA} {CRITERIA} ~ Filter data
[DATA] <FILTER|REGEX> {DATA} {CRITERIA} ~ Filter using regex
```

## uGRID DISPLAY SYSTEM

### [GRID] <ACTION> {PARAMETER}
```ucode
~ uGRID display operations
[GRID] <INIT> {WIDTH/HEIGHT}        ~ Initialize grid
[GRID] <INIT|4X> {WIDTH/HEIGHT}     ~ Initialize with 4× resolution
[GRID] <SIZE> {WIDTH/HEIGHT}        ~ Set grid dimensions
[GRID] <SIZE|AUTO>                  ~ Auto-detect optimal size
[GRID] <TILE> {CREATE*X/Y*CONTENT}  ~ Create tile at position
[GRID] <TILE|UPDATE*X/Y*CONTENT>    ~ Update existing tile
[GRID] <WIDGET> {CREATE*NAME*X/Y*W/H} ~ Create widget
[GRID] <WIDGET|MOVE*NAME*X/Y}       ~ Move widget position
[GRID] <SCREEN> {SWITCH*NAME}       ~ Switch screen context
[GRID] <SCREEN|CREATE*NAME*LAYOUT}  ~ Create new screen
[GRID] <RENDER>                     ~ Force render update
[GRID] <RENDER|CLEAN}               ~ Clean rendering
[GRID] <CLEAR>                      ~ Clear entire grid
[GRID] <CLEAR|REGION*X/Y*W/H}       ~ Clear specific region
```

### [UMAP] <ACTION> {COORDINATE}
```ucode
~ uMAP coordinate operations
[UMAP] <GOTO> {X/Y}                 ~ Navigate to coordinates
[UMAP] <GOTO|SMOOTH> {X/Y}          ~ Smooth navigation
[UMAP] <REGION> {DEFINE*NAME*X/Y*W/H} ~ Define region
[UMAP] <REGION|SELECT*NAME}         ~ Select defined region
[UMAP] <ZOOM> {LEVEL}               ~ Set zoom level
[UMAP] <ZOOM|FIT*CONTENT}           ~ Zoom to fit content
[UMAP] <PAN> {DIRECTION*DISTANCE}   ~ Pan view
[UMAP] <PAN|CENTER}                 ~ Center view
[UMAP] <OVERLAY> {ENABLE*4X}        ~ Enable 4× overlay
[UMAP] <OVERLAY|DISABLE}            ~ Disable overlay
```

### [WIDGET] <ACTION> {WIDGET-NAME}
```ucode
~ Widget management operations
[WIDGET] <CREATE> {NAME*TYPE*X/Y*W/H} ~ Create new widget
[WIDGET] <CREATE|TEMPLATE*NAME*TYPE}  ~ Create from template
[WIDGET] <UPDATE> {NAME*PROPERTY*VALUE} ~ Update widget property
[WIDGET] <UPDATE|BULK*NAME*PROPERTIES}  ~ Bulk property update
[WIDGET] <MOVE> {NAME*X/Y}            ~ Move widget
[WIDGET] <RESIZE> {NAME*W/H}          ~ Resize widget
[WIDGET] <DELETE> {NAME}              ~ Delete widget
[WIDGET] <LIST>                       ~ List all widgets
[WIDGET] <LIST|ACTIVE}                ~ List active widgets
[WIDGET] <REFRESH> {NAME}             ~ Refresh widget content
[WIDGET] <REFRESH|ALL}                ~ Refresh all widgets
```

## WORKFLOW SYSTEM

### [WORKFLOW] <ACTION> {PARAMETER}
```ucode
~ Workflow management
[WORKFLOW] <MODE>               ~ Check current mode
[WORKFLOW] <MODE|VERBOSE>       ~ Detailed mode info
[WORKFLOW] <ASSIST> {ENTER}     ~ Enter assist mode
[WORKFLOW] <ASSIST> {EXIT}      ~ Exit assist mode
[WORKFLOW] <ASSIST|FORCE> {ENTER} ~ Force enter assist mode
[WORKFLOW] <ASSIST> {ANALYZE}   ~ Analyze context
[WORKFLOW] <ASSIST|DEEP> {ANALYZE} ~ Deep context analysis
[WORKFLOW] <BRIEFINGS> {LIST}   ~ List briefings
[WORKFLOW] <BRIEFINGS|RECENT> {LIST} ~ List recent briefings
[WORKFLOW] <BRIEFINGS> {UPDATE} ~ Update briefings
[WORKFLOW] <BRIEFINGS|SYNC> {UPDATE} ~ Sync update briefings
[WORKFLOW] <ROADMAPS> {LIST}    ~ List roadmaps
[WORKFLOW] <ROADMAPS> {ACTIVE}  ~ Active roadmaps
[WORKFLOW] <ROADMAPS|PRIORITY> {ACTIVE} ~ Priority roadmaps
[WORKFLOW] <CLEANUP> {ALL}      ~ Run cleanup
[WORKFLOW] <CLEANUP|FORCE> {ALL} ~ Force cleanup all
```

### [uCORE] <COMMAND> {OPERATION}
```ucode
~ uCORE operations
[uCORE] <COMMAND> {TRASH-LIST}     ~ List trashed items
[uCORE] <COMMAND|DETAIL> {TRASH-LIST} ~ Detailed trash list
[uCORE] <COMMAND> {TRASH-EMPTY}    ~ Empty trash
[uCORE] <COMMAND|SECURE> {TRASH-EMPTY} ~ Secure empty trash
[uCORE] <COMMAND> {BACKUP-CREATE}  ~ Create backup
[uCORE] <COMMAND|COMPRESS> {BACKUP-CREATE} ~ Compressed backup
[uCORE] <SESSION> {SAVE}           ~ Save session
[uCORE] <SESSION|AUTO> {SAVE}      ~ Auto-save session
[uCORE] <SESSION> {UNDO}           ~ Undo operation
[uCORE] <SESSION|ROLL-BACK> {UNDO}  ~ Rollback session
```

## ASSIST MODE MANAGEMENT

### OK / END Commands
```bash
~ Direct assist mode control
OK                          ~ Enter Assist Mode (OI) or continue in assist mode
END                         ~ Exit Assist Mode back to Command Mode (IO)
```

**Behavior:**
- **Not in Assist Mode + OK**: Enters Assist Mode (OI) - AI analyzes and recommends
- **In Assist Mode + OK**: Continue with AI recommendations
- **In Assist Mode + END**: Exit to Command Mode (IO) - User-driven interface
- **Not in Assist Mode + END**: No effect (already in Command Mode)

### Assist Commands
```ucode
~ uCODE assist mode integration
[ASSIST] <ENTER>            ~ Enter assist mode
[ASSIST] <ENTER|FORCE>      ~ Force enter assist mode
[ASSIST] <EXIT>             ~ Exit assist mode
[ASSIST] <CONTINUE>         ~ Continue in assist mode
[ASSIST] <ANALYZE>          ~ Analyze current context
[ASSIST] <ANALYZE|DEEP>     ~ Deep context analysis
```

## SETUP COMMANDS

### SETUP <ACTION> {PARAMETER}
```bash
~ Direct setup management commands
SETUP role                  ~ Setup environment for current role
SETUP test                  ~ Setup testing environment in sandbox (NOT dev)
SETUP check                 ~ Check setup status for current role
```

**Features:**
- **Testing in Sandbox Only**: All testing scripts created in `sandbox/{ROLE}/testing/`
- **No Dev Mode Testing**: Testing in everyday mode uses sandbox environment
- **Role-specific Configuration**: Each role gets its own testing environment
- **Production Safety**: Testing isolated from development environment

### Setup Commands
```ucode
~ uCODE setup operations
[SETUP] <ROLE>              ~ Setup role environment
[SETUP] <ROLE|FORCE>        ~ Force setup role environment
[SETUP] <TEST>              ~ Setup testing environment
[SETUP] <TEST|SANDBOX>      ~ Setup sandbox testing environment
[SETUP] <CHECK>             ~ Check setup status
[SETUP] <CHECK|DETAILED>    ~ Detailed setup validation
```

## SCRIPT EXECUTION

### [SCRIPT] <ACTION> {SCRIPT-NAME}
```ucode
~ Script operations
[SCRIPT] <RUN> {SCRIPT-NAME}        ~ Execute script
[SCRIPT] <RUN|DEBUG> {SCRIPT-NAME}  ~ Execute with debugging
[SCRIPT] <EXECUTE> {COMMAND}        ~ Execute command
[SCRIPT] <EXECUTE|SILENT> {COMMAND} ~ Silent execution
[SCRIPT] <SCHEDULE> {SCRIPT} {TIME} ~ Schedule execution
[SCRIPT] <SCHEDULE|REPEAT> {SCRIPT} {TIME} ~ Repeating schedule
[SCRIPT] <LIST>                     ~ List available scripts
[SCRIPT] <LIST|FILTERED> {PATTERN}  ~ List filtered scripts
[SCRIPT] <VALIDATE> {SCRIPT-NAME}   ~ Validate script syntax
[SCRIPT] <VALIDATE|STRICT> {SCRIPT-NAME} ~ Strict validation
```

### DEF {VARIABLE} = {VALUE}
```ucode
~ Variable operations - CAPITALS-DASH-1234567890 only
DEF {CURRENT-ROLE} = [ROLE] <CURRENT>
DEF {SYSTEM-STATUS} = [SYS] <STATUS>
DEF {USER-DATA} = [MEM] <RETRIEVE> {USER-DATA}
DEF {CONFIG-DATA} = [FILE] <READ> {/CONFIG/SYSTEM.CONF}
DEF {API-RESPONSE} = [GET] <JSON> {API-URL} {PARAMS}
```

### [ENV] <ACTION> {VARIABLE} {VALUE}
```ucode
~ Environment variables
DEF {USER-HOME} = [ENV] <VARIABLE> {HOME}
DEF {DOS-PATH} = [ENV] <VARIABLE> {UDOS-PATH}
[ENV] <SET> {CUSTOM-VAR} {CUSTOM-VALUE}
```

### <FUNCTION> {FUNCTION-NAME}
```ucode
~ Function definitions - use <FUNCTION> instead of SUB
<FUNCTION> {DAILY-MAINTENANCE}
    [LOG] <INFO> {Starting maintenance...}
    [ROLE] <ACTIVATE> {DRONE}
    [SYS] <OPTIMIZE> {CLEANUP}
<END-FUNCTION>

<FUNCTION> {SETUP-PROJECT} {PROJECT-NAME}
    DEF {PROJECT-PATH} = /PROJECTS/ + {PROJECT-NAME}
    [FILE] <WRITE> {PROJECT-PATH} {README-CONTENT}
<END-FUNCTION>
```

## UNDO/REDO OPERATIONS

### Direct Undo/Redo Commands
```bash
~ Session-based undo/redo system
UNDO                        ~ Undo last operation
REDO                        ~ Redo last undone operation
```

### Undo/Redo Support
```ucode
~ uCODE undo/redo operations
[SESSION] <UNDO>            ~ Undo last operation
[SESSION] <UNDO|FORCE>      ~ Force undo operation
[SESSION] <REDO>            ~ Redo last undone operation
[SESSION] <REDO|CONFIRM>    ~ Redo with confirmation
[SESSION] <HISTORY>         ~ Show operation history
[SESSION] <HISTORY|DETAILED> ~ Detailed operation history
```

**Supported Operations:**
- ✅ **TRASH operations**: Undo move to trash, undo restore from trash
- ✅ **ROLE operations**: Undo role switching (restores previous role)
- ✅ **BACKUP operations**: Undo backup creation (removes newest backup)
- ✅ **Memory operations**: Undo store/clear operations
- ✅ **File operations**: Undo write/delete operations

**Limitations:**
- ❌ **TRASH empty**: Cannot undo permanent deletion
- ❌ **Non-undoable commands**: System queries (list, check, status)
- ❌ **Session-based**: Undo/redo only available within current session

### Session Management
```ucode
~ Session control
[SESSION] <SAVE>            ~ Save current session state
[SESSION] <SAVE|AUTO>       ~ Enable auto-save mode
[SESSION] <RESTORE>         ~ Restore saved session
[SESSION] <RESTORE|BACKUP>  ~ Restore from backup session
[SESSION] <CLEAR>           ~ Clear session history
[SESSION] <CLEAR|FORCE>     ~ Force clear all session data
```

## ERROR HANDLING

### [TRY] ... [CATCH] ... [END]
```ucode
~ Error handling
[TRY]
    [ROLE] <ACTIVATE> {INVALID-ROLE}
    [SYS] <STATUS>
[CATCH] {ERROR}
    [LOG] <ERROR|TIMESTAMP> {Operation failed: } + {ERROR}
    [ROLE] <ACTIVATE|FORCE> {GHOST}  ~ Fallback
[END]
```

### [ERROR] <ACTION> {MESSAGE} {SEVERITY}
```ucode
~ Error management
[ERROR] <LOG> {MESSAGE} {WARNING}   ~ Log error
[ERROR] <LOG|STACK> {MESSAGE} {WARNING} ~ Log with stack trace
[ERROR] <LOG> {MESSAGE} {CRITICAL}  ~ Critical error
[ERROR] <LOG|ALERT> {MESSAGE} {CRITICAL} ~ Critical with alert
[ERROR] <REPORT> {ERROR-DETAILS}    ~ Generate report
[ERROR] <REPORT|EMAIL> {ERROR-DETAILS} ~ Email error report
[ERROR] <CHECK> {OPERATION}         ~ Check for errors
[ERROR] <CHECK|DEEP> {OPERATION}    ~ Deep error check
[ERROR] <RETRY> {OPERATION} {COUNT} ~ Retry operation
[ERROR] <RETRY|BACK-OFF> {OPERATION} {COUNT} ~ Retry with backoff
```

### Flow Control
```ucode
~ Conditional operations
IF [SYS] <STATUS> = ONLINE THEN
    [LOG] <INFO> {System online}
ELSE
    [LOG] <WARNING> {System offline}
END IF

~ Loop operations
FOR EACH {ROLE} IN [ROLE] <LIST>
    [LOG] <INFO> {Role: } + {ROLE}
NEXT {ROLE}

WHILE [SYS] <STATUS> <> OPTIMAL
    [SYS] <OPTIMIZE> {INCREMENTAL}
    [SYS] <Sleep> {5000}
WEND
```

## EXAMPLES

### Daily Maintenance
```ucode
~ Streamlined daily maintenance with pipe options
<FUNCTION> {DAILY-MAINTENANCE}
    [TRY]
        [LOG] <INFO|TIMESTAMP> {Starting maintenance...}

        [ROLE] <ACTIVATE|FORCE> {DRONE}
        [SYS] <OPTIMIZE|DEEP> {CLEANUP}
        [WORKFLOW] <CLEANUP|FORCE> {ALL}

        DEF {TIMESTAMP} = [SYS] <TIME|UTC>
        [MEM] <STORE|ENCRYPT> {LAST-MAINTENANCE} {TIMESTAMP}

        [LOG] <INFO|TIMESTAMP> {Maintenance complete}
    [CATCH] {ERROR}
        [ERROR] <LOG|STACK> {Maintenance failed: } + {ERROR} {ERROR}
    [END]
<END-FUNCTION>
```

### Project Setup with Data Control
```ucode
~ Streamlined project setup with API integration and pipe options
<FUNCTION> {SETUP-PROJECT} {PROJECT-NAME}
    [TRY]
        [ROLE] <ACTIVATE|PRESERVE> {IMP}
        [WORKFLOW] <ASSIST|FORCE> {ENTER}

        DEF {PROJECT-PATH} = /PROJECTS/ + {PROJECT-NAME}
        [FILE] <WRITE|CREATE> {PROJECT-PATH} + {/README.MD} {# } + {PROJECT-NAME}

        ~ Get project template from API with retry
        DEF {TEMPLATE-DATA} = [GET] <JSON|RETRY> {API-TEMPLATES} {PROJECT-TYPE}
        [FILE] <WRITE|BACKUP> {PROJECT-PATH} + {/CONFIG.JSON} {TEMPLATE-DATA}

        ~ Post project creation to tracking system with compression
        DEF {PROJECT-INFO} = {NAME: PROJECT-NAME, CREATED: TIMESTAMP}
        [POST] <JSON|COMPRESS> {API-PROJECTS} {PROJECT-INFO}

        [MEM] <STORE|ENCRYPT> {CURRENT-PROJECT} {PROJECT-NAME}
        [KNOW] <ADD|INDEX> {PROJECT-NAME} {Project created}

        [LOG] <INFO|DETAILED> {Project } + {PROJECT-NAME} + { created}
    [CATCH] {ERROR}
        [ERROR] <LOG|EMAIL> {Project setup failed: } + {ERROR} {ERROR}
    [END]
<END-FUNCTION>
### Workflow Automation with Data Sync
```ucode
~ Workflow automation with data synchronization and pipe options
<FUNCTION> {WORKFLOW-AUTOMATION}
    [TRY]
        [WORKFLOW] <ASSIST|FORCE> {ENTER}
        [WORKFLOW] <BRIEFINGS|SYNC> {UPDATE}

        ~ Sync workflow data with remote service using compression
        DEF {LOCAL-DATA} = [MEM] <RETRIEVE|DECRYPT> {WORKFLOW-STATE}
        [POST] <JSON|COMPRESS> {API-WORKFLOW-SYNC} {LOCAL-DATA}

        ~ Get updated roadmaps from API with retry
        DEF {REMOTE-ROADMAPS} = [GET] <JSON|RETRY> {API-ROADMAPS} {ACTIVE}
        [MEM] <STORE|ENCRYPT> {ACTIVE-ROADMAPS} {REMOTE-ROADMAPS}

        [LOG] <INFO|DETAILED> {Active roadmaps: } + {REMOTE-ROADMAPS}

        [uCORE] <SESSION|AUTO> {SAVE}
        [WORKFLOW] <CLEANUP|FORCE> {ALL}

        [MEM] <STORE|ENCRYPT> {WORKFLOW-STATUS} {COMPLETED}
        [WORKFLOW] <ASSIST> {EXIT}

        [LOG] <INFO|TIMESTAMP> {Workflow automation complete}
    [CATCH] {ERROR}
        [ERROR] <LOG|ALERT> {Workflow failed: } + {ERROR} {ERROR}
        [WORKFLOW] <ASSIST> {EXIT}
    [END]
<END-FUNCTION>
```

### API Data Processing
```ucode
~ Comprehensive data control operations with pipe options
<FUNCTION> {PROCESS-API-DATA} {ENDPOINT} {AUTH-TOKEN}
    [TRY]
        ~ GET data from API with retry mechanism
        DEF {RAW-DATA} = [GET] <API|RETRY> {ENDPOINT} {AUTH-TOKEN}

        ~ Parse and validate the response with strict validation
        DEF {PARSED-DATA} = [DATA] <PARSE|STRICT> {RAW-DATA}
        DEF {VALID-DATA} = [DATA] <VALIDATE|REPORT> {PARSED-DATA} {SCHEMA}

        ~ Filter and transform data with regex filtering
        DEF {FILTERED-DATA} = [DATA] <FILTER|REGEX> {VALID-DATA} {CRITERIA}
        DEF {PROCESSED-DATA} = [DATA] <CONVERT|PRESERVE> {FILTERED-DATA} {OUTPUT-FORMAT}

        ~ Store processed data with encryption
        [MEM] <STORE|ENCRYPT> {API-CACHE} {PROCESSED-DATA}
        [FILE] <WRITE|BACKUP> {/DATA/PROCESSED.JSON} {PROCESSED-DATA}

        ~ Send confirmation back to API with secure transmission
        DEF {CONFIRMATION} = {STATUS: SUCCESS, COUNT: DATA-COUNT}
        [POST] <JSON|SECURE> {ENDPOINT} + {/CONFIRM} {CONFIRMATION}

        [LOG] <INFO|DETAILED> {Data processing complete}

    [CATCH] {ERROR}
        [ERROR] <LOG|STACK> {API processing failed: } + {ERROR} {CRITICAL}
        [ERROR] <REPORT|EMAIL> {ERROR-DETAILS}
    [END]
<END-FUNCTION>
```

### System Administration
```ucode
~ Example using core commands with assist mode
<FUNCTION> {SYSTEM-ADMINISTRATION}
    [TRY]
        ~ Enter assist mode for complex operations
        [ASSIST] <ENTER|FORCE>

        ~ Setup role environment
        [SETUP] <ROLE|FORCE> {SORCERER}

        ~ Perform system cleanup with backup
        [SESSION] <SAVE|AUTO>
        BACKUP create
        [uCORE] <COMMAND|SECURE> {TRASH-EMPTY}

        ~ Role management with undo support
        [ROLE] <SWITCH|PRESERVE> {DRONE}
        [ROLE] <ACTIVATE|FORCE> {DRONE}

        ~ Verify operations with detailed logging
        [LOG] <INFO|TIMESTAMP> {Administration complete}
        [SESSION] <HISTORY|DETAILED>

        ~ Exit assist mode
        [ASSIST] <EXIT>

    [CATCH] {ERROR}
        ~ Undo operations on error
        [SESSION] <UNDO|FORCE>
        BACKUP restore {LATEST}
        [ERROR] <LOG|ALERT> {Administration failed: } + {ERROR}
        [ASSIST] <EXIT>
    [END]
<END-FUNCTION>
```

### uGRID Dashboard Creation
```ucode
~ Complete uGRID dashboard setup with widgets and 8-role system
<FUNCTION> {CREATE-DASHBOARD} {GRID-SIZE} {USER-ROLE}
    [TRY]
        ~ Initialize grid system
        [GRID] <INIT|4X> {GRID-SIZE}
        [GRID] <SCREEN|CREATE*DASHBOARD*DEFAULT-LAYOUT}

        ~ Role-based dashboard configuration
        IF {USER-ROLE} = WIZARD THEN
            ~ Wizard dashboard: Full system control
            [WIDGET] <CREATE> {SYSTEM-STATUS*STATUS*0/0*40/8}
            [WIDGET] <CREATE> {ROLE-MANAGER*ROLE*40/0*40/8}
            [WIDGET] <CREATE> {PERFORMANCE*CHART*0/8*80/15}
            [WIDGET] <CREATE> {LOG-VIEWER*LOG*0/23*80/7}
        ELSE IF {USER-ROLE} = SORCERER THEN
            ~ Sorcerer dashboard: Development focus
            [WIDGET] <CREATE> {CODE-STATUS*STATUS*0/0*50/6}
            [WIDGET] <CREATE> {BUILD-OUTPUT*LOG*50/0*30/6}
            [WIDGET] <CREATE> {GRID-EDITOR*EDITOR*0/6*80/20}
            [WIDGET] <CREATE> {DEBUG-PANEL*DEBUG*0/26*80/4}
        ELSE IF {USER-ROLE} = IMP THEN
            ~ Imp dashboard: Automation tools
            [WIDGET] <CREATE> {SCRIPT-STATUS*STATUS*0/0*60/5}
            [WIDGET] <CREATE> {TASK-QUEUE*QUEUE*60/0*20/5}
            [WIDGET] <CREATE> {AUTOMATION*CONTROL*0/5*80/20}
            [WIDGET] <CREATE> {RESULTS*LOG*0/25*80/5}
        ELSE
            ~ Standard dashboard for other roles
            [WIDGET] <CREATE> {USER-STATUS*STATUS*0/0*80/3}
            [WIDGET] <CREATE> {MAIN-CONTENT*CONTENT*0/3*80/24}
            [WIDGET] <CREATE> {FOOTER*INFO*0/27*80/3}
        END IF

        ~ Setup grid regions and navigation
        [UMAP] <REGION> {DEFINE*HEADER*0/0*80/3}
        [UMAP] <REGION> {DEFINE*MAIN*0/3*80/24}
        [UMAP] <REGION> {DEFINE*FOOTER*0/27*80/3}

        ~ Enable optimizations
        [GRID] <RENDER|OPTIMIZE}
        [UMAP] <OVERLAY> {ENABLE*4X}

        [LOG] <INFO|TIMESTAMP> {Dashboard created for } + {USER-ROLE}
        [LOG] <INFO|DETAILED> {Grid: } + {GRID-SIZE} + { | Widgets: } + {WIDGET-COUNT}

    [CATCH] {ERROR}
        [ERROR] <LOG|STACK> {Dashboard creation failed: } + {ERROR} {CRITICAL}
        [GRID] <CLEAR>
    [END]
<END-FUNCTION>
```

### Multi-Role Security Operation
```ucode
~ Complex operation demonstrating 8-role hierarchy and security
<FUNCTION> {SECURE-SYSTEM-OPERATION} {OPERATION-TYPE}
    [TRY]
        ~ Check current role and escalate if needed
        DEF {CURRENT-ROLE} = [ROLE] <CURRENT>
        DEF {ACCESS-LEVEL} = [ROLE] <PERMISSIONS> {CURRENT-ROLE}

        ~ Role-based operation handling
        IF {ACCESS-LEVEL} >= 80 THEN
            ~ Wizard/Sorcerer: Full access
            [LOG] <INFO|TIMESTAMP> {High-level access granted: } + {CURRENT-ROLE}
            [ROLE] <ACTIVATE|PRESERVE> {WIZARD}

            ~ Execute privileged operations
            [SYS] <OPTIMIZE|FORCE> {DEEP-CLEAN}
            [WORKFLOW] <CLEANUP|FORCE> {ALL}
            [GRID] <INIT|4X> {160/60}  ~ High-resolution mode

        ELSE IF {ACCESS-LEVEL} >= 50 THEN
            ~ Knight/Imp: Limited administrative access
            [LOG] <INFO|TIMESTAMP> {Mid-level access: } + {CURRENT-ROLE}
            [ROLE] <ACTIVATE|PRESERVE> {IMP}

            ~ Execute automation operations
            [SYS] <OPTIMIZE> {STANDARD}
            [WORKFLOW] <CLEANUP> {SELECTIVE}
            [GRID] <INIT> {80/30}  ~ Standard resolution

        ELSE IF {ACCESS-LEVEL} >= 30 THEN
            ~ Drone/Crypt: Standard operations
            [LOG] <INFO|TIMESTAMP> {Standard access: } + {CURRENT-ROLE}
            [ROLE] <ACTIVATE|PRESERVE> {DRONE}

            ~ Execute basic operations
            [SYS] <STATUS|BRIEF>
            [WORKFLOW] <BRIEFINGS> {UPDATE}
            [GRID] <SIZE|AUTO>

        ELSE
            ~ Tomb/Ghost: Read-only access
            [LOG] <WARNING|TIMESTAMP> {Limited access: } + {CURRENT-ROLE}
            [ROLE] <ACTIVATE|PRESERVE> {GHOST}

            ~ Read-only operations
            [SYS] <STATUS>
            [WORKFLOW] <BRIEFINGS> {LIST}
            [GRID] <SIZE> {40/16}  ~ Minimal grid
        END IF

        ~ Store operation log with role context
        DEF {OPERATION-LOG} = {
            TYPE: OPERATION-TYPE,
            ROLE: CURRENT-ROLE,
            ACCESS: ACCESS-LEVEL,
            TIMESTAMP: [SYS] <TIME|UTC>,
            GRID: [GRID] <SIZE>
        }
        [MEM] <STORE|ENCRYPT> {SECURITY-LOG} {OPERATION-LOG}

        [LOG] <INFO|DETAILED> {Operation completed: } + {OPERATION-TYPE}

    [CATCH] {ERROR}
        [ERROR] <LOG|ALERT> {Security operation failed: } + {ERROR} {CRITICAL}
        [ROLE] <ACTIVATE> {GHOST}  ~ Fallback to minimal access
    [END]
<END-FUNCTION>
```

### uDATA Processing with uGRID Visualization
```ucode
~ Advanced data processing with grid-based visualization
<FUNCTION> {PROCESS-UDATA-VISUALIZATION} {DATA-SOURCE} {CHART-TYPE}
    [TRY]
        ~ Role check for data processing
        DEF {USER-ROLE} = [ROLE] <CURRENT>
        IF {USER-ROLE} NOT IN [SORCERER, IMP, KNIGHT] THEN
            [ERROR] <LOG|ALERT> {Insufficient role for data processing}
            RETURN
        END IF

        ~ Initialize grid for visualization
        [GRID] <INIT|4X> {120/48}
        [GRID] <SCREEN|CREATE*DATA-VIZ*CHART-LAYOUT}

        ~ Fetch and process data
        DEF {RAW-DATA} = [GET] <JSON|RETRY> {DATA-SOURCE} {AUTH-TOKEN}
        DEF {PARSED-DATA} = [DATA] <PARSE|STRICT> {RAW-DATA}
        DEF {UDATA-FORMATTED} = [DATA] <CONVERT|PRESERVE> {PARSED-DATA} {UDATA}

        ~ Create visualization widgets based on chart type
        IF {CHART-TYPE} = BAR THEN
            [WIDGET] <CREATE> {BAR-CHART*CHART*10/5*100/30}
            [WIDGET] <UPDATE> {BAR-CHART*DATA*UDATA-FORMATTED}
        ELSE IF {CHART-TYPE} = LINE THEN
            [WIDGET] <CREATE> {LINE-CHART*CHART*10/5*100/30}
            [WIDGET] <UPDATE> {LINE-CHART*DATA*UDATA-FORMATTED}
        ELSE IF {CHART-TYPE} = GRID THEN
            [WIDGET] <CREATE> {DATA-GRID*TABLE*10/5*100/35}
            [WIDGET] <UPDATE> {DATA-GRID*DATA*UDATA-FORMATTED}
        END IF

        ~ Add control widgets
        [WIDGET] <CREATE> {DATA-CONTROLS*CONTROL*0/0*120/4}
        [WIDGET] <CREATE> {LEGEND*INFO*0/40*120/8}

        ~ Setup navigation regions
        [UMAP] <REGION> {DEFINE*CONTROLS*0/0*120/4}
        [UMAP] <REGION> {DEFINE*CHART*10/5*100/30}
        [UMAP] <REGION> {DEFINE*LEGEND*0/40*120/8}

        ~ Store processed data
        [MEM] <STORE|ENCRYPT> {CHART-DATA} {UDATA-FORMATTED}
        [FILE] <WRITE|BACKUP> {/DATA/CHART-} + {CHART-TYPE} + {.JSON} {UDATA-FORMATTED}

        [LOG] <INFO|DETAILED> {Data visualization created: } + {CHART-TYPE}
        [LOG] <INFO|TIMESTAMP> {Grid: 120x48 | 4× Mode | Role: } + {USER-ROLE}

    [CATCH] {ERROR}
        [ERROR] <LOG|STACK> {Data visualization failed: } + {ERROR} {ERROR}
        [GRID] <CLEAR>
    [END]
<END-FUNCTION>
```

## BEST PRACTICES

## BEST PRACTICES

### 📝 **Naming Conventions**
```ucode
~ Variables: Use {CAPS-DASH-NUMBERS} only
{USER-DATA}      {PROJECT-NAME}      {API-TOKEN}
{GRID-WIDTH}     {WIDGET-COUNT}      {ROLE-LEVEL}
{SYSTEM-STATUS}  {UHEX-FILENAME}     {CHART-TYPE}

~ Functions: Use <FUNCTION> {FUNCTION-NAME} ... <END-FUNCTION>
<FUNCTION> {DAILY-MAINTENANCE}
<FUNCTION> {SETUP-PROJECT}
<FUNCTION> {CREATE-DASHBOARD}

~ Commands: [SHORTCODE] <ACTION> {PARAMETER}
[ROLE] <ACTIVATE> {WIZARD}
[GRID] <INIT|4X> {160/60}
[WIDGET] <CREATE> {STATUS*CHART*0/0*40/20}
```

### 🎨 **uGRID Display Best Practices**
```ucode
~ Grid Initialization
[GRID] <INIT|4X> {WIDTH/HEIGHT}     ~ Use 4× for high-detail work
[GRID] <SIZE|AUTO>                  ~ Auto-detect for device optimization
[UMAP] <OVERLAY> {ENABLE*4X}        ~ Enable overlay for detailed graphics

~ Widget Management
[WIDGET] <CREATE|TEMPLATE*NAME*TYPE} ~ Use templates for consistency
[WIDGET] <REFRESH|ALL}              ~ Refresh all widgets periodically
[GRID] <RENDER|CLEAN}            ~ Clean rendering performance

~ Screen Organization
[GRID] <SCREEN|CREATE*NAME*LAYOUT}  ~ Create logical screen contexts
[UMAP] <REGION> {DEFINE*NAME*X/Y*W/H} ~ Define regions for navigation
[UMAP] <ZOOM|FIT*CONTENT}           ~ Auto-fit content to viewport
```

### 👥 **8-Role System Guidelines**
```ucode
~ Role Hierarchy (Access Levels 10-100)
👻 GHOST (10)     ~ Read-only access, minimal grid
⚰️ TOMB (20)      ~ Basic storage, simple operations
🔐 CRYPT (30)     ~ Secure storage, standard operations
🤖 DRONE (40)     ~ Automation tasks, standard grid
⚔️ KNIGHT (50)    ~ Security functions, standard grid
😈 IMP (60)       ~ Advanced automation, custom widgets
🧙‍♂️ SORCERER (80) ~ Development tools, full grid control
🧙‍♀️ WIZARD (100)  ~ System administration, all features

~ Role-Based Development
IF {ACCESS-LEVEL} >= 80 THEN         ~ Wizard/Sorcerer operations
    [GRID] <INIT|4X> {160/60}        ~ High-resolution grids
    [WIDGET] <CREATE> {ADVANCED-TYPE} ~ Advanced widget types
ELSE IF {ACCESS-LEVEL} >= 50 THEN    ~ Knight/Imp operations
    [GRID] <INIT> {120/48}           ~ Standard grids
    [WIDGET] <CREATE> {STANDARD-TYPE} ~ Standard widgets
ELSE                                 ~ Basic role operations
    [GRID] <SIZE|AUTO>               ~ Auto-sized grids
    [WIDGET] <CREATE> {BASIC-TYPE}   ~ Basic widgets only
END IF
```

### ⌨️ **Command Syntax Standards**
```ucode
~ Command operator usage
|  ~ Pipe for command options and actions
*  ~ Asterisk for parameters
/  ~ Slash for multiple parameters

~ Correct Format Examples
[COMMAND|ACTION*param1*param2]
[GRID|INIT*80/30]
[WIDGET|CREATE*NAME*TYPE*X/Y*W/H]
[ROLE|ACTIVATE|FORCE*WIZARD]

~ Comment Style
# This is a full line comment in uCODE
[COMMAND] <ACTION> {PARAM}          ~ End-of-line comment
~ Alternative comment style for line comments

~ Character Avoidance in uCODE
~ Avoid these in native syntax: '"`&%$
~ Minimize quotes: Use CAPS instead of "quoted text"
```

### 💾 **Data Management Best Practices**
```ucode
~ uDATA Format Integration
[DATA] <PARSE|STRICT> {JSON-DATA}   ~ Always use strict parsing
[DATA] <CONVERT|PRESERVE> {DATA} {UDATA} ~ Preserve structure
[FILE] <WRITE|BACKUP> {PATH} {DATA} ~ Always backup data files

~ Memory Operations
[MEM] <STORE|ENCRYPT> {KEY} {VALUE} ~ Encrypt sensitive data
[MEM] <RETRIEVE|DECRYPT> {KEY}      ~ Decrypt on retrieval
[MEM] <CLEAR> {PATTERN-WILDCARD}    ~ Use patterns for bulk operations

~ Template Variables
{CUSTOM:PROJECT-NAME}               ~ User-defined variables
{INPUT:DESCRIPTION}                 ~ Interactive input prompts
{UHEX:TYPE}                         ~ uHEX filename types
{GRID-WIDTH}                        ~ System-generated values
```

### 🔄 **Error Handling and Session Management**
```ucode
~ Comprehensive Error Handling
[TRY]
    ~ Main operation block
    [ROLE] <ACTIVATE|PRESERVE> {TARGET-ROLE}
    [GRID] <INIT|4X> {GRID-SIZE}
    ~ ... operations ...
[CATCH] {ERROR}
    ~ Error handling block
    [ERROR] <LOG|STACK> {Operation failed: } + {ERROR} {CRITICAL}
    [SESSION] <UNDO|FORCE>          ~ Undo on critical errors
    [ROLE] <ACTIVATE> {GHOST}       ~ Fallback to safe role
[END]

~ Session Management
[SESSION] <SAVE|AUTO>               ~ Enable auto-save
[SESSION] <HISTORY|DETAILED>        ~ Track operation history
[uCORE] <SESSION|SAVE>              ~ Save uCORE session state

~ Undo/Redo Support
UNDO                                ~ Quick undo last operation
[SESSION] <UNDO|FORCE>              ~ Force undo with verification
[SESSION] <REDO|CONFIRM>            ~ Redo with confirmation
```

### 🎯 **Performance Optimization**
```ucode
~ Grid Performance
[GRID] <RENDER|OPTIMIZE}            ~ Optimize rendering cycles
[WIDGET] <REFRESH> {SPECIFIC-WIDGET} ~ Refresh only changed widgets
[UMAP] <PAN|CENTER}                 ~ Center view efficiently

~ Data Processing
[GET] <JSON|RETRY> {API} {TOKEN}    ~ Retry failed API calls
[POST] <JSON|COMPRESS> {API} {DATA} ~ Compress large payloads
[DATA] <FILTER|REGEX> {DATA} {PATTERN} ~ Use regex for complex filtering

~ Memory Management
[MEM] <CLEAR> {TEMP-*}              ~ Clear temporary variables
[WORKFLOW] <CLEANUP|FORCE> {ALL}    ~ Regular system cleanup
[SYS] <OPTIMIZE|DEEP> {MEMORY}      ~ Deep memory optimization
```

### 🔧 **Development Workflow Integration**
```ucode
~ Assist Mode Usage
[WORKFLOW] <ASSIST|FORCE> {ENTER}   ~ Enter for complex operations
OK                                  ~ Quick assist mode entry
END                                 ~ Exit to command mode

~ Documentation Standards
~ Use markdown code blocks with 'ucode' language
~ Include role-based examples for different access levels
~ Provide both basic and advanced usage patterns
~ Reference complete STYLE-GUIDE.md for comprehensive standards

~ Template Processing
[TEMPLATE|PROCESS*template.md*output.md*variables.json*grid-config.json]
[TEMPLATE|GRID*PROCESS*layout*output*grid-size]
[TEMPLATE|UDATA*PROCESS*template*output*--minified]
```

### 🌟 **Advanced Integration Patterns**
```ucode
~ Multi-System Integration
<FUNCTION> {INTEGRATED-OPERATION} {OPERATION-TYPE}
    ~ Role-based access control
    DEF {ACCESS-LEVEL} = [ROLE] <PERMISSIONS> {CURRENT}

    ~ Grid system integration
    [GRID] <INIT|4X> {OPTIMAL-SIZE}
    [UMAP] <OVERLAY> {ENABLE*4X}

    ~ Data processing pipeline
    DEF {DATA} = [GET] <JSON|RETRY> {API-ENDPOINT}
    [DATA] <VALIDATE|REPORT> {DATA} {SCHEMA}

    ~ Widget visualization
    [WIDGET] <CREATE|TEMPLATE*DATA-VIZ*CHART}
    [WIDGET] <UPDATE> {DATA-VIZ*DATA*PROCESSED-DATA}

    ~ Session management
    [SESSION] <SAVE|AUTO>
    [MEM] <STORE|ENCRYPT> {OPERATION-LOG} {METADATA}
<END-FUNCTION>

~ Cross-Role Collaboration
~ Design functions that adapt to different role capabilities
~ Use access level checks for feature gating
~ Implement graceful degradation for lower roles
~ Provide role-specific UI elements and workflows
```

---

## ADVANCED SCRIPTING

### Multi-Language Container
```ucode
[SCRIPT|CREATE*UNIVERSAL*DATA-PIPELINE*MULTI-LANGUAGE]

<UNIVERSAL NAME="DATA-PIPELINE" ROLE="SORCERER+">
    # uDOS Universal Container v1.0.4.1
    # Multi-language data processing pipeline

    # Phase 1: Python data extraction
    <PYTHON>
        import json, requests, os

        def extract_data(api_url, output_file):
            response = requests.get(api_url)
            data = response.json()

            # Convert to uDATA format
            with open(output_file, 'w') as f:
                for record in data:
                    f.write(json.dumps(record, separators=(',', ':')) + '\n')

            return len(data)

        records = extract_data(
            os.environ.get('API_URL', 'https://api.example.com/data'),
            '/sandbox/data/extracted.json'
        )
        print(f"Extracted {records} records")
    </PYTHON>

    # Phase 2: Shell data validation
    <SHELL>
        #!/bin/bash
        INPUT_FILE="/sandbox/data/extracted.json"
        VALID_FILE="/sandbox/data/validated.json"
        ERROR_FILE="/sandbox/data/errors.json"

        # Validate JSON format
        jq empty "$INPUT_FILE" 2>/dev/null
        if [ $? -eq 0 ]; then
            cp "$INPUT_FILE" "$VALID_FILE"
            echo "Data validation passed"
        else
            echo "Data validation failed" >&2
            echo '{"error":"invalid_json","file":"'$INPUT_FILE'"}' > "$ERROR_FILE"
            exit 1
        fi
    </SHELL>

    # Phase 3: Node.js data transformation
    <NODE>
        const fs = require('fs');
        const inputFile = '/sandbox/data/validated.json';
        const outputFile = '/sandbox/data/transformed.json';

        // Read uDATA format
        const data = fs.readFileSync(inputFile, 'utf8')
            .trim().split('\n')
            .map(line => JSON.parse(line));

        // Transform data
        const transformed = data.map(record => ({
            ...record,
            transformed_at: new Date().toISOString(),
            pipeline: 'UNIVERSAL-DATA-PIPELINE',
            version: '1.0.4.1'
        }));

        // Write back as uDATA
        const output = transformed
            .map(record => JSON.stringify(record))
            .join('\n') + '\n';

        fs.writeFileSync(outputFile, output);
        console.log(`Transformed ${transformed.length} records`);
    </NODE>

    # Phase 4: Final Python reporting
    <PYTHON>
        import json
        from datetime import datetime

        def generate_report():
            with open('/sandbox/data/transformed.json', 'r') as f:
                records = [json.loads(line) for line in f]

            report = {
                'pipeline': 'UNIVERSAL-DATA-PIPELINE',
                'version': '1.0.4.1',
                'processed_at': datetime.now().isoformat(),
                'total_records': len(records),
                'status': 'SUCCESS'
            }

            with open('/sandbox/data/pipeline_report.json', 'w') as f:
                json.dump(report, f, indent=2)

            print(f"Pipeline completed: {len(records)} records processed")

        generate_report()
    </PYTHON>
</UNIVERSAL>

~ Execute the complete pipeline
[SCRIPT|RUN*DATA-PIPELINE]
```

---

## IMPLEMENTATION GUIDE

### System Requirements
```
┌─────────────────────────────────────────────┐
│ uDOS v1.0.4.1 + uSCRIPT Implementation     │
├─────────────────────────────────────────────┤
│ ✓ uSERVER runtime engine (active)          │
│ ✓ uMEMORY template system (configured)     │
│ ✓ Role system CRYPT (30) minimum           │
│ ✓ Python 3.8+ (for Python containers)     │
│ ✓ Node.js 16+ (for Node containers)        │
│ ✓ Bash 4+ (for Shell containers)           │
│ ✓ Sandbox workspace (/sandbox/)            │
└─────────────────────────────────────────────┘
```

### Directory Structure
```
/uDOS/
├─ uSCRIPT/
│  ├─ active/           ~ Active container instances
│  ├─ registry/         ~ Container definitions
│  ├─ library/          ~ Shared container modules
│  └─ runtime/          ~ Execution environment
├─ sandbox/
│  ├─ scripts/          ~ User-created containers
│  ├─ data/             ~ Container input/output
│  ├─ logs/             ~ Container execution logs
│  └─ temp/             ~ Temporary execution files
└─ uMEMORY/
   ├─ system/
   │  └─ templates/     ~ Container templates
   └─ user/
      └─ containers/    ~ User container definitions
```

### Installation & Setup
```ucode
~ Check system readiness
[SYS|VERSION]                              ~ Verify uDOS v1.0.4.1
[ROLE|CURRENT]                             ~ Verify CRYPT+ role
[SCRIPT|SYSTEM*CHECK]                      ~ Verify uSCRIPT availability

~ Initialize uSCRIPT system
[SCRIPT|SYSTEM*INIT]                       ~ Initialize container system
[SCRIPT|TEMPLATE*INSTALL*STANDARD]         ~ Install standard templates
[SCRIPT|RUNTIME*START]                     ~ Start container runtime

~ Create first container
[SCRIPT|CREATE*PYTHON*HELLO-WORLD*TUTORIAL]
[SCRIPT|RUN*HELLO-WORLD]                   ~ Test execution
```

### Development Workflow
```ucode
<FUNCTION> {CONTAINER-DEVELOPMENT-CYCLE}
    ~ 1. Design phase
    [WORKFLOW|ASSIST*ENTER]
    [SCRIPT|DESIGN*CONTAINER-SPEC]

    ~ 2. Template selection
    [TEMPLATE|LIST*{LANGUAGE}]
    [TEMPLATE|SELECT*{TEMPLATE-NAME}]

    ~ 3. Container creation
    [SCRIPT|CREATE*{LANGUAGE}*{NAME}*{PURPOSE}]

    ~ 4. Development iteration
    [SCRIPT|EDIT*{NAME}]
    [SCRIPT|TEST*{NAME}]
    [SCRIPT|DEBUG*{NAME}]

    ~ 5. Production deployment
    [SCRIPT|VALIDATE*{NAME}]
    [SCRIPT|SCHEDULE*{NAME}*{FREQUENCY}]
    [SCRIPT|MONITOR*{NAME}*{METRICS}]

    [WORKFLOW|ASSIST*EXIT]
<END-FUNCTION>
```

---

## 📚 **Reference Guidelines**

### **Code Comments**
- Use `~` for end-of-line comments in uCODE
- Use `#` for full-line comments
- Avoid excessive commenting in production scripts
- Document complex role-based logic and grid operations

### **Variable Management**
- Use descriptive names: `{CURRENT-ROLE}`, `{GRID-STATUS}`
- Use pattern prefixes: `{USER-*}`, `{GRID-*}`, `{WIDGET-*}`
- Clear temporary variables: `[MEM] <CLEAR> {TEMP-*}`
- Define constants: `DEF {MAX-WIDGETS} = 16`

### **Function Design**
- Keep functions focused on single responsibilities
- Use role-based parameter validation
- Implement comprehensive error handling
- Support undo operations where applicable
- Include grid-aware operations for UI functions

### **System Integration**
- Follow uCORE component naming conventions
- Use uHEX v7.0 filename convention for generated files
- Integrate with uDATA format for JSON processing
- Implement uGRID layouts for visual components
- Support multi-device deployment scenarios

---

*uCODE & uSCRIPT Reference Manual v1.0.4.1*
*Complete technical reference for modular scripting on uDOS*
*Preserving the elegance of 1981 Acorn User Manual traditions*

**For user-friendly introduction**: See [USER-GUIDE.md](USER-GUIDE.md)
**For style standards**: See [STYLE-GUIDE.md](STYLE-GUIDE.md)
**For quick reference**: See [QUICK-STYLES.md](QUICK-STYLES.md)
