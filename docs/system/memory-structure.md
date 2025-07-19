# uMemory Structure Documentation

## 🔐 Security Level 1: Private User Files

The `uMemory/` directory contains all private user data and is **NEVER included in the repository**. It is created locally during installation and managed by the user.

### Directory Structure

```
uMemory/
├── user/           # User-specific configurations and settings
├── sandbox/        # Development and testing environments
├── state/          # System state and session data
├── logs/           # System and user activity logs
├── missions/       # User-created mission files
├── moves/          # User-created move files
├── milestones/     # User progress tracking
├── scripts/        # User-created automation scripts
├── templates/      # User-customized templates
└── generated/      # Auto-generated content and exports
```

### Data Sovereignty Levels

Within uMemory, users can organize data into two sharding options:

#### a) **explicit** (default)
- Private, user-controlled data
- Never shared or synchronized
- Maximum privacy protection

#### b) **public** 
- User chooses to make content shareable
- Explicit opt-in for collaboration
- User maintains control

### Installation Behavior

1. **Fresh Installation**: Creates empty uMemory structure
2. **Wizard Setup**: Initializes with default templates and config
3. **User Provisioning**: Each user role gets appropriate access patterns

### Privacy Protection

- ✅ Excluded from git tracking
- ✅ Local filesystem permissions enforced
- ✅ No automatic cloud sync
- ✅ User controls all sharing decisions
- ✅ Encryption option available (future feature)

### Access by User Role

- **wizard**: Full read/write access to all uMemory
- **sorcerer**: Read/write access to sandbox/, scripts/, templates/
- **ghost**: Read-only access to public/ subdirectories only
- **imp**: No direct access, operates through guided interfaces

---

*This directory is created automatically during uDOS installation and populated based on user role and preferences.*
