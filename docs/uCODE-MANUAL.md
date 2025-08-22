# uCODE MODULAR COMMAND REFERENCE MANUAL

The essential command set for uCODE, the native programming language for uSCRIPT operations on devices running uDOS v1.3.3.

## TABLE OF CONTENTS

- [CORE COMMANDS](#core-commands)
- [ENHANCED CORE COMMANDS](#enhanced-core-commands)
- [ROLE MANAGEMENT](#role-management)
- [MEMORY & DATA](#memory--data)
- [DATA CONTROL](#data-control)
- [WORKFLOW SYSTEM](#workflow-system)
- [ASSIST MODE MANAGEMENT](#assist-mode-management)
- [SETUP COMMANDS](#setup-commands)
- [SCRIPT EXECUTION](#script-execution)
- [UNDO/REDO OPERATIONS](#undoredo-operations)
- [ERROR HANDLING](#error-handling)
- [EXAMPLES](#examples)

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

## ENHANCED CORE COMMANDS

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

## ROLE MANAGEMENT

### [ROLE] <ACTION> {ROLE-NAME}
```ucode
~ Role operations
[ROLE] <ACTIVATE> {DRONE}       ~ Activate role
[ROLE] <ACTIVATE> {GHOST}
[ROLE] <ACTIVATE> {IMP}
[ROLE] <ACTIVATE> {SORCERER}
[ROLE] <ACTIVATE> {WIZARD}
[ROLE] <ACTIVATE|FORCE> {ROLE}  ~ Force role activation
[ROLE] <CURRENT>                ~ Get current role
[ROLE] <CURRENT|DETAILED>       ~ Get detailed role info
[ROLE] <SWITCH> {NEW-ROLE}      ~ Switch to new role
[ROLE] <SWITCH|PRESERVE> {NEW-ROLE} ~ Switch preserving session
[ROLE] <LIST>                   ~ List available roles
[ROLE] <LIST|ACTIVE>            ~ List only active roles
[ROLE] <PERMISSIONS> {ROLE}     ~ Check role permissions
[ROLE] <PERMISSIONS|FULL> {ROLE} ~ Full permission details
```

## MEMORY & DATA

### [MEM] <ACTION> {KEY} {VALUE}
```ucode
~ Memory operations
[MEM] <STORE> {KEY} {VALUE}     ~ Store data
[MEM] <STORE|ENCRYPT> {KEY} {VALUE} ~ Store encrypted data
[MEM] <RETRIEVE> {KEY}          ~ Retrieve data
[MEM] <RETRIEVE|DECRYPT> {KEY}  ~ Retrieve and decrypt data
[MEM] <LIST>                    ~ List stored items
[MEM] <LIST> {PATTERN}          ~ List with pattern
[MEM] <LIST|SORTED> {PATTERN}   ~ List sorted with pattern
[MEM] <CLEAR> {KEY}             ~ Clear specific item
[MEM] <CLEAR> {PATTERN-WILDCARD}  ~ Clear with pattern
[MEM] <CLEAR|FORCE> {PATTERN}   ~ Force clear pattern
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

## WORKFLOW SYSTEM

### [WORKFLOW] <ACTION> {PARAMETER}
```ucode
~ Workflow management (v1.3.3)
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
~ Enhanced uCORE operations
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

### Enhanced Assist Commands
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

### Enhanced Setup Commands
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

### Enhanced Undo/Redo Support
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
~ Enhanced session control
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

### Project Setup with Enhanced Data Control
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
```### Workflow Automation with Enhanced Data Sync
```ucode
~ Enhanced workflow automation with data synchronization and pipe options
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

### Enhanced API Data Processing
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

### Enhanced System Administration
```ucode
~ Example using enhanced core commands with assist mode
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

## BEST PRACTICES

### Naming Conventions
- **Variables**: Use {CAPITALS-DASH-1234567890} only
  - Examples: {USER-DATA}, {PROJECT-NAME}, {API-TOKEN}
  - No lowercase, underscores, or special characters except dash and numbers
- **Functions**: Use <FUNCTION> {FUNCTION-NAME} ... <END-FUNCTION>
  - Examples: {DAILY-MAINTENANCE}, {SETUP-PROJECT}
- **Commands**: [SHORTCODE] <ACTION> {PARAMETER}

### Comment Style
- **Comments**: Use single ~ for comments (REM equivalent)
  - Example: `~ This is a comment`
  - Text to the right of ~ is comment-only
- **Avoid Quotes**: uCODE avoids unnecessary quote symbols
  - Use {MESSAGE-TEXT} instead of "message text" where possible
  - String concatenation: {Hello } + {WORLD} instead of "Hello " + "World"

### Command Usage
- Use [TRY] ... [CATCH] ... [END] for error handling
- Activate appropriate roles with [ROLE] <ACTIVATE> {ROLE-NAME}
- Store session data with [MEM] <STORE> {KEY} {VALUE}
- Log operations with [LOG] <LEVEL> {MESSAGE}

### Enhanced Command Best Practices
- **Direct Commands**: Use bash-style commands (TRASH, BACKUP, ROLE) for quick operations
- **uCODE Commands**: Use bracketed syntax [COMMAND] <ACTION> for script integration
- **Assist Mode**: Use OK/END for quick assist mode toggling in interactive sessions
- **Session Management**: Always save sessions before major operations with [SESSION] <SAVE>
- **Undo Support**: Verify operations are undoable before permanent changes
- **Role Isolation**: Use role-specific commands for data separation and security

### Setup and Testing Guidelines
- **Testing Environment**: Use SETUP test for sandbox testing environment
- **Production Safety**: Never test in development mode from everyday operations
- **Role Configuration**: Use SETUP role to properly configure role environments
- **Backup Strategy**: Create backups before major role switches or system changes

### PIPE | Option Syntax
- **Command Options**: Use PIPE | to specify command options and modifiers
  - Format: [COMMAND] <Action|OPTION> {PARAMETER}
  - Examples: [SYS] <STATUS|BRIEF>, [LOG] <INFO|TIMESTAMP> {MESSAGE}
- **Option Guidelines**:
  - Use CAPITALS-DASH-NUMBER format for option names: FORCE, RETRY, ENCRYPT, ASYNC, DETAILED
  - Follow same naming rules as variables: only CAPITALS, DASH, and NUMBERS
  - Chain options with additional pipes: <Action|OPTION-1|OPTION-2>
  - Common options: BRIEF/DETAILED, FORCE/GENTLE, ASYNC/SYNC, ENCRYPT/PLAIN
- **Best Practice Examples**:
  - [GET] <REQUEST|RETRY> for robust API calls
  - [MEM] <STORE|ENCRYPT> for secure data storage
  - [ROLE] <ACTIVATE|PRESERVE> to maintain context
  - [ERROR] <LOG|STACK> for detailed error reporting

### Data Control Best Practices
- Use [GET] for retrieving data from APIs and web services
- Use [POST] for sending data, creating resources, and API calls
- Always validate data with [DATA] <VALIDATE> before processing
- Cache API responses with [MEM] <STORE> to reduce requests
- Handle API errors with proper [TRY] ... [CATCH] blocks

### Variable Management
- Use descriptive names: {CURRENT-ROLE}, {SYSTEM-STATUS}
- Use pattern prefixes: {USER-*}, {SESSION-*}, {WORKFLOW-*}
- Clear temporary variables with [MEM] <CLEAR> {PATTERN}
- Define variables with DEF {VARIABLE} = {VALUE}

### Workflow Integration
- Enter assist mode for complex operations: [WORKFLOW] <ASSIST> {ENTER}
- Update briefings for session continuity: [WORKFLOW] <BRIEFINGS> {UPDATE}
- Use cleanup commands for maintenance: [WORKFLOW] <CLEANUP> {ALL}
- Save sessions before major operations: [uCORE] <SESSION> {SAVE}

---

*This streamlined reference focuses on the essential uCODE commands with proper naming conventions (CAPITALS-DASH-1234567890), ~ comment style, minimal quotes, and enhanced data control capabilities for efficient uDOS v1.3.3 operations.*
