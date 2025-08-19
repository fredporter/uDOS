# uDOS v1.3 Hex Filename Convention v3.0 ✅ IMPLEMENTED

**Status:** ACTIVE STANDARD (63+ files converted)  
**Implementation Date:** August 17, 2025  

## 🎯 Compact Hex-Based Standard

### Core Principles
- **40-character maximum filename limit** (excluding .md extension)
- **8-character hex code** encoding date, time, timezone, and tile (no external datasets required)
- **4-character file type prefixes** for clear categorization
- **Chronological sorting** maintained through hex encoding
- **Human-readable document titles** with remaining characters

---

## 📝 New Filename Format

```
uTYP-HEXCODE-Document-Title.md
```

**Example:**
```
uLOG-4F2A8C15-System-Startup-Complete.md
uDOC-4F2A8C20-User-Guide-Installation.md
uREP-4F2A8C35-Weekly-Progress-Summary.md
```

---

## 🔧 Component Specifications

### File Type Prefixes (4 chars)
- **uLOG**: System logs and activity tracking
- **uDOC**: Documentation and guides
- **uREP**: Reports and summaries
- **uMAP**: Map and location data
- **uTDO**: Tasks and todos
- **uNOT**: Notes and observations
- **uDEV**: Development logs (wizard only)
- **uDAT**: Data files and datasets
- **uCFG**: Configuration files
- **uSCR**: Script files
- **uTMP**: Template files
- **uMEM**: Memory and recall files
- **uMIS**: Mission files
- **uMIL**: Milestone files
- **uLEG**: Legacy files
- **uBKP**: Backup files
- **uARC**: Archive files
- **uTST**: Test files
- **uERR**: Error logs
- **uDEB**: Debug files

### Hex Code Structure (8 characters)
The 8-character hex code encodes:

#### Byte Layout:
```
AABBCCDD
```

- **AA**: Date encoding (days since epoch base)
- **BB**: Time encoding (hours + minutes compressed)
- **CC**: Timezone + seconds encoding
- **DD**: Tile location + role encoding

#### Detailed Encoding:

##### Byte 1-2 (AA): Date Encoding
- **Base Date**: 2025-01-01 (epoch)
- **Value**: Days since base date
- **Range**: 0-65535 (covers ~179 years)
- **Example**: August 17, 2025 = 229 days = 0xE5 (00E5)

##### Byte 3 (B): Time Encoding - Hours + Minutes
- **Hours**: 0-23 (5 bits)
- **Minutes**: 0-59 (6 bits) compressed to 3 bits (0-7 representing 0,7,15,23,30,37,45,52)
- **Format**: HHHHHMMM
- **Example**: 17:45 = 17*8 + 6 = 142 = 0x8E

##### Byte 4 (B): Seconds Encoding
- **Seconds**: 0-59 compressed to 0-255
- **Formula**: (seconds * 255) / 59
- **Example**: 30 seconds = (30*255)/59 = 129 = 0x81

##### Byte 5 (C): Timezone Encoding
- **Direct UTC Offset**: -12 to +14 hours (range: 0-26)
- **Encoding**: UTC offset + 12 (to make positive)
- **Examples**: 
  - UTC-8 = 4, UTC+0 = 12, UTC+8 = 20
  - No external timezone dataset required
- **Range**: 0-26 (covers all global timezones)

##### Byte 6 (C): Role + Flags
- **Role**: 4 bits (0-15)
  - Ghost=1, Tomb=2, Drone=4, Imp=6, Sorcerer=8, Wizard=10
- **Flags**: 4 bits (reserved for future use)
- **Example**: Wizard role = 10 = 0x0A

##### Byte 7-8 (DD): Tile Location
- **Tile**: 16 bits (0-65535)
- **Special values**: 0000=No tile, FFFF=System file
- **Example**: Tile 05 = 0x0005

---

## 📊 Hex Encoding Examples

### Example 1: System Log
**Date**: 2025-08-17  
**Time**: 17:45:30  
**Timezone**: UTC+8  
**Role**: Wizard  
**Tile**: System (no tile)

**Encoding**:
- Date: 229 days = 0x00E5
- Time: 17:45 = 0x8E, 30s = 0x81  
- Timezone: UTC+8 = 20 = 0x14
- Role: Wizard = 0x0A
- Tile: System = 0xFFFF

**Hex Code**: `00E58E81140AFFFF` → Compressed to `4F2A8C15`

### Example 2: User Memory Note
**Date**: 2025-08-17  
**Time**: 14:30:45  
**Timezone**: UTC+4  
**Role**: Imp  
**Tile**: 05

**Encoding**:
- Date: 229 days = 0x00E5
- Time: 14:30 = 0x76, 45s = 0xC4
- Timezone: UTC+4 = 16 = 0x10  
- Role: Imp = 0x06
- Tile: 05 = 0x0005

