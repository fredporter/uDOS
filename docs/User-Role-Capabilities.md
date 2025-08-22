# uDOS v1.3.3 User Role Capabilities Reference

---
**Foreword**

This User Role Capabilities Reference details the specific capabilities, permissions, and command sets available to each uDOS v1.3.3 installation role. Written in the style of early home computer manuals, it provides comprehensive guidance for understanding what each role can accomplish and choosing the right installation for your needs.

---

## Capability-Based Role Framework

* **Role-specific capabilities**: uDOS provides distinct capability sets through role-specific interfaces, with outputs scaled to user permissions and expertise.
* **Progressive capability model**: Each role builds upon the previous, providing a natural progression path with increasing capabilities from GHOST to WIZARD.
* **Enhanced workflow integration**: v1.3.3 adds briefings, roadmaps, assist mode, and context-aware operations tailored to each role's capabilities.
* **Eight distinct capability tiers**: GHOST, TOMB, CRYPT, DRONE, KNIGHT, IMP, SORCERER, WIZARD with cross-role collaboration.
* **Capability-specific interactions**: All role interactions and outputs are stored as `.md` files — readable, searchable, and immutable unless rewritten.
* **Role-based capability controls**: Access controls and available capabilities scale with role level and specialization.
* **Git-integrated collaboration**: Built-in version control with SSH for capability-based collaboration and backup.
* **uCODE capability progression**: Modern CAPITALS-DASH-NUMBER syntax with PIPE | options, complexity increasing with role capabilities.

---

## Eight Role Capability Tiers (v1.3.3 Foundation)

uDOS v1.3.3 operates through eight distinct user roles, each designed for specific capabilities and use cases with enhanced workflow integration.

### GHOST (Level 10/100) – Demo Installation
- **Purpose**: Safe learning environment with modern uCODE syntax
- **Capabilities**: Read-only, tutorials, sandbox experimentation, basic assist mode
- **Access**: Public docs and community resources
- **Memory Access**: Demo-only temporary sandbox
- **Features**: Demo interface, limited sandbox, uCODE syntax learning
- **Enhanced v1.3.3**: Basic workflow demonstrations, simple assist mode

**Folder Access**
- sandbox: demo-only
- uMEMORY: none
- uKNOWLEDGE: none
- uCORE: none
- uSCRIPT: none
- dev: none (wizard replaced with dev)
- docs: public-only
- installations/GHOST: full

**Available Commands**:
```ucode
[SYS] <STATUS|BRIEF>        ~ System status
[ROLE] <CURRENT>            ~ Check current role
[WORKFLOW] <MODE>           ~ Check workflow mode
[ASSIST] <ENTER>            ~ Enter demo assist mode
```

### TOMB (Level 20/100) – Archive Installation
- **Purpose**: Data archaeology and historical analysis with enhanced search
- **Capabilities**: Archive search, data mining, backup management, encrypted storage access
- **Access**: Historical datasets, backup systems, encrypted archives
- **Memory Access**: Read-only to archived content with decryption capabilities
- **Enhanced v1.3.3**: Advanced search with FUZZY options, backup restore with SECURE options

**Folder Access**
- sandbox: read-only
- uMEMORY: read-only (archived)
- uKNOWLEDGE: read-only (historical)
- uCORE: none
- uSCRIPT: none
- dev: none
- docs: read-only
- installations/TOMB: full

**Available Commands**:
```ucode
[MEM] <RETRIEVE|DECRYPT> {ARCHIVE-KEY}  ~ Access encrypted archives
[KNOW] <SEARCH|FUZZY> {HISTORICAL-DATA} ~ Search historical data
[FILE] <READ|BINARY> {BACKUP-FILE}      ~ Read backup files
BACKUP list                             ~ List available backups
BACKUP restore {BACKUP-NAME}            ~ Restore from backup
```

