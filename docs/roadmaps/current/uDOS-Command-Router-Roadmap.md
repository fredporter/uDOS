---
type: roadmap
status: current
priority: high
category: core
created: 2025-08-26
last_updated: 2025-08-26
estimated_completion: 2025-08-27
responsible: team
---

# uDOS Command Router Implementation Roadmap

## Objective
Implement the core uCODE command processing system with role-based access control and integration with the variable management system.

## Background
Following successful documentation consolidation and ASSIST mode implementation, the system now needs a robust command router to process uCODE syntax `[COMMAND|ACTION*params]` and route commands to appropriate system modules.

## Implementation Plan

### Phase 1: Core Router (Day 1)
- **Create**: `uCORE/code/command-router.sh`
- **Features**: 
  - Parse `[COMMAND|ACTION*params]` syntax
  - Basic command validation
  - Error handling and user feedback
- **Integration**: Connect to existing `variable-manager.sh`

### Phase 2: Role-Based Access (Day 1-2)
- **Implement**: Permission checking before command execution
- **Features**:
  - 8-role hierarchy validation (Ghost → Wizard)
  - Role-specific command availability
  - Graceful degradation for insufficient permissions
- **Testing**: Validate with different role configurations

### Phase 3: ASSIST Commands (Day 2)
- **Add**: ASSIST mode command processing
- **Commands**:
  - `[ASSIST|ENTER]` - Activate ASSIST mode
  - `[ASSIST|FINALIZE]` - Auto-commit workflow
  - `[ASSIST|NEXT]` - Task recommendation
  - `[ASSIST|ROADMAP]` - Roadmap updates
  - `[ASSIST|EXIT]` - Deactivate mode
- **Integration**: Session finalization automation

### Phase 4: Variable Integration (Day 2-3)
- **Connect**: Router to variable system
- **Commands**:
  - `[GET $variable]` - Interactive data collection
  - `[SET $variable|value]` - Variable assignment
  - `[STORY collection-name]` - Multi-variable collection
- **Features**: Template generation with `{VARIABLE}` substitution

## Success Criteria
- ✅ Commands properly parsed and routed
- ✅ Role-based access control functional
- ✅ ASSIST mode commands operational
- ✅ Variable commands working with templates
- ✅ Error handling graceful and informative
- ✅ Integration with existing system modules

## Timeline
- **Start**: 26 August 2025 4:30 PM AEST
- **Phase 1 Complete**: 26 August 2025 6:00 PM AEST
- **Phase 2 Complete**: 27 August 2025 10:00 AM AEST
- **Phase 3 Complete**: 27 August 2025 2:00 PM AEST
- **Phase 4 Complete**: 27 August 2025 4:00 PM AEST
- **Testing & Integration**: 27 August 2025 5:00 PM AEST

## Dependencies
- ✅ Documentation consolidation (completed)
- ✅ File location standardization (completed)
- ✅ ASSIST mode implementation (completed)
- ⏳ Variable manager enhancement (in progress)
- ⏳ Role configuration system (needs validation)

## Technical Notes
- Router will be the central command processing hub
- Must maintain backward compatibility with existing scripts
- Error messages should be user-friendly for all roles
- Performance critical - router called for every command

## Related Roadmaps
- **Documentation System** (completed 26 Aug 2025)
- **Variable Management System** (in progress)
- **User Interface Layer** (planned)
- **Extension System** (planned)

---
*Created in ASSIST mode session - Command Router priority identified*
