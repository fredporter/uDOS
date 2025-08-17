# uDOS Architecture Overview

## System Architecture

uDOS follows a predominently flat, modular, user-centric architecture designed for simplicity and extensibility.

### Core Components

#### 🏗️ **Directory Structure**
- **`sandbox/`** - User workspace with identity and temporary scripts
- **`uMEMORY/`** - User data storage (moves, missions, milestones, legacy)
- **`wizard/`** - System development logs and debugging information
- **`uKNOWLEDGE/`** - Documentation and knowledge base
- **`uSCRIPT/`** - Script management and execution
- **`uCORE/templates/`** - Template system for forms, datagets, and configurations
- **`uCORE/`** - Core system scripts and utilities

#### 🔧 **Core Systems**
- **Template System** - Unified template processing with shortcodes and variables
- **Logging System** - Hierarchical user logging (moves → milestones → missions → legacy)
- **Command System** - Dynamic command loading and processing
- **Identity Management** - User identity and preference management

#### 📊 **Data Flow**
1. **User Input** → Template Processing → Configuration Generation
2. **Daily Activities** → Move Logging → Milestone Tracking → Mission Completion
3. **System Events** → Error Logging → Performance Monitoring → Debug Information

### Design Principles

- **User-Centric**: All user data in `uMemory`, system data in `uDev`
- **Template-Driven**: Configuration and setup through unified template system
- **Hierarchical Logging**: Natural progression from moves to device legacy
- **Modular Architecture**: Independent components with clear interfaces
- **Recovery-Focused**: Multiple fallback systems and validation layers

### Version Information

- **Architecture Version**: v1.3
- **Template System**: v2.0 with enhanced shortcode and variable support
- **Logging System**: v1.2 with Notion-style formatting and hierarchical relationships
- **Setup System**: v1.2 with modern template-based approach and legacy fallback
- **Filename Convention**: v1.3 with CAPS-NUMERIC-DASH standards and timezone integration

---
*This architecture document is part of the uDOS knowledge base and should be updated as the system evolves.*