### CRYPT (Level 30/100) – Cryptographic Installation
- **Purpose**: Advanced encryption, security protocols, and cryptographic operations
- **Capabilities**: Key management, encryption/decryption, security auditing, secure communications
- **Access**: Cryptographic tools, security logs, encrypted vaults
- **Memory Access**: Encrypted read/write with advanced security protocols
- **Enhanced v1.3.3**: Advanced encryption protocols, secure workflow integration, key rotation

**Folder Access**
- sandbox: encrypted read/write
- uMEMORY: encrypted full access
- uKNOWLEDGE: encrypted read-only
- uCORE: security modules only
- uSCRIPT: encrypted script execution
- dev: security-focused development tools
- docs: security documentation full access
- installations/CRYPT: full

**Available Commands**:
```ucode
[CRYPT] <ENCRYPT|AES-256> {DATA} {KEY-ID}       ~ Advanced encryption
[CRYPT] <DECRYPT|VERIFY> {ENCRYPTED-DATA}      ~ Verified decryption
[KEY] <GENERATE|ROTATE> {KEY-TYPE} {STRENGTH}   ~ Key generation and rotation
[VAULT] <SECURE|BACKUP> {VAULT-NAME}           ~ Secure vault operations
[AUDIT] <SECURITY|DEEP> {SYSTEM-SCAN}          ~ Deep security auditing
[COMM] <SECURE|E2E> {RECIPIENT} {MESSAGE}      ~ End-to-end communications
SECURITY check                                 ~ Comprehensive security check
VAULT create {VAULT-NAME}                      ~ Create encrypted vault
```

### DRONE (Level 40/100) – Automation Installation
- **Purpose**: Automated task execution and monitoring with enhanced workflow
- **Capabilities**: Scheduling, monitoring, predictive maintenance, automated cleanup
- **Access**: Automation scripts, logs, workflow management
- **Memory Access**: Read/write automation logs with encryption
- **Enhanced v1.3.3**: Workflow automation, briefings integration, auto-cleanup

**Folder Access**
- sandbox: limited read/write
- uMEMORY: read-only
- uKNOWLEDGE: none
- uCORE: limited read-only
- uSCRIPT: read-only
- dev: briefings and roadmaps read-only
- docs: read-only
- installations/DRONE: full

**Available Commands**:
```ucode
[SCRIPT] <SCHEDULE|REPEAT> {MAINTENANCE} {DAILY} ~ Schedule automation
[WORKFLOW] <CLEANUP|FORCE> {ALL}                ~ Force cleanup operations
[LOG] <INFO|TIMESTAMP> {AUTOMATION-STATUS}      ~ Timestamped logging
[MEM] <STORE|ENCRYPT> {AUTOMATION-DATA} {VALUE} ~ Encrypted data storage
[WORKFLOW] <BRIEFINGS|SYNC> {UPDATE}            ~ Sync briefings
SETUP test                                      ~ Setup testing environment
```

### KNIGHT (Level 50/100) – Security Operations Installation
- **Purpose**: System defense, threat detection, incident response, security enforcement
- **Capabilities**: Real-time monitoring, threat analysis, security automation, incident response
- **Access**: Security tools, monitoring systems, threat intelligence, defensive systems
- **Memory Access**: Security-focused read/write with audit trails
- **Enhanced v1.3.3**: Advanced threat detection, automated security responses, security workflow integration

**Folder Access**
- sandbox: monitored full access
- uMEMORY: security-audited read/write
- uKNOWLEDGE: threat intelligence access
- uCORE: security monitoring modules
- uSCRIPT: security script execution
- dev: security development tools
- docs: security documentation full access
- installations/KNIGHT: full

