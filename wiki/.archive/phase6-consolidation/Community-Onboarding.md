# Welcome to the uDOS Community! 🌍

**Welcome!** Whether you're here to learn survival skills, contribute knowledge, or build extensions, we're excited to have you join the uDOS community.

---

## 🎯 Quick Start for New Members

### 1. Get uDOS Running (5 minutes)

**Installation:**
```bash
# Clone the repository
git clone https://github.com/fredporter/uDOS.git
cd uDOS

# Install dependencies
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Launch uDOS
./start_udos.sh
```

**First Commands to Try:**
```
help          # See all available commands
guide         # Interactive tutorial
knowledge     # Explore the knowledge bank
status        # Check your system
```

📚 **Full Guide:** See [Getting Started](Getting-Started.md)

---

### 2. Explore the Knowledge Bank (10 minutes)

uDOS contains **166+ survival guides** across 8 categories:

```
knowledge           # Browse all categories
knowledge water     # Water procurement guides
knowledge fire      # Fire starting techniques
knowledge shelter   # Shelter building guides
```

**Try This:**
```
# Read a guide
READ knowledge/water/guides/solar-water-disinfection.md

# Search for topics
SEARCH fire starting

# View quick reference
READ knowledge/reference/fire-starting-methods.md
```

📚 **Full Guide:** See [Knowledge System](Knowledge-System.md)

---

### 3. Learn uCODE Scripting (15 minutes)

uCODE is uDOS's human-readable scripting language:

**Example - Morning Routine:**
```ucode
# morning-routine.uscript
[SYSTEM|BLANK]
[SYSTEM|ECHO*Good morning! Starting daily routine...]

# Check weather and priorities
[KNOWLEDGE|SEASONAL*today]
[SYSTEM|STATUS]

# Review today's tasks
[MEMORY|RECALL*tasks]
[SYSTEM|ECHO*Have a productive day!]
```

**Run it:**
```
RUN memory/workflow/morning-routine.uscript
```

📚 **Full Guide:** See [uCODE Language](uCODE-Language.md)

---

### 4. Join the Conversation (2 minutes)

**GitHub Discussions:**
- 💡 **Ideas** - Propose features or improvements
- 🎨 **Show & Tell** - Share what you've built
- ❓ **Q&A** - Ask questions and get help
- 📢 **Announcements** - Stay updated on releases

**Community Values:**
- 🌍 **Offline-first** - Everything works without internet
- 🤝 **Barter over currency** - Share knowledge, not wealth
- 🎯 **Practical over political** - Focus on skills that matter
- 👤 **Individual-user-owned** - You control your data

📚 **Read:** [Code of Conduct](../CODE_OF_CONDUCT.md)

---

## 🛠️ Ways to Contribute

### For Everyone

**Share Knowledge**
- Write survival guides using our templates
- Create reference materials (charts, tables, diagrams)
- Share local knowledge (plants, geography, techniques)

