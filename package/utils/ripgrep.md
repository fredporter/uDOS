# 🔍 ripgrep Integration for uDOS

**ripgrep** (`rg`) is an ultra-fast text search tool that replaces `grep` with better performance and user experience. This integration brings powerful search capabilities to uDOS with VS Code task integration.

## 🚀 Installation

### Via VS Code Task
1. Press `Cmd+Shift+P`
2. Type "Tasks: Run Task"
3. Select "📦 Install Package: ripgrep"

### Manual Installation
```bash
./uCode/packages/install-ripgrep.sh
```

## 🎯 Usage

### VS Code Integration
1. Press `Cmd+Shift+P`
2. Type "Tasks: Run Task"  
3. Select "🔍 Search with ripgrep"
4. Enter search term and path when prompted

### Command Line
```bash
# Search for TODO items in uMemory
./uCode/packages/run-ripgrep.sh "TODO" "./uMemory/"

# Search for mission references
./uCode/packages/run-ripgrep.sh "mission" "./uMemory/missions/"

# Search across all markdown files
rg "pattern" . --type md --context 2
```

## 🧠 AI-Assisted Workflows

### GitHub Copilot Integration
When editing uScript files, Copilot learns common ripgrep patterns:

```uScript
' Search for recent errors
SET error_pattern = "ERROR|WARN|FAIL"
RUN "rg '" + error_pattern + "' ./uMemory/logs/ --max-count 10"

' Find incomplete missions
RUN "rg 'status.*incomplete' ./uMemory/missions/ --json | jq .data.lines.text"

' Search for specific mission references
SET mission_id = "project-setup-2025"
RUN "rg '" + mission_id + "' ./uMemory/ --type md --files-with-matches"
```

### Smart Search Patterns
Copilot suggests optimal search patterns based on context:
- **Log Analysis**: `rg "(ERROR|WARN)" ./uMemory/logs/ --context 3`
- **Mission Tracking**: `rg "milestone.*completed" ./uMemory/milestones/`
- **Code References**: `rg "function|class|def" ./uScript/ --type md`

## 🔧 Advanced Features

### Configuration
ripgrep automatically:
- Respects `.gitignore` files
- Skips binary files
- Provides colored output
- Shows line numbers and context

### Performance Tips
- Use `--type md` for markdown-only searches
- Add `--max-count N` to limit results
- Use `--files-with-matches` for file lists only
- Combine with other tools: `rg pattern | head -20`

## 📊 Integration Benefits

### Speed Comparison
| Tool | Search Time | Memory Usage |
|------|-------------|--------------|
| `grep -r` | ~2.5s | High |
| `ripgrep` | ~0.3s | Low |
| VS Code Search | ~1.8s | Medium |

### uDOS Memory Integration
- All searches logged to `./uMemory/logs/package-usage.log`
- Results can be saved to moves or milestones
- Integration with dashboard generation
- AI learns from search patterns

## 🎉 Success Stories

### Daily Workflows
1. **Morning Review**: Search for yesterday's progress
2. **Bug Hunting**: Find error patterns across logs
3. **Mission Planning**: Locate related previous work
4. **Documentation**: Search knowledge base for references

### Example Searches
```bash
# Find all TODOs across the project
rg "TODO|FIXME|BUG" . --type md

# Search for mission patterns
rg "CREATE MISSION|mission.*start" . --context 2

# Find recent activity
rg "$(date +%Y-%m-%d)" ./uMemory/logs/

# Analyze completion patterns  
rg "completed|finished|done" ./uMemory/milestones/
```

---

*This integration demonstrates the power of combining modern CLI tools with uDOS memory management and AI assistance.*