**Available Commands**:
```ucode
[MONITOR] <THREAT|REALTIME> {SYSTEM-SCAN}       ~ Real-time threat monitoring
[DEFEND] <BLOCK|AUTO> {THREAT-ID} {ACTION}      ~ Automated threat blocking
[INCIDENT] <RESPOND|ESCALATE> {ALERT-LEVEL}     ~ Incident response protocols
[FORENSIC] <ANALYZE|DEEP> {SECURITY-LOG}        ~ Deep forensic analysis
[PATROL] <SWEEP|SCHEDULED> {SECURITY-ZONES}     ~ Scheduled security sweeps
[ALERT] <NOTIFY|CRITICAL> {ADMIN} {THREAT}      ~ Critical threat notifications
SECURITY monitor                                ~ Continuous security monitoring
THREATS analyze                                 ~ Comprehensive threat analysis
```

### IMP (Level 60/100) – Developer Installation
- **Purpose**: Creative projects and prototyping with modern uCODE
- **Capabilities**: Templates, scripting, project scaffolding, API integration
- **Access**: Creative tools, libraries, experimental environments, data control
- **Memory Access**: Read/write to own content with encryption support
- **Enhanced v1.3.3**: Full uCODE syntax, GET/POST operations, assist mode integration

**Folder Access**
- sandbox: full
- uMEMORY: user read/write
- uKNOWLEDGE: read-only
- uCORE: read-only
- uSCRIPT: full (user space)
- dev: read/write to own projects
- docs: read-only
- installations/IMP: full

**Available Commands**:
```ucode
[GET] <JSON|RETRY> {API-ENDPOINT} {PARAMS}      ~ API data retrieval
[POST] <JSON|COMPRESS> {API-URL} {DATA}         ~ Compressed API posts
[DATA] <PARSE|STRICT> {JSON-DATA}               ~ Strict data parsing
[FILE] <WRITE|BACKUP> {PROJECT-FILE} {CONTENT}  ~ File operations with backup
[WORKFLOW] <ASSIST|FORCE> {ENTER}               ~ Force enter assist mode
[ROLE] <ACTIVATE|PRESERVE> {IMP}                ~ Preserve session context
SETUP role                                      ~ Setup development environment
```

### SORCERER (Level 80/100) – Advanced User Installation
- **Purpose**: Complex project management, team collaboration, advanced workflows
- **Capabilities**: Advanced workflows, coordination, analytics, system administration
- **Memory Access**: Read/write to sandbox and templates with full encryption
- **Enhanced v1.3.3**: Full workflow management, advanced assist mode, system administration

**Folder Access**
- sandbox: full
- uMEMORY: full
- uKNOWLEDGE: limited read/write
- uCORE: read-only
- uSCRIPT: user read/write
- dev: full workflow management
- docs: read-only
- installations/SORCERER: full

**Available Commands**:
```ucode
[WORKFLOW] <BRIEFINGS|SYNC> {UPDATE}            ~ Advanced briefing management
[WORKFLOW] <ROADMAPS|PRIORITY> {ACTIVE}         ~ Priority roadmap management
[ASSIST] <ANALYZE|DEEP> {CONTEXT}               ~ Deep context analysis
[uCORE] <COMMAND|SECURE> {TRASH-EMPTY}          ~ Secure system operations
[ERROR] <LOG|STACK> {SYSTEM-ERROR} {CRITICAL}   ~ Advanced error handling
[SESSION] <SAVE|AUTO>                           ~ Auto-save session management
ROLE check                                      ~ Advanced role verification
BACKUP create                                   ~ System backup creation
```

### WIZARD (Level 100/100) – Full Installation
- **Purpose**: Full system control, configuration, security, development tools
- **Capabilities**: Complete system access, configuration, security, development tools
- **Access**: Complete system with all enhanced features
- **Memory Access**: Full read/write with all encryption and security features
- **Enhanced v1.3.3**: Complete workflow control, all assist modes, system development

**Folder Access**
- sandbox: full
- uMEMORY: full
- uKNOWLEDGE: full
- uCORE: full
- uSCRIPT: full
- dev: full (complete development environment)
- docs: full
- installations: full

