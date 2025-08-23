# uDOS Development Roadmaps

This directory contains all development roadmaps organized in a flat structure for easy access and maintenance.

## 🔗 Integration with Dev Mode

These roadmaps are automatically integrated with the uDOS workflow system:

```bash
# Access roadmaps through workflow system
./dev/workflow.sh roadmaps list           # List all roadmaps
./dev/workflow.sh roadmaps timeline       # Show timeline view
./dev/workflow.sh roadmaps active         # Show active roadmaps
./dev/workflow.sh roadmaps create         # Create new roadmap
```

## 📅 Roadmap Categories

## 📊 Roadmap Statistics

- **Total roadmaps**: 15
- **Last updated**: Sat Aug 23 01:12:19 AEST 2025
- **Naming convention**: `uROAD-YYYYMMDD-Description.md`

## 🔧 Maintenance

Run the cleanup script to maintain this directory:

```bash
./dev/scripts/roadmaps-cleanup.sh
```

## 🔗 Workflow Integration

This directory is integrated with:
- uDOS Assist Mode (OK/END commands)
- Dev Mode Workflow Scheduler
- Automated roadmap tracking
- Timeline-based organization

For more information, see the workflow documentation in `dev/notes/`.
