# uDOS v1.3 Mystical Role System - Multi-Installation Architecture

## 🎭 Enhanced Role Hierarchy with Installation Support

The uDOS v1.3 system operates with a comprehensive 6-tier mystical role hierarchy, where each role can be installed as a separate environment within the uDOS folder structure. Each installation type provides different capabilities and permissions while sharing common resources.

### 🧙‍♂️ Wizard (Level 100/100) - Full Installation
- **Master Administrator** with complete system access and all capabilities
- **Dev Mode Access**: Full development environment with wizard/ folder
- **Git Integration**: SSH key management and full repository control  
- **Package & Extension Access**: Full read/write access to all system folders
- **User Management**: Can spawn and manage all other installation types
- **Installation Features**: Complete uDOS system, development utilities, advanced workflows

**Folder Access**:
- ✅ sandbox: full
- ✅ uMEMORY: full  
- ✅ uKNOWLEDGE: full
- ✅ uCORE: full (dev mode)
- ✅ uSCRIPT: full (dev mode)
- ✅ wizard: full (exclusive)
- ✅ docs: full
- ✅ installations: full (can manage all)

### 🔮 Sorcerer (Level 80/100) - Advanced User Installation
- **Magical Practitioner** with elevated powers and advanced user capabilities
- **Project Management**: Advanced project and user content management
- **Limited Dev Access**: Can access development tools but not core system modification
- **Installation Features**: Advanced user interface, project management tools, limited scripting

**Folder Access**:
- ✅ sandbox: full
- ✅ uMEMORY: full
- 🟡 uKNOWLEDGE: read_write_limited
- 🔵 uCORE: read_only
- � uSCRIPT: read_write_user
- ❌ wizard: none
- 🔵 docs: read_only
- 🟡 installations/sorcerer: full

### 👹 Imp (Level 60/100) - Developer Installation  
- **Mischievous Creator** with script and template development powers
- **Development Focus**: Can create and modify user scripts and templates
- **Creative Powers**: Advanced template and script editing capabilities
- **Installation Features**: Development environment, script editor, template management

**Folder Access**:
- ✅ sandbox: full
- 🟡 uMEMORY: read_write_user
- 🔵 uKNOWLEDGE: read_only
- 🔵 uCORE: read_only
- ✅ uSCRIPT: full (user space)
- ❌ wizard: none
- 🔵 docs: read_only
- 🟡 installations/imp: full

### 🤖 Drone (Level 40/100) - Automation Installation
- **Automated Entity** with structured operations and task automation
- **Controlled Operations**: Predefined operational patterns and workflows
- **Task Execution**: Automated task processing and basic operations
- **Installation Features**: Task automation, basic scripting, scheduled operations

**Folder Access**:
- 🟡 sandbox: read_write_limited
- 🔵 uMEMORY: read_only
- ❌ uKNOWLEDGE: none
- 🔵 uCORE: read_only (limited)
- 🔵 uSCRIPT: read_only
- ❌ wizard: none
- 🔵 docs: read_only
- 🟡 installations/drone: full

### ⚰️ Tomb (Level 20/100) - Archive Installation **[NEW]**
- **Archival Entity** specialized in data preservation and historical access
- **Data Preservation**: Read-only access to archived content and historical data
- **Backup Operations**: Can access backup and archival systems
- **Installation Features**: Archive browsing, historical data access, backup management

**Folder Access**:
- 🔵 sandbox: read_only
- 🔵 uMEMORY: read_only (archived)
- 🔵 uKNOWLEDGE: read_only (historical)
- ❌ uCORE: none
- ❌ uSCRIPT: none
- ❌ wizard: none
- 🔵 docs: read_only
- 🟡 installations/tomb: full

### 👻 Ghost (Level 10/100) - Demo Installation
- **Ethereal Presence** with minimal access for demos and temporary use
- **Demo Mode**: Access only to demonstration areas and public content
- **Temporary Nature**: Designed for guest, demo, and evaluation scenarios
- **Installation Features**: Demo interface, limited sandbox, read-only documentation

**Folder Access**:
- 🟣 sandbox: demo_only
- ❌ uMEMORY: none
- ❌ uKNOWLEDGE: none
- ❌ uCORE: none
- ❌ uSCRIPT: none
- ❌ wizard: none
- 🟣 docs: public_only
- 🟡 installations/ghost: full

## �️ Multi-Installation Architecture

### Installation Directory Structure
```
uDOS/
├── uCORE/                      # Core system (shared)
├── uMEMORY/                    # User memory (shared with permissions)
├── uKNOWLEDGE/                 # Knowledge base (shared)
├── uSCRIPT/                    # Script library (shared)
├── sandbox/                    # User sandbox (shared with permissions)
├── docs/                       # Documentation (shared)
├── wizard/                     # Development environment (wizard only)
├── installations/              # Role-specific installations
│   ├── ghost/                  # Ghost installation
│   │   ├── demo-interface/     # Demo-only interface
│   │   ├── public-docs/        # Public documentation
│   │   └── temp-sandbox/       # Temporary demo area
│   ├── tomb/                   # Tomb installation
│   │   ├── archive-browser/    # Archive access tools
│   │   ├── backup-manager/     # Backup access system
│   │   └── historical-data/    # Historical data access
│   ├── drone/                  # Drone installation
│   │   ├── task-automation/    # Automated task system
│   │   ├── scheduler/          # Task scheduling
│   │   └── operation-logs/     # Operation logging
│   ├── imp/                    # Imp installation
│   │   ├── script-editor/      # Development environment
│   │   ├── template-manager/   # Template creation tools
│   │   └── user-projects/      # Personal project space
│   ├── sorcerer/               # Sorcerer installation
│   │   ├── project-manager/    # Advanced project tools
│   │   ├── user-admin/         # User management interface
│   │   └── advanced-tools/     # Advanced user utilities
│   └── wizard/                 # Wizard installation (symlink to ../wizard/)
└── shared/                     # Shared resources and configurations
    ├── permissions/            # Permission management
    ├── configs/                # Shared configurations
    └── resources/              # Common resources
```