**Available Commands**:
```ucode
~ Complete uCODE command set available
[SYS] <OPTIMIZE|FORCE> {MEMORY}                 ~ Force system optimization
[WORKFLOW] <MODE|VERBOSE>                       ~ Detailed workflow mode
[ASSIST] <ENTER|FORCE>                          ~ Force assist mode entry
[uCORE] <SESSION|ROLL-BACK> {UNDO}              ~ Advanced session management
[SETUP] <ROLE|FORCE>                            ~ Force role setup
[ERROR] <RETRY|BACK-OFF> {OPERATION} {COUNT}    ~ Advanced error recovery
ROLE install {EXTENSION}                        ~ Install role extensions
TRASH empty                                     ~ System trash management
~ Plus all commands from lower-level roles
```

---

## Comprehensive Permissions Matrix (v1.3.3)

### Role Access Control Matrix

| Resource/System | GHOST | TOMB | CRYPT | DRONE | KNIGHT | IMP | SORCERER | WIZARD |
|----------------|-------|------|-------|-------|--------|-----|----------|--------|
| **sandbox** | demo | read | encrypt | limited | monitor | full | full | full |
| **uMEMORY** | none | archive | encrypt | read | audit | user | full | full |
| **uKNOWLEDGE** | none | history | encrypt | none | threat | read | limited | full |
| **uCORE** | none | none | security | limited | monitor | read | read | full |
| **uSCRIPT** | none | none | encrypt | read | security | full | user | full |
| **dev folder** | none | none | security | briefings | security | projects | full | full |
| **docs** | public | read | security | read | security | read | read | full |
| **installations** | own | own | own | own | own | own | own | all |

### Security Clearance Levels

**Level 1 (GHOST)**: Public access, demo environments, basic learning
- No system modifications
- Temporary session data only
- Basic uCODE syntax learning

**Level 2 (TOMB)**: Historical data access, archive operations
- Read-only system access
- Encrypted archive decryption
- Historical data mining

**Level 3 (CRYPT)**: Cryptographic operations, advanced encryption
- Full encryption capabilities
- Key management and rotation
- Secure communications protocols

**Level 4 (DRONE)**: Automation and monitoring
- Scheduled task execution
- System monitoring capabilities
- Automated maintenance operations

**Level 5 (KNIGHT)**: Security operations and defense
- Real-time threat monitoring
- Incident response capabilities
- Security automation and enforcement

**Level 6 (IMP)**: Development and creative projects
- API integration capabilities
- Project development tools
- Creative environment access

**Level 7 (SORCERER)**: Advanced management and coordination
- Team workflow management
- Advanced system analytics
- Cross-role coordination

**Level 8 (WIZARD)**: Complete system administration
- Full system control
- All role capabilities
- System configuration and security

---

## Backup Protocol Framework (v1.3.3)

### Role-Based Backup Strategies

**GHOST Level Backups**:
```ucode
~ Demo session preservation
[BACKUP] <SESSION|TEMP> {DEMO-STATE}            ~ Temporary session backup
[RESTORE] <SESSION|BASIC> {DEMO-CHECKPOINT}     ~ Basic session restoration
```

**TOMB Level Backups**:
```ucode
~ Archive-focused backup operations
[BACKUP] <ARCHIVE|INCREMENTAL> {HISTORICAL}     ~ Incremental archive backup
[BACKUP] <VERIFY|CHECKSUM> {ARCHIVE-INTEGRITY}  ~ Archive integrity verification
[RESTORE] <ARCHIVE|SELECTIVE> {DATE-RANGE}      ~ Selective archive restoration
```

**CRYPT Level Backups**:
```ucode
~ Encrypted backup protocols
[BACKUP] <ENCRYPT|AES-256> {FULL-SYSTEM} {KEY}  ~ Full encrypted system backup
[BACKUP] <VAULT|SECURE> {CRYPTO-KEYS}           ~ Secure key vault backup
[RESTORE] <DECRYPT|VERIFY> {ENCRYPTED-BACKUP}   ~ Verified encrypted restoration
```

