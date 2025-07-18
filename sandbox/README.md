# 🏖️ uDOS Sandbox v1.0 - Daily Working Space

**Purpose**: Daily working folder for user data organization and session management.

## 🎯 Sandbox Concept

The sandbox serves as your **daily working folder** and implements the core uDOS principle of keeping user data separate and organized per daily session.

## 📁 Sandbox Structure

```
sandbox/
├── README.md           # This file
├── today/              # Current session workspace
├── sessions/           # Historical daily sessions
├── temp/               # Temporary files (auto-cleanup)
├── drafts/             # Work in progress
└── finalized/          # Ready for uMemory storage
```

## ⚡ Daily Session Workflow

### 1. **Start Daily Session**
```bash
./uCode/ucode.sh SANDBOX START
```
- Creates new `today/YYYY-MM-DD/` folder
- Sets up session templates
- Initializes working environment

### 2. **Work in Sandbox**
```bash
./uCode/ucode.sh EDIT myproject.md
./uCode/ucode.sh CREATE notes
./uCode/ucode.sh DRAFT idea.txt
```
- All work happens in `today/` folder
- Files follow uDOS naming conventions
- No complex folder structures needed

### 3. **Finalize Session**
```bash
./uCode/ucode.sh SANDBOX FINALIZE
```
- Moves completed work to `finalized/`
- Archives session to `sessions/`
- Stores important files in uMemory
- Cleans up temporary files

## 🔄 Integration with uMemory

```
Daily Workflow:
sandbox/today/ → sandbox/finalized/ → uMemory/archive/
```

- **sandbox/today/**: Current active work
- **sandbox/finalized/**: Ready for permanent storage  
- **uMemory/archive/**: Long-term storage and legacy

## 🛡️ User Data Separation

The sandbox maintains strict separation:
- ✅ **Personal data** stays in sandbox/
- ✅ **System data** stays in uCode/, uTemplate/
- ✅ **Knowledge** stays in uKnowledge/
- ✅ **Memory** stays in uMemory/

## 🎮 Access by User Role

| Role | Sandbox Access |
|------|----------------|
| **👑 Wizard** | Full read/write to all sandbox areas |
| **🧙 Sorcerer** | Read/write to today/, drafts/, temp/ |
| **👻 Ghost** | Read/write to today/, read-only archives |
| **😈 Imp** | today/ folder only |

## 🔧 uCode Commands

```bash
SANDBOX START              # Start new daily session
SANDBOX FINALIZE           # Finalize current session  
SANDBOX CLEAN              # Clean temporary files
SANDBOX LIST               # List sandbox contents
SANDBOX ARCHIVE            # Archive old sessions
SANDBOX STATUS             # Show current session info
```

## 📅 Session Management

Sessions are automatically organized by date:
```
sessions/
├── 2025-07-18/           # Previous sessions
├── 2025-07-17/
└── 2025-07-16/

today/                    # Current session
├── notes.md
├── project-draft.md
└── temp-calculations.txt
```

*Sandbox follows uDOS filename conventions - users don't need to create folder structures manually.*
