# uDOS User File Standards v1.2
**Standardized user file formats, naming conventions, and location verification**  
**Location**: [10-50-05] uCORE/docs/uDOS-User-File-Standard.md

## 📋 Overview

This document establishes comprehensive standards for user files, including naming conventions, format limits, location verification, and tile addressing systems within the uDOS ecosystem.

## 📝 File Type Standards

### Natural Language Files
```
Format: descriptive-name.md
Purpose: Documentation, notes, plans, journals
Content: Pure markdown, no code blocks
Line Limit: 80 characters maximum
Examples:
- daily-journal.md
- project-notes.md
- meeting-summary.md
- research-findings.md
```

### Code Files  
```
Format: CODE-YYYY-MM-DD-HHMM-TILE.md
Purpose: uCode scripts, uScript procedures, executable content
Content: Code blocks with markdown documentation
Line Limit: 80 characters maximum
Examples:
- CODE-2025-08-16-1430-NYC001.md
- CODE-2025-08-16-1445-LON023.md
- CODE-2025-08-16-1500-SYD456.md
```

## 🗺️ Location Verification System

### Tile Address Format
```
Format: [CITY][NNN]
- CITY: 3-letter city code (IATA-based)
- NNN: 3-digit precision tile (001-999)

Examples:
NYC001 - New York City, Manhattan central
LON023 - London, central business district  
SYD456 - Sydney, harbor area
LAX789 - Los Angeles, downtown
CHI234 - Chicago, loop district
```

### Timezone-Based Detection
```bash
# Automatic tile detection based on system timezone
America/New_York     -> NYC001
Europe/London        -> LON001
Australia/Sydney     -> SYD001
America/Los_Angeles  -> LAX001
America/Chicago      -> CHI001
Europe/Paris         -> CDG001
Asia/Tokyo           -> NRT001
```

### Location Verification Process
1. **System Detection**: Read system timezone
2. **City Mapping**: Map timezone to nearest major city
3. **Tile Assignment**: Default to 001, allow user selection
4. **User Confirmation**: Verify location at setup/reboot
5. **City Override**: User can select from city dataset

## 📐 Format Limits

### Document Standards
```
Line Width: 80 characters maximum
Reason: Terminal compatibility, readable columns
Enforcement: Automatic line wrapping at 80 chars
Validation: Pre-save line length checking
```

### Column View Standards  
```
Column Width: 10 characters per column
Purpose: Structured data display, dashboard views
Usage: Status displays, menu systems, data tables
Example:
┌──────────┬──────────┬──────────┬──────────┐
│   Col1   │   Col2   │   Col3   │   Col4   │
├──────────┼──────────┼──────────┼──────────┤
│ Data1234 │ Info5678 │ Status90 │ Value123 │
└──────────┴──────────┴──────────┴──────────┘
```

### Shortcode Format
```
Length: 8 characters maximum (excluding brackets)
Format: [SHORTCDE] or [SHORT01] or [ABCD1234]
Reason: Fits in 10-character column with brackets
Stacking: Allows vertical arrangement in columns

Examples:
[BACKUP01] - 8 chars + 2 brackets = 10 total
[DEPLOY]   - 6 chars + 2 brackets = 8 total  
[TEST123]  - 7 chars + 2 brackets = 9 total

Column Stacking:
┌──────────┐
│[BACKUP01]│
│[DEPLOY]  │
│[TEST123] │
│[STATUS]  │
└──────────┘
```

## 📊 Logging Standards

### Daily Move Log Format
```
Entry Format: HH:MM [TILE] ACTION (length check)
Maximum: 80 characters per entry
Overflow: Link to individual MOVELOG file

Examples:
14:30 [NYC001] User login successful
14:31 [NYC001] Started project review -> MOVELOG-001
14:35 [NYC001] Backup completed (12 files)
```

