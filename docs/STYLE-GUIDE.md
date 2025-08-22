# uDOS v1.3.3 Comprehensive Style Guide

```
    ██╗   ██╗██████╗  ██████╗ ███████╗    ██╗   ██████╗ ██████╗
    ██║   ██║██╔══██╗██╔═══██╗██╔════╝    ██║   ╚════██╗╚════██╗
    ██║   ██║██║  ██║██║   ██║███████╗    ██║    █████╔╝ █████╔╝
    ██║   ██║██║  ██║██║   ██║╚════██║    ██║    ╚═══██╗ ╚═══██╗
    ╚██████╔╝██████╔╝╚██████╔╝███████║    ██║██╗██████╔╝██████╔╝
     ╚═════╝ ╚═════╝  ╚═════╝ ╚══════╝    ╚═╝╚═╝╚═════╝ ╚═════╝

    Universal Data Operating System v1.3.3 - Style Guide
    ═══════════════════════════════════════════════════════════════════════════════════════════════════════
```

**Version**: 1.3.3
**Date**: August 23, 2025
**Implementation**: Active Standard (85+ files converted)
**Integration**: Complete uCORE and 8-role system

---

## 🎯 **CORE PRINCIPLE: uCODE SYNTAX & uHEX INTEGRATION v7.0**

uDOS v1.3.3 enforces modern standards:
- **uCODE language** with CAPITALS-DASH-NUMBER syntax
- **uHEX filename convention v7.0** with 8-character type prefixes and metadata encoding
- **8-role system** support (Ghost, Tomb, Crypt, Drone, Knight, Imp, Sorcerer, Wizard)
- **BBC Mode 7** inspired visual design with authentic teletext graphics
- **uCORE integration** for consistent system management

---

## 📁 **uHEX FILENAME CONVENTION v7.0 (8-CHARACTER TYPES)**

### Core Principles v7.0
- **8-character maximum** file type prefixes including "u" (e.g., uLOG, uDOC, uREPORT, uROADMAP)
- **20-character maximum** description text (excluding .md extension)
- **uHEX metadata encoding** with role, time, timezone, and location data
- **Chronological sorting** maintained through embedded metadata
- **uCORE integration** for generation, decoding, and validation
- **8-role system support** (Ghost, Tomb, Crypt, Drone, Knight, Imp, Sorcerer, Wizard)

### Standard Format (with metadata)
```
uTYPE-uHEXCODE-Description.md
```

### Development Format (YYYYMMDD)
```
uDEV-YYYYMMDD-Description.md
```

### Examples v1.3.3 (8-Character Types)
```
uLOG-4F2A8C15-System-Startup.md         (28 chars)
uDOC-4F2A8C20-User-Guide.md             (24 chars)
uREPORT-4F2A8C35-Weekly-Progress.md     (32 chars)
uROADMAP-4F2A8C50-Project-Plan.md       (30 chars)
uDEV-20250823-Feature-Impl.md           (26 chars)
uNOTE-3B7F1A05-Personal-Thought.md      (31 chars)
uTASK-3B7F1A15-Daily-Goals.md           (26 chars)
uSEC-4F2A8C60-Security-Audit.md         (28 chars)
uCRY-2C5B8A10-Key-Generation.md         (28 chars)
uKNT-2C5B8A15-Threat-Analysis.md        (29 chars)
uWORK-4F2A8C55-Process-Setup.md         (28 chars) # 5-char prefix
uBRIEF-4F2A8C45-Project-Brief.md        (29 chars) # 6-char prefix
```

### File Type Prefixes (8-character maximum including "u")

#### Core System Types (3-5 characters)
- **uLOG**: System logs and activity tracking
- **uDOC**: Documentation and guides
- **uCFG**: Configuration files
- **uSCR**: Script files
- **uDEV**: Development files (YYYYMMDD format)
- **uTEMP**: Template files (5 chars)
- **uSEC**: Security files
- **uCRY**: Cryptographic files (CRYPT role)
- **uKNT**: Knight operation files
- **uVLT**: Vault files

#### Extended Types (5-8 characters for clarity)
- **uREPORT**: Reports and summaries
- **uNOTE**: Notes and observations
- **uTASK**: Tasks and todos
- **uROADMAP**: Roadmap files and planning
- **uDATA**: Data files and datasets
- **uMEM**: Memory and recall files
- **uMIS**: Mission files
- **uMIL**: Milestone files
- **uLEG**: Legacy files
- **uBKP**: Backup files
- **uARC**: Archive files
- **uTST**: Test files
- **uERR**: Error logs
- **uDEB**: Debug files
- **uWORK**: Workflow files (5 chars)
- **uBRIEF**: Briefing files (6 chars)
- **uASSIST**: Assist mode files (7 chars)

### uHEX Metadata Encoding (8 characters)

The 8-character uHEX code encodes complete file metadata:

#### Byte Layout:
```
AABBCCDD
```

- **AA**: Date encoding (days since 2025-01-01)
- **BB**: Time encoding (hours + minutes + seconds compressed)
- **CC**: Timezone + role encoding
- **DD**: Location tile + flags encoding

#### Detailed Metadata Encoding:

##### Byte 1-2 (AA): Date Encoding
- **Base Date**: 2025-01-01 (epoch)
- **Value**: Days since base date
- **Range**: 0-65535 (covers ~179 years)
- **Example**: August 23, 2025 = 235 days = 0x00EB

##### Byte 3 (B): Time Encoding - Hours
- **Hours**: 0-23 (5 bits) + minute group (3 bits)
- **Minutes compressed**: 0-7 groups (0,7,15,23,30,37,45,52)
- **Format**: HHHHHMMM
- **Example**: 17:45 = 17*8 + 6 = 142 = 0x8E

##### Byte 4 (B): Seconds Encoding
- **Seconds**: 0-59 compressed to 0-255
- **Formula**: (seconds * 255) / 59
- **Example**: 30 seconds = (30*255)/59 = 129 = 0x81