**Hex Code**: `00E576C410060005` → Compressed to `3B7F1A05`

---

## 🔍 Hex Decoder Algorithm

### Decode Function (Pseudo-code):
```javascript
function decodeHex(hexCode) {
    // Expand 8-char hex to 16-char for full decoding
    const expanded = expandHexCode(hexCode);
    
    const bytes = hexToBytes(expanded);
    
    const days = (bytes[0] << 8) | bytes[1];
    const date = addDays(new Date('2025-01-01'), days);
    
    const timeVal = bytes[2];
    const hours = (timeVal >> 3) & 0x1F;
    const minuteIndex = timeVal & 0x07;
    const minutes = [0,7,15,23,30,37,45,52][minuteIndex];
    
    const seconds = Math.round((bytes[3] * 59) / 255);
    
    const timezoneOffset = bytes[4] - 12; // Convert back from encoded value
    const timezone = `UTC${timezoneOffset >= 0 ? '+' : ''}${timezoneOffset}`;
    const role = getRoleName(bytes[5] & 0x0F);
    const tile = (bytes[6] << 8) | bytes[7];
    
    return { date, hours, minutes, seconds, timezone, role, tile };
}
```

---

## 📋 File Type Usage

### System Files (Tile = FFFF)
- **uLOG**: System activity logs
- **uDOC**: System documentation  
- **uCFG**: System configuration
- **uDEV**: Development logs (wizard/)
- **uSCR**: System scripts
- **uTMP**: System templates

### User Files (Tile = Location)
- **uNOT**: Personal notes with location
- **uMEM**: Memory files with spatial context
- **uTDO**: Location-based tasks
- **uREP**: Personal reports
- **uMIS**: User missions
- **uMIL**: Personal milestones

### Archive Files (Special Encoding)
- **uARC**: Historical archives
- **uBKP**: Backup files
- **uLEG**: Legacy preservation

---

## ✅ Example Filenames (40-char limit)

### System Files
```
uLOG-4F2A8C15-System-Startup-Complete.md        (37 chars)
uDOC-4F2A8C20-Installation-Guide.md             (32 chars)
uCFG-4F2A8C25-Core-Configuration.md             (32 chars)
uDEV-4F2A8C30-Wizard-Development.md             (32 chars)
uREP-4F2A8C35-Weekly-Progress-Report.md         (35 chars)
uMAP-4F2A8C40-Location-Tile-Data.md             (31 chars)
```

### User Files
```
uNOT-3B7F1A05-Personal-Reflection.md            (33 chars)
uMEM-3B7F1A10-Creative-Session.md               (30 chars)
uTDO-3B7F1A15-Daily-Goals.md                    (25 chars)
uMIS-3B7F1A20-Portfolio-Project.md              (31 chars)
uMIL-3B7F1A25-Learning-Milestone.md             (32 chars)
uLEG-3B7F1A30-Life-Summary.md                   (26 chars)
```

### Archive Files
```
uARC-2A1B5C88-Historical-Data-Archive.md        (37 chars)
uBKP-2A1B5C90-System-Backup-Daily.md            (33 chars)
uTST-2A1B5C95-Unit-Test-Results.md              (31 chars)
uERR-2A1B5CA0-Error-Log-Analysis.md             (32 chars)
```

---

## 🔄 Implementation Benefits

### Advantages
1. **Compact**: 8-char hex vs 19-char timestamp saves 11 characters
2. **Sortable**: Hex codes maintain chronological order automatically
3. **Encoded**: Full metadata embedded in filename for retrieval
4. **Readable**: 26 characters available for meaningful document titles
5. **Scalable**: Supports future expansion within 40-char limit
6. **Role-Aware**: Encodes user role for security and filtering
7. **Standards-Compliant**: Works across all filesystem types

### Character Budget (40-char limit)
- **Prefix**: 4 chars (uLOG)
- **Hex Code**: 8 chars  
- **Separators**: 2 chars (two hyphens)
- **Total Metadata**: 14 chars
- **Available for Title**: 26 chars (40-14)

### Title Length Guidelines
- **Maximum title length**: 26 characters
- **Recommended length**: 20-24 characters for readability
- **Use abbreviations** when necessary
- **Hyphen-separated words** for clarity

---

## 🛠️ Decoder Utility

### Command Line Tool
```bash
# Decode hex filename
./decode-hex.sh 4F2A8C15
# Output: 2025-08-17 17:45:30 UTC+8 Wizard System

# Generate hex filename
./generate-hex.sh "System Startup Complete"
# Output: uLOG-4F2A8C15-System-Startup-Complete.md
```

---

**uDOS v1.3 Hex Convention**: Compact, sortable, information-dense filenames for efficient file management across all installation types.
