# uDOS Error Handling & Logging System v1.3

**Complete role-based error handling with development logging**

## 🔧 System Overview

The uDOS error handling system provides comprehensive logging and error management across all user roles, with specialized handlers for each environment and a powerful development logging system for wizard-level access.

## 📁 System Components

### Wizard Development Environment (Level 100)

**Location**: `wizard/error-handling/`

- **`wizard-dev-logging.sh`**: Advanced development logging system with session tracking, performance monitoring, and comprehensive analytics
- **`wizard-error-system.sh`**: Comprehensive error handling with recovery protocols, stack traces, and development-focused diagnostics

**Features**:
- Session-based logging with unique session IDs
- Performance monitoring and analytics
- Error recovery and auto-fix capabilities
- Development activity tracking
- Git integration and context awareness
- Desktop notifications and system logging

### Role-Themed Error Handlers

Each user mode has a specialized error handler with role-appropriate terminology and features:

#### 👻 Ghost (Level 10) - Demo Environment
**File**: `ghost/ghost-error-handler.sh`

- **Theme**: Spectral/Ethereal terminology
- **Focus**: Public safety, demo continuity
- **Features**: Spectral barriers, phantom sessions, ethereal error containment
- **Safety**: Maximum protection for public demonstrations

#### ⚰️ Tomb (Level 20) - Archive Environment  
**File**: `tomb/tomb-error-handler.sh`

- **Theme**: Archival/Historical terminology
- **Focus**: Data preservation, vault security
- **Features**: Archive preservation, historical sessions, vault protection
- **Safety**: Read-only access, archive integrity maintained

#### 🤖 Drone (Level 40) - Automation Environment
**File**: `drone/drone-error-handler.sh`

- **Theme**: Automation/Operational terminology
- **Focus**: Task execution continuity, system monitoring
- **Features**: Automated recovery, execution sessions, operation logging
- **Safety**: System isolation, resource management

#### 👹 Imp (Level 60) - Creative Environment
**File**: `imp/imp-error-handler.sh`

- **Theme**: Creative/Innovation terminology  
- **Focus**: Creative problem-solving, experimental safety
- **Features**: Error transformation, project sessions, creative analytics
- **Safety**: Sandbox protection, creative freedom with guardrails

#### 🔮 Sorcerer (Level 80) - Advanced Management
**File**: `sorcerer/sorcerer-error-handler.sh`

- **Theme**: Mystical/Management terminology
- **Focus**: Project coordination, team management
- **Features**: Arcane error channeling, ritual sessions, authority protection
- **Safety**: Advanced permissions, management integrity

## 🎯 Usage Examples

### Wizard Development Logging

```bash
# Initialize development session
./wizard/error-handling/wizard-dev-logging.sh init

# Log development activities
./wizard/error-handling/wizard-dev-logging.sh log INFO "Starting build process"
./wizard/error-handling/wizard-dev-logging.sh activity "build" "Compiling TypeScript"

# Handle errors
./wizard/error-handling/wizard-dev-logging.sh error "Build failed" "compilation"

# Generate reports
./wizard/error-handling/wizard-dev-logging.sh report
```

### Role-Based Error Handling

```bash
# Ghost demo environment
./ghost/ghost-error-handler.sh manifest
./ghost/ghost-error-handler.sh demo "interaction" "User exploring interface"

# Tomb archive environment  
./tomb/tomb-error-handler.sh excavate
./tomb/tomb-error-handler.sh archive "browse" "Historical data access"

# Drone automation environment
./drone/drone-error-handler.sh activate
./drone/drone-error-handler.sh task "schedule" "Automated backup"

# Imp creative environment
./imp/imp-error-handler.sh ignite
./imp/imp-error-handler.sh create "template" "New script template"

# Sorcerer management environment
./sorcerer/sorcerer-error-handler.sh invoke
./sorcerer/sorcerer-error-handler.sh manage "coordinate" "Team project alignment"
```