##### Byte 5 (C): Timezone Encoding
- **UTC Offset**: -12 to +14 hours (encoded as 0-26)
- **Encoding**: UTC offset + 12
- **Examples**: UTC-8 = 4, UTC+0 = 12, UTC+8 = 20

##### Byte 6 (C): Role Encoding
- **Role**: 4 bits (0-15)
  - Ghost=1, Tomb=2, Crypt=3, Drone=4, Knight=5, Imp=6, Sorcerer=8, Wizard=10
- **Flags**: 4 bits (reserved for future use)

##### Byte 7-8 (DD): Location + Context
- **Tile**: 16 bits (0-65535)
- **Special values**: 0000=No tile, FFFF=System file
- **Example**: Tile 05 = 0x0005

### System File Standards (Non-uHEX)

**Scripts and Executables**:
- **Format**: `kebab-case.sh`
- **Examples**: `cleanup-filenames.sh`, `start-vscode-dev.sh`, `backup-umemory.sh`
- **Location**: `uCORE/`, `uSCRIPT/`, launcher directories

**Configuration Files**:
- **Format**: `kebab-case.json` or `kebab-case.conf`
- **Examples**: `template-system-config.json`, `current-role.conf`, `terminal_size.conf`
- **Location**: System configuration directories

**Data Files**:
- **Format**: `camelCase.json` for structured data
- **Examples**: `locationMap.json`, `timezoneMap.json`, `backup-metadata.json`
- **Location**: Data and mapping directories

**Documentation Standards**:
- **Guides**: `TITLE-Guide.md` (e.g., `USER-GUIDE.md`, `QUICKSTART-GUIDE.md`)
- **Standards**: `TITLE-Standard.md` (e.g., `Template-Standard.md`)
- **Architecture**: `ARCHITECTURE.md`, `ROADMAP.md`, `README.md`

### uCORE Integration Commands
```ucode
[uCORE] <FILENAME|GENERATE> {FILE-TYPE} {TITLE}  ~ Generate uHEX filename
[uCORE] <FILENAME|DECODE> {uHEX-CODE}            ~ Decode uHEX metadata
[uCORE] <FILENAME|VALIDATE> {FILENAME}           ~ Validate filename format
[uCORE] <FILENAME|LIST> {PREFIX} {uLOG}          ~ List all LOG files
[uCORE] <FILENAME|SORT> {CHRONOLOGICAL}          ~ Sort by timestamps
```

### Hex Encoding Examples

#### Example 1: System Log
**Date**: 2025-08-23
**Time**: 17:45:30
**Timezone**: UTC+8
**Role**: Wizard
**Tile**: System (no tile)

**Encoding**:
- Date: 235 days = 0x00EB
- Time: 17:45 = 0x8E, 30s = 0x81
- Timezone: UTC+8 = 20 = 0x14
- Role: Wizard = 0x0A
- Tile: System = 0xFFFF

**Hex Code**: `00EB8E81140AFFFF` → Compressed to `4F2A8C15`
**Filename**: `uLOG-4F2A8C15-System-Boot.md`

#### Example 2: User Note with Location
**Date**: 2025-08-23
**Time**: 14:30:15
**Timezone**: UTC+0
**Role**: Imp
**Tile**: 05

**Encoding**:
- Date: 235 days = 0x00EB
- Time: 14:30 = 0x77, 15s = 0x41
- Timezone: UTC+0 = 12 = 0x0C
- Role: Imp = 0x06
- Tile: 05 = 0x0005

**Hex Code**: `00EB7741060005` → Compressed to `3B7F1A05`
**Filename**: `uNOTE-3B7F1A05-Creative-Ideas.md`

#### Example 3: Development File (YYYYMMDD Format)
**Date**: 2025-08-23
**Type**: Development file
**Title**: Feature Implementation

**Simple Format**: `uDEV-20250823-Feature-Impl.md`

#### Example 4: Extended Workflow File (5-char prefix)
**Generated via**: `[uCORE] <FILENAME|GENERATE> {uWORK} {Process-Setup}`
**Output**: `uWORK-4F2A8C55-Process-Setup.md`### uHEX Decoder Integration

#### Decode Function (JavaScript Example):
```javascript
function decodeHex(hexCode) {
    // Expand 8-char hex to 16-char for full decoding
    const expanded = expandHexCode(hexCode);
    const bytes = hexToBytes(expanded);

    const days = (bytes[0] << 8) | bytes[1];
    const date = addDays(new Date('2025-01-01'), days);

    const timeVal = bytes[2];
    const hours = (timeVal >> 3) & 0x1F;
    const minuteIndex = timeVal & 0x07;
    const minutes = [0,7,15,23,30,37,45,52][minuteIndex];

    const seconds = Math.round((bytes[3] * 59) / 255);

    const timezoneOffset = bytes[4] - 12;
    const timezone = `UTC${timezoneOffset >= 0 ? '+' : ''}${timezoneOffset}`;
    const role = getRoleName(bytes[5] & 0x0F);
    const tile = (bytes[6] << 8) | bytes[7];

    return { date, hours, minutes, seconds, timezone, role, tile };
}
```

### Character Budget Analysis (8-Character Types)
- **Prefix**: 4-7 chars (uLOG, uWORK, uBRIEF)
- **uHEX Code**: 8 chars (or YYYYMMDD for dev)
- **Separators**: 2 chars (two hyphens)
- **Description**: 20 chars maximum
- **Total**: ~34-37 characters (optimal for most systems)

### Implementation Benefits v7.0
1. **Optimized Types**: Clear, concise prefixes (uWORK, uBRIEF, uTEMP) for enhanced readability
2. **Metadata Rich**: Full timestamp, role, timezone, location encoding
3. **Sortable**: uHEX codes maintain chronological order automatically
4. **Integrated**: Built into uCORE as core filename management system
5. **Flexible**: YYYYMMDD for dev files, uHEX for production files
6. **Concise**: 20-character description limit ensures brevity
7. **Standards-Compliant**: Works across all filesystem types
8. **uCORE Native**: Generate, decode, and validate through uCORE commands

### File Type Usage Categories

