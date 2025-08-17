# uDOS v1.3 Refined Filename Convention v2.0

## 🎯 New Filename Standard

### Core Principles
- **40 character maximum filename limit** (excluding .md extension)
- **Local time adjustment** to user's current timezone
- **HHMMSS precision** (6-digit time format)
- **2-digit alphanumeric timezone codes**
- **User location TILE only for uMEMORY files**
- **Document title support** with proper formatting

---

## 📝 Filename Formats

### 1. General System Files (Most Files)
```
uTYPE-YYYYMMDD-HHMMSSTZ-Document-Title.md
```

### 2. User Memory Files (uMEMORY only)
```
uTYPE-YYYYMMDD-HHMMSSTZ-TILE-Title.md
```

---

## 🔧 Component Specifications

### uTYPE (File Type Prefixes)
- **uLOG**: System logs and activity logs
- **uDEV**: Development mode logs (wizard/ folder only)
- **uDATA**: Data files and datasets
- **uDOC**: Documentation files
- **uTASK**: Task and mission files
- **uNOTE**: User notes and observations
- **uREP**: Reports and summaries
- **uCONF**: Configuration files
- **uSCRIPT**: Script files
- **uTEMP**: Template files

### Date & Time Format
- **YYYYMMDD**: ISO date format (20250817)
- **HHMMSS**: Local time in 24-hour format (174530 = 5:45:30 PM)
- **Automatic timezone adjustment** to user's current location

### Timezone Codes (2-digit alphanumeric)
```
UTC-12: A0    UTC-11: A1    UTC-10: A2    UTC-9: A3
UTC-8:  A4    UTC-7:  A5    UTC-6:  A6    UTC-5: A7
UTC-4:  A8    UTC-3:  A9    UTC-2:  B0    UTC-1: B1
UTC+0:  B2    UTC+1:  B3    UTC+2:  B4    UTC+3: B5
UTC+4:  B6    UTC+5:  B7    UTC+6:  B8    UTC+7: B9
UTC+8:  C0    UTC+9:  C1    UTC+10: C2    UTC+11: C3
UTC+12: C4    UTC+13: C5    UTC+14: C6
```

### TILE Codes (uMEMORY files only)
Format: **LL** (2-digit location tile)
- **01-99**: Geographic tile references from uCORE/datasets/locationMap.json
- Only used for user-specific files in uMEMORY folder

### Document Title
- **Hyphen-Separated-Title-Case**
- **Maximum characters**: Calculated to fit within 40-char limit
- **Examples**: "Daily-Report", "Meeting-Notes", "Project-Update"

---

## 📊 Examples

### General System Files
```
uLOG-20250817-174530C0-System-Startup.md          (37 chars)
uDEV-20250817-174530C0-Dev-Session.md              (34 chars)
uDATA-20250817-174530C0-User-Data.md               (33 chars)
uDOC-20250817-174530C0-Guide.md                    (28 chars)
uTASK-20250817-174530C0-Daily-Tasks.md             (35 chars)
```

### uMEMORY User Files (with TILE)
```
uNOTE-20250817-174530C0-05-Personal.md             (35 chars)
uLOG-20250817-174530C0-05-Activity.md              (34 chars)
uTASK-20250817-174530C0-05-Goals.md                (32 chars)
uREP-20250817-174530C0-05-Weekly.md                (32 chars)
```

---

## 🗂️ File Type Assignments

### System Files (No TILE)
- **wizard/log/**: uDEV-* files
- **uSCRIPT/**: uSCRIPT-* files  
- **uCORE/**: uDATA-*, uCONF-*, uTEMP-* files
- **docs/**: uDOC-* files
- **sandbox/**: uTASK-* files

### User Files (With TILE)
- **uMEMORY/**: uNOTE-*, uLOG-*, uTASK-*, uREP-* files
- **All user-specific content** that relates to geographic location

---

## 🎯 Implementation Rules

### Character Limit Management
1. **Calculate remaining characters**: 40 - (prefix + timestamp + timezone + tile)
2. **For general files**: 40 - 19 = 21 chars for title
3. **For uMEMORY files**: 40 - 22 = 18 chars for title
4. **Truncate title if necessary**: Use meaningful abbreviations

### Timezone Detection
- **Automatic detection** of user's current timezone
- **Local time calculation** from system time
- **Fallback to UTC** (B2) if detection fails

### TILE Assignment
- **User location based** on geographic tile system
- **Only for uMEMORY files** - user-specific content
- **Consistent across user session** until location changes

---

## 🔄 Migration Strategy

### Current Files
- **Keep existing format** for compatibility
- **New files use v2.0 format** going forward
- **Gradual transition** over time

### Documentation Updates
- **Update Style-Guide.md** with new specifications
- **Update architecture docs** with refined naming
- **Create conversion utilities** for existing files

---

## ✅ Benefits

1. **Precision Timing**: HHMMSS provides exact timestamps
2. **Local Time**: Files reflect user's actual time
3. **Character Efficiency**: 40-char limit ensures compatibility
4. **Location Context**: TILE codes for user files only
5. **Document Clarity**: Readable titles within character limits
6. **System Separation**: Clear distinction between system and user files
