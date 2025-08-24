# uDOS v1.4.0 Changelog
## Released: August 25, 2025

### 🎯 **Major System Reorganization**

#### ✅ **Logging System Consolidation**
- **Centralized Location**: All system logs moved to `/uMEMORY/system/logs/`
- **Data Separation**: User/session data properly separated from system code
- **Log Migration**: 
  - `uMEMORY/role/wizard/logs` → `uMEMORY/system/logs/uMEMORY-role-wizard-logs`
  - `uMEMORY/user/sandbox/logs` → `uMEMORY/system/logs/uMEMORY-user-sandbox-logs`
  - `uNETWORK/wizard/logs` → `uMEMORY/system/logs/uNETWORK-wizard-logs`
  - `uSCRIPT/runtime/logs` → `uMEMORY/system/logs/uSCRIPT-runtime-logs`
- **Backward Compatibility**: Symlink `uMEMORY/logs` → `system/logs`

#### ✅ **System Architecture Improvements**
- **uCORE/**: Now contains only system code (no user data)
- **uMEMORY/**: Properly houses all user data, session information, and logs
- **sandbox/**: Consolidated single user workspace (removed duplicate dev/sandbox)
- **dev/**: Clean development framework with proper guidelines

#### ✅ **Git Repository Health**
- **Removed Development Bloat**: 21MB venv directory removed from tracking
- **Enhanced .gitignore**: Comprehensive exclusions for development environments
- **Clean Distribution**: Proper separation of system code vs user/development data
- **Repository Size**: Maintained clean repository structure

#### ✅ **Development Framework**
- **Guidelines Document**: `/dev/DEVELOPMENT-GUIDELINES-v1.4.md`
- **Data Separation Principles**: Clear rules for system vs user data
- **Directory Organization**: Documented structure and usage patterns
- **Development Best Practices**: Established for future v1.4+ development

### 🔧 **Technical Improvements**

#### **Error Handling**
- Updated `uCORE/system/error-handler.sh` to use new log locations
- Consistent error logging across all system components

#### **System Scripts**
- All integration scripts updated for new log paths
- Backup system respects new directory organization
- Cleanup scripts enhanced for v1.4 structure

#### **Documentation**
- Updated README.md with v1.4 improvements
- Enhanced development guidelines
- Clear separation of concerns documented

### 🚀 **Previous v1.4 Features** *(maintained)*

#### **Three-Mode Display System**
- CLI Terminal (always available)
- Desktop Application (DRONE+ roles)
- Web Export (remote access)
- Role-based access control

#### **Protected DEV Environment**
- Core development workspace protection
- Wizard + DEV mode access control
- Persistent protection (never flushed)

#### **Flushable Sandbox System**
- User workspace for experimentation
- Session management and archiving
- Clean reset capabilities

#### **Memory Archive System**
- Persistent storage in uMEMORY/
- Role-based memory isolation
- Automatic session archiving

### 🐛 **Bug Fixes**
- Fixed logging placement issues (user data in system directories)
- Resolved git repository bloat from development environments
- Cleaned up duplicate sandbox directories
- Corrected symlink structures for backward compatibility

### 🛠️ **Breaking Changes**
- Log file locations moved (symlinks provide compatibility)
- Development environment structure reorganized
- Git tracking exclusions enhanced (affects development workflows)

### 📋 **Migration Notes**
- Existing scripts using log paths will continue working via symlinks
- Development environments should be recreated after git clone
- Personal development data now properly excluded from git tracking

### 🎯 **Next Steps for v1.5**
- Complete UI implementation for three-mode display system
- Enhanced role-based access controls
- Advanced memory archiving features
- Performance optimizations based on v1.4 clean architecture

---

**Full Version**: 1.4.0  
**Build Date**: 2025-08-25  
**Compatibility**: macOS 10.15+, Python 3.8+, Node.js 16+, Rust  
**Architecture**: Universal (CLI/Desktop/Web) + Cross-Platform