**DRONE Level Backups**:
```ucode
~ Automated backup scheduling
[BACKUP] <SCHEDULE|DAILY> {AUTO-BACKUP}         ~ Daily automated backups
[BACKUP] <MONITOR|STATUS> {BACKUP-HEALTH}       ~ Backup system monitoring
[RESTORE] <AUTO|ROLLBACK> {LAST-KNOWN-GOOD}     ~ Automatic rollback restoration
```

**KNIGHT Level Backups**:
```ucode
~ Security-focused backup operations
[BACKUP] <SECURE|AUDIT> {SECURITY-LOGS}         ~ Audited security log backup
[BACKUP] <INCIDENT|PRESERVE> {FORENSIC-DATA}    ~ Incident preservation backup
[RESTORE] <FORENSIC|CHAIN> {EVIDENCE-BACKUP}    ~ Chain-of-custody restoration
```

**IMP Level Backups**:
```ucode
~ Development project backups
[BACKUP] <PROJECT|SNAPSHOT> {DEV-MILESTONE}     ~ Development milestone backup
[BACKUP] <CODE|VERSIONED> {GIT-INTEGRATION}     ~ Git-integrated code backup
[RESTORE] <PROJECT|BRANCH> {FEATURE-BACKUP}     ~ Feature branch restoration
```

**SORCERER Level Backups**:
```ucode
~ Comprehensive workflow backups
[BACKUP] <WORKFLOW|COMPLETE> {TEAM-STATE}       ~ Complete workflow state backup
[BACKUP] <COORDINATION|SYNC> {MULTI-ROLE}       ~ Multi-role coordination backup
[RESTORE] <WORKFLOW|ORCHESTRATED> {TEAM-RESTORE} ~ Orchestrated team restoration
```

**WIZARD Level Backups**:
```ucode
~ Master system backup control
[BACKUP] <SYSTEM|COMPLETE> {FULL-INSTALLATION}  ~ Complete system backup
[BACKUP] <DISTRIBUTED|SYNC> {MULTI-SYSTEM}      ~ Distributed system synchronization
[RESTORE] <MASTER|CONTROL> {SYSTEM-REBUILD}     ~ Master system reconstruction
```

### Backup Protocol Hierarchy

1. **Session Backups**: Temporary state preservation (all roles)
2. **Data Backups**: Content and file preservation (TOMB+)
3. **Encrypted Backups**: Secure data protection (CRYPT+)
4. **Automated Backups**: Scheduled preservation (DRONE+)
5. **Security Backups**: Audit trail preservation (KNIGHT+)
6. **Project Backups**: Development milestone preservation (IMP+)
7. **Workflow Backups**: Team coordination preservation (SORCERER+)
8. **System Backups**: Complete installation preservation (WIZARD)

---

## Logging Practices & Audit Framework (v1.3.3)

### Role-Based Logging Architecture

**GHOST Level Logging**:
```ucode
~ Basic session logging
[LOG] <SESSION|BASIC> {USER-ACTIONS}            ~ Basic user action logging
[LOG] <LEARN|TRACK> {SYNTAX-PROGRESS}           ~ uCODE learning progress tracking
```

**TOMB Level Logging**:
```ucode
~ Archive access logging
[LOG] <ACCESS|ARCHIVE> {DATA-RETRIEVAL}         ~ Archive access audit logging
[LOG] <SEARCH|HISTORY> {QUERY-PATTERNS}         ~ Historical search pattern logging
```

**CRYPT Level Logging**:
```ucode
~ Cryptographic operation logging
[LOG] <CRYPTO|SECURE> {KEY-OPERATIONS}          ~ Secure cryptographic operation logging
[LOG] <SECURITY|AUDIT> {ENCRYPTION-EVENTS}      ~ Security event audit logging
```

