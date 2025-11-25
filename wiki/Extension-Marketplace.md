# Extension Marketplace

**Status:** 🔄 **In Development** (v1.4.0)

The uDOS Extension Marketplace is a community-driven platform for discovering, sharing, and installing extensions. This guide covers submission guidelines, quality standards, and marketplace structure.

---

## 📦 What is an Extension?

Extensions add functionality to uDOS without modifying the core codebase. They can:

- Add new commands
- Create new output interfaces (web apps, GUIs, APIs)
- Integrate external tools and services
- Provide specialized knowledge domains
- Add themes and visual customization
- Automate workflows and tasks

---

## 🏪 Marketplace Structure

### Categories

**1. Knowledge & Content**
- Domain-specific knowledge banks (medical, technical, regional)
- Translation and localization packs
- Educational curriculum and lesson plans
- Reference libraries and datasets

**2. Tools & Utilities**
- Command-line utilities
- File converters and processors
- Backup and sync tools
- System monitoring and diagnostics

**3. Interfaces & Outputs**
- Web applications and dashboards
- Mobile companion apps
- Desktop GUI wrappers
- API servers and integrations

**4. Themes & Visuals**
- Color schemes and palettes
- Teletext graphics packs
- ASCII art collections
- Custom fonts and typography

**5. Integrations**
- External tool connectors
- Cloud service bridges
- Hardware device support
- Protocol implementations

**6. Workflows & Automation**
- Pre-built uCODE scripts
- Mission templates
- Automated routines
- Batch processors

---

## ✅ Quality Standards

### Extension Requirements

**Essential (Must Have)**

- [ ] Clear README with installation instructions
- [ ] License file (must be OSI-approved)
- [ ] Version numbering (semantic versioning)
- [ ] Compatibility statement (uDOS version requirements)
- [ ] Uninstall procedure documented
- [ ] No core uDOS modifications required
- [ ] Offline functionality (or clearly marked as online-only)

**Recommended (Should Have)**

- [ ] Configuration file with defaults
- [ ] Error handling and graceful failures
- [ ] Logging for debugging
- [ ] Example usage and tutorials
- [ ] Tests (unit/integration)
- [ ] CHANGELOG documenting versions
- [ ] Issue tracker (GitHub Issues)

**Optional (Nice to Have)**

- [ ] Screenshots or demos
- [ ] Video walkthrough
- [ ] Interactive tutorial
- [ ] Contribution guidelines
- [ ] Roadmap for future features

---

### Code Quality

**Standards:**

```python
# Good extension code example
class MyExtension:
    """
    Brief description of what this extension does.

    Dependencies:
        - uDOS >= 1.4.0
        - Python >= 3.9

    Configuration:
        See config/my_extension.json
    """

    def __init__(self, udos_context):
        """Initialize with uDOS context."""
        self.logger = udos_context.get_logger(__name__)
        self.config = self.load_config()

    def load_config(self):
        """Load configuration with fallback to defaults."""
        try:
            # Load user config
            pass
        except FileNotFoundError:
            # Return safe defaults
            return self.get_defaults()
```

**Best Practices:**

- Use uDOS logger instead of print()
- Respect uDOS configuration paths
- Follow PEP 8 style guidelines
- Include type hints where possible
- Handle errors gracefully
- Document public APIs
- Test edge cases

---

### Security Review

**Required Checks:**

- [ ] No hardcoded credentials
- [ ] No shell command injection vulnerabilities
- [ ] Input validation on all user data
- [ ] No eval() or exec() of untrusted code
- [ ] File operations use safe paths only
- [ ] Network requests clearly documented
- [ ] Encryption for sensitive data
- [ ] No telemetry without explicit opt-in

**Security Levels:**

**🟢 Safe** - Offline, no external dependencies, sandboxed
**🟡 Caution** - Requires network, system access, or dependencies
**🔴 Trust Required** - Executes code, modifies system, accesses private data

---

## 📝 Submission Process

### 1. Prepare Your Extension

**Structure:**
```
my-extension/
├── README.md          # Overview and installation
├── LICENSE.txt        # OSI-approved license
├── CHANGELOG.md       # Version history
├── requirements.txt   # Python dependencies
├── config/
│   └── defaults.json  # Default configuration
├── src/
│   └── main.py        # Extension code
├── tests/
│   └── test_main.py   # Test suite
└── examples/
    └── demo.uscript   # Usage examples
```

