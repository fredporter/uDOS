# uDOS v1.0 Clean Distribution

## Repository Structure

This is a clean distribution of uDOS v1.0 implementing the proper security model:

### ✅ Included in Repository
- **uCode/**: Core system scripts (read-only for most users)
- **uKnowledge/**: Documentation and packages (read-only)
- **uScript/**: System automation scripts (sorcerer+ access)
- **uTemplate/**: Standard templates (read-only)
- **docs/**: System documentation
- **Distribution scripts**: Installation and build tools
- **VS Code configuration**: Workspace tasks and settings

### 🔒 Excluded from Repository (Created Locally)
- **uMemory/**: Private user files (Security Level 1)
- **uExtension/**: VS Code extension source (Security Level 2)
- **Build artifacts**: Logs, temporary files, compiled output
- **User data**: Missions, moves, personal configurations

## Security Model

### Level 1: uMemory (Private)
- Never included in git repository
- Contains all personal user data
- Two sharing options: explicit (private) and public (opt-in)
- Created during installation with proper permissions

### Level 2: uExtension (Local Development)
- Local development files only
- Extensions distributed via uKnowledge packages
- Reduces repository complexity
- Enables rapid development cycles

### Level 3: Core System (Repository)
- uKnowledge is read-only for users
- uCode provides system functionality
- uTemplate offers standardized content creation
- uScript enables automation (role-dependent access)

## File Count Reduction

This clean distribution contains only essential system files, resulting in:
- 📉 Reduced repository size (~90% smaller)
- 🧹 Clean git history without user data
- 🔒 Enhanced privacy protection
- 🚀 Faster clone and distribution times

## Installation

See INSTALL.md for complete installation instructions.

Generated: Fri Jul 18 17:00:11 AEST 2025
Version: v1.0.0
