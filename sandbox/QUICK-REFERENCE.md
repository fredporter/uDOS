# 🚀 Sandbox Quick Reference - Keep It Clean!

## 🎯 **Golden Rule: NO SCATTERED FILES!**
Everything goes in its proper sandbox location!

## ⚡ **Common Commands**

### Start Working
```bash
sandbox SESSION START                 # Begin development session
sandbox DEV CREATE my-feature.sh     # Create development file
```

### Track Progress
```bash
sandbox WORKFLOW MOVE development "Building auth system"
sandbox WORKFLOW MILESTONE "Auth Complete" "Login working securely"
```

### File Locations
```bash
sandbox DEV CREATE script.sh         # → /sandbox/dev/script.sh
sandbox EXPERIMENT CREATE feature    # → /sandbox/dev/exp-feature.sh
sandbox TEST CREATE validation       # → /sandbox/dev/test-validation.sh
```

### Get Help
```bash
sandbox WORKFLOW ASSIST ENTER development    # AI coding guidance
sandbox STATUS                               # Full environment status
```

## 📁 **Where Things Go**

| Type | Command | Location |
|------|---------|----------|
| Development Scripts | `sandbox DEV CREATE` | `/sandbox/dev/` |
| Test Scripts | `sandbox TEST CREATE` | `/sandbox/dev/test-*.sh` |
| Experiments | `sandbox EXPERIMENT CREATE` | `/sandbox/dev/exp-*.sh` |
| Temporary Files | Manual creation | `/sandbox/temp/` (auto-clean) |
| User Utilities | Manual creation | `/sandbox/scripts/` |

## 🗺️ **Workflow Stages**

1. **MOVES** - What you're doing now
2. **MILESTONES** - What you've achieved
3. **MISSIONS** - What you plan to do
4. **LEGACY** - Lasting impact summary

## 🧹 **Keep Clean Checklist**

- ✅ Start every work session: `sandbox SESSION START`
- ✅ Create files via sandbox commands (not manually in random dirs)
- ✅ Log significant work with workflow commands
- ✅ Use `/sandbox/temp/` for temporary files
- ✅ End sessions: `sandbox SESSION END`

## 🚫 **Avoid These Habits**

- ❌ Creating scripts directly in `/dev/`, `/docs/`, or other main dirs
- ❌ Leaving temporary files scattered around
- ❌ Working without session tracking
- ❌ Not using workflow to track progress

---

**Everything has a place. Keep the main directories clean!** 🏖️