**README Template:**
```markdown
# Extension Name

Brief description (1-2 sentences)

## Features

- Feature 1
- Feature 2
- Feature 3

## Installation

\`\`\`bash
# Installation steps
\`\`\`

## Usage

\`\`\`bash
# Basic usage examples
\`\`\`

## Configuration

\`\`\`json
{
  "setting1": "value1"
}
\`\`\`

## Requirements

- uDOS >= 1.4.0
- Python >= 3.9
- Other dependencies...

## License

[License Name] - See LICENSE.txt
```

---

### 2. Submit to Marketplace

**Option A: GitHub Issue**

1. Go to [Extension Submission Template](https://github.com/fredporter/uDOS/issues/new?template=extension_submission.md)
2. Fill out the form completely
3. Provide repository link
4. Submit for review

**Option B: Pull Request** (for core-adjacent extensions)

1. Fork uDOS repository
2. Add extension to `extensions/community/`
3. Follow [Contributing Guide](../CONTRIBUTING.md)
4. Submit pull request

---

### 3. Review Process

**Timeline:** 1-2 weeks for initial review

**Review Criteria:**

1. **Functionality** - Does it work as described?
2. **Code Quality** - Is it well-written and maintainable?
3. **Documentation** - Is it clear and complete?
4. **Security** - Are there any vulnerabilities?
5. **Philosophy** - Does it align with uDOS principles?

**Possible Outcomes:**

- ✅ **Approved** - Listed in marketplace
- 🔄 **Revisions Needed** - Feedback provided
- ❌ **Rejected** - Explanation given

---

### 4. Maintenance

**Once Approved:**

- Extension listed in marketplace registry
- Added to community extensions directory
- Included in extension browser (`EXTENSIONS LIST`)
- Eligible for featured status

**Ongoing:**

- Keep dependencies updated
- Respond to bug reports
- Maintain compatibility with uDOS releases
- Update documentation as needed
- Tag stable releases

---

## 🔍 Discovery & Installation

### Finding Extensions

**Within uDOS:**
```bash
# List all available extensions
EXTENSIONS LIST

# Search by category
EXTENSIONS LIST tools

# Search by keyword
EXTENSIONS SEARCH backup

# Show extension details
EXTENSIONS INFO my-extension
```

**Online:**
- Browse [Extension Registry](https://github.com/fredporter/uDOS/wiki/Extension-Registry)
- Search GitHub topic: `udos-extension`
- Community showcase in Discussions

---

### Installing Extensions

**Automatic Installation:**
```bash
# Install from registry
EXTENSIONS INSTALL my-extension

# Install specific version
EXTENSIONS INSTALL my-extension@1.2.3

# Install from GitHub
EXTENSIONS INSTALL github:username/repo
```

**Manual Installation:**
```bash
# Clone to extensions directory
cd extensions/community/
git clone https://github.com/username/my-extension

# Install dependencies
cd my-extension
pip install -r requirements.txt

# Enable in uDOS
EXTENSIONS ENABLE my-extension
```

---

### Managing Extensions

**List Installed:**
```bash
EXTENSIONS LIST --installed
```

**Enable/Disable:**
```bash
EXTENSIONS ENABLE my-extension
EXTENSIONS DISABLE my-extension
```

**Update:**
```bash
EXTENSIONS UPDATE my-extension
EXTENSIONS UPDATE --all
```

**Uninstall:**
```bash
EXTENSIONS UNINSTALL my-extension
```

---

## 🌟 Featured Extensions

### Criteria for Featured Status

- ⭐ **5+ star ratings** from community
- 📦 **100+ installs**
- 🔧 **Actively maintained** (updated within 6 months)
- 📚 **Excellent documentation**
- ✅ **High code quality** score
- 🎯 **Solves common needs**

### Current Featured Extensions

*This section will be populated as the marketplace grows*

**Coming Soon:**
- Advanced medical knowledge bank
- Offline map system with GPS integration
- Solar panel calculator and monitoring
- Garden planning and crop rotation tool

---

## 📊 Extension Registry

### Registry Structure

**Location:** `extensions/registry/extensions.json`

**Format:**
```json
{
  "extensions": [
    {
      "id": "my-extension",
      "name": "My Extension",
      "version": "1.0.0",
      "author": "username",
      "description": "Brief description",
      "category": "tools",
      "repository": "https://github.com/username/my-extension",
      "license": "MIT",
      "requires_udos": ">=1.4.0",
      "requires_python": ">=3.9",
      "security_level": "safe",
      "tags": ["backup", "utility", "automation"],
      "install_count": 42,
      "rating": 4.5,
      "last_updated": "2025-11-15"
    }
  ]
}
```

---

## 🛠️ Developer Resources

### Extension API

**Core uDOS Context:**
```python
class ExtensionContext:
    """Context provided to extensions by uDOS."""

    def get_logger(self, name: str) -> Logger:
        """Get configured logger instance."""

    def get_config_path(self) -> Path:
        """Get user config directory."""

    def get_knowledge_path(self) -> Path:
        """Get knowledge bank directory."""

    def get_memory_path(self) -> Path:
        """Get memory directory."""

    def register_command(self, name: str, handler: Callable):
        """Register new command."""

    def emit_event(self, event: str, data: dict):
        """Emit event to uDOS event system."""
```

**Command Registration:**
```python
def setup(context: ExtensionContext):
    """Called when extension is loaded."""
    context.register_command("mycommand", handle_mycommand)

def handle_mycommand(params, grid, parser):
    """Handle custom command."""
    return {
        "status": "success",
        "message": "Command executed",
        "data": {...}
    }
```

📚 **Full API:** [API Reference](API-Reference.md)

---

### Extension Templates

**Starter Templates:**
- `extensions/templates/minimal/` - Bare-bones extension
- `extensions/templates/command/` - Custom command extension
- `extensions/templates/web/` - Web interface extension
- `extensions/templates/knowledge/` - Knowledge domain extension

**Clone and Customize:**
```bash
cp -r extensions/templates/minimal extensions/community/my-extension
cd extensions/community/my-extension
# Edit files...
```

---

### Testing Extensions

**Test Structure:**
```python
# tests/test_main.py
import pytest
from src.main import MyExtension

def test_initialization():
    """Test extension initializes correctly."""
    ext = MyExtension(mock_context)
    assert ext is not None

def test_command_execution():
    """Test custom command works."""
    result = ext.handle_command({"action": "test"})
    assert result["status"] == "success"
```

**Run Tests:**
```bash
pytest tests/
```

---

## 🤝 Community Guidelines

### Extension Philosophy

**Align with uDOS Values:**

- ✅ **Offline-first** - Core features work without internet
- ✅ **Privacy-focused** - Respect user data and privacy
- ✅ **Practical** - Solve real problems for real users
- ✅ **Accessible** - Clear documentation, easy installation
- ✅ **Open** - OSI-approved licenses, open source

**Avoid:**

- ❌ Telemetry without explicit consent
- ❌ Vendor lock-in or proprietary dependencies
- ❌ Cryptocurrency/blockchain requirements
- ❌ Political or controversial content
- ❌ Adware or monetization schemes

---

### Contribution Recognition

**Extension Authors Get:**

- 🏆 Contributor badge on GitHub
- 📝 Credit in extension registry
- 🌟 Featured status when criteria met
- 💬 Direct channel in community discussions
- 🎓 Mentorship for quality improvements

---

## 📋 Extension Checklist

### Pre-Submission

- [ ] Code works on clean uDOS install
- [ ] All dependencies documented
- [ ] README is complete and clear
- [ ] LICENSE file included
- [ ] Version number follows semver
- [ ] No TODO or FIXME in production code
- [ ] Tests pass (if tests provided)
- [ ] No security vulnerabilities
- [ ] Offline functionality verified

### Post-Submission

- [ ] Respond to reviewer feedback
- [ ] Make requested changes
- [ ] Update documentation
- [ ] Tag release version
- [ ] Monitor issues and questions
- [ ] Keep extension updated

---

## 🔮 Future Plans

### v1.5.0 (Q2 2026)

- [ ] Extension browser GUI
- [ ] One-click installation
- [ ] Automatic updates
- [ ] Extension ratings and reviews
- [ ] Community curated collections
- [ ] Extension analytics dashboard

### v1.6.0 (Q3 2026)

- [ ] Extension dependency resolution
- [ ] Sandboxed execution environment
- [ ] Extension marketplace web interface
- [ ] Premium/sponsored extensions support
- [ ] Extension development SDK
- [ ] CI/CD integration for extension testing

---

## 📞 Support

**For Extension Developers:**

- 📖 [API Reference](API-Reference.md)
- 💬 [Developer Discussions](https://github.com/fredporter/uDOS/discussions/categories/development)
- 🐛 [Report Issues](https://github.com/fredporter/uDOS/issues)
- 📧 Extension review team: extensions@udos.dev (coming soon)

**For Extension Users:**

- 📚 [Extension User Guide](Extensions-System.md)
- ❓ [Q&A Discussions](https://github.com/fredporter/uDOS/discussions/categories/q-a)
- 🎨 [Show & Tell](https://github.com/fredporter/uDOS/discussions/categories/show-and-tell)

---

**Last Updated:** v1.4.0 Beta (November 2025)
**Status:** Marketplace infrastructure in development
**Target Launch:** Q1 2026 with public beta
