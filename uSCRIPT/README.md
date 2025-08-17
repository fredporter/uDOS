# 🔧 uScript - Development Script Manager v2.0

**uScript** is now a development script management system for executing one-off cleanup, migration, and development scripts in a safe sandbox environment.

## 🎯 Purpose

- **Development Scripts**: Manage one-off cleanup and maintenance scripts
- **Sandbox Execution**: Scripts run safely in the user sandbox
- **Auto-cleanup**: Executed scripts moved to archive, then trash
- **Development Mode**: Integration with uDev environment

## 📁 Directory Structure

```
uScript/
├── uscript.sh           # Main script manager
├── active/              # Active scripts ready to run
├── executed/            # Recently executed scripts (archive)
├── templates/           # Script templates
└── logs/                # Execution logs

uMemory/sandbox/scripts/ # Temporary execution location
uDev/logs/scripts/       # System execution logs
```

## 🚀 Usage

### Basic Commands

```bash
# Show help
./uScript/uscript.sh help

# Create new script
./uScript/uscript.sh create cleanup-logs

# List all scripts  
./uScript/uscript.sh list

# Run script in sandbox
./uScript/uscript.sh run cleanup-logs

# Show system status
./uScript/uscript.sh status
```

### Development Commands

```bash
# Install script from uCode/
./uScript/uscript.sh install cleanup-uknowledge.sh

# Create from template
./uScript/uscript.sh template cleanup my-cleanup
./uScript/uscript.sh template migration data-migration
./uScript/uscript.sh template validation system-check

# Clean up executed scripts
./uScript/uscript.sh clean
```

## 🔄 Script Lifecycle

1. **Create/Install**: Script created in `active/` directory
2. **Edit**: Optional editing in VS Code
3. **Execute**: Script copied to sandbox, executed safely
4. **Archive**: Successful script moved to `executed/`  
5. **Cleanup**: Archive moved to trash, sandbox cleaned

## 📝 Script Templates

### Cleanup Template
- File/directory reorganization
- Reference updates
- Validation checks
- Summary reporting

### Migration Template  
- Data migration scripts
- System updates
- Legacy cleanup
- Verification steps

### Validation Template
- System validation
- Health checks
- Configuration validation
- Report generation

## 🛡️ Safety Features

- **Sandbox Execution**: Scripts run in isolated sandbox
- **Backup Integration**: Automatic logging and history
- **Error Handling**: Proper error reporting and rollback
- **Development Mode**: Integration with uDev logging

## 🎯 Use Cases

1. **System Cleanup**: Reorganize directories and files
2. **Migration Scripts**: Move data between locations
3. **Validation Scripts**: Check system integrity  
4. **One-off Tasks**: Temporary development scripts
5. **Maintenance**: System cleanup and optimization

## 🔧 Integration

- **uCode Integration**: Install scripts from uCode directory
- **uDev Logging**: Execution logged to development environment
- **Sandbox Safety**: User data protected in sandbox
- **Template System**: Pre-built script patterns
- **VS Code**: Automatic editor integration

---

**Version 2.0** - Redesigned for development script management and sandbox execution

