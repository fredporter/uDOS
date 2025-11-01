# uDOS Wiki Content

This directory contains all wiki pages for the uDOS GitHub Wiki.

## 📚 Wiki Pages

- **Home.md** - Main wiki landing page
- **Quick-Start.md** - 5-minute getting started guide
- **Architecture.md** - System design and components
- **Command-Reference.md** - Complete command documentation
- **FAQ.md** - Frequently asked questions
- **_Sidebar.md** - Wiki navigation sidebar
- **_Footer.md** - Wiki footer with links
- **DEPLOYMENT-GUIDE.md** - Instructions for deploying to GitHub

## 🚀 Deploying to GitHub

### Quick Deploy

```bash
./deploy_wiki.sh
```

### Manual Deploy

1. Enable Wiki feature in GitHub repository settings
2. Clone wiki repo: `git clone https://github.com/fredporter/uDOS.wiki.git`
3. Copy all `.md` files from this directory
4. Commit and push

[Full deployment instructions →](DEPLOYMENT-GUIDE.md)

## 📝 Adding New Pages

1. Create `NewPage.md` in this directory
2. Write content using GitHub Flavored Markdown
3. Add link to `_Sidebar.md` navigation
4. Run `./deploy_wiki.sh` to publish

## 🎨 Markdown Guidelines

- Use `#` for main headings (one per page)
- Use `##` for section headings
- Use `###` for sub-sections
- Include code blocks with syntax highlighting
- Add tables for comparisons
- Use emojis sparingly for visual emphasis
- Cross-reference related pages: `[Text](Page-Name)`

## 🔗 Wiki Links

Format: `[Link Text](Page-Name)` (no `.md` extension)

**Example**:
```markdown
See the [Command Reference](Command-Reference) for details.
```

## 📦 Current Wiki Structure

```
Getting Started
├── Home
├── Quick-Start
├── Installation
└── First-Steps

Reference
├── Command-Reference
├── Architecture
├── uCODE-Language
└── API-Documentation

Features
├── Mapping-System
├── AI-Integration
├── Color-Palette
├── Grid-System
└── Session-Logging

Development
├── Contributing
├── Development-Workflow
├── Testing
└── Extensions

Help
├── FAQ
├── Troubleshooting
├── Changelog
└── Roadmap
```

## ✅ Deployment Checklist

Before deploying:

- [ ] All links work (use relative wiki links)
- [ ] Code examples are tested
- [ ] Images are uploaded (if any)
- [ ] Sidebar updated with new pages
- [ ] Footer has current date
- [ ] Content is proofread
- [ ] Version numbers are current

## 🛠️ Local Testing

Preview markdown files:
- VS Code: Built-in preview (Cmd+Shift+V)
- GitHub Desktop: Markdown preview
- Online: [StackEdit](https://stackedit.io/)

## 📅 Maintenance

- **Weekly**: Review and update based on code changes
- **Per Release**: Update version numbers and features
- **As Needed**: Add community-requested documentation

## 🤝 Contributing

To suggest wiki improvements:
1. Open an issue with label "wiki"
2. Describe the improvement
3. Provide example content if possible

Or:
1. Fork the repository
2. Edit wiki pages
3. Submit pull request with changes

## 📖 Resources

- [GitHub Wiki Docs](https://docs.github.com/en/communities/documenting-your-project-with-wikis)
- [Markdown Guide](https://www.markdownguide.org/)
- [GitHub Flavored Markdown](https://github.github.com/gfm/)

---

**Wiki Status**: ✅ Ready for deployment

**Last Updated**: October 30, 2025

🔮 *Documentation is magic - keep it clear and current!*