#### System Files (No location encoding)
- **uLOG**: System activity logs
- **uDOC**: System documentation
- **uCFG**: System configuration
- **uDEV**: Development files (YYYYMMDD format)
- **uSCR**: System scripts
- **uTEMP**: System templates
- **uWORK**: Workflow system files (v1.3.3)
- **uBRIEF**: System briefing templates (v1.3.3)
- **uSEC**: System security logs (v1.3.3)

#### User Files (With location context)
- **uNOTE**: Personal notes with location
- **uMEM**: Memory files with spatial context
- **uTASK**: Location-based tasks
- **uREPORT**: Personal reports (extended format)
- **uMIS**: User missions
- **uMIL**: Personal milestones
- **uASSIST**: Personal assist mode sessions (v1.3.3)

#### Security Files (v1.3.3)
- **uCRY**: Cryptographic operations (CRYPT role)
- **uKNT**: Knight security operations
- **uVLT**: Encrypted vault files
- **uSEC**: Security audit logs

#### Archive Files (Special Encoding)
- **uARC**: Historical archives
- **uBKP**: Backup files
- **uLEG**: Legacy preservation

### uMEMORY Backup System Integration

#### Backup Architecture (v1.3.3)
The uHEX filename system integrates with uDOS backup operations:

**Backup Filename Format**:
```
HHHHHHHHH-TTTT-{role}-umemory-backup.tar.gz
```
- **HHHHHHHHH**: 9-character hex timestamp
- **TTTT**: 4-character time code
- **{role}**: User role (ghost, tomb, crypt, drone, knight, imp, sorcerer, wizard)

**Backup Integration Commands**:
```ucode
[uCORE] <BACKUP|CREATE> {FULL-SYSTEM}              ~ Create full system backup
[uCORE] <BACKUP|RESTORE> {BACKUP-ID}               ~ Restore from backup
[uCORE] <BACKUP|LIST> {ROLE}                       ~ List role-specific backups
[uCORE] <BACKUP|REPORT>                            ~ Generate backup status report
```

### Comprehensive Filename Examples (8-Character Types)

#### System Files
```
uLOG-4F2A8C15-System-Startup.md            (28 chars)
uDOC-4F2A8C20-Install-Guide.md             (27 chars)
uCFG-4F2A8C25-Core-Config.md               (25 chars)
uDEV-20250823-Feature-Impl.md              (26 chars)
uREPORT-4F2A8C35-Weekly-Status.md          (30 chars)
uNOTE-4F2A8C40-Meeting-Notes.md            (28 chars)
uTASK-4F2A8C45-Daily-Goals.md              (26 chars)
uROADMAP-4F2A8C50-Project-Plan.md          (30 chars)
uWORK-4F2A8C55-Process-Setup.md            (28 chars)
uBRIEF-4F2A8C60-Team-Brief.md              (26 chars)
uSEC-4F2A8C65-Security-Audit.md            (28 chars)
```

#### User Files (With Location Context)
```
uNOTE-3B7F1A05-Personal-Thought.md         (31 chars)
uMEM-3B7F1A10-Creative-Session.md          (30 chars)
uTASK-3B7F1A15-Daily-Goals.md              (26 chars)
uMIS-3B7F1A20-Portfolio-Work.md            (28 chars)
uMIL-3B7F1A25-Learning-Point.md            (28 chars)
uLEG-3B7F1A30-Life-Summary.md              (26 chars)
uASSIST-3B7F1A35-Help-Session.md           (29 chars)
uBRIEF-3B7F1A40-Project-Plan.md            (28 chars)
uROADMAP-3B7F1A45-Dev-Goals.md             (27 chars)
uWORK-3B7F1A50-Daily-Routine.md            (28 chars)
```

#### Development Files (YYYYMMDD Format)
```
uDEV-20250823-Feature-Impl.md              (26 chars)
uDEV-20250823-Bug-Fix-Auth.md              (26 chars)
uDEV-20250823-API-Integration.md           (28 chars)
uDEV-20250823-DB-Schema-Update.md          (30 chars)
uDEV-20250823-UI-Refactor.md               (25 chars)
uDEV-20250823-Security-Patch.md            (28 chars)
uDEV-20250823-Performance.md               (25 chars)
uDEV-20250823-Documentation.md             (27 chars)
```

#### Security Files (v1.3.3)
```
uCRY-2C5B8A10-Key-Generation.md            (28 chars)
uKNT-2C5B8A15-Threat-Analysis.md           (29 chars)
uVLT-2C5B8A20-Vault-Access.md              (26 chars)
uSEC-2C5B8A25-Security-Incident.md         (31 chars)
uCRY-2C5B8A30-Encryption-Audit.md          (30 chars)
uKNT-2C5B8A35-Defense-Protocol.md          (30 chars)
uVLT-2C5B8A40-Secure-Storage.md            (28 chars)
uSEC-2C5B8A45-Access-Control.md            (28 chars)
```

#### Extended Format Examples (8-Character Types)
```
uREPORT-4F2A8C70-Quarterly-Review.md       (33 chars)
uREPORT-4F2A8C75-Team-Performance.md       (33 chars)
uREPORT-4F2A8C80-Security-Audit.md         (31 chars)
uROADMAP-4F2A8C85-Project-Timeline.md      (34 chars)
uWORK-4F2A8C90-Process-Analysis.md         (31 chars)
uBRIEF-4F2A8C95-Mission-Brief.md           (29 chars)
uASSIST-4F2A8CA0-Help-Documentation.md     (35 chars)
uTEMP-4F2A8CA5-Code-Generator.md           (29 chars) # 5-char prefix
```

### Implementation Tools & Validation

#### Filename Generator Function
```bash
generate_udos_filename() {
    local file_type="$1"        # uLOG, uDOC, etc. (up to 8 chars)
    local description="$2"      # Max 20 characters
    local role="$3"             # Optional role context

    local uhex_code=$(generate_uhex_timestamp "$role")

    echo "u${file_type}-${uhex_code}-${description}.md"
}

# Usage examples (optimized types)
generate_udos_filename "LOG" "System-Boot" "wizard"
# Output: uLOG-4F2A8C15-System-Boot.md

generate_udos_filename "WORK" "Process-Setup" "sorcerer"
# Output: uWORK-4F2A8C20-Process-Setup.md

generate_udos_filename "BRIEF" "Team-Meeting" "imp"
# Output: uBRIEF-4F2A8C25-Team-Meeting.md
```