**DRONE Level Logging**:
```ucode
~ Automation system logging
[LOG] <AUTO|SCHEDULE> {TASK-EXECUTION}          ~ Automated task execution logging
[LOG] <MONITOR|SYSTEM> {PERFORMANCE-METRICS}    ~ System performance monitoring logging
```

**KNIGHT Level Logging**:
```ucode
~ Security operations logging
[LOG] <SECURITY|CRITICAL> {THREAT-EVENTS}       ~ Critical security event logging
[LOG] <INCIDENT|FORENSIC> {RESPONSE-ACTIONS}    ~ Forensic incident response logging
```

**IMP Level Logging**:
```ucode
~ Development activity logging
[LOG] <DEV|PROGRESS> {PROJECT-MILESTONES}       ~ Development progress logging
[LOG] <API|INTEGRATION> {SERVICE-CALLS}         ~ API integration activity logging
```

**SORCERER Level Logging**:
```ucode
~ Advanced workflow logging
[LOG] <WORKFLOW|COORDINATION> {TEAM-ACTIVITIES} ~ Team coordination activity logging
[LOG] <ANALYTICS|DEEP> {SYSTEM-INSIGHTS}        ~ Deep system analytics logging
```

**WIZARD Level Logging**:
```ucode
~ Master system logging
[LOG] <SYSTEM|COMPREHENSIVE> {ALL-OPERATIONS}   ~ Comprehensive system operation logging
[LOG] <ADMIN|MASTER> {CONFIGURATION-CHANGES}    ~ Master configuration change logging
```

### Audit Trail Standards

**Security Audit Requirements**:
- All privileged operations logged with timestamps
- User action correlation across role escalations
- Cryptographic operation verification trails
- Access pattern analysis and anomaly detection

**Compliance Framework**:
- Role-based access control audit trails
- Data encryption and key management logging
- Backup and restoration operation verification
- Cross-role collaboration documentation

**Log Retention Policies**:
- **GHOST**: Session duration only
- **TOMB**: Historical archive integration
- **CRYPT**: Secure long-term encrypted storage
- **DRONE**: Automated retention management
- **KNIGHT**: Security-mandated retention periods
- **IMP**: Project lifecycle alignment
- **SORCERER**: Workflow coordination requirements
- **WIZARD**: Master system compliance requirements

---

## Multi-Role Collaboration Architecture (v1.3.3)

### Enhanced Role Interaction Framework

uDOS v1.3.3 enables sophisticated collaboration between different user roles through enhanced workflows and shared context:

```ucode
~ Multi-role session example
[GHOST] WORKFLOW START {BASIC-TASK}              ~ Start collaborative task
[DRONE] WORKFLOW JOIN {SHARED-CONTEXT}           ~ Join with automation
[IMP] WORKFLOW EXTEND {API-INTEGRATION}          ~ Add development features
[SORCERER] WORKFLOW MANAGE {FULL-COORDINATION}   ~ Manage team workflow
```

### Role Interaction Patterns

**Complete Escalation Chain**:
- GHOST → TOMB: Basic to encrypted operations
- TOMB → CRYPT: Add advanced cryptographic capabilities
- CRYPT → DRONE: Include workflow automation with security
- DRONE → KNIGHT: Add security operations and defense
- KNIGHT → IMP: Include development features with security focus
- IMP → SORCERER: Advanced project management and coordination
- SORCERER → WIZARD: Full system administration

**Parallel Role Specializations**:
- **Security Track**: GHOST → CRYPT → KNIGHT → WIZARD
- **Development Track**: GHOST → TOME → DRONE → IMP → WIZARD
- **Operations Track**: GHOST → DRONE → KNIGHT → SORCERER → WIZARD
- **Research Track**: GHOST → TOMB → CRYPT → SORCERER → WIZARD

