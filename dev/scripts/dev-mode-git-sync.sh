#!/bin/bash
# uDOS Dev Mode Git Sync Workflow
# Only allow git sync in Dev Mode (VS Code)


# Enable Dev Mode by setting UDOS_DEV_MODE=1 in your VS Code terminal:
# export UDOS_DEV_MODE=1
if [ "$UDOS_DEV_MODE" != "1" ]; then
  echo "Git sync only allowed in Dev Mode (VS Code)."
  exit 1
fi

git add uCORE/ uSCRIPT/ uMEMORY/core/ wizard/uKNOWLEDGE/ wizard/docs/ wizard/briefings/ wizard/workflows/
git commit -m "Dev Mode sync"
git push

echo "uDOS Dev Mode Git sync complete."
