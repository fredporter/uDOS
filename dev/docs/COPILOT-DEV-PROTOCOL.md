# uDOS Development Session Protocol v1.0.5.3
# GitHub Copilot Development Instructions

## 🎯 **Consistent Development Round Protocol**

### **📋 Pre-Development Round Checklist:**
1. **Review current session status** via `./udos build testing`
2. **Check integration layer** via `./udos demo integration` 
3. **Verify bash 3.x compatibility** for all new code
4. **Confirm directory structure compliance** (scripts in `dev/scripts/`)

### **🔄 During Development Round:**
1. **Implement features incrementally** with frequent testing
2. **Use centralized logging** via uCORE foundation
3. **Follow uDOS modular architecture** (uCORE, uMEMORY, uKNOWLEDGE, uNETWORK, uSCRIPT)
4. **Test integration** after each significant change

### **✅ Post-Development Round Protocol:**
1. **Clean up duplicate/rogue scripts** to `dev/backups/legacy/`
2. **Update version documentation** in relevant modules
3. **Run full integration test** via `./udos demo integration`
4. **Git commit with session identifier** (e.g., "v1.0.5.3 - Memory & Knowledge Integration")
5. **Git push to preserve session state**

### **🚨 Critical Requirements:**
- **Bash 3.x Compatibility**: No associative arrays, no +=, use compatible parameter expansion
- **Directory Structure**: All development scripts in `dev/scripts/`, no root clutter
- **Centralized Backups**: All backups in `dev/backups/` with proper categorization
- **Integration Testing**: Every round must pass integration tests
- **Version Tracking**: Each round increments version (v1.0.5.x)

### **📁 Standard Directory Compliance:**
```
uDOS/
├── udos                    # Main launcher only
├── dev/
│   ├── scripts/           # All development scripts
│   ├── backups/           # Centralized backup system
│   └── docs/              # Development documentation
├── uCORE/                 # Core foundation system
├── uMEMORY/               # Data persistence layer
├── uKNOWLEDGE/            # Knowledge graph system
├── uNETWORK/              # Network services
└── uSCRIPT/               # Script environment
```

### **🔧 Express Development Session Template:**
1. **v1.0.5.x - [Feature Name]**
2. **Implement core functionality** with bash 3.x compatibility
3. **Create integration points** with existing modules
4. **Add comprehensive testing** and error handling
5. **Update documentation** and version numbers
6. **Clean up and consolidate** before git push

### **🎯 Testing Standards:**
- **Unit Testing**: Each module function tested independently
- **Integration Testing**: Cross-module communication verified
- **Compatibility Testing**: Bash 3.x compliance confirmed
- **Structure Testing**: Directory organization validated

### **📊 Success Metrics:**
- ✅ `./udos build testing` passes without errors
- ✅ `./udos demo integration` demonstrates full functionality
- ✅ No scattered scripts outside `dev/scripts/`
- ✅ All backups centralized in `dev/backups/`
- ✅ Git history clean with session-based commits

## 🚀 **Current Development State: v1.0.5.3**
- **Core Foundation**: Complete with bash 3.x compatibility
- **Memory System**: JSON-based persistence with CRUD operations
- **Knowledge System**: Graph database with relationships
- **Integration Layer**: Unified API connecting all modules
- **Directory Structure**: Clean and compliant
- **Backup System**: Centralized and managed

## 🎯 **Next Development Target: v1.0.5.4**
- **Network Layer Foundation**: Service discovery, communication protocols
- **API Gateway**: Unified external interface
- **Service Registry**: Dynamic service management
- **Health Monitoring**: System status and diagnostics
