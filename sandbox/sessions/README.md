# Sandbox Sessions - Archive Provisions

## Overview
This directory manages session data flow and archiving provisions for the uDOS flushable sandbox system.

## Structure
```
sessions/
├── README.md           # This file
├── current/            # Active session data (FLUSHABLE)
├── archive/            # Session data ready for archiving (FLUSHABLE)
└── .session-rules      # Session archiving rules (future implementation)
```

## Session Lifecycle (Future Implementation)

### 1. Session Start
- Create session ID and metadata
- Initialize `/sessions/current/` with session data
- Begin logging session activity

### 2. Session Active
- All session data flows to `/sessions/current/`
- Continuous logging and data capture
- Session state maintained in current directory

### 3. Session End (Pre-Archive)
- Move valuable data from `/sessions/current/` to `/sessions/archive/`
- Apply session rules to determine what gets archived
- Prepare data for transfer to `/uMEMORY/`

### 4. Archive Transfer (Pre-Flush)
- Role-specific data → `/uMEMORY/role/{current_role}/`
- User-specific data → `/uMEMORY/user/`
- System data → `/uMEMORY/system/` (if applicable)

### 5. Sandbox Flush
- Clear entire `/sandbox/` directory
- Session data safely preserved in `/uMEMORY/`
- Fresh sandbox ready for next session

## Archive Rules (Future Development)
Session rules will determine:
- What data gets archived vs discarded
- Role-specific vs user-specific classification
- Data retention policies
- Archive organization patterns

## Data Flow Protection
```
[Live Session] → /sandbox/sessions/current/
[Session End] → /sandbox/sessions/archive/
[Apply Rules] → /uMEMORY/role/ or /uMEMORY/user/
[Sandbox Flush] → Clear /sandbox/ (memory preserved)
```

---
**Note:** This directory is FLUSHABLE and excluded from GitHub sync.
All permanent data is archived to uMEMORY before sandbox clearing.