### Installation Features by Role

#### 🧙‍♂️ Wizard Installation
- **Complete uDOS System**: All features and capabilities
- **Development Environment**: Full wizard/ folder with dev-utils.sh
- **Git Integration**: SSH key management, push/pull capabilities  
- **Permission Management**: Can create and manage other installations
- **System Administration**: Full system control and configuration

#### 🔮 Sorcerer Installation
- **Advanced User Interface**: Enhanced project management tools
- **User Administration**: Limited user management capabilities
- **Advanced Workflows**: Complex task and project management
- **Resource Allocation**: Can manage resource distribution
- **Collaboration Tools**: Advanced sharing and collaboration features

#### 👹 Imp Installation
- **Development Environment**: Script and template development tools
- **Creative Suite**: Advanced editing and creation capabilities
- **User Project Management**: Personal project organization
- **Template System**: Template creation and management
- **Script Library**: Personal script collection and execution

#### 🤖 Drone Installation
- **Task Automation**: Automated task execution and scheduling
- **Operation Monitoring**: System monitoring and logging
- **Scheduled Operations**: Cron-like scheduling system
- **Basic Scripting**: Limited script execution capabilities
- **Status Reporting**: Automated status and health reporting

#### ⚰️ Tomb Installation **[NEW]**
- **Archive Access**: Historical data browsing and retrieval
- **Backup Management**: Backup creation and restoration tools
- **Data Preservation**: Long-term data storage and organization
- **Historical Analysis**: Timeline and historical data analysis
- **Recovery Tools**: Data recovery and restoration utilities

#### 👻 Ghost Installation
- **Demo Interface**: Limited demonstration capabilities
- **Public Access**: Public documentation and basic features
- **Evaluation Mode**: Trial and evaluation functionality
- **Temporary Access**: Session-based temporary operations
- **Guest Features**: Basic guest user capabilities

## 🔐 Permission and Sharing System

### Permission Levels
- **full**: Complete read/write access
- **read_write_limited**: Read/write with restrictions
- **read_write_user**: Read/write only to user-owned content
- **read_only**: Read access only
- **demo_only**: Limited demo access
- **none**: No access

### Shared Resource Management

#### uMEMORY Sharing
- **Wizard**: Full access to all memory areas
- **Sorcerer**: Access to shared areas and own content
- **Imp**: Access to own content and public areas
- **Drone**: Read-only access to relevant operational data
- **Tomb**: Read-only access to archived content
- **Ghost**: No access

#### uKNOWLEDGE Sharing  
- **Wizard**: Full read/write access
- **Sorcerer**: Read/write to shared knowledge areas
- **Imp**: Read-only access to public knowledge
- **Drone**: No access
- **Tomb**: Read-only access to historical knowledge
- **Ghost**: No access

#### Sandbox Sharing
- **Wizard**: Full access to all sandbox areas
- **Sorcerer**: Full access to own sandbox + shared areas
- **Imp**: Full access to own sandbox + project areas
- **Drone**: Limited access to operational areas
- **Tomb**: Read-only access to archived sandbox content
- **Ghost**: Demo-only temporary sandbox

### Cross-Installation Communication

#### Message System
- **Wizard ↔ All**: Can communicate with any installation
- **Sorcerer ↔ Imp/Drone**: Can manage and communicate with lower roles
- **Imp ↔ Drone**: Limited project-based communication
- **Tomb**: Receive-only communication for archival purposes
- **Ghost**: No inter-installation communication

#### Resource Sharing
- **Templates**: Shared template library with role-based permissions
- **Scripts**: Role-appropriate script sharing and execution
- **Documentation**: Tiered access to documentation based on role
- **Configurations**: Shared configurations with permission overlays

## 🛠️ Installation Management

### Installation Commands
```bash
# Install specific role environment
./install-role.sh wizard
./install-role.sh sorcerer
./install-role.sh imp
./install-role.sh drone
./install-role.sh tomb
./install-role.sh ghost

# Manage installations
./manage-installations.sh list
./manage-installations.sh permissions
./manage-installations.sh upgrade

# Switch between installations
./switch-role.sh imp
./switch-role.sh wizard
```

### Upgrade Paths
- **Ghost → Tomb**: Archive access upgrade
- **Tomb → Drone**: Automation upgrade  
- **Drone → Imp**: Development upgrade
- **Imp → Sorcerer**: Advanced user upgrade
- **Sorcerer → Wizard**: Full system upgrade

## 📊 Role Comparison Matrix

| Role     | Level | Features | Sandbox | uMEMORY | uKNOWLEDGE | uCORE | uSCRIPT | Wizard | Install Dir |
|----------|-------|----------|---------|---------|------------|-------|---------|--------|-------------|
| Wizard   | 100   | Complete | Full    | Full    | Full       | Full  | Full    | Full   | wizard/     |
| Sorcerer | 80    | Advanced | Full    | Full    | Limited    | Read  | User    | None   | sorcerer/   |
| Imp      | 60    | Developer| Full    | User    | Read       | Read  | Full    | None   | imp/        |
| Drone    | 40    | Automation| Limited | Read    | None       | Read  | Read    | None   | drone/      |
| **Tomb** | **20** | **Archive** | **Read** | **Archive** | **Historical** | **None** | **None** | **None** | **tomb/** |
| Ghost    | 10    | Demo     | Demo    | None    | None       | None  | None    | None   | ghost/      |