**Report Issues**
- Found a bug? [Report it](https://github.com/fredporter/uDOS/issues/new?template=bug_report.md)
- Documentation unclear? [Let us know](https://github.com/fredporter/uDOS/issues/new?template=documentation.md)
- Have an idea? [Share it](https://github.com/fredporter/uDOS/discussions)

**Help Others**
- Answer questions in Discussions
- Share your workflows and scripts
- Review and test beta features

---

### For Developers

**Contribute Code**
1. Read [Contributing Guide](../CONTRIBUTING.md)
2. Check [Developers Guide](Developers-Guide.md)
3. Review [Good First Issues](https://github.com/fredporter/uDOS/labels/good%20first%20issue)
4. Submit a [Pull Request](https://github.com/fredporter/uDOS/compare)

**Build Extensions**
1. Explore [Extensions System](Extensions-System.md)
2. Use extension templates in `extensions/templates/`
3. Submit via [Extension Submission](https://github.com/fredporter/uDOS/issues/new?template=extension_submission.md)

**Improve Documentation**
- Fix typos or unclear sections
- Add code examples
- Create tutorials for specific workflows
- Translate to other languages

---

### For Content Creators

**Knowledge Guides**
- Use `knowledge/templates/guide_template.md`
- Follow [Content Curation](Content-Curation.md) guidelines
- Include diagrams (ASCII, SVG, or Teletext)
- Cite sources and provide context

**Visual Content**
- Create content using our [Content Generation](Content-Generation.md) system
- Design ASCII art for terminal display
- Build Teletext graphics for web interface
- Follow Mac OS System 1 aesthetic guidelines

**Workflows & Scripts**
- Share practical uCODE scripts
- Create mission templates
- Build automation workflows
- Document use cases

---

## 📋 Community Resources

### Documentation

| Resource | Purpose | Audience |
|----------|---------|----------|
| [Quick Start](../QUICK-START.md) | Get running in 5 minutes | New users |
| [Quick Reference](Quick-Reference.md) | Essential commands | All users |
| [Command Reference](Command-Reference.md) | Complete command list | Power users |
| [uCODE Language](uCODE-Language.md) | Scripting guide | Scripters |
| [Developers Guide](Developers-Guide.md) | Complete developer docs | All developers |

| [Troubleshooting](Troubleshooting-Complete.md) | Fix common issues | All users |

**Full Index:** [Documentation Index](Documentation-Index.md)

---

### Support Channels

**📖 Documentation First**
- 90% of questions are answered in the wiki
- Use wiki search or browse by category
- Check [FAQ](FAQ.md) for common questions

**💬 GitHub Discussions**
- Ask questions: [Q&A Category](https://github.com/fredporter/uDOS/discussions/categories/q-a)
- Share ideas: [Ideas Category](https://github.com/fredporter/uDOS/discussions/categories/ideas)
- Show projects: [Show & Tell](https://github.com/fredporter/uDOS/discussions/categories/show-and-tell)

**🐛 GitHub Issues**
- Bug reports: [Bug Template](https://github.com/fredporter/uDOS/issues/new?template=bug_report.md)
- Feature requests: [Feature Template](https://github.com/fredporter/uDOS/issues/new?template=feature_request.md)
- Documentation: [Docs Template](https://github.com/fredporter/uDOS/issues/new?template=documentation.md)

---

## 🎓 Learning Path

### Beginner (Week 1)

**Day 1-2: Basic Usage**
- Install and launch uDOS
- Try basic commands (help, status, blank, exit)
- Explore knowledge bank categories
- Read 3-5 guides that interest you

**Day 3-4: Knowledge Management**
- Import your own markdown files
- Create personal notes
- Learn BANK, MEMORY, and SEARCH commands
- Organize content with tags

**Day 5-7: Simple Scripting**
- Write your first uCODE script
- Create a daily routine workflow
- Use variables and conditionals
- Run automated tasks

---

### Intermediate (Week 2)

**Advanced Commands**
- Master PANEL and TILE layouts
- Use GRID system for organized display
- Create custom themes
- Configure user preferences

**Content Creation**
- Write a knowledge guide using templates
- Generate diagrams with OK Assist
- Create reference materials
- Share with the community

**Extension Basics**
- Explore existing extensions
- Install community extensions
- Understand extension architecture
- Modify simple extensions

---

### Advanced (Week 3+)

**Extension Development**
- Build your first extension
- Create custom commands
- Integrate external tools
- Submit to community marketplace

**Contributing Code**
- Understand uDOS architecture
- Set up development environment
- Write tests for your changes
- Submit pull requests

**Community Leadership**
- Help answer questions
- Review pull requests
- Mentor new contributors
- Shape project direction

---

## 🌟 Success Stories

### Community Projects

**Extension: Medicinal Plant Database**
*by @herbalist_jane*
- 200+ plant profiles with identification
- Regional availability maps
- Preparation methods and dosages
- Integrated with knowledge bank

**Knowledge: Urban Foraging Series**
*by @city_forager*
- 50 guides for city dwellers
- Seasonal availability calendars
- Legal considerations by region
- Safety and identification tips

**Workflow: Emergency Prep Checklist**
*by @prepper_pro*
- Automated monthly equipment checks
- Expiration date tracking
- Supply reorder reminders
- Family communication plans

---

## 📅 Events & Milestones

### Community Calls

**Monthly Office Hours** (First Friday, 3pm UTC)
- Demo new features
- Q&A session
- Community showcase
- Roadmap discussions

**Beta Testing Sprints** (Ongoing)
- Help test new features
- Report bugs and issues
- Suggest improvements
- Earn contributor badges

---

### Recent Release

**v1.1.0 Stable Release** (November 2025)
- 58 wiki pages of documentation
- 166+ survival guides
- 68+ diagrams across formats
- Community infrastructure complete

**Future Goals** (2026+)
- Target: 1,000+ guides
- 500+ diagrams
- Shared asset library

---

## 🏆 Recognition

### Contributor Levels

**🌱 Seedling** (Just joined)
- First contribution made
- Introduction posted
- Profile setup

**🌿 Sprout** (5+ contributions)
- Multiple guides or PRs
- Helped answer questions
- Regular participant

**🌳 Tree** (25+ contributions)
- Significant codebase contributions
- Extension developer
- Community moderator

**🌲 Forest** (100+ contributions)
- Core team member
- Project maintainer
- Mentor to others

---

## 📞 Getting Help

### Before Asking

1. **Search the wiki** - Most questions are documented
2. **Check troubleshooting** - Common issues have solutions
3. **Review discussions** - Someone may have asked already
4. **Try debugging** - Enable verbose logging with `--debug`

### When Asking

**Good Question:**
```
I'm trying to import a guide into the knowledge bank, but getting
"File not found" error.

Setup:
- uDOS v1.1.0
- macOS Sonoma 14.2
- File location: ~/Documents/guide.md

Command: BANK ADD ~/Documents/guide.md
Error: File not found: ~/Documents/guide.md

I've verified the file exists. What am I missing?
```

**Include:**
- uDOS version (`status` command)
- Your OS and Python version
- Exact commands you ran
- Complete error messages
- What you've tried already

---

## 🤝 Community Guidelines

### Our Values

**Respect & Inclusion**
- Welcome all skill levels
- Be patient with beginners
- Assume good intentions
- Focus on ideas, not people

**Quality & Accuracy**
- Verify information before sharing
- Cite sources for knowledge
- Test code before submitting
- Write clear documentation

**Collaboration**
- Share credit generously
- Help others succeed
- Build on existing work
- Give constructive feedback

**Sustainability**
- Think long-term
- Avoid vendor lock-in
- Prioritize offline access
- Respect user privacy

📚 **Full Guidelines:** [Code of Conduct](../CODE_OF_CONDUCT.md)

---

## 🎯 Next Steps

**Choose Your Path:**

- 📖 **Learn More:** [Quick Start Guide](../QUICK-START.md)
- 💬 **Ask Questions:** [GitHub Discussions](https://github.com/fredporter/uDOS/discussions)
- 🛠️ **Start Contributing:** [Contributing Guide](../CONTRIBUTING.md)
- 🎨 **Build Something:** [Extension Development](Extensions-System.md)
- 📚 **Share Knowledge:** [Content Guidelines](Content-Curation.md)

**Welcome to uDOS!** We're building something meaningful together - a tool that empowers individuals with practical knowledge and skills for self-sufficiency. Every contribution matters, whether it's a bug report, a guide, or a line of code.

*Let's build the future of offline knowledge together!* 🌍🤝

---

**Last Updated:** v1.1.0 (November 2025)
**Maintainers:** uDOS Community Team
**License:** See [LICENSE.txt](../LICENSE.txt)
