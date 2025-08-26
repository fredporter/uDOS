# Dev Roadmaps Structure
Development workspace for roadmap management

## Structure
```
dev/roadmaps/
├── current -> ../../docs/roadmaps/current  # Symlink to public roadmaps
└── archive/                                # Local archive storage
```

## Purpose
- **current/**: Symlinked to `/docs/roadmaps/current` for GitHub visibility
- **archive/**: Local storage for completed and outdated roadmaps

## Workflow Integration
- **ASSIST Mode**: Accesses roadmaps via dev/roadmaps/current symlink
- **GitHub Visibility**: Current roadmaps remain visible in docs/roadmaps/current
- **Archive Management**: Completed roadmaps moved to dev/roadmaps/archive (local only)
- **Clean Distribution**: Only active roadmaps visible on GitHub

## Benefits
- ✅ Copilot has consistent access path (`dev/roadmaps/current`)
- ✅ GitHub shows only current roadmaps (clean public view)
- ✅ Archives preserved locally without cluttering repository
- ✅ Seamless integration with ASSIST mode workflow

---
*Roadmap structure optimized for development workflow and GitHub visibility*