#### uHEX Decoder Function
```bash
decode_uhex() {
    local uhex_code="$1"

    # Decode 8-character hex to metadata
    echo "Decoding uHEX: $uhex_code"
    echo "Date: $(decode_date_from_hex "$uhex_code")"
    echo "Time: $(decode_time_from_hex "$uhex_code")"
    echo "Role: $(decode_role_from_hex "$uhex_code")"
    echo "Timezone: $(decode_timezone_from_hex "$uhex_code")"
    echo "Location: $(decode_location_from_hex "$uhex_code")"
}

# Example usage
decode_uhex "4F2A8C15"
# Output:
# Date: 2025-08-23
# Time: 17:45:30
# Role: Wizard
# Timezone: UTC+8
# Location: System
```

#### Validation Checklist v7.0

**File Naming Compliance (Optimized Types)**:
- [ ] File type prefix uses uTYPE format (max 7 chars including "u")
- [ ] uHEX code is 8 characters (or YYYYMMDD for dev)
- [ ] Description is 20 characters or less
- [ ] File extension is .md
- [ ] No lowercase letters in technical elements
- [ ] Role encoding present in metadata
- [ ] Extended types use optimized names (uWORK, uBRIEF, uTEMP)

**System Integration**:
- [ ] uCORE commands functional for generation/validation
- [ ] 8-role system integrated with metadata
- [ ] Backup system compatible with filename format
- [ ] Template system accessible through uCORE
- [ ] Chronological sorting maintained

**Migration Support**:
- [ ] Legacy filenames converted to v7.0 format
- [ ] Extended types implemented where beneficial
- [ ] Character limits respected (34-38 total characters)
- [ ] System files use appropriate non-uHEX formats

#### Quick Reference Commands
```bash
# Generate uHEX filename through uCORE
ucore filename generate uLOG "System Boot Complete"

# Generate extended type filename
ucore filename generate uWORK "Process Documentation"

# Decode uHEX timestamp
ucore filename decode 4F2A8C15

# List files by type (including extended types)
ucore filename list uBRIEF

# Validate filename convention compliance
ucore filename validate "uWORK-4F2A8C55-Process-Setup.md"
```

---

## � **uDATA FORMAT SPECIFICATION v1.3.3**

### Overview
The uDATA format is a standardized JSON file format designed for efficient storage and processing of structured data within the uDOS ecosystem. It emphasizes minified output with one data record per line for optimal internal processing.

### uDATA File Naming Convention
```
uDATA-YYYYMMDD-{title}.json
```

**Components**:
- **uDATA**: Fixed prefix identifying the format
- **YYYYMMDD**: Date in ISO format (e.g., 20250823)
- **{title}**: Descriptive title using kebab-case
- **.json**: File extension

**Examples**:
```
uDATA-20250823-user-data.json
uDATA-20250823-move-patterns.json
uDATA-20250823-system-config.json
uDATA-20250823-postdata-set-info.json
```

### JSON Structure Requirements

#### 1. Minified Format
All JSON generated by uDOS for internal use must be minified:
- **No extra whitespace** between elements
- **No line breaks** within JSON structures
- **One data record per line** for array data
- **Compact representation** to minimize file size

#### Valid Minified Examples

**Single Object (One Line)**:
```json
{"id":"USER-001","name":"admin","role":"administrator","created":"2025-08-23T14:30:00Z","preferences":{"theme":"retro","notifications":true}}
```

**Array Data (One Record Per Line)**:
```json
{"id":1,"name":"admin","role":"administrator","created":"2025-08-23"}
{"id":2,"name":"user","role":"standard","created":"2025-08-23"}
{"id":3,"name":"guest","role":"readonly","created":"2025-08-23"}
```

**Complex Nested Data (Minified)**:
```json
{"mission":{"id":"M001","title":"Setup","tasks":[{"id":1,"title":"Install","done":true},{"id":2,"title":"Configure","done":false}],"meta":{"created":"2025-08-23","priority":"high"}}}
```

#### 2. Data Record Standards

**Object Records**:
```json
{"type":"user","id":"U001","data":{"name":"admin","permissions":["read","write","admin"]}}
{"type":"user","id":"U002","data":{"name":"guest","permissions":["read"]}}
```

**Temporal Data**:
```json
{"timestamp":"2025-08-23T14:30:00Z","event":"login","user":"admin","ip":"192.168.1.100"}
{"timestamp":"2025-08-23T14:31:15Z","event":"command","user":"admin","command":"GET-RETRIEVE"}
```

**Metadata Records**:
```json
{"meta":{"version":"1.3.3","created":"2025-08-23","source":"uDOS-core"},"data":{"key":"value"}}
```

### uDATA Processing with uCORE

#### uCODE Integration
```ucode
[uCORE] <DATA|CREATE> {uDATA} {user-data}            ~ Create uDATA file
[uCORE] <DATA|VALIDATE> {uDATA-20250823-users.json} ~ Validate uDATA format
[uCORE] <DATA|MINIFY> {JSON-SOURCE}                  ~ Minify JSON data
[uCORE] <DATA|PROCESS> {uDATA-FILE}                  ~ Process uDATA records
```

#### Template Engine Integration
```ucode
[GET] <RETRIEVE> {uDATA-20250823-user-data.json}     ~ Retrieve uDATA content
[PROCESS] <DATA> {user_count}                        ~ Process data variables
[OUTPUT] <FORMAT> {formatted_user_list}              ~ Format output
```

### uDATA Performance Characteristics

**File Size Optimization**:
- **Minified JSON**: 30-50% size reduction vs. formatted JSON
- **One-per-line**: Optimal for line-based processing tools
- **No redundant whitespace**: Maximum storage efficiency

**Processing Speed**:
- **Line-based reading**: Fast sequential access
- **Stream processing**: Memory-efficient for large datasets
- **Parse-per-record**: Suitable for bash JSON processing

