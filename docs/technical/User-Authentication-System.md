# 🔐 uDOS User Authentication System v1.3

The uDOS User Authentication System provides secure user management with personal data stored exclusively in the sandbox folder. This document covers the complete authentication framework implementation.

## 🎯 Overview

The authentication system is designed with security and simplicity in mind:

- **Single File Storage**: All user data in `sandbox/user.md`
- **Git Protection**: User data never tracked in git repository
- **Security Protocol**: Missing user.md triggers destroy/reboot
- **Password Security**: SHA-256 hashing with 1-16 character limit
- **Development Mode**: Authentication bypass for development

## 📁 File Structure

```
sandbox/
├── user.md                 # Primary user authentication file
├── user.md.backup         # Backup file (temporary)
└── README.md              # Sandbox documentation
```

## 🔐 User.md File Format

The `sandbox/user.md` file contains structured user data:

```markdown
# 🎭 uDOS User Identity
**System**: uDOS v1.3  
**Created**: 2025-08-20 20:45:55  
**Last Modified**: 2025-08-20 20:45:55  

## 🔐 Authentication
**Username**: testuser  
**Password**: NONE|SET  
**Password Hash**: BLANK|<sha256_hash>

## 🎯 User Settings
**User ID**: 202508209662  
**Role**: user|admin|developer  
**Theme**: default|dark|light|auto  
**Debug Mode**: true|false

## 🌍 Location Profile
**Timezone**: AEST  
**Location Code**: UNKNOWN  
**City**: Unknown  
**Country**: UNKNOWN

## 📁 Workspace Preferences
**Auto Backup**: true|false  
**Companion Enabled**: true|false  
**Default Editor**: nano|vim|code
```

## 🛠️ User Authentication Script

### Location
- **Script**: `/uCORE/code/user-auth.sh`
- **Permissions**: Executable (`chmod +x`)
- **Dependencies**: SHA-256 (shasum), bash utilities

### Commands

#### Setup and Creation
```bash
# Create new user account (interactive)
./uCORE/code/user-auth.sh create
./uCORE/code/user-auth.sh setup

# Reset existing user account
./uCORE/code/user-auth.sh reset
```

#### Authentication
```bash
# Authenticate current user
./uCORE/code/user-auth.sh auth

# Check user file validity
./uCORE/code/user-auth.sh check
```

#### User Management
```bash
# Show user information
./uCORE/code/user-auth.sh info
./uCORE/code/user-auth.sh show

# Change password
./uCORE/code/user-auth.sh password
./uCORE/code/user-auth.sh passwd
```

#### Security Protocol
```bash
# Trigger destroy and reboot
./uCORE/code/user-auth.sh destroy
```

## 🎮 uCode Integration

### USER Command

The main uDOS interface provides a `USER` command for user management:

```bash
USER INFO        # Show user information
USER AUTH        # Authenticate user
USER PASSWORD    # Change password
USER SETUP       # Create/setup account
USER RESET       # Reset account
USER CHECK       # Validate user file
USER HELP        # Show help
```

### Integration Points

1. **Startup Authentication**: `uCORE/code/startup.sh`
   - Checks user.md existence on system startup
   - Validates file format and structure
   - Triggers security protocol if missing

2. **Main Authentication**: `uCORE/code/ucode.sh`
   - Modified `authenticate_user()` function
   - Uses sandbox/user.md instead of uMEMORY/.auth
   - Integrates with USER command handler

## 🔒 Security Features

### Password Security
- **Hashing**: SHA-256 with salt (username)
- **Length Limit**: 1-16 characters (configurable)
- **Blank Passwords**: Supported for development/testing
- **Storage**: Hash only, never plain text

### File Protection
- **Git Exclusion**: `.gitignore` prevents tracking
- **Sandbox Only**: Never stored outside sandbox/
- **Format Validation**: Structured markdown validation
- **Backup System**: Temporary backups during operations

### Security Protocols

#### Missing File Protocol
1. **Detection**: Startup check or command validation
2. **Warning**: User notification with countdown
3. **Cleanup**: Remove sandbox/ and uMEMORY/user/
4. **Restart**: Fresh system initialization

#### Invalid File Protocol
1. **Format Check**: Markdown structure validation
2. **Header Check**: Required "🎭 uDOS User Identity" header
3. **Field Validation**: Required authentication fields
4. **Reset Option**: Offer to recreate valid file

## 🔧 Implementation Details

### Function Overview

