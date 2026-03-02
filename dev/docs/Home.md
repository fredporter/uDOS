# uDOS-dev Scaffold Wiki

**Version:** v1.0
**Last Updated:** 2026-02-05

Welcome to the **uDOS-dev** scaffold wiki—your guide to building extensions, containers, and custom projects on top of uDOS.

---

## 🚀 What is `/dev/`?

The `/dev/` submodule is a **public, empty scaffold** that provides:

- ✅ **Framework structure** for organizing your work
- ✅ **Template scripts** and build configurations
- ✅ **Example code** to learn from
- ✅ **Gitignore patterns** to keep your projects private

**What it is NOT:**
- ❌ A project repository (your projects stay local)
- ❌ uDOS documentation (see `/docs/` at root)
- ❌ uDOS development workspace (this is for YOUR code)

---

## 📖 Quick Navigation

| Guide | Purpose |
|-------|---------|
| [**ADD-SUBMODULE**](ADD-SUBMODULE) | Add `/dev/` to your workspace |
| [**DEVELOP-EXTENSION**](DEVELOP-EXTENSION) | Build custom extensions |
| [**DEVELOP-CONTAINER**](DEVELOP-CONTAINER) | Create container definitions |
| [**SCAFFOLD-STRUCTURE**](SCAFFOLD-STRUCTURE) | Understand the framework |
| [**API-REFERENCE**](API-REFERENCE) | uDOS API for extensions |
| [**DEV-WORKSPACE-PRACTICES**](DEV-WORKSPACE-PRACTICES) | uDOS dev practices & tooling |
| [**DEV-WORKSPACE-TEMPLATES**](DEV-WORKSPACE-TEMPLATES) | Safe VS Code + Copilot templates |

---

## 🎯 Getting Started

### 1. Add the Submodule

```bash
# In your uDOS workspace root
git submodule add https://github.com/fredporter/uDOS-dev.git dev
git submodule update --init --recursive
```

**See [ADD-SUBMODULE](ADD-SUBMODULE) for detailed instructions.**

### 2. Choose Your Path

- **Building an extension?** → [DEVELOP-EXTENSION](DEVELOP-EXTENSION)
- **Creating a container?** → [DEVELOP-CONTAINER](DEVELOP-CONTAINER)
- **Exploring the structure?** → [SCAFFOLD-STRUCTURE](SCAFFOLD-STRUCTURE)

---

## 🔧 Development Workflow

1. **Install uDOS** — See [main repo](https://github.com/fredporter/uDOS)
2. **Add `/dev/` submodule** — [ADD-SUBMODULE](ADD-SUBMODULE)
3. **Create your project** — Use guides above
4. **Test locally** — Keep projects in `/dev/` (gitignored)
5. **Deploy independently** — Publish your own repos when ready

---

## 📝 Important Notes

- All your projects in `/dev/` are **automatically gitignored**
- The scaffold provides **structure only**—no code is tracked
- Your work remains **private** until you choose to publish
- Extensions integrate with **uDOS Core** and **Wizard** APIs

---

## 🔗 Related Resources

- [uDOS Main Repository](https://github.com/fredporter/uDOS)
- [uDOS Wiki](https://github.com/fredporter/uDOS/wiki)
- [uDOS Documentation](https://github.com/fredporter/uDOS/tree/main/docs)

---

## 🤝 Community & Support

### Contributing
- [Contributing Guide](https://github.com/fredporter/uDOS/blob/main/CONTRIBUTORS.md) — How to contribute to uDOS
- [Code of Conduct](https://github.com/fredporter/uDOS/blob/main/CODE_OF_CONDUCT.md) — Community guidelines
- [Style Guide](https://github.com/fredporter/uDOS/wiki/STYLE-GUIDE) — Coding standards

### Issues & Support
- [Report uDOS Issues](https://github.com/fredporter/uDOS/issues) — Main project bugs/features
- [Report Scaffold Issues](https://github.com/fredporter/uDOS-dev/issues) — Dev scaffold issues
- [Discussions](https://github.com/fredporter/uDOS/discussions) — Questions & ideas

### Resources
- [Installation Guide](https://github.com/fredporter/uDOS/blob/main/INSTALLATION.md)
- [Quick Start](https://github.com/fredporter/uDOS/blob/main/QUICKSTART.md)

---

**Author:** Fred Porter
**License:** See main uDOS repo
