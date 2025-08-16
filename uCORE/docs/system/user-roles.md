# uDOS Mystical Role System v2.2 - 5-Tier Hierarchy

## 🎭 Enhanced Role Hierarchy Overview

The uDOS system now operates with a comprehensive 5-tier mystical role hierarchy:

### 🧙‍♂️ Wizard (Level 100/100)
- **Master Administrator** with full system access and server-like powers
- **Dev Mode Access**: Can enable/disable dev mode for system folder write access
- **Package & Extension Access**: Full read/write access to package and extension folders (in dev mode)
- **User Management**: Can spawn and manage other users
- **System Control**: Full access to all uDOS components

**Folder Access**:
- ✅ sandbox: full
- ✅ uMemory: full  
- ✅ uKnowledge: full
- 🔧 uTemplate: conditional_dev (write access in dev mode)
- 🔧 uCode: conditional_dev (write access in dev mode)
- 🔧 uScript: conditional_dev (write access in dev mode)
- 🔧 **package**: conditional_dev (write access in dev mode)
- 🔧 **extension**: conditional_dev (write access in dev mode)
- ✅ docs: full

### 🔮 Sorcerer (Level 75/100) 
- **Magical Practitioner** with elevated powers and limited system access
- **No Dev Mode**: Cannot access system folders in write mode
- **Administrative Tasks**: Limited admin capabilities
- **Project Management**: Can manage projects and user content

**Folder Access**:
- ✅ sandbox: full
- 🟡 uMemory: read_write_limited
- 🔵 uKnowledge: read_only
- 🔵 uTemplate: read_only
- 🔵 uCode: read_only
- 🔵 uScript: read_only
- ❌ package: none
- ❌ extension: none
- 🔵 docs: read_only

### 👹 Imp (Level 50/100)
- **Mischievous Spirit** with script and template creation powers
- **Development Focus**: Can create and modify user scripts and templates
- **Limited System Access**: Cannot access core system folders
- **Creative Powers**: Template and script editing within user space

**Folder Access**:
- ✅ sandbox: full
- 🟡 uMemory: read_write_user
- 🔵 uKnowledge: read_only
- 🔵 uTemplate: read_only
- 🔵 uCode: read_only
- 🟡 uScript: read_write_user
- ❌ package: none
- ❌ extension: none
- 🔵 docs: read_only

### 🤖 Drone (Level 25/100) **[UPDATED]**
- **Automated Entity** with structured access to basic operations and sandbox
- **Controlled Operations**: Limited to predefined operational patterns
- **Basic Functionality**: Read access to documentation and templates
- **Sandbox Access**: Limited read/write access to sandbox areas

**Folder Access**:
- 🟡 sandbox: read_write_limited
- 🔵 uMemory: read_only
- ❌ uKnowledge: none
- 🔵 uTemplate: read_only
- ❌ uCode: none
- 🔵 uScript: read_only
- ❌ package: none
- ❌ extension: none
- 🔵 docs: read_only

### 👻 Ghost (Level 10/100)
- **Ethereal Presence** with limited access for demos and temporary use
- **Demo Mode**: Can only access demonstration areas
- **Minimal Permissions**: Read-only access to public documentation
- **Temporary Nature**: Designed for guest and demo scenarios

**Folder Access**:
- 🟣 sandbox: demo_only
- ❌ uMemory: none
- ❌ uKnowledge: none
- ❌ uTemplate: none
- ❌ uCode: none
- ❌ uScript: none
- ❌ package: none
- ❌ extension: none
- 🟣 docs: public_only

## 🎯 Role Positioning Logic

The **Drone** role is positioned between **Imp** and **Ghost**, providing:

1. **Level 25** positioning between Imp (50) and Ghost (10)
2. **Structured automation** capabilities for basic operations
3. **Controlled sandbox access** for automated tasks
4. **Read-only system awareness** without modification privileges
5. **Bridge functionality** between creative (Imp) and demo (Ghost) roles

## 🔧 Enhanced Features

### 5-Tier Hierarchy Benefits
- **Granular Control**: More precise permission assignments
- **Automation Support**: Drone role designed for automated entities
- **Flexibility**: Better role assignment options for different use cases
- **Security Layering**: More controlled access progression

### Role Management Commands
```bash
# View all 5 mystical roles
./user-role-manager.sh roles

# Set user to drone role  
./user-role-manager.sh set-role username drone

# Test complete role system
./mystical-role-test.sh
```

## 🧪 Testing Results

✅ **5-Role Hierarchy**: All roles properly ordered and functional  
✅ **Drone Integration**: New role positioned correctly between Imp and Ghost  
✅ **Permission Validation**: Drone has appropriate access levels  
✅ **System Compatibility**: All existing functionality preserved  
✅ **Documentation Updated**: Complete role documentation and testing  

## 📊 Role Comparison Matrix

| Role     | Level | Sandbox | uMemory | uKnowledge | System | Package/Ext | Dev Mode |
|----------|-------|---------|---------|------------|--------|-------------|----------|
| Wizard   | 100   | Full    | Full    | Full       | Dev    | Dev         | ✅       |
| Sorcerer | 75    | Full    | Limited | Read       | Read   | None        | ❌       |
| Imp      | 50    | Full    | User    | Read       | Read   | None        | ❌       |
| **Drone** | **25** | **Limited** | **Read** | **None** | **Read** | **None** | **❌** |
| Ghost    | 10    | Demo    | None    | None       | None   | None        | ❌       |

## 🚀 Implementation Status

- ✅ **Role Definition**: Drone role added to user-roles.json dataset
- ✅ **Level Assignment**: Positioned at level 35 between Imp and Ghost
- ✅ **Permission Structure**: Automated entity access pattern implemented
- ✅ **Folder Access**: Structured sandbox and read-only system access
- ✅ **Testing Validation**: All 5 roles tested and operational
- ✅ **Documentation**: Complete role hierarchy documentation

**Status**: 🎉 **COMPLETE** - 5-Tier Mystical Role System v2.2 fully operational!