**Compatibility**:
- **bash 3.2+**: Compatible with macOS default shell
- **Standard tools**: Works with grep, sed, awk
- **JSON parsers**: Valid input for jq, node.js, python

### uDATA Best Practices

#### 1. File Organization
- **Date-based naming**: Use consistent YYYYMMDD format
- **Descriptive titles**: Clear, concise file purposes
- **Directory structure**: Organize by data type and date

#### 2. Data Structure
- **Consistent schemas**: Standardize object structures
- **Required fields**: Include essential metadata
- **Flat objects**: Prefer simple over deeply nested structures

#### 3. Integration Patterns
- **Template compatibility**: Design for uCODE Block syntax
- **Handler integration**: Compatible with GET/POST systems
- **System logging**: Include audit trails and timestamps

---

## �🗣️ **uCODE LANGUAGE SYNTAX v1.3.3**

### Command Structure
```ucode
[COMPONENT] <ACTION|METHOD> {PARAMETER} ~ comment
```

### Examples (with Optimized Types)
```ucode
[uCORE] <FILENAME|GENERATE> {uLOG} {System-Boot}      ~ Generate uHEX filename
[uCORE] <FILENAME|GENERATE> {uWORK} {Process-Doc}     ~ Generate workflow file
[uCORE] <FILENAME|GENERATE> {uBRIEF} {Team-Update}    ~ Generate briefing file
[uCORE] <FILENAME|DECODE> {4F2A8C15}                  ~ Decode uHEX metadata
[MEMORY] <STORE|DATA> {PROJECT-STATUS}                ~ Store project data
[PACKAGE] <INSTALL|SYSTEM> {SECURITY-TOOLS}          ~ Install security package
[STATUS] <CHECK|ALL>                                  ~ Check all system status
[WORKFLOW] <START|ASSIST>                             ~ Enter assist mode
[BRIEFING] <CREATE|NEW> {PROJECT-KICKOFF}             ~ Create new briefing
[TEMPLATE] <GENERATE> {uASSIST} {HELP-SESSION}        ~ Generate assist template
```

### Syntax Rules
- **Components**: [UPPERCASE] for system components
- **Actions**: <UPPERCASE|METHOD> for operations
- **Parameters**: {UPPERCASE-DASH} for data
- **Comments**: ~ description
- **Options**: Use PIPE | for multiple choices
- **Numbers**: Direct numeric values (no formatting)

### Component Categories
- **Core**: [uCORE], [MEMORY], [STATUS], [WORKFLOW]
- **Tools**: [PACKAGE], [SCRIPT], [BACKUP], [SECURITY]
- **User**: [ASSIST], [BRIEFING], [ROADMAP], [MISSION]
- **Roles**: [GHOST], [TOMB], [CRYPT], [DRONE], [KNIGHT], [IMP], [SORCERER], [WIZARD]

---

## 🎨 **BBC MODE 7 VISUAL DESIGN**

