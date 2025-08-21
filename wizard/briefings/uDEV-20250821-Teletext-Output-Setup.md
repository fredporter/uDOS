# uDEV-Teletext-Output-Setup

**Purpose:** Enable live output monitoring in VS Code using Teletext view for uDOS workflows.

## Steps
1. Open the integrated terminal in VS Code.
2. Run your workflow script (e.g., `bash wizard/workflows/dev-mode-git-sync.sh`).
3. Use the Teletext extension or VS Code's built-in markdown preview to monitor output.
4. For persistent logs, redirect output to a markdown file and open it in Teletext view:
   ```bash
   bash wizard/workflows/dev-mode-git-sync.sh | tee wizard/briefings/uDEV-20250821-Teletext-Output.md
   ```
5. Refresh the markdown preview to see live updates.

---
*This setup keeps your workflow output visible and organized during Dev Mode sessions.*