### MOVELOG Overflow System
```
Trigger: Any input/output exceeding 80 characters
Action: Create individual MOVELOG file in uMEMORY
Format: MOVELOG-NNN-YYYY-MM-DD-HHMM.md
Reference: Link in daily log

Example Daily Log Entry:
14:31 [NYC001] Complex analysis started -> MOVELOG-001-2025-08-16-1431

MOVELOG File Content:
# MOVELOG-001-2025-08-16-1431
**Time**: 14:31  
**Tile**: NYC001  
**Action**: Complex data analysis of quarterly reports

## Input
[Long detailed input content that exceeded 80 characters...]

## Output  
[Detailed results and analysis that exceeded limits...]

## Summary
Generated comprehensive quarterly analysis report with 47 data points
```

## 🏗️ Implementation Components

### Location Detection Script
```bash
# Location: [20-70-01] uMEMORY/scripts/detect-location.sh
# Purpose: Automatic timezone-based location detection
# Output: TILE address for current session
```

### File Validator
```bash
# Location: [20-70-02] uMEMORY/scripts/validate-files.sh  
# Purpose: Check file format compliance
# Validation: Line lengths, naming conventions, content types
```

### MOVELOG Manager
```bash
# Location: [20-70-03] uMEMORY/scripts/movelog-manager.sh
# Purpose: Handle overflow logging system
# Function: Create, link, and manage MOVELOG files
```

### City Dataset
```json
# Location: [20-40-01] uMEMORY/datasets/cities.json
# Purpose: Available cities for tile selection
# Format: IATA codes with timezone mappings
```

## ⚙️ Setup and Reboot Verification

### Setup Process
1. **Timezone Detection**: Read system timezone
2. **City Mapping**: Map to nearest city code
3. **User Verification**: Confirm or select different city
4. **Tile Assignment**: Default 001 or user selection
5. **Configuration Save**: Store in user identity

### Reboot Verification
1. **Load Saved Location**: Read from user identity
2. **Timezone Check**: Compare with current system timezone  
3. **Change Detection**: Alert if timezone changed
4. **Location Update**: Offer to update tile if needed
5. **Session Start**: Begin with verified location

### User Identity Integration
```markdown
# Location: [20-10-01] uMEMORY/configs/identity.md
# Additional fields for location tracking

## Location Information
- **Current Tile**: NYC001
- **Timezone**: America/New_York
- **Last Verified**: 2025-08-16 14:30
- **Auto-Update**: enabled
- **Backup Tiles**: LON001, SYD001
```

## 📋 File Naming Examples

### Natural Language Files
```
daily-journal-2025-08-16.md
project-alpha-requirements.md
team-meeting-notes.md
research-blockchain-summary.md
personal-goals-quarterly.md
```

### Code Files with Location
```
CODE-2025-08-16-1430-NYC001.md    # Script created in NYC at 2:30 PM
CODE-2025-08-16-1445-NYC001.md    # Follow-up script 15 minutes later
CODE-2025-08-16-0800-LON001.md    # Morning script from London
CODE-2025-08-16-2200-SYD001.md    # Evening script from Sydney
```

### MOVELOG Files
```
MOVELOG-001-2025-08-16-1431.md    # First overflow of the day
MOVELOG-002-2025-08-16-1502.md    # Second overflow  
MOVELOG-003-2025-08-16-1634.md    # Third overflow
```

## ✅ Validation Rules

### File Creation Checks
- [ ] Filename follows standard pattern
- [ ] Content type matches filename pattern
- [ ] Line lengths within 80 character limit
- [ ] Location tile is valid
- [ ] Timestamp is current and accurate

### Content Validation
- [ ] Natural language files contain no code blocks
- [ ] Code files properly document executable content
- [ ] Shortcodes are 8 characters or less
- [ ] Column data fits 10-character width
- [ ] Log entries under 80 characters

### Location Verification  
- [ ] System timezone detected correctly
- [ ] City mapping is accurate
- [ ] User confirmed location
- [ ] Tile address is valid format
- [ ] Configuration saved properly

This standard ensures consistent, location-aware file management with proper format limits and overflow handling for optimal uDOS operation.
