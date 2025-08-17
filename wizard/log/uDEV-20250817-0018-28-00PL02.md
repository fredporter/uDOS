# uDOS Root Directory Restructure Plan

## 🎯 New Architecture Overview

### Target Structure:
```
uDOS/
├── uCORE/                    # Core system files (read-only in production)
├── uMEMORY/                  # User-generated & customized files
├── uKNOWLEDGE/              # Shared public knowledge bank (Wizard managed)
├── uSANDBOX/                # User workspace & drafts
├── assistant/               # AI/Gemini companion system
└── [Root files]             # README, LICENSE, etc.
```

## 📦 Migration Mapping

### → uCORE/ (Core System)
**Purpose**: All core system files, extensions, installers, templates, datasets
```
Current → New Location
uCode/ → uCORE/code/
uCore/ → uCORE/system/
uExtensions/ → uCORE/extensions/
uInstall/ → uCORE/installers/
uTemplate/ → uCORE/templates/
package/ → uCORE/package/
launcher/ → uCORE/launcher/
docs/ → uCORE/docs/
uDev/ → uCORE/development/
uMapping/ → uCORE/datasets/mapping/
```

### → uMEMORY/ (User Data)
**Purpose**: User-generated content, customizations, personal templates
```
New Structure:
uMEMORY/
├── templates/          # User custom templates
├── scripts/           # User custom scripts  
├── datasets/          # User datasets
├── configs/           # User configurations
├── projects/          # User projects
└── extensions/        # User-specific extensions
```

### → uKNOWLEDGE/ (Knowledge Bank)
**Purpose**: Shared public knowledge (Wizard managed, read-only)
```
Current → New Location
uKnowledge/ → uKNOWLEDGE/
```

### → uSANDBOX/ (User Workspace)
**Purpose**: User drafts, scripts, experiments
```
Current → New Location
uSandbox/ → uSANDBOX/
uScript/ → uSANDBOX/scripts/
+ user.md (new file)
```

### → assistant/ (AI Companion)
**Purpose**: AI/Gemini companion system
```
Current → New Location
uCompanion/ → assistant/
```

## 🔧 Implementation Steps

1. **Create new directory structure**
2. **Migrate core system files to uCORE/**
3. **Set up uMEMORY/ for user data**
4. **Reorganize uKNOWLEDGE/**
5. **Consolidate uSANDBOX/**
6. **Rename companion system to assistant/**
7. **Update all references and paths**
8. **Update documentation**
9. **Test functionality**

## ⚡ Benefits

- **Clear Separation**: System vs User vs Knowledge vs Workspace
- **Security**: Core files protected from user modifications
- **Scalability**: Easy to backup user data separately
- **Maintainability**: Logical organization for development
- **User Experience**: Clear understanding of file purposes

Ready to execute this restructure?