### Inspired by BBC BASIC Manual
Following the design principles from [BBC BASIC for Windows Manual](https://www.bbcbasic.co.uk/bbcwin/manual/bbcwinh.html), uDOS implements authentic Mode 7 teletext graphics with chunky block UI elements.

### BBC Mode 7 Color Palette (Vibrant Scheme)
```css
/* New uDOS Vibrant Color Palette */
--color-red: #ef4136        /* Vibrant Red (239,65,54) */
--color-orange: #f7941d     /* Vibrant Orange (247,148,29) */
--color-amber: #fbb040      /* Vibrant Amber (251,176,64) */
--color-yellow: #f9ed32     /* Vibrant Yellow (249,237,50) */
--color-blue: #00aeef       /* Vibrant Blue (0,174,239) */
--color-lime: #e9ff39       /* Vibrant Lime (233,255,57) */
--color-green: #8cff1f      /* Vibrant Green (140,255,31) */
--color-cyan: #00c6cc       /* Vibrant Cyan (0,198,204) */
--color-pink: #f08ed3       /* Vibrant Pink (240,142,211) */

/* Dark/Grey/Light variants for styling */
--color-black: #000000      /* Pure Black */
--color-dark-grey: #1a1a1a  /* Very Dark Grey */
--color-grey: #333333       /* Dark Grey */
--color-mid-grey: #666666   /* Medium Grey */
--color-light-grey: #999999 /* Light Grey */
--color-pale-grey: #cccccc  /* Pale Grey */
--color-white: #ffffff      /* Pure White */
```

### uDOS Professional Color Palette (Secondary)
```css
/* uDOS Professional Color Palette */
--udos-red: #ce4a4a        /* Muted Red - RGB(206,74,74) */
--udos-green: #48a56a      /* Forest Green - RGB(72,165,106) */
--udos-blue: #6688c3       /* Steel Blue - RGB(102,136,195) */
--udos-yellow: #eaaf41     /* Golden Yellow - RGB(234,175,65) */
--udos-purple: #b25da6     /* Soft Purple - RGB(178,93,166) */
--udos-cyan: #4a9fb8       /* Professional Cyan - RGB(74,159,184) */
--udos-orange: #d87538     /* Warm Orange - RGB(216,117,56) */
```

### Mode 7 Display Characteristics
- **Resolution**: 40×25 characters (320×200 pixels effective)
- **Font**: MODE7GX3 (authentic BBC Micro teletext)
- **Character Size**: 16×20 pixels per character
- **Block Graphics**: SAA5050 standard block characters
- **Background**: Text backgrounds using color codes

### Chunky Block Graphics Buttons
```html
<!-- BBC Mode 7 Button Structure -->
<button class="mode7-button">
    ▌█ BUTTON TEXT █▐<br>
    DESCRIPTION
</button>
```

### Button Color Variations
```css
.mode7-button         /* Green (default) */
.mode7-btn-blue       /* Blue for system functions */
.mode7-btn-red        /* Red for admin/critical */
.mode7-btn-magenta    /* Magenta for special functions */
.mode7-btn-cyan       /* Cyan for utilities */
```

### Block Character Set
- `█` - Full block (U+2588)
- `▌` - Left half block (U+258C)
- `▐` - Right half block (U+2590)
- `▀` - Upper half block (U+2580)
- `▄` - Lower half block (U+2584)
- `░` - Light shade (U+2591)
- `▒` - Medium shade (U+2592)
- `▓` - Dark shade (U+2593)

---

## 📐 **uDOS DISPLAY ETHOS v1.3.3 – 16×16 GRID**

### Quick Specs
- **uCELL**: 16×16 (square)
- **Text box**: default 12×12 (centred), can also be **14×14** or **10×10** depending on font/spacing needs
- **Baseline**: row 9 of 16
- **Block fills**: edge-to-edge (ignore buffer) → no gaps between tiles
- **Overlays**: optional high-detail 64×64 per uCELL (4× overlay grid)
- **Layers**: Light / Dark / Colour / Transparent (L/D/C/T)
- **Alignment**: monosort glyphs centred in the text box size chosen (10, 12, or 14)

### Core Display Sizes
Effective resolution = `(cols × 16) × (rows × 16)`.

| Grid (cols×rows) | Effective px | Device class             |
| ---------------- | ------------ | ------------------------ |
| 160×60           | 2560×960     | Wallboard                |
| 120×48           | 1920×768     | Large Dashboard          |
| 80×30            | 1280×480     | Standard Terminal (16:9) |
| 64×24            | 1024×384     | Small Screen (16:9)      |
| 48×20            | 768×320      | Tablet (4:3)             |
| 40×16            | 640×256      | Mobile (16:9)            |
| 32×24            | 512×384      | Compact 4:3              |
| 16×16            | 256×256      | Wearable (Square)        |

### Aspect Ratios
- **16:9** → 80×30, 64×24, 40×16
- **4:3** → 48×20, 32×24
- **Square** → 16×16
- **Ultrawide / Wallboard** → 160×60, 120×48

### Block Graphics & Shading
Use Unicode block characters for fills and shading:

- **░ Light** - Base shading
- **▒ Medium** - Mid-level fill
- **▓ Heavy** - Dark fill
- **█ Solid** - Full block
- **▀** upper half, **▄** lower half, **▌** left half, **▐** right half
- **▘ ▝ ▖ ▗** quarter blocks (TL/TR/BL/BR)

### 4× Overlay (64×64 effective)
Inside one 16×16 uCELL, enable a **4×4 overlay grid** for crisp icons or dithered fills.

---

## 🔤 **TYPOGRAPHY STANDARDS**

### Authentic BBC Mode 7 Fonts
```css
/* Primary: Authentic MODE7GX teletext fonts */
--font-mode7gx3: 'MODE7GX3', monospace;     /* Standard teletext */
--font-mode7gx0: 'MODE7GX0', monospace;     /* Square aspect */
--font-mode7gx2: 'MODE7GX2', monospace;     /* Alternative */
--font-mode7gx4: 'MODE7GX4', monospace;     /* Wide aspect */
```

### Bundled Pixel/Retro Fonts
- **MODE7GX0.TTF** (default teletext look)
- **pot_noodle.ttf** (retro/BBS)
- **Pet Me 64** (C64)
- **Perfect DOS VGA 437**
- **Pixel Operator**
- **DotGothic16**
- **GNU Unifont** (Unicode coverage)
- **Valova** (tile-based)

### System Monospace Fallbacks
- **macOS**: Menlo, SF Mono
- **Linux/Ubuntu**: Ubuntu Mono, DejaVu Sans Mono
- **Windows/Chrome**: Consolas, Courier New

### Capitalization Rules

#### ALL CAPS Usage
- **Commands**: STATUS, HELP, MEMORY, PACKAGE
- **File Types**: uSCRIPT, uLOG, uDATA, uDOC
- **Variables**: UDOS-USERNAME, CURRENT-MODE
- **Shortcodes**: [MEM|LIST], [PACK|INSTALL]
- **Technical Elements**: All system identifiers

#### Sentence Case Usage
- **Documentation text**: "Your memory stores all data"
- **User messages**: "Welcome to the system"
- **Descriptions**: "This command shows status"
- **Interface labels**: "Current status:", "Available options:"

#### Proper Case Usage
- **System Name**: "uDOS"
- **Component Names**: "Memory Vaults", "Command Center"
- **Technology Names**: "Markdown", "ASCII"

---

## 🏗️ **8-ROLE SYSTEM ARCHITECTURE**

### Role Hierarchy (v1.3.3)
1. **GHOST** - Minimal read-only access
2. **TOMB** - Basic storage with limited interaction
3. **CRYPT** - Secure storage with encryption capabilities
4. **DRONE** - Standard operational access
5. **KNIGHT** - Enhanced security and protection functions
6. **IMP** - Scripting and automation capabilities
7. **SORCERER** - Advanced system administration
8. **WIZARD** - Complete system access and development

### Role-Based File Access
- **System Files**: All roles can read documentation
- **User Files**: Role-specific access to uMEMORY content
- **Security Files**: CRYPT and KNIGHT roles for security operations
- **Development Files**: IMP, SORCERER, WIZARD for development
- **Admin Files**: SORCERER and WIZARD for system administration

### Role Integration in uHEX
The uHEX metadata encoding includes role information:
- **Role encoding**: 4 bits (0-15) in metadata
- **File location**: Role-specific directories in uMEMORY
- **Access control**: Automatic role-based file filtering

---

## 🎨 **UI DESIGN STANDARDS**

### Main Dashboard Grid
Based on BBC Mode 7 40×25 character layout:
- **3×3 Grid**: Primary module buttons
- **Center Layout**: 640×500 pixel viewport
- **Block Buttons**: Chunky teletext-style buttons

### Dashboard Categories
1. **uDOS Core Modules**
   - uCORE (System Core) - Green
   - uSERVER (Web Services) - Blue
   - uSCRIPT (Automation) - Magenta

2. **User Modes**
   - WIZARD (Development) - Cyan
   - SORCERER (Admin Tools) - Red
   - IMP (Scripting) - Green

3. **Special Functions**
   - uKNOWLEDGE (Docs & Help) - Blue
   - TEMPLATES (Generators) - Magenta
   - TERMINAL (Command Line) - Cyan

### UI Building Blocks

#### Button
```
┌────────────────────────────────┐
│        C O N T I N U E ▷       │
└────────────────────────────────┘
```

#### Input field
```
┌──────────────────────────────────┐
│  U s e r n a m e :  _ _ _ _ _    │
└──────────────────────────────────┘
```

#### Pill badge
```
╭───────────────────╮
│     O N L I N E   │
╰───────────────────╯
```

---

## 📋 **NAMING CONVENTIONS**

### 1. Variables
```bash
# Environment Variables (ALL CAPS with underscores)
UDOS-USERNAME
UDOS-LOCATION-CODE
UDOS-TIMEZONE-CODE
UDOS-MAP-NUMBER

# Script Variables (CAPS-DASH format)
CURRENT-USER
FILE-PATH
TIME-STAMP
LOCATION-CODE
```

### 2. Commands (uCODE)
```ucode
[STATUS]                                    ~ Check system status
[MEMORY] <LIST|ALL>                        ~ List all memory items
[PACKAGE] <INSTALL|SECURITY>               ~ Install security package
[RESTART]                                  ~ Restart system
[DASH] <LIVE>                             ~ Start live dashboard
[CONFIG] <SET> {PARAMETER} {VALUE}        ~ Set configuration
```

### 3. Shortcodes
```bash
# Format: [TYPE|ACTION]
[MEM|LIST]
[PACK|INSTALL]
[DASH|LIVE]
[CONFIG|SET]
[MAP|CREATE]
[LOG|VIEW]
```

### 4. Directory Names
```
uCORE/
uMEMORY/
uKNOWLEDGE/
uDOS-EXTENSION/
```

### 5. System File Standards (Non-uHEX)

**Scripts and Executables**:
- **Format**: `kebab-case.sh`
- **Examples**: `cleanup-filenames.sh`, `start-vscode-dev.sh`, `backup-umemory.sh`

**Configuration Files**:
- **Format**: `kebab-case.json` or `kebab-case.conf`
- **Examples**: `template-system-config.json`, `current-role.conf`

**Data Files**:
- **Format**: `camelCase.json` for structured data
- **Examples**: `locationMap.json`, `timezoneMap.json`

---

## 🎨 **COLOR CODING STANDARDS**

### Command Line Interface
```bash
# Commands (YELLOW)
STATUS, HELP, MEMORY, PACKAGE

# Shortcodes (CYAN brackets, YELLOW content)
[MEM|LIST], [PACK|INSTALL], [DASH|LIVE]

# Variables (GREEN)
UDOS-USERNAME, CURRENT-MODE, UDOS-VERSION

# File paths (BLUE)
/Users/username/uDOS/uMEMORY/

# Success (GREEN)
✅ Operation completed successfully

# Warning (YELLOW)
⚠️ This action requires confirmation

# Error (RED)
❌ Command not found

# Info (CYAN)
ℹ️ Helpful information
```

### 8×8 Color Palette Integration
The 8×8 color palette system provides comprehensive color choices:

1. **Classic Vintage Rainbow** - For retro interfaces
2. **Neo Retro Neon** - For 80s arcade themes
3. **Cyberpunk Dusk** - For dark, high-contrast themes
4. **Earth & Nature** - For organic, natural themes
5. **Desert & Sun** - For warm, earthy themes
6. **Oceanic Blues** - For cool, aquatic themes
7. **Pastel Dream** - For soft, gentle themes
8. **Neutral Core** - For UI foundations and accessibility

---

## 🔧 **uCORE INTEGRATION**

### Filename Generation
```ucode
[uCORE] <FILENAME|GENERATE> {uLOG} {System-Boot}    ~ Generate uHEX filename
[uCORE] <FILENAME|DECODE> {4F2A8C15}                ~ Decode uHEX metadata
[uCORE] <FILENAME|LIST> {PREFIX} {uLOG}             ~ List all LOG files
[uCORE] <FILENAME|SORT> {CHRONOLOGICAL}             ~ Sort by timestamps
[uCORE] <FILENAME|VALIDATE> {FILENAME}              ~ Check format
```

### System Integration Commands
```ucode
[uCORE] <BACKUP|CREATE> {FULL-SYSTEM}              ~ Create system backup
[uCORE] <BACKUP|RESTORE> {BACKUP-ID}               ~ Restore from backup
[uCORE] <STATUS|CHECK> {ALL-SYSTEMS}               ~ Check all systems
[uCORE] <TREE|GENERATE>                            ~ Generate system tree
```

### Template System Commands
```ucode
[TEMPLATE] <CREATE> {TYPE} {NAME}                   ~ Create new template
[TEMPLATE] <LIST> {CATEGORY}                       ~ List templates
[TEMPLATE] <APPLY> {NAME} {TARGET}                 ~ Apply template
[TEMPLATE] <VALIDATE> {TEMPLATE}                   ~ Validate template
```

---

## 📊 **IMPLEMENTATION TOOLS**

### Filename Generator Function
```bash
generate_udos_filename() {
    local file_type="$1"        # uLOG, uDOC, etc.
    local description="$2"      # Max 20 characters
    local role="$3"             # Optional role context

    local uhex_code=$(generate_uhex_timestamp "$role")

    echo "u${file_type}-${uhex_code}-${description}.md"
}

# Usage examples
generate_udos_filename "LOG" "System-Boot" "wizard"
# Output: uLOG-4F2A8C15-System-Boot.md

generate_udos_filename "DOC" "User-Guide" "sorcerer"
# Output: uDOC-4F2A8C20-User-Guide.md
```

### uHEX Decoder
```bash
decode_uhex() {
    local uhex_code="$1"

    # Decode 8-character hex to metadata
    echo "Decoding uHEX: $uhex_code"
    echo "Date: $(decode_date_from_hex "$uhex_code")"
    echo "Time: $(decode_time_from_hex "$uhex_code")"
    echo "Role: $(decode_role_from_hex "$uhex_code")"
    echo "Timezone: $(decode_timezone_from_hex "$uhex_code")"
}
```

### Color Palette Generator
```bash
generate_color_palette() {
    local palette_name="$1"
    local output_format="$2"    # css, json, html

    case "$palette_name" in
        "mode7") generate_mode7_palette "$output_format" ;;
        "vibrant") generate_vibrant_palette "$output_format" ;;
        "professional") generate_professional_palette "$output_format" ;;
        *) echo "Unknown palette: $palette_name" ;;
    esac
}
```

---

## 🚀 **TEMPLATE SYSTEM INTEGRATION**

### Template Categories
1. **Documentation Templates**
   - User guides
   - Technical specifications
   - API documentation
   - Style guides

2. **Development Templates**
   - Project structure
   - Script templates
   - Configuration files
   - Test suites

3. **UI Templates**
   - Mode 7 interfaces
   - Dashboard layouts
   - Color schemes
   - Component libraries

### Template Generation Commands
```ucode
[TEMPLATE] <GENERATE> {STYLE-GUIDE} {PROJECT-NAME}   ~ Generate style guide
[TEMPLATE] <GENERATE> {DASHBOARD} {LAYOUT-TYPE}      ~ Generate dashboard
[TEMPLATE] <GENERATE> {COLOR-SCHEME} {PALETTE}       ~ Generate colors
[TEMPLATE] <GENERATE> {DOCUMENTATION} {DOC-TYPE}     ~ Generate docs
```

---

## ✅ **VALIDATION CHECKLIST**

### File Naming Compliance
- [ ] File type prefix uses uTYPE format
- [ ] uHEX code is 8 characters (or YYYYMMDD for dev)
- [ ] Description is 20 characters or less
- [ ] File extension is .md
- [ ] No lowercase letters in technical elements
- [ ] Role encoding present in metadata

### Visual Design Compliance
- [ ] Mode 7 color palette used
- [ ] Block graphics for UI elements
- [ ] 16×16 grid system followed
- [ ] Authentic teletext fonts implemented
- [ ] Chunky button design applied

### uCODE Syntax Compliance
- [ ] Commands use [COMPONENT] <ACTION|METHOD> format
- [ ] Parameters use {PARAMETER} format
- [ ] Comments use ~ format
- [ ] All technical elements in CAPITALS
- [ ] Proper PIPE | usage for options

### System Integration
- [ ] uCORE commands functional
- [ ] 8-role system integrated
- [ ] Backup system compatible
- [ ] Template system accessible
- [ ] Color palette system implemented

---

## 🔗 **RELATED DOCUMENTATION**

### Core References
- **[uHEX Filename Convention](./Filename-Convention.md)** - Complete filename system
- **[User Role Capabilities](./User-Role-Capabilities.md)** - 8-role system documentation
- **[uDATA Format Specification](../uDATA-Format-Specification-v1.3.3.md)** - Data format standards
- **[Template Standard](../reference/Template-Standard.md)** - Template system documentation

### Visual Design References
- **[uDOS Palettes](../uDOS-palettes.html)** - Interactive color palette viewer
- **[Display Ethos](../u_dos_16_16_grid_reference_fonts_blocks_overlays_markdown.md)** - 16×16 grid system
- **[BBC BASIC Manual](https://www.bbcbasic.co.uk/bbcwin/manual/bbcwinh.html)** - Mode 7 inspiration

### Implementation Guides
- **User Guides**: Complete implementation documentation
- **Technical Specifications**: System architecture and integration
- **Legacy Documentation**: Historical reference materials

---

## 📈 **SYSTEM STATUS & HEALTH (v1.3.3 - Filename Convention v7.0)**

### Implementation Metrics v7.0
- **uHEX adoption**: 85+ files converted to v7.0 format with 8-character types
- **8-character types**: Extended descriptive prefixes implemented (uWORKFLW, uBRIEFNG, uASSIST)
- **Role system**: Complete 8-tier implementation with filename integration
- **uCORE integration**: Full filename management active with v7.0 support
- **Template system**: Complete template generation with 8-character type support
- **Color system**: 8×8 palette implementation
- **Visual design**: Mode 7 components implemented
- **Metadata encoding**: Complete uHEX timestamp and role integration

### v7.0 Enhancements
- **Optimized type clarity**: uWORK, uBRIEF, uTEMP for enhanced readability and efficiency
- **Character optimization**: Balanced 5-7 character max with 20-character descriptions
- **Backward compatibility**: Maintains support for existing shorter types (uLOG, uDOC)
- **Enhanced tooling**: Updated generation and validation tools for optimized types
- **uDATA integration**: Complete JSON data format specification with minified processing

### System Health Indicators
- **Core integrity**: ✅ All critical systems operational
- **8-role system**: ✅ Complete hierarchy implemented
- **Documentation**: ✅ Comprehensive guides available
- **Security model**: ✅ Role-based access controls active
- **Visual consistency**: ✅ Mode 7 design standards applied
- **Template system**: ✅ Generation and validation active

---

## 🛠️ **MIGRATION & SUPPORT**

### Migration from Previous Versions
```bash
# Automated migration script
./uCORE/scripts/migrate-to-v1.3.3.sh

# Manual validation
./uCORE/scripts/validate-style-compliance.sh

# Color palette migration
./uCORE/scripts/update-color-schemes.sh
```

### Support Resources
- **Template Generation**: Automated style guide creation
- **Color Picker**: Interactive palette selection
- **Validation Tools**: Format and compliance checking
- **Migration Scripts**: Automated conversion tools

---

**STATUS**: ACTIVE v1.3.3 (Filename Convention v7.0 + uDATA Integration)
**ENFORCEMENT**: All new files must comply with v7.0 optimized type standards
**INTEGRATION**: Complete uCORE, template, color system, and uDATA format integration
**SUPPORT**: Contact wizard for implementation assistance

---

*uDOS v1.3.3 Comprehensive Style Guide*
*BBC Mode 7 Design • uHEX v7.0 (Optimized Types) • uDATA JSON Format • 8-Role System • Complete Integration*
*Precision Through Standardization*