## 📊 Logging Structure

### File Organization

Each role creates its own logging directory structure:

```
{role}/
├── {theme}-logs/           # Daily logs
├── {theme}-errors/         # Error records  
├── {theme}-analytics/      # Analytics data
└── {theme}-sessions/       # Session tracking
```

### Log Entry Format

All handlers use consistent structured logging:

```
[TIMESTAMP] [LEVEL] [CONTEXT] [ROLE SESSION_ID]
Message: {error/info message}
State: {role-specific state information}
Context: {execution context}
---
```

## 🔧 Environment Variables

### Wizard Development

```bash
WIZARD_DEBUG=true                    # Enable debug logging
WIZARD_LOG_LEVEL=debug              # Set minimum log level
WIZARD_DEV_MODE=true                # Enable development features
WIZARD_ERROR_RECOVERY=true          # Enable automatic error recovery
WIZARD_ERROR_NOTIFICATIONS=true     # Enable error notifications
WIZARD_ERROR_AUTO_FIX=false         # Enable automatic fixes (use with caution)
```

### Role-Specific Variables

Each role has environment variables following the pattern:
```bash
{ROLE}_{FEATURE}_MODE=true          # Feature toggles
{ROLE}_{ASPECT}_LEVEL=value         # Configuration levels
{ROLE}_{SETTING}_ACCESS=mode        # Access controls
```

## 📈 Analytics & Reporting

### Wizard Development Analytics

- Session tracking with performance metrics
- Error pattern analysis
- Development activity monitoring  
- Git integration for change correlation
- Resource usage tracking

### Role-Based Analytics

Each role tracks metrics appropriate to its function:

- **Ghost**: Demo interactions, public safety metrics
- **Tomb**: Archive access patterns, preservation status
- **Drone**: Task execution rates, automation efficiency
- **Imp**: Creative activities, innovation metrics
- **Sorcerer**: Management actions, coordination events

## 🛡️ Security Features

### Development Environment
- Comprehensive error containment
- Stack trace capture and analysis
- Automatic cleanup on interruption
- Safe command execution wrappers

### Role-Based Security
- **Ghost**: Complete public safety isolation
- **Tomb**: Read-only access enforcement  
- **Drone**: Resource limit enforcement
- **Imp**: Sandbox isolation for experiments
- **Sorcerer**: Authority level validation

## 🔄 Error Recovery

### Automatic Recovery
- Command availability checking
- Permission validation and correction
- Directory creation for missing paths
- Network connectivity validation
- Resource usage monitoring

### Role-Specific Recovery
Each role implements recovery strategies appropriate to its access level and responsibilities.

## 📋 Integration

### Script Integration

Source the appropriate error handler in your scripts:

```bash
# For wizard development
source "$(dirname "${BASH_SOURCE[0]}")/wizard/error-handling/wizard-error-system.sh"

# For role-specific scripts  
source "$(dirname "${BASH_SOURCE[0]}")/{role}/{role}-error-handler.sh"
```

### Error Handling Functions

```bash
# Set error context
set_error_context "build" "compilation"

# Safe command execution
safe_execute "your-command" "context" "operation"

# Specialized error handling
handle_build_error "Build failed message"
handle_deployment_error "Deployment failed message"
handle_test_error "Test failed message"
```

## 🎨 Customization

### Adding New Roles

1. Create new error handler following the pattern
2. Implement role-specific theming and terminology
3. Add appropriate safety measures for the role's access level
4. Include role-specific analytics and session management

### Extending Functionality

- Add new error recovery protocols
- Implement additional notification channels
- Extend analytics with custom metrics
- Add role-specific safety checks

---

**Development Authority**: Level 100 Wizard Access  
**System Version**: uDOS v1.3  
**Error Handling**: Comprehensive Role-Based System

*This system provides enterprise-grade error handling with role-appropriate interfaces and comprehensive logging for all uDOS environments.*