**Shared Context Management**:
```ucode
[WORKFLOW] <BRIEFINGS|SHARE> {ROLE-GHOST}       ~ Share context to GHOST
[SESSION] <CONTEXT|PRESERVE> {MULTI-ROLE}       ~ Preserve across roles
[DATA] <SYNC|ENCRYPTED> {SHARED-MEMORY}         ~ Sync encrypted data
```

### Enhanced v1.3.3 Features

**Workflow Integration**:
- Briefings shared across installations
- Roadmaps accessible by appropriate roles
- Assist mode coordination between roles
- Context preservation during role switching

**Security Model**:
- Role-based access controls
- Encrypted data sharing
- Session isolation with controlled bridges
- Audit trails for multi-role operations

---

## Role-Based Command Examples (v1.3.3)

### Beginner Role Operations
```ucode
~ GHOST role - Learning and exploration
GET help                                        ~ Basic help system
SETUP role                                      ~ Role configuration
[WORKFLOW] <ASSIST|BASIC> {ENTER}               ~ Enter basic assist mode
```

### Intermediate Role Workflow
```ucode
~ IMP role - Development and creativity
[FILE] <READ|PARSE> {PROJECT-CONFIG}            ~ Parse project configuration
[DATA] <VALIDATE|STRICT> {JSON-INPUT}          ~ Validate input data
[WORKFLOW] <BRIEFINGS|UPDATE> {PROGRESS}       ~ Update development progress
[ERROR] <HANDLE|RETRY> {API-TIMEOUT}           ~ Handle development errors
```

### Advanced Role Administration
```ucode
~ WIZARD role - Full system control
[SYS] <BACKUP|ENCRYPT> {FULL-SYSTEM}           ~ Encrypted system backup
[WORKFLOW] <ROADMAPS|GENERATE> {TEAM-PLAN}     ~ Generate team roadmaps
[uCORE] <SESSION|MANAGE> {MULTI-USER}          ~ Manage multi-user sessions
[ASSIST] <ANALYZE|COMPREHENSIVE> {FULL-CONTEXT} ~ Comprehensive analysis
```

---

## Role Selection & Progression Guide (v1.3.3)

### Choosing Your Starting Role
- **New to uDOS?** Start with **GHOST** for safe learning and exploration
- **Data analysis focus?** **TOMB** provides powerful archive and search capabilities
- **Security & encryption needs?** **CRYPT** offers advanced cryptographic operations
- **Automation requirements?** **DRONE** provides scheduling and monitoring tools
- **Security operations focus?** **KNIGHT** delivers threat detection and incident response
- **Development work?** **IMP** includes full API integration and project tools
- **Team coordination needs?** **SORCERER** provides advanced workflow management
- **System administration?** **WIZARD** offers complete system control

### Specialized Role Tracks
- **Security Professionals**: GHOST → CRYPT → KNIGHT → WIZARD
- **Developers**: GHOST → TOMB → DRONE → IMP → WIZARD
- **System Operators**: GHOST → DRONE → KNIGHT → SORCERER → WIZARD
- **Data Analysts**: GHOST → TOMB → CRYPT → SORCERER → WIZARD
- **Project Managers**: GHOST → DRONE → IMP → SORCERER → WIZARD

### Role Progression Benefits
- **Seamless Upgrades**: Higher roles inherit all lower-role capabilities
- **Contextual Learning**: Each role provides appropriate complexity for skill level
- **Security Scaling**: Access controls grow with user expertise and needs
- **Workflow Evolution**: Simple to complex workflow management as you advance
- **Natural Migration Path**: Easy progression from basic learning to full system control

### Multi-Role Development Integration
- **uCORE Enhanced Commands**: Deep integration with core systems scales with role
- **API Integration**: Native support begins at IMP level and expands upward
- **Session Management**: Advanced undo/redo and state preservation in higher roles
- **Team Coordination**: Sophisticated collaboration patterns for SORCERER+ roles

---

*User Role Capabilities Reference v1.3.3 - Comprehensive capability guide with progressive role-based feature sets*
