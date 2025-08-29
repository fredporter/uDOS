# User Setup Story

**Story ID**: user-setup  
**Required Variables**: USER_USERNAME, USER_PASSWORD, USER_ROLE, USER_TIMEZONE, USER_LOCATION  
**Template Type**: interactive  
**Variable Scope**: USER
**Output File**: sandbox/user.md

## Story Flow

### Step 1: Welcome
Welcome to uDOS! Let's set up your user profile.

Your user profile is stored in `sandbox/user.md` as simple key-value pairs:
- USERNAME (display name)
- PASSWORD (can be blank to skip authentication)
- ROLE (permission level)
- TIMEZONE (for proper time display)
- LOCATION (unique name for this installation)

### Step 2: Username
**Question**: What username would you like to use?
**Variable**: USER_USERNAME
**Default**: {SYSTEM_DEFAULT_USER:user}
**Validation**: alphanumeric, 3-20 characters

### Step 3: Password
**Question**: Set a password (leave blank to skip authentication)
**Variable**: USER_PASSWORD
**Default**: (blank)
**Validation**: optional, any characters

### Step 4: Role Selection
**Question**: Select your starting role
**Variable**: USER_ROLE
**Options**: 
- GHOST (Demo/Evaluation - Level 10)
- TOMB (Archive Management - Level 20) 
- CRYPT (Secure Storage & Network - Level 30)
- DRONE (Task Automation - Level 40)
- KNIGHT (Security & Network Management - Level 50)
- IMP (Development Tools - Level 60)
- SORCERER (Advanced User - Level 80)
- WIZARD (Full Development - Level 100)
**Default**: {INSTALL_DEFAULT_ROLE:KNIGHT}

### Step 5: Timezone
**Question**: What is your timezone?
**Variable**: USER_TIMEZONE
**Default**: {SYSTEM_TIMEZONE:America/New_York}
**Examples**: America/Los_Angeles, Europe/London, Asia/Tokyo

### Step 6: Location Name
**Question**: Give this uDOS installation a unique location name
**Variable**: USER_LOCATION
**Default**: {SYSTEM_HOSTNAME:uDOS-Desktop-1}
**Validation**: alphanumeric and hyphens, 5-30 characters

## Template Output

```
USERNAME={USER_USERNAME}
PASSWORD={USER_PASSWORD}
ROLE={USER_ROLE}
TIMEZONE={USER_TIMEZONE}
LOCATION={USER_LOCATION}
```

## Variable Integration

This story integrates with uMEMORY system variables:
- Reads defaults from installation.md via INSTALL_* variables
- Sets USER_* scope variables for user data
- Uses SYSTEM_* variables for platform defaults
- Outputs to sandbox/user.md in key=value format

## Integration

This story is automatically triggered when:
1. `sandbox/user.md` is missing
2. `sandbox/user.md` has incorrect format
3. Manual command: `[STORY|RUN*user-setup]`
4. Command router detects invalid user configuration
