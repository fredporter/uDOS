# Roadmap: Filename Convention v2.0 Implementation

**Priority**: High  
**Status**: In Progress  
**Created**: 2025-08-17  
**Assignee**: Development Team  

## Objective

Implement the refined filename convention v2.0 across the entire uDOS system with 40-character limits, HHMMSS precision, and location tiles for uMEMORY files only.

## Key Requirements

### ✅ Completed
- [x] Define v2.0 specification with 40-char limit
- [x] Create 2-digit alphanumeric timezone codes
- [x] Update Style-Guide.md with new convention
- [x] Create filename generator utility
- [x] Move utilities to wizard/utilities/

### 🔄 In Progress
- [ ] Test filename generator with all timezone codes
- [ ] Create migration scripts for existing files
- [ ] Update documentation examples throughout system
- [ ] Implement auto-detection of user timezone and location

### 📋 Future Tasks
- [ ] Create VS Code extension for filename generation
- [ ] Integrate with uMEMORY location tile system
- [ ] Add filename validation utilities
- [ ] Create batch rename tools for legacy files

## Implementation Notes

- Focus on uMEMORY files for location tiles initially
- Maintain backward compatibility during transition
- Ensure 40-character limit compliance
- Test with international timezone scenarios

## Dependencies

- Location tile mapping system (uCORE/datasets/locationMap.json)
- Timezone detection utilities
- User preference system for default locations

---

**Next Review**: 2025-08-20  
**Related Tasks**: wizard/workflows/tasks/