#### user-auth.sh Functions
```bash
check_user_file()          # Validate user.md existence and format
get_user_value()           # Extract values from user.md
set_user_value()           # Update values in user.md
hash_password()            # Generate SHA-256 password hash
validate_password()        # Check password length constraints
create_user_file()         # Create new user.md from template
interactive_setup()        # User-friendly account creation
authenticate()             # Perform user authentication
change_password()          # Update user password
show_user_info()          # Display user information
trigger_destroy_reboot()   # Execute security protocol
```

#### ucode.sh Integration
```bash
authenticate_user()        # Modified for sandbox/user.md
handle_user_command()      # USER command processor
check_user_authentication()# Startup validation (startup.sh)
```

### Configuration Variables

#### Environment Variables
```bash
UDOS_DEV_MODE=true         # Skip authentication in development
UDOS_ROOT=/path/to/udos    # uDOS installation directory
```

#### File Paths
```bash
USER_FILE="$SANDBOX_DIR/user.md"
USER_AUTH_SCRIPT="$UDOS_ROOT/uCORE/code/user-auth.sh"
SANDBOX_DIR="$UDOS_ROOT/sandbox"
```

## 🚀 Usage Examples

### First Time Setup

```bash
# Interactive user creation
cd /path/to/uDOS
./uCORE/code/user-auth.sh setup

# Follow prompts:
# Username: myuser
# Password: secret123 (or blank for none)
# Creates: sandbox/user.md with hashed password
```

### Daily Authentication

```bash
# System startup automatically checks user.md
./uCORE/code/startup.sh

# Manual authentication test
./uCORE/code/user-auth.sh auth

# From within uDOS
USER AUTH
```

### Password Management

```bash
# Change password
./uCORE/code/user-auth.sh password
# Enter new password: newSecret456
# Confirm password: newSecret456

# Disable password
./uCORE/code/user-auth.sh password
# Enter new password: [blank]
# Password disabled
```

### User Information

```bash
# Show detailed user info
./uCORE/code/user-auth.sh info

# From within uDOS
USER INFO
```

## 🔄 Integration with Existing Systems

### uMEMORY Migration
- Old authentication in `uMEMORY/.auth` deprecated
- New system uses `sandbox/user.md` exclusively
- Migration handled automatically on first run

### Backup Integration
- User data excluded from system backups
- Sandbox backup separate from uMEMORY
- User.md backed up during password changes

### Development Mode
- `UDOS_DEV_MODE=true` bypasses authentication
- Allows development without user setup
- Security warnings displayed

## 📋 Testing Checklist

### Basic Functionality
- [ ] Create new user account
- [ ] Set password (1-16 characters)
- [ ] Authenticate with correct password
- [ ] Reject incorrect password
- [ ] Change password
- [ ] Disable password (blank)
- [ ] Show user information
- [ ] Reset user account

### Security Testing
- [ ] Missing user.md triggers destroy/reboot
- [ ] Invalid file format triggers reset
- [ ] Password hashing working correctly
- [ ] Development mode bypass
- [ ] Git exclusion working
- [ ] Backup system functional

### Integration Testing
- [ ] USER command in main interface
- [ ] Startup authentication check
- [ ] Help system updated
- [ ] Error handling and recovery
- [ ] Cross-platform compatibility

## 🔧 Troubleshooting

### Common Issues

#### Authentication Fails
```bash
# Check file exists and is valid
./uCORE/code/user-auth.sh check

# Verify user info
./uCORE/code/user-auth.sh info

# Reset if corrupted
./uCORE/code/user-auth.sh reset
```

#### Missing user.md
```bash
# Expected behavior: system destroy/reboot
# To recover: create new user account
./uCORE/code/user-auth.sh create
```

#### Permission Issues
```bash
# Ensure script is executable
chmod +x /path/to/uDOS/uCORE/code/user-auth.sh

# Check sandbox directory permissions
ls -la /path/to/uDOS/sandbox/
```

### Debug Mode

```bash
# Enable debug output
export UDOS_DEBUG=true
./uCORE/code/user-auth.sh auth

# Check system integration
USER CHECK
```

## 📚 References

### Related Documentation
- `docs/user-guides/USER-GUIDE.md` - General user guide
- `docs/technical/ARCHITECTURE.md` - System architecture
- `sandbox/README.md` - Sandbox workspace documentation
- `.gitignore` - File exclusion patterns

### Security Standards
- SHA-256 password hashing
- Secure file permissions (600)
- No plain text password storage
- Automated security protocols

---

*This documentation covers the complete uDOS User Authentication System implementation. For additional support, use the `USER HELP` command or consult the main system documentation.*
