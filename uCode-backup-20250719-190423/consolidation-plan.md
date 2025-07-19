# uCode Scripts Consolidation Plan v1.0

## Current State Analysis
- **Total Scripts**: 67+ shell scripts
- **Main Issues**: Redundant functionality, similar naming patterns, scattered features
- **Goal**: Reduce to ~20-25 core scripts with clear, standardized naming

## Consolidation Strategy

### 🎯 **CORE SYSTEM** (Keep & Enhance)
1. **`ucode.sh`** - Main shell (keep as is)
2. **`core.sh`** - Consolidate: check.sh + init-user.sh + validate-installation.sh
3. **`dash.sh`** - Keep main dashboard, merge dash-enhanced.sh
4. **`setup.sh`** - Merge: setup-*.sh scripts
5. **`companion.sh`** - Rename: companion-system.sh

### 🔧 **PROCESSING ENGINES** (Consolidate)
6. **`template.sh`** - Merge: template-*.sh, display-template-processor.sh, vscode-template-processor.sh
7. **`processor.sh`** - Merge: shortcode-processor*.sh, json-processor.sh
8. **`display.sh`** - Merge: display-*.sh, enhanced-visual-framework.sh

### 🏗️ **SYSTEM MANAGEMENT** (Simplify)
9. **`package.sh`** - Rename: package-manager.sh + packages/ folder integration
10. **`sandbox.sh`** - Rename: sandbox-manager.sh, enhanced-sandbox-manager.sh
11. **`dev.sh`** - Merge: developer-mode.sh, setup-dev.sh
12. **`roles.sh`** - Rename: user-roles.sh
13. **`privacy.sh`** - Rename: privacy-guard.sh

### 🧰 **UTILITIES** (Streamline)
14. **`log.sh`** - Merge: log.sh + enhanced-log.sh
15. **`help.sh`** - Merge: enhanced-help-system.sh + help components
16. **`tree.sh`** - Merge: tree-generator.sh, make-tree*.sh
17. **`trash.sh`** - Keep (already consolidated)
18. **`error.sh`** - Rename: error-handler.sh

### 🧪 **TESTING & VALIDATION** (Consolidate)  
19. **`test.sh`** - Merge: test-*.sh, validate-*.sh, *-validation.sh
20. **`misc.sh`** - Merge: location-manager.sh, variable-manager.sh, other utilities

### 📁 **REMOVE/ARCHIVE** (Clean Up)
- All `demo-*.sh` scripts (move to examples)
- All `enhanced-*` duplicates after consolidation  
- All `*-test.sh` after merging into test.sh
- All template processor variants after consolidation
- All validation variants after consolidation

## Implementation Steps

### Phase 1: Create Consolidated Core Scripts
1. Create `core.sh` - merge check.sh + init-user.sh + validate-installation.sh
2. Create `setup.sh` - merge all setup-*.sh
3. Create `template.sh` - merge all template-*.sh  
4. Create `processor.sh` - merge shortcode + json processors
5. Create `test.sh` - merge all testing/validation scripts

### Phase 2: Rename & Simplify
6. Rename companion-system.sh → companion.sh
7. Rename package-manager.sh → package.sh  
8. Rename sandbox-manager.sh → sandbox.sh
9. Rename developer-mode.sh → dev.sh
10. Rename user-roles.sh → roles.sh

### Phase 3: Clean Up
11. Archive demo-*.sh to examples/
12. Remove redundant enhanced-*.sh scripts
13. Remove test-*.sh variants  
14. Update all references in ucode.sh

### Phase 4: Standardization
15. Standardize function naming across all scripts
16. Implement consistent error handling
17. Add unified help system
18. Update documentation

## Expected Outcome
- **From**: 67+ scripts with confusing names
- **To**: ~20 scripts with clear, single-purpose names
- **Benefits**: Faster loading, easier maintenance, clearer architecture
- **Performance**: 50-70% reduction in script count and complexity

## File Naming Standards
- Single word names where possible (setup.sh not setup-user.sh)
- Clear purpose identification (test.sh handles ALL testing)
- No redundant prefixes (enhanced-, demo-, etc.)
- Consistent with uDOS component naming (template, processor, etc.)

## Next Steps
1. Backup current uCode directory
2. Implement Phase 1 consolidations
3. Test functionality
4. Continue with remaining phases
5. Update all documentation and references
