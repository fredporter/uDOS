# Documentation Index & Navigation

**Last Updated:** 2026-03-03

Complete navigation guide for uDOS + Vibe documentation.

## Quick Start (Choose Your Path)

### 👨‍💻 I'm New to This Project
1. Read [Project Overview](../README.md) (5 min)
2. Follow [Getting Started](dev/GETTING-STARTED.md) (10 min)
3. Understand [Architecture](ARCHITECTURE.md) (20 min)

### 🏗️ I'm an Architect/Reviewer
- [Architecture Guide](ARCHITECTURE.md) — Full system design
- [Decisions](decisions/) — Design rationale
- [Integration Readiness](INTEGRATION-READINESS.md) — Audit results

### 🔧 I'm a Maintainer
- [Integration Readiness](INTEGRATION-READINESS.md) — Health checks
- [Roadmap](roadmap.md) — Active milestone and execution steps
- [v1.5 Workflow Decision](decisions/v1-5-workflow.md) — Active workflow architecture and lane split
- [UCODE Offline Operator Runbook](howto/UCODE-OFFLINE-OPERATOR-RUNBOOK.md) — No-network recovery flow
- [Troubleshooting](troubleshooting/) — Common issues

### 📚 I'm Building Tools/Skills
- [Phase A Quick Reference](PHASE-A-QUICKREF.md) — Templates & examples
- [Decisions](decisions/) — Design context
- [Specifications](specs/) — Technical requirements

---

## Full Documentation Map

### Core Documentation

| Document | Read Time | Purpose |
|----------|-----------|---------|
| [README.md](../README.md) | 5 min | Project overview |
| [ARCHITECTURE.md](ARCHITECTURE.md) | 20 min | Non-fork integration model |
| [INTEGRATION-READINESS.md](INTEGRATION-READINESS.md) | 15 min | Audit results & validation |
| [roadmap.md](roadmap.md) | 10 min | Active milestone and execution priorities |
| [decisions/v1-5-workflow.md](decisions/v1-5-workflow.md) | 10 min | Active workflow scheduler decision |
| [PHASE-A-QUICKREF.md](PHASE-A-QUICKREF.md) | 15 min | Developer templates |

### Development Guides

| Folder | Contains | For Whom |
|--------|----------|----------|
| [dev/](dev/) | Setup, workflows, tasks | All developers |
| [howto/](howto/) | Step-by-step procedures | Everyone |
| [specs/](specs/) | Format specifications | Architects |
| [decisions/](decisions/) | Architecture decisions | Decision makers |
| [troubleshooting/](troubleshooting/) | Problem solving | Everyone |
| [examples/](examples/) | Code samples | Learners |

---

## What's Inside Each Folder

### `docs/dev/`
Development setup and workflows:
- `GETTING-STARTED.md` — Installation, project nav, first commands
- Other dev-specific guides

### `docs/decisions/`
Architecture decision records (ADRs):
- Documenting major design choices
- Trade-offs and rationale
- Reference when implementing

### `docs/specs/`
Technical specifications:
- Format schemas and contracts
- Interface definitions
- Compatibility requirements

### `docs/howto/`
Procedures and step-by-step guides:
- How to X, How to Y, etc.
- Best practices
- Common workflows

### `docs/troubleshooting/`
Problem-solving guides:
- Common issues and fixes
- Debugging techniques
- FAQ by category

### `docs/examples/`
Code samples and patterns:
- Tool examples
- Skill examples
- Integration patterns

---

## Document Dependency Map

```
README.md (start here)
  ├→ Getting Started (dev/GETTING-STARTED.md)
  ├→ Architecture (ARCHITECTURE.md)
  │   └→ Decisions (decisions/)
  │   └→ Integrations (INTEGRATION-READINESS.md)
  │
  ├→ Phase A (PHASE-A-QUICKREF.md)
  │   ├→ Examples (examples/)
  │   └→ Specifications (specs/)
  │
  └→ Maintenance (roadmap.md)
      └→ Troubleshooting (troubleshooting/)
```

---

## Quick Links

### Most Important

- **New to project?** → [dev/GETTING-STARTED.md](dev/GETTING-STARTED.md)
- **Understand design?** → [ARCHITECTURE.md](ARCHITECTURE.md)
- **Track current priorities?** → [roadmap.md](roadmap.md)
- **Track workflow architecture?** → [decisions/v1-5-workflow.md](decisions/v1-5-workflow.md)
- **Build a tool?** → [PHASE-A-QUICKREF.md](PHASE-A-QUICKREF.md)

### For Specific Tasks

- **Set up dev environment** → [dev/GETTING-STARTED.md](dev/GETTING-STARTED.md)
- **Understand project readiness** → [INTEGRATION-READINESS.md](INTEGRATION-READINESS.md)
- **Find workflow status/scope split** → [roadmap.md](roadmap.md) and [decisions/v1-5-workflow.md](decisions/v1-5-workflow.md)
- **Find format specs** → [specs/](specs/)
- **Solve a problem** → [troubleshooting/](troubleshooting/)
- **Learn design decisions** → [decisions/](decisions/)
- **See code examples** → [examples/](examples/)

---

## Archive & History

Superseded documentation is archived under `/.compost/<date>/archive/`.

See [COMPOST-POLICY.md](COMPOST-POLICY.md) for archival procedures.

---

<div align="center">

**Still have questions?** Open an issue or check the relevant guide above. 📚

</div>
