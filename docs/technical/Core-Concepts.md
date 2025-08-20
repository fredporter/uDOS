# uDOS v1.3 Comprehensive Concepts & Architecture

---
**Foreword**

This Concepts Guide explains the foundations of uDOS v1.3. Written in the style of early home computer manuals, it is practical and direct, giving you the background you need to explore the system with confidence.

---

## Input-Output Flow

* Role-based processing: uDOS accepts input through role-specific interfaces, producing outputs appropriate to user capabilities and permissions.  
* Multi-installation model: Six distinct installation types (Ghost, Tomb, Drone, Imp, Sorcerer, Wizard) with cross-installation collaboration.  
* Markdown-first: All interactions and outputs are stored as `.md` files — readable, searchable, and immutable unless rewritten.  
* Privacy-by-default: No external syncing or telemetry. All computation and memory stays local unless exported.  
* Git-integrated: Built-in version control with SSH for collaboration and backup.  

---

## Role-Based Architecture (v1.3 Foundation)

uDOS v1.3 operates through six installation roles, each with specific capabilities.  

### Ghost (Level 10/100) – Demo Installation
- Purpose: Safe learning environment  
- Capabilities: Read-only, tutorials, sandbox experimentation  
- Access: Public docs and community resources  
- Memory Access: Demo-only temporary sandbox  
- Features: Demo interface, limited sandbox  

**Folder Access**  
- sandbox: demo-only  
- uMEMORY: none  
- uKNOWLEDGE: none  
- uCORE: none  
- uSCRIPT: none  
- wizard: none  
- docs: public-only  
- installations/ghost: full  

### Tomb (Level 20/100) – Archive Installation
- Purpose: Data archaeology and historical analysis  
- Capabilities: Archive search, data mining, backup management  
- Access: Historical datasets, backup systems  
- Memory Access: Read-only to archived content  

**Folder Access**  
- sandbox: read-only  
- uMEMORY: read-only (archived)  
- uKNOWLEDGE: read-only (historical)  
- uCORE: none  
- uSCRIPT: none  
- wizard: none  
- docs: read-only  
- installations/tomb: full  

### Drone (Level 40/100) – Automation Installation
- Purpose: Automated task execution and monitoring  
- Capabilities: Scheduling, monitoring, predictive maintenance  
- Access: Automation scripts, logs  
- Memory Access: Read/write automation logs  

**Folder Access**  
- sandbox: limited read/write  
- uMEMORY: read-only  
- uKNOWLEDGE: none  
- uCORE: limited read-only  
- uSCRIPT: read-only  
- wizard: none  
- docs: read-only  
- installations/drone: full  

### Imp (Level 60/100) – Developer Installation
- Purpose: Creative projects and prototyping  
- Capabilities: Templates, scripting, project scaffolding  
- Access: Creative tools, libraries, experimental environments  
- Memory Access: Read/write to own content  

**Folder Access**  
- sandbox: full  
- uMEMORY: user read/write  
- uKNOWLEDGE: read-only  
- uCORE: read-only  
- uSCRIPT: full (user space)  
- wizard: none  
- docs: read-only  
- installations/imp: full  

### Sorcerer (Level 80/100) – Advanced User Installation
- Purpose: Complex project management, team collaboration  
- Capabilities: Advanced workflows, coordination, analytics  
- Memory Access: Read/write to sandbox and templates  

**Folder Access**  
- sandbox: full  
- uMEMORY: full  
- uKNOWLEDGE: limited read/write  
- uCORE: read-only  
- uSCRIPT: user read/write  
- wizard: none  
- docs: read-only  
- installations/sorcerer: full  

### Wizard (Level 100/100) – Full Installation
- Purpose: Full system control  
- Capabilities: Configuration, security, development tools  
- Access: Complete system  
- Memory Access: Full read/write  

**Folder Access**  
- sandbox: full  
- uMEMORY: full  
- uKNOWLEDGE: full  
- uCORE: full  
- uSCRIPT: full  
- wizard: full  
- docs: full  
- installations: full  

---

## Multi-Installation Architecture