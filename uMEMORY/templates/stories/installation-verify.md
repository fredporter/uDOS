# Installation Verification Story

**Story ID**: installation-verify  
**Required Variables**: INSTALL_ID, VERSION, PLATFORM  
**Template Type**: system  

## Verification Checks

### Check 1: Installation Profile
Verify `uMEMORY/installation.md` exists and has proper format:

```markdown
# uDOS Installation Profile

**Installation ID**: {INSTALL_ID}
**Version**: {VERSION}
**Type**: enterprise-dev
**Created**: {CREATED_DATE}
**Updated**: {UPDATED_DATE}
**Platform**: {PLATFORM}
```

### Check 2: Required Fields
- ✅ Installation ID (format: uDOS-YYYYMMDD-XXXX)
- ✅ Version (current system version)
- ✅ Platform (detected system platform)
- ✅ Created date (ISO format)
- ✅ Type (installation type)

### Check 3: System Components
- ✅ uCORE/ directory exists
- ✅ uMEMORY/ directory exists  
- ✅ sandbox/ directory exists
- ✅ Core scripts are executable

## Auto-Repair Actions

If installation.md is missing or malformed:
1. Generate new installation ID
2. Detect current platform
3. Set version from VERSION file
4. Create properly formatted installation.md
5. Log repair action

## Integration

This verification runs during:
1. System startup
2. Manual command: `[SYSTEM|VERIFY-INSTALL]`
3. When installation.md is detected as corrupted
